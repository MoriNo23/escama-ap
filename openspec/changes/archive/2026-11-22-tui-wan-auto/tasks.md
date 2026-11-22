# Tasks

## 1. Tests de caracterización

- [x] 1.1 Escribir un test que falle hoy: el submenú de WAN ofrece `AUTO` y al elegirlo el valor guardado es `WAN_IFACE=""`; verificar el fallo previo con `python3 -m pytest tests/test_escama.py -q -k wan_auto`.
- [x] 1.2 Escribir un test que falle hoy: al guardar un cambio de WAN, se ejecuta `escama egress` sin detener el AP y se muestra su resultado; verificar el fallo previo.
- [x] 1.3 Escribir un test que falle hoy: si `escama egress` falla, se dice que la config se guardó pero la salida no se aplicó, con el comando manual, y no se anuncia éxito; verificar el fallo previo.

## 2. TUI: opción AUTO y aplicación en caliente

- [x] 2.1 Agregar `AUTO - detectar internet automaticamente` al submenú de WAN y mostrar `Interfaz WAN: AUTO` cuando el valor esté vacío; verificar test 1.1 en verde.
- [x] 2.2 Después de guardar, si `WAN_IFACE` cambió, ejecutar `escama egress` en caliente y mostrar el resultado real; verificar test 1.2 en verde y que no se llama a `stop`/`restart`.
- [x] 2.3 Manejar el fallo de `egress` con mensaje explícito y comando manual, sin anunciar guardado exitoso de la salida; verificar test 1.3 en verde.
- [x] 2.4 Ejecutar la suite completa con el path explícito (`python3 -m pytest tests/test_escama.py -q`); verificar todo en verde.

## 3. Documentación y versionado

- [x] 3.1 Documentar `WAN AUTO` en `README.md`, `README.es.md` y las notas de VPN egress en ambos idiomas, aclarando que el cambio se aplica sin reiniciar; verificar que ambos idiomas coincidan.
- [x] 3.2 Bump `minor` de `2.4.2` a `2.5.0` en `VERSION`: se agrega una opción nueva compatible en la TUI; verificar que `escama --version`, `escama-tui --version` e `install.sh --version` coincidan y agregar la entrada en `CHANGELOG.md`.
- [x] 3.3 Ejecutar `openspec validate tui-wan-auto --strict` y revisar el delta contra el comportamiento implementado; verificar salida limpia.

## Workflow follow-up

- Archivar este change junto con los dos anteriores y sincronizar sus deltas a las specs principales sin duplicar capabilities.
- Publicar la release `v2.5.0` desde `VERSION` y `CHANGELOG.md`.
