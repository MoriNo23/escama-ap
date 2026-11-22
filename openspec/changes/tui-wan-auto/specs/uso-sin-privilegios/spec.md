# Spec Delta

## ADDED Requirements

### Requirement: Selección automática de WAN en la TUI
La TUI MUST ofrecer una opción para seleccionar la WAN automáticamente. Al
elegirla MUST guardar el valor que indica autodetección y MUST mostrar ese
estado en el menú. Cuando el valor de WAN cambie, incluida la selección de
automático, la TUI MUST reaplicar la salida sin detener el AP y MUST informar
el resultado real. Si la reaplicación falla, MUST indicar que la configuración
se guardó pero la salida no se aplicó, y MUST NOT anunciar éxito.

#### Scenario: elegir WAN AUTO
- **WHEN** el usuario elige la opción automática en el submenú de interfaz WAN
- **THEN** la configuración queda en autodetección y el menú muestra `AUTO`

#### Scenario: cambio aplicado sin reinicio
- **WHEN** se guarda un cambio de interfaz WAN, incluido pasar a automático
- **THEN** se reaplica la salida sin bajar el AP y se muestra el resultado real

#### Scenario: fallo al reaplicar la salida
- **WHEN** la reaplicación de la salida falla después de guardar
- **THEN** se indica que la configuración se guardó pero la salida no se aplicó, con el comando manual, y no se anuncia éxito
