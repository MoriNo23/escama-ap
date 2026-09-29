# Spec Delta

## Purpose

Define cómo el AP "escama" elige su canal 2.4 GHz al arrancar para no interferir
con la interfaz WAN (cliente WiFi del upstream), leyendo la WAN sin modificarla.

## ADDED Requirements

### Requirement: Elección de canal sin conflicto con la WAN
Cuando `CHANNEL_MODE=auto` y la WAN es una interfaz WiFi asociada a un upstream
en la banda 2.4 GHz, el AP MUST arrancar en un canal del conjunto `{1, 6, 11}`
cuya distancia al canal de la WAN sea mayor o igual a 5 (sin solapamiento de
20 MHz). La elección MUST ser determinista: se prefiere el candidato más lejano
al canal de la WAN y, en caso de empate, el de menor número.

#### Scenario: WAN en el canal 6
- **WHEN** la WAN está asociada en el canal 6 y se ejecuta `escama start` con `CHANNEL_MODE=auto`
- **THEN** el AP arranca en el canal 1 (empate entre 1 y 11 a distancia 5; gana el menor) y el conf de hostapd generado no contiene ningún canal del 2 al 10

#### Scenario: WAN en el canal 1
- **WHEN** la WAN está asociada en el canal 1 y se ejecuta `escama start` con `CHANNEL_MODE=auto`
- **THEN** el AP arranca en el canal 11 (distancia 10, mayor que la del 6)

#### Scenario: WAN en un canal intermedio
- **WHEN** la WAN está asociada en el canal 4 (solapa con 1 y con 6) y se ejecuta `escama start` con `CHANNEL_MODE=auto`
- **THEN** el AP arranca en el canal 11, único candidato sin solapamiento

### Requirement: Fallback cuando la WAN no aporta canal legible
Cuando `CHANNEL_MODE=auto` y no puede leerse un canal 2.4 GHz de la WAN (WAN por
Ethernet, WAN en banda 5 GHz, WAN ausente o sin asociación), el AP MUST arrancar
usando el valor `CHANNEL` del env, sin fallar y sin bloquear el arranque.

#### Scenario: WAN desconectada
- **WHEN** la WAN es WiFi pero no está asociada a ningún upstream y se ejecuta `escama start` con `CHANNEL_MODE=auto`
- **THEN** el AP arranca con el `CHANNEL` del env y el arranque termina en éxito

#### Scenario: WAN en banda de 5 GHz
- **WHEN** la WAN está asociada en 5 GHz (no solapa con el AP 2.4 GHz) y se ejecuta `escama start` con `CHANNEL_MODE=auto`
- **THEN** el AP arranca con el `CHANNEL` del env

### Requirement: Modo manual preserva el comportamiento actual
Cuando `CHANNEL_MODE=manual`, el AP MUST arrancar exactamente con el valor
`CHANNEL` del env, sin intentar detectar el canal de la WAN.

#### Scenario: Manual ignora la detección
- **WHEN** `CHANNEL_MODE=manual` con `CHANNEL=6`, la WAN está asociada en el canal 6, y se ejecuta `escama start`
- **THEN** el conf de hostapd generado contiene `channel=6` y no se consulta el canal de la WAN

### Requirement: La WAN solo se lee
La determinación del canal MUST realizarse únicamente con operaciones de lectura
sobre la WAN. Ningún paso de la selección puede modificar la configuración, el
estado o la gestión (NetworkManager) de la WAN.

#### Scenario: La selección no emite comandos de escritura sobre la WAN
- **WHEN** se ejecuta `escama start` con `CHANNEL_MODE=auto` y la WAN es WiFi asociada
- **THEN** los únicos comandos ejecutados contra la WAN son de consulta de estado (p. ej. `iw dev <wan> link`), sin `nmcli` de configuración, sin cambios de `ip addr`/`ip link` y sin hostapd sobre ella

### Requirement: Canal estable mientras el AP está activo
El canal del AP MUST NOT cambiar mientras el AP está activo. El seguimiento de
egress (`watch`) y la re-evaluación de salida (`egress`) MUST regenerar solo la
configuración de dnsmasq (DNS/MTU) y jamás reescribir la configuración de
hostapd. Un cambio de canal solo ocurre en el siguiente `start`/`restart`/
`reconnect`.

#### Scenario: Cambio de VPN no toca el canal
- **WHEN** el AP está activo y el watcher detecta un cambio de tunnel VPN y re-aplica el egress
- **THEN** la configuración de hostapd no se reescribe y el canal del AP permanece sin cambios

#### Scenario: Cambio de canal de la WAN post-arranque
- **WHEN** el AP está activo y el upstream de la WAN cambia de canal
- **THEN** el canal del AP permanece igual hasta el próximo `start`/`restart`/`reconnect`

### Requirement: Trazabilidad de la elección
En cada arranque con `CHANNEL_MODE=auto`, el resultado de la elección MUST quedar
registrado en el log del AP: el canal elegido y, cuando aplique, el canal de la
WAN detectado o el motivo del fallback a `CHANNEL`.

#### Scenario: Log con detección exitosa
- **WHEN** `escama start` con `CHANNEL_MODE=auto` elige el canal 1 porque la WAN está en el 6
- **THEN** el log del AP registra el canal elegido y el canal detectado de la WAN

#### Scenario: Log con fallback
- **WHEN** `escama start` con `CHANNEL_MODE=auto` no logra leer el canal de la WAN y cae al `CHANNEL` del env
- **THEN** el log del AP registra el canal usado y el motivo del fallback
