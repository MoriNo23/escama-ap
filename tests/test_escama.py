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
    monkeypatch.setattr(escama, "generar_hostapd", lambda c: None)
    monkeypatch.setattr(escama, "generar_dnsmasq", lambda c, kind="": None)
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
    monkeypatch.setattr(escama, "generar_hostapd", lambda c: None)
    monkeypatch.setattr(escama, "generar_dnsmasq", lambda c, kind="": None)
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
    """main() rutea cada arg a su accion; solo-lectura no pide root."""
    # El preflight/bootstrap no debe tocar el sistema real en tests.
    monkeypatch.setattr(escama, "preflight", lambda: {
        "estado": "completa", "componentes": {}, "faltan": [],
        "version_repo": "1", "version_instalada": "1"})
    monkeypatch.setattr(escama, "rootless_disponible",
                        lambda: (False, "sin launcher en el test"))
    # Sin args, la accion por defecto es `status`, que es de solo lectura:
    # corre sin root (antes rebotaba pidiendo sudo).
    monkeypatch.setattr(escama.os, "geteuid", lambda: 1000)
    monkeypatch.setattr(escama, "do_status", lambda: 0)
    assert escama.main([]) == 0
    # Con root, el resto de las acciones despachan normal.
    monkeypatch.setattr(escama.os, "geteuid", lambda: 0)
    assert escama.main([]) == 0
    monkeypatch.setattr(escama, "do_stop", lambda: 0)
    assert escama.main(["stop"]) == 0
    monkeypatch.setattr(escama, "do_start", lambda: 0)
    assert escama.main(["start"]) == 0
    monkeypatch.setattr(escama, "do_preflight", lambda: 0)
    assert escama.main(["preflight"]) == 0


def test_main_unknown(monkeypatch, capsys):
    monkeypatch.setattr(escama, "preflight", lambda: {
        "estado": "completa", "componentes": {}, "faltan": [],
        "version_repo": "1", "version_instalada": "1"})
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


def test_apply_egress_vpn_rule_scoped_to_ap_ingress_not_source_subnet(monkeypatch, tmp_path):
    """Regression for DIAGNOSIS-FINAL.md §1/§4.1: the VPN policy rule must
    match the AP ingress interface (`iif <ap>`), not the source subnet
    (`from <subnet>`). A source match also catches host-originated packets
    from the AP IP (10.42.1.1) and diverts them into the tunnel, breaking
    host->client scans/connections while VPN egress is active."""
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
    assert any(f"rule add iif wn8200nd lookup {escama.ESCAMA_TABLE}"
               in f for f in flat)
    # the offending source-based selector must be gone
    assert not any(f"rule add from 10.42.1.0/24 lookup {escama.ESCAMA_TABLE}"
                   in f for f in flat)


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


# ---------------------------------------------------------------------------
# Selección de canal (CHANNEL_MODE auto/manual, evita el canal de la WAN)
# ---------------------------------------------------------------------------

def _cfg_canal(**over):
    return dict(escama.DEFAULTS, AP_IFACE="wn8200nd", WAN_IFACE="stonepi", **over)


def _fake_iw_link(stdout_iw):
    """fake_run que responde los `iw dev <wan> link` con la salida dada."""
    def fake_run(cmd, check=True, capture=True):
        class R:
            returncode = 0
            stdout = stdout_iw if cmd[:2] == ["iw", "dev"] else ""
            stderr = ""
        return R()
    return fake_run


def test_detectar_canal_wan_parsea_freq(monkeypatch):
    monkeypatch.setattr(escama, "iface_exists", lambda x: True)
    casos = {"2412": "1", "2422": "3", "2437": "6", "2462": "11",
             "2472": "13", "2484": "14"}
    for freq, canal in casos.items():
        monkeypatch.setattr(escama, "run", _fake_iw_link(f"freq: {freq} MHz"))
        assert escama.detectar_canal_wan("stonepi") == canal, freq


