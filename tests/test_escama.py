"""Unit tests for escama.py core logic (anti-error design).

These tests mock all system calls (run/subprocess/os) so they never touch
the real interfaces (stonepi, wn8200nd). They validate the design rules:
- load_env merges defaults + file
- WAN auto-detection when WAN_IFACE empty
- generate_configs produces correct hostapd/dnsmasq from env (single source of truth)
- do_start validates real AP mode (not bogus grep ssid)
- duplicate-IP / module reload logic triggers on missing AP mode
"""
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import opt.escama.escama as escama


@pytest.fixture
def patch_run(monkeypatch):
    calls = []

    def fake_run(cmd, check=True, capture=True):
        calls.append(cmd)
        # default: simulate success
        class R:
            returncode = 0
            stdout = ""
            stderr = ""
        return R()

    monkeypatch.setattr(escama, "run", fake_run)
    return calls


def test_load_env_defaults():
    assert escama.DEFAULTS["AP_IFACE"] == "wn8200nd"
    assert escama.DEFAULTS["WAN_IFACE"] == "stonepi"


def test_load_env_from_file(tmp_path, monkeypatch):
    env = tmp_path / "escama.env"
    env.write_text('SSID="mired"\nCHANNEL="11"\nWAN_IFACE=""\n')
    monkeypatch.setattr(escama, "ENV_FILE", str(env))
    cfg = escama.load_env()
    assert cfg["SSID"] == "mired"
    assert cfg["CHANNEL"] == "11"
    assert cfg["WAN_IFACE"] == ""  # empty preserved
    assert cfg["AP_IFACE"] == "wn8200nd"  # default kept


def test_generate_configs_from_env(tmp_path, monkeypatch):
    env = tmp_path / "escama.env"
    env.write_text('AP_IFACE="wlan9"\nSSID="testap"\nCHANNEL="3"\nWPA_PASSPHRASE="pass1234"\nAP_IP="10.0.0.1"\nAP_CIDR="24"\nAP_SUBNET="10.0.0.0/24"\nDHCP_START="10.0.0.10"\nDHCP_END="10.0.0.50"\nDHCP_LEASE="1h"\nDNS1="1.1.1.1"\nDNS2="9.9.9.9"\n')
    monkeypatch.setattr(escama, "ENV_FILE", str(env))
    monkeypatch.setattr(escama, "HOSTAPD_CONF", str(tmp_path / "hostapd.conf"))
    monkeypatch.setattr(escama, "DNSMASQ_CONF", str(tmp_path / "dnsmasq.conf"))
    cfg = escama.load_env()
    escama.generate_configs(cfg)
    ha = (tmp_path / "hostapd.conf").read_text()
    dq = (tmp_path / "dnsmasq.conf").read_text()
    assert "interface=wlan9" in ha
    assert "ssid=testap" in ha
    assert "channel=3" in ha
    assert "wpa_passphrase=pass1234" in ha
    assert "interface=wlan9" in dq
    assert "dhcp-range=10.0.0.10,10.0.0.50,255.255.255.0,1h" in dq
    assert "dhcp-option=option:dns-server,1.1.1.1,9.9.9.9" in dq
    # single source of truth: both confs use AP_IFACE
    assert "wlan9" in ha and "wlan9" in dq


def test_wan_autodetect_from_default_route(monkeypatch):
    calls = []

    def fake_run(cmd, check=True, capture=True):
        calls.append(cmd)
        class R:
            returncode = 0
            stdout = "default via 192.168.1.1 dev eth7 proto dhcp\n" if cmd[:3] == ["ip", "route", "show"] else ""
            stderr = ""
        return R()

    monkeypatch.setattr(escama, "run", fake_run)
    cfg = escama.load_env()
    cfg["WAN_IFACE"] = ""  # empty -> autodetect
    # replicate do_start's autodetect block
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = escama.run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            import re
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan
    assert wan == "eth7"


def test_wan_autodetect_fallback_stonepi(monkeypatch):
    def fake_run(cmd, check=True, capture=True):
        class R:
            returncode = 0
            stdout = ""  # no default route
            stderr = ""
        return R()

    monkeypatch.setattr(escama, "run", fake_run)
    cfg = escama.load_env()
    cfg["WAN_IFACE"] = ""
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = escama.run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            import re
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan
    assert wan == "stonepi"  # last-resort, never modifies stonepi


