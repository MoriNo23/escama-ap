#!/usr/bin/env python3
"""
escama.py - Núcleo del AP casero "escama" (hostapd + dnsmasq).

Única fuente de lógica. Lee /etc/escama/escama.env como fuente de verdad,
genera hostapd-escama.conf y dnsmasq-escama.conf desde el env, levanta/baja
el AP, valida de verdad (type AP, no grep ssid), y aplica masquerade dinámico
usando WAN_IFACE del env (nunca hardcodeado).

Regla de oro: la iface WAN (stonepi por defecto) SOLO se lee, NUNCA se modifica
(ip addr del, nmcli, hostapd) salvo que el env diga lo contrario.

Uso: sudo escama.py {start|stop|restart|status|reconnect|genconfig}
"""
import os
import sys
import syslog
import subprocess
import shutil
import time
import re

# --- Version ---
VERSION = "1.0.0"

# --- Paths ---
CONFIG_DIR = "/etc/escama"
ENV_FILE = os.path.join(CONFIG_DIR, "escama.env")
HOSTAPD_CONF = "/etc/hostapd/hostapd-escama.conf"
DNSMASQ_CONF = "/etc/dnsmasq-escama.conf"
LOG = "/var/log/escama-ap.log"
LEASE_FILE = "/var/lib/misc/dnsmasq-escama.leases"
PIDFILE = "/run/dnsmasq-escama.pid"

# Defaults (overriden by env)
DEFAULTS = {
    "AP_IFACE": "wn8200nd",
    "WAN_IFACE": "stonepi",
    "SSID": "escama",
    "CHANNEL": "6",
    "HW_MODE": "g",
    "AP_IP": "10.42.1.1",
    "AP_CIDR": "24",
    "AP_SUBNET": "10.42.1.0/24",
    "DHCP_START": "10.42.1.10",
    "DHCP_END": "10.42.1.254",
    "DHCP_LEASE": "12h",
    "WPA_PASSPHRASE": "#[REMOVED]",
    "DNS1": "8.8.8.8",
    "DNS2": "8.8.4.4",
}


def log(msg: str) -> None:
    line = f"{time.strftime('%H:%M:%S')} {msg}"
    try:
        os.makedirs(os.path.dirname(LOG) or ".", exist_ok=True)
        with open(LOG, "a") as f:
            f.write(line + "\n")
    except OSError:
        pass
    print(line)
    try:
        syslog.syslog(syslog.LOG_INFO, msg)
    except Exception:
        pass


def run(cmd, check=True, capture=True):
    """Run a command via root (sudo if not already root)."""
    if os.geteuid() != 0:
        cmd = ["sudo"] + cmd
    try:
        if capture:
            return subprocess.run(cmd, capture_output=True, text=True)
        return subprocess.run(cmd)
    except FileNotFoundError as e:
        if check:
            raise
        return None


def load_env() -> dict:
    cfg = dict(DEFAULTS)
    if os.path.isfile(ENV_FILE):
        with open(ENV_FILE) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                cfg[k.strip()] = v.strip().strip('"').strip("'")
    return cfg


def iface_exists(iface: str) -> bool:
    return os.path.islink(f"/sys/class/net/{iface}")


def wan_has_internet(wan: str) -> bool:
    """Ping the WAN gateway. WAN iface is only READ, never modified."""
    r = run(["ip", "route", "show", "dev", wan], capture=True)
    gw = None
    for l in (r.stdout or "").splitlines():
        if "default" in l:
            m = re.search(r"via (\S+)", l)
            if m:
                gw = m.group(1)
                break
    if not gw:
        return False
    p = run(["ping", "-c", "1", "-W", "3", gw], capture=True)
    return p.returncode == 0


def module_has_ap_mode() -> bool:
    """Check the loaded 8192eu module exposes AP mode (CONFIG_AP_MODE=y)."""
    p = run(["iw", "phy", _ap_phy(), "info"], capture=True)
    if p.returncode != 0:
        return False
    return "type AP" in (p.stdout or "") or "* AP" in (p.stdout or "")


