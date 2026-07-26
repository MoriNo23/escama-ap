#!/bin/bash
# detect-iface.sh - Detecta la interfaz para el AP stonepi
# Busca por: 1) nombre fijo "stonepi", 2) MAC conocida, 3) wlan* que no sea wn8200nd
# Uso: /opt/stonepi/detect-iface.sh [ap|wan]
#   ap  - imprime la interfaz del AP (default)
#   wan - imprime la interfaz de internet

MODE="${1:-ap}"
AP_MAC="02:1a:2b:3c:4d:03"

detect_ap() {
    # 1. Nombre fijo por udev
    if ip link show stonepi &>/dev/null; then
        echo "stonepi"
        return 0
    fi
    # 2. Por MAC
    for iface in /sys/class/net/*; do
        name=$(basename "$iface")
        [ "$name" = "lo" ] && continue
        mac=$(cat "$iface/address" 2>/dev/null)
        if [ "$mac" = "$AP_MAC" ]; then
            echo "$name"
            return 0
        fi
    done
    # 3. Por patrón: wlan* que no sea la de internet
    WAN=$(detect_wan)
    for iface in /sys/class/net/wlan*; do
        [ -e "$iface" ] || continue
        name=$(basename "$iface")
        [ "$name" = "$WAN" ] && continue
        echo "$name"
        return 0
    done
    echo "wlan1"
    return 1
}

detect_wan() {
    ip route show default 2>/dev/null | awk '{print $5; exit}'
}

if [ "$MODE" = "ap" ]; then
    detect_ap
else
    detect_wan
fi
