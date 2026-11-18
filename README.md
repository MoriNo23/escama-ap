<div align="center">

# escama-ap

Turns a WiFi adapter into an Access Point on Debian/Linux.
One command brings up the AP (hostapd + dnsmasq); connected clients reach the
internet through the WAN or a VPN tunnel, with automatic NAT.

![version](https://img.shields.io/badge/version-2.1.0-2ea44f)
![python](https://img.shields.io/badge/python-3.10%2B-3776AB?logo=python&logoColor=white)
![platform](https://img.shields.io/badge/platform-Debian%20%2F%20Linux-A81D33?logo=debian&logoColor=white)
![tests](https://img.shields.io/badge/tests-124%20passing-brightgreen)
![config](https://img.shields.io/badge/config-TOML-blue)
![license](https://img.shields.io/badge/license-MIT-green)

[Readme en español](README.es.md)

</div>

```
 client A ┐
 client B ├─ Wi-Fi "escama" ──►  AP (hostapd + dnsmasq)  ── NAT ──► internet
 client C ┘                            │
                              is a VPN tunnel up?
                                        │ yes          │ no
                                        ▼              ▼
                                  exit via tunnel   exit via WAN
```

> Design rule: the WAN interface is **read-only** for escama. Everything it
> configures lives on the AP side.

## Install

```bash
git clone https://github.com/MoriNo23/escama-ap.git
cd escama-ap
sudo ./install.sh install    # code in /opt/escama, escama/escama-tui commands, units
sudo ./install.sh enable     # optional: start at boot
```

The installer never overwrites your configuration: if `/etc/escama/escama.toml`
already exists, new defaults land next to it in `escama.toml.new`.

Before the first start you must set the AP passphrase (escama refuses to run
an open network):

```bash
sudo escama-tui          # option 7 (WPA2 passphrase), Save and Exit
```

## Usage

```bash
sudo escama start         # bring the AP up (hostapd + dnsmasq + NAT + forwarding)
sudo escama stop          # take it down, restore the interface to client mode
sudo escama restart       # stop + start
sudo escama status        # current state (works without sudo)
sudo escama reconnect     # re-up after unplug/replug of the adapter
sudo escama genconfig     # regenerate hostapd/dnsmasq from escama.toml
sudo escama egress        # re-evaluate exit path (VPN/WAN) without dropping the AP
sudo escama egress vpn    # force exit: auto | vpn | wan | <iface>
sudo escama watch         # loop: follow the VPN tunnel, re-apply routing
sudo escama rename <iface> <new>   # rename a WiFi adapter
escama preflight          # machine check (components, version, permissions)

sudo escama-tui           # interactive menu (whiptail) to edit the config
```

## Configuration

Everything lives in `/etc/escama/escama.toml` (TOML, comments included). Edit
it with `escama-tui` or by hand; changes apply with `sudo escama restart`.

```toml
AP_IFACE  = "stonepi"     # interface acting as AP
WAN_IFACE = "wn8200nd"    # the one with internet ("" = auto-detect)
SSID      = "escama"
CHANNEL_MODE = "auto"     # auto = pick from {1,6,11} without overlapping the WAN
EGRESS_MODE  = "auto"     # auto = VPN if a tunnel is up, else WAN
                          # vpn  = kill-switch (no tunnel, no traffic)
                          # wan  = always WAN, ignore the VPN
```

To swap roles (use the current WAN as the AP) just exchange `AP_IFACE` and
`WAN_IFACE`: NAT and validation follow the config, nothing is hardcoded.

## Renaming adapters

USB dongles show up as `wlx<MAC>` (impossible to remember). `rename` writes a
udev rule keyed by MAC and renames the interface instantly:

```bash
sudo escama rename wlx020304050607 wifi-usb
```

- Persistent (survives boots and re-plugs) and live: brings the interface
  down, renames it, brings it back up.
- Rebinds NetworkManager profiles tied to the old name, so your current WiFi
  connection does not drop.
- Updates `AP_IFACE`/`WAN_IFACE` in the toml if they pointed at the old name.
- If that MAC had a manual rule in `70-persistent-net.rules` or similar, it is
  retired and consolidated into `76-escama-ifaces.rules`.

## VPN egress

If the host has a VPN running, AP clients exit through the tunnel instead of
losing internet. ProtonVPN, WARP, WireGuard and OpenVPN are supported
(auto-detected or forced), with policy routing and MSS clamp per tunnel.
Provider-by-provider details: [docs/VPN-EGRESS.md](docs/VPN-EGRESS.md).

## Autostart (systemd)

```bash
sudo ./install.sh enable          # at boot + now
sudo ./install.sh disable         # no boot + stop
sudo ./install.sh enable --user   # at login, no system unit
```

`Restart=on-failure` covers process death, not missing hardware: if the
adapter is unplugged, run `sudo escama reconnect`.

## Without sudo (optional)

Besides the classic `sudo` mode there is a rootless mode: an ELF binary with
`CAP_NET_ADMIN`/`RAW`/`BIND_SERVICE` passes those capabilities to the Python
core (the kernel ignores file capabilities on shebang scripts). It covers
network operations; anything needing to write `/etc` degrades with an explicit
message. `escama status` always shows which mode is running and where logs and
confs land, so "it did not start" is never confused with "I lack permission".

|                             | with sudo             | rootless             |
|-----------------------------|-----------------------|----------------------|
| Network (hostapd, NAT, routes) | yes                | yes, via the launcher |
| Autostart                   | system unit           | user unit            |
| Log                         | `/var/log/escama-ap.log` | `~/.local/state/escama/` |
| Reload driver module        | yes                   | degrades with reason |

## Testing

```bash
python3 -m pytest tests/test_escama.py -q    # 124 tests, ~15 s
```

Tests mock `run()`/`subprocess`/`os`: they never touch real interfaces
(enforced by a fixture that blocks subprocess for the whole suite). Optional
mutation testing with `mutmut run` (config in `setup.cfg`).

## Requirements

- Debian/Linux with NetworkManager (`nmcli`)
- Python 3.10+ — stdlib only, zero dependencies
- `hostapd`, `dnsmasq`, `iw`; `whiptail` for the TUI only
- A WiFi adapter with AP-mode support (rtl8192eu and aic8800 drivers verified)

## Documentation

- [docs/TECHNICAL.md](docs/TECHNICAL.md) — internal design (English)
- [docs-es/TECHNICAL.md](docs-es/TECHNICAL.md) — internal design (Spanish)
- [docs/VPN-EGRESS.md](docs/VPN-EGRESS.md) — tunnel egress, cases, troubleshooting
- [CHANGELOG.md](CHANGELOG.md) — release history
- [SECURITY.md](SECURITY.md) — how to report vulnerabilities

## License

[MIT](LICENSE)
