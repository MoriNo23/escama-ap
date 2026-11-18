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

    def fake_run(cmd, capture=True, **_kw):
        calls.append(cmd)
        # default: simulate success
        class R:
            returncode = 0
            stdout = ""
            stderr = ""
        return R()

    monkeypatch.setattr(escama, "run", fake_run)
    return calls


@pytest.fixture(autouse=True)
def _prohibido_tocar_el_sistema(monkeypatch):
    """Red de seguridad: ningun test puede ejecutar un comando de verdad.

    Contrato declarado en AGENTS.md ("los tests mockean run/subprocess/os => NO
    tocan stonepi/wn8200nd"). Se cumplia a mano y un test se filtro: mutmut
    levanto el AP real sobre wn8200nd (la interfaz del usuario) con los DEFAULTS
    del env. Este fixture convierte esa fuga silenciosa en un fallo con
    traceback, que es la unica forma de que no vuelva a pasar.
    """
    import subprocess

    real = subprocess.run

    def guardia(*a, **k):
        cmd = a[0] if a else k.get("args")
        raise AssertionError(
            "un test intento ejecutar un comando REAL: {!r}. "
            "Mockea run()/subprocess (ver AGENTS.md).".format(cmd))

    monkeypatch.setattr(subprocess, "run", guardia)
    monkeypatch.setattr(subprocess, "Popen", guardia)
    yield
    monkeypatch.setattr(subprocess, "run", real)


def test_load_env_defaults():
    assert escama.DEFAULTS["AP_IFACE"] == "wn8200nd"
    assert escama.DEFAULTS["WAN_IFACE"] == "stonepi"


def test_load_env_from_file(tmp_path, monkeypatch):
    env = tmp_path / "escama.env"
    env.write_text('SSID="mired"\nCHANNEL="11"\nWAN_IFACE=""\n')
    monkeypatch.setattr(escama, "CONFIG_FILE", str(env))
    cfg = escama.load_env()
    assert cfg["SSID"] == "mired"
    assert cfg["CHANNEL"] == "11"
    assert cfg["WAN_IFACE"] == ""  # empty preserved
    assert cfg["AP_IFACE"] == "wn8200nd"  # default kept


def test_generate_configs_from_env(tmp_path, monkeypatch):
    env = tmp_path / "escama.env"
    env.write_text('AP_IFACE="wlan9"\nSSID="testap"\nCHANNEL="3"\nWPA_PASSPHRASE="pass1234"\nAP_IP="10.0.0.1"\nAP_CIDR="24"\nAP_SUBNET="10.0.0.0/24"\nDHCP_START="10.0.0.10"\nDHCP_END="10.0.0.50"\nDHCP_LEASE="1h"\nDNS1="1.1.1.1"\nDNS2="9.9.9.9"\n')
    monkeypatch.setattr(escama, "CONFIG_FILE", str(env))
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

    def fake_run(cmd, capture=True, **_kw):
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
    def fake_run(cmd, capture=True, **_kw):
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

    def fake_run(cmd, capture=True, **_kw):
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
    monkeypatch.setattr(escama, "_driver_de", lambda a: "8192eu")
    escama.reload_module_if_needed("wn8200nd")
    assert any(c[:1] == ["rmmod"] for c in calls), "should rmmod when AP mode missing"
    assert any(c[:1] == ["modprobe"] for c in calls), "should modprobe after rmmod"


def test_ap_mode_present_no_reload(monkeypatch):
    calls = []
    def fake_run(cmd, capture=True, **_kw):
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
    def fake_run(cmd, capture=True, **_kw):
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
    def fake_run(cmd, capture=True, **_kw):
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
    """do_stop must remove AP IP, set NM managed=yes, kill procs, and NOT force
    the global ip_forward to 0 (LXC/libvirt share that sysctl): without IPFWD
    in the state, do_stop must not touch it at all."""
    calls = []
    def fake_run(cmd, capture=True, **_kw):
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
    monkeypatch.setattr(escama, "_read_state", lambda: {})
    rc = escama.do_stop()
    assert rc == 0
    # NM managed yes on AP iface
    assert any(c[:3] == ["nmcli", "device", "set"] and "managed" in c and "yes" in c
               for c in calls), "do_stop must restore NM managed=yes"
    # ip_forward: solo se restaura si el state lo guarda (nunca a 0 por decreto)
    assert not any("ip_forward" in " ".join(c) for c in calls), (
        "sin IPFWD en el state, do_stop NO debe tocar el ip_forward global")
    # masquerade deleted for WAN iface
    assert any(c[:3] == ["iptables", "-t", "nat"] and "stonepi" in c for c in calls)


def test_do_stop_restaura_ip_forward_del_state(monkeypatch):
    """El ip_forward previo guardado por apply_egress (IPFWD) se restaura al
    stop: escama comparte ese sysctl con el host (LXC/libvirt NAT)."""
    calls = []
    def fake_run(cmd, capture=True, **_kw):
        calls.append(cmd)
        class R:
            returncode = 0
            stdout = ""
            stderr = ""
        return R()
    monkeypatch.setattr(escama, "run", fake_run)
    monkeypatch.setattr(escama, "_kill_procs", lambda: None)
    monkeypatch.setattr(escama, "load_env", lambda: {
        "AP_IFACE": "wn8200nd", "WAN_IFACE": "stonepi", "AP_IP": "10.42.1.1",
        "AP_CIDR": "24", "AP_SUBNET": "10.42.1.0/24"})
    monkeypatch.setattr(escama, "_read_state", lambda: {"IPFWD": "1"})
    escama.do_stop()
    assert any(c == ["sysctl", "-w", "net.ipv4.ip_forward=1"] for c in calls)
    calls.clear()
    monkeypatch.setattr(escama, "_read_state", lambda: {"IPFWD": "0"})
    escama.do_stop()
    assert any(c == ["sysctl", "-w", "net.ipv4.ip_forward=0"] for c in calls)


def test_wan_has_internet_true(monkeypatch):
    def fake_run(cmd, capture=True, **_kw):
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
    def fake_run(cmd, capture=True, **_kw):
        class R:
            returncode = 1  # ping fails
            stdout = "default via 192.168.1.1 dev stonepi\n" if cmd[:2] == ["ip", "route"] else ""
            stderr = ""
        return R()
    monkeypatch.setattr(escama, "run", fake_run)
    assert escama.wan_has_internet("stonepi") is False


def test_do_status_runs(monkeypatch, capsys):
    def fake_run(cmd, capture=True, **_kw):
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


def test_load_env_toml(tmp_path, monkeypatch):
    """load_env parsea TOML real: comentarios, espacios, comillas y tipos."""
    env = tmp_path / "escama.toml"
    env.write_text(
        "# comment line\n"
        "\n"
        'AP_IFACE = "wlan5"\n'          # espacios alrededor de =
        "CHANNEL = 11\n"                # int -> str
        "VPN_MSS_CLAMP = true\n"        # bool -> str
        'SSID = "my ssid"\n'
        'CLAVE_AJENA = "x"\n'           # clave desconocida: se conserva
    )
    monkeypatch.setattr(escama, "CONFIG_FILE", str(env))
    cfg = escama.load_env()
    assert cfg["AP_IFACE"] == "wlan5"
    assert cfg["CHANNEL"] == "11", "int de TOML se coacciona a str"
    assert escama._yes(cfg["VPN_MSS_CLAMP"]), "bool de TOML sigue parseando como yes"
    assert cfg["SSID"] == "my ssid"
    assert cfg["CLAVE_AJENA"] == "x"
    # defaults preserved for keys not in file
    assert cfg["AP_IP"] == "10.42.1.1"


def test_load_env_toml_invalido_aborta(tmp_path, monkeypatch):
    """Fail-closed: un TOML con error de sintaxis aborta con motivo. El parser
    viejo saltaba lineas rotas en silencio: media config aplicada es peor que
    ninguna."""
    env = tmp_path / "escama.toml"
    env.write_text('AP_IFACE="a"\nSSID="sin cerrar\n')
    monkeypatch.setattr(escama, "CONFIG_FILE", str(env))
    with pytest.raises(SystemExit):
        escama.load_env()


