# Spec Delta

## Purpose

Define cómo escama declara su versión y registra los cambios: una fuente única,
visible desde cualquier punto de entrada, con historial acumulativo.

## ADDED Requirements

### Requirement: Fuente única de versión
La versión MUST existir en un único lugar del repo y MUST ser la misma que
reportan todos los puntos de entrada: `escama --version`, `escama-tui --version`
e `install.sh --version`. Ningún punto de entrada MUST mantener su propia copia.

#### Scenario: Los tres puntos de entrada coinciden
- **WHEN** se consulta `escama --version`, `escama-tui --version` e `install.sh --version` en la misma máquina
- **THEN** los tres reportan la misma cadena de versión, tomada de la fuente única

#### Scenario: La copia instalada coincide con el repo
- **WHEN** se ejecuta `escama --version` (binario instalado) y se compara con la versión del repo
- **THEN** coinciden, o el sistema reporta que la instalación está desactualizada respecto del repo

### Requirement: Changelog acumulativo
El proyecto MUST mantener un `CHANGELOG.md` en el que cada cambio cerrado quede
registrado con su versión, fecha y resumen del comportamiento observable. El
changelog MUST cubrir también los cambios de la serie 0.x, de modo que el
historial no empiece recién en la primera versión del esquema nuevo.

#### Scenario: Registrar un cambio cerrado
- **WHEN** se cierra un change que introduce un cambio de comportamiento
- **THEN** el changelog incluye una entrada con la versión nueva, la fecha y el comportamiento observable afectado

#### Scenario: El changelog es consultable sin la herramienta
- **WHEN** alguien lee `CHANGELOG.md` sin instalar ni ejecutar nada
- **THEN** puede reconstruir qué versión tenía cada comportamiento

### Requirement: Disciplina semver por change
Cada change que altera comportamiento MUST venir con un bump semver explícito
en su `tasks.md`, razonado según el tipo de cambio (patch = corrección sin cambio
de contrato, minor = requisito nuevo compatible, major = ruptura). El bump MUST
ocurrir antes de archivar el change.

#### Scenario: Cambio compatible nuevo
- **WHEN** un change añade un requisito nuevo de una capability existente (p. ej. un setting más)
- **THEN** su `tasks.md` incluye un bump minor con esa justificación

#### Scenario: Corrección sin cambio de contrato
- **WHEN** un change corrige un comportamiento que ya violaba su spec
- **THEN** su `tasks.md` incluye un bump patch con esa justificación

#### Scenario: Cambio incompatible
- **WHEN** un change elimina o altera el comportamiento de un requisito existente de forma incompatible
- **THEN** su `tasks.md` incluye un bump major y la nota de migración

### Requirement: La versión se lee de la fuente, no se codifica
`escama.py`, `escama-tui.py` e `install.sh` MUST leer la versión de la fuente
única en tiempo de ejecución. Una copia literal hardcodeada de la versión en
cualquiera de los tres MUST considerarse un defecto.

#### Scenario: No queda ninguna versión duplicada
- **WHEN** se busca la cadena de versión en los tres ejecutables y en el launcher
- **THEN** aparece como valor en la fuente única, no como literal en cada archivo
