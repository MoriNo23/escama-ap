# gestion-egress Specification

## Purpose

Define el ciclo de vida del egress del AP escama: cómo se elige, se aplica y se
limpia la salida de los clientes, con reglas que no se pisan entre sí ni quedan
huérfanas al cambiar de modo de privilegio.

## Requirements

### Requirement: Aplicación de egress serializada y verificable
Los cambios de egress MUST ejecutarse de forma serializada: el watcher y una
invocación manual de `egress` no pueden aplicar reglas al mismo tiempo. Tras
aplicar, el estado real del kernel (NAT, forwarding y policy routing) MUST
coincidir con el egress deseado; si falta una regla, la operación MUST
reportarlo y MUST NOT anunciar éxito.

#### Scenario: Cambio de VPN concurrente con egress manual
- **WHEN** el watcher detecta un cambio de túnel mientras una invocación manual de `egress` está aplicando reglas
- **THEN** las aplicaciones se serializan y el estado final corresponde a la última intención

#### Scenario: Regla requerida no instalada
- **WHEN** se aplica un egress y una regla necesaria no queda instalada en el kernel
- **THEN** la operación informa el fallo en vez de anunciar egress aplicado

### Requirement: Limpieza sin reglas huérfanas
La limpieza MUST remover todas las reglas que escama instaló para el egress
anterior, incluso si la interfaz cambió de nombre o el archivo de estado
desapareció o quedó desactualizado. MUST NOT borrar reglas instaladas por otros
sistemas.

#### Scenario: Estado ausente al detener el AP
- **WHEN** el archivo de estado no existe o no refleja el egress real y se detiene el AP
- **THEN** las reglas NAT, de forwarding, de policy routing y de rp_filter instaladas por escama se identifican en el kernel y se eliminan

#### Scenario: dos egress consecutivos
- **WHEN** se aplica un egress por VPN y después se aplica un egress por WAN
- **THEN** no queda ninguna regla del egress anterior

### Requirement: Estado independiente del modo de privilegio
La información necesaria para limpiar el egress MUST estar disponible tanto en
el modo root como en el rootless, o MUST poder reconstruirse del kernel. Una
operación en un modo MUST NOT dejar reglas creadas por el otro modo.

#### Scenario: arranque con sudo y parada como usuario
- **WHEN** el AP se levanta con privilegio y se detiene desde la unit de usuario
- **THEN** se eliminan también las reglas creadas por el arranque con privilegio

#### Scenario: arranque rootless y parada con sudo
- **WHEN** el AP se levanta desde la unit de usuario y se ejecuta `sudo escama stop`
- **THEN** se eliminan las reglas creadas en el modo rootless

### Requirement: Roles efectivos reutilizados por stop y egress
Los roles AP/WAN efectivamente usados al arrancar MUST quedar disponibles para
`stop`, `egress` y `watch`, aunque difieran de los valores del TOML. Esas
acciones MUST NOT actuar sobre una interfaz que `start` no eligió.

#### Scenario: WAN detectada distinta de la configurada
- **WHEN** `start` detecta una WAN distinta de `WAN_IFACE` y después se ejecuta `stop`
- **THEN** la limpieza usa la WAN detectada y no modifica la interfaz del TOML

#### Scenario: AP detectado distinto del configurado
- **WHEN** `start` elige una interfaz de AP detectada y después se ejecuta `egress`
- **THEN** las reglas y el killswitch se aplican contra esa interfaz detectada

### Requirement: Fallo cerrado sin salida válida
Cuando no hay un egress válido, el sistema MUST bloquear el tráfico de clientes
hacia la WAN y MUST NOT anunciar que aplicó NAT sobre una interfaz ausente.

#### Scenario: interfaz de egress ausente
- **WHEN** la interfaz elegida como egress no existe
- **THEN** los clientes quedan sin internet, su tráfico hacia la WAN queda bloqueado y la operación reporta la ausencia

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
