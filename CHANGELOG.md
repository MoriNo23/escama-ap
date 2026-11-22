## 2.5.1 — 2026-11-22

### Corregido
- **Roles viejos ya no pisan la config**: `escama-roles.state` guarda la firma
  de la configuración que lo originó. Si `WAN_IFACE` cambia —por ejemplo a
  `""` con WAN AUTO— los roles anteriores se ignoran. Antes podían hacer que
  `egress` reaplicara NAT por el AP o por un adaptador caído.
- **`status` con WAN AUTO**: re-detecta la salida igual que `egress`, en vez de
  mostrar "NINGUNA" y un aviso falso de reglas desincronizadas.
- Bump **patch**: corrige comportamientos que ya violaban el contrato de
  egress verificado.

## 2.5.0 — 2026-11-22

### Agregado
- **`WAN AUTO` en la TUI**: el submenú de interfaz WAN ofrece una opción
  automática que guarda `WAN_IFACE=""`. escama detecta entonces la interfaz con
  la ruta por defecto —por ejemplo `wlxd20dab62b48f` en vez de un dongle caído—.
- **Aplicación en caliente**: al guardar un cambio de WAN, la TUI ejecuta
  `escama egress` sin bajar el AP. Muestra el resultado real; si falla, dice que
  la configuración se guardó pero la salida no se aplicó y da el comando manual.

### Notas
- Bump **minor**: se agrega una opción nueva compatible; la CLI, el TOML y el core
  de detección no cambian.

## 2.4.2 — 2026-11-22

### Corregido
- **Tailscale nunca se elige como egress automático**: `tailscale0` se clasifica
  como interfaz de administración (acceso remoto a OpenCode). Con
  `EGRESS_MODE="auto"` los clientes usan la WAN y con `"vpn"` quedan en
  fail-closed, en vez de caer en un túnel sin nodo de salida que los dejaba sin
  internet. Si se fija explícitamente con `VPN_IFACE="tailscale0"`, escama
  comprueba el exit node y, si no hay, falla cerrado con mensaje explícito.
  Bump **patch**: corrige la selección de un egress que no podía dar salida.

## 2.4.1 — 2026-11-22

### Corregido
- **Menú TUI visible**: `whiptail` dibuja la interfaz en stdout y devuelve la
  selección en stderr (confirmado en su man page). Los helpers capturaban
  stdout y leían la respuesta de ahí, así que el menú quedaba dibujado en un
  pipe descartado y la selección llegaba vacía. Ahora se hereda stdout y se lee
  stderr. Bump **patch**: corrige un comportamiento que ya violaba el requisito
  de menú contextual.

## 2.4.0 — 2026-11-22

### Agregado
- **Entrada por defecto con TUI**: `escama` sin argumentos abre el menú
  interactivo cuando hay TTY; sin TTY sigue imprimiendo `status`. El menú
  muestra el estado real de AP/WAN/egress, ofrece acciones válidas para ese
  estado y delega cada mutación en los subcomandos existentes. Sin `whiptail`
  avisa cómo instalarlo y cae a `status`. La TUI permite navegar y consultar
  sin sudo: guardar delega con `sudo -n` o falla con mensaje explícito.
- **`gestion-egress` como capability**: contrato para aplicación serializada,
  limpieza sin reglas huérfanas y reutilización de los roles efectivos.

### Corregido
- **Launcher con capabilities acotadas**: solo ejecuta el `core` y la sonda
  exacta `ip link add|del escv<PID> type dummy`; cualquier otro argv de `ip`
  se rechaza con rc 2, así que no sirve como ejecutor privilegiado genérico.
- **Egress reconciliado**: cada regla lleva `--comment escama`, la limpieza lee
  `iptables-save`/`ip rule` y ya no depende del archivo de estado;
  `apply_egress` toma un `flock`, verifica el NAT en el kernel antes de
  anunciar éxito y restaura el `rp_filter` previo.
- **Roles efectivos**: `start` guarda el AP/WAN detectados en runtime y
  `stop`, `egress` y `watch` los reutilizan en vez de un TOML desactualizado.
- **Guard no forjable**: el core verifica `CapEff`; exportar
  `ESCAMA_VIA_LAUNCHER=1` ya no omite la verificación de rootless.
- **`install.sh status`** reporta también las user units y `uninstall` las
  remueve; la documentación nombra `escama.toml` como formato vigente.

### Notas
- Bump **minor**: se agrega un requisito nuevo compatible (entrada TUI y menú
  contextual). Los comandos explícitos y el modo sin TTY conservan su
  comportamiento.

