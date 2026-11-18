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

### 1.1 Modos y estado de runtime (a partir de 1.1.0)

- **Dos modos de operación**: con `sudo` (el histórico, todo como root) o
  **rootless** — `/opt/escama/escama-launch` es un launcher ELF que porta
  `CAP_NET_ADMIN/NET_RAW/NET_BIND_SERVICE` y se las pasa al núcleo, así que
  `start|stop|restart|egress` corren sin sudo. Tiene que ser ELF porque el
  kernel ignora las file capabilities en scripts con shebang. Lo que no puede
  ser rootless (recargar el módulo del driver exige `CAP_SYS_MODULE`, `nmcli`
  exige autorización de NM) degrada con mensaje explícito, nunca en silencio.
- **Preflight**: `escama preflight` comprueba la máquina antes de operar —
  componentes, versión del repo vs instalada, y viabilidad rootless verificada
  con una operación real (no con `getcap`). Solo lectura, corre sin privilegio.
- **Las rutas de runtime dependen del privilegio**: con root,
  log/pidfile/state/confs generados van a `/var` y `/etc`; sin root, a los dirs
  XDG del usuario (`~/.local/state`, `XDG_RUNTIME_DIR`, `~/.config/escama`).
  `escama.toml` queda en `/etc` y solo se lee. `escama status` muestra las
  rutas efectivas.
- **Versionado**: fuente única en `VERSION`, leída en runtime por núcleo, TUI e
  instalador (hardcodearla es un defecto con test en contra). Historial en `CHANGELOG.md`.
- **Autostart**: unit de sistema privilegiada, o **unit de usuario**
  (`install.sh enable --user`) que levanta el AP al iniciar sesión sin privilegio.
- La tabla completa modo por modo vive en `README.md` ("Rootless vs sudo",
  "Unit de usuario").

## 2. Archivos

| Archivo | Rol |
|---------|-----|
| `opt/escama/escama.py` | Núcleo. Acciones: `start\|stop\|restart\|status\|reconnect\|genconfig\|egress\|watch\|rename\|preflight` |
| `opt/escama/escama-tui.py` | TUI whiptail. Edita `escama.toml`, regenera confs |
| `opt/escama/escama-launch.c` | Launcher ELF rootless (capabilities → núcleo); se compila a `/opt/escama/escama-launch` |
| `etc/escama/escama.toml` | **Única fuente de verdad** |
| `etc/hostapd/hostapd-escama.conf` | Generado desde env. No editar a mano |
| `etc/dnsmasq-escama.conf` | Generado desde env. No editar a mano |
| `etc/systemd/system/escama-ap.service` | Unit systemd (`ExecStart=/opt/escama/escama.py start`) |
| `etc/systemd/user/escama-ap.service` | Unit de usuario — autostart sin sudo al iniciar sesión |
| `etc/systemd/user/escama-egress.service` | Unit de usuario — watcher de egress en modo rootless |
| `VERSION` | Fuente única de la versión, leída en runtime por los tres puntos de entrada |
| `CHANGELOG.md` | Historial de versiones (0.x retrospectiva + semver por change) |
| `tests/test_escama.py` | 124 unit tests, mocks de system calls (comando en §7) |
| `setup.cfg` | Config mutmut |

## 3. `escama.toml` (fuente de verdad)

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
WPA_PASSPHRASE=""
DNS1="8.8.8.8"
DNS2="8.8.4.4"
```

Cambiar cualquiera de estos y correr `sudo escama.py genconfig` (o `restart`) regenera
los confs de hostapd/dnsmasq. No hay 3 lugares que editar a mano.

## 4. Flujo de `escama.py start` (anti-errores)

1. Carga `escama.toml`.
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

Editar `escama.toml`:
```ini
AP_IFACE="stonepi"
WAN_IFACE="wn8200nd"
```
`sudo escama.py restart`. El masquerade y validaciones usan estos valores; no hay
hardcodeos. Precaución: la WAN debe tener internet real tras el cambio.

## 5b. Renombrar adaptadores (udev por MAC)

Productiza el renombre manual de siempre (`stonepi`, `wn8200nd`, antes
`wlx<MAC>`):

```bash
sudo escama rename wlx020304050607 wifi-usb
```

Solo WiFi (sysfs `phy80211`); nombre ≤15 chars, `[A-Za-z0-9_-]`, sin dígito
inicial. Deja UNA regla por MAC en `/etc/udev/rules.d/76-escama-ifaces.rules`
(idempotente) y **retira** la regla manual vieja de esa misma MAC de
`70-persistent-net.rules` / `99-stonepi-ap.rules`. Aplica en vivo
(nmcli managed no → down → `ip link set name` → up → managed yes, revinculando
el perfil NM activo). Sincroniza `AP_IFACE`/`WAN_IFACE` del `escama.toml` si
apuntaban al nombre viejo. Solo sudo directo (el launcher rootless da caps de
red, no escritura en `/etc`). Se niega si la iface está en modo AP.

## 6. Reconexión tras plug/unplug

Sin auto-reconnect (decisión de diseño: manual). Si el adaptador se cae:
```bash
sudo escama.py reconnect    # igual que restart, para usar tras re-enchufar
```
`Restart=on-failure` en systemd solo cubre muerte de proceso, no hardware ausente.

## 7. Testing

```bash
python3 -m pytest tests/test_escama.py -q   # 105 tests, mockeados, ~22s
~/.local/bin/mutmut run                      # mutation testing (lee setup.cfg)
```
Los tests mockean `run()`/`subprocess`/`os` → **nunca tocan stonepi ni wn8200nd**.
No es un dicho sino una garantía: un fixture `autouse` bloquea `subprocess`
durante TODA la suite, así que un test que se filtre falla con el comando exacto
que intentó ejecutar.

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
- La tabla corrida por corrida (hasta la 5ª: 105 tests, 2846 mutantes, ≈43,1%
  de los testeados killed) vive en `README.md`.
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
