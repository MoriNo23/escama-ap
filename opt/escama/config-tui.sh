#!/bin/bash
# config-tui.sh - TUI (whiptail) to configure escama-ap
#
# Lets you choose the AP interface (designated access point), SSID, passphrase,
# channel, IP/subnet, DHCP range, DNS, and the WAN interface. Writes /etc/escama/escama.env
# and regenerates the hostapd/dnsmasq config files.
#
# Uso: sudo /opt/escama/config-tui.sh

set -u

CONFIG_DIR="/etc/escama"
CONFIG_FILE="$CONFIG_DIR/escama.env"
HOSTAPD_CONF="/etc/hostapd/hostapd-escama.conf"
DNSMASQ_CONF="/etc/dnsmasq-escama.conf"

WHIPTAIL="whiptail"
if ! command -v whiptail >/dev/null 2>&1; then
    echo "ERROR: whiptail no está instalado. Instalalo con: sudo apt install whiptail" >&2
    exit 1
fi

# Load current config if present
if [ -f "$CONFIG_FILE" ]; then
    # shellcheck disable=SC1090
    . "$CONFIG_FILE"
fi

# Defaults
AP_IFACE="${AP_IFACE:-wn8200nd}"
WAN_IFACE="${WAN_IFACE:-stonepi}"
SSID="${SSID:-escama}"
CHANNEL="${CHANNEL:-6}"
HW_MODE="${HW_MODE:-g}"
AP_IP="${AP_IP:-10.42.1.1}"
AP_CIDR="${AP_CIDR:-24}"
AP_SUBNET="${AP_SUBNET:-10.42.1.0/24}"
DHCP_START="${DHCP_START:-10.42.1.10}"
DHCP_END="${DHCP_END:-10.42.1.254}"
DHCP_LEASE="${DHCP_LEASE:-12h}"
WPA_PASSPHRASE="${WPA_PASSPHRASE:-#[REMOVED]}"
DNS1="${DNS1:-8.8.8.8}"
DNS2="${DNS2:-8.8.4.4}"

# Root check
if [ "$(id -u)" -ne 0 ]; then
    echo "Este script necesita sudo. Ejecutalo con: sudo $0" >&2
    exit 1
fi

TITLE="escama-ap Configuración"
BACKTITLE="escama-ap — hostapd + dnsmasq AP converter"