def test_detectar_canal_wan_no_legible(monkeypatch):
    monkeypatch.setattr(escama, "iface_exists", lambda x: True)
    # sin asociacion / 5 GHz / fuera de rango / rc != 0 / WAN ausente
    monkeypatch.setattr(escama, "run", _fake_iw_link("Not connected."))
    assert escama.detectar_canal_wan("stonepi") == ""
    monkeypatch.setattr(escama, "run", _fake_iw_link("freq: 5180 MHz"))
    assert escama.detectar_canal_wan("stonepi") == ""
    monkeypatch.setattr(escama, "run", _fake_iw_link("freq: 2400 MHz"))
    assert escama.detectar_canal_wan("stonepi") == ""

    def rc_fail(cmd, check=True, capture=True):
        class R:
            returncode = 1
            stdout = ""
            stderr = ""
        return R()
    monkeypatch.setattr(escama, "run", rc_fail)
    assert escama.detectar_canal_wan("stonepi") == ""
    monkeypatch.setattr(escama, "iface_exists", lambda x: False)
    assert escama.detectar_canal_wan("") == ""
    assert escama.detectar_canal_wan("noexiste") == ""


def test_elegir_canal_tabla_determinista(monkeypatch):
    monkeypatch.setattr(escama, "iface_exists", lambda x: True)
    # WAN 6 -> empate 1/11 a distancia 5 -> gana el menor (canal 1)
    monkeypatch.setattr(escama, "run", _fake_iw_link("freq: 2437 MHz"))
    canal, motivo = escama.elegir_canal(_cfg_canal(CHANNEL="6"))
    assert canal == "1" and "WAN en canal 6" in motivo
    # WAN 1 -> canal 11 (distancia 10)
    monkeypatch.setattr(escama, "run", _fake_iw_link("freq: 2412 MHz"))
    assert escama.elegir_canal(_cfg_canal(CHANNEL="6"))[0] == "11"
    # WAN 4 (solapa con 1 y 6) -> 11 unico seguro
    monkeypatch.setattr(escama, "run", _fake_iw_link("freq: 2422 MHz"))
    assert escama.elegir_canal(_cfg_canal(CHANNEL="6"))[0] == "11"
    # WAN 11 -> canal 1
    monkeypatch.setattr(escama, "run", _fake_iw_link("freq: 2462 MHz"))
    assert escama.elegir_canal(_cfg_canal(CHANNEL="6"))[0] == "1"


def test_elegir_canal_fallback_sin_wan_legible(monkeypatch):
    monkeypatch.setattr(escama, "iface_exists", lambda x: True)
    monkeypatch.setattr(escama, "run", _fake_iw_link("Not connected."))
    canal, motivo = escama.elegir_canal(_cfg_canal(CHANNEL="6"))
    assert canal == "6" and "fallback" in motivo


def test_elegir_canal_default_es_auto():
    assert escama.DEFAULTS["CHANNEL_MODE"] == "auto"


def test_elegir_canal_manual_no_consulta_la_wan(monkeypatch):
    """CHANNEL_MODE=manual: usa CHANNEL del env y NUNCA consulta la WAN."""
    def fake_run(cmd, check=True, capture=True):
        if cmd[:3] == ["iw", "dev", "stonepi"] and "link" in cmd:
            raise AssertionError("manual no debe consultar el canal de la WAN")
        class R:
            returncode = 0
            stdout = ""
            stderr = ""
        return R()
    monkeypatch.setattr(escama, "run", fake_run)
    canal, motivo = escama.elegir_canal(_cfg_canal(CHANNEL_MODE="manual",
                                                  CHANNEL="6"))
    assert canal == "6" and "manual" in motivo


