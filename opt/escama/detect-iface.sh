#!/bin/bash
# detect-iface.sh - Detects the interfaces used by escama-ap
#
# The AP (designated access point / "escama") interface defaults to "wn8200nd"
# (configurable via AP_IFACE in /etc/escama/escama.env).
# The WAN/internet WiFi interface keeps the name "stonepi".
#
# Uso: /opt/escama/detect-iface.sh [ap|wan]
#   ap  - prints the AP interface (default)
#   wan - prints the internet interface

# Load config if present
CONFIG_FILE="/etc/escama/escama.env"
if [ -f "$CONFIG_FILE" ]; then
    # shellcheck disable=SC1090
    . "$CONFIG_FILE"
fi

# Default AP interface if not set in config
AP_IFACE="${AP_IFACE:-wn8200nd}"
# WAN interface keeps the name "stonepi" by default
WAN_IFACE="${WAN_IFACE:-stonepi}"

MODE="${1:-ap}"

detect_ap() {
    # 1. Explicit AP interface from config (default: wn8200nd)
    if ip link show "$AP_IFACE" &>/dev/null; then
        echo "$AP_IFACE"
        return 0
    fi
    # 2. Fallback: any wlan* that is not the WAN interface
    for iface in /sys/class/net/wlan*; do
        [ -e "$iface" ] || continue
        name=$(basename "$iface")
        [ "$name" = "$WAN_IFACE" ] && continue
        echo "$name"
        return 0
    done
    echo "$AP_IFACE"
    return 1
}

detect_wan() {
    # Explicit override
    if [ -n "$WAN_IFACE" ] && ip link show "$WAN_IFACE" &>/dev/null; then
        echo "$WAN_IFACE"
        return 0
    fi
    # Fallback: default route interface
    ip route show default 2>/dev/null | awk '{print $5; exit}'
}

if [ "$MODE" = "ap" ]; then
    detect_ap
else
    detect_wan
fi
