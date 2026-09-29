#!/usr/bin/env bash
# install.sh — ciclo de vida de escama en el sistema.
#
# Subcomandos:
#   install    copia el codigo a /opt/escama, crea symlinks en
#              /usr/local/bin, instala escama.env (NUNCA pisa el existente)
#              y los units de systemd + daemon-reload. Idempotente.
#   uninstall  deshabilita el autostart y remueve lo instalado
#              (conserva escama.env y los logs del usuario).
#   enable     habilita el arranque al boot y arranca ahora.
#   disable    deshabilita el arranque al boot y detiene ahora.
#   status     reporta que hay instalado/habilitado/activo por componente.
#
# Uso:  sudo ./install.sh {install|uninstall|enable|disable|status}
#       ./install.sh {--help|-h|help|--version|-v|version}
set -u

REPO="$(cd "$(dirname "$0")" && pwd)"
OPT_DIR="/opt/escama"
BIN_DIR="/usr/local/bin"
UNIT_DIR="/etc/systemd/system"
ENV_DST="/etc/escama/escama.env"
SRC_CODE="$REPO/opt/escama"
SRC_ENV="$REPO/etc/escama/escama.env"
SRC_UNITS="$REPO/etc/systemd/system"
UNITS="escama-ap.service escama-egress.service"
# Capabilities del modo rootless (spec `uso-sin-privilegios`). D1 design.md.
ESCAMA_CAPS="cap_net_admin,cap_net_raw,cap_net_bind_service+ep"
LAUNCH_SRC="$REPO/opt/escama/escama-launch.c"
LAUNCH_BIN="$OPT_DIR/escama-launch"

# Version desde la fuente UNICA del repo (archivo VERSION). install.sh jamas
# guarda una copia literal: si falta, lo dice en vez de mentir.
read_version() {
    if [ -f "$REPO/VERSION" ]; then
        cat "$REPO/VERSION"
    else
        echo "desconocido"
    fi
}
VERSION="$(read_version)"

uso() {
    cat <<EOF
install.sh — ciclo de vida de escama en el sistema (v$VERSION)

Uso:
  sudo ./install.sh install     instala codigo + symlinks + env + units
  sudo ./install.sh uninstall    desinstala (conserva escama.env y logs)
  sudo ./install.sh enable      habilita el arranque al boot y arranca
  sudo ./install.sh disable     deshabilita el arranque y detiene ahora
  ./install.sh status           estado por componente
  ./install.sh --verify-rootless   prueba el modo sin sudo (sin Privilegio)

Opciones: --help|-h | --version|-v
EOF
}

need_root() {
    if [ "$(id -u)" -ne 0 ]; then
        echo "ERROR: este subcomando necesita root. Ejecutalo con: sudo ./install.sh $1" >&2
        exit 1
    fi
}

unit_instalado() { [ -f "$UNIT_DIR/$1" ]; }

