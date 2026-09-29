# Design

## Context

`escama.py` concentra toda la lógica: `main()` (línea ~934) rechaza el no-root
antes de cualquier subcomando, incluso `--help`/`--version`/`status`;
`run()` (línea ~118) ya antepone `sudo` por comando; `VERSION` está hardcodeado
en `escama.py` y `install.sh` (dos copias); la TUI tiene su propio gate
(línea ~124). El estado de runtime va a rutas de root (`/run/dnsmasq-escama.pid`,
`/var/log/escama-ap.log`). En la máquina de dev, `/opt/escama`, `/etc/escama` y
`/usr/local/bin` son root-only y `pkexec` está disponible. Specs existentes
(`instalacion`, `seleccion-canal`) siguen vigentes y esta change no las toca.
Ver AGENTS.md: "sin build step" — este design mete una excepción deliberada
(D2), y queda explícita.

## Goals / Non-Goals

**Goals:**
- Una versión, un changelog, una disciplina de bump por change.
- Primera ejecución sin pasos manuales (auto-instalación con un prompt).
- Operaciones de red como usuario normal vía capabilities sobre un launcher ELF.
- Autostart rootless vía unit de usuario; read-only sin privilegio alguno.

**Non-Goals:**
- No tocar la lógica de negocio de AP/VPN/canal (ver proposal).
- No rootless-izar `rmmod`/`modprobe` ni la gestión de NM (imposible sin
  `CAP_SYS_MODULE`/polkit; se degradan explícitamente).
- No compilar el driver ni tocar el kernel.
- No convertir el proyecto a un binario distribuible; el núcleo sigue siendo el
  script Python.

## Decisions

> **Método (obligatorio en este change): investigar antes de espiar.** Toda
> decisión de mecanismo MUST apoyarse primero en la documentación oficial
> (`capabilities(7)`, `execve(2)`, `prctl(2)`, `systemd.exec(5)`, upstream) con
> cita de la fuente, y recién después validarse con un spike. Un spike confirma
> una receta leída; si el spike contradice la documentación, se investiga el
> porqué antes de seguir — no se improvisa una variante.

**D1 — La versión vive en un archivo, no en código.**
Fuente única: un archivo de texto de una línea (p. ej. `VERSION` en la raíz o
`etc/escama/VERSION`) que `escama.py`, `escama-tui.py` e `install.sh` leen en
runtime; si falta, se degrada a un valor "desconocido" con aviso en vez de
mentir. Bump manual disciplinado: cada change que altera comportamiento añade un
paso en su `tasks.md` ("bumpear X.Y.Z porque …") y una entrada de CHANGELOG antes
de archivarse. *Alternativas*: (a) `git describe` en runtime → la versión cambia
sola, no es estable para `install.sh --version` ni para reportar "instalado vs
repo", y exige tags en cada commit; (b) script `./version.sh bump` → automatiza
un paso que se ejecuta una vez por change y agrega una dependencia más que
mantener. Se elige (fuente única + disciplina manual + CHANGELOG) por ser
simple y determinista; el CHANGELOG MUST cubrir también la serie 0.x para que el
historial no arranque vacío.

**D2 — Rootless real = launcher ELF con `setcap +ep`, que suma las capabilities
al set inheritable con `capset()` y las eleva a ambient antes de `execv` del
núcleo; el modo sudo actual se conserva como camino válido.**
El kernel ignora file capabilities sobre scripts con shebang, así que el rootless
de `ip`/`iptables`/`hostapd` exige un binario. La receta sale de `capabilities(7)`
y fue verificada end-to-end en esta máquina (`iptables -L` rc=0, `ip link add`
rc=0, bind en puerto 80 OK, todo como usuario normal):

- `setcap cap_net_admin,cap_net_raw,cap_net_bind_service+ep` sobre el launcher
  (`escama-launch`, C diminuto compilado por `install.sh`).