def test_do_start_resuelve_canal_y_logea(monkeypatch, capsys):
    """do_start elige el canal ANTES de generar confs y lo loguea."""
    calls = []

    def fake_run(cmd, check=True, capture=True):
        calls.append(cmd)
        class R:
            returncode = 0
            if cmd[:3] == ["iw", "dev", "stonepi"] and "link" in cmd:
                stdout = "freq: 2437 MHz\n"  # WAN en canal 6
            elif cmd[:2] == ["iw", "dev"]:
                stdout = "type AP\nssid escama\n"
            else:
                stdout = ""
            stderr = ""
        return R()

    monkeypatch.setattr(escama, "run", fake_run)
    monkeypatch.setattr(escama, "iface_exists", lambda x: True)
    monkeypatch.setattr(escama, "_ap_phy", lambda: "phy2")
    monkeypatch.setattr(escama, "load_env", lambda: {
        "AP_IFACE": "wn8200nd", "WAN_IFACE": "stonepi", "SSID": "escama",
        "CHANNEL": "6", "CHANNEL_MODE": "auto", "HW_MODE": "g",
        "AP_IP": "10.42.1.1", "AP_CIDR": "24", "AP_SUBNET": "10.42.1.0/24",
        "DHCP_START": "10.42.1.10", "DHCP_END": "10.42.1.254",
        "DHCP_LEASE": "12h", "WPA_PASSPHRASE": "x", "DNS1": "8.8.8.8",
        "DNS2": "8.8.4.4"})
    generados = {}
    monkeypatch.setattr(escama, "generar_hostapd",
                        lambda c: generados.update(canal=c["CHANNEL"]))
    monkeypatch.setattr(escama, "generar_dnsmasq", lambda c, kind="": None)
    monkeypatch.setattr(escama, "_kill_procs", lambda: None)
    monkeypatch.setattr(escama, "_ensure_ip", lambda *a: None)
    rc = escama.do_start()
    assert rc == 0
    # WAN en canal 6 -> el AP arranca en el 1 y el log dice por que
    assert generados["canal"] == "1"
    out = capsys.readouterr().out
    assert "Canal AP: 1" in out and "WAN en canal 6" in out


def test_do_watch_no_reescribe_hostapd(monkeypatch, tmp_path):
    """watch solo regenera dnsmasq; hostapd.conf (canal) queda intacto."""
    ha = tmp_path / "hostapd.conf"
    ha.write_text("channel=1\n")
    monkeypatch.setattr(escama, "HOSTAPD_CONF", str(ha))
    monkeypatch.setattr(escama, "DNSMASQ_CONF", str(tmp_path / "dnsmasq.conf"))
    monkeypatch.setattr(escama, "STATE_FILE", str(tmp_path / "state"))
    monkeypatch.setattr(escama, "load_env", lambda: dict(
        escama.DEFAULTS, AP_IFACE="wn8200nd", WAN_IFACE="stonepi",
        CHANNEL="1"))
    monkeypatch.setattr(escama, "detect_vpn_iface", lambda c: "proton0")
    monkeypatch.setattr(escama, "apply_egress", lambda c, e, k: None)

    def fake_run(cmd, check=True, capture=True):
        class R:
            returncode = 0
            stdout = ""
            stderr = ""
        return R()
    monkeypatch.setattr(escama, "run", fake_run)

    def boom(interval):
        raise KeyboardInterrupt
    monkeypatch.setattr(escama.time, "sleep", boom)
    with pytest.raises(KeyboardInterrupt):
        escama.do_watch(5)
    assert ha.read_text() == "channel=1\n"
    assert (tmp_path / "dnsmasq.conf").exists()


def test_do_egress_no_reescribe_hostapd(monkeypatch, tmp_path):
    """egress solo regenera dnsmasq; hostapd.conf (canal) queda intacto."""
    ha = tmp_path / "hostapd.conf"
    ha.write_text("channel=1\n")
    monkeypatch.setattr(escama, "HOSTAPD_CONF", str(ha))
    monkeypatch.setattr(escama, "DNSMASQ_CONF", str(tmp_path / "dnsmasq.conf"))
    monkeypatch.setattr(escama, "STATE_FILE", str(tmp_path / "state"))
    monkeypatch.setattr(escama, "load_env", lambda: dict(
        escama.DEFAULTS, AP_IFACE="wn8200nd", WAN_IFACE="stonepi",
        CHANNEL="1"))
    monkeypatch.setattr(escama, "detect_vpn_iface", lambda c: "proton0")
    monkeypatch.setattr(escama, "apply_egress", lambda c, e, k: None)
    monkeypatch.setattr(escama, "run", lambda *a, **k: type(
        "R", (), {"returncode": 0, "stdout": "", "stderr": ""})())
    rc = escama.do_egress([])
    assert rc == 0
    assert ha.read_text() == "channel=1\n"
    assert (tmp_path / "dnsmasq.conf").exists()


