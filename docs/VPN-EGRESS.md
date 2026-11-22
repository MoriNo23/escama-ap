# VPN egress (ProtonVPN / WARP / WireGuard) — investigation and options

> Answer to the problem: **"when I connect a VPN on the laptop, the AP clients lose
> internet"**. Here is why it happens, which real options exist, and what escama
> implements.

## 1. Why client internet breaks when the VPN comes up

The AP used to always do this:

```bash
iptables -t nat -A POSTROUTING -o <WAN_IFACE> -s 10.42.1.0/24 -j MASQUERADE
```

That is: NAT **pinned to the physical WAN interface** (`stonepi`). When a tunnel
comes up, three things happen at once, and any of them breaks the clients:

| # | What happens | Effect on clients |
|---|--------------|-------------------|
| 1 | The VPN installs a default route through the tunnel (`0.0.0.0/1` + `128.0.0.0/1` via `proton0`, or table `51820` with `ip rule not fwmark` in WireGuard) | The client packet is routed into the tunnel, but the `MASQUERADE` was `-o stonepi` → it leaves the tunnel **without NAT**, source IP `10.42.1.x`. The VPN server drops it (it does not know that network). Total silence. |
| 2 | The Proton/WireGuard **kill switch** installs `REJECT`/`DROP` rules for everything that does not leave via the tunnel | Even if the packet wanted to leave via `stonepi`, the kill switch blocks it. |
| 3 | Strict `rp_filter` | The reply comes back through the tunnel while the kernel expects it on the egress interface → dropped by reverse-path check. |

Add the classic MTU issue: WireGuard uses 1420 (Proton) or 1280 (WARP). Without MSS
clamping, clients complete the TCP handshake fine but heavy websites hang half-loaded.

**Conclusion:** you do not have to choose between VPN and AP. The NAT and the
routing need to point at the tunnel instead of the physical adapter.

## 2. Existing options (and which one is worth it)

### Option A — dynamic NAT toward the tunnel  ✅ *implemented, the recommended one*

Move the AP egress to the tunnel interface:

```bash
iptables -t nat -A POSTROUTING -o proton0 -s 10.42.1.0/24 -j MASQUERADE
iptables -A FORWARD -i wn8200nd -o proton0 -s 10.42.1.0/24 -j ACCEPT
iptables -A FORWARD -i proton0 -o wn8200nd -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
```

