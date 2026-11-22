# Spec Delta

## ADDED Requirements

### Requirement: Tailscale es plano de control, no egress automático
Las interfaces que sirven de acceso de administración remota, incluida
`tailscale0`, MUST NOT seleccionarse automáticamente como egress aunque estén
activas. Un egress fijado explícitamente a una interfaz de Tailscale MUST
validar que exista un nodo de salida activo; si no existe, la operación MUST
fallar cerrado con un mensaje que nombre el motivo y MUST NOT anunciar que
aplicó NAT o egreso alguno.

#### Scenario: auto ignora Tailscale
- **WHEN** `tailscale0` está activo, `EGRESS_MODE=auto` y no hay otro túnel válido
- **THEN** el sistema usa la WAN como salida y no instala reglas hacia `tailscale0`

#### Scenario: fijar Tailscale sin nodo de salida
- **WHEN** `VPN_IFACE=tailscale0` y Tailscale no tiene un nodo de salida activo
- **THEN** la operación falla con un mensaje explícito y no anuncia egress aplicado

#### Scenario: fijar Tailscale con nodo de salida
- **WHEN** `VPN_IFACE=tailscale0` y Tailscale tiene un nodo de salida activo
- **THEN** se aplica el egress por `tailscale0` con las reglas habituales del modo VPN

#### Scenario: modo vpn con único túnel administrativo
- **WHEN** `EGRESS_MODE=vpn` y el único túnel presente es `tailscale0` sin nodo de salida
- **THEN** los clientes quedan sin internet en fail-closed, sin aplicar NAT hacia `tailscale0`
