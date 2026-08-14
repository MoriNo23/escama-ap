#!/bin/bash
# start-ap.sh - Brings up the escama AP (hostapd + dnsmasq)
# Uso: sudo /opt/escama/start-ap.sh
#
# The AP interface is the designated access point ("escama", default wn8200nd).
# The WAN/internet interface keeps the name "stonepi".

CONFIG_FILE="/etc/escama/escama.env"
if [ -f "$CONFIG_FILE" ]; then
    # shellcheck disable=SC1090
    . "$CONFIG_FILE"
fi

LOG="/var/log/escama-ap.log"
IFACE_INTERNET="${WAN_IFACE:-$(/opt/escama/detect-iface.sh wan)}"
IFACE_AP="$(/opt/escama/detect-iface.sh ap)"
AP_IP="${AP_IP:-10.42.1.1}/${AP_CIDR:-24}"
AP_SUBNET="${AP_SUBNET:-10.42.1.0/24}"

log() { echo "$(date '+%H:%M:%S') $1" | tee -a "$LOG"; }

log "=== Iniciando AP manual (escama) ==="
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

if ! ip addr show "$IFACE_AP" | grep -q "${AP_IP%%/*}"; then
    ip addr add "$AP_IP" dev "$IFACE_AP" 2>/dev/null
    log "IP $AP_IP asignada a $IFACE_AP"
else
    log "IP $AP_IP ya presente en $IFACE_AP"
fi

# Matar hostapd zombie (proceso vivo pero sin emitir) antes de arrancar
pkill -x hostapd 2>/dev/null
sleep 1
ip link set "$IFACE_AP" up 2>/dev/null
hostapd -B /etc/hostapd/hostapd-escama.conf
sleep 2
if iw dev "$IFACE_AP" info 2>/dev/null | grep -q "type AP"; then
    log "hostapd OK (AP emitiendo)"
else
    log "WARN: hostapd no emite tras arranque, reintentando con iface up"
    ip link set "$IFACE_AP" up 2>/dev/null
    hostapd -B /etc/hostapd/hostapd-escama.conf
    sleep 2
    if iw dev "$IFACE_AP" info 2>/dev/null | grep -q "type AP"; then
        log "hostapd OK (reintento)"
    else
        log "ERROR: hostapd fallo (iface no entra en modo AP)"
        exit 1
    fi
fi

if ! pgrep -F /run/dnsmasq-escama.pid 2>/dev/null > /dev/null 2>&1; then
    sleep 1
    dnsmasq --conf-file=/etc/dnsmasq-escama.conf --pid-file=/run/dnsmasq-escama.pid
    pgrep -F /run/dnsmasq-escama.pid 2>/dev/null > /dev/null || { log "ERROR: dnsmasq fallo"; exit 1; }
    log "dnsmasq OK"
else
    log "dnsmasq ya corriendo, saltando"
fi

sysctl -w net.ipv4.ip_forward=1 > /dev/null 2>&1

log "=== AP activo: escama ($IFACE_AP) -> $IFACE_INTERNET ==="
