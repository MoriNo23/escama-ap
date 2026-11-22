# Design

## Context

El core corre en dos modos (root con `sudo`, rootless vía `escama-launch`) y
calcula rutas de estado según `euid` al importar. El launcher tiene
`CAP_NET_ADMIN/RAW/BIND_SERVICE` vía file capabilities y hoy ejecuta
`/usr/bin/ip` con argumentos arbitrarios. `apply_egress` borra y vuelve a crear
reglas usando un archivo de estado como memoria; `watch` y `egress` pueden
correr a la vez. La spec `uso-sin-privilegios` ya exige preflight completo y
degradación explícita; el código no lo cumple del todo. Ver proposal.md para la
motivación y los deltas de specs para el contrato.

## Goals / Non-Goals

**Goals:**
- Reducir el privilegio del launcher a las operaciones propias de escama.
- Hacer que limpiar el egress no dependa de un archivo de estado ni del modo de
  privilegio.
- Reutilizar los roles efectivos de `start` en `stop`/`egress`/`watch`.
- Hacer que la TUI falle de forma explícita o delegue con privilegio.
- Hacer que `escama` sin argumentos sea una entrada útil en TTY, con un menú
  que refleje el estado real y sugiera acciones válidas.
- Cubrir los bordes con tests que no mockeen el límite real.
- Mantener la presentación pública de GitHub alineada con el código y la
  versión que el propio proyecto reporta.

**Non-Goals:**
- Partir el monolito en módulos (se deja para después de estabilizar).
- Cambiar el formato de `escama.toml` ni la interfaz de los comandos
  explícitos; la única excepción es la entrada sin argumentos, con fallback.
- Agregar `CAP_DAC_OVERRIDE` ni ninguna capability nueva al launcher.
- Modificar la WAN: se mantiene la regla de oro de solo lectura.

## Decisions

### D1 — Whitelist del launcher por forma de argv, no ejecutor de `ip`
Validar en C que la única forma permitida de `/usr/bin/ip` sea la sonda:
`link add|del escv<digits> type dummy`. Todo lo demás se rechaza con rc 2.
- Alternativa descartada: hacer la sonda dentro del launcher con netlink. Más
  código (raw netlink/libnl) para el mismo efecto observable.
- Costo aceptado: seguir concediendo `CAP_NET_ADMIN` para crear/borrar una
  dummy con prefijo `escv`; es una capacidad acotada a nombres que escama usa.

### D2 — El kernel es la fuente de verdad del egress; el archivo es caché
En la limpieza, enumerar las reglas por marcadores estables (tabla `51821`,
pref `100`, subnet del AP, ifaces conocidas y un comment de propiedad) en vez de
confiar solo en el state file. El archivo sigue guardando `IPFWD` para
restaurar el sysctl previo.
- Alternativa descartada: un state file compartido en `/run` con permisos
  amplios. Choca con la spec de rutas por `euid` y abre un objetivo de
  escritura para cualquier usuario.

### D3 — Roles efectivos en runtime, nunca en el TOML
`start` escribe AP/WAN detectados en un archivo de runtime propio del modo;
`stop`, `egress` y `watch` lo leen primero y caen al TOML solo si no existe.
- Alternativa descartada: reescribir `escama.toml`. La config es del usuario y
  es la fuente de verdad declarada; el resultado de una detección es estado,
  no configuración.

### D4 — `flock` por modo de runtime
Un lock en el directorio de runtime serializa `watch` y `egress` dentro de un
mismo modo. Entre modos no se comparte lock: la reconciliación de D2 es la que
impide dejar reglas huérfanas si alguien mezcla sudo y unit de usuario.

### D5 — TUI: intento no interactivo y degradación explícita
La TUI escribe el TOML candidato a un archivo temporal y usa
`sudo -n install -m 644 <tmp> /etc/escama/escama.toml`. Si no hay privilegio
silencioso, no toca nada y muestra el motivo + el comando manual. `genconfig`
sigue generando confs en XDG, que no requieren root.
- Alternativa descartada: ejecutar la TUI por el launcher. El launcher no tiene
  `CAP_DAC_OVERRIDE`, así que no podría escribir el TOML de root.

### D6 — Guard de invocación verificado por capacidades efectivas
`_tiene_caps_del_launcher()` pasa a comprobar `CapEff` en `/proc/self/status`
para las tres capabilities, en vez de fiarse solo de `ESCAMA_VIA_LAUNCHER=1`.
Un proceso que ya tiene esas caps tiene privilegio de red por otro camino; el
guard deja de ser un secreto exportable.
- Alternativa descartada: pasar un descriptor heredado desde el launcher.
  Más cambio en C sin ganancia observable.

### D7 — Tests en dos niveles, partición diferida
Tests de propiedad sobre rutas/estado/lock en la suite actual (mockeada), más
un job de integración que use el launcher con caps reales y ejecute dos sondas
en paralelo — el caso que produjo la carrera de arranque. La separación en
módulos (`privilege`, `net`, `config`, `cli`) queda fuera de este change.

### D8 — Entrada por defecto: TUI solo con TTY
`main()` elige la TUI cuando no hay argumentos y la entrada es una terminal;
sin TTY mantiene `status`. Se invoca el core de la TUI existente, sin duplicar
el dispatch ni crear un segundo interpretador de comandos.
- Alternativa descartada: abrir la TUI siempre. Rompe scripts y unidades que
  llaman a `escama` sin argumentos esperando texto.
- Consecuencia: `escama status` sigue siendo la forma estable para scripts.

