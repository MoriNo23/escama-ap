# Proposal: bordes de privilegio y estado

## Why

La revisión de arquitectura encontró fallos en los **bordes** del sistema: el
launcher concede `CAP_NET_ADMIN` para `ip(8)` con argumentos arbitrarios, el
estado de egress se parte según `euid` (root usa `/run`, la unit de usuario usa
`/run/user/<uid>`), los roles detectados en `start` no se persisten para `stop`,
y la TUI intenta escribir un TOML de root sin capabilities. El núcleo (config,
AP, canal, validación) está sano; estos bordes pueden dejar reglas huérfanas o
actuar sobre la WAN. Además, `egress` es hoy una capability central sin spec.

También hay un vacío de uso: `escama` sin argumentos solo imprime `status`, y
la TUI se alcanza con `escama-tui` + sudo, sin mostrar el estado real ni
sugerir acciones. El usuario pidió que escribir `escama` abra una TUI agradable
y contextual.

El repositorio es público: su presentación en GitHub y el mantenimiento de su
configuración (badges, Dependabot, releases, plantillas, política de seguridad)
también forman parte del producto. Hoy hay datos duros desactualizados
(`tests-139` frente a 147, Python 3.10+ frente al 3.11 que exige `tomllib`) y
ajustes de metadata pendientes.

## What Changes

- Restringir la whitelist del launcher: de `execv(/usr/bin/ip, argv)` arbitrario
  a la única sonda que el propio escama necesita (`link add/del escv<PID> type
  dummy`), o ejecutar la sonda dentro del launcher sin exponer `ip`.
- Unificar el estado de egress: una sola fuente de verdad legible por root y por
  el usuario, y reconciliación contra el kernel (reglas `iptables`/`ip rule`)
  para no depender de un archivo que puede quedar viejo o partido.
- Persistir los roles efectivos (AP/WAN) que `start` detecta, para que `stop`,
  `egress` y `watch` no vuelvan a un TOML desactualizado. La WAN sigue siendo
  solo lectura salvo configuración explícita.
- Serializar `apply_egress` con un lock para que `watch` y `escama egress` no se
  pisen, y hacer la escritura de estado atómica.
- Delegar el guardado de configuración de la TUI a un camino con privilegio, con
  degradación explícita cuando no pueda hacerse (spec `uso-sin-privilegios` ya
  exige nombrar lo que no es rootless).
- Corregir la deriva de specs: `instalacion` nombra `escama.env` (hoy es TOML)
  y no describe las user units; el preflight no informa de la unit de usuario
  ni de las capabilities instaladas.
- Endurecer el guard `ESCAMA_VIA_LAUNCHER`: dejar de confiar ciegamente en una
  variable de entorno exportable por cualquier proceso.
- Abrir la TUI cuando se ejecuta `escama` sin argumentos y hay TTY; sin TTY
  (scripts, units) se mantiene el `status` actual. Los comandos explícitos no
  cambian.
- Hacer la TUI contextual: cabecera con estado real (AP, WAN, egress, SSID),
  acciones válidas para ese estado y etiquetas legibles en vez de códigos.
- Permitir navegar y consultar desde la TUI sin privilegio; las acciones
  mutantes delegan en los subcomandos existentes y muestran el resultado real.
- Actualizar la presentación en GitHub: README en inglés y español con quick
  start, sección de TUI, requisitos correctos y badges sin contadores duros.
- Publicar `CONTRIBUTING.md` y plantillas de issue/PR con checklist de tests,
  changelog, bump y artefactos OpenSpec.
- Mantener la configuración de GitHub: Dependabot agrupado, alertas y reporte
  privado de vulnerabilidades verificados, y releases creadas desde `VERSION`
  y `CHANGELOG.md`.
- No cambia el formato de configuración ni la interfaz de los comandos
  explícitos. **No hay cambios breaking.**

## Capabilities

### New Capabilities
- `gestion-egress`: ciclo de vida del egress — selección, aplicación atómica y
  serializada de NAT/policy routing, reconciliación con el kernel y limpieza
  sin reglas huérfanas, indistintamente del modo root o rootless.

### Modified Capabilities
- `uso-sin-privilegios`: alcance mínimo de las capabilities del launcher,
  guard de re-ejecución no forjable, degradación explícita al guardar config y
  entrada por defecto / menú contextual de la TUI sin privilegio.
- `instalacion`: inventario real de artefactos (TOML, user units) en el ciclo
  de vida y en `status`.

## Impact

- Código: `opt/escama/escama-launch.c`, `opt/escama/escama.py` (dispatch sin
  argumentos, rutas de estado, egress, `do_start`/`do_stop`, preflight),
  `opt/escama/escama-tui.py` (menú y estado), `install.sh` y los units de
  usuario.
- Tests: `tests/test_escama.py` gana tests de propiedad sobre rutas/estado y una
  suite de integración con capabilities reales (la actual mockea todo el límite
  del sistema y no detectó la carrera de arranque ni el estado partido).
- CI: nuevo job de integración; se mantiene `mutmut` manual.
- GitHub: `README.md`, `README.es.md`, `docs/TECHNICAL.md`,
  `docs-es/TECHNICAL.md`, `.github/`, metadata del repo y publicación de la
  release `v2.4.0`; sin cambios de comportamiento runtime.
- Estructura: partición posterior del monolito en módulos (privilegios, red,
  configuración, CLI) como consecuencia, no como requisito de este change.
- Versionado: bump `minor` a `2.4.0` con entrada en `CHANGELOG.md`: agrega el
  requisito nuevo de entrada TUI y UX contextual; es compatible porque los
  comandos explícitos y el modo sin TTY conservan su comportamiento.
