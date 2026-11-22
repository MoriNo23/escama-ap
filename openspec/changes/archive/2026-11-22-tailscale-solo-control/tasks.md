# Tasks

## 1. Tests de caracterización

- [x] 1.1 Escribir un test que falle hoy: con `tailscale0` activo, `EGRESS_MODE=auto` y sin otro túnel válido, `resolve_egress` debe devolver la WAN y no seleccionar `tailscale0`; verificar el fallo previo con `python3 -m pytest tests/test_escama.py -q -k tailscale`.
- [x] 1.2 Escribir un test que falle hoy: con `VPN_IFACE=tailscale0` y Tailscale sin nodo de salida, la operación debe fallar cerrado, no anunciar egress aplicado y nombrar el motivo en el mensaje; verificar el fallo previo.
- [x] 1.3 Escribir un test de caracterización con nodo de salida activo: el pin explícito a `tailscale0` debe aplicar el egress por ese túnel con las reglas habituales; verificar que el comportamiento se conserva.

## 2. Selección y validación de egress

- [x] 2.1 Clasificar `tailscale0` como interfaz de administración: quitarlo de la detección automática sin impedir que se fije explícitamente con `VPN_IFACE`; verificar tests 1.1 y 1.3 en verde.
- [x] 2.2 Validar el nodo de salida solo cuando Tailscale se fija explícitamente, con fallo cerrado y mensaje que nombre el motivo; verificar test 1.2 en verde y que no se instalan reglas NAT hacia un túnel sin ruta.
- [x] 2.3 Ejecutar la suite completa con el path explícito (`python3 -m pytest tests/test_escama.py -q`); verificar que no cambia el modo `wan` ni emite comandos de escritura sobre la WAN.

## 3. Documentación y versionado

- [x] 3.1 Actualizar `docs/VPN-EGRESS.md` y `docs-es/VPN-EGRESS.md` con el rol de Tailscale como plano de control, el uso explícito permitido y el requisito de nodo de salida; verificar que ambos idiomas describan el mismo comportamiento.
- [x] 3.2 Bump `patch` de `2.4.1` a `2.4.2` en `VERSION`: se corrige la selección automática de un túnel que no podía dar egress, sin cambiar contratos, CLI ni formato de config; verificar que `escama --version`, `escama-tui --version` e `install.sh --version` coincidan y agregar la entrada en `CHANGELOG.md`.
- [x] 3.3 Ejecutar `openspec validate tailscale-solo-control --strict`; verificar salida limpia y que el delta cubra los cuatro escenarios de `gestion-egress`.

## Workflow follow-up

- Archivar este change junto con `bordes-privilegio-estado` y sincronizar `gestion-egress` a las specs principales sin duplicarla.
- Publicar la release `v2.4.2` desde `VERSION` y `CHANGELOG.md`.
