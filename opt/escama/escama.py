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
# Fuente UNICA de la version (spec `versionado`): el archivo VERSION de la raiz
# del repo. Se busca subiendo niveles desde el script, asi funciona igual desde
# el repo (opt/escama/ -> ../../) que instalado en /opt/escama (-> ../), donde
# install.sh deja una copia del VERSION al lado del core.
# Ningun ejecutable guarda una copia literal. Si no se encuentra, degrada a
# "desconocido": es preferible a mentir con un numero viejo.
def _read_version() -> str:
    d = os.path.dirname(os.path.abspath(__file__))
    for _ in range(4):  # script dir + hasta 3 niveles hacia la raiz
        try:
            with open(os.path.join(d, "VERSION")) as f:
                v = f.read().strip()
            if v:
                return v
        except OSError:
            pass
        padre = os.path.dirname(d)
        if padre == d:
            break
        d = padre
    return "desconocido"


VERSION = _read_version()

# --- Paths ---
CONFIG_DIR = "/etc/escama"
ENV_FILE = os.path.join(CONFIG_DIR, "escama.env")
HOSTAPD_CONF = "/etc/hostapd/hostapd-escama.conf"
DNSMASQ_CONF = "/etc/dnsmasq-escama.conf"
LOG = "/var/log/escama-ap.log"
LEASE_FILE = "/var/lib/misc/dnsmasq-escama.leases"
PIDFILE = "/run/dnsmasq-escama.pid"
STATE_FILE = "/run/escama-egress.state"

# --- Installation (spec `auto-instalacion`) ---
# Rutas de la instalacion canonica que produce install.sh. El nucleo solo las
# LEE para el preflight: jamas las escribe (la escritura es de install.sh).
INSTALL_PREFIX = "/opt/escama"
INSTALL_BIN_DIR = "/usr/local/bin"
INSTALL_UNIT_DIR = "/etc/systemd/system"
INSTALL_UNITS = ("escama-ap.service", "escama-egress.service")
INSTALL_SCRIPT = "install.sh"

# Routing table used to force client traffic into the VPN tunnel.
ESCAMA_TABLE = "51821"
# ip rule preference for the AP -> tunnel policy rule.
ESCAMA_RULE_PREF = "100"

# Known VPN/tunnel interface names, in priority order. Anything else that looks
# like a tunnel (see iface_is_tunnel) is still detected, this list only decides
# which one wins when several are up.
VPN_KNOWN = [
    "proton0",      # ProtonVPN OpenVPN / official Linux app
    "pvpn0",        # pVPN / Proton WireGuard daemons
    "protonwire0",
    "CloudflareWARP",  # warp-cli (WireGuard or MASQUE)
    "warp0",
    "nordlynx",
    "mullvad-wg",
    "wg0",
    "tun0",
    "tailscale0",
]

# Interfaces that are never a valid egress even if they look like a tunnel.
VPN_BLACKLIST = ("ipv6leakintrf0", "pvpnksintrf0", "lo")

