#!/usr/bin/env python3
"""
escama-tui.py - TUI (whiptail) para configurar escama-ap.

Edita /etc/escama/escama.env y regenera los confs via escama.py genconfig.
No duplica logica: delega en escama.py.

Uso: sudo escama-tui.py
"""
import os
import sys
import subprocess
import time

ENV_FILE = "/etc/escama/escama.env"
WHIPTAIL = shutil_whiptail = "/usr/bin/whiptail"

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

import shutil

if not shutil.which("whiptail"):
    print("ERROR: whiptail no instalado. sudo apt install whiptail", file=sys.stderr)
    sys.exit(1)


def load_env():
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


def save_env(cfg):
    os.makedirs(os.path.dirname(ENV_FILE), exist_ok=True)
    with open(ENV_FILE, "w") as f:
        f.write("# escama.env - config central de escama-ap\n")
        f.write("# Editar aqui. Los confs se regeneran con: sudo escama.py genconfig\n\n")
        for k in DEFAULTS:
            f.write(f'{k}="{cfg[k]}"\n')
        f.write('\n# WAN override opcional (dejar vacio = auto-detecta ruta default)\n')
        f.write(f'WAN_IFACE="{cfg["WAN_IFACE"]}"\n')


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


def main():
    if len(sys.argv) > 1 and sys.argv[1] in ("--help", "-h", "help"):
        print("escama-tui - TUI de configuracion para escama-ap")
        print("Uso: sudo escama-tui [--help|--version]")
        print("  --help     Muestra esta ayuda")
        print("  --version  Version instalada")
        sys.exit(0)
    if len(sys.argv) > 1 and sys.argv[1] in ("--version", "-v", "version"):
        print("escama-tui 1.0.0")
        sys.exit(0)
    if os.geteuid() != 0:
        print("Necesita sudo: sudo escama-tui", file=sys.stderr)
        sys.exit(1)
    cfg = load_env()
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
             "E", "EDITAR CONFIG (nvim)",
             "S", "GUARDAR Y SALIR"],
        )
        if choice is None or choice == "S":
            break
        if choice == "E":
            editor = os.environ.get("EDITOR", "nvim")
            subprocess.run([editor, ENV_FILE], check=False)
            cfg = load_env()  # reload after external edit
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

    save_env(cfg)
    # regenerar confs
    subprocess.run(["escama", "genconfig"], check=False)
    # feedback de aplicación
    subprocess.run(["whiptail", "--infobox", "Aplicando configuracion...", "5", "50"],
                   check=False)
    time.sleep(1)
    # traer estado real para feedback
    status = subprocess.run(["escama", "status"], capture_output=True, text=True)
    subprocess.run(["whiptail", "--msgbox",
                    f"Configuracion guardada en {ENV_FILE}\n\n"
                    f"AP={cfg['AP_IFACE']} WAN={cfg['WAN_IFACE']} SSID={cfg['SSID']}\n\n"
                    f"Para aplicar: sudo escama restart\n\n"
                    f"--- status ---\n{(status.stdout or '').strip()}", 20, 70],
                   check=False)
    sys.exit(0)


if __name__ == "__main__":
    main()