## 2.3.1 — 2026-11-22

### Corregido
- **Carrera de la sonda rootless al boot**: `escama-ap` y `escama-egress`
  arrancan a la vez y ambas verificaban las capabilities creando la misma
  interfaz dummy `escama-verify`; la que perdía el `ip link add` recibía
  `EEXIST` y lo interpretaba como "las capabilities no sobreviven", fallando
  el primer arranque hasta el reintento de systemd. Ahora la dummy es única
  por proceso (`escv<PID>`), y `escama-launch` exporta
  `ESCAMA_VIA_LAUNCHER=1` para que el core invocado por systemd no repita la
  verificación (ya trae las capabilities).

## 2.3.0 — 2026-11-17

### Agregado
- **`escama qr`**: genera el QR de conexión en la terminal para unirse al AP
  desde el teléfono sin tipear la contraseña. Payload estándar
  `WIFI:T:WPA;S:<ssid>;P:<pass>;;` con escaping de `\ ; , : "` (helper
  `_wifi_qr_string`). Render vía `qrencode -t UTF8` (binario del sistema,
  ro=True: nunca sudo). Solo lectura: corre sin sudo, igual que `status`.
  Degradación amable: sin `qrencode` instalado imprime el string listo para
  pegar en un generador web + la línea `sudo apt install qrencode` (rc 1).
  `preflight` reporta `binario qrencode` como componente **opcional**: no
  afecta el estado de la instalación ni dispara el bootstrap.

## 2.2.1 — 2026-11-17

### Corregido
- **`escama egress` ya no aplica NAT a ifaces ausentes**: si `WAN_IFACE` de la
  config apunta a un dongle desenchufado, `_egress_valido()` re-detecta la WAN
  real (mismo criterio que `do_start`: el env explícito gana solo si la iface
  existe) y, si el egress elegido no existe, falla cerrado con aviso explícito
  en vez de aplicar MASQUERADE a la iface muerta anunciando éxito. Caso real:
  `start` detectó WU900, la config seguía con `wn8200nd` ausente, y
  `escama egress` rompía el egress correcto. Mismo fix en `escama watch`.

# Changelog

Todas las versiones de escama-ap. La versión vive en el archivo `VERSION` de la
raíz del repo (fuente única: la leen `escama.py`, `escama-tui.py` e
`install.sh`). Los números de abajo son semver.

La serie 0.x cubre la historia anterior al versionado: Those releases never
declared a version, así que se reconstruyen por épocas a partir de los commits
del repo. Desde 1.0.0 el bump es explícito: cada change que altera comportamiento
incluye el bump en su `tasks.md` y una entrada acá.

## 2.2.0 — 2026-11-17

### Agregado
- **`escama autorename`**: nombres legibles por defecto para adaptadores WiFi
  con nombre genérico del kernel (`wlx<MAC>`, `wlanN`, `wlpXsY`). Esquema
  `wifi-<últimos 4 hex de la MAC>` (ej. `wifi-b48f`), determinístico y sin
  estado (estable entre replugs y boots); si el nombre ya está ocupado escala
  a 6/8/10 nibbles (12 no entra en IFNAMSIZ). `sudo escama start` renombra el
  AP automáticamente la primera vez (también tras resetear la config o si
  `AP_IFACE` apunta a un genérico) via `_autorename_ap_si_corresponde`;
  `sudo escama autorename` renombra todas las WiFi genéricas presentes, WAN
  incluida. Los nombres personalizados (stonepi, WU900) nunca se
  sobreescriben y la WAN nunca se renombra automáticamente (regla de oro:
  WAN read-only).
- Refactor: la secuencia viva de `do_rename` (regla udev + retiro legacy +
  down/rename/up + rebind NM + sync toml) queda en `_rename_aplicar`,
  compartida por `rename` y `autorename`. Comportamiento de `rename` intacto
  (9 tests existentes verdes).

### Tests
- 12 nuevos (136 total): patrones genéricos, esquema y escalada de nombres,
  renombre con sync de toml, idempotencia, WAN por comando manual, root/args,
  salto de modo AP, colisión entre dongles, hook de start (renombra/no toca/
  WAN intacta), dispatch con gate de privilegio.

## 2.1.0 — 2026-11-17