def test_load_env_overrides_defaults(tmp_path, monkeypatch):
    env = tmp_path / "escama.env"
    env.write_text('AP_IFACE="custom"\nWAN_IFACE="wlan9"\n')
    monkeypatch.setattr(escama, "CONFIG_FILE", str(env))
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

    def fake_run(cmd, capture=True, **_kw):
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


def test_detect_wan_iface_detecta_usb_wifi_wlx(monkeypatch):
    # Los dongles USB (p. ej. AIC8800D80) se llaman wlx<MAC>: el nombre no es
    # filtro; la deteccion es por ruta default, por tipo de iface.
    monkeypatch.setattr(
        escama, "iface_exists", lambda i: i in ("stonepi", "wlx020304050607")
    )
    monkeypatch.setattr(escama, "iface_is_tunnel", lambda i: False)
    monkeypatch.setattr(escama, "detect_ap_iface", lambda c: "stonepi")

    def fake_run(cmd, capture=True, **_kw):
        class R:
            returncode = 0
            stdout = "default via 192.168.1.1 dev wlx020304050607 metric 600\n"
            stderr = ""

        return R()

    monkeypatch.setattr(escama, "run", fake_run)
    cfg = dict(escama.DEFAULTS, AP_IFACE="stonepi", WAN_IFACE="wn8200nd")
    assert escama.detect_wan_iface(cfg) == "wlx020304050607"


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

    def fake_run(cmd, capture=True, **_kw):
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

    def fake_run(cmd, capture=True, **_kw):
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

    def fake_run(cmd, capture=True, **_kw):
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

    def fake_run(cmd, capture=True, **_kw):
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

    def fake_run(cmd, capture=True, **_kw):
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
    def fake_run(cmd, capture=True, **_kw):
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

    def rc_fail(cmd, capture=True, **_kw):
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
    def fake_run(cmd, capture=True, **_kw):
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

    def fake_run(cmd, capture=True, **_kw):
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

    def fake_run(cmd, capture=True, **_kw):
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
    monkeypatch.setattr(escama, "iface_exists",
                        lambda x: x in ("stonepi", "proton0"))
    monkeypatch.setattr(escama, "detect_vpn_iface", lambda c: "proton0")
    monkeypatch.setattr(escama, "apply_egress", lambda c, e, k: None)
    monkeypatch.setattr(escama, "run", lambda *a, **k: type(
        "R", (), {"returncode": 0, "stdout": "", "stderr": ""})())
    rc = escama.do_egress([])
    assert rc == 0
    assert ha.read_text() == "channel=1\n"
    assert (tmp_path / "dnsmasq.conf").exists()


def _egress_banco(monkeypatch, tmp_path, wan_cfg, existe, detectada):
    """Banco de egress: config con WAN_IFACE=wan_cfg, sysfs simulado con
    `existe`, deteccion de WAN que devuelve `detectada`. Devuelve la lista
    de (egress, kind) aplicados."""
    monkeypatch.setattr(escama, "HOSTAPD_CONF", str(tmp_path / "hostapd.conf"))
    monkeypatch.setattr(escama, "DNSMASQ_CONF", str(tmp_path / "dnsmasq.conf"))
    monkeypatch.setattr(escama, "STATE_FILE", str(tmp_path / "state"))
    monkeypatch.setattr(escama, "load_env", lambda: dict(
        escama.DEFAULTS, AP_IFACE="stonepi", WAN_IFACE=wan_cfg))
    monkeypatch.setattr(escama, "iface_exists", lambda x: x in existe)
    monkeypatch.setattr(escama, "detect_vpn_iface", lambda c: "")
    monkeypatch.setattr(escama, "detect_wan_iface", lambda c: detectada)
    aplicado = []
    monkeypatch.setattr(escama, "apply_egress",
                        lambda c, e, k: aplicado.append((e, k)))
    monkeypatch.setattr(escama, "run", lambda *a, **k: type(
        "R", (), {"returncode": 0, "stdout": "", "stderr": ""})())
    return aplicado


def test_do_egress_detecta_wan_si_la_configurada_no_existe(monkeypatch, tmp_path):
    """WAN_IFACE apunta a un dongle desenchufado: egress detecta la WAN real
    (mismo criterio que do_start) en vez de aplicar NAT a la iface muerta.
    Caso real: start detecto WU900, config seguia con wn8200nd ausente."""
    aplicado = _egress_banco(
        monkeypatch, tmp_path, wan_cfg="wn8200nd",
        existe=("stonepi", "WU900"), detectada="WU900")
    rc = escama.do_egress([])
    assert rc == 0
    assert aplicado == [("WU900", "wan")], "aplica la WAN detectada, no la muerta"


def test_do_egress_no_aplica_a_iface_muerta(monkeypatch, tmp_path):
    """WAN configurada ausente y deteccion vacia: fail-closed (flush), rc 1;
    nunca aplica NAT a una iface que no existe."""
    aplicado = _egress_banco(
        monkeypatch, tmp_path, wan_cfg="wn8200nd",
        existe=("stonepi",), detectada="")
    rc = escama.do_egress([])
    assert rc == 1
    assert aplicado == [("", "none")], "fail-closed, sin reglas a iface muerta"


def test_do_egress_wan_configurada_existente_se_respeta(monkeypatch, tmp_path):
    """WAN_IFACE existe: el env gana, no hay re-deteccion (sin sorpresas)."""
    aplicado = _egress_banco(
        monkeypatch, tmp_path, wan_cfg="wn8200nd",
        existe=("stonepi", "wn8200nd"), detectada="otra")
    rc = escama.do_egress([])
    assert rc == 0
    assert aplicado == [("wn8200nd", "wan")], "env explicito y existente gana"


# ---------------------------------------------------------------------------
# Versionado (spec `versionado`): fuente única + coherencia entre las piezas
# ---------------------------------------------------------------------------

def _raiz_de_repo() -> str:
    """Raiz del repo real, subiendo hasta encontrar VERSION + el core.

    No se puede asumir `dirname(__file__)/..`: mutmut copia la suite a
    `mutants/tests/`, y ahi `..` es `mutants/`, que no tiene VERSION. Se
    distingue la raiz de verdad porque es el unico directorio que tiene a la vez
    el archivo VERSION y opt/escama/escama.py.
    """
    d = os.path.dirname(os.path.abspath(__file__))
    for _ in range(5):
        if (os.path.isfile(os.path.join(d, "VERSION"))
                and os.path.isfile(os.path.join(d, "opt", "escama", "escama.py"))):
            return d
        padre = os.path.dirname(d)
        if padre == d:
            break
        d = padre
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


RAIZ_REPO = _raiz_de_repo()
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
    out = capsys.readouterr().out
    assert "escama " in out, "--version debe imprimir la version (sea cual sea), sin pedir root"


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
                   ver_inst=None):
    """Simula una maquina con los componentes indicados en `installed`.

    `ver_inst` por defecto es la version real del repo: si se hardcodea un
    numero, el test deja de validar nada en cuanto se hace un bump.
    """
    if ver_inst is None:
        ver_inst = open(os.path.join(RAIZ_REPO, "VERSION")).read().strip()
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
    monkeypatch.setattr(escama, "CONFIG_FILE", str(tmp_path / "etc/escama/escama.env"))
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

    def fake_run(cmd, capture=True, **_kw):
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

    def fake_run(cmd, capture=True, **_kw):
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
    # rootless_disponible() ejecuta una sonda REAL (crea/borra una iface
    # dummy): en un test va siempre mockeada. Aca se mockea aparte porque
    # este test llama al do_preflight real, no a preflight().
    monkeypatch.setattr(escama, "rootless_disponible",
                        lambda: (False, "sin launcher en el test"))
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


# ---------------------------------------------------------------------------
# Fix: run() no debe escalar cuando ya hay capabilities del launcher
# (el rootless volvia a pedir sudo por comando)
# ---------------------------------------------------------------------------