# --- Collect available network interfaces (physical + wireless) ---
list_ifaces() {
    local out=""
    for d in /sys/class/net/*; do
        name=$(basename "$d")
        [ "$name" = "lo" ] && continue
        # skip virtual/tunnel interfaces
        case "$name" in
            docker*|veth*|br-*|tailscale*|wg*|tun*|cni*) continue ;;
        esac
        out="$out $name $name"
    done
    echo "${out# }"
}

IFACE_CHOICES=$(list_ifaces)

# Fallback if empty
if [ -z "$IFACE_CHOICES" ]; then
    IFACE_CHOICES="wn8200nd wn8200nd stonepi stonepi"
fi

main_menu() {
    while true; do
        choice=$($WHIPTAIL --clear --backtitle "$BACKTITLE" --title "$TITLE" \
            --menu "Elige qué configurar:" 18 70 9 \
            "1" "Interfaz AP (access point): $AP_IFACE" \
            "2" "Interfaz WAN (internet, stonepi): $WAN_IFACE" \
            "3" "SSID: $SSID" \
            "4" "Canal: $CHANNEL" \
            "5" "IP/Subred AP: $AP_IP/$AP_CIDR" \
            "6" "Rango DHCP: $DHCP_START-$DHCP_END ($DHCP_LEASE)" \
            "7" "Passphrase WPA2" \
            "8" "DNS: $DNS1, $DNS2" \
            "S" "GUARDAR Y SALIR" \
            3>&1 1>&2 2>&3)

        [ $? -ne 0 ] && save_and_exit

        case "$choice" in
            1) pick_ap_iface ;;
            2) pick_wan_iface ;;
            3) edit_text "SSID" "$SSID" SSID ;;
            4) edit_text "Canal (1-11 2.4GHz)" "$CHANNEL" CHANNEL ;;
            5) edit_network ;;
            6) edit_dhcp ;;
            7) edit_passphrase ;;
            8) edit_dns ;;
            S|s) save_and_exit ;;
        esac
    done
}

pick_ap_iface() {
    local current_radio="$AP_IFACE"
    # Build a radiolist with current selected
    local items=""
    for d in /sys/class/net/*; do
        name=$(basename "$d")
        [ "$name" = "lo" ] && continue
        case "$name" in docker*|veth*|br-*|tailscale*|wg*|tun*|cni*) continue ;; esac
        if [ "$name" = "$current_radio" ]; then
            items="$items $name '$name (AP)' on"
        else
            items="$items $name '$name' off"
        fi
    done
    local sel=$($WHIPTAIL --clear --backtitle "$BACKTITLE" --title "Interfaz AP" \
        --radiolist "Elige la interfaz del access point (escama):" 18 70 10 \
        $items 3>&1 1>&2 2>&3)
    [ $? -eq 0 ] && [ -n "$sel" ] && AP_IFACE="$sel"
}

pick_wan_iface() {
    local current_radio="$WAN_IFACE"
    local items=""
    for d in /sys/class/net/*; do
        name=$(basename "$d")
        [ "$name" = "lo" ] && continue
        case "$name" in docker*|veth*|br-*|tailscale*|wg*|tun*|cni*) continue ;; esac
        if [ "$name" = "$current_radio" ]; then
            items="$items $name '$name (WAN)' on"
        else
            items="$items $name '$name' off"
        fi
    done
    local sel=$($WHIPTAIL --clear --backtitle "$BACKTITLE" --title "Interfaz WAN" \
        --radiolist "Elige la interfaz de internet (WAN, stonepi):" 18 70 10 \
        $items 3>&1 1>&2 2>&3)
    [ $? -eq 0 ] && [ -n "$sel" ] && WAN_IFACE="$sel"
}

edit_text() {
    local label="$1" default="$2" varname="$3"
    local input=$($WHIPTAIL --clear --backtitle "$BACKTITLE" --title "$label" \
        --inputbox "$label:" 10 60 "$default" 3>&1 1>&2 2>&3)
    [ $? -eq 0 ] && [ -n "$input" ] && printf -v "$varname" '%s' "$input"
}

edit_network() {
    local input=$($WHIPTAIL --clear --backtitle "$BACKTITLE" --title "Red AP" \
        --inputbox "IP del AP (ej: 10.42.1.1):" 10 50 "$AP_IP" 3>&1 1>&2 2>&3)
    [ $? -eq 0 ] && [ -n "$input" ] && AP_IP="$input"
    input=$($WHIPTAIL --clear --backtitle "$BACKTITLE" --title "Red AP" \
        --inputbox "CIDR (ej: 24):" 10 50 "$AP_CIDR" 3>&1 1>&2 2>&3)
    [ $? -eq 0 ] && [ -n "$input" ] && AP_CIDR="$input"
    input=$($WHIPTAIL --clear --backtitle "$BACKTITLE" --title "Red AP" \
        --inputbox "Subred (ej: 10.42.1.0/24):" 10 50 "$AP_SUBNET" 3>&1 1>&2 2>&3)
    [ $? -eq 0 ] && [ -n "$input" ] && AP_SUBNET="$input"
}

edit_dhcp() {
    local input
    input=$($WHIPTAIL --clear --backtitle "$BACKTITLE" --title "DHCP" \
        --inputbox "Inicio rango DHCP (ej: 10.42.1.10):" 10 50 "$DHCP_START" 3>&1 1>&2 2>&3)
    [ $? -eq 0 ] && [ -n "$input" ] && DHCP_START="$input"
    input=$($WHIPTAIL --clear --backtitle "$BACKTITLE" --title "DHCP" \
        --inputbox "Fin rango DHCP (ej: 10.42.1.254):" 10 50 "$DHCP_END" 3>&1 1>&2 2>&3)
    [ $? -eq 0 ] && [ -n "$input" ] && DHCP_END="$input"
    input=$($WHIPTAIL --clear --backtitle "$BACKTITLE" --title "DHCP" \
        --inputbox "Lease time (ej: 12h):" 10 50 "$DHCP_LEASE" 3>&1 1>&2 2>&3)
    [ $? -eq 0 ] && [ -n "$input" ] && DHCP_LEASE="$input"
}

edit_passphrase() {
    local input=$($WHIPTAIL --clear --backtitle "$BACKTITLE" --title "WPA2" \
        --passwordbox "Passphrase WPA2 (8-63 chars):" 10 60 "$WPA_PASSPHRASE" 3>&1 1>&2 2>&3)
    [ $? -eq 0 ] && [ -n "$input" ] && WPA_PASSPHRASE="$input"
}

edit_dns() {
    local input
    input=$($WHIPTAIL --clear --backtitle "$BACKTITLE" --title "DNS" \
        --inputbox "DNS primario:" 10 50 "$DNS1" 3>&1 1>&2 2>&3)
    [ $? -eq 0 ] && [ -n "$input" ] && DNS1="$input"
    input=$($WHIPTAIL --clear --backtitle "$BACKTITLE" --title "DNS" \
        --inputbox "DNS secundario:" 10 50 "$DNS2" 3>&1 1>&2 2>&3)
    [ $? -eq 0 ] && [ -n "$input" ] && DNS2="$input"
}

save_and_exit() {
    mkdir -p "$CONFIG_DIR"
    cat > "$CONFIG_FILE" <<EOF
# escama.env — central configuration for escama-ap (hostapd + dnsmasq AP converter)
# Generated/edited by config-tui.sh. Restart the service after changes:
#   sudo systemctl restart escama-ap.service

# --- Access Point interface (the designated AP / "escama") ---
AP_IFACE="$AP_IFACE"

# --- AP network ---
AP_IP="$AP_IP"
AP_CIDR="$AP_CIDR"
AP_SUBNET="$AP_SUBNET"
DHCP_START="$DHCP_START"
DHCP_END="$DHCP_END"
DHCP_LEASE="$DHCP_LEASE"

# --- hostapd / SSID ---
SSID="$SSID"
CHANNEL="$CHANNEL"
HW_MODE="$HW_MODE"
WPA_PASSPHRASE="$WPA_PASSPHRASE"

# --- DNS for DHCP clients ---
DNS1="$DNS1"
DNS2="$DNS2"

# --- WAN interface override (optional) ---
# Leave empty to auto-detect from the default route.
# The WAN WiFi interface keeps the name "stonepi".
WAN_IFACE="$WAN_IFACE"
EOF
    chmod 644 "$CONFIG_FILE"

    # Regenerate hostapd conf
    cat > "$HOSTAPD_CONF" <<EOF
interface=$AP_IFACE
driver=nl80211
ssid=$SSID
hw_mode=$HW_MODE
channel=$CHANNEL
ieee80211n=1
ht_capab=[HT20]
wmm_enabled=1
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=$WPA_PASSPHRASE
wpa_key_mgmt=WPA-PSK
wpa_pairwise=CCMP
rsn_pairwise=CCMP
EOF

    # Regenerate dnsmasq conf
    cat > "$DNSMASQ_CONF" <<EOF
interface=$AP_IFACE
bind-interfaces
dhcp-range=$DHCP_START,$DHCP_END,255.255.255.0,$DHCP_LEASE
dhcp-option=option:router,$AP_IP
dhcp-option=option:dns-server,$DNS1,$DNS2
dhcp-leasefile=/var/lib/misc/dnsmasq-escama.leases
EOF

    $WHIPTAIL --clear --backtitle "$BACKTITLE" --title "Guardado" \
        --msgbox "Configuración guardada en:\n\n$CONFIG_FILE\n$HOSTAPD_CONF\n$DNSMASQ_CONF\n\nPara aplicar: sudo systemctl restart escama-ap.service" 14 70
    exit 0
}

main_menu
