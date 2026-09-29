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
opt/escama/escama.py        # NÚCLEO: start|stop|restart|status|reconnect|genconfig|egress|watch|preflight
opt/escama/escama-launch.c  # launcher ELF rootless (capabilities → núcleo); se compila a /opt/escama/escama-launch
opt/escama/escama-tui.py    # TUI (whiptail): edita escama.env y regenera confs
etc/escama/escama.env       # ÚNICA fuente de verdad (AP_IFACE, WAN_IFACE, SSID, etc.)
etc/hostapd/hostapd-escama.conf    # generado (con root) — sin root: ~/.config/escama/hostapd-escama.conf
etc/dnsmasq-escama.conf           # generado (con root) — sin root: ~/.config/escama/dnsmasq-escama.conf
etc/systemd/system/escama-ap.service      # ExecStart=/opt/escama/escama.py start
etc/systemd/system/escama-egress.service  # watcher VPN: escama.py watch 5
etc/systemd/user/escama-ap.service        # autostart sin sudo (rootless) al iniciar sesión
etc/systemd/user/escama-egress.service    # watcher VPN en modo rootless
tests/test_escama.py        # 102 unit tests (mock de system calls, no toca el sistema)
setup.cfg                   # config de mutmut (mutation testing)
install.sh                  # ciclo de vida: install|uninstall|enable|disable|status|enable --user
```

Instalación y autostart: `sudo ./install.sh install|enable|disable|uninstall` y
`./install.sh status` — crea los symlinks de `escama`/`escama-tui` en
`/usr/local/bin/`, instala los units y **nunca pisa tu `escama.env`** (las
novedades quedan al lado, en `escama.env.new`). También instala las user units
(rootless) sin habilitarlas: eso es `install.sh enable --user`.

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
8. **Canal sin choque con la WAN**: al `start`, `CHANNEL_MODE=auto` lee el canal de la
   WAN (solo lectura, `iw dev <wan> link`), elige de `{1, 6, 11}` el canal sin solape
   (gana el más lejano; empate → menor) y lo loguea. WAN no WiFi legible (ethernet,
   5 GHz, desconectada) → `CHANNEL` del env. El watcher de VPN solo regenera dnsmasq:
   **el canal nunca cambia con el AP activo**.

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
escama preflight             # comprueba la maquina (componentes, version, rootless viable)

sudo escama-tui              # menú interactivo (whiptail) para editar escama.env
```

## Versionado

`VERSION` (en la raíz del repo) es la **única fuente de la versión**: la leen en
runtime `escama.py`, `escama-tui.py` e `install.sh`. No está hardcodeada en ningún
ejecutable. El historial completo está en [`CHANGELOG.md`](CHANGELOG.md).

```bash
escama.py --version      # o -v / version
```

## Preflight

`escama preflight` comprueba **antes de operar** que la máquina tiene lo necesario:
componentes del sistema, versión del repo frente a la instalada en `/opt/escama`, y
si el modo rootless es viable. No toca nada.

```bash
escama preflight        # sin sudo
sudo escama.py preflight
```

## Rootless vs sudo: dos modos, mismo núcleo

**Modo con privilegio** (el histórico): `sudo escama.py start`. Todo pasa por root.

**Modo rootless** (sin sudo): el launcher `/opt/escama/escama-launch` es un binario
ELF con `CAP_NET_ADMIN`, `CAP_NET_RAW` y `CAP_NET_BIND_SERVICE`, y se las pasa al
Python. Hace falta un ELF porque **el kernel ignora las file capabilities en scripts
con shebang**. Solo cubre operaciones de red: escribir en `/etc` sigue necesitando
privilegio, y lo que no puede hacer rootless **degrada con un mensaje explícito**
(recargar el módulo del driver necesita `CAP_SYS_MODULE`; quitarle la interfaz a
NetworkManager necesita autorización de NM).

