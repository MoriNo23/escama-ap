#!/bin/bash
# cleanup-warp.sh - Bypass quirúrgico para que AP + WARP coexistan
# NO mata túnel WARP, agrega reglas a SU tabla cuando existe
LOG="/var/log/stonepi-cleanup.log"
IFACE_INTERNET="${IFACE_WAN:-$(/opt/stonepi/detect-iface.sh wan)}"
IFACE_AP="$(/opt/stonepi/detect-iface.sh ap)"
AP_SUBNET="10.42.1.0/24"
AP_IP="10.42.1.1"

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
    echo "  ~ WARP inactivo: usando tabla own stonepi-ap"
    if ! nft list tables 2>/dev/null | grep -q "inet stonepi-ap"; then
        nft add table inet stonepi-ap
        nft add chain inet stonepi-ap forward '{ type filter hook forward priority -1; policy accept; }'
        nft add rule inet stonepi-ap forward iifname "$IFACE_AP" oifname "$IFACE_INTERNET" accept
        nft add rule inet stonepi-ap forward iifname "$IFACE_INTERNET" oifname "$IFACE_AP" ct state related,established accept
        echo "    + tabla inet stonepi-ap creada (forward)"
    fi
fi

if ! nft list table inet stonepi-ap 2>/dev/null | grep -q "masquerade"; then
    nft add chain inet stonepi-ap postrouting '{ type nat hook postrouting priority srcnat; policy accept; }' 2>/dev/null
    nft add rule inet stonepi-ap postrouting ip saddr "$AP_SUBNET" oifname "$IFACE_INTERNET" masquerade 2>/dev/null
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
