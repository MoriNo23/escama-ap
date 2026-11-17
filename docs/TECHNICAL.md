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

### 1.1 Modes and runtime state (as of 1.1.0)

- **Two operating modes**: with `sudo` (historical, everything as root) or
  **rootless** — `/opt/escama/escama-launch` is an ELF launcher carrying
  `CAP_NET_ADMIN/NET_RAW/NET_BIND_SERVICE` and passing them to the core, so
  `start|stop|restart|egress` run without sudo. It must be an ELF because the
  kernel ignores file capabilities on shebang scripts. What cannot be rootless
  (driver module reload needs `CAP_SYS_MODULE`, `nmcli` needs NM authorization)
  degrades with an explicit message, never silently.
- **Preflight**: `escama preflight` checks the machine before operating —
  components, repo-vs-installed version, and rootless viability verified with a
  real operation (not `getcap`). Read-only, runs without privilege.
- **Runtime paths depend on privilege**: as root, log/pidfile/state/generated
  confs live in `/var` and `/etc`; without root they move to the user's XDG
  dirs (`~/.local/state`, `XDG_RUNTIME_DIR`, `~/.config/escama`). `escama.toml`
  stays in `/etc` and is only read. `escama status` shows the effective paths.
- **Versioning**: single source in `VERSION`, read at runtime by core, TUI and
  installer (hardcoding it is a tested-against defect). History in `CHANGELOG.md`.
- **Autostart**: privileged system unit, or **user unit**
  (`install.sh enable --user`) which brings the AP up at session login without
  privilege.
- The full mode-vs-mode table lives in `README.md` ("Rootless vs sudo", "Unit
  de usuario").

## 2. Files

| File | Role |
|------|------|
| `opt/escama/escama.py` | Core. Actions: `start\|stop\|restart\|status\|reconnect\|genconfig\|egress\|watch\|preflight` |
| `opt/escama/escama-tui.py` | whiptail TUI. Edits `escama.toml`, regenerates confs |
| `opt/escama/escama-launch.c` | Rootless ELF launcher (capabilities → core); compiled to `/opt/escama/escama-launch` |
| `etc/escama/escama.toml` | **Single source of truth** |
| `etc/hostapd/hostapd-escama.conf` | Generated from env. Do not edit by hand |
| `etc/dnsmasq-escama.conf` | Generated from env. Do not edit by hand |
| `etc/systemd/system/escama-ap.service` | systemd unit (`ExecStart=/opt/escama/escama.py start`) |
| `etc/systemd/user/escama-ap.service` | User unit — autostart without sudo at session login |
| `etc/systemd/user/escama-egress.service` | User unit — egress watcher in rootless mode |
| `VERSION` | Single version source, read at runtime by the three entry points |
| `CHANGELOG.md` | Version history (0.x retrospective + semver per change) |
| `tests/test_escama.py` | 105 unit tests, system-call mocks (command in §7) |
| `setup.cfg` | mutmut config |

## 3. `escama.toml` (source of truth)

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
WPA_PASSPHRASE=""
DNS1="8.8.8.8"
DNS2="8.8.4.4"
```

Edit any of these and run `sudo escama.py genconfig` (or `restart`) to regenerate
hostapd/dnsmasq confs. There is no second place to edit by hand.

## 4. `escama.py start` flow (anti-error design)

1. Load `escama.toml`.
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

Edit `escama.toml`:
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
python3 -m pytest tests/test_escama.py -q   # 105 tests, mocked, ~22s
~/.local/bin/mutmut run                      # mutation testing (reads setup.cfg)
```
Tests mock `run()`/`subprocess`/`os` → **never touch stonepi or wn8200nd**.
It is not a convention but a guarantee: an `autouse` fixture blocks
`subprocess` during the whole suite, so a leaking test fails with the exact
command it tried to run.

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
- The full run-by-run table (up to the 5th run: 105 tests, 2846 mutants,
  ≈43.1% of tested killed) lives in `README.md`.
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