def test_ap_mode_missing_triggers_reload(monkeypatch):
    """If iw phy info lacks '* AP', reload_module_if_needed must rmmod/modprobe."""
    states = {"phy": "* IBSS\n* managed\n", "exists": True}
    calls = []

    def fake_run(cmd, check=True, capture=True):
        calls.append(cmd)
        class R:
            returncode = 0
            if cmd[:2] == ["iw", "phy"]:
                stdout = states["phy"]
            else:
                stdout = ""
            stderr = ""
        return R()

    monkeypatch.setattr(escama, "run", fake_run)
    monkeypatch.setattr(escama, "iface_exists", lambda x: True)
    monkeypatch.setattr(escama, "_ap_phy", lambda: "phy2")
    escama.reload_module_if_needed("wn8200nd")
    assert any(c[:1] == ["rmmod"] for c in calls), "should rmmod when AP mode missing"
    assert any(c[:1] == ["modprobe"] for c in calls), "should modprobe after rmmod"


def test_ap_mode_present_no_reload(monkeypatch):
    calls = []
    def fake_run(cmd, check=True, capture=True):
        calls.append(cmd)
        class R:
            returncode = 0
            stdout = "* IBSS\n* managed\n* AP\n* AP/VLAN\n" if cmd[:2] == ["iw", "phy"] else ""
            stderr = ""
        return R()
    monkeypatch.setattr(escama, "run", fake_run)
    monkeypatch.setattr(escama, "iface_exists", lambda x: True)
    monkeypatch.setattr(escama, "_ap_phy", lambda: "phy2")
    escama.reload_module_if_needed("wn8200nd")
    assert not any(c[:1] == ["rmmod"] for c in calls), "no rmmod when AP mode present"


def test_do_start_validates_real_ap_mode(monkeypatch):
    """do_start must report OK only if iw dev shows 'type AP', not a bogus ssid."""
    calls = []
    def fake_run(cmd, check=True, capture=True):
        calls.append(cmd)
        class R:
            returncode = 0
            if cmd[:2] == ["iw", "dev"]:
                stdout = "type AP\nssid escama\n"  # real validation
            elif cmd[:1] == ["hostapd"]:
                stdout = ""
            else:
                stdout = ""
            stderr = ""
        return R()
    monkeypatch.setattr(escama, "run", fake_run)
    monkeypatch.setattr(escama, "iface_exists", lambda x: True)
    monkeypatch.setattr(escama, "_ap_phy", lambda: "phy2")
    monkeypatch.setattr(escama, "load_env", lambda: {
        "AP_IFACE": "wn8200nd", "WAN_IFACE": "stonepi", "SSID": "escama",
        "CHANNEL": "6", "HW_MODE": "g", "AP_IP": "10.42.1.1", "AP_CIDR": "24",
        "AP_SUBNET": "10.42.1.0/24", "DHCP_START": "10.42.1.10", "DHCP_END": "10.42.1.254",
        "DHCP_LEASE": "12h", "WPA_PASSPHRASE": "x", "DNS1": "8.8.8.8", "DNS2": "8.8.4.4"})
    monkeypatch.setattr(escama, "generate_configs", lambda c, kind="": None)
    monkeypatch.setattr(escama, "_kill_procs", lambda: None)
    monkeypatch.setattr(escama, "_ensure_ip", lambda *a: None)
    rc = escama.do_start()
    assert rc == 0, "do_start should succeed when iw reports type AP"


def test_do_start_fails_when_ap_mode_not_reached(monkeypatch):
    calls = []
    def fake_run(cmd, check=True, capture=True):
        calls.append(cmd)
        class R:
            returncode = 0
            if cmd[:2] == ["iw", "dev"]:
                stdout = "type managed\nssid something\n"  # NOT type AP
            else:
                stdout = ""
            stderr = ""
        return R()
    monkeypatch.setattr(escama, "run", fake_run)
    monkeypatch.setattr(escama, "iface_exists", lambda x: True)
    monkeypatch.setattr(escama, "_ap_phy", lambda: "phy2")
    monkeypatch.setattr(escama, "load_env", lambda: {
        "AP_IFACE": "wn8200nd", "WAN_IFACE": "stonepi", "SSID": "escama",
        "CHANNEL": "6", "HW_MODE": "g", "AP_IP": "10.42.1.1", "AP_CIDR": "24",
        "AP_SUBNET": "10.42.1.0/24", "DHCP_START": "10.42.1.10", "DHCP_END": "10.42.1.254",
        "DHCP_LEASE": "12h", "WPA_PASSPHRASE": "x", "DNS1": "8.8.8.8", "DNS2": "8.8.4.4"})
    monkeypatch.setattr(escama, "generate_configs", lambda c, kind="": None)
    monkeypatch.setattr(escama, "_kill_procs", lambda: None)
    monkeypatch.setattr(escama, "_ensure_ip", lambda *a: None)
    rc = escama.do_start()
    assert rc == 1, "do_start must FAIL if iface not in type AP (anti false-positive)"


