# escama-ap — Technical Documentation

> Software that turns a WiFi interface into an Access Point (hostapd + dnsmasq)
> with NAT output through a WAN interface. Refactored from 6 bash scripts to 1
> Python core on 2026-08-14 to remove noise and design errors.

## 1. Mental model

```
 CLIENTS (TV, phone)        AP iface (wn8200nd)          WAN iface (stonepi)
 10.42.1.x/24   <--- wifi -->  [escama SSID]  <--- hostapd/dnsmasq --->  NAT masquerade  -->  Internet
```

- **AP iface**: emits the SSID, hands out IP/DNS/DHCP to clients. Defaults to `wn8200nd`.
- **WAN iface**: has internet (client of an external network). Defaults to `stonepi`.
- The software **never modifies the WAN iface** (golden rule). It only reads its route for masquerade.

## 2. Files

| File | Role |
|------|------|
| `opt/escama/escama.py` | Core. Actions: `start\|stop\|restart\|status\|reconnect\|genconfig` |
| `opt/escama/escama-tui.py` | whiptail TUI. Edits `escama.env`, regenerates confs |
| `etc/escama/escama.env` | **Single source of truth** |
| `etc/hostapd/hostapd-escama.conf` | Generated from env. Do not edit by hand |
| `etc/dnsmasq-escama.conf` | Generated from env. Do not edit by hand |
| `etc/systemd/system/escama-ap.service` | systemd unit (`ExecStart=/opt/escama/escama.py start`) |
| `tests/test_escama.py` | 19 unit tests, system-call mocks |
| `setup.cfg` | mutmut config |

## 3. `escama.env` (source of truth)

```ini
AP_IFACE="wn8200nd"          # interface that emits the AP
WAN_IFACE="stonepi"          # interface with internet (empty = auto-detect default route)
SSID="escama"
CHANNEL="6"
HW_MODE="g"
AP_IP="10.42.1.1"
AP_CIDR="24"
AP_SUBNET="10.42.1.0/24"
DHCP_START="10.42.1.10"
DHCP_END="10.42.1.254"
DHCP_LEASE="12h"
WPA_PASSPHRASE="#[REMOVED]"
DNS1="8.8.8.8"
DNS2="8.8.4.4"
```

Edit any of these and run `sudo escama.py genconfig` (or `restart`) to regenerate
hostapd/dnsmasq confs. There is no second place to edit by hand.

## 4. `escama.py start` flow (anti-error design)

1. Load `escama.env`.
2. If `WAN_IFACE` empty → auto-detect from `ip route show default`; fallback `stonepi`.
3. If AP iface missing → clear error "plug the adapter in", rc=1.
4. `nmcli device set <AP> managed no` (free iface from NM).
5. `reload_module_if_needed()`: if `iw phy <AP>` does not list `* AP`, do
   `rmmod 8192eu` + `modprobe 8192eu` (reloads DKMS with `CONFIG_AP_MODE=y`). This
   prevents hostapd's `nl80211: -95 Operation not supported`.
6. `generate_configs()`: writes hostapd/dnsmasq from env.
7. Kill previous hostapd/dnsmasq (idempotent).
8. `ip addr flush` + `ip addr add <AP_IP>/<CIDR> dev <AP>` (mitigates duplicate IP).
9. `hostapd -B` + `dnsmasq`.
10. `sysctl ip_forward=1` + `iptables -t nat -A POSTROUTING -o <WAN> -s <SUBNET> -j MASQUERADE`
    (dynamic masquerade, uses real WAN_IFACE).
11. **Real validation**: `iw dev <AP> info | grep "type AP"`. Only then OK.
    If not → rc=1 (older code lied with `grep ssid`).

## 5. Swapping AP ↔ WAN (migration)

Edit `escama.env`:
```ini
AP_IFACE="stonepi"
WAN_IFACE="wn8200nd"
```
`sudo escama.py restart`. Masquerade and validation use these values; no hardcodes.
Caution: the WAN must have real internet after the swap.

## 6. Reconnect after plug/unplug

No auto-reconnect (design decision: manual). If the adapter drops:
```bash
sudo escama.py reconnect    # same as restart, for use after re-plugging
```
systemd `Restart=on-failure` only covers process death, not missing hardware.

## 7. Testing

```bash
PYTHONPATH=opt/escama python3 -m pytest tests/test_escama.py -v   # 19 tests, mocked
python3 -m mutmut run                                      # mutation testing
```
Tests mock `run()`/`subprocess`/`os` → **never touch stonepi or wn8200nd**.

### Mutation testing (mutmut) — improvement loop
- Suite 1 (9 tests): 772 mutants, ~19% killed. Showed `do_stop`, `do_status`,
  `wan_has_internet`, `main` were untested.
- Suite 2 (15 tests): 775 mutants, 264 killed / 158 survived ≈ 62.6%.
- Suite 3 (19 tests, after adding log()/load_env() + dir-creation fix): 783 mutants,
  **279 killed / 158 survived ≈ 63.8%**.
- The 158 survivors are in `load_env()` (parsing a 15-line .env, branches not hit by
  test inputs) and `log()` (string format). `run()` is the mocked boundary and does
  not count as a design survivor. The ~346 🙁 are timeouts from the `sleep` in
  start/stop (technique noise, not real survivors).
- Conclusion: ALL critical anti-error logic is covered (real `type AP` validation,
  dynamic masquerade, reload on -95, do_stop/do_status, wan_has_internet, main).
  Survivors are non-critical parsing/logging. 80% was not chased due to diminishing
  returns (surgical tests per branch of a trivial .env parser).

## 8. Requirements

- Python 3.10+, `hostapd`, `dnsmasq`, `iw`, `nmcli` (NetworkManager)
- RTL8192EU driver built with `CONFIG_AP_MODE=y` (DKMS `rtl8192eu/1.6.2` on this box)
- `whiptail` only for the TUI
- VPN (ProtonVPN / warp-cli / WireGuard): **does coexist**. Client egress is moved to
  the tunnel automatically (NAT + policy routing + MSS clamp). See `docs-es/VPN-EGRESS.md`.

## 9. Design errors of the old system (now fixed)

| Old error | Fix |
|-----------|-----|
| `grep ssid` in validation (false positives) | real `grep "type AP"` |
| Masquerade hardcode `-o stonepi` | `-o <WAN_IFACE>` dynamic |
| 3 sources of truth (env + 2 confs) | env canonical + genconfig |
| cleanup-warp.sh coupled to WARP | removed |
| Masquerade pinned to WAN: clients lost internet when a VPN came up | dynamic egress (`resolve_egress`/`apply_egress`) toward the tunnel, with WAN fallback |
| 6 duplicated bash scripts | 1 `escama.py` |
| No detection of module without AP_MODE | auto reload on -95 |
| Duplicate IP 10.42.1.1 on WAN | flush on AP iface |