### Agregado
- **`escama rename <iface> <nuevo-nombre>`**: productiza el renombre manual de
  adaptadores WiFi por regla udev (lo que se hacía a mano con `stonepi` y
  `wn8200nd`, antes `wlx<MAC>`). Deja una regla por MAC en
  `/etc/udev/rules.d/76-escama-ifaces.rules` (idempotente), retira la regla
  manual vieja de esa misma MAC de `70-persistent-net.rules` y
  `99-stonepi-ap.rules`, renombra en vivo (nmcli managed no → down →
  `ip link set name` → up → managed yes) revinculando el perfil NM activo, y
  sincroniza `AP_IFACE`/`WAN_IFACE` del `escama.toml` si apuntaban al nombre
  viejo. Validación: solo WiFi (phy80211), nombre ≤15 chars
  (`[A-Za-z0-9_-]`, sin dígito inicial), sin colisión, rechaza si la iface
  está en modo AP (`sudo escama stop` primero). Requiere sudo directo.
- TUI: entrada "R" para renombrar (delega 100% en `escama rename`).
- 9 tests nuevos (124 total): validación, secuencia viva, rollback con motivo
  real, idempotencia de regla, retiro legacy, sincronía del toml.

## 2.0.0 — 2026-11-17

### Roto (breaking)
- **La config ya no es `escama.env` (dotenv): es `/etc/escama/escama.toml`
  (TOML).** El formato viejo `KEY="value"` con comentarios `#` ya era TOML
  valido, asi que `install.sh install` migra con un rename automatico; si el
  archivo no parsea como TOML, se avisa y queda intacto (fail-closed). El core
  lee con `tomllib` (stdlib, Python 3.11+): un TOML con error de sintaxis
  aborta con motivo en vez de aplicar media config (el parser viejo saltaba
  lineas rotas en silencio). La TUI guarda con `save_config`, que reescribe
  SOLO las claves conocidas y conserva comentarios y claves ajenas.

### Seguridad
- **Sin passphrase WPA por defecto en el repo**: la default era la passphrase
  real del AP, publica en GitHub (sigue en el historial de git: rotar la
  passphrase del AP es accion del usuario). Ahora `WPA_PASSPHRASE=""` y
  `do_start` falla con error claro si esta vacia.
- **`escama-launch` con whitelist**: solo ejecuta el modo `core` y la probe de
  ip(8). Antes ejecutaba argv[1] arbitrario con CAP_NET_ADMIN/RAW/BIND_SERVICE:
  `escama-launch /bin/bash` daba una shell con caps de red a cualquier proceso
  del usuario.
- `pkill -x dnsmasq` eliminado: el dnsmasq de escama se mata por pidfile (LXC
  corre el suyo para lxcbr0 y un restart del AP lo mataba). hostapd sigue por
  nombre: es exclusivo de escama.
- `stop` ya no apaga el forwarding global: guarda el valor previo de
  `net.ipv4.ip_forward` en el state (clave IPFWD) y lo restaura (LXC/libvirt
  comparten ese sysctl y su NAT depende de el). Sin valor guardado, no toca.
- `rp_filter=2` solo sobre la iface del AP (el kernel usa max(all, iface)),
  nunca global y sin restaurar.
- El unit de sistema pierde el ExecStartPre roto: grepeaba texto inexistente
  en el env y caia a `wn8200nd` (iface ausente), con lo que el unit no booteaba.

### Corregido
- `run()` degrada a None si el binario falta o no es ejecutable
  (FileNotFoundError/PermissionError): sin traceback en maquinas peladas.
- Los comandos de SOLO LECTURA (`iw dev info`, `ip route show`, `ping`,
  `systemctl is-active`, `ip -d link`) ya no piden sudo sin launcher
  (`run(..., ro=True)`): `escama status` no pide password ni miente sin TTY.
- El reload de modulo ya no hardcodea 8192eu: lee el driver real de sysfs
  (`_driver_de`); con otro driver (p. ej. aic8800_fdrv) degrada con informacion
  en vez de rmmod del modulo equivocado.
- La TUI ya no duplica DEFAULTS ni la lista de tunnels (importa el core) y
  recalcula el rango DHCP al cambiar IP/subred (antes dejaba el rango fuera de
  la red nueva).
- install.sh borra los residuos de la instalacion vieja en /opt/escama
  (detect-iface.sh, start-ap.sh, stop-ap.sh, toggle-ap.sh, config-tui.sh,
  cleanup-warp.sh, __pycache__).
- Muerto: `module_has_ap_mode()` (nunca se llamaba) e `import shutil`.

### CI
- Job `lint`: shellcheck de install.sh + py_compile del core y la TUI.
- Job `build`: compila escama-launch.c (gcc -O2 -Wall -Werror), verifica el
  whitelist con capabilities reales y publica el binario como artifact.
- `tests` (gate push/PR) y `mutmut` (manual) quedan igual.

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