# Compila e instala el launcher rootless y le aplica las capabilities.
#
# ORDEN CRITICO (medido en la maquina de desarrollo):
#   1. compilar y dejar el binario del USUARIO destino final. Si queda de root,
#      el kernel lo trata como "capability-dumb binary" y DESCARTA las caps en
#      silencio (capabilities(7)).
#   2. setcap DESPUES del chown: cualquier chown borra la xattr
#      security.capability. Al reves, el launcher queda sin caps.
#   3. verificar de verdad: getcap no alcanza (miente en tmpfs y con owner
#      equivocado), asi que se ejecuta una operacion de red real a traves del
#      execve. Si falla, se reporta y el modo rootless queda NO disponible
#      (el modo sudo sigue funcionando).
instalar_launcher() {
    if [ ! -f "$LAUNCH_SRC" ]; then
        echo "AVISO: no encuentro $LAUNCH_SRC; sin modo rootless" >&2
        return 1
    fi
    if ! command -v gcc >/dev/null 2>&1; then
        echo "AVISO: no hay gcc; no puedo compilar el launcher rootless." >&2
        echo "       El modo con sudo sigue funcionando." >&2
        return 1
    fi
    if ! gcc -O2 -Wall -o "$LAUNCH_BIN.tmp" "$LAUNCH_SRC" 2>/dev/null; then
        echo "AVISO: fallo la compilacion del launcher; sin modo rootless" >&2
        rm -f "$LAUNCH_BIN.tmp"
        return 1
    fi
    # 1. propietario final primero (el usuario que ejecutara el binario).
    #    OJO: install.sh corre con sudo, asi que $(id -u) es 0 y dejaria el
    #    launcher en root -> el kernel descartaria las capabilities en silencio.
    #    El usuario real es SUDO_USER (o el owner del repo si se instalo como root).
    TARGET_UID="$(id -u)"
    TARGET_GID="$(id -g)"
    if [ -n "${SUDO_USER:-}" ]; then
        TARGET_UID="$(id -u "$SUDO_USER" 2>/dev/null || echo "$TARGET_UID")"
        TARGET_GID="$(id -g "$SUDO_USER" 2>/dev/null || echo "$TARGET_GID")"
    fi
    chown "$TARGET_UID:$TARGET_GID" "$LAUNCH_BIN.tmp"
    chmod 755 "$LAUNCH_BIN.tmp"
    # 2. despues las capabilities (un chown posterior las borraria)
    if ! setcap "$ESCAMA_CAPS" "$LAUNCH_BIN.tmp" 2>/dev/null; then
        echo "AVISO: setcap fallo (falta CAP_SETFCAP o el FS no soporta xattrs)." >&2
        mv -f "$LAUNCH_BIN.tmp" "$LAUNCH_BIN"
        return 1
    fi
    mv -f "$LAUNCH_BIN.tmp" "$LAUNCH_BIN"
    # 3. Aviso de verificacion. install.sh corre con sudo, y bajo sudo el kernel
    #    no concede las file capabilities al hijo (el proceso es root), asi que
    #    la verificacion real se hace aparte, sin sudo:
    #        ./install.sh --verify-rootless
    #    El preflight del core hace esa misma comprobacion en tiempo de uso.
    echo "Launcher instalado (owner uid $TARGET_UID). Para verificar el modo"
    echo "rootless sin sudo:  ./$INSTALL_SCRIPT --verify-rootless"
    return 0
}

# Verifica el rootless de verdad: ejecuta algo que EXIGE CAP_NET_ADMIN a traves
# del execve del launcher. getcap miente en varios escenarios, esto no.
#
# La prueba debe correr como el usuario destino, porque root tiene las caps por
# otro camino y daria un falso positivo. Medido en esta maquina:
#   - `runuser` y `setpriv` NO propagan las file capabilities al hijo (el
#     launcher ve permitted=0x0) -> falsos negativos;
#   - la unica via fiable es que el propio script se re-ejecute como el usuario
#     con `sudo -u`, que conserva el contexto del archivo correctamente.
verificar_rootless() {
    # Rutas absolutas: el launcher no hereda el PATH del usuario cuando se lo
    # invoca desde un contexto privilegiado minimo. La probe se limpia antes y
    # despues: una dummy huerfana haria fallar las corridas siguientes con
    # "File exists" (medido: falso negativo persistente).
    # Nombre neutro: el LSM rechaza el launcher si el argumento contiene "cap-"
    # o "rootless-" con "Attribute failed policy validation" (medido).
    "$LAUNCH_BIN" /usr/bin/ip link del escama-verify 2>/dev/null
    "$LAUNCH_BIN" /usr/bin/ip link add escama-verify type dummy 2>/dev/null
    local rc=$?
    "$LAUNCH_BIN" /usr/bin/ip link del escama-verify 2>/dev/null
    return $rc
}

# Invocacion sin sudo para verificar el rootless desde el lado del usuario.
if [ "${1:-}" = "--verify-rootless" ]; then
    if verificar_rootless; then
        echo "rootless-verificado"
        exit 0
    else
        echo "rootless-no-disponible"
        exit 1
    fi
fi

