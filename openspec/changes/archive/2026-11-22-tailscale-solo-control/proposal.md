# Proposal: tailscale solo control

## Why

Tailscale está instalado en el host y en el Android del usuario para acceder a
OpenCode en remoto: es un plano de control, no la salida a internet de los
invitados del AP. Hoy `tailscale0` está en `VPN_KNOWN`, así que con
`EGRESS_MODE="auto"` o `"vpn"` escama lo elige como egress. Sin exit node
(`ExitNode: None`, verificado) eso deja a los clientes sin internet, aunque el
acceso remoto a OpenCode siga funcionando. La config actual (`wan`) mitiga el
caso, pero el riesgo queda latente para cualquiera que cambie de modo.

## What Changes

- Quitar `tailscale0` de la detección automática de egress y tratarlo como
  interfaz de administración: `auto` nunca lo elige solo.
- Si alguien lo fija explícitamente con `VPN_IFACE="tailscale0"`, validar que
  exista exit node; si no, fallar cerrado con mensaje explícito en vez de
  anunciar un egress que no lleva a internet.
- Agregar escenarios a `gestion-egress`, tests de detección y una nota en la
  documentación de VPN egress en ambos idiomas.
- No cambia `EGRESS_MODE`, el formato de `escama.toml` ni la interfaz de
  comandos. **No hay cambios breaking.**
- Bump **patch** de `2.4.1` a `2.4.2`: corrige un comportamiento que ya
  violaba el contrato de egress verificado; entrada en `CHANGELOG.md`.

## Capabilities

### New Capabilities
(ninguna)

### Modified Capabilities
- `gestion-egress`: selección de egress — `tailscale0` se clasifica como plano
  de control y no es candidato automático; el uso explícito exige exit node.
  La capability fue introducida por el change `bordes-privilegio-estado` y
  todavía está pendiente de sync a las specs principales.

## Impact

- Código: `opt/escama/escama.py` (detección de túneles y validación de egress).
- Tests: `tests/test_escama.py` (detección automática, pin explícito sin exit
  node y mensaje de fallo).
- Docs: `docs/VPN-EGRESS.md` y `docs-es/VPN-EGRESS.md`.
- Versionado: `VERSION` y `CHANGELOG.md` con bump patch `2.4.2`.
- No toca reglas de NAT existentes ni la WAN: la config en `wan` queda igual.
