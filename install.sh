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
ENV_DST="/etc/escama/escama.toml"
# dotenv pre-TOML: si existe y parsea como TOML, cmd_install lo renombra
# (el formato KEY="value" con comentarios # ya era TOML valido).
LEGACY_ENV="/etc/escama/escama.env"
SRC_CODE="$REPO/opt/escama"
SRC_ENV="$REPO/etc/escama/escama.toml"
SRC_UNITS="$REPO/etc/systemd/system"
UNITS="escama-ap.service escama-egress.service"
# Units de USUARIO para el modo rootless (spec `uso-sin-privilegios`).
USER_UNITS="escama-ap.service escama-egress.service"
USER_UNIT_SRC="$REPO/etc/systemd/user"
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
  sudo ./install.sh enable --user    autostart sin sudo (user units, al iniciar sesion)
  sudo ./install.sh disable --user   deshabilita el autostart de usuario
  ./install.sh --verify-rootless   prueba el modo sin sudo (sin privilegio)

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
    echo "rootless sin sudo:  ./$0 --verify-rootless"
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
    # residuos de la instalacion vieja: los .sh que el core Python consolido
    # siguen ejecutables en /opt si no se borran (el preflight diria "completa"
    # al lado de codigo muerto).
    rm -f "$OPT_DIR/detect-iface.sh" "$OPT_DIR/config-tui.sh" \
          "$OPT_DIR/start-ap.sh" "$OPT_DIR/stop-ap.sh" \
          "$OPT_DIR/toggle-ap.sh" "$OPT_DIR/cleanup-warp.sh"
    rm -rf "$OPT_DIR/__pycache__"
    # migracion dotenv->TOML: un rename alcanza porque el formato viejo ya era
    # TOML valido. Fail-closed: si no parsea, queda intacto y se avisa (nunca
    # se destruye la config del usuario).
    if [ -f "$LEGACY_ENV" ] && [ ! -f "$ENV_DST" ]; then
        if python3 -c 'import sys, tomllib; tomllib.load(open(sys.argv[1], "rb"))' "$LEGACY_ENV" 2>/dev/null; then
            mv "$LEGACY_ENV" "$ENV_DST"
            echo "Migrado: $LEGACY_ENV -> $ENV_DST (el formato ya era TOML valido)"
        else
            echo "AVISO: $LEGACY_ENV no es TOML valido; NO se migro." >&2
            echo "       Corrige la sintaxis y vuelve a correr install.sh install." >&2
        fi
    fi
    # config: NUNCA se pisa la del usuario (novedades al lado, en .new)
    if [ -f "$ENV_DST" ]; then
        cp "$SRC_ENV" "$ENV_DST.new"
        echo "AVISO: $ENV_DST existente: se conserva; novedades en $ENV_DST.new"
        # Decir QUE variables es nueva: sin esto el aviso obliga a un diff a mano y en
        # la practica nadie lo lee, asi que las variables nuevas nunca se aplican.
        _nuevas="$(nuevas_del_env "$SRC_ENV" "$ENV_DST")"
        if [ -n "$_nuevas" ]; then
            echo "       variables nuevas en el env del repo, ausentes en el tuyo:"
            echo "$_nuevas" | sed 's/^/         + /'
            echo "       agregalas a $ENV_DST a mano si queres los defaults nuevos."
        fi
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
    instalar_user_units
    echo "OK: instalado. Autostart (install no lo modifica):"
    cmd_status
}

# --- Units de usuario (modo rootless) ---
user_unit_dir() {
    # install.sh corre con sudo, asi que $HOME es /root: las user units deben
    # ir al home del usuario REAL (SUDO_USER), o quedarian donde ningun user
    # manager las mira.
    local home="$HOME"
    if [ "$(id -u)" -eq 0 ] && [ -n "${SUDO_USER:-}" ]; then
        home="$(getent passwd "$SUDO_USER" 2>/dev/null | cut -d: -f6)"
    fi
    [ -n "$home" ] || home="$HOME"
    if [ -n "${XDG_CONFIG_HOME:-}" ] && [ "$(id -u)" -ne 0 ]; then
        echo "$XDG_CONFIG_HOME/systemd/user"
    else
        echo "$home/.config/systemd/user"
    fi
}

# Corre un comando del user manager de systemd del usuario REAL.
# install.sh va con sudo, asi que el bus del usuario no esta disponible:
# hay que invocar como el usuario, con SU runtime dir. Sin esto falla con
# "Failed to connect to bus" (medido en esta maquina).
user_systemctl() {
    if systemctl --user "$@" 2>/dev/null; then
        return 0
    fi
    if [ "$(id -u)" -ne 0 ] || [ -z "${SUDO_USER:-}" ]; then
        return 1
    fi
    local _uid _rt
    _uid="$(id -u "$SUDO_USER")"
    _rt="/run/user/$_uid"
    [ -d "$_rt" ] || return 1
    runuser -u "$SUDO_USER" -- env XDG_RUNTIME_DIR="$_rt" \
        systemctl --user "$@" 2>/dev/null
}

