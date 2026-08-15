# escama-ap

Convertidor de interfaz WiFi a Access Point (hostapd + dnsmasq) para Debian/Linux.
El AP emite el SSID `escama`; el tráfico de los clientes sale por la interfaz WAN
(modo NAT/masquerade).

> **Regla de diseño:** la interfaz WAN (por defecto `stonepi`) **solo se lee, nunca se
> modifica** por el software. El AP usa la otra interfaz (por defecto `wn8200nd`).

## Arquitectura (post-refactor 2026-08-14)

Consolidado de 6 scripts bash sueltos → **1 librería Python + 1 TUI**. Menos ruido,
única fuente de verdad.

```
opt/escama/escama.py        # NÚCLEO: start|stop|restart|status|reconnect|genconfig
opt/escama/escama-tui.py    # TUI (whiptail): edita escama.env y regenera confs
etc/escama/escama.env       # ÚNICA fuente de verdad (AP_IFACE, WAN_IFACE, SSID, etc.)
etc/hostapd/hostapd-escama.conf    # generado desde escama.env (no editar a mano)
etc/dnsmasq-escama.conf           # generado desde escama.env (no editar a mano)
etc/systemd/system/escama-ap.service      # ExecStart=/opt/escama/escama.py start
etc/systemd/system/escama-egress.service  # watcher VPN: escama.py watch 5
tests/test_escama.py        # 35 unit tests (mock de system calls, no toca el sistema)
setup.cfg                   # config de mutmut (mutation testing)
```

Binarios: `escama` y `escama-tui` → symlinks en `/usr/local/bin/` y `~/.local/bin/`.

## Diseño anti-errores (por qué no se rompe solo)

1. **Validación real del AP**: `do_start()` comprueba `iw dev <AP> info | grep "type AP"`.
   No usa el `grep ssid` bogus que antes decía "AP activo" mintiendo.
2. **WAN dinámico**: el masquerade iptables usa `WAN_IFACE` del env
   (`-o <WAN_IFACE>`), no hardcodeado a `stonepi`. Si cambiás WAN, el NAT sigue funcionando.
3. **Auto-detección de WAN**: si `WAN_IFACE=""` en el env, se toma de la ruta default
   (`ip route show default`). Fallback final: `stonepi` (nunca lo modifica).
4. **Recarga de módulo en fallo -95**: si el driver 8192eu en memoria no expone modo AP
   (`iw phy` sin `* AP`), `reload_module_if_needed()` hace `rmmod`+`modprobe` del DKMS
   (CONFIG_AP_MODE=y) y reintenta. Esto soluciona el "Operation not supported" del hostapd.
5. **Idempotencia**: `start` mata la instancia previa, valida y solo reporta OK si
   `type AP` es real. `restart` = `stop` + `start`.
6. **Egress dinámico VPN/WAN**: el NAT ya no está clavado a la WAN. Si hay un tunnel
   arriba (ProtonVPN, warp-cli, WireGuard, OpenVPN) los clientes salen **por el tunnel**;
   si no lo hay, fallback automático a la WAN. Ver [docs-es/VPN-EGRESS.md](docs-es/VPN-EGRESS.md).
   (Corrige la afirmación vieja de que "WARP + AP no coexisten": sí coexisten, sólo
   había que mover el masquerade y agregar policy routing.)
7. **Bug de IP duplicada mitigado**: `do_stop()` y `_ensure_ip()` hacen `ip addr flush`
   sobre la AP iface, evitando que quede `10.42.1.1/24` pegado en la WAN (que dropeaba
   las respuestas DNS de los clientes con `ICMP unreachable`).

## Uso

```bash
sudo escama.py status        # estado actual
sudo escama.py start         # levanta el AP (hostapd + dnsmasq + masq + forward)
sudo escama.py stop          # baja el AP, restaura iface a cliente (NM managed)
sudo escama.py restart       # stop + start
sudo escama.py reconnect     # igual que restart pero para reconexión manual tras plug/unplug
sudo escama.py genconfig     # regenera hostapd/dnsmasq confs desde escama.env
sudo escama.py egress        # re-evalua salida VPN/WAN sin tirar el AP
sudo escama.py egress vpn    # forzar salida por tunnel (auto|vpn|wan|<iface>)
sudo escama.py watch         # loop: sigue el tunnel y reaplica NAT solo

sudo escama-tui              # menú interactivo (whiptail) para editar escama.env
```

