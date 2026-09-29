# Tasks

## 1. Cifras de tests al día (la suite real: 105, ~22s)

- [ ] 1.1 `AGENTS.md`: corregir las tres menciones (línea del comando de test
  "35 tests, ~16s" → "105 tests, ~22s"; la de "los 35 tests sigan en verde"; la
  fila de la tabla de skills `pytest-9-0-3`), y eliminar la nota meta
  "README está desactualizado: dice '15 tests'…" (falsa desde hace rato).
  Verificar: `grep -c '35 tests' AGENTS.md` → 0 y el comando del archivo corre
  tal cual está escrito
- [ ] 1.2 `docs/TECHNICAL.md` (EN): 19 → 105 en la tabla de componentes y en el
  comando de la sección testing (verificar contra la salida real antes de
  escribir). Verificar: `grep -c '19 unit tests\|# 19 tests' docs/TECHNICAL.md` → 0
- [ ] 1.3 `docs-es/TECHNICAL.md` (ES): resolver la inconsistencia interna
  (línea de componentes dice 19, comando dice 15) → 105 en ambas. Verificar:
  `grep -cE '19 unit tests|15 tests' docs-es/TECHNICAL.md` → 0

## 2. VPN-EGRESS: la regla real es `iif`, no `from`

- [ ] 2.1 `docs-es/VPN-EGRESS.md`: auditar TODO el archivo (no solo las líneas
  conocidas 50/116/200) y reemplazar `from <AP_SUBNET>` / `from 10.42.1.0/24`
  por `iif <AP_IFACE>`, con una línea que explique el motivo y cite
  `docs/diagnostics/DIAGNOSIS-FINAL.md` §4.1 (la variante `from` también
  capturaba tráfico originado en el host y lo secuestraba hacia el tunnel).
  Verificar: `grep -ci 'from <AP_SUBNET>\|from 10.42' docs-es/VPN-EGRESS.md` → 0
- [ ] 2.2 `docs/VPN-EGRESS.md` (EN): mismo reemplazo y misma cita en inglés
  (línea conocida 51 + auditoría completa). Verificar: mismo grep → 0
- [ ] 2.3 Verificar que lo documentado coincide con el código:
  `grep -n '"iif"' opt/escama/escama.py` muestra las reglas `ip rule … iif <ap> …
  lookup <tabla>` tal como quedaron en la doc.

## 3. TECHNICAL.md: el estado actual del sistema (ambos idiomas)

- [ ] 3.1 `docs/TECHNICAL.md` (EN): sacar `PYTHONPATH=opt/escama` del comando
  (la suite hace `sys.path.insert` sola — pitfall documentado en AGENTS.md) y
  dejar el comando canónico con path explícito. Verificar: `grep -c PYTHONPATH
  docs/TECHNICAL.md` → 0
- [ ] 3.2 `docs-es/TECHNICAL.md` (ES): ídem 3.1. Verificar: mismo grep → 0
- [ ] 3.3 `docs/TECHNICAL.md` (EN): nueva sección breve con el estado actual:
  dos modos (sudo vs rootless vía launcher ELF), `preflight`, rutas de runtime
  según privilegio (`/var`+`/etc` vs XDG), `VERSION`/`CHANGELOG`, unit de
  usuario — **apuntando a README para la tabla completa** (un solo lugar por
  tema, sin duplicar). Verificar: `grep -ci 'preflight\|rootless'
  docs/TECHNICAL.md` → >0
- [ ] 3.4 `docs-es/TECHNICAL.md` (ES): ídem 3.3. Verificar: mismo grep → >0

## 4. README y convención anti-drift

- [ ] 4.1 `README.md`: agregar la 5ª corrida a la tabla de mutmut — 105 tests,
  2846 mutantes, 1076 killed / 1417 survived ≈ 43,1% de los testeados (352 sin
  tests, 1 timeout), con la nota de la re-corrida secuencial que la confirmó.
  Verificar: la tabla tiene fila "5ª" y los números coinciden con
  `mutmut results` de la corrida del change `arranque-sin-friccion`
- [ ] 4.2 Convención: revisar que cada cifra citada en docs lleve al lado (o
  debajo) el comando con que se verifica. Verificar: lectura de las secciones
  tocadas, ninguna cifra suelta sin comando
- [ ] 4.3 Suite en verde sin tocar código (el change es solo-docs):
  `python3 -m pytest tests/test_escama.py -q` → 105 passed. Verificar: salida
  real, y `git diff --stat` muestra solo archivos de documentación

## 5. Cierre

- [ ] 5.1 Commits tipo `docs:` (uno por grupo de archivos o uno por tema) +
  push: la CI de GitHub corre sola en el push (job `tests` ya existe). **Sin
  bump semver** — el change no altera comportamiento (disciplina del repo).
  Verificar: el job `tests` de la corrida del push queda en verde
