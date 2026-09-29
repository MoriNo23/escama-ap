# Proposal

## Why

La documentación quedó desactualizada respecto del código tras dos changes
consecutivos (`canal-auto-orden-repo` y `arranque-sin-friccion`), y varios de
esos desvíos ya confunden a quien los lee: las cifras de tests son falsas en
tres archivos (docs/TECHNICAL.md dice 19, docs-es/TECHNICAL.md dice 19 en una
línea y 15 en otra —inconsistente consigo mismo—, AGENTS.md dice 35; la real es
105), y VPN-EGRESS documenta una regla de policy routing que el código ya no
usa (`from <AP_SUBNET>`) cuando la actual (`iif <ap>`) fue un fix de diagnóstico
medido. El modo rootless, el preflight, el versionado y las rutas XDG —todo lo
que este último change entregó— no aparecen en TECHNICAL.md (0 menciones).

## What Changes

- **Cifras de tests al día**: `docs/TECHNICAL.md` (19 → 105), `docs-es/TECHNICAL.md`
  (19/15 → 105, eliminando la inconsistencia interna), `AGENTS.md` (35 → 105,
  ~16s → ~22s) y su nota meta "README dice 15 tests" (ya corregida hace rato).
- **VPN-EGRESS en ambos idiomas**: `from <AP_SUBNET>` → `iif <AP_IFACE>` con el
  motivo (la variante `from` secuestraba tráfico originado en el host hacia la
  tabla del tunnel; ver `docs/diagnostics/DIAGNOSIS-FINAL.md` §4.1). A auditar
  ambas versiones completas, no solo las líneas conocidas (docs-es 50/116/200,
  docs 51).
- **TECHNICAL.md en ambos idiomas**: sacar `PYTHONPATH=opt/escama` (la suite hace
  `sys.path.insert` sola) y usar el comando canónico con path explícito.
- **TECHNICAL.md en ambos idiomas**: cubrir el estado actual del sistema — dos
  modos (sudo vs rootless), `preflight`, rutas de runtime según privilegio,
  `VERSION`/`CHANGELOG`, unit de usuario — apuntando a README para la tabla
  completa (un solo lugar por tema, sin duplicar).
- **README**: agregar la 5ª corrida a la tabla de mutmut (105 tests, 2846
  mutantes, 1076 killed / 1417 survived ≈ 43,1% de los testeados, 352 sin
  tests, 1 timeout — medido hoy, reproducido en re-corrida secuencial).
- **Convención anti-drift**: cada cifra citada en docs lleva al lado el comando
  con que se verifica, para que el desvío sea autoevidente.

## Capabilities

### New Capabilities
- Ninguna: es un change **solo-docs**. No crea ni modifica requisitos ni
  comportamiento observable del sistema (declarado `skip_specs: true`).

### Modified Capabilities
- Ninguna. La spec `versionado` ya exige CHANGELOG por change cerrado; este
  change solo lo cumple en docs, no lo cambia.

## Impact

- **Archivos**: `docs/TECHNICAL.md`, `docs-es/TECHNICAL.md`, `docs/VPN-EGRESS.md`,
  `docs-es/VPN-EGRESS.md`, `README.md`, `AGENTS.md`.
- **Código**: ninguno. Sin tocar `opt/escama/`, `install.sh` ni tests.
- **Versionado**: **sin bump semver** — la disciplina del repo exige bump en
  changes que alteran comportamiento; este no lo altera (commits `docs:`).
- **Riesgo principal**: repetir cifras ya viejas al escribir las nuevas. Mitigado
  por la convención del comando al lado de cada cifra y por verificar cada
  número contra la salida real antes de committear.