def _ap_phy() -> str:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    phy = f"/sys/class/net/{ap}/phy80211"
    if os.path.islink(phy):
        return os.path.basename(os.readlink(phy))
    return ""


def reload_module_if_needed(ap: str) -> None:
    """If hostapd will fail with -95 (Operation not supported), the module in
    memory lacks CONFIG_AP_MODE. Reload the DKMS module to fix."""
    if not iface_exists(ap):
        return
    phy = _ap_phy()
    if not phy:
        return
    p = run(["iw", "phy", phy, "info"], capture=True)
    if p.returncode == 0 and "* AP" not in (p.stdout or ""):
        log(f"AP mode NOT exposed by {ap}; reloading 8192eu DKMS module")
        run(["rmmod", "8192eu"], check=False)
        time.sleep(1)
        run(["depmod", "-a"], check=False)
        run(["modprobe", "8192eu"], check=False)
        time.sleep(2)


def generate_configs(cfg: dict) -> None:
    """Single source of truth: env -> hostapd + dnsmasq confs."""
    hostapd = f"""interface={cfg['AP_IFACE']}
driver=nl80211
ssid={cfg['SSID']}
hw_mode={cfg['HW_MODE']}
channel={cfg['CHANNEL']}
ieee80211n=1
ht_capab=[HT20]
wmm_enabled=1
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase={cfg['WPA_PASSPHRASE']}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=CCMP
rsn_pairwise=CCMP
"""
    dnsmasq = f"""interface={cfg['AP_IFACE']}
bind-interfaces
dhcp-range={cfg['DHCP_START']},{cfg['DHCP_END']},255.255.255.0,{cfg['DHCP_LEASE']}
dhcp-option=option:router,{cfg['AP_IP']}
dhcp-option=option:dns-server,{cfg['DNS1']},{cfg['DNS2']}
dhcp-leasefile={LEASE_FILE}
"""
    os.makedirs(os.path.dirname(HOSTAPD_CONF), exist_ok=True)
    with open(HOSTAPD_CONF, "w") as f:
        f.write(hostapd)
    with open(DNSMASQ_CONF, "w") as f:
        f.write(dnsmasq)
    log("Configs regenerated from escama.env")


def _kill_procs() -> None:
    run(["pkill", "-x", "hostapd"], check=False)
    run(["pkill", "-x", "dnsmasq"], check=False)
    time.sleep(1)
    run(["pkill", "-9", "-x", "hostapd"], check=False)
    run(["pkill", "-9", "-x", "dnsmasq"], check=False)
    if os.path.exists(PIDFILE):
        os.remove(PIDFILE)


