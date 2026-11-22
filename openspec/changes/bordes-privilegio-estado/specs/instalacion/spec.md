# Spec Delta

## MODIFIED Requirements

### Requirement: Configuración del usuario preservada
La instalación MUST conservar la configuración efectiva del usuario:
`/etc/escama/escama.toml`, y `/etc/escama/escama.env` cuando exista como
formato heredado. Nunca sobrescribirla durante `install` u upgrade. El archivo
heredado solo se renombra a TOML si parsea como TOML válido; si no parsea, se
conserva intacto y se avisa.

#### Scenario: Env con personalizaciones
- **WHEN** existe un `/etc/escama/escama.toml` editado por el usuario y se ejecuta `install.sh install`
- **THEN** el archivo conserva intacto su contenido y las novedades del repo quedan en un `.new`

#### Scenario: Heredado válido
- **WHEN** existe un `/etc/escama/escama.env` heredado que parsea como TOML y todavía no existe `escama.toml`
- **THEN** se renombra a `escama.toml` sin perder ninguna clave

#### Scenario: Heredado inválido
- **WHEN** el `escama.env` heredado no es TOML válido
- **THEN** no se migra, se conserva intacto y la instalación lo informa

### Requirement: Consulta de estado de instalación
`install.sh status` MUST reportar por componente (comandos, código,
configuración, units de sistema y units de usuario) si está instalado,
habilitado y activo, sin fallar ante componentes ausentes.

#### Scenario: Estado mixto
- **WHEN** se ejecuta `install.sh status` en la PC de desarrollo con `escama-ap.service` instalado pero `escama-egress.service` ausente
- **THEN** el comando reporta el estado real de cada componente (presente/ausente, enabled/disabled, active/inactive) y termina con éxito

#### Scenario: Units de usuario
- **WHEN** las units de usuario están instaladas y habilitadas en el directorio de usuario
- **THEN** `status` las reporta por separado de las units de sistema, con su estado real

## ADDED Requirements

### Requirement: Units de usuario en el ciclo de vida
`install.sh install` MUST instalar o actualizar las units de usuario en el
directorio de configuración del usuario real, aun cuando corra con `sudo`.
`enable --user` y `disable --user` MUST controlar el autostart de esas units
sin depender de que las units de sistema estén habilitadas. `uninstall` MUST
removerlas.

#### Scenario: instalación con sudo
- **WHEN** se ejecuta `sudo install.sh install`
- **THEN** las units de usuario quedan en el directorio del usuario real, no en el de root

#### Scenario: autostart sin unit privilegiada
- **WHEN** se ejecuta `install.sh enable --user` con la unit de sistema deshabilitada
- **THEN** el AP queda habilitado para arrancar al iniciar sesión sin unit privilegiada
