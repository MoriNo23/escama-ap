# Security Policy

## Reporting a vulnerability

Do **not** open a public issue for security problems.

Use [GitHub's private vulnerability reporting](https://github.com/MoriNo23/escama-ap/security/advisories/new)
for anything that could expose traffic, weaken the AP, or escalate privileges
(NAT/iptables handling, udev rules, the capabilities launcher, passphrase handling).

You can expect a response within a few days. If a report is confirmed, a fix
lands in the next patch release and the advisory is published with credit
unless you prefer otherwise.

## Scope

- `opt/escama/escama.py` (core), `opt/escama/escama-tui.py` (TUI)
- `opt/escama/escama-launch.c` (capabilities launcher)
- `install.sh` (installer / systemd units)

Out of scope: misconfiguration of hostapd/dnsmasq by the user, and issues that
require local root already (the tool assumes the operator is root).