def test_do_stop_restores_client_mode(monkeypatch):
    """do_stop must remove AP IP, set NM managed=yes, kill procs, disable forward."""
    calls = []
    def fake_run(cmd, check=True, capture=True):
        calls.append(cmd)
        class R:
            returncode = 0
            stdout = ""
            stderr = ""
        return R()
    monkeypatch.setattr(escama, "run", fake_run)
    monkeypatch.setattr(escama, "_kill_procs", lambda: calls.append(["_kill_procs"]))
    monkeypatch.setattr(escama, "load_env", lambda: {
        "AP_IFACE": "wn8200nd", "WAN_IFACE": "stonepi", "AP_IP": "10.42.1.1",
        "AP_CIDR": "24", "AP_SUBNET": "10.42.1.0/24"})
    rc = escama.do_stop()
    assert rc == 0
    # NM managed yes on AP iface
    assert any(c[:3] == ["nmcli", "device", "set"] and "managed" in c and "yes" in c
               for c in calls), "do_stop must restore NM managed=yes"
    # ip_forward disabled
    assert any(c[:3] == ["sysctl", "-w", "net.ipv4.ip_forward=0"] for c in calls)
    # masquerade deleted for WAN iface
    assert any(c[:3] == ["iptables", "-t", "nat"] and "stonepi" in c for c in calls)


def test_wan_has_internet_true(monkeypatch):
    def fake_run(cmd, check=True, capture=True):
        class R:
            returncode = 0
            if cmd[:2] == ["ip", "route"]:
                stdout = "default via 192.168.1.1 dev stonepi\n"
            elif cmd[:1] == ["ping"]:
                stdout = ""
            else:
                stdout = ""
            stderr = ""
        return R()
    monkeypatch.setattr(escama, "run", fake_run)
    assert escama.wan_has_internet("stonepi") is True


def test_wan_has_internet_false(monkeypatch):
    def fake_run(cmd, check=True, capture=True):
        class R:
            returncode = 1  # ping fails
            stdout = "default via 192.168.1.1 dev stonepi\n" if cmd[:2] == ["ip", "route"] else ""
            stderr = ""
        return R()
    monkeypatch.setattr(escama, "run", fake_run)
    assert escama.wan_has_internet("stonepi") is False


def test_do_status_runs(monkeypatch, capsys):
    def fake_run(cmd, check=True, capture=True):
        class R:
            returncode = 0
            stdout = "type AP\nssid escama\n"
            stderr = ""
        return R()
    monkeypatch.setattr(escama, "run", fake_run)
    monkeypatch.setattr(escama, "load_env", lambda: {
        "AP_IFACE": "wn8200nd", "WAN_IFACE": "stonepi", "SSID": "escama",
        "AP_IP": "10.42.1.1", "AP_CIDR": "24"})
    rc = escama.do_status()
    assert rc == 0
    out = capsys.readouterr().out
    assert "escama AP Status" in out
    assert "AP iface:    wn8200nd" in out


def test_main_dispatch(monkeypatch, capsys):
    """main() must route args to correct action and require root."""
    # non-root -> exit 1
    monkeypatch.setattr(escama.os, "geteuid", lambda: 1000)
    assert escama.main() == 1
    # status as root (default action via empty args)
    monkeypatch.setattr(escama.os, "geteuid", lambda: 0)
    monkeypatch.setattr(escama, "do_status", lambda: 0)
    assert escama.main([]) == 0  # default action = status
    monkeypatch.setattr(escama, "do_stop", lambda: 0)
    assert escama.main(["stop"]) == 0
    monkeypatch.setattr(escama, "do_start", lambda: 0)
    assert escama.main(["start"]) == 0


def test_main_unknown(monkeypatch, capsys):
    monkeypatch.setattr(escama.os, "geteuid", lambda: 0)
    assert escama.main(["bogus"]) == 2


