# Proposal: tui wan auto

## Why

La TUI solo permitía elegir un nombre de interfaz concreto para `WAN_IFACE`.
Si el adaptador elegido se desconecta o cambia (caso real: `WU900` caído
mientras `wlxd20dab62b48f` tiene la ruta por defecto), escama sigue haciendo NAT
por una interfaz muerta y los invitados se quedan sin internet. Salir de ese
estado exigía editar el TOML a mano y reiniciar el AP.

## What Changes

- Agregar una entrada `AUTO - detectar internet automaticamente` al submenú de
  interfaz WAN de la TUI. Al elegirla se guarda `WAN_IFACE=""`.
- Mostrar `Interfaz WAN: AUTO` en el menú cuando el valor esté vacío.
- Después de guardar, si `WAN_IFACE` cambió —incluido pasar a AUTO— ejecutar
  `escama egress` para reaplicar NAT/rutas en caliente, sin bajar `hostapd` ni
  `dnsmasq`. Mostrar el resultado real; si falla, decir que la config se guardó
  pero la salida no se aplicó y dar el comando manual.
- No cambia el core: `detect_wan_iface()` y `_egress_valido()` ya manejan el
  valor vacío. Tampoco cambia `EGRESS_MODE`, el formato del TOML ni la CLI.
  **No hay cambios breaking.**
- Bump **minor** de `2.4.2` a `2.5.0`: se agrega una opción nueva compatible
  en la TUI; entrada en `CHANGELOG.md`.

## Capabilities

### New Capabilities
(ninguna)

### Modified Capabilities
- `uso-sin-privilegios`: la TUI debe ofrecer selección automática de WAN y
  aplicar el cambio de salida sin reiniciar el AP, desde una cuenta sin sudo.

## Impact

- Código: `opt/escama/escama-tui.py` (submenú WAN y flujo de guardado).
- Tests: `tests/test_escama.py` (elección AUTO, disparo de `egress` y fallo
  explícito si no se aplica).
- Docs: `README.md`, `README.es.md` y notas de VPN egress en ambos idiomas.
- Versionado: `VERSION` y `CHANGELOG.md` con bump minor `2.5.0`.
- Sin cambios en `install.sh`, units, reglas iptables existentes ni la WAN.
