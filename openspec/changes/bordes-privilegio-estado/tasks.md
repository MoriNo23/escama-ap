# Tasks

## 1. Launcher con capabilities acotadas (D1)

- [x] 1.1 Escribir tests de caracterización que exijan rechazo de `escama-launch /usr/bin/ip` con argumentos arbitrarios y acepten solo la sonda `link add|del escv<digits> type dummy`; verificar que fallan con el launcher actual y que pasan tras el cambio (`python3 -m pytest tests/test_escama.py -q -k launcher`).
- [x] 1.2 Validar la forma de argv en `escama-launch.c` y documentar el patrón único en la cabecera; verificar con `gcc -O2 -Wall -Werror` y los smoke del job `build` (rc 2 para comando arbitrario, éxito para la sonda).
- [x] 1.3 Actualizar `docs/TECHNICAL.md` y `docs-es/TECHNICAL.md` con el alcance real de las capabilities; verificar que el texto describa la whitelist restrictiva.

## 2. Egress reconciliado y roles efectivos (D2, D3)

- [x] 2.1 Escribir tests que fallen hoy: sin state file la limpieza debe encontrar y borrar las reglas en el kernel; `stop` tras un `start` con roles detectados debe usar esos roles y no el TOML; verificar que fallan con el código actual.
- [x] 2.2 Marcar las reglas propias y enumerarlas desde el kernel en `clear_egress`, manteniendo el state file solo como caché de `IPFWD`; verificar los tests de `apply_egress`/`clear_egress` en verde.
- [x] 2.3 Persistir los roles efectivos en runtime y leerlos desde `stop`, `egress` y `watch` con fallback al TOML; verificar los tests de roles y que `escama status` sigue funcionando sin launcher.
- [x] 2.4 Actualizar `docs/VPN-EGRESS.md` y `docs-es/VPN-EGRESS.md` con la reconciliación y el fallback; verificar que los ejemplos de limpieza coincidan con el comportamiento.

## 3. Serialización y guard no forjable (D4, D6)

- [x] 3.1 Escribir tests que fallen hoy: dos aplicaciones de egress concurrentes no se pisan; exportar la variable de guard sin capabilities no omite la verificación de rootless ni el escalado; verificar el fallo previo.
- [x] 3.2 Implementar `flock` en el directorio de runtime y comprobar `CapEff` en `/proc/self/status` para el guard; verificar la suite completa en verde y que `escama preflight` corre sin sudo.
- [x] 3.3 Añadir una nota al `SECURITY.md` sobre el guard y el alcance de capabilities; verificar que no prometa secreto ni invocación arbitraria.

## 4. TUI y estado de instalación (D5, deriva de specs)

- [x] 4.1 Escribir tests que fallen hoy: la TUI sin privilegio no anuncia guardado si no pudo escribir; `install.sh status` informa user units y el TOML por separado de las units de sistema; verificar el fallo previo.
- [x] 4.2 Delegar el guardado de la TUI con `sudo -n install` sobre un archivo temporal y degradar con mensaje explícito sin tocar la config; verificar el test y una corrida manual como usuario sin privilegio.
- [x] 4.3 Hacer que `install.sh install`/`status`/`uninstall` reporten y gestionen también las user units; verificar `./install.sh status` con sistema y usuario a la vez.
- [x] 4.4 Corregir la referencia a `escama.env` en la documentación de instalación donde aún aparezca como formato vigente; verificar con búsqueda en `docs/`, `docs-es/` y `README*`.

## 5. TUI como entrada por defecto (D8, D9, D10)