### D9 — Menú contextual desde estado estructurado
Extraer un productor de estado compartido entre `do_status` y la TUI, para que
la cabecera y las acciones salgan de datos reales (AP, WAN, egress, túneles,
SSID). Menú agrupado —estado, acciones rápidas, configuración, salir— con
etiquetas legibles y `--default-item` apuntando a la acción sugerida.
- Alternativa descartada: que la TUI consulte `iptables`/`iw` por su cuenta y
  reimplemente el estado. Duplicaría reglas y volvería a divergir.
- Costo: una pequeña función interna de estado; no cambia la salida de
  `status`.

### D10 — Degradación de la TUI sin whiptail y sin privilegio
Si falta `whiptail`, la TUI imprime el aviso de instalación y cae a `status`.
La navegación y las consultas no piden sudo; la escritura sigue D5 y las
acciones mutantes siguen el gate del core (D6).
- Alternativa descartada: agregar una librería de UI nueva. `whiptail` ya es
  requisito del proyecto.

### D11 — GitHub como escaparate, con `VERSION` como ancla
El README en ambos idiomas se reorganiza con quick start, sección de TUI y
enlaces a docs/changelog/SECURITY. Los badges dejan de llevar números de tests
escritos a mano: el badge de CI ya es dinámico; la prosa dice "suite completa"
en vez de `139 passing`. Los requisitos pasan a Python 3.11+ (`tomllib` es
stdlib desde 3.11) y se menciona que CI usa 3.13.

La release `v2.4.0` se crea en la misma tarea del bump, con notas tomadas de
`CHANGELOG.md`; `VERSION` sigue siendo la única fuente. Dependabot agrupa las
actualizaciones de GitHub Actions en un PR semanal, con label `dependencies` y
prefijo `chore(deps)`; no se agrega ecosistema `pip` porque no hay manifiesto.
Se publican `CONTRIBUTING.md`, plantilla de issue (con salida de
`escama preflight`, versión y modo root/rootless) y plantilla de PR (tests,
changelog, bump, spec). La metadata del repo se completa con homepage, social
preview usando `docs/logo/social-1280x640.png` y topics ya existentes.
Discussions/Wiki se evalúan, no se imponen: las decisiones quedan en `docs/`.
Branch protection se deja como recomendación explícita, no como cambio
automático del flujo de push directo.
- Alternativa descartada: mover documentación a la Wiki o duplicar el README
  en Discussions. Rompería la fuente única de documentación.
- Verificación: `gh release view`, `gh repo view` y render de los archivos
  `.github/` en GitHub tras el push.

## Risks / Trade-offs

- [Reconciliación por marcadores] → puede borrar reglas ajenas si alguien usa
  la misma tabla/subnet. Mitigación: comment de propiedad en cada regla y
  filtro por iface conocida.
- [Lock por modo] → root y usuario no comparten serialización. Mitigación: D2
  repara el resultado aunque ambos corran; documentar que solo un modo debe
  estar habilitado.
- [CapEff como guard] → un proceso con caps por otra vía pasaría el guard. Es
  aceptable: ya posee el privilegio que el guard protege.
- [TUI con `sudo -n`] → no puede pedir contraseña dentro de whiptail.
  Mitigación: mensaje explícito y config sin cambios.
- [Cambio en la forma de argv del launcher] → si la sonda cambia, hay que
  actualizar C y Python. Mitigación: un único patrón documentado y un test de
  integración que lo exerza.
- [Detección de TTY] → una terminal inesperada podría abrir la TUI donde se
  esperaba texto. Mitigación: comprobar `isatty()` y mantener `escama status`
  documentado como forma estable para scripts.
- [Gate sin privilegio] → dejar navegar sin sudo podría filtrar mutaciones.
  Mitigación: la TUI nunca ejecuta mutaciones directas; delega en el gate del
  core (D6) y en D5 para escribir la config.
- [Menú contextual] → sugerencias basadas en estado viejo. Mitigación:
  construir el menú justo antes de mostrarlo y re-leer el estado tras cada
  acción.
- [Cambio de entrada por defecto] → usuarios que escribían `escama` esperando
  `status`. Mitigación: fallback sin TTY y documentación explícita del cambio.
- [Contadores duros en badges] → `tests-139` ya no coincide con la suite real.
  Mitigación: badge dinámico de CI y sin números fijos en la prosa.
- [Release desincronizada] → `VERSION` marca 2.3.1 pero el latest es v2.3.0.
  Mitigación: crear la release en la misma tarea del bump (D11).
- [Branch protection] → exigir CI verde cambia el flujo actual de push directo.
  Mitigación: recomendación manual, no cambio automático.
- [Reporte privado] → `SECURITY.md` ya apunta a private reporting; verificar
  que esté habilitado en el repo o corregir el enlace.

## Migration Plan

1. Tests de caracterización de los cuatro bordes (fallan con el código actual).
2. Cambios en launcher, core y TUI, uno por uno, con la suite verde.
3. `sudo install.sh install` + reinicio de las user units; verificar
   `iptables -S`, `ip rule` y el state file tras `start`/`stop`.
4. Actualizar `README*`, `docs/TECHNICAL.md` y `docs-es/TECHNICAL.md` con la
   entrada `escama` sin args, el menú y el fallback; verificar con y sin TTY.
5. Publicar: corregir badges/requisitos, plantillas y Dependabot, completar
   metadata y crear la release `v2.4.0` desde `VERSION` + `CHANGELOG.md`.
6. Rollback: revertir los commits y reinstalar; la limpieza es idempotente, así
   que no deja reglas del change.

## Open Questions

Ninguna que pueda responder después sin cambiar specs, enfoque o tareas.
