#!/usr/bin/env python3
"""
escama-tui.py - TUI (whiptail) para configurar escama-ap.

Edita /etc/escama/escama.toml (TOML, tomllib es stdlib) y regenera los confs
via escama.py genconfig. No duplica logica: delega en escama.py (DEFAULTS,
load_env, save_config, list_tunnels).

Uso: sudo escama-tui.py
"""
import os
import sys
import subprocess
import time
import ipaddress

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import escama

CONFIG_FILE = escama.CONFIG_FILE

import shutil

if not shutil.which("whiptail"):
    print("ERROR: whiptail no instalado. sudo apt install whiptail", file=sys.stderr)
    sys.exit(1)


def list_ifaces():
    out = []
    for d in os.listdir("/sys/class/net"):
        if d == "lo":
            continue
        if any(d.startswith(p) for p in ("docker", "veth", "br-", "tailscale", "wg", "tun", "cni")):
            continue
        out.append(d)
    return out


def whiptail_menu(title, text, items, height=18, width=70, menu_h=9):
    cmd = ["whiptail", "--clear", "--backtitle", "escama-ap",
           "--title", title, "--menu", text, str(height), str(width), str(menu_h)] + items
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        return None
    return p.stdout.strip()


def whiptail_input(title, text, init):
    cmd = ["whiptail", "--inputbox", text, "10", "70", init]
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        return None
    return p.stdout.strip()


def read_version() -> str:
    """Version desde la fuente UNICA (archivo VERSION), nunca una copia literal.

    Misma busqueda que escama.py: el directorio del script y su padre, para
    funcionar tanto desde el repo como desde /opt/escama.

    realpath, NO abspath: install.sh symlinkea /usr/local/bin/escama-tui ->
    /opt/escama/escama-tui.py, y con abspath se buscaria VERSION subiendo desde
    /usr/local/bin, donde no esta: el resultado seria "desconocido" justo en el
    comando que el usuario ejecuta.
    """
    aqui = os.path.dirname(os.path.realpath(__file__))
    d = aqui
    for _ in range(4):  # script dir + hasta 3 niveles hacia la raiz del repo
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


def _recalcular_dhcp(cfg: dict) -> None:
    """Al cambiar IP/subred, el rango DHCP debe seguir dentro de la red nueva:
    un rango de otra subred hace que dnsmasq ofrezca config inusable."""
    try:
        red = ipaddress.ip_network(cfg["AP_SUBNET"], strict=False)
        ini = ipaddress.ip_address(cfg["DHCP_START"])
        fin = ipaddress.ip_address(cfg["DHCP_END"])
    except ValueError:
        return
    if ini in red and fin in red:
        return
    base = int(red.network_address) + 10
    cfg["DHCP_START"] = str(ipaddress.ip_address(base))
    cfg["DHCP_END"] = str(ipaddress.ip_address(int(red.broadcast_address) - 1))


