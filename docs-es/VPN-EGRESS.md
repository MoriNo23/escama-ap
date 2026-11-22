# Salida por VPN (ProtonVPN / WARP / WireGuard) — investigación y opciones

> Respuesta al problema: **"si uso VPN en la laptop, los clientes del AP se quedan sin
> internet"**. Aquí está por qué pasa, qué opciones reales hay, y qué implementa escama.

## 1. Por qué se cae el internet de los clientes al conectar la VPN

El AP hacía siempre esto:

```bash
iptables -t nat -A POSTROUTING -o <WAN_IFACE> -s 10.42.1.0/24 -j MASQUERADE
```

Es decir: NAT **clavado a la interfaz WAN física** (`stonepi`). Cuando levantás un
tunnel, pasan tres cosas a la vez, y cualquiera de las tres rompe a los clientes:

| # | Qué pasa | Efecto en los clientes |
|---|----------|------------------------|
| 1 | La VPN mete una ruta default por el tunnel (`0.0.0.0/1` + `128.0.0.0/1` por `proton0`, o tabla `51820` con `ip rule not fwmark` en WireGuard) | El paquete del cliente se rutea al tunnel, pero el `MASQUERADE` era `-o stonepi` → sale **sin NAT** por el tunnel con IP origen `10.42.1.x`. El servidor VPN lo dropea (no conoce esa red). Silencio total. |
| 2 | El **kill switch** de Proton/WireGuard instala reglas `REJECT`/`DROP` para todo lo que no salga por el tunnel | Aunque el paquete quisiera salir por `stonepi`, lo bloquea el kill switch. |
| 3 | `rp_filter` estricto | La respuesta vuelve por el tunnel mientras el kernel espera que vuelva por donde salió → descarte por reverse path. |

Sumale el clásico de MTU: WireGuard usa 1420 (Proton) o 1280 (WARP). Sin MSS clamp,
los clientes hacen handshake TCP OK pero las webs pesadas se cuelgan a medio cargar.

**Conclusión:** no hace falta elegir entre VPN y AP. Hace falta que el NAT y el
routing apunten al tunnel en vez de al adaptador físico.

## 2. Opciones que existen (y cuál conviene)

### Opción A — NAT dinámico hacia el tunnel  ✅ *implementada, la recomendada*

Mover el egress del AP a la interfaz del tunnel:

```bash
iptables -t nat -A POSTROUTING -o proton0 -s 10.42.1.0/24 -j MASQUERADE
iptables -A FORWARD -i wn8200nd -o proton0 -s 10.42.1.0/24 -j ACCEPT
iptables -A FORWARD -i proton0 -o wn8200nd -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
```

- **Pro:** los clientes salen *dentro* de la VPN (esto suele ser lo que querés: el TV
  y el celu con la IP de Proton). Un solo cambio, sin tocar la WAN.
- **Contra:** el proveedor debe aceptar tráfico NATeado del cliente. Proton y WARP sí.
- **Requiere:** `ip_forward=1`, `rp_filter=2` (loose) y, si la default del host no es
  el tunnel, **policy routing** (ver más abajo).

### Opción B — Split: clientes por WAN, laptop por VPN

Dejar el `MASQUERADE -o stonepi` y **excluir** el tráfico del AP del tunnel
(`ip rule add iif <AP_IFACE> lookup main pref 90`, o en Proton/WARP el split tunnel).
Con `iif` (interfaz de ingreso) la regla matchea solo lo que entra por el AP: un
selector `from <subnet>` atraparía también los paquetes originados en el host
con esa IP de origen (ver `docs/diagnostics/DIAGNOSIS-FINAL.md` §4.1).

- **Pro:** la VPN te cubre solo a vos; los clientes no pierden velocidad.
- **Contra:** los clientes navegan con tu IP real → si el motivo de la VPN es
  privacidad para todos, no sirve. Además el kill switch de Proton puede seguir
  bloqueando el forward.
- En escama: `EGRESS_MODE="wan"`.

### Opción C — Network namespace para la VPN

Meter el cliente VPN en un `netns` y unir el AP por un `veth`.

- **Pro:** aislamiento total, la VPN no toca el routing del host.
- **Contra:** mucha complejidad (veth, resolv.conf propio, servicios duplicados). Es
  la receta que circula para Docker+WARP. Overkill para este caso.

### Opción D — Router-level (OpenWrt / OPNsense con WireGuard)

Poner la VPN en el router, no en la laptop.

- **Pro:** lo más robusto y lo que documenta Proton oficialmente.
- **Contra:** no aplica: acá la caja *es* el router.

### Opción E — WARP Connector / Cloudflare Mesh (solo warp-cli)

Cloudflare tiene un modo oficial para que un Linux enrute una LAN entera: hay que
habilitar *Override local interface IP*, `ip_forward=1`, y publicar el CIDR
(`10.42.1.0/24`) como ruta en el dashboard de Zero Trust.

- **Pro:** soportado oficialmente, con políticas Gateway.
- **Contra:** requiere cuenta Zero Trust y configuración en el dashboard. Para el WARP
  gratis (`warp-cli connect` normal) alcanza con la Opción A.

