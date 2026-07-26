#!/bin/bash
# start-ap.sh - Restaura el AP manualmente
# Uso: sudo /opt/stonepi/start-ap.sh
LOG="/var/log/stonepi-ap.log"
IFACE_INTERNET="${IFACE_WAN:-$(/opt/stonepi/detect-iface.sh wan)}"
IFACE_AP="$(/opt/stonepi/detect-iface.sh ap)"
AP_IP="10.42.1.1/24"
AP_SUBNET="10.42.1.0/24"

log() { echo "$(date '+%H:%M:%S') $1" | tee -a "$LOG"; }

log "=== Iniciando AP manual ==="
log "AP: $IFACE_AP | WAN: $IFACE_INTERNET"

nmcli device set "$IFACE_AP" managed no 2>/dev/null
log "NM: $IFACE_AP managed no"

# Liberar la iface de iwd/station para que hostapd pueda pasarla a modo AP
iw dev "$IFACE_AP" disconnect 2>/dev/null
ip link set "$IFACE_AP" down 2>/dev/null
sleep 1
ip link set "$IFACE_AP" up 2>/dev/null
log "AP iface liberada de iwd/station (disconnect + link down + up)"

if ! ping -c 1 -W 3 -I "$IFACE_INTERNET" 8.8.8.8 &>/dev/null; then
    log "WARN: $IFACE_INTERNET sin internet, continuando..."
fi
log "Internet check via $IFACE_INTERNET"

if ! ip addr show "$IFACE_AP" | grep -q "10.42.1.1"; then
    ip addr add "$AP_IP" dev "$IFACE_AP" 2>/dev/null
    log "IP $AP_IP asignada a $IFACE_AP"
else
    log "IP $AP_IP ya presente en $IFACE_AP"
fi

# Matar hostapd zombie (proceso vivo pero sin emitir) antes de arrancar
pkill -x hostapd 2>/dev/null
sleep 1
ip link set "$IFACE_AP" up 2>/dev/null
hostapd -B /etc/hostapd/hostapd-stonepi.conf
sleep 2
if iw dev "$IFACE_AP" info 2>/dev/null | grep -q "ssid"; then
    log "hostapd OK (AP emitiendo)"
else
    log "WARN: hostapd no emite tras arranque, reintentando con iface up"
    ip link set "$IFACE_AP" up 2>/dev/null
    hostapd -B /etc/hostapd/hostapd-stonepi.conf
    sleep 2
    if iw dev "$IFACE_AP" info 2>/dev/null | grep -q "ssid"; then
        log "hostapd OK (reintento)"
    else
        log "ERROR: hostapd fallo"
        exit 1
    fi
fi

if ! pgrep -F /run/dnsmasq-stonepi.pid 2>/dev/null > /dev/null 2>&1; then
    sleep 1
    dnsmasq --conf-file=/etc/dnsmasq-stonepi.conf --pid-file=/run/dnsmasq-stonepi.pid
    pgrep -F /run/dnsmasq-stonepi.pid 2>/dev/null > /dev/null || { log "ERROR: dnsmasq fallo"; exit 1; }
    log "dnsmasq OK"
else
    log "dnsmasq ya corriendo, saltando"
fi

sysctl -w net.ipv4.ip_forward=1 > /dev/null 2>&1

log "=== AP activo: stonepi -> $IFACE_INTERNET ==="
