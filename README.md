# stonepi-ap

WiFi Access Point service for Stonepi, with WARP coexistence.

## Files

- `opt/stonepi/start-ap.sh` – brings up hostapd + dnsmasq
- `opt/stonepi/cleanup-warp.sh` – nftables rules to coexist with Cloudflare WARP
- `opt/stonepi/detect-iface.sh` – detects AP interface by name, MAC, or fallback
- `etc/hostapd/hostapd-stonepi.conf` – hostapd config (SSID: `stonepi`, WPA2-PSK)
- `etc/dnsmasq-stonepi.conf` – DHCP range `10.42.1.10–254`
- `etc/systemd/system/stonepi-ap.service` – systemd unit

## Installation

1. Copy files to system locations:
   ```bash
   sudo cp -r opt/stonepi /opt/
   sudo cp etc/hostapd/hostapd-stonepi.conf /etc/hostapd/
   sudo cp etc/dnsmasq-stonepi.conf /etc/
   sudo cp etc/systemd/system/stonepi-ap.service /etc/systemd/system/
   ```

2. Enable and start:
   ```bash
   sudo systemctl enable stonepi-ap.service
   sudo systemctl start stonepi-ap.service
   ```

3. Check status:
   ```bash
   sudo systemctl status stonepi-ap
   tail -f /var/log/stonepi-ap.log /var/log/stonepi-cleanup.log
   ```

## Dependencies

- `hostapd`
- `dnsmasq`
- `nftables` (for WARP coexistence)
- `iw`
- `nmcli` (optional, to set managed no)

## Network

- AP IP: `10.42.1.1/24`
- DHCP range: `10.42.1.10 – 10.42.1.254`
- WAN interface: detected automatically from default route
- AP interface: detected by name `stonepi`, MAC `02:1a:2b:3c:4d:03`, or first `wlan*` not used for WAN

## WARP Coexistence

If Cloudflare WARP is active, `cleanup-warp.sh` inserts `accept` rules into WARP's nftables table. If WARP is off, it creates its own table `inet stonepi-ap` with forwarding and masquerade.

## Notes

- Passphrase contains special chars (`#`, `@@`); ensure systemd unit escapes properly.
- Interface must be named `stonepi` (via udev) or have the expected MAC.
- Rules may need re-application if WARP restarts; consider a cron/timer.