- **Pro:** clients egress *inside* the VPN (usually what you want: the TV and the
  phone behind Proton's IP). A single change, the WAN is never touched.
- **Con:** the provider must accept NATed client traffic. Proton and WARP do.
- **Requires:** `ip_forward=1`, `rp_filter=2` (loose) and, when the host default
  route is not the tunnel, **policy routing** (see below).

### Option B — Split: clients via WAN, laptop via VPN

Keep `MASQUERADE -o stonepi` and **exclude** the AP traffic from the tunnel
(`ip rule add iif <AP_IFACE> lookup main pref 90`, or Proton/WARP split tunnel).
With `iif` (ingress interface) the rule matches only traffic entering via the
AP: a `from <subnet>` selector would also hijack host-originated packets
carrying that source IP (see `docs/diagnostics/DIAGNOSIS-FINAL.md` §4.1).

- **Pro:** the VPN covers only you; clients keep full speed.
- **Con:** clients browse with your real IP → if the point of the VPN is privacy
  for everyone, this does not work. Proton's kill switch may also keep blocking
  the forward.
- In escama: `EGRESS_MODE="wan"`.

### Option C — Network namespace for the VPN

Put the VPN client inside a `netns` and join the AP through a `veth`.

- **Pro:** total isolation, the VPN never touches host routing.
- **Con:** a lot of complexity (veth, its own resolv.conf, duplicated services).
  It is the recipe that circulates for Docker+WARP. Overkill here.

### Option D — Router-level (OpenWrt / OPNsense with WireGuard)

Put the VPN in the router, not in the laptop.

- **Pro:** the most robust approach, and the one Proton documents officially.
- **Con:** does not apply: here the box *is* the router.

### Option E — WARP Connector / Cloudflare Mesh (warp-cli only)

Cloudflare has an official mode for a Linux host to route a whole LAN: enable
*Override local interface IP*, `ip_forward=1`, and publish the CIDR
(`10.42.1.0/24`) as a route in the Zero Trust dashboard.

- **Pro:** officially supported, with Gateway policies.
- **Con:** needs a Zero Trust account and dashboard setup. Free WARP
  (plain `warp-cli connect`) works with Option A alone.

## 3. What escama implements

`EGRESS_MODE` in `/etc/escama/escama.toml`:

| Mode | Behavior |
|------|----------|
| `auto` *(default)* | Tunnel up → clients egress through the tunnel. No tunnel → **automatic fallback to the WAN**. Clients never lose internet because the VPN went down. |
| `vpn` | Tunnel only. No tunnel → clients **do not** browse (kill switch, fail-closed). Zero real-IP leakage. |
| `wan` | Classic behavior: always NAT via the WAN, VPN ignored (Option B). |

### Tunnel detection

`VPN_IFACE=""` = auto-detect. Recognized, in this order:

`proton0` (Proton OpenVPN / official app) → `pvpn0`, `protonwire0` (Proton
WireGuard) → `CloudflareWARP`, `warp0` (warp-cli, both WireGuard and MASQUE) →
`nordlynx` → `mullvad-wg` → `wg0` → `tun0` → `tailscale0`.

It also detects any device whose kind is `wireguard`, or that has `tun_flags`
(tun/tap), or `ppp`. `ipv6leakintrf0` and `pvpnksintrf0` are blacklisted: they are
Proton's anti-leak *dummy* interfaces; picking them as egress would send traffic
into a black hole.

If you run several tunnels, pin one manually: `VPN_IFACE="proton0"`.

In the TUI, choose `Interfaz WAN: AUTO` to store `WAN_IFACE=""`: escama detects
the interface with the default route and reapplies egress on save, without
stopping the AP.

### What gets applied when the egress is the VPN

1. `MASQUERADE -o <tunnel> -s <AP_SUBNET>` (instead of `-o WAN`).
2. Explicit AP↔tunnel `FORWARD` rules with conntrack (survives a default
   `FORWARD DROP`, which is what Proton's kill switch leaves behind).
3. `rp_filter=2` (loose) on `all` and on the AP iface → replies coming back
   through the tunnel are not discarded.
4. **Policy routing** (`VPN_FORCE_ROUTE="yes"`): table `51821` with
   `default dev <tunnel>` + `ip rule add iif <AP_IFACE> lookup 51821 pref 100`.
   The rule matches the AP **ingress interface** (`iif`), not the source subnet:
   a `from <subnet>` selector would also hijack host-originated packets from the
   AP IP into the tunnel (see `docs/diagnostics/DIAGNOSIS-FINAL.md` §4.1).
   This is **mandatory with warp-cli**, which uses split tunnel + fwmark and no
   flat default route; without the rule, client packets never reach the tunnel.
5. **MSS clamping** (`VPN_MSS_CLAMP="yes"`): `TCPMSS --clamp-mss-to-pmtu` on
   `mangle FORWARD -o <tunnel>`. Without it, WARP (MTU 1280) breaks half the
   internet for clients.
6. **DHCP MTU option**: clients get the tunnel's real MTU.
7. **Own kill switch**: `FORWARD -i <AP> -o <WAN> -s <SUBNET> -j REJECT`, so not
   a single AP packet leaks out through the WAN in the clear while the VPN is up.
8. **DNS**: `VPN_DNS1/VPN_DNS2` replace `DNS1/DNS2` in DHCP. Recommended:
   otherwise clients keep asking `8.8.8.8`, a blatant DNS leak (and with
   Proton's kill switch, it does not even resolve).
   - ProtonVPN: `10.2.0.1`
   - WARP: `1.1.1.1`, `1.0.0.1`

## 4. Usage

```bash
sudo escama status     # shows: tunnels up, mode, and where clients egress
sudo escama egress     # re-evaluates and re-applies WITHOUT dropping the AP
sudo escama egress vpn # force VPN mode now
sudo escama egress wan # force WAN egress now
sudo escama egress proton0   # force a specific tunnel
sudo escama watch 5    # loop: follows tunnel state and re-applies alone
```

Typical ProtonVPN flow:

```bash
sudo escama start          # AP up, egress via stonepi
protonvpn-app / wg-quick up protonnl
sudo escama egress         # detects proton0 and moves NAT into the tunnel
# ...when the VPN goes down:
sudo escama egress         # falls back to stonepi by itself
```

To make it automatic (no need to remember `egress`):

```bash
sudo ./install.sh enable   # enables escama-ap + escama-egress (systemctl enable --now)
```

That service runs `escama watch 5`: every 5 s it compares the computed egress
against the applied one; on change it re-applies NAT + policy routing + DNS and
SIGHUPs dnsmasq. Connect Proton and within ≤5 s clients are already egressing
through the tunnel.

## 5. Provider-specific cases

### ProtonVPN (official app / OpenVPN)
Interface `proton0`. The app installs a kill switch with iptables plus the dummy
interfaces `ipv6leakintrf0` / `pvpnksintrf0`. escama ignores those and adds
explicit FORWARD rules, so the kill switch does not kill the clients. Tunnel DNS:
`10.2.0.1`.

### ProtonVPN WireGuard (wg-quick with a downloaded .conf)
The interface name **is the file name** (`protonnl.conf` → `protonnl`), not
`wg0`. That is why detection is by *kind* `wireguard` and not by name alone.
Note: `wg-quick` with `AllowedIPs = 0.0.0.0/0` uses fwmark policy routing and
puts routes in table `51820` — our table `51821` with `ip rule iif <AP> ...`
wins by `pref 100` and resolves the case.

### warp-cli (Cloudflare WARP)
Interface `CloudflareWARP`. The case where `VPN_FORCE_ROUTE` and MSS clamping
matter the most (MTU 1280). Notes:
- WARP excludes RFC1918 ranges from the tunnel by default (split tunnel). AP
  traffic to the internet still enters the tunnel thanks to the policy routing
  rule.
- If you run WARP in **proxy** mode (`warp-cli mode proxy`, SOCKS5 on :1080)
  **there is no interface to NAT**: no IP-level egress exists. The only way out
  is a transparent proxy (redsocks) or switching to tunnel mode
  (`warp-cli mode warp`).
- To make it "official" with a Zero Trust account: WARP Connector, with *Override
  local interface IP* enabled and `10.42.1.0/24` published as a route.
- The old README said *"WARP + AP cannot coexist by Linux design"*. **False**:
  they did not coexist because NAT was pinned to the WAN. With NAT + policy
  routing toward `CloudflareWARP` they coexist fine.

### Tailscale (management only)
`tailscale0` is a management interface: remote access to the host (for example,
OpenCode from your phone). It is never selected automatically as egress, even
with `EGRESS_MODE="auto"` or `"vpn"`. With `auto` the clients use the WAN; with
`vpn` they stay fail-closed. To use it deliberately, pin
`VPN_IFACE="tailscale0"` after configuring an exit node
(`tailscale up --exit-node=<node>`). escama checks the exit node read-only via
`tailscale status --json`; if there is none, it fails closed with an explicit
message and installs no NAT toward the tunnel.

### Cleanup and reconciliation

Every rule escama installs carries `-m comment --comment escama`. On `stop` or
an egress change the core reads `iptables-save` and `ip rule show` first and
deletes its own rules by marker, AP subnet and table `51821`. The state file
(`escama-egress.state`) is now a cache for `IPFWD`/`RP_FILTER` and the previous
egress: cleanup no longer depends on it, so a stale or missing file (or a
different `euid` mode) cannot leave orphaned NAT or policy rules.

The AP/WAN roles detected at `start` are saved to `escama-roles.state` and read
back by `stop`, `egress` and `watch`; a config still pointing at the old
interface no longer makes cleanup act on the wrong NIC. `apply_egress` takes a
`flock` and verifies the NAT rule in the kernel before reporting success.

## 6. Quick diagnosis

```bash
sudo escama status                      # which tunnel does it see, what did it apply?
ip rule                                 # is the iif <AP_IFACE> lookup 51821 rule there?
ip route show table 51821               # default dev <tunnel>?
sudo iptables -t nat -S POSTROUTING     # is MASQUERADE -o <tunnel>?
sudo iptables -S FORWARD                # ACCEPT AP<->tunnel? any VPN DROP in the way?
cat /proc/sys/net/ipv4/ip_forward       # 1
sysctl net.ipv4.conf.all.rp_filter      # 2 (loose) while the VPN is up
ping -I 10.42.1.1 1.1.1.1               # the host itself, with the AP IP: does it egress?
```

Symptoms and likely cause:

| Symptom | Cause |
|---------|-------|
| Client associates and gets an IP, but nothing loads | NAT still pointing at the old WAN → `sudo escama egress` |
| Ping to IPs OK, DNS does not resolve | DNS leak blocked by the kill switch → set `VPN_DNS1` |
| Small pages load, heavy ones hang | MTU/PMTU → `VPN_MSS_CLAMP="yes"` |
| After disconnecting the VPN, clients stay offline | You were in `EGRESS_MODE="vpn"` (fail-closed, intentional) → use `auto` |
| Slow double NAT | Normal: AP NAT + VPN provider NAT. No fix within this scheme. |
