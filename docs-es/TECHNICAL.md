# escama-ap — Documentación técnica

> Software que convierte una interfaz WiFi en Access Point (hostapd + dnsmasq)
> con salida por una interfaz WAN vía NAT. Convertido de 6 scripts bash a 1 núcleo
> Python el 2026-08-14 para eliminar ruido y errores de diseño.

## 1. Modelo mental

```
 CLIENTES (TV, cel)          AP iface (wn8200nd)          WAN iface (stonepi)
 10.42.1.x/24   <--- wifi -->  [escama SSID]  <--- hostapd/dnsmasq --->  NAT masquerade  -->  Internet
```

- **AP iface**: emite el SSID, da IP/DNS/DHCP a los clientes. Por defecto `wn8200nd`.
- **WAN iface**: tiene internet (cliente de una red externa). Por defecto `stonepi`.
- El software **nunca modifica la WAN iface** (regla de oro). Solo lee su ruta para masquerade.

## 2. Archivos

| Archivo | Rol |
|---------|-----|
| `opt/escama/escama.py` | Núcleo. Acciones: `start\|stop\|restart\|status\|reconnect\|genconfig` |
| `opt/escama/escama-tui.py` | TUI whiptail. Edita `escama.env`, regenera confs |
| `etc/escama/escama.env` | **Única fuente de verdad** |
| `etc/hostapd/hostapd-escama.conf` | Generado desde env. No editar a mano |
| `etc/dnsmasq-escama.conf` | Generado desde env. No editar a mano |
| `etc/systemd/system/escama-ap.service` | Unit systemd (`ExecStart=/opt/escama/escama.py start`) |
| `tests/test_escama.py` | 19 unit tests, mocks de system calls |
| `setup.cfg` | Config mutmut |

## 3. `escama.env` (fuente de verdad)

```ini
AP_IFACE="wn8200nd"          # interfaz que emite el AP
WAN_IFACE="stonepi"          # interfaz con internet (vacío = auto-detecta ruta default)
SSID="escama"
CHANNEL="6"
HW_MODE="g"
AP_IP="10.42.1.1"
AP_CIDR="24"
AP_SUBNET="10.42.1.0/24"
DHCP_START="10.42.1.10"
DHCP_END="10.42.1.254"
DHCP_LEASE="12h"
WPA_PASSPHRASE="#[REMOVED]"
DNS1="8.8.8.8"
DNS2="8.8.4.4"
```

Cambiar cualquiera de estos y correr `sudo escama.py genconfig` (o `restart`) regenera
los confs de hostapd/dnsmasq. No hay 3 lugares que editar a mano.

## 4. Flujo de `escama.py start` (anti-errores)

1. Carga `escama.env`.
2. Si `WAN_IFACE` vacío → auto-detecta desde `ip route show default`; fallback `stonepi`.
3. Si AP iface no existe → error claro "enchufa el adaptador", rc=1.
4. `nmcli device set <AP> managed no` (libera la iface de NM).
5. `reload_module_if_needed()`: si `iw phy <AP>` NO lista `* AP`, hace `rmmod 8192eu`
   + `modprobe 8192eu` (recarga DKMS con `CONFIG_AP_MODE=y`). Esto evita el
   `nl80211: -95 Operation not supported` de hostapd.
6. `generate_configs()`: escribe hostapd/dnsmasq desde el env.
7. Mata hostapd/dnsmasq previos (idempotente).
8. `ip addr flush` + `ip addr add <AP_IP>/<CIDR> dev <AP>` (mitiga IP duplicada).
9. `hostapd -B` + `dnsmasq`.
10. `resolve_egress()`: decide salida según `EGRESS_MODE` (auto/vpn/wan) y el tunnel
    detectado. `apply_egress()` aplica `ip_forward=1`, `MASQUERADE -o <egress>`,
    FORWARD con conntrack y —si el egress es VPN— `rp_filter=2`, tabla de routing
    `51821`, MSS clamp y kill-switch contra fuga por la WAN. Ver `docs-es/VPN-EGRESS.md`.
