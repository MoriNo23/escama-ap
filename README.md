# escama-ap

WiFi Access Point service (hostapd + dnsmasq AP converter) with WARP coexistence.

The **AP (designated access point, "escama")** interface defaults to `wn8200nd`
(TL-WN8200ND adapter). The **WAN/internet WiFi interface** keeps the name `stonepi`.

## Files

- `opt/escama/start-ap.sh` – brings up hostapd + dnsmasq
- `opt/escama/stop-ap.sh` – stops AP and restores WiFi client mode
- `opt/escama/toggle-ap.sh` – CLI to toggle AP mode on/off
- `opt/escama/config-tui.sh` – TUI (whiptail) to configure all settings, including AP interface
- `opt/escama/cleanup-warp.sh` – nftables rules to coexist with Cloudflare WARP
- `opt/escama/detect-iface.sh` – detects AP (default `wn8200nd`) and WAN (`stonepi`) interfaces
- `etc/escama/escama.env` – central configuration (generated/edited by the TUI)
- `etc/hostapd/hostapd-escama.conf` – hostapd config (SSID: `escama`, WPA2-PSK)
- `etc/dnsmasq-escama.conf` – DHCP range `10.42.1.10–254`
- `etc/systemd/system/escama-ap.service` – systemd unit

## Installation

1. Copy files to system locations:
   ```bash
   sudo cp -r opt/escama /opt/
   sudo mkdir -p /etc/escama
   sudo cp etc/escama/escama.env /etc/escama/
   sudo cp etc/hostapd/hostapd-escama.conf /etc/hostapd/
   sudo cp etc/dnsmasq-escama.conf /etc/
   sudo cp etc/systemd/system/escama-ap.service /etc/systemd/system/
   ```

2. Enable and start:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable escama-ap.service
   sudo systemctl start escama-ap.service
   ```

3. Check status:
   ```bash
   sudo systemctl status escama-ap
   tail -f /var/log/escama-ap.log /var/log/escama-cleanup.log
   ```

## Configuration (TUI)

Run the TUI to configure everything interactively — including choosing the AP
interface and all network/SSID settings:

```bash
sudo /opt/escama/config-tui.sh
```

This writes `/etc/escama/escama.env` and regenerates the hostapd/dnsmasq configs.
Restart the service to apply:

```bash
sudo systemctl restart escama-ap.service
```

The AP interface is configured via `AP_IFACE` in `/etc/escama/escama.env`
(default: `wn8200nd`). The WAN interface is `WAN_IFACE` (default: `stonepi`).

## CLI Toggle Tool

Use `toggle-ap.sh` to switch between AP mode and normal WiFi client mode:

```bash
sudo /opt/escama/toggle-ap.sh start    # Activar modo AP
sudo /opt/escama/toggle-ap.sh stop     # Detener AP, restaurar WiFi cliente
sudo /opt/escama/toggle-ap.sh restart  # Reiniciar AP
sudo /opt/escama/toggle-ap.sh status   # Ver estado actual
sudo /opt/escama/toggle-ap.sh enable   # Habilitar inicio automatico
sudo /opt/escama/toggle-ap.sh disable  # Deshabilitar y detener AP
```

Shortcuts (equivalent):
```bash
sudo /opt/escama/start-ap.sh           # Iniciar AP (legacy)
sudo /opt/escama/stop-ap.sh            # Detener AP (nuevo)
```

## Dependencies

- `hostapd`
- `dnsmasq`
- `nftables` (for WARP coexistence)
- `iw`
- `nmcli` (optional, to set managed no)
- `whiptail` (for the TUI)

## Network

- AP IP: `10.42.1.1/24`
- DHCP range: `10.42.1.10 – 10.42.1.254`
- AP interface: `wn8200nd` (configurable via `AP_IFACE` in `/etc/escama/escama.env`)
- WAN interface: `stonepi` (configurable via `WAN_IFACE`)

## WARP Coexistence

If Cloudflare WARP is active, `cleanup-warp.sh` inserts `accept` rules into WARP's
nftables table. If WARP is off, it creates its own table `inet escama-ap` with
forwarding and masquerade.

## Notes

- Passphrase contains special chars (`#`, `@@`); ensure config files escape properly.
- The AP interface defaults to `wn8200nd`; override via `AP_IFACE` in `/etc/escama/escama.env`.
- Rules may need re-application if WARP restarts; consider a cron/timer.