# Defaults (overriden by env)
DEFAULTS = {
    "AP_IFACE": "wn8200nd",
    "WAN_IFACE": "stonepi",
    "SSID": "escama",
    "CHANNEL": "6",
    # auto : al start, elegir de {1,6,11} sin solape con el canal de la WAN
    #        (solo lectura); WAN no legible -> CHANNEL de arriba.
    # manual: CHANNEL tal cual (comportamiento clasico, sin deteccion).
    "CHANNEL_MODE": "auto",
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
    # --- VPN egress ---
    # auto  : si hay un tunnel VPN arriba, los clientes salen por el tunnel;
    #         si no, salen por WAN_IFACE (fallback automatico).
    # vpn   : exige tunnel; si no hay tunnel el AP NO da internet (fail-closed).
    # wan   : ignora el tunnel, siempre NAT por WAN_IFACE (comportamiento viejo).
    "EGRESS_MODE": "auto",
    # Override manual del nombre del tunnel (proton0, CloudflareWARP, wg0...).
    # Vacio = auto-deteccion.
    "VPN_IFACE": "",
    # Forzar la salida de los clientes al tunnel con policy routing aunque el
    # tunnel no sea la ruta default (necesario con warp-cli / split tunnel).
    "VPN_FORCE_ROUTE": "yes",
    # Clamp MSS a la MTU del tunnel (evita webs que cargan a medias por PMTU).
    "VPN_MSS_CLAMP": "yes",
    # Al usar tunnel, entregar estos DNS a los clientes en vez de DNS1/DNS2.
    # Vacio = usar DNS1/DNS2 tambien con VPN.
    "VPN_DNS1": "",
    "VPN_DNS2": "",
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


def iface_type_ap(iface: str) -> bool:
    """True if `iface` is currently operating as a Wi-Fi Access Point."""
    if not iface or not iface_exists(iface):
        return False
    p = run(["iw", "dev", iface, "info"], capture=True)
    return bool(p) and "type AP" in (p.stdout or "")


def iface_is_routable_wan(iface: str) -> bool:
    """True if `iface` has a default route toward the internet.
    Heuristic: `ip route show default dev <iface>` returns something with
    'via <gw>' (i.e. is a real upstream after excluding tunnels).
    """
    if not iface or not iface_exists(iface) or iface_is_tunnel(iface):
        return False
    r = run(["ip", "route", "show", "default", "dev", iface], capture=True)
    return bool(r) and "default" in (r.stdout or "")


def detect_ap_iface(cfg: dict) -> str:
    """Find which iface is currently running as the AP. Order: explicit env
    > iface holding the AP IP > iface in 'type AP' mode."""
    forced = (cfg.get("AP_IFACE") or "").strip()
    if forced and iface_exists(forced):
        return forced
    ap_ip = (cfg.get("AP_IP") or "").strip()
    if ap_ip:
        r = run(["ip", "-o", "-4", "addr", "show", "to", ap_ip],
                 capture=True)
        for line in (r.stdout or "").splitlines():
            m = re.match(r"\S+\s+(\S+)\s+", line)
            if m:
                return m.group(1)
    # fallback: any Wi-Fi iface in 'type AP' mode
    try:
        for i in sorted(os.listdir("/sys/class/net")):
            if iface_type_ap(i):
                return i
    except OSError:
        pass
    return ""


def detect_wan_iface(cfg: dict) -> str:
    """Find which iface is the WAN (internet upstream), excluding tunnels and
    the AP itself."""
    forced = (cfg.get("WAN_IFACE") or "").strip()
    if forced and iface_exists(forced) and not iface_is_tunnel(forced):
        return forced
    ap = detect_ap_iface(cfg)
    # all default routes, lowest metric first
    r = run(["ip", "route", "show", "default"], capture=True)
    candidates = []
    for line in (r.stdout or "").splitlines():
        m = re.search(r"dev (\S+)", line)
        if m:
            dev = m.group(1)
            if dev == ap or iface_is_tunnel(dev):
                continue
            metric_m = re.search(r"metric (\d+)", line)
            candidates.append((int(metric_m.group(1)) if metric_m else 0, dev))
    # lower metric = higher priority
    candidates.sort()
    for _, dev in candidates:
        if iface_exists(dev) and not iface_is_tunnel(dev) and dev != ap:
            return dev
    return ""


def _is_tty() -> bool:
    """True when stdin is connected to a terminal (user running escama
    directly), False when running under systemd without a TTY."""
    return sys.stdin and sys.stdin.isatty()


def _prompt_iface(role: str, suggestion: str, exclude: str = "") -> str:
    """Ask the user (interactively) which iface to use as `role`.
    Falls back to `suggestion` when there are no other candidates or when
    input is non-interactive (systemd)."""
    try:
        present = sorted(os.listdir("/sys/class/net"))
    except OSError:
        present = []
    # candidate ifaces: non-tunnels (except when role == "vpn"), excluding lo
    exclude_set = {exclude, "lo"} if exclude else {"lo"}
    if role == "vpn":
        options = [i for i in present if iface_is_tunnel(i)]
    else:
        options = [i for i in present
                   if i not in exclude_set
                   and not iface_is_tunnel(i)
                   and iface_exists(i)]
    if not options:
        return suggestion
    if suggestion and len(options) == 1 and options[0] == suggestion:
        return suggestion
    print(f"\nescama no pudo auto-detectar '{role}' de forma inequívoca.")
    print(f"Sugerencia: {suggestion or '(ninguna)'}")
    print("Opciones disponibles:")
    for n, i in enumerate(options, 1):
        extra = " (sugerido)" if i == suggestion else ""
        print(f"  {n}. {i}{extra}")
    if not _is_tty():
        # correr bajo systemd: no podemos preguntar, usar sugerencia
        log(f"WARN: '{role}' ambiguo y sin TTY; usando sugerencia '{suggestion}'")
        print(f"\nSin TTY interactivo: usando '{suggestion}'.")
        return suggestion
    while True:
        try:
            ans = input(f"¿Cuál es el iface {role}? [1-{len(options)} / Enter=sugerido]: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return suggestion
        if not ans:
            return suggestion
        if ans.isdigit() and 1 <= int(ans) <= len(options):
            return options[int(ans) - 1]
        if ans in options:
            return ans
        print("Selección inválida. Probá de nuevo o Enter para usar sugerido.")


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


# ---------------------------------------------------------------------------
# Seleccion de canal 2.4 GHz (evita el canal de la WAN, solo lectura)
# ---------------------------------------------------------------------------

# Canales mutuamente sin solape en 2.4 GHz con 20 MHz de ancho.
CANALES_24G = (1, 6, 11)


def detectar_canal_wan(wan: str) -> str:
    """Canal 2.4 GHz donde opera la WAN asociada. SOLO LECTURA (regla de
    oro): `iw dev <wan> link` y parseo de `freq: NNNN`. '' si la WAN no
    aporta canal legible (ethernet, 5 GHz, sin asociacion, iw ausente)."""
    if not wan or not iface_exists(wan):
        return ""
    p = run(["iw", "dev", wan, "link"], capture=True)
    if not p or p.returncode != 0:
        return ""
    m = re.search(r"freq:?\s*(\d+)", p.stdout or "")
    if not m:
        return ""
    freq = int(m.group(1))
    if freq == 2484:
        return "14"
    canal = (freq - 2407) // 5
    if 2412 <= freq <= 2472 and 1 <= canal <= 13:
        return str(canal)
    return ""


def elegir_canal(cfg: dict) -> tuple:
    """Canal del AP evitando el de la WAN. Devuelve (canal, motivo).

    CHANNEL_MODE=manual -> CHANNEL del env tal cual (sin deteccion).
    auto -> candidatos {1,6,11} a distancia >= 5 del canal de la WAN
    (sin solape de 20 MHz); gana el mas lejano, empate -> menor canal.
    Sin canal WAN legible -> CHANNEL del env (fallback seguro).
    """
    canal_env = (cfg.get("CHANNEL") or DEFAULTS["CHANNEL"]).strip()
    modo = (cfg.get("CHANNEL_MODE") or "auto").strip().lower()
    if modo == "manual":
        return canal_env, f"manual: CHANNEL={canal_env} del env"
    wan = (cfg.get("WAN_IFACE") or "").strip()
    wan_ch = detectar_canal_wan(wan)
    if not wan_ch:
        return canal_env, f"fallback: WAN sin canal legible, uso CHANNEL={canal_env}"
    wan_ch = int(wan_ch)
    seguros = [c for c in CANALES_24G if abs(c - wan_ch) >= 5]
    if not seguros:
        return canal_env, f"fallback: sin candidato seguro vs WAN canal {wan_ch}"
    elegido = max(seguros, key=lambda c: (abs(c - wan_ch), -c))
    return str(elegido), f"auto: canal {elegido} (WAN en canal {wan_ch})"


# ---------------------------------------------------------------------------
# VPN / tunnel egress
# ---------------------------------------------------------------------------

def iface_is_up(iface: str) -> bool:
    """True if the iface exists and is operationally usable."""
    if not iface or not iface_exists(iface):
        return False
    try:
        with open(f"/sys/class/net/{iface}/operstate") as f:
            state = f.read().strip()
    except OSError:
        return False
    # WireGuard/tun devices report "unknown" when up (no carrier concept).
    if state in ("up", "unknown"):
        try:
            with open(f"/sys/class/net/{iface}/flags") as f:
                flags = int(f.read().strip(), 16)
            return bool(flags & 0x1)  # IFF_UP
        except OSError:
            return True
    return False


def iface_is_tunnel(iface: str) -> bool:
    """True if iface is a VPN-ish device (wireguard, tun, ppp) or a known name."""
    if not iface or iface in VPN_BLACKLIST:
        return False
    if iface in VPN_KNOWN:
        return True
    # tun/tap devices expose tun_flags in sysfs
    if os.path.exists(f"/sys/class/net/{iface}/tun_flags"):
        return True
    # wireguard devices report their kind via `ip -d link`
    p = run(["ip", "-d", "link", "show", iface], capture=True)
    out = (p.stdout or "") if p else ""
    return "wireguard" in out or "ppp" in out or " tun " in out


def list_tunnels() -> list:
    """All tunnel-looking ifaces currently present, known names first."""
    try:
        present = sorted(os.listdir("/sys/class/net"))
    except OSError:
        return []
    tunnels = [i for i in present if iface_is_tunnel(i)]
    tunnels.sort(key=lambda i: (VPN_KNOWN.index(i) if i in VPN_KNOWN else 99, i))
    return tunnels


def detect_vpn_iface(cfg: dict) -> str:
    """Return the VPN iface to use as egress, or "" if none is usable.

    Order: explicit VPN_IFACE from env > known names that are up > any tunnel up.
    """
    forced = (cfg.get("VPN_IFACE") or "").strip()
    if forced:
        return forced if iface_is_up(forced) else ""
    for iface in list_tunnels():
        if iface_is_up(iface):
            return iface
    return ""


def iface_mtu(iface: str) -> int:
    try:
        with open(f"/sys/class/net/{iface}/mtu") as f:
            return int(f.read().strip())
    except (OSError, ValueError):
        return 1500


def iface_gateway(iface: str) -> str:
    """Default gateway advertised on `iface` (via <gw>), or "" if none/P2P."""
    r = run(["ip", "route", "show", "dev", iface], capture=True)
    for line in (r.stdout or "").splitlines():
        if line.startswith("default"):
            m = re.search(r"via (\S+)", line)
            if m:
                return m.group(1)
    return ""


def iface_addr(iface: str) -> str:
    """Primary IPv4 address of `iface`, or "" if none assigned."""
    r = run(["ip", "-o", "-4", "addr", "show", "dev", iface], capture=True)
    for line in (r.stdout or "").splitlines():
        m = re.search(r"inet (\S+)", line)
        if m:
            return m.group(1).split("/")[0]
    return ""


def resolve_egress(cfg: dict) -> tuple:
    """Decide where client traffic must exit.

    Returns (iface, kind) with kind in {"vpn", "wan", "none"}.
    """
    mode = (cfg.get("EGRESS_MODE") or "auto").strip().lower()
    wan = cfg.get("WAN_IFACE") or ""
    if mode == "wan":
        return (wan, "wan") if wan else ("", "none")
    vpn = detect_vpn_iface(cfg)
    if mode == "vpn":
        # fail-closed: sin tunnel no hay internet para los clientes
        return (vpn, "vpn") if vpn else ("", "none")
    # auto: tunnel si existe, si no fallback a WAN
    if vpn:
        return vpn, "vpn"
    return (wan, "wan") if wan else ("", "none")


def _read_state() -> dict:
    st = {}
    try:
        with open(STATE_FILE) as f:
            for line in f:
                if "=" in line:
                    k, v = line.strip().split("=", 1)
                    st[k] = v
    except OSError:
        pass
    return st


def _write_state(**kw) -> None:
    try:
        os.makedirs(os.path.dirname(STATE_FILE) or ".", exist_ok=True)
        with open(STATE_FILE, "w") as f:
            for k, v in kw.items():
                f.write(f"{k}={v}\n")
    except OSError:
        pass


def _clear_state() -> None:
    try:
        os.remove(STATE_FILE)
    except OSError:
        pass


def clear_egress(cfg: dict, egress: str = "", kind: str = "") -> None:
    """Remove every NAT/forward/policy rule escama may have installed.

    Idempotent: uses the state file when available, and also tries the
    previously known WAN so upgrades from older versions clean up too.
    """
    st = _read_state()
    egress = egress or st.get("EGRESS", "")
    kind = kind or st.get("KIND", "")
    subnet = cfg["AP_SUBNET"]
    ap = cfg["AP_IFACE"]

    candidates = {c for c in (egress, cfg.get("WAN_IFACE") or "") if c}
    for out in candidates:
        # delete repeatedly: older runs may have stacked duplicates
        for _ in range(3):
            r = run(["iptables", "-t", "nat", "-D", "POSTROUTING",
                     "-o", out, "-s", subnet, "-j", "MASQUERADE"], check=False)
            if not r or r.returncode != 0:
                break
        run(["iptables", "-D", "FORWARD", "-i", ap, "-o", out,
             "-s", subnet, "-j", "ACCEPT"], check=False)
        run(["iptables", "-D", "FORWARD", "-i", out, "-o", ap,
             "-m", "conntrack", "--ctstate", "ESTABLISHED,RELATED",
             "-j", "ACCEPT"], check=False)
        run(["iptables", "-t", "mangle", "-D", "FORWARD", "-o", out,
             "-p", "tcp", "--tcp-flags", "SYN,RST", "SYN",
             "-j", "TCPMSS", "--clamp-mss-to-pmtu"], check=False)

    # kill-switch rule (fail-closed): drop AP traffic leaving via WAN
    wan = cfg.get("WAN_IFACE") or ""
    if wan:
        for _ in range(3):
            r = run(["iptables", "-D", "FORWARD", "-i", ap, "-o", wan,
                     "-s", subnet, "-j", "REJECT"], check=False)
            if not r or r.returncode != 0:
                break

    # policy routing
    for _ in range(3):
        # remove the AP-ingress rule (escama.py:537-538 uses `iif <ap>`);
        # see docs/diagnostics/DIAGNOSIS-FINAL.md §4.1 — previously `from <subnet>`, which also
        # caught host-origin traffic from the AP IP and hijacked it into the
        # tunnel.
        r = run(["ip", "rule", "del", "iif", ap, "lookup", ESCAMA_TABLE],
                check=False)
        if not r or r.returncode != 0:
            break
    run(["ip", "route", "flush", "table", ESCAMA_TABLE], check=False)
    _clear_state()


def apply_egress(cfg: dict, egress: str, kind: str) -> None:
    """Install forwarding + NAT (+ policy routing / MSS clamp) toward `egress`."""
    subnet = cfg["AP_SUBNET"]
    ap = cfg["AP_IFACE"]
    wan = cfg.get("WAN_IFACE") or ""

    clear_egress(cfg)
    run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)

    if not egress:
        # fail-closed: sin salida valida, no dejamos fugar por WAN
        if wan:
            run(["iptables", "-A", "FORWARD", "-i", ap, "-o", wan,
                 "-s", subnet, "-j", "REJECT"], check=False)
        _write_state(EGRESS="", KIND="none")
        log("WARN: sin egress valido; clientes SIN internet (fail-closed)")
        return

    # NAT + forward
    run(["iptables", "-t", "nat", "-A", "POSTROUTING",
         "-o", egress, "-s", subnet, "-j", "MASQUERADE"], check=False)
    run(["iptables", "-A", "FORWARD", "-i", ap, "-o", egress,
         "-s", subnet, "-j", "ACCEPT"], check=False)
    run(["iptables", "-A", "FORWARD", "-i", egress, "-o", ap,
         "-m", "conntrack", "--ctstate", "ESTABLISHED,RELATED",
         "-j", "ACCEPT"], check=False)

    if kind == "vpn":
        # rp_filter loose: el retorno entra por el tunnel, no por WAN
        run(["sysctl", "-w", "net.ipv4.conf.all.rp_filter=2"], check=False)
        run(["sysctl", "-w", f"net.ipv4.conf.{ap}.rp_filter=2"], check=False)

        if _yes(cfg.get("VPN_MSS_CLAMP", "yes")):
            run(["iptables", "-t", "mangle", "-A", "FORWARD", "-o", egress,
                 "-p", "tcp", "--tcp-flags", "SYN,RST", "SYN",
                 "-j", "TCPMSS", "--clamp-mss-to-pmtu"], check=False)

        if _yes(cfg.get("VPN_FORCE_ROUTE", "yes")):
            # tabla dedicada: TODO lo que venga del subnet del AP sale por el
            # tunnel, aunque la default del host siga apuntando a la WAN
            # (caso warp-cli / split-tunnel / kill switch con fwmark).
            #
            # Es IMPRESCINDIBLE declarar via <gw> y src <ip> en la ruta default
            # de la tabla dedicada. Con solo "default dev tun0 scope link" el
            # kernel responde "Network is unreachable" para cualquier source
            # que no sea una IP del propio tun0 (caso 10.42.1.x del AP): el
            # paquete nunca llega al POSTROUTING donde MASQUERADE lo reescribe
            # -> los clientes se quedan sin internet aunque las reglas NAT
            # esten perfectas. La via le dice al kernel como alcanzar el
            # siguiente salto; la src le da una IP valida para el paquete
            # saliente (MASQUERADE la reescribe despues por la IP del tun0).
            gw = iface_gateway(egress)
            src = iface_addr(egress)
            run(["ip", "route", "flush", "table", ESCAMA_TABLE], check=False)
            # orden ip route: add default [via <gw>] dev <iface> [src <ip>]
            # table <id>. Sin via, el kernel declara "Network unreachable"
            # para paquetes con source fuera del subnet del tunnel (caso
            # AP 10.42.1.x -> tun0): el MASQUERADE nunca llega a correr.
            cmd = ["ip", "route", "add", "default"]
            if gw:
                cmd += ["via", gw]
            cmd += ["dev", egress]
            if src:
                cmd += ["src", src]
            cmd += ["table", ESCAMA_TABLE]
            run(cmd, check=False)
            # Match on the AP INGRESS interface, NOT the source subnet.
            # A `from <subnet>` selector also catches host-originated packets
            # from the AP IP (10.42.1.1), hijacking host->client scans into the
            # tunnel (see docs/diagnostics/DIAGNOSIS-FINAL.md §1 / §4.1). `iif <ap>` only matches
            # forwarded client ingress, so host-origin traffic uses the main
            # table and reaches clients directly.
            run(["ip", "rule", "add", "iif", ap, "lookup", ESCAMA_TABLE,
                 "pref", ESCAMA_RULE_PREF], check=False)

        # kill-switch: nada del AP puede escaparse por la WAN en claro
        if wan and wan != egress:
            run(["iptables", "-A", "FORWARD", "-i", ap, "-o", wan,
                 "-s", subnet, "-j", "REJECT"], check=False)

    _write_state(EGRESS=egress, KIND=kind, AP=ap, SUBNET=subnet, WAN=wan)
    log(f"Egress aplicado: {egress} (modo={kind}, mtu={iface_mtu(egress)})")


def _yes(v) -> bool:
    return str(v).strip().lower() in ("1", "yes", "y", "true", "on", "si", "sí")


def effective_dns(cfg: dict, kind: str) -> tuple:
    """DNS handed to clients: VPN_DNS* when tunneled and set, else DNS1/DNS2."""
    if kind == "vpn":
        d1 = (cfg.get("VPN_DNS1") or "").strip()
        d2 = (cfg.get("VPN_DNS2") or "").strip()
        if d1:
            return d1, (d2 or d1)
    return cfg["DNS1"], cfg["DNS2"]


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


def generar_hostapd(cfg: dict) -> None:
    """Genera hostapd-escama.conf desde el env (cfg['CHANNEL'] ya resuelto)."""
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
    os.makedirs(os.path.dirname(HOSTAPD_CONF), exist_ok=True)
    with open(HOSTAPD_CONF, "w") as f:
        f.write(hostapd)


def generar_dnsmasq(cfg: dict, kind: str = "") -> None:
    """Genera dnsmasq-escama.conf (DNS/MTU de clientes segun egress)."""
    dns1, dns2 = effective_dns(cfg, kind)
    dnsmasq = f"""interface={cfg['AP_IFACE']}
bind-interfaces
dhcp-range={cfg['DHCP_START']},{cfg['DHCP_END']},255.255.255.0,{cfg['DHCP_LEASE']}
dhcp-option=option:router,{cfg['AP_IP']}
dhcp-option=option:dns-server,{dns1},{dns2}
dhcp-leasefile={LEASE_FILE}
"""
    if kind == "vpn":
        egress = _read_state().get("EGRESS", "") or detect_vpn_iface(cfg)
        if egress:
            mtu = iface_mtu(egress)
            if 0 < mtu < 1500:
                # los clientes negocian MTU del tunnel -> nada de PMTU roto
                dnsmasq += f"dhcp-option=option:mtu,{mtu}\n"
    with open(DNSMASQ_CONF, "w") as f:
        f.write(dnsmasq)


def generate_configs(cfg: dict, kind: str = "") -> None:
    """Single source of truth: env -> hostapd + dnsmasq confs (ambos).

    Solo para `genconfig` y arranques: reescribe AMBOS confs. El watcher
    de egress NO debe usar esto (regeneraria hostapd con canal obsoleto);
    que use generar_dnsmasq() a solas.
    """
    generar_hostapd(cfg)
    generar_dnsmasq(cfg, kind)
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
    # --- Auto-detección de roles AP/WAN ---
    # La regla es: el env explicito gana. Si el iface explicito NO existe
    # (o es un tunnel) caemos a detección. Si detectar solo es ambiguo y hay
    # TTY, preguntamos al usuario. Sin TTY (systemd) usamos la sugerencia.
    ap_env = (cfg.get("AP_IFACE") or "").strip()
    if ap_env and iface_exists(ap_env) and not iface_is_tunnel(ap_env):
        ap = ap_env
    else:
        ap_suggested = detect_ap_iface(cfg)
        if ap_suggested:
            # detección inequívoca: usarla
            ap = ap_suggested
        else:
            # ni el env era valido ni pudimos detectar: mantener env (para
            # preservar el mensaje de error original "enchufa el adaptador")
            ap = ap_env or DEFAULTS["AP_IFACE"]
            # última posibilidad: preguntar al usuario si hay TTY
            ap = _prompt_iface("AP", ap)
        cfg["AP_IFACE"] = ap
        if ap_env and ap != ap_env:
            log(f"AVISO: AP_IFACE del env='{ap_env}' no era valido, "
                f"usando detectado='{ap}'")

    wan = detect_wan_iface(cfg)
    if not wan:
        wan_suggested = cfg.get("WAN_IFACE") or ""
        wan = _prompt_iface("WAN", wan_suggested, exclude=ap)
    cfg["WAN_IFACE"] = wan
    log(f"Roles: AP={ap}  WAN={wan}")

    if not iface_exists(ap):
        log(f"ERROR: AP iface {ap} no existe. Enchufa el adaptador.")
        return 1
    if not iface_exists(wan):
        log(f"WARN: WAN iface {wan} no existe. El AP no tendra internet saliente.")

    # free iface from NM (AP iface only)
    run(["nmcli", "device", "set", ap, "managed", "no"], check=False)
    # reload module if AP mode missing (anti -95)
    reload_module_if_needed(ap)

    # decide egress BEFORE generating confs (DNS/MTU dependen del tunnel)
    egress, kind = resolve_egress(cfg)
    # canal: evitar el de la WAN (CHANNEL_MODE=auto) o CHANNEL del env (manual)
    canal, motivo = elegir_canal(cfg)
    cfg["CHANNEL"] = canal
    log(f"Canal AP: {canal} ({motivo})")
    generar_hostapd(cfg)
    generar_dnsmasq(cfg, kind)
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

    # forward + masquerade hacia el egress elegido (VPN o WAN)
    if kind == "vpn":
        log(f"VPN detectada: {egress} -> clientes saldran por el tunnel")
    elif kind == "wan":
        log(f"Sin VPN activa: clientes saldran por WAN {egress}")
    apply_egress(cfg, egress, kind)

    # validate for real
    p = run(["iw", "dev", ap, "info"], capture=True)
    if p.returncode == 0 and "type AP" in (p.stdout or ""):
        log(f"OK: AP activo en {ap} ({cfg['AP_IP']}/{cfg['AP_CIDR']}, ssid={cfg['SSID']})")
        if kind == "vpn":
            log(f"OK: egress por VPN {egress} (kill-switch: sin fuga por {wan})")
        elif wan_has_internet(wan):
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
    clear_egress(cfg)
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
    egress, kind = resolve_egress(cfg)
    st = _read_state()
    tunnels = [t for t in list_tunnels() if iface_is_up(t)]
    print(f"Egress mode: {cfg.get('EGRESS_MODE', 'auto')}")
    print(f"Tunnels up:  {', '.join(tunnels) if tunnels else '(ninguno)'}")
    if kind == "vpn":
        print(f"Salida:      VPN {egress} (mtu {iface_mtu(egress)})")
    elif kind == "wan":
        print(f"Salida:      WAN {egress} (sin VPN)")
    else:
        print("Salida:      NINGUNA (fail-closed, clientes sin internet)")
    applied = st.get("EGRESS")
    if applied is not None and applied != egress:
        print(f"AVISO:       reglas aplicadas apuntan a '{applied or '(ninguna)'}'"
              f" != salida actual '{egress or '(ninguna)'}'."
              " Corre: sudo escama egress")
    svc = run(["systemctl", "is-active", "escama-ap.service"], capture=True)
    print(f"Service:     {(svc.stdout or '').strip()}")
    return 0


def do_egress(args: list = None) -> int:
    """Re-evaluate egress and re-apply NAT rules WITHOUT dropping the AP.

    Uso: escama egress [auto|vpn|wan|<iface>]
    Pensado para correr cuando conectas/desconectas ProtonVPN o warp-cli:
    los clientes no pierden la asociacion WiFi, solo cambia por donde salen.
    """
    cfg = load_env()
    args = args or []
    if args:
        sel = args[0].strip().lower()
        if sel in ("auto", "vpn", "wan"):
            cfg["EGRESS_MODE"] = sel
        else:
            cfg["EGRESS_MODE"] = "vpn"
            cfg["VPN_IFACE"] = args[0].strip()
    if not cfg.get("WAN_IFACE"):
        cfg["WAN_IFACE"] = detect_wan_iface(cfg)
    egress, kind = resolve_egress(cfg)
    apply_egress(cfg, egress, kind)
    # DNS/MTU de los clientes cambian con el tunnel -> regenerar SOLO dnsmasq.
    # hostapd no se toca: el canal del AP debe quedar estable en vivo.
    generar_dnsmasq(cfg, kind)
    run(["pkill", "-HUP", "-x", "dnsmasq"], check=False)
    return 0 if egress else 1


def do_watch(interval: int = 5) -> int:
    """Daemon loop: follow VPN up/down and swap egress on the fly."""
    cfg = load_env()
    log(f"watch: vigilando tunnels cada {interval}s "
        f"(modo={cfg.get('EGRESS_MODE', 'auto')})")
    last = None
    while True:
        cfg = load_env()
        if not cfg.get("WAN_IFACE"):
            cfg["WAN_IFACE"] = detect_wan_iface(cfg)
        egress, kind = resolve_egress(cfg)
        if (egress, kind) != last:
            log(f"watch: cambio de salida -> {egress or '(ninguna)'} ({kind})")
            apply_egress(cfg, egress, kind)
            # solo dnsmasq: NUNCA regenerar hostapd aqui (canal estable)
            generar_dnsmasq(cfg, kind)
            run(["pkill", "-HUP", "-x", "dnsmasq"], check=False)
            last = (egress, kind)
        time.sleep(interval)


# ---------------------------------------------------------------------------
# Preflight y auto-instalacion (spec `auto-instalacion`)
# ---------------------------------------------------------------------------

def _version_instalada() -> str:
    """Version de la copia instalada, o "" si no se puede leer."""
    try:
        with open(os.path.join(INSTALL_PREFIX, "VERSION")) as f:
            return f.read().strip()
    except OSError:
        return ""


def _repo_root() -> str:
    d = os.path.dirname(os.path.abspath(__file__))
    for _ in range(4):
        if os.path.isfile(os.path.join(d, "VERSION")):
            return d
        padre = os.path.dirname(d)
        if padre == d:
            break
        d = padre
    return ""


def _codigo_difiere() -> bool:
    """True si el core instalado no es identico al del repo."""
    repo = _repo_root()
    if not repo:
        return False
    try:
        with open(os.path.join(repo, "opt", "escama", "escama.py")) as f:
            a = f.read()
        with open(os.path.join(INSTALL_PREFIX, "escama.py")) as f:
            b = f.read()
    except OSError:
        return False
    return a != b


def preflight() -> dict:
    """Clasifica la instalacion sin modificarla (spec `auto-instalacion`).

    Estados: `completa`, `desactualizada`, `faltante`. Incluye el detalle de
    cada componente para que el mensaje sea accionable.
    """
    comps = {}
    for b in ("escama", "escama-tui"):
        comps[f"comando {b}"] = os.path.lexists(os.path.join(INSTALL_BIN_DIR, b))
    comps[f"core {INSTALL_PREFIX}/escama.py"] = os.path.isfile(
        os.path.join(INSTALL_PREFIX, "escama.py"))
    comps["config /etc/escama/escama.env"] = os.path.isfile(ENV_FILE)
    for u in INSTALL_UNITS:
        comps[f"unit {u}"] = os.path.isfile(os.path.join(INSTALL_UNIT_DIR, u))

    faltan = [k for k, ok in comps.items() if not ok]
    ver_inst = _version_instalada()
    desactualizada = bool(ver_inst) and (ver_inst != VERSION or _codigo_difiere())

    if faltan:
        estado = "faltante"
    elif desactualizada:
        estado = "desactualizada"
    else:
        estado = "completa"
    return {
        "estado": estado,
        "componentes": comps,
        "faltan": faltan,
        "version_repo": VERSION,
        "version_instalada": ver_inst or "(ninguna)",
    }


def do_preflight() -> int:
    """Reporte de preflight. Solo lectura: no pide privilegio ni cambia nada."""
    p = preflight()
    print("=== escama preflight ===")
    for k, ok in p["componentes"].items():
        print(f"  [{'ok' if ok else 'FALTA'}] {k}")
    print(f"Version repo:       {p['version_repo']}")
    print(f"Version instalada:  {p['version_instalada']}")
    print(f"Estado:             {p['estado']}")
    if p["estado"] == "faltante":
        print("\nFalta la instalacion. Para instalarla:")
        print(f"  sudo {INSTALL_SCRIPT} install")
    elif p["estado"] == "desactualizada":
        print("\nLa instalacion esta desactualizada respecto del repo. Para actualizarla:")
        print(f"  sudo {INSTALL_SCRIPT} install")
    return 0


def _bootstrap_instalacion() -> bool:
    """Delega la instalacion en install.sh (unica implementacion) con un prompt.

    True si la instalacion quedo lista; False si el usuario rechazo o fallo.
    """
    repo = _repo_root()
    script = os.path.join(repo, INSTALL_SCRIPT) if repo else INSTALL_SCRIPT
    print("escama no esta instalado en esta maquina.")
    print(f"  Comandos faltantes: {', '.join(preflight()['faltan'])}")
    if not os.path.isfile(script):
        print(f"\nNo encuentro {INSTALL_SCRIPT}. Instalalo manualmente y reintenta.",
              file=sys.stderr)
        return False
    if not _is_tty():
        print(f"\nSin terminal interactivo: no puedo preguntar. Instala con:\n"
              f"  sudo {script} install", file=sys.stderr)
        return False
    try:
        r = input("¿Instalo ahora? [s/N]: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return False
    if r not in ("s", "si", "sí", "y", "yes"):
        print(f"Cancelado. Instala manualmente con:\n  sudo {script} install")
        return False
    # Un unico prompt de privilegio: install.sh hace el resto con su propio sudo
    # (sudo cachea la credencial, asi que no vuelve a pedirla).
    p = run(["bash", script, "install"], check=False, capture=True)
    if p is None or p.returncode != 0:
        print("ERROR: la instalacion fallo. Instalalo manualmente con:\n"
              f"  sudo {script} install", file=sys.stderr)
        return False
    post = preflight()
    if post["estado"] == "faltante":
        print("ERROR: la instalacion quedo incompleta.", file=sys.stderr)
        return False
    print(f"Instalacion completa (estado: {post['estado']}).")
    return True


# --- Gate de privilegio (spec `uso-sin-privilegios`) ---
# El gate NO es global: las acciones de solo lectura corren sin privilegio y las
# que mutan el sistema requieren root o el launcher rootless (fase 2 del change).
ACCIONES_SIN_PRIVILEGIO = ("status", "--help", "-h", "help", "--version", "-v",
                          "version", "preflight")
ACCIONES_CON_BOOTSTRAP = ("start", "stop", "restart", "reconnect", "genconfig",
                          "egress", "watch")


def main(args: list = None) -> int:
    argv = args if args is not None else sys.argv[1:]
    action = argv[0] if len(argv) > 0 else "status"

    # Auto-instalacion (spec `auto-instalacion`): antes de una accion que muta el
    # sistema, si falta la instalacion se ofrece completarla. Sin TTY no se
    # pregunta: se imprime el comando y se sigue (el servicio puede estar bien
    # instalado y ser la invocacion local la que llego antes).
    if action in ACCIONES_CON_BOOTSTRAP:
        p = preflight()
        if p["estado"] == "faltante" and not _bootstrap_instalacion():
            return 1

    # Solo lectura: nunca pide privilegio, ni siquiera para imprimirse.
    if action not in ACCIONES_SIN_PRIVILEGIO and os.geteuid() != 0:
        # Modo rootless (escama-launch con capabilities) todavia no implementado:
        # se implementa en la fase 2 del change. Mientras tanto se pide privilegio,
        # con un mensaje que explica el camino rootless disponible.
        print("Esta accion modifica el sistema y necesita privilegio.\n"
              "  Ejecutala con sudo:  sudo escama " + " ".join(argv) + "\n"
              "  (el modo rootless sin sudo llega con la fase 2 del change "
              "arranque-sin-friccion)", file=sys.stderr)
        return 1

    # global flags
    if action in ("--help", "-h", "help"):
        print(__doc__.strip())
        print("\nUso: sudo escama {start|stop|restart|status|reconnect|genconfig|egress|watch|edit}")
        print("  start      Levanta el AP (hostapd + dnsmasq + masquerade)")
        print("  stop       Baja el AP, restaura iface a cliente")
        print("  restart    stop + start")
        print("  status     Estado actual")
        print("  reconnect  Reconexion manual tras plug/unplug")
        print("  genconfig Regenera hostapd/dnsmasq desde escama.env")
        print("  egress     Re-evalua la salida (VPN/WAN) sin tirar el AP")
        print("             uso: escama egress [auto|vpn|wan|<iface>]")
        print("  watch      Loop que sigue el estado del tunnel y reaplica NAT")
        print("  edit       Abre escama.env en $EDITOR (nvim por defecto)")
        print("  preflight  Estado de la instalacion (solo lectura, sin sudo)")
        print("\nOpciones: --help|-h  --version|-v")
        print("\nSin sudo: status, preflight, --help y --version.")
        print("Con sudo (o rootless): start, stop, restart, reconnect,")
        print("genconfig, egress, watch.")
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
        cfg = load_env()
        _, kind = resolve_egress(cfg)
        generate_configs(cfg, kind)
        log("Configs generados.")
        return 0
    elif action == "egress":
        return do_egress(argv[1:])
    elif action == "watch":
        try:
            interval = int(argv[1]) if len(argv) > 1 else 5
        except ValueError:
            interval = 5
        return do_watch(interval)
    elif action == "preflight":
        return do_preflight()
    elif action == "edit":
        editor = os.environ.get("EDITOR", "nvim")
        os.execvp(editor, [editor, ENV_FILE])
        return 0  # unreachable
    else:
        print(f"Accion desconocida: {action}", file=sys.stderr)
        print("Uso: sudo escama {start|stop|restart|status|reconnect|genconfig|egress|watch|edit}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