def test_run_no_antepone_sudo_con_caps_del_launcher(monkeypatch):
    """Con capabilities (guard activo) NO debe anteponer sudo: el modo
    rootless existe justamente para no pedir password."""
    monkeypatch.setattr(escama.os, "geteuid", lambda: 1000)
    monkeypatch.setenv("ESCAMA_VIA_LAUNCHER", "1")
    vistos = []

    def fake_subprocess_run(cmd, **kw):
        vistos.append(cmd)
        class R:
            returncode = 0
            stdout = ""
            stderr = ""
        return R()
    monkeypatch.setattr(escama.subprocess, "run", fake_subprocess_run)
    escama.run(["ip", "link", "show"])
    assert vistos[0] == ["ip", "link", "show"], \
        f"no debe anteponer sudo bajo el launcher: {vistos[0]}"


def test_run_si_antepone_sudo_sin_caps_ni_root(monkeypatch):
    """Sin root y SIN capabilities, escalar es lo correcto (fallback)."""
    monkeypatch.setattr(escama.os, "geteuid", lambda: 1000)
    monkeypatch.delenv("ESCAMA_VIA_LAUNCHER", raising=False)
    vistos = []

    def fake_subprocess_run(cmd, **kw):
        vistos.append(cmd)
        class R:
            returncode = 0
            stdout = ""
            stderr = ""
        return R()
    monkeypatch.setattr(escama.subprocess, "run", fake_subprocess_run)
    escama.run(["ip", "link", "show"])
    assert vistos[0] == ["sudo", "ip", "link", "show"]


def test_run_no_escala_si_ya_es_root(monkeypatch):
    monkeypatch.setattr(escama.os, "geteuid", lambda: 0)
    monkeypatch.delenv("ESCAMA_VIA_LAUNCHER", raising=False)
    vistos = []

    def fake_subprocess_run(cmd, **kw):
        vistos.append(cmd)
        class R:
            returncode = 0
            stdout = ""
            stderr = ""
        return R()
    monkeypatch.setattr(escama.subprocess, "run", fake_subprocess_run)
    escama.run(["ip", "link", "show"])
    assert vistos[0] == ["ip", "link", "show"]


def test_tiene_caps_detecta_el_guard():
    import os as _os
    previo = _os.environ.get("ESCAMA_VIA_LAUNCHER")
    try:
        _os.environ.pop("ESCAMA_VIA_LAUNCHER", None)
        assert escama._tiene_caps_del_launcher() is False
        _os.environ["ESCAMA_VIA_LAUNCHER"] = "1"
        assert escama._tiene_caps_del_launcher() is True
        _os.environ["ESCAMA_VIA_LAUNCHER"] = "0"
        assert escama._tiene_caps_del_launcher() is False
    finally:
        if previo is None:
            _os.environ.pop("ESCAMA_VIA_LAUNCHER", None)
        else:
            _os.environ["ESCAMA_VIA_LAUNCHER"] = previo


def test_probe_y_run_no_divergen_sobre_escalar(monkeypatch):
    """La probe (rootless_disponible) corre en un proceso SIN caps: debe usar
    _run_sin_sudo, nunca run(), que si escalaria y haria la prueba mentir."""
    assert "run(" not in __import__("inspect").getsource(escama.rootless_disponible)
    assert "_run_sin_sudo" in __import__("inspect").getsource(escama.rootless_disponible)


def test_degradacion_nombra_el_motivo_real(monkeypatch, tmp_path, capsys):
    """Si el launcher no sirve, el mensaje dice el motivo y da la salida, no
    un FileNotFoundError de subcomando arbitrario."""
    monkeypatch.setattr(escama, "preflight", lambda: {
        "estado": "completa", "componentes": {}, "faltan": [],
        "version_repo": "1", "version_instalada": "1"})
    monkeypatch.setattr(escama.os, "geteuid", lambda: 1000)
    monkeypatch.delenv("ESCAMA_VIA_LAUNCHER", raising=False)
    monkeypatch.setattr(escama, "rootless_disponible",
                        lambda: (False, "el launcher es de uid 0 y no tuyo"))
    rc = escama.main(["start"])
    assert rc == 1
    err = capsys.readouterr().err
    assert "uid 0 y no tuyo" in err, "debe nombrar el motivo real"
    assert "sudo escama start" in err, "debe dar la salida exacta"


# ---------------------------------------------------------------------------
# Rutas de runtime (spec `uso-sin-privilegios`, design D3): XDG sin root
# ---------------------------------------------------------------------------

def test_log_usa_xdg_sin_root(monkeypatch, tmp_path):
    """Sin root el log va a XDG_STATE_HOME, no a /var/log."""
    monkeypatch.setattr(escama.os, "geteuid", lambda: 1000)
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))
    p = escama._log_path()
    assert p.startswith(str(tmp_path / "state")), p
    assert "escama-ap.log" in p
    assert (tmp_path / "state" / "escama").is_dir(), "debe crear el directorio"


def test_log_usa_var_log_con_root(monkeypatch):
    """Con root se conservan las rutas de sistema (compatibilidad)."""
    monkeypatch.setattr(escama.os, "geteuid", lambda: 0)
    assert escama._log_path() == "/var/log/escama-ap.log"


def test_lease_usa_var_lib_misc_con_root(monkeypatch):
    monkeypatch.setattr(escama.os, "geteuid", lambda: 0)
    assert escama._lease_path() == "/var/lib/misc/dnsmasq-escama.leases"


def test_lease_cae_a_runtime_sin_root(monkeypatch, tmp_path):
    """dnsmasq escribe el leasefile: sin root no puede usar /var/lib/misc."""
    monkeypatch.setattr(escama.os, "geteuid", lambda: 1000)
    monkeypatch.setenv("XDG_RUNTIME_DIR", str(tmp_path / "run"))
    p = escama._lease_path()
    assert p.startswith(str(tmp_path / "run")), p
    assert (tmp_path / "run").is_dir()


def test_runtime_dir_usa_xdg_runtime_sin_root(monkeypatch, tmp_path):
    monkeypatch.setattr(escama.os, "geteuid", lambda: 1000)
    monkeypatch.setenv("XDG_RUNTIME_DIR", str(tmp_path / "run"))
    assert escama._runtime_dir() == str(tmp_path / "run")


def test_runtime_dir_con_root_usa_run(monkeypatch):
    monkeypatch.setattr(escama.os, "geteuid", lambda: 0)
    assert escama._runtime_dir() == "/run"


def test_runtime_dir_cae_a_tmp_si_no_puede_crear(monkeypatch, tmp_path):
    """Si el dir XDG no es escribible, cae a /tmp en vez de romper el arranque."""
    monkeypatch.setattr(escama.os, "geteuid", lambda: 1000)
    monkeypatch.setenv("XDG_RUNTIME_DIR", "/proc/no-escribible/x")
    d = escama._runtime_dir()
    assert d.startswith("/tmp"), d


def test_status_muestra_la_ruta_efectiva(monkeypatch, capsys, tmp_path):
    """status expone la ruta real: sin esto no se distingue 'no arranco' de
    'no tengo permiso'."""
    monkeypatch.setattr(escama, "load_env", lambda: {
        "AP_IFACE": "wn8200nd", "WAN_IFACE": "stonepi", "SSID": "escama",
        "AP_IP": "10.42.1.1", "AP_CIDR": "24"})
    monkeypatch.setattr(escama, "resolve_egress", lambda c: ("stonepi", "wan"))
    monkeypatch.setattr(escama, "_read_state", lambda: {})
    monkeypatch.setattr(escama, "list_tunnels", lambda: [])
    monkeypatch.setattr(escama, "run", lambda *a, **k: type(
        "R", (), {"returncode": 0, "stdout": "", "stderr": ""})())
    monkeypatch.setattr(escama, "LOG", str(tmp_path / "log.txt"))
    monkeypatch.setattr(escama, "PIDFILE", str(tmp_path / "pid"))
    escama.do_status()
    out = capsys.readouterr().out
    assert "Log:" in out and "Pidfile:" in out
    assert str(tmp_path / "log.txt") in out
    assert "Modo:" in out


def test_kill_procs_no_aborta_si_el_pidfile_no_se_borra(monkeypatch, tmp_path):
    """Con rootless el pidfile es del usuario; si el borrado falla (permisos),
    stop no debe abortar con PermissionError."""
    pid = tmp_path / "pid"
    pid.write_text("123")
    monkeypatch.setattr(escama, "PIDFILE", str(pid))
    monkeypatch.setattr(escama, "run", lambda *a, **k: None)
    monkeypatch.setattr(escama.time, "sleep", lambda s: None)

    def boom(_p):
        raise PermissionError("denegado")
    monkeypatch.setattr(escama.os, "remove", boom)
    escama._kill_procs()  # no debe lanzar


