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
    "")  uso; echo "ERROR: falta el subcomando" >&2; exit 2 ;;
    *)   uso; echo "ERROR: subcomando desconocido: $1" >&2; exit 2 ;;
esac
