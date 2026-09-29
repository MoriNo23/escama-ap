# Proposal

## Why

Hoy el programa tiene tres fricciones de uso, todas verificadas en la máquina:

1. **No hay versionado real**: la versión vive duplicada en dos lugares
   (`escama.py:24` e `install.sh:27`, ambas `1.0.0`) que pueden divergir, no hay
   CHANGELOG ni tags, y 12+ commits no movieron la versión — no se puede saber
   qué cambió ni qué hay instalado sin leer el código.
2. **La instalación es un paso manual que hay que recordar**: si el usuario está en
   una máquina nueva o reinstalló, `escama` no existe en el PATH; hay que saber
   que existe `install.sh` y acordarse de correrlo.
3. **Todo exige sudo, incluso lo que no lo necesita**: `main()` rechaza el
   no-root para *cualquier* subcomando, incluso `--help`, `--version` y `status`
   (lectura pura). El usuario pidió rootless real: que el AP pueda operarse sin
   teclear `sudo` en cada comando.

## What Changes

- **Investigación en internet antes de todo**: toda decisión de mecanismo
  (kernel, systemd, herramientas de terceros) MUST documentarse primero en la
  documentación oficial — man-pages del kernel, `systemd.exec(5)`, upstream — y
  recién después validarse empíricamente con un spike. El spike **confirma, no
  descubre**: serviría para verificar una receta ya leída, no para deducirla a
  fuerza de ensayo/error. Justificación medida: el primer spike de este change
  "descubrió" por ensayo/error una mecánica de capabilities que ya estaba
  documentada en `capabilities(7)`, con el resultado añadido de partir de una
  hipótesis falsa (`setcap +ei`) y de no detectar que `getcap` mentía en
  silencio. Cada decisión de mecanismo en los artefactos de este change MUST
  citar su fuente.
- **Versionado por cambios**: una única fuente de verdad de la versión
  (compartida por `escama.py`, `escama-tui.py` e `install.sh`), un
  `CHANGELOG.md` y una disciplina semver bumpeada al cerrar cada change
  (documentada como paso en el propio change).
- **Auto-instalación**: `escama` detecta que falta la instalación (symlinks,
  `/opt/escama`, env, units) y la completa él mismo con un único prompt de
  privilegio y un mensaje claro de qué va a hacer; también un chequeo de
  preflight que dice qué falta.
- **Rootless real**:Capabilities de Linux aplicadas a un launcher ELF mínimo
  (`CAP_NET_ADMIN`, `CAP_NET_RAW`, `CAP_NET_BIND_SERVICE`) para que el proceso
  normal pueda hablar con nl80211, iptables/ip y el DHCP de dnsmasq sin ser root;
  estado de runtime (pidfile, logs) en rutas del usuario; y autostart con una
  **unit de usuario** (`systemctl --user`), sin privileged unit. Los read-only
  (`status`, `--help`, `--version`) funcionan sin privilegios desde el arranque.
- **Fuera de scope deliberado**: no se toca la lógica de egress/VPN ni la de
  selección de canal (ya especificadas en `seleccion-canal` e `instalacion`);
  `instalacion` conserva sus requisitos actuales (el instalador sigue siendo la
  vía canónica; la auto-instalación solo lo invoca). El cambio de módulos del
  kernel (`rmmod`/`modprobe` 8192eu) y la gestión de NetworkManager no son
  rootless: se degradan con mensaje explícito, no se silencian.

## Capabilities

### New Capabilities
- `versionado`: fuente única de versión + `CHANGELOG.md` + disciplina semver por
  change (qué debe reportar `escama --version` y cuándo se bumpea).
- `auto-instalacion`: detección de instalación faltante/incompleta, bootstrap
  con un prompt de privilegio, y reporte de preflight.
- `uso-sin-privilegios`: operación rootless real (capabilities sobre launcher
  ELF, estado de runtime escribible por el usuario, autostart con unit de
  usuario) y degradación explícita de lo que no puede ser rootless.

### Modified Capabilities
- Ninguna: `instalacion` y `seleccion-canal` conservan sus requisitos; lo nuevo
  se expresa en las capabilities nuevas para no duplicar ni reescribir
  contratos existentes.

## Impact

- **Código**: `opt/escama/escama.py` (preflight + auto-install + gate de root
  por subcomando), `opt/escama/escama-tui.py` (gate coherente), `install.sh`
  (deja de duplicar la versión; instala capabilities y la unit de usuario).
- **Nuevo**: launcher ELF mínimo versionado en el repo y compilado por
  `install.sh` (ver R1 de `uso-sin-privilegios`); `CHANGELOG.md`.
- **Config**: paths de estado de runtime (pidfile/log) con alternativa escrita
  por el usuario; nueva unit de usuario de systemd.
- **Tests**: `tests/test_escama.py` — preflight, auto-install (bootstrap
  invocado una vez), gate por subcomando (read-only sin privilegios), coherencia
  de versión entre las tres piezas.
- **Sistemas**: capabilities sobre un binario, unit de usuario bajo
  `~/.config/systemd/user/`, permisos de `/opt/escama` y `/etc/escama`.
- **Riesgo principal (actualizado tras la investigación)**: la viabilidad del
  rootless **quedó verificada empíricamente** — la receta `setcap +ep` + `capset`
  al inheritable + `PR_CAP_AMBIENT_RAISE` conserva las capabilities a través del
  `execve` y habilita `iptables`, `ip` y el bind en puertos privilegiados como
  usuario normal (ver `design.md` D2). Riesgo residual: que la máquina destino
  tenga compilador y soporte de xattrs; sin ellos el preflight MUST negar el modo
  rootless y ofrecer el camino de elevación documentado, nunca fingir que
  funciona. El paso de compilación sigue siendo la desviación consciente de
  "sin build step" (AGENTS.md) y queda explícito en `design.md`.