# ---------------------------------------------------------------------------
# Degradacion explicita (spec `uso-sin-privilegios`): rmmod/modprobe y nmcli
# no se omiten en silencio ni se reportan como exitosos
# ---------------------------------------------------------------------------

def _fake_run(monkeypatch, fallan=(), ok=()):
    """fake_run donde los comandos de `fallan` devuelven rc!=0 con stderr."""
    calls = []

    def fake_run(cmd, capture=True, **_kw):
        calls.append(cmd)
        nombre = " ".join(cmd[:2]) if len(cmd) > 1 else cmd[0]
        if nombre in fallan or (nombre, " ".join(cmd)) in fallan:
            class R:
                returncode = 1
                stdout = ""
                stderr = "Operation not permitted"
            return R()
        class R:
            returncode = 0
            stdout = ""
            stderr = ""
        return R()
    monkeypatch.setattr(escama, "run", fake_run)
    return calls


def test_rmmod_fallido_se_reporta_con_motivo(monkeypatch, tmp_path, capsys):
    """Sin CAP_SYS_MODULE el reload no se puede hacer: se DEBE decir, con el
    motivo real, no seguir en silencio."""
    monkeypatch.setattr(escama, "iface_exists", lambda x: True)
    monkeypatch.setattr(escama, "_ap_phy", lambda: "phy0")
    monkeypatch.setattr(escama, "_driver_de", lambda a: "8192eu")
    _fake_run(monkeypatch, fallan=("rmmod 8192eu",))
    monkeypatch.setattr(escama.time, "sleep", lambda s: None)
    escama.reload_module_if_needed("wn8200nd")
    out = capsys.readouterr().out
    assert "DEGRADADO" in out, "no debe omitir el fallo en silencio"
    assert "rmmod" in out, "debe nombrar el comando que fallo"
    assert "CAP_SYS_MODULE" in out, "debe explicar por que"


def test_modprobe_fallido_se_reporta(monkeypatch, capsys):
    monkeypatch.setattr(escama, "iface_exists", lambda x: True)
    monkeypatch.setattr(escama, "_ap_phy", lambda: "phy0")
    monkeypatch.setattr(escama, "_driver_de", lambda a: "8192eu")
    _fake_run(monkeypatch, fallan=("modprobe 8192eu",))
    monkeypatch.setattr(escama.time, "sleep", lambda s: None)
    escama.reload_module_if_needed("wn8200nd")
    out = capsys.readouterr().out
    assert "DEGRADADO" in out and "modprobe" in out


def test_reload_exitoso_no_inventa_degradacion(monkeypatch, capsys):
    """Si todo va bien, no debe decir DEGRADADO."""
    monkeypatch.setattr(escama, "iface_exists", lambda x: True)
    monkeypatch.setattr(escama, "_ap_phy", lambda: "phy0")
    monkeypatch.setattr(escama, "_driver_de", lambda a: "8192eu")
    _fake_run(monkeypatch)
    monkeypatch.setattr(escama.time, "sleep", lambda s: None)
    escama.reload_module_if_needed("wn8200nd")
    out = capsys.readouterr().out
    assert "DEGRADADO" not in out
    assert "recargado" in out


def test_reload_no_hace_nada_si_el_modo_ap_ya_esta(monkeypatch):
    """Si '* AP' esta presente, no toca nada (no es un fallo)."""
    monkeypatch.setattr(escama, "iface_exists", lambda x: True)
    monkeypatch.setattr(escama, "_ap_phy", lambda: "phy0")
    calls = []

    def fake_run(cmd, capture=True, **_kw):
        calls.append(cmd)
        class R:
            returncode = 0
            stdout = "* managed\n* AP\n"
            stderr = ""
        return R()
    monkeypatch.setattr(escama, "run", fake_run)
    escama.reload_module_if_needed("wn8200nd")
    assert not any(c[:1] == ["rmmod"] for c in calls)


def test_nmcli_managed_no_fallido_se_reporta(monkeypatch, tmp_path, capsys):
    """Si polkit no autoriza, se informa con el motivo y se dice si impide el
    arranque. Antes se ignoraba el resultado en silencio."""
    monkeypatch.setattr(escama, "preflight", lambda: {
        "estado": "completa", "componentes": {}, "faltan": [],
        "version_repo": "1", "version_instalada": "1"})
    monkeypatch.setattr(escama, "iface_exists", lambda x: True)
    monkeypatch.setattr(escama, "_ap_phy", lambda: "phy0")
    monkeypatch.setattr(escama, "load_env", lambda: {
        "AP_IFACE": "wn8200nd", "WAN_IFACE": "stonepi", "SSID": "escama",
        "CHANNEL": "6", "CHANNEL_MODE": "auto", "HW_MODE": "g",
        "AP_IP": "10.42.1.1", "AP_CIDR": "24", "AP_SUBNET": "10.42.1.0/24",
        "DHCP_START": "10.42.1.10", "DHCP_END": "10.42.1.254",
        "DHCP_LEASE": "12h", "WPA_PASSPHRASE": "x", "DNS1": "8.8.8.8",
        "DNS2": "8.8.4.4"})
    _fake_run(monkeypatch, fallan=("nmcli device",))
    monkeypatch.setattr(escama, "generar_hostapd", lambda c: None)
    monkeypatch.setattr(escama, "generar_dnsmasq", lambda c, kind="": None)
    monkeypatch.setattr(escama, "_kill_procs", lambda: None)
    monkeypatch.setattr(escama, "_ensure_ip", lambda *a: None)
    monkeypatch.setattr(escama.time, "sleep", lambda s: None)
    escama.do_start()
    out = capsys.readouterr().out
    assert "DEGRADADO" in out
    assert "NetworkManager" in out


def test_motivo_fallo_incluye_el_stderr_real():
    class R:
        returncode = 1
        stdout = ""
        stderr = "Error: Failed to open file\nlinea2"
    m = escama._motivo_fallo(R(), "rmmod 8192eu")
    assert "rmmod 8192eu" in m
    assert "Failed to open file" in m
    assert "linea2" not in m, "solo la primera linea del error"


# ---------------------------------------------------------------------------
# Confs GENERADOS en ruta de usuario sin root (spec `uso-sin-privilegios`:
# "Mutar sin sudo en modo rootless" exige que el arranque no escriba en /etc)
# ---------------------------------------------------------------------------

def test_hostapd_conf_va_a_etc_con_root(monkeypatch):
    monkeypatch.setattr(escama.os, "geteuid", lambda: 0)
    assert escama._hostapd_conf() == "/etc/hostapd/hostapd-escama.conf"


def test_hostapd_conf_va_a_xdg_sin_root(monkeypatch, tmp_path):
    """Escribir en /etc/hostapd sin CAP_DAC_OVERRIDE aborta con
    PermissionError: el modo rootless no tendria con que arrancar."""
    monkeypatch.setattr(escama.os, "geteuid", lambda: 1000)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "cfg"))
    p = escama._hostapd_conf()
    assert p.startswith(str(tmp_path / "cfg")), p
    assert "hostapd-escama.conf" in p


def test_dnsmasq_conf_va_a_etc_con_root(monkeypatch):
    monkeypatch.setattr(escama.os, "geteuid", lambda: 0)
    assert escama._dnsmasq_conf() == "/etc/dnsmasq-escama.conf"


def test_dnsmasq_conf_va_a_xdg_sin_root(monkeypatch, tmp_path):
    monkeypatch.setattr(escama.os, "geteuid", lambda: 1000)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "cfg"))
    p = escama._dnsmasq_conf()
    assert p.startswith(str(tmp_path / "cfg")), p


def test_env_file_siempre_en_etc(monkeypatch):
    """La config del usuario NUNCA se mueve: es la fuente de verdad y solo se
    lee. Moverla romperia el contrato documentado en AGENTS.md."""
    assert escama.CONFIG_FILE == "/etc/escama/escama.toml"