def _ensure_ip(ap: str, ip_addr: str, cidr: str) -> None:
    # remove any stale 10.42.1.1 on OTHER ifaces (the duplicate-IP bug), but
    # never touch WAN iface config beyond reading.
    run(["ip", "addr", "flush", "dev", ap], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    run(["ip", "addr", "add", f"{ip_addr}/{cidr}", "dev", ap], check=False)


def do_start() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    if not wan:
        r = run(["ip", "route", "show", "default"], capture=True)
        for l in (r.stdout or "").splitlines():
            m = re.search(r"dev (\S+)", l)
            if m:
                wan = m.group(1)
                break
        if not wan:
            wan = "stonepi"
        cfg["WAN_IFACE"] = wan

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    generate_configs(cfg)
    _kill_procs()

    # assign AP IP
    _ensure_ip(ap, cfg["AP_IP"], cfg["AP_CIDR"])

    # hostapd
    r = run(["hostapd", "-B", HOSTAPD_CONF], check=False)
    if r.returncode != 0:
        log(f"ERROR: hostapd fallo (rc={r.returncode})")
        return 1
    time.sleep(3)

    # dnsmasq
    run(["dnsmasq", "--conf-file=" + DNSMASQ_CONF,
         "--pid-file=" + PIDFILE], check=False)

    # forward + masquerade (dynamic WAN iface)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", wan, "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if wan_has_internet(wan):
            log(f"OK: {wan} tiene internet (gateway alcanzable)")
        else:
            log(f"WARN: {wan} sin internet al momento de levantar")
        return 0
    else:
        log(f"ERROR: {ap} no entro en modo AP tras levantar")
        return 1


def do_stop() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    log("Deteniendo AP...")
    _kill_procs()
    run(["ip", "addr", "del", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}", "dev", ap],
        check=False)
    run(["nmcli", "device", "set", ap, "managed", "yes"], check=False)
    run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-o", wan,
         "-s", cfg["AP_SUBNET"], "-j", "MASQUERADE"], check=False)
    run(["sysctl", "-w", "net.ipv4.ip_forward=0"], check=False)
    run(["ip", "link", "set", ap, "down"], check=False)
    time.sleep(1)
    run(["ip", "link", "set", ap, "up"], check=False)
    log("AP detenido. iface restaurada a cliente (NM gestionado).")
    return 0


def do_status() -> int:
    cfg = load_env()
    ap = cfg["AP_IFACE"]
    wan = cfg["WAN_IFACE"]
    print(f"=== escama AP Status ===")
    print(f"AP iface:    {ap}")
    print(f"WAN iface:   {wan}")
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        print("Modo:        AP (activo)")
        print(f"IP:          {cfg['AP_IP']}/{cfg['AP_CIDR']}")
        print(f"SSID:        {cfg['SSID']}")
    else:
        print("Modo:        CLIENTE (AP inactivo)")
    svc = run(["systemctl", "is-active", "escama-ap.service"], capture=True)
    print(f"Service:     {(svc.stdout or '').strip()}")
    return 0


def main(args: list = None) -> int:
    if os.geteuid() != 0:
        print("Este script necesita sudo. Ejecutalo con: sudo escama ...", file=sys.stderr)
        return 1
    argv = args if args is not None else sys.argv[1:]
    action = argv[0] if len(argv) > 0 else "status"

    # global flags
    if action in ("--help", "-h", "help"):
        print(__doc__.strip())
        print("\nUso: sudo escama {start|stop|restart|status|reconnect|genconfig|edit}")
        print("  start      Levanta el AP (hostapd + dnsmasq + masquerade)")
        print("  stop       Baja el AP, restaura iface a cliente")
        print("  restart    stop + start")
        print("  status     Estado actual")
        print("  reconnect  Reconexion manual tras plug/unplug")
        print("  genconfig Regenera hostapd/dnsmasq desde escama.env")
        print("  edit       Abre escama.env en $EDITOR (nvim por defecto)")
        print("\nOpciones: --help|-h  --version|-v")
        return 0
    if action in ("--version", "-v", "version"):
        print(f"escama {VERSION}")
        return 0

    if action == "start":
        return do_start()
    elif action == "stop":
        return do_stop()
    elif action == "restart":
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "status":
        return do_status()
    elif action == "reconnect":
        # manual reconnection: ensure iface present then restart
        cfg = load_env()
        if not iface_exists(cfg["AP_IFACE"]):
            log(f"ERROR: {cfg['AP_IFACE']} no presente. Enchufa el adaptador.")
            return 1
        do_stop()
        time.sleep(1)
        return do_start()
    elif action == "genconfig":
        generate_configs(load_env())
        log("Configs generados.")
        return 0
    elif action == "edit":
        editor = os.environ.get("EDITOR", "nvim")
        os.execvp(editor, [editor, ENV_FILE])
        return 0  # unreachable
    else:
        print(f"Accion desconocida: {action}", file=sys.stderr)
        print("Uso: sudo escama {start|stop|restart|status|reconnect|genconfig|edit}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