## 3. Lo que implementa escama

`EGRESS_MODE` en `/etc/escama/escama.toml`:

| Modo | Comportamiento |
|------|----------------|
| `auto` *(default)* | Si hay tunnel arriba → los clientes salen por el tunnel. Si no hay → **fallback automático a la WAN**. Nunca se quedan sin internet por bajar la VPN. |
| `vpn` | Solo tunnel. Sin tunnel, los clientes **no** navegan (kill-switch, fail-closed). Cero fuga de IP real. |
| `wan` | Comportamiento clásico: siempre NAT por la WAN, ignora la VPN (Opción B). |

### Detección del tunnel

`VPN_IFACE=""` = auto-detección. Se reconocen, en este orden:

`proton0` (Proton OpenVPN / app oficial) → `pvpn0`, `protonwire0` (Proton WireGuard) →
`CloudflareWARP`, `warp0` (warp-cli, tanto WireGuard como MASQUE) → `nordlynx` →
`mullvad-wg` → `wg0` → `tun0` → `tailscale0`.

Además detecta cualquier device cuyo kind sea `wireguard`, o que tenga `tun_flags`
(tun/tap), o `ppp`. Están en lista negra `ipv6leakintrf0` y `pvpnksintrf0`: son las
interfaces *dummy* de anti-leak de Proton, elegirlas como egress mandaría el tráfico
a un agujero negro.

Si tenés varios tunnels arriba, fijalo a mano: `VPN_IFACE="proton0"`.

En la TUI elegí `Interfaz WAN: AUTO` para guardar `WAN_IFACE=""`: escama detecta
la interfaz con la ruta por defecto y reaplica la salida al guardar, sin detener
el AP.

### Qué aplica cuando el egress es VPN

1. `MASQUERADE -o <tunnel> -s <AP_SUBNET>` (en vez de `-o WAN`).
2. Reglas `FORWARD` explícitas AP↔tunnel con conntrack (sobrevive a un
   `FORWARD DROP` por defecto, que es lo que deja el kill switch de Proton).
3. `rp_filter=2` (loose) en `all` y en la iface del AP → el retorno por el tunnel
   no se descarta.
4. **Policy routing** (`VPN_FORCE_ROUTE="yes"`): tabla `51821` con
   `default dev <tunnel>` + `ip rule add iif <AP_IFACE> lookup 51821 pref 100`.
   La regla matchea la **interfaz de ingreso** del AP (`iif`), no el subnet de
   origen: un selector `from <subnet>` también secuestraría los paquetes
   originados en el host con esa IP de origen hacia la tabla del tunnel
   (ver `docs/diagnostics/DIAGNOSIS-FINAL.md` §4.1).
   Esto es **imprescindible con warp-cli**, que usa split tunnel + fwmark y no pone
   una default plana; sin la regla, los paquetes de los clientes ni llegan al tunnel.
5. **MSS clamp** (`VPN_MSS_CLAMP="yes"`): `TCPMSS --clamp-mss-to-pmtu` en `mangle
   FORWARD -o <tunnel>`. Sin esto, WARP (MTU 1280) rompe medio internet para los
   clientes.
6. **DHCP option MTU**: se les entrega a los clientes la MTU real del tunnel.
7. **Kill-switch propio**: `FORWARD -i <AP> -o <WAN> -s <SUBNET> -j REJECT`, para que
   ni un paquete del AP se escape por la WAN en claro mientras la VPN está arriba.
8. **DNS**: `VPN_DNS1/VPN_DNS2` reemplazan a `DNS1/DNS2` en el DHCP. Recomendado,
   porque si no los clientes preguntan a `8.8.8.8` y eso es una fuga de DNS clarísima
   (y con el kill switch de Proton, además, ni resuelve).
   - ProtonVPN: `10.2.0.1`
   - WARP: `1.1.1.1`, `1.0.0.1`

## 4. Uso

```bash
sudo escama status     # muestra: tunnels arriba, modo, y por dónde salen los clientes
sudo escama egress     # re-evalúa y reaplica SIN tirar el AP (los clientes no se desconectan)
sudo escama egress vpn # forzar modo VPN ahora
sudo escama egress wan # forzar salida por WAN ahora
sudo escama egress proton0   # forzar un tunnel específico
sudo escama watch 5    # loop: sigue el estado del tunnel y reaplica solo
```

Flujo típico con ProtonVPN:

```bash
sudo escama start          # AP arriba, sale por stonepi
protonvpn-app / wg-quick up protonnl
sudo escama egress         # detecta proton0 y mueve el NAT al tunnel
# ...al desconectar la VPN:
sudo escama egress         # vuelve solo a stonepi (fallback)
```

Para que sea automático (sin acordarse de correr `egress`):

```bash
sudo systemctl enable --now escama-egress.service
```

Ese service corre `escama watch 5`: cada 5 s compara el egress calculado contra el
aplicado, y si cambió reaplica NAT + policy routing + DNS y le manda `SIGHUP` a
dnsmasq. Conectás Proton y en ≤5 s los clientes ya están saliendo por el tunnel.

