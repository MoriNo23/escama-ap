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
import tempfile
import time
import ipaddress

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import escama

CONFIG_FILE = escama.CONFIG_FILE

import shutil


def list_ifaces():
    out = []
    for d in os.listdir("/sys/class/net"):
        if d == "lo":
            continue
        if any(d.startswith(p) for p in ("docker", "veth", "br-", "tailscale", "wg", "tun", "cni")):
            continue
        out.append(d)
    return out


def whiptail_menu(title, text, items, height=18, width=70, menu_h=9,
                  default=None):
    cmd = ["whiptail", "--clear", "--backtitle", "escama-ap"]
    if default:
        cmd += ["--default-item", str(default)]
    cmd += ["--title", title, "--menu", text, str(height), str(width),
            str(menu_h)] + items
    # whiptail dibuja en stdout (heredado) y escribe la respuesta en stderr.
    p = subprocess.run(cmd, text=True, stderr=subprocess.PIPE)
    if p.returncode != 0:
        return None
    return (getattr(p, "stderr", "") or "").strip()


def whiptail_input(title, text, init):
    cmd = ["whiptail", "--inputbox", text, "10", "70", init]
    # whiptail dibuja en stdout (heredado) y escribe la respuesta en stderr.
    p = subprocess.run(cmd, text=True, stderr=subprocess.PIPE)
    if p.returncode != 0:
        return None
    return (getattr(p, "stderr", "") or "").strip()


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


WAN_AUTO = "AUTO"


def elegir_wan(cfg: dict) -> str:
    """Devuelve el nuevo WAN_IFACE; AUTO significa autodeteccion ('')."""
    ifaces = list_ifaces()
    items = [WAN_AUTO, "Detectar internet automaticamente"]
    for iface in ifaces:
        items += [iface, iface]
    actual = cfg.get("WAN_IFACE") or WAN_AUTO
    sel = whiptail_menu("WAN iface", "Elige interfaz WAN (internet):", items,
                        21, 66, min(len(ifaces) + 1, 12), default=actual)
    if sel is None:
        return cfg.get("WAN_IFACE", "")
    return "" if sel == WAN_AUTO else sel


def aplicar_cambio_wan(antes: str, despues: str) -> tuple:
    """Reaplica la salida en caliente solo si WAN_IFACE cambio."""
    if antes == despues:
        return True, ""
    p = subprocess.run(["escama", "egress"], capture_output=True, text=True,
                       check=False)
    salida = ((p.stdout or "") + (p.stderr or "")).strip()
    return p.returncode == 0, salida


def texto_guardado(cfg: dict, cambio_wan: bool, ok_egress: bool,
                   salida_egress: str, salida_status: str) -> str:
    lineas = [f"Configuracion guardada en {CONFIG_FILE}", "",
              f"AP={cfg['AP_IFACE']} WAN={cfg['WAN_IFACE'] or 'AUTO'} "
              f"SSID={cfg['SSID']}"]
    if cambio_wan:
        if ok_egress:
            lineas += ["", "Salida reaplicada sin reiniciar el AP.",
                       salida_egress or "(sin salida)"]
        else:
            lineas += ["", "Configuracion guardada, pero la salida NO se aplico.",
                       "Aplicá a mano con: sudo escama egress",
                       salida_egress or "(sin salida)"]
    else:
        lineas += ["", "Para aplicar cambios de red: sudo escama restart"]
    lineas += ["", "--- status ---", salida_status]
    return "\n".join(lineas)


def construir_menu(estado: dict) -> tuple:
    """Menú principal contextual: estado real, acciones válidas y sugerencia."""
    texto = (f"AP {estado['ap']} ({estado['ip']}) - "
             f"{'ACTIVO' if estado['up'] else 'INACTIVO'}\n"
             f"WAN {estado['wan']} | salida {estado['kind']} "
             f"{estado['egress'] or '(ninguna)'} | modo {estado['modo']}\n"
             f"SSID: {estado['ssid']}")
    items = [
        "1", "Arrancar AP" if not estado["up"] else "Parar AP",
        "2", "Ver estado",
        "3", "QR para el telefono",
        "4", "Cambiar salida (VPN/WAN)",
        "5", "Preflight de la maquina",
        "C", "Configurar SSID, interfaces, canal, passphrase...",
        "R", "Renombrar adaptador WiFi",
        "E", "Editar TOML en $EDITOR",
        "X", "Salir (sin guardar cambios)",
    ]
    return texto, items, "1" if not estado["up"] else "2"