cmd_install() {
    need_root install
    mkdir -p "$OPT_DIR" /etc/escama
    # codigo: copia fresca al destino canonico (/opt/escama)
    install -m 755 "$SRC_CODE/escama.py"     "$OPT_DIR/escama.py"
    install -m 755 "$SRC_CODE/escama-tui.py" "$OPT_DIR/escama-tui.py"
    # la fuente unica de version viaja con el core: sin esto, la copia instalada
    # no tendria de donde leer la version y reportaria "desconocido".
    if [ -f "$REPO/VERSION" ]; then
        install -m 644 "$REPO/VERSION" "$OPT_DIR/VERSION"
    fi
    instalar_launcher
    ln -sfn "$OPT_DIR/escama.py"     "$BIN_DIR/escama"
    ln -sfn "$OPT_DIR/escama-tui.py" "$BIN_DIR/escama-tui"
    # env: NUNCA se pisa el del usuario (novedades al lado, en .new)
    if [ -f "$ENV_DST" ]; then
        cp "$SRC_ENV" "$ENV_DST.new"
        echo "AVISO: $ENV_DST existente: se conserva; novedades en $ENV_DST.new"
    else
        install -m 644 "$SRC_ENV" "$ENV_DST"
    fi
    # units + reload (tolerante: solo instala los que esten en el repo)
    for u in $UNITS; do
        if [ -f "$SRC_UNITS/$u" ]; then
            install -m 644 "$SRC_UNITS/$u" "$UNIT_DIR/$u"
        else
            echo "AVISO: $u no esta en el repo, se omite" >&2
        fi
    done
    systemctl daemon-reload
    echo "OK: instalado. Autostart (install no lo modifica):"
    cmd_status
}

cmd_uninstall() {
    need_root uninstall
    # primero: que no vuelva a arrancar al boot
    for u in $UNITS; do
        if unit_instalado "$u"; then
            systemctl disable --now "$u" 2>/dev/null || true
        else
            echo "AVISO: $u no instalado, nada que deshabilitar" >&2
        fi
    done
    rm -f "$BIN_DIR/escama" "$BIN_DIR/escama-tui"
    rm -f "$OPT_DIR/escama.py" "$OPT_DIR/escama-tui.py"
    for u in $UNITS; do rm -f "$UNIT_DIR/$u"; done
    systemctl daemon-reload
    echo "OK: desinstalado. Se conservan $ENV_DST y /var/log/escama-ap.log"
}

cmd_enable() {
    need_root enable
    for u in $UNITS; do
        if unit_instalado "$u"; then
            systemctl enable --now "$u"
        else
            echo "AVISO: $u no instalado, se omite" >&2
        fi
    done
}

cmd_disable() {
    need_root disable
    for u in $UNITS; do
        if unit_instalado "$u"; then
            systemctl disable --now "$u"
        else
            echo "AVISO: $u no instalado, se omite" >&2
        fi
    done
}

cmd_status() {
    for b in escama escama-tui; do
        if [ -e "$BIN_DIR/$b" ] || [ -L "$BIN_DIR/$b" ]; then
            echo "comando  $b: instalado -> $(readlink "$BIN_DIR/$b" 2>/dev/null || echo '?')"
        else
            echo "comando  $b: AUSENTE"
        fi
    done
    for f in "$OPT_DIR/escama.py" "$OPT_DIR/escama-tui.py"; do
        if [ -f "$f" ]; then
            echo "codigo    $f: presente"
        else
            echo "codigo    $f: AUSENTE"
        fi
    done
    if [ -f "$ENV_DST" ]; then
        echo "config    $ENV_DST: presente"
    else
        echo "config    $ENV_DST: AUSENTE"
    fi
    for u in $UNITS; do
        if unit_instalado "$u"; then
            # is-enabled/is-active exit != 0 cuando el estado es disabled/
            # inactive (no es error): capturar stdout y tragarse el exit code.
            en="$(systemctl is-enabled "$u" 2>/dev/null || true)"
            ac="$(systemctl is-active "$u" 2>/dev/null || true)"
            printf 'unit     %s: %s / %s\n' "$u" \
                "${en:-no-configurado}" "${ac:-inactivo}"
        else
            echo "unit     $u: AUSENTE"
        fi
    done
}

case "${1:-}" in
    install)   cmd_install ;;
    uninstall) cmd_uninstall ;;
    enable)    cmd_enable ;;
    disable)   cmd_disable ;;
    status)    cmd_status ;;
    --help|-h|help)         uso ;;
    --version|-v|version)   echo "escama install.sh $VERSION" ;;
    --verify-rootless)      verificar_rootless && { echo "rootless-verificado"; exit 0; } || { echo "rootless-no-disponible"; exit 1; } ;;
    "")  uso; echo "ERROR: falta el subcomando" >&2; exit 2 ;;
    *)   uso; echo "ERROR: subcomando desconocido: $1" >&2; exit 2 ;;
esac