def test_config_dir_cae_a_tmp_si_no_se_puede_crear(monkeypatch):
    monkeypatch.setattr(escama.os, "geteuid", lambda: 1000)
    monkeypatch.setenv("XDG_CONFIG_HOME", "/proc/no-escribible/x")
    d = escama._config_dir()
    assert d.startswith("/tmp"), d


def test_genconfig_escribe_en_la_ruta_del_usuario(monkeypatch, tmp_path):
    """End-to-end del arranque rootless: generar los confs sin privilege debe
    funcionar y no tocar /etc."""
    monkeypatch.setattr(escama.os, "geteuid", lambda: 1000)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "cfg"))
    monkeypatch.setattr(escama, "HOSTAPD_CONF", escama._hostapd_conf())
    monkeypatch.setattr(escama, "DNSMASQ_CONF", escama._dnsmasq_conf())
    monkeypatch.setattr(escama, "_read_state", lambda: {})
    monkeypatch.setattr(escama, "detect_vpn_iface", lambda c: "")
    monkeypatch.setattr(escama, "iface_mtu", lambda i: 1500)
    cfg = {
        "AP_IFACE": "stonepi", "WAN_IFACE": "wn8200nd", "SSID": "escama",
        "CHANNEL": "1", "HW_MODE": "g", "AP_IP": "10.42.1.1",
        "AP_CIDR": "24", "AP_SUBNET": "10.42.1.0/24", "DHCP_START": "10.42.1.10",
        "DHCP_END": "10.42.1.254", "DHCP_LEASE": "12h", "WPA_PASSPHRASE": "x",
        "DNS1": "8.8.8.8", "DNS2": "8.8.4.4", "LEASE_FILE": str(tmp_path / "l"),
    }
    escama.generar_hostapd(cfg)
    escama.generar_dnsmasq(cfg)
    assert (tmp_path / "cfg" / "escama" / "hostapd-escama.conf").is_file()
    assert (tmp_path / "cfg" / "escama" / "dnsmasq-escama.conf").is_file()
    txt = (tmp_path / "cfg" / "escama" / "hostapd-escama.conf").read_text()
    assert "ssid=escama" in txt


def test_version_se_lee_a_traves_de_un_symlink(monkeypatch, tmp_path):
    """install.sh symlinkea /usr/local/bin/escama -> /opt/escama/escama.py.

    Con abspath(__file__) la busqueda sube desde /usr/local/bin y nunca ve el
    VERSION de /opt/escama: el usuario que ejecuta `escama --version` (el comando
    que el propio install.sh crea) recibia "desconocido".
    """
    opt = tmp_path / "opt" / "escama"
    opt.mkdir(parents=True)
    (opt / "VERSION").write_text("9.9.9\n")
    core = opt / "escama.py"
    core.write_text("# copia simulada\n")
    bin_dir = tmp_path / "usr" / "local" / "bin"
    bin_dir.mkdir(parents=True)
    link = bin_dir / "escama"
    link.symlink_to(core)
    # Con abspath (lo que hacia antes) esto daba "desconocido"; con realpath
    # se resuelve el symlink y se encuentra el VERSION de al lado del core.
    monkeypatch.setattr(escama, "__file__", str(link))
    assert escama._read_version() == "9.9.9"


def test_version_degrada_sin_hay_VERSION(tmp_path):
    """Sin VERSION debe degradar a 'desconocido', nunca a un numero viejo."""
    lonely = tmp_path / "sin" / "version" / "escama.py"
    lonely.parent.mkdir(parents=True)
    lonely.write_text("# nada\n")
    assert escama._leer_version_desde(str(lonely)) == "desconocido"


def test_tui_usa_realpath_para_no_perder_la_version():
    """El mismo bug en escama-tui.py: sin realpath degradaba a desconocido."""
    import importlib.util
    ruta = os.path.join(RAIZ_REPO, "opt", "escama", "escama-tui.py")
    src = open(ruta).read()
    assert "os.path.realpath(__file__)" in src, (
        "escama-tui debe resolver la version con realpath para funcionar via symlink")
    assert "os.path.abspath(__file__)" not in src, (
        "abspath rompe la busqueda de VERSION cuando el comando se invoca por symlink")


# ---------------------------------------------------------------------------
# Endurecimiento 2.0.0 (audit) + config TOML
# ---------------------------------------------------------------------------

import tomllib


def test_do_start_sin_passphrase_no_levanta_nada(monkeypatch):
    """Sin passphrase el AP no arranca: ni abierto ni reusando una contrasena
    del historial de git (el repo es publico)."""
    calls = []
    monkeypatch.setattr(escama, "load_env", lambda: dict(escama.DEFAULTS))
    monkeypatch.setattr(escama, "run", lambda *a, **k: calls.append(a[0]) or type(
        "R", (), {"returncode": 0, "stdout": "", "stderr": ""})())
    rc = escama.do_start()
    assert rc == 1
    assert not any(c[:1] == ["hostapd"] for c in calls), "no hostapd sin passphrase"


def test_kill_procs_dnsmasq_solo_por_pidfile(monkeypatch, tmp_path):
    """El dnsmasq de escama se mata por pidfile, NUNCA por nombre: LXC corre el
    suyo para lxcbr0 y un pkill -x lo romperia. hostapd sigue por nombre (es
    exclusivo de escama)."""
    pid = tmp_path / "pid"
    pid.write_text("123\n")
    monkeypatch.setattr(escama, "PIDFILE", str(pid))
    calls = []

    def fake_run(cmd, capture=True, **_kw):
        calls.append(cmd)
        return None
    monkeypatch.setattr(escama, "run", fake_run)
    monkeypatch.setattr(escama.time, "sleep", lambda s: None)
    escama._kill_procs()
    planas = [" ".join(c) for c in calls]
    assert "kill 123" in planas and "kill -9 123" in planas, planas
    assert any("hostapd" in p for p in planas), "hostapd sigue matandose por nombre"
    assert not any("dnsmasq" in p for p in planas), "NUNCA pkill por nombre de dnsmasq"


def test_run_devuelve_none_si_el_binario_no_existe(monkeypatch):
    """Maquina pelada sin iw: degradar a None (los callers ya lo manejan), no
    traceback."""
    def boom(*a, **k):
        raise FileNotFoundError("iw")
    monkeypatch.setattr(escama.subprocess, "run", boom)
    assert escama.run(["iw", "dev", "info"]) is None


def test_run_ro_nunca_prefija_sudo(monkeypatch):
    """Los comandos de SOLO LECTURA nunca llevan sudo: escama status sin
    launcher no debe pedir password (y sin TTY, sudo falla en silencio)."""
    vistos = []

    def fake(*a, **k):
        vistos.append(a[0])
        return type("R", (), {"returncode": 0, "stdout": "", "stderr": ""})()
    monkeypatch.setattr(escama.subprocess, "run", fake)
    monkeypatch.setattr(escama.os, "geteuid", lambda: 1000)
    monkeypatch.delenv("ESCAMA_VIA_LAUNCHER", raising=False)
    escama.run(["iw", "dev", "info"], ro=True)
    assert vistos[-1] == ["iw", "dev", "info"], "ro=True nunca antepone sudo"
    escama.run(["ip", "link", "set", "x", "up"])
    assert vistos[-1][0] == "sudo", "lo mutante, sin root ni launcher, pide sudo"


def test_reload_otro_driver_no_toca_rmmod(monkeypatch, capsys):
    """El reload automatico era un truco del DKMS 8192eu. Con otro driver en
    memoria (p. ej. aic8800_fdrv) rmmod del modulo equivocado no arregla nada:
    degradar con informacion, sin rmmod."""
    monkeypatch.setattr(escama, "iface_exists", lambda x: True)
    monkeypatch.setattr(escama, "_ap_phy", lambda: "phy0")
    monkeypatch.setattr(escama, "_driver_de", lambda a: "aic8800_fdrv")
    calls = []

    def fake_run(c, capture=True, **_kw):
        calls.append(c)
        return type("R", (), {"returncode": 0, "stdout": "* IBSS\n", "stderr": ""})()
    monkeypatch.setattr(escama, "run", fake_run)
    escama.reload_module_if_needed("wlx020204050607")
    out = capsys.readouterr().out
    assert "DEGRADADO" in out and "aic8800_fdrv" in out
    assert not any(c[:1] == ["rmmod"] for c in calls), "no rmmod de otro driver"
    assert not any(c[:1] == ["modprobe"] for c in calls)