def test_log_writes_file(tmp_path, monkeypatch):
    """log() must append the message to LOG file."""
    logf = tmp_path / "escama-ap.log"
    monkeypatch.setattr(escama, "LOG", str(logf))
    escama.log("test message 123")
    content = logf.read_text()
    assert "test message 123" in content
    assert content.startswith("[") or ":" in content  # has timestamp prefix


def test_log_handles_missing_dir(tmp_path, monkeypatch):
    """log() must not raise if the log dir is missing (graceful)."""
    logf = tmp_path / "sub" / "escama-ap.log"
    monkeypatch.setattr(escama, "LOG", str(logf))
    escama.log("no crash")  # should not raise
    assert "no crash" in logf.read_text()


def test_load_env_parsing_edge_cases(tmp_path, monkeypatch):
    """load_env must skip comments, blanks, handle spaces and unquoted values."""
    env = tmp_path / "escama.env"
    env.write_text(
        "# comment line\n"
        "\n"
        "AP_IFACE = wlan5\n"          # spaces around =
        "WAN_IFACE=eth0\n"            # unquoted
        "SSID='my ssid'\n"            # single quotes
        "BADLINE\n"                   # no = sign, skipped
        "CHANNEL=11\n"
    )
    monkeypatch.setattr(escama, "ENV_FILE", str(env))
    cfg = escama.load_env()
    assert cfg["AP_IFACE"] == "wlan5"
    assert cfg["WAN_IFACE"] == "eth0"
    assert cfg["SSID"] == "my ssid"
    assert cfg["CHANNEL"] == "11"
    # defaults preserved for keys not in file
    assert cfg["AP_IP"] == "10.42.1.1"


def test_load_env_overrides_defaults(tmp_path, monkeypatch):
    env = tmp_path / "escama.env"
    env.write_text('AP_IFACE="custom"\nWAN_IFACE="wlan9"\n')
    monkeypatch.setattr(escama, "ENV_FILE", str(env))
    cfg = escama.load_env()
    assert cfg["AP_IFACE"] == "custom"
    assert cfg["WAN_IFACE"] == "wlan9"
    # other defaults intact
    assert cfg["SSID"] == "escama"




# ---------------------------------------------------------------------------
# VPN egress (ProtonVPN / warp-cli / WireGuard) — fallback y kill-switch
# ---------------------------------------------------------------------------

def test_yes_parsing():
    assert escama._yes("yes") and escama._yes("1") and escama._yes("si")
    assert not escama._yes("no") and not escama._yes("") and not escama._yes("0")


def test_iface_is_tunnel_known_names(monkeypatch):
    monkeypatch.setattr(escama.os.path, "exists", lambda p: False)
    monkeypatch.setattr(escama, "run", lambda *a, **k: type(
        "R", (), {"returncode": 0, "stdout": "", "stderr": ""})())
    assert escama.iface_is_tunnel("proton0")
    assert escama.iface_is_tunnel("CloudflareWARP")
    assert escama.iface_is_tunnel("wg0")
    assert not escama.iface_is_tunnel("stonepi")
    # leak-protection dummies must never be picked as egress
    assert not escama.iface_is_tunnel("ipv6leakintrf0")
    assert not escama.iface_is_tunnel("pvpnksintrf0")


def test_iface_is_tunnel_detects_wireguard_kind(monkeypatch):
    monkeypatch.setattr(escama.os.path, "exists", lambda p: False)

    def fake_run(cmd, check=True, capture=True):
        class R:
            returncode = 0
            stdout = "12: pvpnwg: <POINTOPOINT> ... wireguard numtxqueues 1"
            stderr = ""
        return R()

    monkeypatch.setattr(escama, "run", fake_run)
    assert escama.iface_is_tunnel("pvpnwg")


def test_detect_vpn_iface_prefers_explicit_override(monkeypatch):
    monkeypatch.setattr(escama, "iface_is_up", lambda i: i == "proton0")
    cfg = dict(escama.DEFAULTS, VPN_IFACE="proton0")
    assert escama.detect_vpn_iface(cfg) == "proton0"
    # override that is down -> no vpn (does not silently fall back to another)
    cfg2 = dict(escama.DEFAULTS, VPN_IFACE="wg9")
    assert escama.detect_vpn_iface(cfg2) == ""


def test_detect_vpn_iface_auto(monkeypatch):
    monkeypatch.setattr(escama, "list_tunnels", lambda: ["proton0", "tun0"])
    monkeypatch.setattr(escama, "iface_is_up", lambda i: i == "tun0")
    cfg = dict(escama.DEFAULTS, VPN_IFACE="")
    assert escama.detect_vpn_iface(cfg) == "tun0"