- [x] 5.1 Escribir tests que fallen hoy: `escama` sin argumentos con TTY abre la TUI; sin TTY imprime `status` con el mismo código; sin `whiptail` avisa y cae a `status` sin traceback; verificar el fallo previo.
- [x] 5.2 Escribir tests del menú contextual: cabecera con estado real, acciones válidas según AP/egress y sin identificadores crudos; verificar que fallan con la TUI actual.
- [x] 5.3 Extraer el estado estructurado compartido por `status` y la TUI y cambiar el dispatch sin argumentos con su fallback; verificar suite verde y que `escama status` no cambia.
- [x] 5.4 Rediseñar el menú con agrupación, etiquetas legibles, `--default-item` y cancelación consistente; verificar manualmente con el AP arriba y abajo.
- [x] 5.5 Actualizar `README.md`, `README.es.md`, `docs/TECHNICAL.md` y `docs-es/TECHNICAL.md` con `escama` sin argumentos, el menú y el fallback; verificar que los ejemplos funcionen.

## 6. Integración y verificación en sistema real (D7)

- [x] 6.1 Agregar al job `build` una prueba con capabilities reales que lance dos sondas rootless en paralelo 20 veces y exija 0 fallos; verificar que el job pase en push.
- [x] 6.2 Probar en el host `start`/`stop` con sudo y con la unit de usuario, verificando con `iptables -S`, `ip rule` y el state file que no quedan reglas huérfanas ni se tocó la WAN.
- [x] 6.3 Ejecutar la suite completa con el path explícito (`python3 -m pytest tests/test_escama.py -q`) y `shellcheck -S error install.sh`; verificar todo en verde.

## 7. Versionado y cierre

- [x] 7.1 Bump `minor` de `2.3.1` a `2.4.0` en `VERSION`: se agrega el requisito compatible de entrada TUI y menú contextual, además de corregir los bordes que violaban sus specs (alcance de capabilities, limpieza de egress, roles efectivos, guard y guardado de TUI); los comandos explícitos y el modo sin TTY conservan su comportamiento; verificar que `escama --version`, `escama-tui --version` e `install.sh --version` coincidan y que los tests de versión pasen.
- [x] 7.2 Agregar la entrada `2.4.0` a `CHANGELOG.md` con fecha, bump razonado y comportamiento observable; verificar que el changelog cubre todos los ítems de este change.
- [x] 7.3 Ejecutar `openspec validate bordes-privilegio-estado --strict` y revisar los tres deltas contra el código implementado; verificar salida limpia.

## 8. Presentación y mantenimiento en GitHub (D11)

- [ ] 8.1 Corregir `README.md` y `README.es.md`: badge de CI dinámico sin `tests-139`, Python 3.11+, quick start y sección de TUI coordinada con 5.5, y enlaces a docs/`CHANGELOG.md`/`SECURITY.md`; verificar render en GitHub y que no queden `139` ni `3.10`.
- [ ] 8.2 Actualizar `docs/TECHNICAL.md` y `docs-es/TECHNICAL.md` con la versión de Python y el conteo de tests vigente, sin números duros; verificar con búsqueda que no queden `139`, `124` ni `3.10+`.
- [ ] 8.3 Crear `CONTRIBUTING.md`, `.github/ISSUE_TEMPLATE/bug_report.md`, `.github/ISSUE_TEMPLATE/feature_request.md` y `.github/PULL_REQUEST_TEMPLATE.md` con checklist de tests, changelog, bump y spec; verificar que GitHub los ofrezca al abrir un issue o PR.
- [ ] 8.4 Ajustar `.github/dependabot.yml` con `groups` para GitHub Actions, label `dependencies` y `commit-message` con prefijo `chore(deps)`; verificar el YAML y que el próximo PR de Dependabot agrupe las actualizaciones.
- [ ] 8.5 Completar la metadata del repo (homepage, social preview con `docs/logo/social-1280x640.png`, topics ya existentes) y verificar que el reporte privado de vulnerabilidades esté habilitado; documentar la decisión sobre Discussions/Wiki y branch protection como recomendación, no cambio automático; verificar con `gh repo view` y `gh api`.
- [ ] 8.6 Crear la release `v2.4.0` desde `VERSION` y `CHANGELOG.md` con `gh release create`; verificar `gh release view v2.4.0` y que el badge de release del README apunte a ella.

## Workflow follow-up

- Archivar el change tras la revisión.
- Sincronizar los deltas a las specs principales (`instalacion`, `uso-sin-privilegios` y la nueva `gestion-egress`).
