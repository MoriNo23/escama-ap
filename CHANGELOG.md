# Changelog

Todas las versiones de escama-ap. La versión vive en el archivo `VERSION` de la
raíz del repo (fuente única: la leen `escama.py`, `escama-tui.py` e
`install.sh`). Los números de abajo son semver.

La serie 0.x cubre la historia anterior al versionado: Those releases never
declared a version, así que se reconstruyen por épocas a partir de los commits
del repo. Desde 1.0.0 el bump es explícito: cada change que altera comportamiento
incluye el bump en su `tasks.md` y una entrada acá.

## 1.1.0 — 2026-09-29

### Agregado
- **Arranque sin fricción**: `escama preflight` comprueba la máquina antes de
  operar (componentes, versión del repo frente a la instalada, viabilidad
  rootless) y ofrece instalar con un solo prompt si falta algo. Los subcomandos
  de solo lectura (`status`, `--help`, `--version`) nunca piden privilegio.
- **Modo rootless real**: `/opt/escama/escama-launch` (binario ELF, porque el
  kernel ignora las file capabilities en scripts con shebang) aporta
  `CAP_NET_ADMIN`, `CAP_NET_RAW` y `CAP_NET_BIND_SERVICE` al núcleo, de modo que
  `start`/`stop`/`restart`/`egress` funcionan **sin `sudo`**. El preflight lo
  verifica con una operación real (crear/borrar una interfaz de prueba), no
  leyendo `getcap`.
- **Unit de usuario** (`etc/systemd/user/`, `install.sh enable --user` /
  `disable --user`): el AP arranca al iniciar sesión sin privileged unit.
  `enable --user` verifica el modo rootless antes de habilitar, para no dejar un
  unit que falla al iniciar sesión.
- `VERSION` como fuente única de la versión, leída en runtime por `escama.py`,
  `escama-tui.py` e `install.sh` (antes no había versionado).
- **CI en GitHub Actions** (`.github/workflows/ci.yml`): job `tests` corre la
  suite en cada push/PR a `master` (~25 s); job `mutmut` de mutation testing
  solo manual (`workflow_dispatch`), separado porque sus ~2.200 mutantes
  tardan 30+ min y son tendencia, no gate. La suite es segura en un runner
  ajeno por construcción: un fixture `autouse` bloquea `subprocess` durante
  toda la suite.

### Cambiado
- **Rutas de runtime según privilegio**: con root, log/pidfile/state/confs
  generados van a `/var` y `/etc` como siempre; sin root van a las rutas del
  usuario (`XDG_STATE_HOME`, `XDG_RUNTIME_DIR`, `XDG_CONFIG_HOME`). `escama.env`
  sigue en `/etc` y solo se lee: es la fuente de verdad. `status` muestra el modo
  y las rutas efectivas, para no confundir "no arrancó" con "no tengo permiso".
- El AP elige canal 2.4 GHz sin solape con el de la interfaz WAN: `CHANNEL_MODE=auto`
  (default) lee el canal de la WAN —solo lectura, regla de oro— y elige de
  `{1,6,11}` el más lejano; `manual` conserva el `CHANNEL` fijo. Verificado en la
  máquina: la WAN estaba en el canal 3 y el AP pasó de 6 (solapado) a 11.
- La generación de configs se separó: `watch`/`egress` solo regeneran dnsmasq y
  nunca reescriben hostapd, así el canal no queda obsoleto tras un cambio de VPN.
- `install.sh`: ciclo de vida reproducible (`install|uninstall|enable|disable|status`),
  idempotente y que jamás pisa el `escama.env` del usuario (las novedades quedan
  en `escama.env.new`).

### Corregido
- **Degradación explícita**: recargar el módulo del driver (`rmmod`/`modprobe`,
  necesita `CAP_SYS_MODULE`) y quitarle la interfaz a NetworkManager
  (`nmcli device set managed no`, necesita autorización de NM) se ignoraban en
  silencio con `check=False`. Ahora se reporta el fallo con su motivo real, sin
  reportarlo como exitoso.
- `run()` auto-elevaba con `sudo` aunque el proceso ya tuviera las capabilities
  del launcher, pidiendo una contraseña en el camino rootless.
- `--version` devolvía `desconocido` cuando el comando se invocaba por el symlink
  que crea `install.sh` (`/usr/local/bin/escama`): la búsqueda del archivo
  `VERSION` usaba `abspath` y no resolvía el enlace.
- `install.sh install` avisaba de que había novedades en `escama.env.new` sin
  decir **cuáles**, lo que en la práctica equivale a no avisar: ahora lista las
  variables que están en el env del repo y ausentes en el tuyo.

### Documentado
- `README.md`: versionado, preflight, tabla rootless vs sudo, y unit de usuario.
- `docs/VPN-EGRESS.md` en inglés; los análisis de debugging pasaron a
  `docs/diagnostics/`.

### Cambiado
- El AP elige canal 2.4 GHz sin solape con el de la interfaz WAN: `CHANNEL_MODE=auto`
  (default) lee el canal de la WAN —solo lectura, regla de oro— y elige de
  `{1,6,11}` el más lejano; `manual` conserva el `CHANNEL` fijo. Verificado en la
  máquina: la WAN estaba en el canal 3 y el AP pasó de 6 (solapado) a 11.
- La generación de configs se separó: `watch`/`egress` solo regeneran dnsmasq y
  nunca reescriben hostapd, así el canal no queda obsoleto tras un cambio de VPN.
- `install.sh`: ciclo de vida reproducible (`install|uninstall|enable|disable|status`),
  idempotente y que jamás pisa el `escama.env` del usuario (las novedades quedan
  en `escama.env.new`).

### Agregado
- `docs/VPN-EGRESS.md` en inglés; los análisis de debugging pasaron a
  `docs/diagnostics/`.

## 1.0.0 — 2026-08-14

- Consolidación de 6 scripts bash en un núcleo Python (`escama.py`) + TUI.
- Egress dinámico VPN/WAN con policy routing, kill-switch y clamp de MSS.
- Validación real del AP (`type AP`), auto-detección de roles AP/WAN, recarga
  del módulo 8192eu ante el fallo -95, y documentación ES/EN.

## Serie 0.x (historia previa al versionado)

Reconstruida desde los commits; estas versiones nunca se declararon formalmente.

### 0.4 — Instalación y autostart
- `install.sh` (en el change 1.0.0): instalación y control de arranque automático
  sin pasos manuales.
- Units de systemd `escama-ap.service` y `escama-egress.service`; el watcher de
  egress pasa a ser una unit en vez de un proceso suelto.

### 0.3 — Selección de canal
- `CHANNEL_MODE` y lectura del canal de la WAN (solo lectura) para evitar
  interferencia entre el AP y la iface cliente WiFi.

### 0.2 — Egress por VPN
- Salida de clientes por tunnel (ProtonVPN / WARP / WireGuard) con
  `EGRESS_MODE=auto|vpn|wan`, política de kill-switch y fix de la regla de
  routing `iif <ap>` (regresión documentada en `docs/diagnostics/DIAGNOSIS-FINAL.md`).

### 0.1 — Núcleo
- `escama.py` con `start|stop|restart|status|reconnect|genconfig`, validación real
  del modo AP, masquerade/NAT hacia la WAN, y `dnsmasq` sirviendo DHCP/DNS.