## 5. Casos particulares por proveedor

### ProtonVPN (app oficial / OpenVPN)
Interfaz `proton0`. La app instala kill switch con iptables y las interfaces dummy
`ipv6leakintrf0` / `pvpnksintrf0`. escama las ignora y añade reglas FORWARD explícitas,
así que el kill switch no mata a los clientes. DNS del tunnel: `10.2.0.1`.

### ProtonVPN WireGuard (wg-quick con .conf descargado)
El nombre de la interfaz **es el nombre del archivo** (`protonnl.conf` → `protonnl`),
no `wg0`. Por eso hay detección por *kind* `wireguard` y no solo por nombre. Ojo:
`wg-quick` con `AllowedIPs = 0.0.0.0/0` usa policy routing con fwmark, y las rutas
quedan en la tabla `51820` — nuestra tabla `51821` con `ip rule iif <AP_IFACE>` tiene
precedencia por `pref 100` y resuelve el caso.

### warp-cli (Cloudflare WARP)
Interfaz `CloudflareWARP`. Es el caso donde **más** hace falta `VPN_FORCE_ROUTE` y
el MSS clamp (MTU 1280). Notas:
- WARP excluye por defecto los rangos RFC1918 del tunnel (split tunnel). El tráfico
  del AP hacia internet igual entra al tunnel gracias a la regla de policy routing.
- Si usás WARP en modo **proxy** (`warp-cli mode proxy`, SOCKS5 en :1080) **no hay
  interfaz que NATear**: no existe egress a nivel IP. Ahí la única salida es un
  transparent proxy (redsocks) o cambiar a modo tunnel (`warp-cli mode warp`).
- Para hacerlo "oficial" con una cuenta Zero Trust: WARP Connector, con *Override
  local interface IP* activado y `10.42.1.0/24` publicado como ruta.
- El README viejo decía *"WARP + AP no coexisten por diseño de Linux"*. **Es falso**:
  no coexistían porque el NAT estaba clavado a la WAN. Con NAT + policy routing hacia
  `CloudflareWARP` conviven bien.

### Tailscale (solo administración)
`tailscale0` es una interfaz de administración: acceso remoto al host (por
ejemplo, OpenCode desde tu celular). Nunca se elige automáticamente como egress,
ni con `EGRESS_MODE="auto"` ni con `"vpn"`. Con `auto` los clientes usan la WAN;
con `vpn` quedan en fail-closed. Para usarlo a propósito, fijá
`VPN_IFACE="tailscale0"` después de configurar un exit node
(`tailscale up --exit-node=<node>`). escama comprueba el exit node solo lectura
con `tailscale status --json`; si no hay, falla cerrado con mensaje explícito y
no instala NAT hacia el túnel.

### Limpieza y reconciliación

Toda regla que instala escama lleva `-m comment --comment escama`. En `stop` o
al cambiar el egress, el core lee primero `iptables-save` y `ip rule show` y
borra sus propias reglas por marcador, subnet del AP y tabla `51821`. El state
file (`escama-egress.state`) pasa a ser una caché de `IPFWD`/`RP_FILTER` y del
egress anterior: la limpieza ya no depende de él, así que un archivo viejo,
ausente o de otro modo de `euid` no deja reglas NAT/policy huérfanas.

Los roles AP/WAN detectados en `start` se guardan en `escama-roles.state` y los
leen `stop`, `egress` y `watch`: una config que todavía apunta a la iface vieja
ya no hace que la limpieza actúe sobre la placa equivocada. `apply_egress`
toma un `flock` y verifica la regla NAT en el kernel antes de anunciar éxito.

## 6. Diagnóstico rápido

```bash
sudo escama status                      # ¿qué tunnel ve y qué aplicó?
ip rule                                 # ¿está la regla iif <AP_IFACE> lookup 51821?
ip route show table 51821               # ¿default dev <tunnel>?
sudo iptables -t nat -S POSTROUTING     # ¿el MASQUERADE es -o <tunnel>?
sudo iptables -S FORWARD                # ¿hay ACCEPT AP<->tunnel? ¿algún DROP de la VPN?
cat /proc/sys/net/ipv4/ip_forward       # 1
sysctl net.ipv4.conf.all.rp_filter      # 2 (loose) cuando hay VPN
ping -I 10.42.1.1 1.1.1.1               # el host, con IP del AP, ¿sale?
```

Síntomas y causa probable:

| Síntoma | Causa |
|---------|-------|
| Cliente asocia y toma IP, pero nada carga | NAT apuntando a la WAN vieja → `sudo escama egress` |
| Ping a IPs OK, DNS no resuelve | Fuga DNS bloqueada por kill switch → seteá `VPN_DNS1` |
| Webs chicas cargan, las pesadas se cuelgan | MTU/PMTU → `VPN_MSS_CLAMP="yes"` |
| Al desconectar la VPN quedan sin internet | Estabas en `EGRESS_MODE="vpn"` (fail-closed, es intencional) → usá `auto` |
| Doble NAT lento | Normal: NAT del AP + NAT del proveedor VPN. Sin arreglo posible en este esquema. |