## systemd

```bash
sudo systemctl enable escama-ap.service   # arranca en boot
sudo systemctl start  escama-ap.service   # levanta ahora
sudo systemctl status escama-ap.service
```
```bash
sudo systemctl enable --now escama-egress.service   # sigue la VPN automaticamente
```

`Restart=on-failure` reinicia el service si el proceso muere (no por fallo de hardware:
si el adaptador se desenchufa, hay que correr `sudo escama.py reconnect` a mano).

## Migrar AP ↔ WAN (ej. usar stonepi como AP)

Editar `/etc/escama/escama.env`:

```ini
AP_IFACE="stonepi"
WAN_IFACE="wn8200nd"
```
Luego: `sudo escama.py restart`.

El masquerade y las validaciones usan estos valores; no hay hardcodeos que rompan el cambio.
(NOTA: hoy stonepi da internet al equipo y al TV vía NAT; invertirlo requiere que
wn8200nd sea cliente con internet.)

## Testing

```bash
cd escama-ap
PYTHONPATH=opt/escama python3 -m pytest tests/test_escama.py -v   # 15 tests
python3 -m mutmut run                                         # mutation testing
```
Los tests mockean `run()`/`subprocess`/`os` → **nunca tocan stonepi ni wn8200nd**.

### Mutation testing (mutmut)
- 1ª suite (9 tests): 772 mutantes, ~19% killed → reveló funciones sin cubrir
  (`do_stop`, `do_status`, `wan_has_internet`, `main`).
- 2ª suite (15 tests): 775 mutantes, 264 killed / 158 survived ≈ 62.6%.
- 3ª suite (19 tests, tras agregar log()/load_env() + fix dir-creacion): 783 mutantes,
  **279 killed / 158 survived ≈ 63.8%**.
- Supervivientes restantes: en `load_env()` (parsing de .env, ramas no ejercitadas por
  los inputs de test) y `log()` (formato de string). `run()` es el boundary mockeado.
  Los ~346 🙁 son timeouts por `sleep` en start/stop (ruido de la técnica).
- Conclusión: TODA la lógica anti-errores crítica está cubierta. No se persiguió 80%
  por diminishing returns (tests quirúrgicos por cada rama de parsing de un .env trivial).

## Requisitos

- Python 3.10+
- `hostapd`, `dnsmasq`, `iw`, `nmcli` (NetworkManager)
- Driver RTL8192EU compilado con `CONFIG_AP_MODE=y` (DKMS `rtl8192eu/1.6.2` en este equipo)
- `whiptail` solo para la TUI

## Salida por VPN (ProtonVPN / WARP / WireGuard)

Si usás una VPN en este equipo, los clientes del AP **no** se quedan sin internet:
escama detecta el tunnel y mueve el NAT ahí.

```ini
# /etc/escama/escama.env
EGRESS_MODE="auto"    # auto = VPN si hay tunnel, si no WAN (fallback)
                      # vpn  = solo VPN (kill-switch, sin tunnel no navegan)
                      # wan  = siempre WAN (ignora la VPN)
VPN_IFACE=""          # vacio = auto-detecta proton0/CloudflareWARP/wg0/tun0/...
VPN_FORCE_ROUTE="yes" # policy routing tabla 51821 (imprescindible con warp-cli)
VPN_MSS_CLAMP="yes"   # clamp MSS a la MTU del tunnel (WARP=1280, Proton wg=1420)
VPN_DNS1="10.2.0.1"   # DNS dentro del tunnel (Proton). WARP: 1.1.1.1
```

Detalle completo, casos por proveedor y diagnóstico: **[docs-es/VPN-EGRESS.md](docs-es/VPN-EGRESS.md)**.
