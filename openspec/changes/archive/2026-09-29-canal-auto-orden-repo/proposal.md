# Proposal

## Why

El AP emite en un canal **fijo** (`CHANNEL=6`, 2.4 GHz) sin ninguna lógica de
selección: si la interfaz WAN (cliente WiFi hacia el upstream) opera en el mismo
canal o en uno solapado, ambos radios se degradan (co-channel interference) y el
rendimiento del AP y de la WAN cae sin diagnóstico aparente. En paralelo, el repo
acumula deuda de organización que ya produjo problemas reales: el working tree
lleva cambios clave sin commitear (`detect_ap_iface`/`detect_wan_iface` viven solo
en disco), hay 4 documentos de análisis sueltos en la raíz (uno **referenciado
desde el código** y ninguno versionado), `docs/` (inglés) carece de `VPN-EGRESS.md`,
el README está desactualizado (dice "15 tests", hay 36), no existe script de
instalación (los symlinks y units se instalaron a mano) y `escama-ap.service`
arranca en cada boot de la PC de dev aunque ahí no se use, secuestrando `stonepi`
y dejándolo fuera de NetworkManager.

## What Changes

- **Selección automática de canal**: al `escama start`, leer el canal de la WAN
  (solo lectura, `iw dev <wan> link`) y elegir para el AP un canal de `{1, 6, 11}`
  que no se solape con el de la WAN. Nuevo setting `CHANNEL_MODE=auto|manual`
  (default `auto`; `manual` preserva el comportamiento actual con `CHANNEL` fijo).
  Si la WAN no es WiFi legible (ethernet, 5 GHz, desconectada), cae al `CHANNEL`
  del env.
- **Refactor de generación de configs**: separar la generación de hostapd y dnsmasq
  para que el watcher de egress (`watch`/`egress`) solo regenere la parte dnsmasq
  (DNS/MTU) y jamás reescriba el conf de hostapd con un canal obsoleto.
- **`install.sh`** con subcomandos `install|uninstall|enable|disable|status`:
  reemplaza la instalación a mano (symlinks, units, env) y da control reproducible
  del autostart.
- **Desactivar el autostart en la PC de dev** (`systemctl disable --now
  escama-ap.service`); en stonepi el AP sigue arrancando al boot salvo decisión
  explícita del usuario (esa máquina es el servidor del AP).
- **Higiene del repo**: commitear el working tree pendiente *antes* de cualquier
  otro cambio; mover los 4 análisis de la raíz a `docs/diagnostics/` (corrigiendo
  la referencia del código); completar `docs/VPN-EGRESS.md` en inglés; corregir
  README (36 tests, sin `PYTHONPATH`); commitear `AGENTS.md` y `openspec/`;
  ignorar `.opencode/` y `.pi/` en `.gitignore`.
- Fuera de alcance: TUI (`escama-tui.py`) sin cambios, no dividir `escama.py`
  en módulos, no usar ACS de hostapd como mecanismo primario (flaky en RTL8192EU),
  no tocar la lógica de egress/VPN vigente.

## Capabilities

### New Capabilities
- `seleccion-canal`: el AP elige al arrancar un canal 2.4 GHz que no choque con el
  de la interfaz WAN, leyendo la WAN sin modificarla (regla de oro), manteniendo
  el canal estable mientras el AP está activo.
- `instalacion`: ciclo de vida reproducible de la herramienta (instalar,
  desinstalar, habilitar y deshabilitar el autostart) sin pasos manuales a memoria.

### Modified Capabilities
- Ninguna: no existen specs previos (`openspec/specs/` está vacío).

## Impact

- **Código**: `opt/escama/escama.py` — nueva detección de canal de la WAN,
  elección automática, split de `generate_configs()`, `CHANNEL_MODE` en `DEFAULTS`.
- **Config**: `etc/escama/escama.env` — documentar `CHANNEL_MODE` (y `CHANNEL`
  como fallback). Los confs generados (`hostapd-escama.conf`,
  `dnsmasq-escama.conf`) siguen siendo productos derivados; no se editan a mano.
- **Nuevo archivo**: `install.sh` en la raíz (bash, requiere sudo para los
  targets de sistema).
- **Tests**: `tests/test_escama.py` — tests nuevos con el patrón vigente de
  `monkeypatch` sobre `run()` (tabla WAN→canal, fallbacks, manual, estabilidad en
  watch). Suite debe seguir pasando con el path explícito
  (`python3 -m pytest tests/test_escama.py -q`).
- **Docs/organización**: raíz (quedan solo README/AGENTS/install/setup.cfg),
  `docs/diagnostics/` (nuevo), `docs/VPN-EGRESS.md` (nuevo, traducción),
  `README.md`, `.gitignore`.
- **Sistemas**: estado `systemctl enable/disable` en la PC de dev (off) y stonepi
  (sin cambios por defecto); `daemon-reload` tras instalar units.
- **Riesgo principal**: default nuevo `CHANNEL_MODE=auto` cambia el canal respecto
  de la versión anterior cuando la WAN es WiFi legible — es el comportamiento
  buscado, con fallback seguro y vía de escape `manual`.