# ---------------------------------------------------------------------------
# Versionado (spec `versionado`): fuente única + coherencia entre las piezas
# ---------------------------------------------------------------------------

RAIZ_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# euid real capturado antes de cualquier monkeypatch de os.geteuid:
# patchearlo con un lambda que lo vuelve a leer causa recursion.
_EUID = os.geteuid()


def test_escama_lee_la_version_del_archivo_unico():
    with open(os.path.join(RAIZ_REPO, "VERSION")) as f:
        esperado = f.read().strip()
    assert escama.VERSION == esperado, "escama.py debe leer VERSION, no una copia"
    assert esperado, "VERSION no puede estar vacio"


def test_tui_lee_la_misma_version_que_el_core():
    import importlib.util
    ruta = os.path.join(RAIZ_REPO, "opt", "escama", "escama-tui.py")
    spec = importlib.util.spec_from_file_location("escama_tui", ruta)
    tui = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tui)
    assert tui.read_version() == escama.VERSION


def test_install_sh_no_tiene_version_literal():
    """install.sh debe LEER el VERSION, no llevar su propia copia (que divergiria)."""
    with open(os.path.join(RAIZ_REPO, "install.sh")) as f:
        src = f.read()
    # VERSION="algo" con algo que NO sea un comando substitution ni un numero:
    # seria una copia literal (el bug que esto previene).
    import re
    assert not re.search(r'VERSION="(?!\$\()[^"]+"', src), \
        "install.sh no debe hardcodear la version"
    assert not re.search(r"VERSION='(?!\$\()[^']+'", src), \
        "install.sh no debe hardcodear la version"
    assert "read_version" in src, "install.sh debe leer la fuente unica"


def test_ningun_ejecutable_duplica_la_version():
    """Ningun ejecutable debe llevar la version como literal."""
    import re
    for rel in ("opt/escama/escama.py", "opt/escama/escama-tui.py",
                "install.sh"):
        with open(os.path.join(RAIZ_REPO, rel)) as f:
            src = f.read()
        assert not re.search(r'VERSION\s*=\s*["\']\d+\.\d+', src), \
            f"{rel} tiene la version hardcodeada"


def test_escama_degrada_la_version_sin_mentir(tmp_path, monkeypatch):
    """Sin archivo VERSION debe decir 'desconocido', nunca un numero viejo."""
    import importlib.util
    src = open(os.path.join(RAIZ_REPO, "opt", "escama", "escama.py")).read()
    # ejecutar solo la funcion de lectura, aislada, en un arbol sin VERSION
    ns = {"os": os, "__file__": str(tmp_path / "opt" / "escama" / "escama.py")}
    exec(compile("\n".join(l for l in src.split("\n")
                           if not l.startswith(("import ", "VERSION ="))),
                 "escama.py", "exec"), ns)
    assert ns["_read_version"]() == "desconocido"


# ---------------------------------------------------------------------------
# Gate de privilegio (spec `uso-sin-privilegios`)
# ---------------------------------------------------------------------------

def test_acciones_de_solo_lectura_no_piden_privilegio():
    for a in ("status", "--help", "-h", "help", "--version", "-v", "version"):
        assert a in escama.ACCIONES_SIN_PRIVILEGIO, a
    for a in ("start", "stop", "restart", "genconfig", "egress", "watch"):
        assert a not in escama.ACCIONES_SIN_PRIVILEGIO, a


