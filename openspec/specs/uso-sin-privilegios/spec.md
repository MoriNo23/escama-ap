# Uso-sin-privilegios Specification

## Purpose

Permitir operar el AP escama desde una cuenta de usuario normal, sin teclear
`sudo`: capacidades de Linux sobre el componente que habla con el kernel, estado
de runtime escribible por el usuario y arranque automático sin privileged unit.


## Requirements

### Requirement: Capacidades sobre un launcher, no sobre el script
Las operaciones que requieren privilegio (nl80211/hostapd, iptables/ip, el
puerto DHCP de dnsmasq, el sysctl de forwarding) MUST ejecutarse desde un
componente con capabilities de Linux — `CAP_NET_ADMIN`, `CAP_NET_RAW` y
`CAP_NET_BIND_SERVICE` — aplicado al launcher, no al script de Python (el kernel
ignora capabilities en scripts con shebang). El launcher MUST preservar esas
capacidades al ejecutar el núcleo.

#### Scenario: Operaciones de red sin root
- **WHEN** un usuario sin privilegios ejecuta una operación que ajusta la interfaz, las reglas de NAT o la tabla de rutas
- **THEN** la operación se completa con éxito sin que el proceso se convierta en root y sin pedir contraseña

#### Scenario: DHCP de dnsmasq en puerto privilegiado
- **WHEN** dnsmasq binds el puerto 67 y sirve el leasefile como usuario sin privilegios
- **THEN** bind y escritura funcionan gracias a `CAP_NET_BIND_SERVICE` y a rutas de runtime escribibles

#### Scenario: Verificación de capabilities
- **WHEN** se inspecciona el componente ejecutable que invoca al núcleo
- **THEN** muestra `cap_net_admin`, `cap_net_raw` y `cap_net_bind_service` en su lista de capabilities

### Requirement: Estado de runtime escribible por el usuario
Los archivos de estado de runtime que hoy viven en rutas de root (pidfile,
log) MUST escribirse en rutas del usuario (XDG o equivalents), y la ruta
privilegiada MUST usarse solo cuando el proceso efectivamente corre como root.
Ambos casos MUST quedar registrados en el log para diagnóstico.

#### Scenario: AP corriendo como usuario
- **WHEN** el AP se levanta en modo rootless
- **THEN** pidfile y log se crean bajo el home del usuario y son legibles por él

#### Scenario: AP corriendo como root
- **WHEN** el AP se levanta con privilegio
- **THEN** el estado va a las rutas de sistema y el log lo indica

### Requirement: Arranque automático sin privileged unit
El arranque al boot MUST poder configurarse como **unit de usuario**
(`systemctl --user`), de modo que el AP levante al iniciar sesión sin privileged
unit de sistema. El modo rootless MUST seguir funcionando cuando la unit de
sistema no está habilitada.

#### Scenario: Autostart de usuario
- **WHEN** el usuario habilita la unit de usuario y reinicia la sesión
- **THEN** el AP levanta sin pedir privilegio y sin depender de la unit de sistema

#### Scenario: Convivencia de modos
- **WHEN** la unit de sistema está deshabilitada y la de usuario habilitada
- **THEN** el AP opera igual y `status` refleja el modo de usuario

### Requirement: Operaciones de solo lectura sin privilegio
Los subcomandos de solo lectura (`status`, `--help`, `--version`) MUST ejecutarse
sin privilegio y MUST NOT solicitar elevación. Los subcomandos que mutan el
sistema MUST funcionar en modo rootless cuando el launcher tiene capabilities, y
MUST escalar por el mecanismo de privilegio del proyecto cuando no las tiene.

#### Scenario: Consultar estado sin sudo
- **WHEN** un usuario sin privilegios ejecuta `escama status`
- **THEN** obtiene el estado real del AP sin prompted de privilegio y con código de salida coherente

#### Scenario: Mutar sin sudo en modo rootless
- **WHEN** un usuario sin privilegios ejecuta `escama restart` con el launcheryzado
- **THEN** el AP se reinicia sin pedir sudo

#### Scenario: Mutar sin capabilities
- **WHEN** un usuario sin privilegios ejecuta una acción mutante y el launcher no tiene capabilities
- **THEN** la acción escala por el mecanismo de privilegio del proyecto con un único prompt, o falla con un mensaje que explique cómo habilitar el modo rootless

### Requirement: Degradación explícita de lo no-rootless
Lo que no puede ser rootless MUST degradarse con mensaje explícito que diga qué
no se pudo hacer y por qué: la recarga del módulo del kernel
(`rmmod`/`modprobe`, `CAP_SYS_MODULE`) y la gestión de NetworkManager sobre la
interfaz (`nmcli device set managed no`, que requiere autorización de NM). El
sistema MUST NOT omitir silenciosamente esos pasos, y MUST NOT|reportarlos como
exitosos.

#### Scenario: Sin capabilities de módulo
- **WHEN** una operación requiere recargar el módulo y el proceso no tiene `CAP_SYS_MODULE`
- **THEN** el log y la salida dicen que la recarga no se hizo y explican el motivo

#### Scenario: NM no autoriza el cambio
- **WHEN** `nmcli device set managed no` falla por falta de autorización
- **THEN** se informa del fallo con su motivo y se indica si impide o no el arranque

### Requirement: Preflight del modo rootless
El preflight MUST determinar si el modo rootless es viable en esta máquina
(sistema de archivos con soporte de xattrs, capabilities aplicables, unit de
usuario disponible) y MUST negarlo explícitamente cuando no lo es, ofreciendo el
modo con privilegio ya existente como camino válido.

#### Scenario: Rootless viable
- **WHEN** el preflight se ejecuta en una máquina donde todas las condiciones se cumplen
- **THEN** informa que el modo rootless está disponible

#### Scenario: Rootless no viable
- **WHEN** falta alguna condición (por ejemplo, el sistema de archivos no soporta las capabilities necesarias)
- **THEN** informa que el modo rootless no está disponible, nombra la condición faltante y deja claro que el modo con privilegio sigue funcionando
