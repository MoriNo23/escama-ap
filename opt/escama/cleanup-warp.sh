#!/bin/bash
# cleanup-warp.sh - Bypass quirúrgico para que AP + WARP coexistan
# NO mata túnel WARP, agrega reglas a SU tabla cuando existe
#
# AP interface = designated access point (escama, default wn8200nd).
# WAN interface = internet WiFi, keeps name "stonepi".

CONFIG_FILE="/etc/escama/escama.env"
if [ -f "$CONFIG_FILE" ]; then
    # shellcheck disable=SC1090
    . "$CONFIG_FILE"
fi

LOG="/var/log/escama-cleanup.log"
IFACE_INTERNET="${WAN_IFACE:-$(/opt/escama/detect-iface.sh wan)}"
IFACE_AP="$(/opt/escama/detect-iface.sh ap)"
AP_SUBNET="${AP_SUBNET:-10.42.1.0/24}"
AP_IP="${AP_IP:-10.42.1.1}"

echo "$(date): Iniciando cleanup quirúrgico (AP: $IFACE_AP, WAN: $IFACE_INTERNET)" >> "$LOG"

if ! ip rule show 2>/dev/null | grep -q "500:.*from $AP_SUBNET lookup main"; then
    ip rule add from "$AP_SUBNET" lookup main priority 500 2>/dev/null
    echo "  + ip rule 500: $AP_SUBNET -> main table"
fi

if nft list tables 2>/dev/null | grep -q "inet cloudflare-warp"; then
    echo "  ~ WARP activo: agregando reglas a tabla cloudflare-warp"
    if ! nft list table inet cloudflare-warp 2>/dev/null | grep -q "iifname \"$IFACE_AP\".*accept"; then
        nft insert rule inet cloudflare-warp forward iifname "$IFACE_AP" oifname "$IFACE_INTERNET" accept 2>/dev/null
        nft insert rule inet cloudflare-warp forward iifname "$IFACE_INTERNET" oifname "$IFACE_AP" ct state related,established accept 2>/dev/null
        echo "    + ACCEPT rules agregadas a cloudflare-warp forward"
    fi
else
    echo "  ~ WARP inactivo: usando tabla own escama-ap"
    if ! nft list tables 2>/dev/null | grep -q "inet escama-ap"; then
        nft add table inet escama-ap
        nft add chain inet escama-ap forward '{ type filter hook forward priority -1; policy accept; }'
        nft add rule inet escama-ap forward iifname "$IFACE_AP" oifname "$IFACE_INTERNET" accept
        nft add rule inet escama-ap forward iifname "$IFACE_INTERNET" oifname "$IFACE_AP" ct state related,established accept
        echo "    + tabla inet escama-ap creada (forward)"
    fi
fi

if ! nft list table inet escama-ap 2>/dev/null | grep -q "masquerade"; then
    nft add chain inet escama-ap postrouting '{ type nat hook postrouting priority srcnat; policy accept; }' 2>/dev/null
    nft add rule inet escama-ap postrouting ip saddr "$AP_SUBNET" oifname "$IFACE_INTERNET" masquerade 2>/dev/null
    echo "    + MASQUERADE nft nativa agregada"
fi

iptables -D FORWARD -i "$IFACE_AP" -o "$IFACE_INTERNET" -j ACCEPT 2>/dev/null
iptables -D FORWARD -i "$IFACE_INTERNET" -o "$IFACE_AP" -m state --state RELATED,ESTABLISHED -j ACCEPT 2>/dev/null
iptables -t nat -D POSTROUTING -s "$AP_SUBNET" -o "$IFACE_INTERNET" -j MASQUERADE 2>/dev/null

iptables -I FORWARD -i "$IFACE_AP" -o "$IFACE_INTERNET" -j ACCEPT
iptables -I FORWARD -i "$IFACE_INTERNET" -o "$IFACE_AP" -m state --state RELATED,ESTABLISHED -j ACCEPT
iptables -t nat -I POSTROUTING -s "$AP_SUBNET" -o "$IFACE_INTERNET" -j MASQUERADE
sysctl -w net.ipv4.ip_forward=1 > /dev/null 2>&1
echo "  + iptables NAT + forward OK"

echo "$(date): Cleanup completado" >> "$LOG"