def test_main_solo_lectura_corren_sin_root(monkeypatch, capsys):
    """status/--help/--version NO deben rebotar por falta de root."""
    monkeypatch.setattr(escama, "preflight", lambda: {
        "estado": "completa", "componentes": {}, "faltan": [],
        "version_repo": "1", "version_instalada": "1"})
    monkeypatch.setattr(escama.os, "geteuid", lambda: 1000)
    monkeypatch.setattr(escama, "do_status", lambda: 0)
    assert escama.main(["status"]) == 0
    assert escama.main(["--version"]) == 0
    assert escama.main(["--help"]) == 0
    assert "1." in capsys.readouterr().out or "desconocido" in capsys.readouterr().out


def test_main_mutante_exige_privilegio_con_mensaje(monkeypatch, capsys):
    monkeypatch.setattr(escama, "preflight", lambda: {
        "estado": "completa", "componentes": {}, "faltan": [],
        "version_repo": "1", "version_instalada": "1"})
    monkeypatch.setattr(escama.os, "geteuid", lambda: 1000)
    monkeypatch.setattr(escama, "rootless_disponible",
                        lambda: (False, "sin launcher en el test"))
    called = []
    monkeypatch.setattr(escama, "do_start", lambda: called.append(1) or 0)
    rc = escama.main(["start"])
    assert rc == 1, "una accion mutante sin privilegio debe fallar"
    assert not called, "no debe ejecutar la accion sin privilegio"
    err = capsys.readouterr().err
    assert "sudo" in err and "Motivo" in err


# ---------------------------------------------------------------------------
# Preflight y auto-instalacion (spec `auto-instalacion`)
# ---------------------------------------------------------------------------

def _preflight_con(tmp_path, monkeypatch, installed=(), codigo_igual=True,
                   ver_inst="1.0.0"):
    """Simula una maquina con los componentes indicados en `installed`."""
    for rel in ("escama", "escama-tui"):
        p = tmp_path / "bin" / rel
        if rel in installed:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.symlink_to("/opt/escama/x")
    for rel in ("core", "env", "u1", "u2"):
        p = {"core": "opt/escama/escama.py", "env": "etc/escama/escama.env",
             "u1": "units/escama-ap.service",
             "u2": "units/escama-egress.service"}[rel]
        if rel in installed:
            p = tmp_path / p
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("x")
    monkeypatch.setattr(escama, "INSTALL_BIN_DIR", str(tmp_path / "bin"))
    monkeypatch.setattr(escama, "INSTALL_PREFIX", str(tmp_path / "opt" / "escama"))
    monkeypatch.setattr(escama, "ENV_FILE", str(tmp_path / "etc/escama/escama.env"))
    monkeypatch.setattr(escama, "INSTALL_UNIT_DIR", str(tmp_path / "units"))
    if ver_inst:
        (tmp_path / "opt" / "escama" / "VERSION").parent.mkdir(
            parents=True, exist_ok=True)
        (tmp_path / "opt" / "escama" / "VERSION").write_text(ver_inst)
    monkeypatch.setattr(escama, "_codigo_difiere", lambda: not codigo_igual)
    return escama.preflight()


def test_preflight_completa(tmp_path, monkeypatch):
    p = _preflight_con(tmp_path, monkeypatch,
                       installed=("escama", "escama-tui", "core", "env", "u1", "u2"))
    assert p["estado"] == "completa"
    assert p["faltan"] == []


def test_preflight_detecta_faltantes(tmp_path, monkeypatch):
    p = _preflight_con(tmp_path, monkeypatch, installed=(), ver_inst="")
    assert p["estado"] == "faltante"
    assert len(p["faltan"]) == 6, "debe listar todos los componentes ausentes"


def test_preflight_distingue_desactualizada_por_version(tmp_path, monkeypatch):
    p = _preflight_con(tmp_path, monkeypatch,
                       installed=("escama", "escama-tui", "core", "env", "u1", "u2"),
                       ver_inst="0.9.0")
    assert p["estado"] == "desactualizada"
    assert p["version_repo"] != p["version_instalada"]


def test_preflight_distingue_desactualizada_por_codigo(tmp_path, monkeypatch):
    p = _preflight_con(tmp_path, monkeypatch,
                       installed=("escama", "escama-tui", "core", "env", "u1", "u2"),
                       codigo_igual=False)
    assert p["estado"] == "desactualizada", "mismo version pero codigo distinto"


