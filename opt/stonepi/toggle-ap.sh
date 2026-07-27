#!/bin/bash
# toggle-ap.sh - CLI para activar/desactivar modo AP en stonepi
# Uso: sudo toggle-ap.sh {start|stop|restart|status|enable|disable}

ACTION="${1:-status}"
LOG="/var/log/stonepi-ap.log"
IFACE_AP="$(/opt/stonepi/detect-iface.sh ap)"
AP_IP="10.42.1.1"
AP_SUBNET="10.42.1.0/24"
IFACE_WAN="${IFACE_WAN:-$(/opt/stonepi/detect-iface.sh wan)}"

sudo() { command sudo "$@"; }

is_ap_active() {
    ip addr show "$IFACE_AP" 2>/dev/null | grep -q "$AP_IP" && return 0
    return 1
}

do_start() {
    echo "==> Activando modo AP en $IFACE_AP..."
    sudo systemctl start stonepi-ap.service
    sleep 2
    if is_ap_active; then
        echo "OK: AP activo en $IFACE_AP ($AP_IP)"
    else
        echo "ERROR: AP no se activo correctamente"
        exit 1
    fi
}

do_stop() {
    echo "==> Deteniendo modo AP en $IFACE_AP..."

    echo "  Matando hostapd..."
    sudo killall hostapd 2>/dev/null
    sleep 1
    sudo killall -9 hostapd 2>/dev/null

    echo "  Matando dnsmasq..."
    sudo killall dnsmasq 2>/dev/null
    sleep 1
    sudo killall -9 dnsmasq 2>/dev/null
    sudo rm -f /run/dnsmasq-stonepi.pid

    echo "  Eliminando IP $AP_IP de $IFACE_AP..."
    sudo ip addr del "${AP_IP}/24" dev "$IFACE_AP" 2>/dev/null

    echo "  Restaurando NM managed=yes..."
    sudo nmcli device set "$IFACE_AP" managed yes

    echo "  Limpiando nftables stonepi-ap..."
    sudo nft delete table inet stonepi-ap 2>/dev/null

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
    echo "Para conectar a una red: nmcli device connect stonepi"
}

do_restart() {
    do_stop
    sleep 1
    do_start
}

do_status() {
    echo "=== stonepi AP Status ==="
    echo "Interface AP: $IFACE_AP"
    echo "Interface WAN: $IFACE_WAN"

    if is_ap_active; then
        echo "Modo: AP (activo)"
        echo "IP: $AP_IP/24"
    else
        echo "Modo: CLIENTE (AP inactivo)"
    fi

    echo ""
    echo "Servicio stonepi-ap:"
    sudo systemctl is-active stonepi-ap.service 2>/dev/null | xargs -I{} echo "  Active: {}"
    sudo systemctl is-enabled stonepi-ap.service 2>/dev/null | xargs -I{} echo "  Enabled: {}"

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
    echo "==> Habilitando stonepi-ap.service para inicio automatico..."
    sudo systemctl enable stonepi-ap.service
    sudo systemctl enable stonepi-cleanup.service
    sudo systemctl enable stonepi-health.timer
    echo "OK: Servicios habilitados"
}

do_disable() {
    echo "==> Deshabilitando stonepi-ap.service..."
    do_stop
    sudo systemctl stop stonepi-ap.service 2>/dev/null
    sudo systemctl disable stonepi-ap.service 2>/dev/null
    sudo systemctl disable stonepi-cleanup.service 2>/dev/null
    sudo systemctl stop stonepi-health.timer 2>/dev/null
    sudo systemctl disable stonepi-health.timer 2>/dev/null
    echo "OK: Servicios deshabilitados, AP detenido"
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
        echo "  start    Activar modo AP en stonepi"
        echo "  stop     Detener AP, restaurar WiFi cliente"
        echo "  restart  Reiniciar modo AP"
        echo "  status   Mostrar estado actual (AP o cliente)"
        echo "  enable   Habilitar servicio para inicio automatico"
        echo "  disable  Deshabilitar servicio y detener AP"
        exit 1
        ;;
esac