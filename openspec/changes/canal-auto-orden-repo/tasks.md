# Tasks

## 1. Fase 0 — Commitear el working tree pendiente (antes de tocar nada)

- [ ] 1.1 Correr `python3 -m pytest tests/test_escama.py -q` (path explícito, NUNCA `python3 -m pytest` a secas) y commitear `opt/escama/escama.py` + `tests/test_escama.py` tal cual están (auto-detección de ifaces) con prefijo `feat+test:`. Verificar: suite en verde ANTES del commit (36 tests) y esos archivos fuera de `git status`
- [ ] 1.2 Commitear `etc/escama/escama.env` (ifaces de dev) con prefijo `chore(env):`. Verificar: `git diff --cached --name-only` lista solo el env
- [ ] 1.3 Commitear `AGENTS.md`, `openspec/` (scaffold + este change) y `.gitignore` si cambia, con prefijo `docs:`/`chore:`. Verificar: `git status --short` sin archivos tracked modificados y `git log --oneline` muestra los commits de la fase

## 2. Fase 1 — Feature: selección de canal (design D1–D5)

- [ ] 2.1 Implementar lectura del canal de la WAN: `iw dev <wan> link`, parsear `freq: NNNN`, validar rango 2412–2484 y convertir `canal = (freq - 2407) / 5`; devolver "" si no es legible. Verificar: tests con `run()` mockeado — freq 2412→canal 1, 2437→6, 2462→11, "Not connected."→"", freq 5180 (5 GHz)→"", freq fuera de rango→""
- [ ] 2.2 Implementar elección determinista sobre `{1, 6, 11}`: filtrar distancia ≥ 5 al canal de la WAN, elegir el de mayor distancia y en empate el menor; sin candidatos legibles, devolver `CHANNEL` del env. Verificar: tests de tabla — WAN 6→AP 1, WAN 1→AP 11, WAN 4→AP 11, WAN 11→AP 1, WAN ilegible→`CHANNEL` del env
- [ ] 2.3 Agregar `CHANNEL_MODE=auto|manual` a `DEFAULTS` (default `auto`) y documentarlo en `etc/escama/escama.env` junto a `CHANNEL` como fallback. Verificar: test `manual` usa `CHANNEL` del env sin ejecutar `iw dev <wan> link` (assert sobre comandos capturados por el mock)
- [ ] 2.4 Split de `generate_configs` (design D5): generación de hostapd (con canal resuelto) separada de dnsmasq (DNS/MTU); `watch`/`egress` solo regeneran dnsmasq; `do_start` resuelve el canal antes de generar y loguea canal elegido + canal WAN o motivo de fallback. Ajustar los mocks existentes que parchean `generate_configs` por nombre. Verificar: test nuevo "watch no reescribe `hostapd-escama.conf`" + test de trazabilidad del log + tests previos adaptados en verde
- [ ] 2.5 QA del feature: `python3 -m pytest tests/test_escama.py -q` (path explícito) en verde con los tests nuevos, y `mutmut run` (usa `setup.cfg`). Verificar: suite verde y mutantes del código nuevo killed (o survived documentados), siempre con el path explícito de tests

## 3. Fase 2 — install.sh (design D6)

- [ ] 3.1 Crear `install.sh` en la raíz: subcomandos `install|uninstall|enable|disable|status` + `--help|-h`, chequeo de root con mensaje claro, `ln -sf` idempotente, env sin sobrescribir (backup `.new`), `systemctl daemon-reload` tras instalar units, tolerante a units ausentes (warning, no error). Verificar: `bash -n install.sh` sin errores de sintaxis y `./install.sh --help` muestra el uso
- [ ] 3.2 Ejecutar `sudo ./install.sh install` en la PC de dev. Verificar: `escama --version` responde vía symlink, `systemctl list-unit-files | grep escama` lista los units presentes, y una segunda ejecución es idempotente (sin errores, mismo estado)
- [ ] 3.3 Corregir `README.md`: "15 tests"→36, eliminar la sugerencia de `PYTHONPATH`, documentar `install.sh` (install/enable/disable) y `CHANNEL_MODE` (auto/manual y fallback). Verificar: `grep -rn "15 tests\|PYTHONPATH" README.md` no devuelve nada y las secciones nuevas existen

## 4. Fase 3 — Orden del repo (docs y referencias)

- [ ] 4.1 Mover los 4 análisis de la raíz (`DIAGNOSIS-FINAL.md`, `ROOT-CAUSE-SYNTHESIS.md`, `NETWORK-BINDING-ANALYSIS.md`, `VPN-TUNNEL-ANALYSIS.md`) a `docs/diagnostics/` (son untracked: `mv` + `git add`, nombres intactos) y actualizar las referencias a `DIAGNOSIS-FINAL.md` en `opt/escama/escama.py` a la nueva ruta. Verificar: la raíz queda solo con `README.md`/`AGENTS.md`/`install.sh`/`setup.cfg` y `grep -rn "DIAGNOSIS" opt/escama/escama.py` apunta a `docs/diagnostics/`
- [ ] 4.2 Crear `docs/VPN-EGRESS.md` (inglés) traduciendo `docs-es/VPN-EGRESS.md`. Verificar: el archivo existe y cubre los mismos temas que la versión española (~217 líneas)
- [ ] 4.3 `.gitignore`: agregar `.opencode/` y `.pi/` (tooling de harness) y quitar el patrón `/var/log/escama-*.log` (path absoluto que nunca matchea dentro del repo). Verificar: `git status --short` deja de listar `.opencode/` y `.pi/` como untracked
- [ ] 4.4 Commits de la fase separados por tipo (`docs:`, `chore:`, en español, prefijo conventional). Verificar: `git status` limpio y `git log --oneline` refleja un commit por tipo de cambio

## 5. Fase 4 — Ops: autostart (spec `instalacion`)

- [ ] 5.1 PC de dev: desactivar el autostart con `sudo ./install.sh disable` (equivalente a `sudo systemctl disable --now escama-ap.service`); stonepi queda `enabled` (es el servidor del AP). Verificar: `systemctl is-enabled escama-ap.service` → `disabled`, `systemctl is-active escama-ap.service` → `inactive`
- [ ] 5.2 Verificación de integración en la PC de dev: sin procesos `hostapd`/`dnsmasq` vivos, `escama status` responde (Modo: CLIENTE) y `systemctl list-unit-files | grep escama` muestra el estado deshabilitado. Verificar: los tres checks en verde
- [ ] 5.3 En stonepi (cuando se aplique ahí): `sudo ./install.sh install && sudo ./install.sh enable` mantiene el AP al boot. Verificar: `systemctl is-enabled escama-ap.service` → `enabled` y el AP activo tras restart del servicio