# Instala las user units. NO habilita el autostart: eso es `enable --user`.
instalar_user_units() {
    local d u
    d="$(user_unit_dir)"
    if [ ! -d "$USER_UNIT_SRC" ]; then
        echo "AVISO: no hay etc/systemd/user en el repo; sin modo rootless autostart" >&2
        return 1
    fi
    mkdir -p "$d"
    for u in $USER_UNITS; do
        if [ -f "$USER_UNIT_SRC/$u" ]; then
            install -m 644 "$USER_UNIT_SRC/$u" "$d/$u"
        else
            echo "AVISO: falta $USER_UNIT_SRC/$u; se omite" >&2
        fi
    done
    # daemon-reload del user manager. install.sh corre con sudo, asi que el
    # bus del usuario no esta en $DBUS_SESSION_BUS_ADDRESS ni $XDG_RUNTIME_DIR:
    # hay que invocarlo como el usuario, apuntando a SU runtime dir. Sin eso
    # falla con "Failed to connect to bus" (medido).
    if user_systemctl daemon-reload; then
        echo "OK: user units instaladas en $d (user manager recargado)"
    else
        echo "AVISO: no pude hablar con el user manager de systemd." >&2
        echo "       Las units quedaron en $d; corré 'systemctl --user daemon-reload'" >&2
        echo "       cuando tengas sesion, y despues '$0 enable --user'." >&2
    fi
    return 0
}

cmd_enable_user() {
    local d u
    d="$(user_unit_dir)"
    for u in $USER_UNITS; do
        if [ ! -f "$d/$u" ]; then
            echo "AVISO: $u no instalado como user unit. Corré: sudo $0 install" >&2
            continue
        fi
    done
    if [ ! -x "$OPT_DIR/escama-launch" ]; then
        echo "AVISO: no hay launcher en $OPT_DIR; el modo rootless no puede arrancar el AP." >&2
        echo "       Reinstalá con: sudo $0 install" >&2
        return 1
    fi
    if ! verificar_rootless; then
        echo "AVISO: el modo rootless no verifica en esta maquina (mira 'preflight')." >&2
        echo "       No habilito el autostart de usuario para no dejar un unit que falla." >&2
        return 1
    fi
    user_systemctl daemon-reload || {
        echo "ERROR: sin user manager de systemd (sesion sin bus?)." >&2
        return 1
    }
    for u in $USER_UNITS; do
        [ -f "$d/$u" ] && user_systemctl enable --now "$u"
    done
    echo "OK: autostart de usuario habilitado (arranca al iniciar sesion, sin sudo)."
}

cmd_disable_user() {
    local d u
    d="$(user_unit_dir)"
    for u in $USER_UNITS; do
        [ -f "$d/$u" ] && user_systemctl disable --now "$u"
    done
    echo "OK: autostart de usuario deshabilitado."
}

# Nombres de variable presentes en $1 (env del repo) y AUSENTES en $2 (el del
# usuario). Solo el nombre de la clave: el valor por defecto se lee del repo.
nuevas_del_env() {
    awk -F= '/^[A-Za-z_][A-Za-z0-9_]*=/ {print $1}' "$1" | sort -u \
    | comm -23 - <(awk -F= '/^[A-Za-z_][A-Za-z0-9_]*=/ {print $1}' "$2" | sort -u)
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
    udir="$(user_unit_dir)"
    for u in $USER_UNITS; do
        if [ -f "$udir/$u" ]; then
            user_systemctl disable --now "$u" 2>/dev/null || true
            rm -f "$udir/$u"
        fi
    done
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
    d="$(user_unit_dir)"
    for u in $USER_UNITS; do
        if [ -f "$d/$u" ]; then
            en="$(user_systemctl is-enabled "$u" 2>/dev/null || true)"
            ac="$(user_systemctl is-active "$u" 2>/dev/null || true)"
            printf 'unit user %s: %s / %s\n' "$u" \
                "${en:-no-configurado}" "${ac:-inactivo}"
        else
            echo "unit user $u: AUSENTE"
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
    "enable --user")   cmd_enable_user ;;
    "disable --user")  cmd_disable_user ;;
    --verify-rootless)      verificar_rootless && { echo "rootless-verificado"; exit 0; } || { echo "rootless-no-disponible"; exit 1; } ;;
    "")  uso; echo "ERROR: falta el subcomando" >&2; exit 2 ;;
    *)   uso; echo "ERROR: subcomando desconocido: $1" >&2; exit 2 ;;
esac