def test_save_config_preserva_comentarios_y_claves_ajenas(tmp_path, monkeypatch):
    """save_config reescribe SOLO las claves conocidas: los comentarios y las
    claves ajenas del usuario se conservan (la version vieja borraba ~40
    lineas de documentacion)."""
    toml = tmp_path / "escama.toml"
    toml.write_text(
        "# mi config casera\n"
        'SSID = "red-vieja"\n'
        "# comentario entre claves\n"
        'CLAVE_AJENA = "no tocar"\n'
        'DNS1 = "1.1.1.1"\n'
    )
    monkeypatch.setattr(escama, "CONFIG_FILE", str(toml))
    cfg = dict(escama.DEFAULTS, SSID="red-nueva", DNS1="1.1.1.1")
    escama.save_config(cfg)
    out = toml.read_text()
    assert "# mi config casera" in out, "los comentarios del usuario NO se borran"
    assert "# comentario entre claves" in out
    assert 'CLAVE_AJENA = "no tocar"' in out, "claves ajenas se conservan"
    assert 'SSID = "red-nueva"' in out
    assert 'SSID = "red-vieja"' not in out
    for k in escama.DEFAULTS:  # faltantes se agregan
        assert f"{k} = " in out, k
    with open(toml, "rb") as f:  # el resultado vuelve a ser TOML valido
        d = tomllib.load(f)
    assert d["SSID"] == "red-nueva"


def test_save_config_comenta_duplicadas(tmp_path, monkeypatch):
    """Claves repetidas: la primera gana y el resto se comenta (TOML no
    admite duplicados y el archivo debe seguir parseando)."""
    toml = tmp_path / "escama.toml"
    toml.write_text('SSID = "a"\nSSID = "b"\n')
    monkeypatch.setattr(escama, "CONFIG_FILE", str(toml))
    escama.save_config(dict(escama.DEFAULTS, SSID="c"))
    with open(toml, "rb") as f:
        d = tomllib.load(f)
    assert d["SSID"] == "c"
    assert "# duplicada" in toml.read_text()


# ---------------------------------------------------------------------------
# rename: productiza los renombres manuales udev por MAC (stonepi, wn8200nd)
# ---------------------------------------------------------------------------

def _rename_entorno(monkeypatch, tmp_path, old="wlx020304050607", new="wifi-usb",
                    mac="02:1a:2b:3c:4d:01", wifi=True, tipo_ap=False,
                    ap_iface="", wan_iface="", euid=0):
    """Banco de pruebas comun: sysfs simulado, reglas udev en tmp_path,
    config en tmp_path, todo en orden (geteuid parametrizable)."""
    monkeypatch.setattr(escama.os, "geteuid", lambda: euid)
    monkeypatch.setattr(escama, "iface_exists",
                        lambda x: x in (old, "otra-ifi"))
    monkeypatch.setattr(escama, "iface_wifi", lambda x: wifi)
    monkeypatch.setattr(escama, "iface_type_ap", lambda x: tipo_ap)
    monkeypatch.setattr(escama, "_mac_de", lambda x: mac)
    monkeypatch.setattr(escama, "RENAME_RULES",
                        str(tmp_path / "76-escama-ifaces.rules"))
    legacy1 = tmp_path / "70-persistent-net.rules"
    legacy2 = tmp_path / "99-stonepi-ap.rules"
    legacy1.write_text(
        '# This file was automatically generated\n'
        'ACTION=="add", SUBSYSTEM=="net", DRIVERS=="?*", '
        'ATTR{address}=="02:1a:2b:3c:4d:02", NAME="wn8200nd"\n')
    legacy2.write_text(
        "# regla manual: renombrado a mano para el AP\n"
        'SUBSYSTEM=="net", ACTION=="add", ATTR{address}=="02:1a:2b:3c:4d:03", '
        'NAME="stonepi"\n')
    monkeypatch.setattr(escama, "RENAME_LEGACY", (str(legacy1), str(legacy2)))
    toml = tmp_path / "escama.toml"
    toml.write_text("# config casera\n"
                    f'AP_IFACE = "{ap_iface or "wn8200nd"}"\n'
                    f'WAN_IFACE = "{wan_iface or "stonepi"}"\n')
    monkeypatch.setattr(escama, "CONFIG_FILE", str(toml))
    monkeypatch.setattr(escama, "load_env", lambda: dict(
        escama.DEFAULTS, AP_IFACE=ap_iface or "wn8200nd",
        WAN_IFACE=wan_iface or "stonepi"))
    return legacy1, legacy2, toml


def test_do_rename_valida_nombre(monkeypatch, tmp_path):
    """Nombre invalido: rechaza ANTES de tocar nada (sin reglas, sin comandos)."""
    calls = []
    _rename_entorno(monkeypatch, tmp_path)
    monkeypatch.setattr(escama, "run", lambda c, **k: calls.append(c) or None)
    for nuevo in ("a" * 16, "9wifi", "con espacio", "con.punto", "lo", ""):
        rc = escama.do_rename(["wlx020304050607", nuevo])
        assert rc == 1, nuevo
    assert calls == [], "ningun comando ni escritura con nombre invalido"
    assert not os.path.exists(tmp_path / "76-escama-ifaces.rules")


def test_do_rename_requiere_wifi_y_root(monkeypatch, tmp_path):
    """Solo adaptadores WiFi (phy80211) y solo con sudo directo (la regla udev
    escribe /etc: el launcher rootless no da DAC override)."""
    _rename_entorno(monkeypatch, tmp_path, wifi=False)
    rc = escama.do_rename(["wlx020304050607", "nuevo"])
    assert rc == 1

    _rename_entorno(monkeypatch, tmp_path, euid=1000)
    rc = escama.do_rename(["wlx020304050607", "nuevo"])
    assert rc == 1


def test_do_rename_rechaza_colision_y_si_esta_en_ap(monkeypatch, tmp_path):
    """No renombrar sobre un nombre existente, ni una iface en modo AP (baja
    el AP primero: un rename a mitad de hostapd rompe las dos cosas)."""
    _rename_entorno(monkeypatch, tmp_path, new="otra-ifi")
    calls = []
    monkeypatch.setattr(escama, "run", lambda c, **k: calls.append(c) or None)
    assert escama.do_rename(["wlx020304050607", "otra-ifi"]) == 1
    assert calls == []

    _rename_entorno(monkeypatch, tmp_path, tipo_ap=True)
    calls.clear()
    assert escama.do_rename(["wlx020304050607", "nuevo"]) == 1
    assert calls == []


def test_do_rename_sin_argumentos(monkeypatch, capsys):
    assert escama.do_rename([]) == 2
    assert escama.do_rename(["solo-uno"]) == 2
    assert "rename <iface>" in capsys.readouterr().err


def test_do_rename_secuencia_en_vivo(monkeypatch, tmp_path, capsys):
    """managed no -> down -> rename -> up -> managed yes, y revincula el
    perfil NM que estaba activo sobre el nombre viejo."""
    legacy1, legacy2, toml = _rename_entorno(monkeypatch, tmp_path)
    calls = []

    def fake_run(cmd, capture=True, **_kw):
        calls.append(cmd)
        if cmd[:3] == ["nmcli", "-t", "-f"]:
            class R:
                returncode = 0
                stdout = "internet:wlx020304050607\notra:red\n"
                stderr = ""
            return R()
        class R:
            returncode = 0
            stdout = ""
            stderr = ""
        return R()
    monkeypatch.setattr(escama, "run", fake_run)
    rc = escama.do_rename(["wlx020304050607", "wifi-usb"])
    assert rc == 0
    planas = [" ".join(c) for c in calls]
    orden = [p for p in planas if p.startswith("ip link set")]
    assert orden == ["ip link set wlx020304050607 down",
                     "ip link set wlx020304050607 name wifi-usb",
                     "ip link set wifi-usb up"], orden
    assert "nmcli device set wlx020304050607 managed no" in planas
    assert "nmcli device set wifi-usb managed yes" in planas
    assert any("connection modify internet connection.interface-name wifi-usb" in p
               for p in planas), "perfil NM activo en el nombre viejo debe revincularse"
    assert not any("connection modify otra" in p for p in planas)


