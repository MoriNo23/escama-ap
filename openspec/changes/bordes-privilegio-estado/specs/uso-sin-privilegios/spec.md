# Spec Delta

## ADDED Requirements

### Requirement: Alcance mínimo de las capabilities del launcher
El launcher MUST exponer sus capabilities únicamente a las operaciones propias
de escama. MUST NOT actuar como ejecutor genérico de `ip(8)` (ni de cualquier
otro binario) con argumentos elegidos por el llamador. La sonda de
capabilities, si usa `ip`, MUST estar restringida a la operación concreta que
escama necesita.

#### Scenario: invocación arbitraria de ip
- **WHEN** un usuario invoca `escama-launch /usr/bin/ip` con argumentos distintos de la sonda de escama
- **THEN** el launcher rechaza la invocación sin conceder capabilities

#### Scenario: sonda legítima del rootless
- **WHEN** el core verifica el modo rootless mediante su sonda de interfaz dummy
- **THEN** la sonda se ejecuta con las capabilities necesarias y la interfaz se elimina al terminar

### Requirement: Guard de re-ejecución no forjable
El hecho de que el núcleo haya sido invocado por el launcher MUST verificarse
por un mecanismo que otro proceso no pueda simular exportando una variable de
entorno. Una variable suelta NO MUST ser suficiente para omitir la verificación
de rootless o el escalado de privilegios.

#### Scenario: guard falso sin capabilities
- **WHEN** un proceso sin capabilities exporta la variable de guard antes de ejecutar una acción mutante
- **THEN** la acción no omite la verificación de rootless ni el escalado por ese solo motivo

#### Scenario: guard legítimo desde el launcher
- **WHEN** el launcher ejecuta el núcleo con sus capabilities
- **THEN** el núcleo reconoce la invocación y no se re-lanza a sí mismo ni pide privilegio

### Requirement: Guardado de configuración con degradación explícita
Las acciones que escriben la configuración del usuario, incluida la TUI, MUST
ejecutarse con el privilegio suficiente o fallar con un mensaje que nombre el
motivo y la alternativa. MUST NOT terminar con una excepción no controlada ni
anunciar éxito si el archivo no se escribió.

#### Scenario: TUI sin privilegio
- **WHEN** la TUI intenta guardar `escama.toml` desde una cuenta sin privilegio
- **THEN** delega el guardado a un camino con privilegio o informa explícitamente que no pudo hacerlo

#### Scenario: delegación no disponible
- **WHEN** no hay forma de delegar el guardado y el archivo permanece sin cambios
- **THEN** se informa el motivo, se indica el comando manual y no se muestra un mensaje de guardado correcto

### Requirement: Entrada por defecto de la TUI
Cuando `escama` se invoca sin argumentos en una terminal interactiva, el
sistema MUST abrir la TUI en vez de imprimir solo el estado. Sin terminal
interactiva MUST imprimir el estado actual con el mismo código de salida que
hoy. Si `whiptail` no está instalado, MUST avisar con el comando de instalación
y caer al estado sin traceback.

#### Scenario: escama sin argumentos con TTY
- **WHEN** el usuario ejecuta `escama` en una terminal interactiva
- **THEN** se abre la TUI con el menú principal

#### Scenario: escama sin argumentos sin TTY
- **WHEN** `escama` corre desde un script o una unit sin terminal
- **THEN** imprime el estado actual y termina con el mismo código que `escama status`

#### Scenario: whiptail ausente
- **WHEN** `whiptail` no está instalado
- **THEN** se avisa con el comando de instalación y se imprime el estado sin traceback

### Requirement: Menú contextual y navegación sin privilegio
La TUI MUST mostrar en la cabecera el estado real del AP y del egress, y MUST
ofrecer acciones válidas para ese estado con etiquetas legibles, sin exponer
identificadores internos. La navegación y las consultas MUST funcionar sin
privilegio; las acciones mutantes MUST delegar en los subcomandos de escama y
mostrar el resultado real.

#### Scenario: estado en la cabecera
- **WHEN** se abre la TUI
- **THEN** muestra AP, WAN, egress y SSID leídos del estado real, no de valores fijos

#### Scenario: acciones según el estado
- **WHEN** el AP está caído y hay un túnel VPN disponible
- **THEN** la TUI ofrece arrancar el AP y usar esa salida, y no ofrece acciones que no correspondan a ese estado

#### Scenario: navegación sin sudo
- **WHEN** un usuario sin privilegio recorre el menú o consulta el estado
- **THEN** no se le pide contraseña

#### Scenario: mutación desde la TUI
- **WHEN** se elige una acción mutante en el menú
- **THEN** se delega en el subcomando correspondiente y se muestra éxito o fallo real, sin anunciar éxito falso