| | con sudo | rootless |
|---|---|---|
| Red (hostapd, NAT, rutas, sysctl) | ✅ | ✅ vía el launcher |
| Autostart | unit de sistema | unit de usuario |
| Log | `/var/log/escama-ap.log` | `~/.local/state/escama/escama-ap.log` |
| Confs generados | `/etc/{hostapd,dnsmasq}…` | `~/.config/escama/` |
| Recargar módulo del driver | ✅ | ❌ degrada con motivo |

`status` muestra siempre el modo y las rutas efectivas, para no confundir "no
arrancó" con "no tengo permiso".

## systemd

```bash
sudo ./install.sh enable      # arranca al boot + ahora (escama-ap + escama-egress)
sudo ./install.sh disable      # NO arranca al boot + detiene ahora
sudo ./install.sh status      # estado por componente (units, symlinks, env)
```

### Unit de usuario (autostart sin sudo)

Arranca el AP **al iniciar sesión**, sin privileged unit de sistema:

```bash
sudo ./install.sh enable --user     # instala y habilita las user units
sudo ./install.sh disable --user    # y para deshabilitarlas
```

Se instalan en `~/.config/systemd/user/`. `enable --user` **verifica el modo rootless
antes de habilitar**: si no verifica, no deja un unit que falla al iniciar sesión.
Ambos modos pueden convivir, pero solo uno debe estar habilitado a la vez.

```bash
systemctl --user status escama-ap.service
journalctl --user -u escama-ap.service -f
```
Equivale a `systemctl enable/disable --now` sobre los units instalados, con
tolerancia a los que falten en esa máquina.

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

## Canal del AP (no chocar con la WAN)

```ini
# /etc/escama/escama.env
CHANNEL_MODE="auto"    # auto = al start elige de {1,6,11} sin solape con la WAN
                       # manual = usa CHANNEL tal cual (comportamiento clásico)
CHANNEL="6"            # fallback si la WAN no es WiFi legible (o en modo manual)
```

La detección lee la WAN sin modificarla (`iw dev <wan> link`); el canal elegido
y su motivo quedan en el log (`/var/log/escama-ap.log`).

## Testing

```bash
python3 -m pytest tests/test_escama.py -q   # 102 tests (SIEMPRE el path explícito)
~/.local/bin/mutmut run                      # mutation testing (lee setup.cfg)
```
NO corras `python3 -m pytest` sin el path: `mutants/tests/` tiene el mismo
basename y rompe la colección (pitfall documentado en AGENTS.md).
Los tests mockean `run()`/`subprocess`/`os` → **nunca tocan stonepi ni wn8200nd**.

### Mutation testing (mutmut)

| Suite (evolución) | Tests | Mutantes | Killed / survived |
|---|---|---|---|
| 1ª — inicial (reveló `do_stop`, `do_status`, `wan_has_internet`, `main` sin cubrir) | 9 | 772 | ~19% killed |
| 2ª | 15 | 775 | 264 / 158 ≈ 62.6% |
| 3ª — `log()`/`load_env()` + fix de dir-creación | 19 | 783 | 279 / 158 ≈ 63.8% |
| 4ª — selección de canal + split de generación de confs | 45 | 2170 | 676 / 1136 ≈ 37.3% de los testeados |

- La 4ª corrida usa la base de conteo actual de mutmut 3.7 (2170 mutantes vs 783 de
  la 3ª): no comparable en valor absoluto con las filas anteriores.
- Survived del feature nuevo (selección de canal): **equivalentes** — guardas
  redundantes re-rankeadas por `max()`, defaults que `load_env()` siempre mergea, y
  boundary `run()` (mockeado por diseño). Los mutantes significativos (umbral de
  distancia, desempate, parseo de freq, fallback, modo manual) mueren con la tabla
  de tests.
- ~357 untested: mutantes en funciones sin tests mapeados (`main`, `_prompt_iface`,
  caminos de `do_watch`) — condición preexistente.
- Supervivientes restantes: en `load_env()` (parsing de .env, ramas no ejercitadas por
  los inputs de test) y `log()` (formato de string). `run()` es el boundary mockeado.
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