def test_do_rename_fallo_kernel_rollback(monkeypatch, tmp_path, capsys):
    """Si el kernel rechaza el rename, rollback a up+managed yes y rc 1, con
    el motivo real del comando fallido (no un generico)."""
    _rename_entorno(monkeypatch, tmp_path)
    calls = []
    monkeypatch.setattr(escama, "_motivo_fallo",
                        lambda r, cmd: f"{cmd}: Operation not permitted")

    def fake_run(cmd, capture=True, **_kw):
        calls.append(cmd)
        if cmd[:3] == ["ip", "link", "set"] and "name" in cmd:
            class R:
                returncode = 1
                stdout = ""
                stderr = "Operation not permitted"
            return R()
        class R:
            returncode = 0
            stdout = ""
            stderr = ""
        return R()
    monkeypatch.setattr(escama, "run", fake_run)
    rc = escama.do_rename(["wlx020304050607", "wifi-usb"])
    assert rc == 1
    planas = [" ".join(c) for c in calls]
    assert "ip link set wlx020304050607 up" in planas, "rollback: deja la iface arriba"
    assert "nmcli device set wlx020304050607 managed yes" in planas
    captura = capsys.readouterr()
    out = captura.out + captura.err
    assert "Operation not permitted" in out, "motivo real del fallo"
    # la regla udev igual quedo escrita: aplica en el proximo boot/plug
    assert 'NAME="wifi-usb"' in (tmp_path / "76-escama-ifaces.rules").read_text()


def test_do_rename_regla_udev_y_retiro_legacy(monkeypatch, tmp_path):
    """Escribe la regla por MAC en el archivo de escama y retira de los
    legacy la regla de esa misma MAC (con su comentario). Idempotente."""
    legacy1, legacy2, toml = _rename_entorno(
        monkeypatch, tmp_path, old="wn8200nd",
        mac="02:1a:2b:3c:4d:02")  # MAC de ejemplo (wn8200nd)
    calls = []
    monkeypatch.setattr(escama, "run", lambda c, **k: calls.append(c) or type(
        "R", (), {"returncode": 0, "stdout": "", "stderr": ""})())
    rc = escama.do_rename(["wn8200nd", "wifi-usb"])
    assert rc == 0
    reglas = (tmp_path / "76-escama-ifaces.rules").read_text()
    assert 'ATTR{address}=="02:1a:2b:3c:4d:02", NAME="wifi-usb"' in reglas
    # legacy: la regla de esa MAC se retiro (con el comentario de arriba)
    l1 = legacy1.read_text()
    assert "02:1a:2b:3c:4d:02" not in l1
    assert 'NAME="wn8200nd"' not in l1, "la regla retirada no deja huerfana"
    assert "This file was automatically generated" in l1, "resto del archivo intacto"
    # la otra MAC (stonepi) no se toca: el retiro es SOLO por la MAC renombrada
    assert 'NAME="stonepi"' in legacy2.read_text()
    # idempotente: re-corrida no duplica (wifi-usb ya existe tras el rename)
    existe = {"wifi-usb"}
    monkeypatch.setattr(escama, "iface_exists", lambda x: x in existe)
    rc = escama.do_rename(["wifi-usb", "wifi-usb2"])
    assert rc == 0
    reglas = (tmp_path / "76-escama-ifaces.rules").read_text()
    assert reglas.count("02:1a:2b:3c:4d:02") == 1, "una sola regla por MAC"


def test_do_rename_regla_otros_mac_con_ese_nombre_rechaza(monkeypatch, tmp_path):
    """Otra MAC ya reclama el nombre en el archivo de escama: no crear la
    ambiguedad (dos reglas pisan el mismo NAME)."""
    _rename_entorno(monkeypatch, tmp_path)
    reglas = tmp_path / "76-escama-ifaces.rules"
    reglas.write_text('SUBSYSTEM=="net", ACTION=="add", '
                      'ATTR{address}=="aa:bb:cc:dd:ee:ff", NAME="wifi-usb"\n')
    monkeypatch.setattr(escama, "run", lambda c, **k: None)
    rc = escama.do_rename(["wlx020304050607", "wifi-usb"])
    assert rc == 1


def test_do_rename_sincroniza_config(monkeypatch, tmp_path):
    """Si AP_IFACE o WAN_IFACE apuntaban al nombre viejo, el toml se
    actualiza (save_config conserva los comentarios)."""
    legacy1, legacy2, toml = _rename_entorno(
        monkeypatch, tmp_path, wan_iface="wlx020304050607")
    calls = []
    monkeypatch.setattr(escama, "run", lambda c, **k: calls.append(c) or type(
        "R", (), {"returncode": 0, "stdout": "", "stderr": ""})())
    rc = escama.do_rename(["wlx020304050607", "wifi-usb"])
    assert rc == 0
    out = toml.read_text()
    assert "# config casera" in out, "comentarios intactos"
    assert 'WAN_IFACE = "wifi-usb"' in out
    assert "wlx020304050607" not in out
    with open(toml, "rb") as f:
        d = tomllib.load(f)
    assert d["WAN_IFACE"] == "wifi-usb"
    assert d["AP_IFACE"] == "wn8200nd", "solo las claves que apuntaban al viejo"

    # sin claves apuntando al viejo: toml sin cambios
    legacy1, legacy2, toml2 = _rename_entorno(monkeypatch, tmp_path)
    antes = toml2.read_text()
    escama.do_rename(["wlx020304050607", "wifi-usb"])
    assert toml2.read_text() == antes, "sin claves afectadas, no reescribe"


# ---------------------------------------------------------------------------
# autorename: nombres por defecto (wifi-<4 de MAC>) para WiFi con nombre
# generico del kernel. Personalizados no se tocan; WAN nunca se renombra
# automaticamente (solo por el comando manual).
# ---------------------------------------------------------------------------

def _autorename_entorno(monkeypatch, tmp_path, wifis=("wlx020304050607",),
                        macs=None, tipo_ap=(), euid=0, ap_iface="",
                        wan_iface=""):
    """Banco de pruebas de autorename: WiFi presentes simuladas, config en
    tmp_path y secuencia run() capturada."""
    monkeypatch.setattr(escama.os, "geteuid", lambda: euid)
    monkeypatch.setattr(escama, "iface_exists",
                        lambda x: x in set(wifis) | {"otra-ifi"})
    monkeypatch.setattr(escama, "_wifis_presentes", lambda: sorted(wifis))
    macs = macs or {w: "02:1a:2b:3c:4d:01" for w in wifis}
    monkeypatch.setattr(escama, "_mac_de", lambda x: macs.get(x, ""))
    monkeypatch.setattr(escama, "iface_type_ap", lambda x: x in tipo_ap)
    monkeypatch.setattr(escama, "RENAME_RULES",
                        str(tmp_path / "76-escama-ifaces.rules"))
    monkeypatch.setattr(escama, "RENAME_LEGACY", ())
    toml = tmp_path / "escama.toml"
    toml.write_text("# config casera\n"
                    f'AP_IFACE = "{ap_iface}"\n'
                    f'WAN_IFACE = "{wan_iface}"\n')
    monkeypatch.setattr(escama, "CONFIG_FILE", str(toml))
    monkeypatch.setattr(escama, "load_env", lambda: dict(
        escama.DEFAULTS, AP_IFACE=ap_iface, WAN_IFACE=wan_iface))
    calls = []
    monkeypatch.setattr(escama, "run", lambda c, **k: calls.append(c) or type(
        "R", (), {"returncode": 0, "stdout": "", "stderr": ""})())
    return toml, calls


def test_nombre_generico_patrones():
    """Genericos: wlx<MAC>, wlanN, wlpXsY. Un nombre puesto por el usuario
    (stonepi, WU900, wifi-b48f) no matchea."""
    assert escama._nombre_generico("wlx020304050607")
    assert escama._nombre_generico("wlan0")
    assert escama._nombre_generico("wlan12")
    assert escama._nombre_generico("wlp3s0")
    for nombre in ("stonepi", "wn8200nd", "WU900", "wifi-b48f", "wifi-usb",
                   "lo", "eth0", "wlan0mon", "wlan_ap", "wlx02030405060"):
        assert not escama._nombre_generico(nombre), nombre


