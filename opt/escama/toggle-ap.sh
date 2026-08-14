#!/bin/bash
# toggle-ap.sh - CLI para activar/desactivar modo AP en escama
# Uso: sudo toggle-ap.sh {start|stop|restart|status|enable|disable}

CONFIG_FILE="/etc/escama/escama.env"
if [ -f "$CONFIG_FILE" ]; then
    # shellcheck disable=SC1090
    . "$CONFIG_FILE"
fi

ACTION="${1:-status}"
LOG="/var/log/escama-ap.log"
IFACE_AP="$(/opt/escama/detect-iface.sh ap)"
AP_IP="${AP_IP:-10.42.1.1}"
AP_SUBNET="${AP_SUBNET:-10.42.1.0/24}"
IFACE_WAN="${WAN_IFACE:-$(/opt/escama/detect-iface.sh wan)}"

sudo() { command sudo "$@"; }

is_ap_active() {
    ip addr show "$IFACE_AP" 2>/dev/null | grep -q "$AP_IP" && return 0
    return 1
}

do_start() {
    echo "==> Activando modo AP en $IFACE_AP (escama)..."
    sudo systemctl start escama-ap.service
    sleep 2
    if is_ap_active; then
        echo "OK: AP activo en $IFACE_AP ($AP_IP)"
    else
        echo "ERROR: AP no se activo correctamente"
        exit 1
    fi
}

do_stop() {
    echo "==> Deteniendo modo AP en $IFACE_AP (escama)..."

    echo "  Matando hostapd..."
    sudo killall hostapd 2>/dev/null
    sleep 1
    sudo killall -9 hostapd 2>/dev/null

    echo "  Matando dnsmasq..."
    sudo killall dnsmasq 2>/dev/null
    sleep 1
    sudo killall -9 dnsmasq 2>/dev/null
    sudo rm -f /run/dnsmasq-escama.pid

    echo "  Eliminando IP $AP_IP de $IFACE_AP..."
    sudo ip addr del "${AP_IP}/24" dev "$IFACE_AP" 2>/dev/null

    echo "  Restaurando NM managed=yes..."
    sudo nmcli device set "$IFACE_AP" managed yes

    echo "  Limpiando nftables escama-ap..."
    sudo nft delete table inet escama-ap 2>/dev/null

    echo "  Limpiando iptables FORWARD..."
    sudo iptables -D FORWARD -i "$IFACE_AP" -o "$IFACE_WAN" -j ACCEPT 2>/dev/null
    sudo iptables -D FORWARD -i "$IFACE_WAN" -o "$IFACE_AP" -m state --state RELATED,ESTABLISHED -j ACCEPT 2>/dev/null

    echo "  Limpiando iptables NAT POSTROUTING..."
    sudo iptables -t nat -D POSTROUTING -s "$AP_SUBNET" -o "$IFACE_WAN" -j MASQUERADE 2>/dev/null

    echo "  Limpiando reglas nft cloudflare-warp..."
    sudo nft delete rule inet cloudflare-warp forward iifname "$IFACE_AP" oifname "$IFACE_WAN" accept 2>/dev/null
    sudo nft delete rule inet cloudflare-warp forward iifname "$IFACE_WAN" oifname "$IFACE_AP" ct state related,established accept 2>/dev/null

    echo "  Desactivando ip_forward..."
    sudo sysctl -w net.ipv4.ip_forward=0 > /dev/null 2>&1

    echo "  Reiniciando interfaz $IFACE_AP..."
    sudo ip link set "$IFACE_AP" down 2>/dev/null
    sleep 1
    sudo ip link set "$IFACE_AP" up 2>/dev/null

    sudo tee -a "$LOG" > /dev/null <<EOF
$(date '+%H:%M:%S') === AP detenido - $IFACE_AP restaurado a modo cliente ===
EOF

    echo "OK: AP detenido. $IFACE_AP esta en modo cliente (NM gestionado)."
    echo "Para conectar a una red: nmcli device connect $IFACE_AP"
}

do_restart() {
    do_stop
    sleep 1
    do_start
}

do_status() {
    echo "=== escama AP Status ==="
    echo "Interface AP: $IFACE_AP"
    echo "Interface WAN: $IFACE_WAN"

    if is_ap_active; then
        echo "Modo: AP (activo)"
        echo "IP: $AP_IP/24"
    else
        echo "Modo: CLIENTE (AP inactivo)"
    fi

    echo ""
    echo "Servicio escama-ap:"
    sudo systemctl is-active escama-ap.service 2>/dev/null | xargs -I{} echo "  Active: {}"
    sudo systemctl is-enabled escama-ap.service 2>/dev/null | xargs -I{} echo "  Enabled: {}"

    echo ""
    echo "Procesos:"
    pgrep -x hostapd > /dev/null 2>&1 && echo "  hostapd: RUNNING" || echo "  hostapd: STOPPED"
    pgrep -x dnsmasq > /dev/null 2>&1 && echo "  dnsmasq: RUNNING" || echo "  dnsmasq: STOPPED"
    pgrep -x iwd > /dev/null 2>&1 && echo "  iwd: RUNNING" || echo "  iwd: STOPPED"

    echo ""
    echo "NM state for $IFACE_AP:"
    sudo nmcli device show "$IFACE_AP" 2>/dev/null | grep -E "GENERAL.STATE|GENERAL.CONNECTION|IP4.ADDRESS|IP4.GATEWAY" | sed 's/^/  /'

    echo ""
    echo "IP forwarding:"
    sudo sysctl net.ipv4.ip_forward 2>/dev/null | sed 's/^/  /'
}

do_enable() {
    echo "==> Habilitando escama-ap.service para inicio automatico..."
    sudo systemctl enable escama-ap.service
    echo "OK: Servicio habilitado"
}

do_disable() {
    echo "==> Deshabilitando escama-ap.service..."
    do_stop
    sudo systemctl stop escama-ap.service 2>/dev/null
    sudo systemctl disable escama-ap.service 2>/dev/null
    echo "OK: Servicio deshabilitado, AP detenido"
}

case "$ACTION" in
    start)   do_start ;;
    stop)    do_stop ;;
    restart) do_restart ;;
    status)  do_status ;;
    enable)  do_enable ;;
    disable) do_disable ;;
    *)
        echo "Uso: toggle-ap.sh {start|stop|restart|status|enable|disable}"
        echo ""
        echo "Comandos:"
        echo "  start    Activar modo AP en escama ($IFACE_AP)"
        echo "  stop     Detener AP, restaurar WiFi cliente"
        echo "  restart  Reiniciar modo AP"
        echo "  status   Mostrar estado actual (AP o cliente)"
        echo "  enable   Habilitar servicio para inicio automatico"
        echo "  disable  Deshabilitar servicio y detener AP"
        exit 1
        ;;
esac