def main():
    if len(sys.argv) > 1 and sys.argv[1] in ("--help", "-h", "help"):
        print("escama-tui - TUI de configuracion para escama-ap")
        print("Uso: escama-tui [--help|--version]")
        print("  --help     Muestra esta ayuda")
        print("  --version  Version instalada")
        sys.exit(0)
    if len(sys.argv) > 1 and sys.argv[1] in ("--version", "-v", "version"):
        print(f"escama-tui {read_version()}")
        sys.exit(0)
    # Gate por accion (spec `uso-sin-privilegios`): --help/--version ya salie-
    # ron; el menu lee la config pero escribir TOML en /etc/escama requiere
    # privilegio, asi que el gate queda para el resto.
    if os.geteuid() != 0:
        print("Editar la configuracion necesita privilegio.\n"
              "  Ejecutalo con sudo:  sudo escama-tui\n"
              "  (--help y --version funcionan sin sudo)", file=sys.stderr)
        sys.exit(1)
    cfg = escama.load_env()
    while True:
        choice = whiptail_menu(
            "escama-ap Config",
            "Elige que configurar:",
            ["1", f"Interfaz AP: {cfg['AP_IFACE']}",
             "2", f"Interfaz WAN: {cfg['WAN_IFACE']}",
             "3", f"SSID: {cfg['SSID']}",
             "4", f"Canal: {cfg['CHANNEL']}",
             "5", f"IP/Subred AP: {cfg['AP_IP']}/{cfg['AP_CIDR']}",
             "6", f"Rango DHCP: {cfg['DHCP_START']}-{cfg['DHCP_END']}",
             "7", "Passphrase WPA2",
             "8", f"DNS: {cfg['DNS1']}, {cfg['DNS2']}",
             "9", f"Salida VPN: {cfg['EGRESS_MODE']} ({cfg['VPN_IFACE'] or 'auto-detect'})",
             "A", f"DNS con VPN: {cfg['VPN_DNS1'] or '(usa DNS normal)'}",
             "R", "Renombrar adaptador WiFi (udev)",
             "E", "EDITAR CONFIG (nvim)",
             "S", "GUARDAR Y SALIR"],
        )
        if choice is None or choice == "S":
            break
        if choice == "E":
            editor = os.environ.get("EDITOR", "nvim")
            subprocess.run([editor, CONFIG_FILE], check=False)
            cfg = escama.load_env()  # reload after external edit
            continue
        if choice == "1":
            ifaces = list_ifaces()
            items = [i for pair in [(x, x) for x in ifaces] for i in pair]
            sel = whiptail_menu("AP iface", "Elige interfaz AP:", items, 20, 60,
                                min(len(ifaces), 12))
            if sel:
                cfg["AP_IFACE"] = sel
        elif choice == "2":
            ifaces = list_ifaces()
            items = [i for pair in [(x, x) for x in ifaces] for i in pair]
            sel = whiptail_menu("WAN iface", "Elige interfaz WAN (internet):", items, 20, 60,
                                min(len(ifaces), 12))
            if sel:
                cfg["WAN_IFACE"] = sel
        elif choice == "3":
            v = whiptail_input("SSID", "Nombre de la red:", cfg["SSID"])
            if v:
                cfg["SSID"] = v
        elif choice == "4":
            v = whiptail_input("Canal", "Canal 1-11 (2.4GHz):", cfg["CHANNEL"])
            if v:
                cfg["CHANNEL"] = v
        elif choice == "5":
            v = whiptail_input("IP AP", "IP/mascara (ej 10.42.1.1/24):", f"{cfg['AP_IP']}/{cfg['AP_CIDR']}")
            if v and "/" in v:
                cfg["AP_IP"], cfg["AP_CIDR"] = v.split("/", 1)
                cfg["AP_SUBNET"] = f"{cfg['AP_IP'].rsplit('.',1)[0]}.0/{cfg['AP_CIDR']}"
                _recalcular_dhcp(cfg)
        elif choice == "6":
            v = whiptail_input("DHCP", "rango inicio-fin (ej 10.42.1.10-10.42.1.254):",
                               f"{cfg['DHCP_START']}-{cfg['DHCP_END']}")
            if v and "-" in v:
                cfg["DHCP_START"], cfg["DHCP_END"] = v.split("-", 1)
        elif choice == "7":
            v = whiptail_input("Passphrase", "WPA2 passphrase:", cfg["WPA_PASSPHRASE"])
            if v:
                cfg["WPA_PASSPHRASE"] = v
        elif choice == "8":
            v = whiptail_input("DNS", "DNS1,DNS2 (ej 8.8.8.8,8.8.4.4):",
                               f"{cfg['DNS1']},{cfg['DNS2']}")
            if v and "," in v:
                cfg["DNS1"], cfg["DNS2"] = v.split(",", 1)
        elif choice == "9":
            sel = whiptail_menu(
                "Salida de los clientes",
                "Por donde salen los clientes del AP:",
                ["auto", "VPN si hay tunnel, si no WAN (recomendado)",
                 "vpn", "Solo VPN (kill-switch: sin tunnel no hay internet)",
                 "wan", "Siempre WAN (ignora la VPN)"], 15, 74, 3)
            if sel:
                cfg["EGRESS_MODE"] = sel
            tuns = escama.list_tunnels()
            items = ["", "auto-detectar"] + [i for pair in [(t, t) for t in tuns]
                                             for i in pair]
            pick = whiptail_menu("Interfaz VPN",
                                 "Tunnel a usar (auto = detectar solo):",
                                 items, 20, 66, min(len(tuns) + 1, 12))
            if pick is not None:
                cfg["VPN_IFACE"] = pick
        elif choice == "R":
            # delega TODO en `escama rename` (validacion, udev, NM, toml):
            # la TUI no duplica logica, solo pregunta y lanza.
            wifis = [d for d in list_ifaces() if escama.iface_wifi(d)]
            if not wifis:
                subprocess.run(["whiptail", "--msgbox",
                                "No hay adaptadores WiFi presentes.",
                                "8", "50"], check=False)
            else:
                items = [i for pair in [(x, x) for x in wifis] for i in pair]
                sel = whiptail_menu("Renombrar adaptador",
                                    "Cual adaptador?", items, 15, 60,
                                    min(len(wifis), 8))
                if sel:
                    nombre = whiptail_input(
                        "Nuevo nombre",
                        "Nuevo nombre (max 15, letras/digitos/-/_).\n"
                        "Ej: wlx020304050607 -> wifi-usb:", "")
                    if nombre:
                        subprocess.run(["escama", "rename", sel, nombre],
                                       check=False)
        elif choice == "A":
            v = whiptail_input(
                "DNS con VPN",
                "DNS cuando salen por tunnel (Proton: 10.2.0.1 | WARP: 1.1.1.1)\n"
                "Vacio = usar el DNS normal:",
                f"{cfg['VPN_DNS1']},{cfg['VPN_DNS2']}" if cfg["VPN_DNS1"] else "")
            if v is not None:
                if "," in v:
                    cfg["VPN_DNS1"], cfg["VPN_DNS2"] = v.split(",", 1)
                else:
                    cfg["VPN_DNS1"] = cfg["VPN_DNS2"] = v.strip()

    escama.save_config(cfg)
    # regenerar confs
    subprocess.run(["escama", "genconfig"], check=False)
    # feedback de aplicación
    subprocess.run(["whiptail", "--infobox", "Aplicando configuracion...", "5", "50"],
                   check=False)
    time.sleep(1)
    # traer estado real para feedback
    status = subprocess.run(["escama", "status"], capture_output=True, text=True)
    subprocess.run(["whiptail", "--msgbox",
                    f"Configuracion guardada en {CONFIG_FILE}\n\n"
                    f"AP={cfg['AP_IFACE']} WAN={cfg['WAN_IFACE']} SSID={cfg['SSID']}\n\n"
                    f"Para aplicar: sudo escama restart\n\n"
                    f"--- status ---\n{(status.stdout or '').strip()}", 20, 70],
                   check=False)
    sys.exit(0)


if __name__ == "__main__":
    main()