def test_nombre_default_esquema_y_escalada():
    """wifi-<ultimos 4 hex de la MAC>; si colisiona escala a 6, 8 y 10
    nibbles (12 no entra en IFNAMSIZ). Sin nombre libre: ""."""
    mac = "02:1a:2b:3c:4d:01"
    assert escama._nombre_default(mac) == "wifi-4d01"
    assert escama._nombre_default(mac, {"wifi-4d01"}) == "wifi-3c4d01"
    assert escama._nombre_default(
        mac, {"wifi-4d01", "wifi-3c4d01"}) == "wifi-2b3c4d01"
    assert escama._nombre_default(
        mac, {"wifi-4d01", "wifi-3c4d01",
              "wifi-2b3c4d01"}) == "wifi-1a2b3c4d01"
    assert escama._nombre_default(
        mac, {"wifi-4d01", "wifi-3c4d01", "wifi-2b3c4d01",
              "wifi-1a2b3c4d01"}) == ""
    assert escama._nombre_default("no-es-una-mac") == ""


def test_do_autorename_renomba_y_sincroniza_toml(monkeypatch, tmp_path):
    """AP_IFACE generica: renombre vivo + regla udev + toml al nombre nuevo."""
    toml, calls = _autorename_entorno(
        monkeypatch, tmp_path, ap_iface="wlx020304050607")
    rc = escama.do_autorename([])
    assert rc == 0
    planas = [" ".join(c) for c in calls]
    assert "ip link set wlx020304050607 name wifi-4d01" in planas
    assert 'AP_IFACE = "wifi-4d01"' in toml.read_text()
    reglas = (tmp_path / "76-escama-ifaces.rules").read_text()
    assert 'ATTR{address}=="02:1a:2b:3c:4d:01"' in reglas
    assert 'NAME="wifi-4d01"' in reglas


def test_do_autorename_idempotente_con_personalizados(monkeypatch, tmp_path):
    """Solo personalizados presentes: nada que hacer, rc 0, toml intacto."""
    toml, calls = _autorename_entorno(
        monkeypatch, tmp_path, wifis=("stonepi",),
        macs={"stonepi": "02:1a:2b:3c:4d:02"}, ap_iface="stonepi")
    antes = toml.read_text()
    assert escama.do_autorename([]) == 0
    assert not any("ip link set" in " ".join(c) for c in calls)
    assert toml.read_text() == antes


def test_do_autorename_renomba_wan_si_es_manual(monkeypatch, tmp_path):
    """El comando manual escanea TODAS las WiFi presentes, incluida la WAN
    generica (el dongle nuevo); el AP personalizado no se toca."""
    toml, calls = _autorename_entorno(
        monkeypatch, tmp_path, wifis=("stonepi", "wlx020304050607"),
        macs={"stonepi": "02:1a:2b:3c:4d:02",
              "wlx020304050607": "02:1a:2b:3c:4d:01"},
        ap_iface="stonepi", wan_iface="wlx020304050607")
    rc = escama.do_autorename([])
    assert rc == 0
    planas = [" ".join(c) for c in calls]
    assert "ip link set wlx020304050607 name wifi-4d01" in planas
    out = toml.read_text()
    assert 'WAN_IFACE = "wifi-4d01"' in out
    assert 'AP_IFACE = "stonepi"' in out, "el AP personalizado queda igual"


def test_do_autorename_requiere_root_y_sin_args(monkeypatch, tmp_path):
    """Sin sudo: rc 1. Con argumentos de mas: rc 2."""
    _autorename_entorno(monkeypatch, tmp_path, euid=1000)
    assert escama.do_autorename([]) == 1
    assert escama.do_autorename(["extra"]) == 2


def test_do_autorename_salta_modo_ap(monkeypatch, tmp_path):
    """Iface generica en modo AP activo: no se renombra en caliente; el
    resto no falla (rc 0, salto logueado)."""
    _autorename_entorno(
        monkeypatch, tmp_path, ap_iface="wlx020304050607",
        tipo_ap=("wlx020304050607",))
    assert escama.do_autorename([]) == 0


def test_do_autorename_colision_entre_dongles(monkeypatch, tmp_path):
    """Dos dongles con mismos ultimos 4 hex: nombres distintos (escalada)."""
    _autorename_entorno(
        monkeypatch, tmp_path,
        wifis=("wlx020304050607", "wlx030405060708"),
        macs={"wlx020304050607": "02:1a:2b:3c:4d:01",
              "wlx030405060708": "aa:bb:cc:dd:4d:01"})
    rc = escama.do_autorename([])
    assert rc == 0
    reglas = (tmp_path / "76-escama-ifaces.rules").read_text()
    assert reglas.count('NAME="wifi-4d01"') == 1
    assert 'NAME="wifi-dd4d01"' in reglas, \
        "segundo dongle escala a 6 nibbles de SU MAC"


def test_hook_start_renombra_ap_generico(monkeypatch, tmp_path):
    """Gatillo en start: primera vez tras instalar (o config reseteada) el
    AP generico se renombra, el toml queda apuntando al nombre nuevo."""
    toml, calls = _autorename_entorno(
        monkeypatch, tmp_path, ap_iface="wlx020304050607")
    cfg = escama.load_env()
    nuevo = escama._autorename_ap_si_corresponde(cfg)
    assert nuevo == "wifi-4d01"
    assert cfg["AP_IFACE"] == "wifi-4d01"
    assert 'AP_IFACE = "wifi-4d01"' in toml.read_text()
    planas = [" ".join(c) for c in calls]
    assert "ip link set wlx020304050607 name wifi-4d01" in planas


def test_hook_start_no_toca_personalizada(monkeypatch, tmp_path):
    """AP con nombre propio (stonepi): hook sin efecto, cada start."""
    toml, calls = _autorename_entorno(
        monkeypatch, tmp_path, wifis=("stonepi",),
        macs={"stonepi": "02:1a:2b:3c:4d:02"}, ap_iface="stonepi")
    cfg = escama.load_env()
    assert escama._autorename_ap_si_corresponde(cfg) == ""
    assert toml.read_text().count('AP_IFACE = "stonepi"') == 1
    assert not any("ip link set" in " ".join(c) for c in calls)


def test_hook_start_wan_intacta(monkeypatch, tmp_path):
    """Regla de oro: el gatillo automatico nunca renombra la WAN generica
    (solo el AP); el comando manual es el que la cubre."""
    toml, calls = _autorename_entorno(
        monkeypatch, tmp_path, wifis=("stonepi", "wlx020304050607"),
        macs={"stonepi": "02:1a:2b:3c:4d:02",
              "wlx020304050607": "02:1a:2b:3c:4d:01"},
        ap_iface="stonepi", wan_iface="wlx020304050607")
    cfg = escama.load_env()
    assert escama._autorename_ap_si_corresponde(cfg) == ""
    assert 'WAN_IFACE = "wlx020304050607"' in toml.read_text()
    assert not any("name" in " ".join(c) for c in calls)


def test_main_despacha_autorename_y_pide_sudo(monkeypatch, tmp_path, capsys):
    """autorename entra por el gate de privilegio (como rename: no es de
    solo lectura y no dispara bootstrap) y despacha a do_autorename."""
    _autorename_entorno(
        monkeypatch, tmp_path, wifis=("stonepi",),
        macs={"stonepi": "02:1a:2b:3c:4d:02"}, ap_iface="stonepi")
    assert escama.main(["autorename"]) == 0
    _autorename_entorno(
        monkeypatch, tmp_path, euid=1000, wifis=("wlx020304050607",),
        ap_iface="wlx020304050607")
    monkeypatch.setattr(escama, "rootless_disponible",
                        lambda: (False, "sin launcher"))
    assert escama.main(["autorename"]) == 1
    captura = capsys.readouterr()
    assert "modifica el sistema" in captura.out + captura.err, \
        "el gate de main avisa antes que el check interno"