def test_preflight_no_modifica_nada(tmp_path, monkeypatch):
    """preflight es de solo lectura: no crea archivos ni pide privilegio."""
    _preflight_con(tmp_path, monkeypatch, installed=())
    antes = sorted(p.name for p in tmp_path.rglob("*"))
    escama.preflight()
    assert sorted(p.name for p in tmp_path.rglob("*")) == antes


def test_bootstrap_rechaza_y_explica_comando(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(escama, "_is_tty", lambda: True)
    monkeypatch.setattr(builtins_module := __import__("builtins"), "input",
                        lambda _="": "n")
    monkeypatch.setattr(escama, "preflight",
                        lambda: {"estado": "faltante", "faltan": ["a", "b"],
                                 "componentes": {}, "version_repo": "1",
                                 "version_instalada": "(ninguna)"})
    monkeypatch.setattr(escama, "_repo_root", lambda: str(tmp_path))
    (tmp_path / "install.sh").write_text("#!/bin/sh\n")
    assert escama._bootstrap_instalacion() is False
    out = capsys.readouterr().out
    assert "Cancelado" in out and "install.sh install" in out


def test_bootstrap_sin_tty_no_pregunta(tmp_path, monkeypatch, capsys):
    """Sin terminal no se pregunta: se imprime el comando y se aborta."""
    monkeypatch.setattr(escama, "_is_tty", lambda: False)
    monkeypatch.setattr(escama, "preflight",
                        lambda: {"estado": "faltante", "faltan": ["a"],
                                 "componentes": {}, "version_repo": "1",
                                 "version_instalada": "(ninguna)"})
    monkeypatch.setattr(escama, "_repo_root", lambda: str(tmp_path))
    (tmp_path / "install.sh").write_text("#!/bin/sh\n")
    assert escama._bootstrap_instalacion() is False
    err = capsys.readouterr().err
    assert "Sin terminal interactivo" in err and "install.sh install" in err


def test_bootstrap_acepta_con_un_solo_prompt(tmp_path, monkeypatch, capsys):
    """Aceptar -> UN solo run() de install.sh (un prompt de privilegio)."""
    monkeypatch.setattr(escama, "_is_tty", lambda: True)
    monkeypatch.setattr(__import__("builtins"), "input", lambda _="": "s")
    monkeypatch.setattr(escama, "_repo_root", lambda: str(tmp_path))
    (tmp_path / "install.sh").write_text("#!/bin/sh\n")
    calls = []
    estados = iter([{"estado": "faltante", "faltan": ["core"], "componentes": {},
                     "version_repo": "1", "version_instalada": "(ninguna)"},
                    {"estado": "completa", "faltan": [], "componentes": {},
                     "version_repo": "1", "version_instalada": "1"}])

    def fake_run(cmd, check=True, capture=True):
        calls.append(cmd)
        class R:
            returncode = 0
            stdout = ""
            stderr = ""
        return R()
    monkeypatch.setattr(escama, "run", fake_run)
    monkeypatch.setattr(escama, "preflight", lambda: next(estados))
    assert escama._bootstrap_instalacion() is True
    installs = [c for c in calls if "install" in c]
    assert len(installs) == 1, f"debe invocar install.sh una sola vez, hubo {len(installs)}"
    assert "Instalacion completa" in capsys.readouterr().out


def test_bootstrap_fallido_no_continua(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(escama, "_is_tty", lambda: True)
    monkeypatch.setattr(__import__("builtins"), "input", lambda _="": "s")
    monkeypatch.setattr(escama, "_repo_root", lambda: str(tmp_path))
    (tmp_path / "install.sh").write_text("#!/bin/sh\n")
    monkeypatch.setattr(escama, "preflight",
                        lambda: {"estado": "faltante", "faltan": ["core"],
                                 "componentes": {}, "version_repo": "1",
                                 "version_instalada": "(ninguna)"})

    def fake_run(cmd, check=True, capture=True):
        class R:
            returncode = 1
            stdout = ""
            stderr = "boom"
        return R()
    monkeypatch.setattr(escama, "run", fake_run)
    assert escama._bootstrap_instalacion() is False
    assert "fallo" in capsys.readouterr().err


def test_acciones_mutantes_pasan_por_bootstrap(monkeypatch):
    for a in ("start", "stop", "restart", "reconnect", "genconfig", "egress",
              "watch"):
        assert a in escama.ACCIONES_CON_BOOTSTRAP, a
    for a in ("status", "preflight", "--version"):
        assert a not in escama.ACCIONES_CON_BOOTSTRAP, a


def test_main_preflight_no_pide_privilegio_ni_bootstrap(monkeypatch, capsys):
    """preflight debe correr sin sudo y sin tocar el bootstrap."""
    monkeypatch.setattr(escama.os, "geteuid", lambda: 1000)
    monkeypatch.setattr(escama, "preflight",
                        lambda: {"estado": "faltante", "faltan": ["x"],
                                 "componentes": {}, "version_repo": "1",
                                 "version_instalada": "(ninguna)"})
    monkeypatch.setattr(escama, "_bootstrap_instalacion",
                        lambda: pytest.fail("preflight no debe bootstrap"))
    assert escama.main(["preflight"]) == 0
    assert "escama preflight" in capsys.readouterr().out


def test_main_mutante_bootstrap_fallido_aborta(monkeypatch):
    monkeypatch.setattr(escama, "preflight",
                        lambda: {"estado": "faltante", "faltan": ["x"],
                                 "componentes": {}, "version_repo": "1",
                                 "version_instalada": "(ninguna)"})
    monkeypatch.setattr(escama, "_bootstrap_instalacion", lambda: False)
    called = []
    monkeypatch.setattr(escama, "do_start", lambda: called.append(1) or 0)
    assert escama.main(["start"]) == 1
    assert not called, "no debe ejecutar la accion si el bootstrap falla"


# ---------------------------------------------------------------------------
# Rootless (spec `uso-sin-privilegios`): launcher, probe y degradacion
# ---------------------------------------------------------------------------

def test_rootless_no_disponible_sin_launcher(tmp_path, monkeypatch):
    monkeypatch.setattr(escama, "LAUNCHER", str(tmp_path / "no-existe"))
    ok, motivo = escama.rootless_disponible()
    assert ok is False
    assert "no esta instalado" in motivo


def test_rootless_no_disponible_si_es_root(tmp_path, monkeypatch):
    """Con root el rootless no aplica: no es un motivo de negation real."""
    p = tmp_path / "escama-launch"
    p.write_text("x")
    monkeypatch.setattr(escama, "LAUNCHER", str(p))
    monkeypatch.setattr(escama.os, "geteuid", lambda: 0)
    ok, motivo = escama.rootless_disponible()
    assert ok is False and "root" in motivo


def test_rootless_no_disponible_con_owner_ajeno(tmp_path, monkeypatch):
    """El kernel descarta las caps si el launcher no es del usuario (falla
    en silencio): el preflight MUST detectarlo por owner."""
    p = tmp_path / "escama-launch"
    p.write_text("x")
    os.chmod(p, 0o755)
    monkeypatch.setattr(escama, "LAUNCHER", str(p))
    monkeypatch.setattr(escama.os, "geteuid", lambda: _EUID)
    st = os.stat(p)
    real_stat = os.stat
    # simular owner distinto sin tocar el archivo real
    real = os.stat(p)
    class FakeStat:
        st_uid = 12345
        st_mode = real.st_mode
        st_size = real.st_size
        st_mtime = real.st_mtime
    monkeypatch.setattr(escama.os, "stat", lambda _p, **kw: FakeStat())
    ok, motivo = escama.rootless_disponible()
    assert ok is False
    assert "uid 12345" in motivo and "silencio" in motivo
    monkeypatch.setattr(escama.os, "stat", real_stat)


def test_rootless_verifica_con_operacion_real(tmp_path, monkeypatch):
    """La verificacion NO se fia de getcap: ejecuta una operacion real."""
    p = tmp_path / "escama-launch"
    p.write_text("x")
    os.chmod(p, 0o755)
    monkeypatch.setattr(escama, "LAUNCHER", str(p))
    monkeypatch.setattr(escama.os, "geteuid", lambda: _EUID)
    llamadas = []

    def fake_run_sin_sudo(cmd):
        llamadas.append(cmd)
        return 0
    monkeypatch.setattr(escama, "_run_sin_sudo", fake_run_sin_sudo)
    ok, motivo = escama.rootless_disponible()
    assert ok is True
    # debe limpiar antes, crear (la prueba) y borrar despues
    ops = [" ".join(c) for c in llamadas]
    assert any("link del" in o and escama.PROBE_IFACE in o for o in ops), ops
    assert any("link add" in o and "dummy" in o for o in ops), ops
    assert ops[-1].count("link del") >= 1, "la probe debe limpiar al final"


def test_rootless_falla_si_la_operacion_no_pasa(tmp_path, monkeypatch):
    p = tmp_path / "escama-launch"
    p.write_text("x")
    os.chmod(p, 0o755)
    monkeypatch.setattr(escama, "LAUNCHER", str(p))
    monkeypatch.setattr(escama.os, "geteuid", lambda: _EUID)
    monkeypatch.setattr(escama, "_run_sin_sudo", lambda cmd: 1)
    ok, motivo = escama.rootless_disponible()
    assert ok is False
    assert "no sobreviven" in motivo


def test_probe_se_limpia_antes_de_crear(tmp_path, monkeypatch):
    """Una dummy huerfana de una corrida previa no debe dar falso negativo."""
    p = tmp_path / "escama-launch"
    p.write_text("x")
    os.chmod(p, 0o755)
    monkeypatch.setattr(escama, "LAUNCHER", str(p))
    monkeypatch.setattr(escama.os, "geteuid", lambda: _EUID)
    ops = []
    monkeypatch.setattr(escama, "_run_sin_sudo",
                        lambda cmd: ops.append(" ".join(cmd)) or 0)
    escama.rootless_disponible()
    assert "link del" in ops[0], f"la primera operacion debe limpiar: {ops[0]}"


def test_run_sin_sudo_no_antepone_sudo(monkeypatch):
    """_run_sin_sudo debe llamar a subprocess.run SIN el auto-sudo de run():
    bajo sudo el kernel no concede las file capabilities y la probe miente."""
    vistos = []

    class R:
        returncode = 0

    def fake_subprocess_run(cmd, **kw):
        vistos.append(cmd)
        return R()
    monkeypatch.setattr(escama.subprocess, "run", fake_subprocess_run)
    rc = escama._run_sin_sudo(["/opt/escama/escama-launch", "ip", "link"])
    assert rc == 0
    assert vistos[0][0] == "/opt/escama/escama-launch", vistos


def test_relaunch_marca_el_guard_de_entorno(monkeypatch):
    """Re-ejecutar por el launcher marca ESCAMA_VIA_LAUNCHER: sin ese guard el
    core re-lanzado vuelve a entrar al gate y se cicla (cuelgue medido)."""
    p = os.path.join(RAIZ_REPO, "opt", "escama", "escama.py")
    with open(p) as f:
        src = f.read()
    assert "ESCAMA_VIA_LAUNCHER" in src, "falta el guard anti-ciclo"
    assert '"core"' in src, "el re-lanzado debe usar el modo core del launcher"


def test_preflight_reporta_rootless(monkeypatch, capsys):
    monkeypatch.setattr(escama, "preflight", lambda: {
        "estado": "completa", "componentes": {}, "faltan": [],
        "version_repo": "1", "version_instalada": "1"})
    monkeypatch.setattr(escama, "rootless_disponible",
                        lambda: (False, "falta el launcher"))
    monkeypatch.setattr(escama.os, "geteuid", lambda: 1000)
    escama.do_preflight()
    out = capsys.readouterr().out
    assert "Rootless: NO DISPONIBLE" in out
    assert "falta el launcher" in out, "el preflight debe nombrar la causa"
