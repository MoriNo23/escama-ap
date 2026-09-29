# Spec Delta

## Purpose

Que escama se pueda usar en una máquina recién clonada sin pasos manuales: si
falta la instalación, el propio programa la completa o dice exactamente qué falta.

## ADDED Requirements

### Requirement: Detección de instalación faltante o incompleta
Antes de ejecutar una acción, escama MUST comprobar si la instalación está
completa: symlinks de los comandos, código en `/opt/escama`, configuración y
units de sistema. La comprobación MUST distinguir entre "no instalado" y
"instalado pero desactualizado respecto del repo" (código o versión distintos).

#### Scenario: Máquina nueva sin nada
- **WHEN** se ejecuta `escama start` en una máquina sin symlinks, sin `/opt/escama` y sin units
- **THEN** escama detecta la instalación faltante e informa qué componentes faltan

#### Scenario: Instalado pero desactualizado
- **WHEN** el código instalado en `/opt/escama` no coincide con el del repo
- **THEN** escama lo distingue de "no instalado" y lo reporta como desactualizado, con la versión de cada lado

#### Scenario: Instalación completa
- **WHEN** la instalación está completa y coherente con el repo
- **THEN** la acción se ejecuta normalmente, sin bootstrap ni avisos de instalación

### Requirement: Bootstrap con un único prompt de privilegio
Cuando la instalación falte y el usuario lo acepte, escama MUST delegar la
instalación a `install.sh install` y MUST pedir el privilegio **una sola vez**,
con un mensaje previo que declare qué va a hacer. Si el usuario rechaza, escama
MUST explicar cómo instalarlo manualmente y terminar sin cambios.

#### Scenario: Aceptar el bootstrap
- **WHEN** el usuario acepta instalar y el sistema pide privilegio
- **THEN** se ejecuta la instalación, escama la re-verifica y continúa con la acción que la originó

#### Scenario: Rechazar el bootstrap
- **WHEN** el usuario rechaza el prompt de privilegio
- **THEN** escama imprime el comando de instalación manual, no modifica el sistema y termina con error claro

#### Scenario: Un solo prompt
- **WHEN** el bootstrap instala y la acción original continúa (por ejemplo, levantar el AP)
- **THEN** el usuario no ve más de una petición de privilegio en toda la operación

### Requirement: Preflight sin cambios
Un chequeo de preflight MUST listar el estado de cada componente (comandos,
código, env, units, unit de usuario, capabilities) y MUST poder ejecutarse sin
privilegios y sin modificar nada. Un preflight MUST señalar específicamente los
requisitos que no se pueden satisfacer en esta máquina.

#### Scenario: Preflight en máquina compliant
- **WHEN** se ejecuta el preflight en una máquina con todo en su lugar
- **THEN** reporta cada componente en verde sin pedir privilegio ni cambiar nada

#### Scenario: Preflight con requisitos insatisfebles
- **WHEN** falta un requisito estructural para el modo rootless (por ejemplo, no hay forma de aplicar capabilities)
- **THEN** el preflight lo nombra explícitamente y declara que el modo rootless no está disponible, en vez de fallar en la primera operación

### Requirement: La instalación sigue siendo la vía canónica
La auto-instalación MUST delegar en `install.sh` y MUST NOT duplicar la lógica de
instalación. `install.sh` MUST seguir siendo invocable manualmente con los mismos
resultados, y sus requisitos vigentes (idempotencia, preservation del `env`) MUST
mantenerse.

#### Scenario: Una sola implementación de la instalación
- **WHEN** se compara lo que hace el bootstrap con lo que hace `install.sh install` invocado a mano
- **THEN** el resultado sobre el sistema es el mismo