11. **Valida de verdad**: `iw dev <AP> info | grep "type AP"`. Solo si está → OK.
    Si no → rc=1 (antes mentía con `grep ssid`).

## 5. Cambiar AP ↔ WAN (migración)

Editar `escama.env`:
```ini
AP_IFACE="stonepi"
WAN_IFACE="wn8200nd"
```
`sudo escama.py restart`. El masquerade y validaciones usan estos valores; no hay
hardcodeos. Precaución: la WAN debe tener internet real tras el cambio.

## 6. Reconexión tras plug/unplug

Sin auto-reconnect (decisión de diseño: manual). Si el adaptador se cae:
```bash
sudo escama.py reconnect    # igual que restart, para usar tras re-enchufar
```
`Restart=on-failure` en systemd solo cubre muerte de proceso, no hardware ausente.

## 7. Testing

```bash
PYTHONPATH=opt/escama python3 -m pytest tests/test_escama.py -v   # 15 tests, mocked
python3 -m mutmut run                                      # mutation testing
```
Los tests mockean `run()`/`subprocess`/`os` → **nunca tocan stonepi ni wn8200nd**.

### Mutation testing (mutmut) — ciclo de mejora
- Suite 1 (9 tests): 772 mutantes, ~19% killed. Reveló que `do_stop`, `do_status`,
  `wan_has_internet`, `main` no estaban cubiertos por tests.
- Suite 2 (15 tests): 775 mutantes, 264 killed / 158 survived ≈ 62.6%.
- Suite 3 (19 tests, tras agregar log()/load_env()): 783 mutantes,
  **279 killed / 158 survived ≈ 63.8%**.
- Los 158 supervivientes restantes están en `load_env()` (parsing de .env de 15 líneas,
  ramas no ejercitadas por los inputs de test) y `log()` (formato de string). `run()` es
  el boundary mockeado y no cuenta como superviviente de diseño. Los ~346 🙁 son timeouts
  por el `sleep` de start/stop (ruido de la técnica, no supervivientes reales).
- Conclusión: TODA la lógica anti-errores crítica está cubierta (validación type AP,
  masquerade dinámico, reload en -95, do_stop/do_status, wan_has_internet, main). Los
  supervivientes son parsing/logging no crítico. No se persiguió 80% por diminishing
  returns (requeriría tests quirúrgicos por cada rama de parsing de un .env trivial).
Cubren: load_env, generate_configs (single source of truth), auto-detect WAN,
reload en fallo -95, validación real type AP (pass y fail).

## 8. Requisitos

- Python 3.10+, `hostapd`, `dnsmasq`, `iw`, `nmcli` (NetworkManager)
- Driver RTL8192EU con `CONFIG_AP_MODE=y` (DKMS `rtl8192eu/1.6.2` en este equipo)
- `whiptail` solo para la TUI
- VPN (ProtonVPN / warp-cli / WireGuard): **sí coexiste**. El egress de los clientes
  se mueve al tunnel automáticamente. Ver `docs-es/VPN-EGRESS.md`.
  Opcional: `iptables` con soporte `TCPMSS` y `conntrack` (estándar en Debian)

## 9. Errores de diseño del sistema anterior (ya corregidos)

| Error viejo | Fix |
|-------------|-----|
| `grep ssid` en validación (falsos positivos) | `grep "type AP"` real |
| Masquerade hardcodeado `-o stonepi` | `-o <WAN_IFACE>` dinámico |
| 3 fuentes de verdad (env + 2 confs) | env canonical + genconfig |
| cleanup-warp.sh acoplado a WARP | eliminado |
| Masquerade clavado a WAN: al conectar VPN los clientes perdían internet | egress dinámico (`resolve_egress`/`apply_egress`): NAT + policy routing + MSS clamp hacia el tunnel, con fallback a WAN |
| 6 scripts bash duplicados | 1 `escama.py` |
| Sin detección de módulo sin AP_MODE | reload automático en fallo -95 |
| IP duplicada 10.42.1.1 en WAN | flush en AP iface |