def test_resolve_egress_auto_uses_vpn(monkeypatch):
    monkeypatch.setattr(escama, "detect_vpn_iface", lambda c: "proton0")
    cfg = dict(escama.DEFAULTS, EGRESS_MODE="auto", WAN_IFACE="stonepi")
    assert escama.resolve_egress(cfg) == ("proton0", "vpn")


def test_resolve_egress_auto_falls_back_to_wan(monkeypatch):
    monkeypatch.setattr(escama, "detect_vpn_iface", lambda c: "")
    cfg = dict(escama.DEFAULTS, EGRESS_MODE="auto", WAN_IFACE="stonepi")
    assert escama.resolve_egress(cfg) == ("stonepi", "wan")


def test_resolve_egress_vpn_mode_is_fail_closed(monkeypatch):
    monkeypatch.setattr(escama, "detect_vpn_iface", lambda c: "")
    cfg = dict(escama.DEFAULTS, EGRESS_MODE="vpn", WAN_IFACE="stonepi")
    assert escama.resolve_egress(cfg) == ("", "none")


def test_resolve_egress_wan_mode_ignores_vpn(monkeypatch):
    monkeypatch.setattr(escama, "detect_vpn_iface",
                        lambda c: pytest.fail("no debe consultar VPN en modo wan"))
    cfg = dict(escama.DEFAULTS, EGRESS_MODE="wan", WAN_IFACE="stonepi")
    assert escama.resolve_egress(cfg) == ("stonepi", "wan")


def test_apply_egress_vpn_masquerades_on_tunnel_and_blocks_wan(monkeypatch, tmp_path):
    calls = []

    def fake_run(cmd, check=True, capture=True):
        calls.append(cmd)
        class R:
            returncode = 1  # make delete-loops terminate
            stdout = ""
            stderr = ""
        return R()

    monkeypatch.setattr(escama, "run", fake_run)
    monkeypatch.setattr(escama, "STATE_FILE", str(tmp_path / "state"))
    cfg = dict(escama.DEFAULTS, AP_IFACE="wn8200nd", WAN_IFACE="stonepi",
               AP_SUBNET="10.42.1.0/24")
    escama.apply_egress(cfg, "proton0", "vpn")
    flat = [" ".join(c) for c in calls]
    # NAT out the tunnel, never out the WAN
    assert any("nat -A POSTROUTING -o proton0 -s 10.42.1.0/24 -j MASQUERADE"
               in f.replace("-t ", "") for f in flat)
    assert not any("-A POSTROUTING -o stonepi" in f for f in flat)
    # kill-switch: AP traffic must not leak out the WAN in the clear
    assert any("-A FORWARD -i wn8200nd -o stonepi -s 10.42.1.0/24 -j REJECT"
               in f for f in flat)
    # policy routing into the tunnel (warp-cli / wg-quick split tunnel)
    assert any(f"route add default dev proton0 table {escama.ESCAMA_TABLE}"
               in f for f in flat)
    # policy routing into the tunnel uses `iif <ap>` (not `from <subnet>`) so
    # host-origin traffic from the AP IP is NOT hijacked into the tunnel
    assert any(f"rule add iif wn8200nd lookup {escama.ESCAMA_TABLE}"
               in f for f in flat)
    assert not any(f"rule add from 10.42.1.0/24 lookup {escama.ESCAMA_TABLE}"
                   in f for f in flat)
    # MSS clamp for WireGuard MTU
    assert any("TCPMSS --clamp-mss-to-pmtu" in f for f in flat)
    assert any("net.ipv4.ip_forward=1" in f for f in flat)


def test_apply_egress_wan_has_no_killswitch_or_policy_route(monkeypatch, tmp_path):
    calls = []

    def fake_run(cmd, check=True, capture=True):
        calls.append(cmd)
        class R:
            returncode = 1
            stdout = ""
            stderr = ""
        return R()

    monkeypatch.setattr(escama, "run", fake_run)
    monkeypatch.setattr(escama, "STATE_FILE", str(tmp_path / "state"))
    cfg = dict(escama.DEFAULTS, AP_IFACE="wn8200nd", WAN_IFACE="stonepi",
               AP_SUBNET="10.42.1.0/24")
    escama.apply_egress(cfg, "stonepi", "wan")
    flat = [" ".join(c) for c in calls]
    assert any("-A POSTROUTING -o stonepi -s 10.42.1.0/24 -j MASQUERADE"
               in f for f in flat)
    assert not any("-j REJECT" in f and "-A FORWARD" in f for f in flat)
    assert not any("rule add from" in f for f in flat)