def accion_rapida(choice: str, estado: dict) -> None:
    """Delega la acción en el subcomando de escama y muestra el resultado real."""
    comandos = {
        "1": ["escama", "start" if not estado["up"] else "stop"],
        "2": ["escama", "status"],
        "3": ["escama", "qr"],
        "4": ["escama", "egress"],
        "5": ["escama", "preflight"],
    }
    cmd = comandos.get(choice)
    if not cmd:
        return
    p = subprocess.run(cmd, capture_output=True, text=True, check=False)
    salida = ((p.stdout or "") + (p.stderr or "")).strip() or "Accion terminada."
    subprocess.run(["whiptail", "--msgbox", salida[-2000:], "20", "74"],
                   check=False)


def guardar_config(cfg: dict) -> bool:
    """Escribe el TOML con privilegio suficiente; si no puede, lo dice.

    Sin root, `save_config` trabaja sobre un temporal (conserva comentarios) y
    `sudo -n install` lo coloca en su sitio. Sin sudo silencioso no se toca el
    archivo del usuario y se devuelve False para no anunciar éxito falso.
    """
    destino = escama.CONFIG_FILE
    if os.geteuid() == 0:
        escama.save_config(cfg)
        return True
    temporal = os.path.join(tempfile.gettempdir(),
                            f"escama-toml-{os.getpid()}.toml")
    try:
        escama.CONFIG_FILE = temporal
        escama.save_config(cfg)
    finally:
        escama.CONFIG_FILE = destino
    try:
        p = subprocess.run(["sudo", "-n", "install", "-m", "644",
                            temporal, destino], check=False)
    except OSError:
        p = None
    if p is None or p.returncode != 0:
        subprocess.run(["whiptail", "--msgbox",
                        "No pude escribir la configuracion sin privilegio.\n"
                        "El archivo quedo sin cambios. Guardalo con:\n"
                        f"  sudo escama-tui\n"
                        "o copiá el temporal a mano.", "10", "60"],
                       check=False)
        return False
    return True


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
    if not shutil.which("whiptail"):
        print("ERROR: whiptail no instalado. sudo apt install whiptail",
              file=sys.stderr)
        return escama.do_status()
    # Navegacion y consultas sin privilegio (spec `uso-sin-privilegios`).
    # Solo guardar exige root: guardar_config() delega o degrada explicitamente.
    cfg = escama.load_env()
    wan_inicial = cfg["WAN_IFACE"]
    salir_sin_guardar = False
    while True:
        estado = escama.estado_escama(cfg)
        texto, items, sugerido = construir_menu(estado)
        principal = whiptail_menu("escama-ap", texto, items, 21, 74, 13,
                                  default=sugerido)
        if principal is None or principal == "X":
            salir_sin_guardar = True
            break
        if principal in ("R", "E"):
            choice = principal
        elif principal != "C":
            accion_rapida(principal, estado)
            continue
        else:
            choice = whiptail_menu(
            "escama-ap Config",
            "Elige que configurar:",
            ["1", f"Interfaz AP: {cfg['AP_IFACE']}",
             "2", f"Interfaz WAN: {cfg['WAN_IFACE'] or 'AUTO'}",
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
            cfg["WAN_IFACE"] = elegir_wan(cfg)
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

    if salir_sin_guardar:
        return 0
    if not guardar_config(cfg):
        sys.exit(1)
    # regenerar confs y reaplicar la salida si el WAN cambio (sin bajar el AP)
    subprocess.run(["escama", "genconfig"], check=False)
    cambio_wan = cfg["WAN_IFACE"] != wan_inicial
    ok_egress, salida_egress = aplicar_cambio_wan(wan_inicial,
                                                  cfg["WAN_IFACE"])
    subprocess.run(["whiptail", "--infobox", "Aplicando configuracion...", "5", "50"],
                   check=False)
    time.sleep(1)
    status = subprocess.run(["escama", "status"], capture_output=True, text=True)
    subprocess.run(["whiptail", "--msgbox",
                    texto_guardado(cfg, cambio_wan, ok_egress, salida_egress,
                                   (status.stdout or "").strip()), 20, 70],
                   check=False)
    sys.exit(0)


if __name__ == "__main__":
    main()
