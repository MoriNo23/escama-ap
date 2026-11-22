<div align="center">

# escama-ap

<img src="docs/logo/social-1280x640.png" alt="escama ap — wifi access point" width="100%">

Convierte un adaptador WiFi en Access Point para Debian/Linux.
Un comando levanta el AP con hostapd + dnsmasq; los clientes salen a internet
por la WAN o por un túnel VPN, con NAT automático.

![release](https://img.shields.io/github/v/release/MoriNo23/escama-ap)
![build](https://img.shields.io/github/actions/workflow/status/MoriNo23/escama-ap/ci.yml?branch=master)
![python](https://img.shields.io/badge/python-3.11%2B-3776AB?logo=python&logoColor=white)
![plataforma](https://img.shields.io/badge/plataforma-Debian%20%2F%20Linux-A81D33?logo=debian&logoColor=white)
![config](https://img.shields.io/badge/config-TOML-blue)
![licencia](https://img.shields.io/github/license/MoriNo23/escama-ap)

[Readme in English](README.md)

</div>

```
 cliente A ┐
 cliente B ├─ Wi-Fi "escama" ──►  AP (hostapd + dnsmasq)  ── NAT ──► internet
 cliente C ┘                            │
                                 ¿hay túnel VPN arriba?
                                        │ sí            │ no
                                        ▼               ▼
                                 salida por el túnel   salida por la WAN
```

> Regla de diseño: la interfaz WAN **solo se lee, nunca se modifica**. Todo lo
> que escama configura vive del lado del AP.

## Instalación

```bash
git clone https://github.com/MoriNo23/escama-ap.git
cd escama-ap
sudo ./install.sh install    # código en /opt/escama, comandos escama/escama-tui, units
sudo ./install.sh enable     # opcional: arranque al boot
```

El instalador nunca pisa tu configuración: si `/etc/escama/escama.toml` ya
existe, las novedades de cada versión quedan al lado en `escama.toml.new`.

Antes del primer arranque hay que definir la passphrase del AP (escama no
levanta una red abierta):

```bash
sudo escama-tui          # opción 7 (Passphrase WPA2), Guardar y Salir
```

## Uso

```bash
sudo escama start         # levanta el AP (hostapd + dnsmasq + NAT + forwarding)
sudo escama stop          # baja el AP y restaura la interfaz a modo cliente
sudo escama restart       # stop + start
sudo escama status        # estado actual (funciona sin sudo)
escama qr                 # QR para unirte al AP desde el telefono (terminal, sin sudo)
sudo escama reconnect     # re-levantar tras desenchufar/enchufar el adaptador
sudo escama genconfig     # regenera hostapd/dnsmasq desde escama.toml
sudo escama egress        # re-evalúa la salida (VPN/WAN) sin tirar el AP
sudo escama egress vpn    # forzar salida: auto | vpn | wan | <iface>
sudo escama watch         # loop: sigue el túnel VPN y reaplica la ruta solo
sudo escama rename <iface> <nuevo>   # renombra un adaptador WiFi
sudo escama autorename               # nombres por defecto (wifi-<4 de MAC>) para WiFi genéricas
escama preflight          # diagnóstico de la máquina (componentes, versión, perms)

escama                    # menú interactivo (whiptail): entrada sugerida
sudo escama-tui           # el mismo menú, forzado aunque no haya TTY
```

## Menú interactivo

`escama` sin argumentos y con terminal abre el menú whiptail. Muestra el estado
real de AP/WAN/egress, ofrece solo las acciones que tienen sentido en ese
estado y delega cada mutación en los mismos comandos que se usan desde la shell.
Sin TTY (scripts, systemd) sigue imprimiendo `status`; sin `whiptail` avisa cómo
instalarlo y cae a `status`.

## Configuración

Todo vive en `/etc/escama/escama.toml` (TOML, comentarios incluidos). Se edita
con `escama-tui` o a mano, y los cambios aplican con `sudo escama restart`.

```toml
AP_IFACE  = "stonepi"     # la interfaz que hace de AP
WAN_IFACE = "wn8200nd"    # la que trae internet ("" = auto-detectar)
SSID      = "escama"
CHANNEL_MODE = "auto"     # auto = elige de {1,6,11} sin solapar la WAN
EGRESS_MODE  = "auto"     # auto = VPN si hay túnel, si no WAN
                          # vpn  = kill-switch (sin túnel no navegan)
                          # wan  = siempre WAN, ignora la VPN
```

Para invertir los roles (usar la WAN actual como AP) alcanza con intercambiar
`AP_IFACE` y `WAN_IFACE`: el NAT y las validaciones siguen la config, no hay
nada hardcodeado.

## Renombrar adaptadores

Los dongles USB aparecen como `wlx<MAC>` (imposible de memorizar). `rename`
deja una regla udev por MAC y renombra la interfaz al instante:

```bash
sudo escama rename wlx020304050607 WU900
```

- Persistente (sobrevive a boots y re-plugs) y en vivo: baja la interfaz,
  la renombra y la vuelve a subir.
- Revincula los perfiles de NetworkManager atados al nombre viejo, así que la
  conexión WiFi actual no se corta.
- Actualiza `AP_IFACE`/`WAN_IFACE` del toml si apuntaban al nombre viejo.
- Si esa MAC tenía una regla manual en `70-persistent-net.rules` o similar,
  la retira y la consolida en `76-escama-ifaces.rules`.

`autorename` evita tipear siquiera una vez: todo adaptador WiFi que conserve
un nombre genérico del kernel (`wlx<MAC>`, `wlan0`, `wlp3s0`) pasa a
`wifi-<últimos 4 hex de su MAC>` (ej. `wifi-b48f`; si colisiona usa más
nibbles). `start` lo hace con el AP automáticamente en la primera vez —
también tras resetear la config o si `AP_IFACE` apunta a un nombre genérico —
y `sudo escama autorename` renombra todas las WiFi genéricas presentes, WAN
incluida. Los nombres personalizados nunca se sobreescriben, y la WAN solo se
renombra con ese comando manual.

## Salida por VPN

Si el equipo tiene una VPN activa, los clientes del AP salen por el túnel en
vez de quedar fuera de internet. Soporta ProtonVPN, WARP, WireGuard y OpenVPN
(detección automática o forzada), con policy routing y MSS clamp según el
túnel. Detalle por proveedor: [docs-es/VPN-EGRESS.md](docs-es/VPN-EGRESS.md).

## Arranque automático (systemd)

```bash
sudo ./install.sh enable          # al boot + ahora
sudo ./install.sh disable         # no al boot + detener
sudo ./install.sh enable --user   # al iniciar sesión, sin unit de sistema
```

`Restart=on-failure` cubre muerte del proceso, no hardware ausente: si el
adaptador se desenchufa, `sudo escama reconnect` a mano.

## Sin sudo (opcional)

Además del modo clásico con `sudo`, existe un modo rootless: un binario ELF
con `CAP_NET_ADMIN`/`RAW`/`BIND_SERVICE` le pasa las capabilities al núcleo
Python (el kernel ignora file capabilities en scripts con shebang). Cubre las
operaciones de red; lo que necesita escribir en `/etc` degrada con un mensaje
explícito. `escama status` muestra siempre qué modo está corriendo y dónde
quedan log y confs, para no confundir "no arrancó" con "no tengo permiso".

|                             | con sudo              | rootless            |
|-----------------------------|-----------------------|---------------------|
| Red (hostapd, NAT, rutas)   | sí                    | sí, vía el launcher |
| Autostart                   | unit de sistema       | unit de usuario     |
| Log                         | `/var/log/escama-ap.log` | `~/.local/state/escama/` |
| Recargar módulo del driver  | sí                    | degrada con motivo  |

## Testing

```bash
python3 -m pytest tests/test_escama.py -q    # suite completa, ~16 s
```

Los tests mockean `run()`/`subprocess`/`os`: nunca tocan las interfaces reales
(lo garantiza un fixture que bloquea subprocess en toda la suite). Mutation
testing opcional con `mutmut run` (config en `setup.cfg`).

## Requisitos

- Debian/Linux con NetworkManager (`nmcli`)
- Python 3.11+ — solo stdlib, cero dependencias (`tomllib`)
- `hostapd`, `dnsmasq`, `iw`; `whiptail` solo para la TUI
- `qrencode` — opcional, solo para `escama qr` (`sudo apt install qrencode`;
  sin él el comando imprime el string WIFI y la línea de instalación)
- Un adaptador WiFi con soporte de modo AP (drivers rtl8192eu y aic8800 verificados)

## Documentación

- [docs/TECHNICAL.md](docs/TECHNICAL.md) — diseño interno (inglés)
- [docs-es/TECHNICAL.md](docs-es/TECHNICAL.md) — diseño interno (español)
- [docs-es/VPN-EGRESS.md](docs-es/VPN-EGRESS.md) — salida por túnel, casos y diagnóstico
- [CHANGELOG.md](CHANGELOG.md) — historial de versiones

## Licencia

[MIT](LICENSE)