- El launcher suma esas caps a su set **inheritable** con `capset()`. Necesario
  porque en `execve` el inheritable **no** se toma del archivo
  (`P'(inheritable) = P(inheritable)`, capabilities(7) §"Transformation of
  capabilities during execve()"), así que `setcap +ei` no aporta nada para un
  usuario normal cuyo inheritable está vacío. Sumar al inheritable está
  permitido sin `CAP_SETPCAP` porque el nuevo set es subconjunto del permitted
  (capabilities(7) §"Programmatically adjusting capability sets").
- El launcher las eleva a **ambient** con `PR_CAP_AMBIENT_RAISE`, por el
  invariante "ninguna cap puede ser ambient si no está en permitted **e**
  inheritable" (capabilities(7) §Ambient). El ambient sobrevive al `execve` de un
  binario no privilegiado y se suma al permitted del proceso siguiente: el núcleo
  Python queda con las tres capabilities.
- **Condición operational verificada**: el launcher MUST ser propiedad del
  usuario que lo ejecuta. Con el binario en root el kernel lo trata como
  *capability-dumb binary* y **descarta las capabilities en silencio**
  (capabilities(7) §"Safety checking for capability-dumb binaries"): `getcap`
  sigue mostrando las caps y el fallo es invisible. El preflight MUST verificar
  el owner además de las capabilities.
- El `preflight` verifica *antes* de prometer nada: toolchain, xattrs del FS
  destino, owner del launcher, `setcap` efectivo **y** una operación de red real
  a través del `execve`. Si algo falta, el modo rootless se **niega** con el
  motivo y el proyecto sigue operable con el modo sudo actual (no se
  desinstala ni se rompe nada existente).
*Alternativas descartadas*: (a) `cap_net_admin+ep` sobre `/usr/bin/python3` →
otorga las capabilities a *todo* script de Python del sistema: inaceptable;
(b) `AmbientCapabilities=` de systemd → sirve para una unit de sistema, pero
descartado como mecanismo del CLI interactivo: un user manager no puede elevar
el bounding set por encima del suyo (misma limitación que systemd documenta para
`Limit*` en user units), así que solo resolvería el arranque por servicio y
dejaría el CLI igual; (c) `sudo` NOPASSWD para un subconjunto de binarios →
sigue siendo root, no es rootless (el usuario pidió rootless real). Coste
asumido: un paso de compilación, que es la desviación consciente de "sin build
step"; por eso el preflight lo trata como condición de primera clase y el
fallback (sudo) es un modo soportado, no un plan B de emergencia.

**D3 — Estado de runtime en rutas del usuario; las de sistema solo si hay
privilegio.**
`STATE/PID/LOG` se resuelven por XDG (`$XDG_RUNTIME_DIR`, `$XDG_STATE_HOME`) cuando
el proceso no es root, y a las rutas actuales cuando sí lo es; la resolución se
registra en el log. Esto desbloquea dnsmasq/hostapd sin root (leasefile, pidfile,
log) sin cambiar el comportamiento del modo root. *Alternativa*: dejar las rutas
y放开 permisos →“行權 de /var/log y /run a un usuario” es peor que mover el
estado a XDG.

**D4 — Autostart rootless = unit de usuario (`systemctl --user`), y el gate de
root pasa a ser por-subcomando.**
`main()` deja de exigir root globalmente: `--help`/`--version`/`status` corren
siempre sin privilegio; las acciones mutantes intentaran el camino rootless
(launcher con capabilities) y, si no está, escalan por el mecanismo de privilegio
del proyecto con un prompt único (no uno por `run()`), o fallan con el mensaje
del preflight. `install.sh enable` sigue siendo la vía de sistema; se suma
`install.sh enable --user` (o equivalente) para la unit de usuario. La TUI sigue
la misma lógica (arranca y muestra estado sin privilegio; las acciones que mutan
escalan). *Alternativa*: user unit que invoca un privileged unit de sistema vía
systemd — evita el launcher pero sigue siendo root, descartado por D2.

**D5 — Auto-instalación = bootstrap delegada a `install.sh`, con preflight y un
único prompt.**
`escama` calcula un preflight (comandos, código, env, units, unit de usuario,
capabilities → "instalado" / "desactualizado" / "faltante"). Si falta algo y el
usuario acepta, delega en `install.sh install` (lógica única, conserva
idempotencia y preservation del env), re-verifica y continúa la acción original
con un solo prompt. Si el usuario rechaza, imprime el comando manual y sale con
error claro. *Alternativa*: que el propio Python duplique la copia de archivos →
dos implementaciones que divergen; descartada (spec MUST NOT duplicar).

**D6 — La TUI y el core comparten versión y gate, sin refactor grande.**
`escama-tui.py` lee la versión de la fuente única (D1) y su gate de root pasa a
ser por-acción, no global. Sin tocar el flujo de la TUI más allá del gate y la
versión.

## Risks / Trade-offs

- [Capabilities requieren toolchain y FS con xattrs; stonepi puede no tener gcc]
  → preflight lo detecta y niega el modo con motivo; el modo sudo (actual)
  queda siempre soportado. Primera tarea de implementación: verificar gcc/xattr
  en la máquina destino antes de invertir en el resto.
- [Un binario con `cap_net_admin` es superficie de ataque si el usuario lo
  ejecuta a diario] → el launcher no acepta argumentos propios ni hace otra cosa
  que `exec` del núcleo; se documenta la987863 superficie.
- [Execve del launcher puede perder capabilities salvo que se preserven
  (inheritable/ambient)] → el launcher las preserva explícitamente y el preflight
  *verifica de verdad* (ejecuta una operación real) que sobreviven al exec, no
  solo que `getcap` las muestre.
- [XDG cambia rutas que hoy diagnostican fallos (logs en /var/log)] → la ruta
  efectiva se loguea en cada operación y `status` la muestra.
- [Discrepancia "instalado vs repo" (copia en /opt) como en el change anterior]
  → el preflight compara código y versión y distingue los dos estados.
- [Bump manual discipline puede olvidarse] → el paso va en el `tasks.md` de cada
  change; el preflight/validate no lo fuerza, es proceso.

## Migration Plan

1. **Fase 0 (spike)**: verificar en la máquina destino gcc, xattrs, `setcap` y
   que el launcher preserva capabilities a través de `execve`. Si el spike falla,
   parar y replantear D2 antes de seguir (es la única parte con dependencia
   ambiental fuerte).
2. **Fase 1 (sin riesgo)**: D1 (fuente única + CHANGELOG + bump retroactivo 0.x),
   D5 (preflight + auto-instalación), gate por subcomando de lectura. Todo
   reversible por commit.
3. **Fase 2 (rootless)**: D2 launcher + capabilities, D3 rutas XDG, D4 unit de
   usuario. Cada piece entra con su preflight; si el launcher no compila, el
   proyecto queda en Fase 1 (que ya es útil) y el modo rootless se reporta no
   disponible.
4. **Rollback**: volver a los commits previos; el modo sudo histórico sigue
   funcionando en todo momento (es el fallback de D2).

## Open Questions

- ¿Nome do binário do launcher e do subcomando de preflight já foram escolhidos
  como `escama-launch` y `escama preflight`? → *ajuste menor de nombres, decided
  en implementación, no cambia specs ni enfoque.*
- ¿El cambio retroactivo de versión a 0.x del CHANGELOG debe ser un resumen
  por commit o por "épocas" (p. ej. 0.1 Núcleo, 0.2 VPN, 0.3 Canal, 0.4
  Instalación)? → detalle de redacción del changelog, no afecta comportamiento.