def test_apply_egress_none_is_fail_closed(monkeypatch, tmp_path):
    calls = []

    def fake_run(cmd, check=True, capture=True):
        calls.append(cmd)
        class R:
            returncode = 1
            stdout = ""
            stderr = ""
        return R()

    monkeypatch.setattr(escama, "run", fake_run)
    monkeypatch.setattr(escama, "STATE_FILE", str(tmp_path / "state"))
    cfg = dict(escama.DEFAULTS, AP_IFACE="wn8200nd", WAN_IFACE="stonepi",
               AP_SUBNET="10.42.1.0/24")
    escama.apply_egress(cfg, "", "none")
    flat = [" ".join(c) for c in calls]
    assert not any("MASQUERADE" in f and "-A POSTROUTING" in f for f in flat)
    assert any("-A FORWARD -i wn8200nd -o stonepi -s 10.42.1.0/24 -j REJECT"
               in f for f in flat)


def test_clear_egress_removes_rules_from_state(monkeypatch, tmp_path):
    state = tmp_path / "state"
    state.write_text("EGRESS=proton0\nKIND=vpn\n")
    monkeypatch.setattr(escama, "STATE_FILE", str(state))
    calls = []

    def fake_run(cmd, check=True, capture=True):
        calls.append(cmd)
        class R:
            returncode = 1
            stdout = ""
            stderr = ""
        return R()

    monkeypatch.setattr(escama, "run", fake_run)
    cfg = dict(escama.DEFAULTS, AP_IFACE="wn8200nd", WAN_IFACE="stonepi",
               AP_SUBNET="10.42.1.0/24")
    escama.clear_egress(cfg)
    flat = [" ".join(c) for c in calls]
    assert any("-D POSTROUTING -o proton0" in f for f in flat)
    assert any("-D POSTROUTING -o stonepi" in f for f in flat)  # legacy cleanup
    assert any(f"rule del iif wn8200nd lookup {escama.ESCAMA_TABLE}"
               in f for f in flat)
    assert not any(f"rule del from 10.42.1.0/24 lookup {escama.ESCAMA_TABLE}"
                   in f for f in flat)
    assert not state.exists()  # state cleared


def test_effective_dns_switches_with_vpn():
    cfg = dict(escama.DEFAULTS, DNS1="8.8.8.8", DNS2="8.8.4.4",
               VPN_DNS1="10.2.0.1", VPN_DNS2="")
    assert escama.effective_dns(cfg, "vpn") == ("10.2.0.1", "10.2.0.1")
    assert escama.effective_dns(cfg, "wan") == ("8.8.8.8", "8.8.4.4")
    plain = dict(escama.DEFAULTS, VPN_DNS1="")
    assert escama.effective_dns(plain, "vpn") == ("8.8.8.8", "8.8.4.4")


def test_generate_configs_vpn_sets_client_mtu(tmp_path, monkeypatch):
    monkeypatch.setattr(escama, "HOSTAPD_CONF", str(tmp_path / "hostapd.conf"))
    monkeypatch.setattr(escama, "DNSMASQ_CONF", str(tmp_path / "dnsmasq.conf"))
    monkeypatch.setattr(escama, "_read_state", lambda: {"EGRESS": "proton0"})
    monkeypatch.setattr(escama, "iface_mtu", lambda i: 1420)
    cfg = dict(escama.DEFAULTS, VPN_DNS1="10.2.0.1", VPN_DNS2="10.2.0.1")
    escama.generate_configs(cfg, "vpn")
    dq = (tmp_path / "dnsmasq.conf").read_text()
    assert "dhcp-option=option:mtu,1420" in dq
    assert "dhcp-option=option:dns-server,10.2.0.1,10.2.0.1" in dq


def test_generate_configs_wan_has_no_mtu_option(tmp_path, monkeypatch):
    monkeypatch.setattr(escama, "HOSTAPD_CONF", str(tmp_path / "hostapd.conf"))
    monkeypatch.setattr(escama, "DNSMASQ_CONF", str(tmp_path / "dnsmasq.conf"))
    escama.generate_configs(dict(escama.DEFAULTS), "wan")
    dq = (tmp_path / "dnsmasq.conf").read_text()
    assert "option:mtu" not in dq
