# Changelog

Todas las versiones de escama-ap. La versión vive en el archivo `VERSION` de la
raíz del repo (fuente única: la leen `escama.py`, `escama-tui.py` e
`install.sh`). Los números de abajo son semver.

La serie 0.x cubre la historia anterior al versionado: Those releases never
declared a version, así que se reconstruyen por épocas a partir de los commits
del repo. Desde 1.0.0 el bump es explícito: cada change que altera comportamiento
incluye el bump en su `tasks.md` y una entrada acá.

## [No publicado]

### Cambiado
- El AP elige canal 2.4 GHz sin solape con el de la interfaz WAN: `CHANNEL_MODE=auto`
  (default) lee el canal de la WAN —solo lectura, regla de oro— y elige de
  `{1,6,11}` el más lejano; `manual` conserva el `CHANNEL` fijo. Verificado en la
  máquina: la WAN estaba en el canal 3 y el AP pasó de 6 (solapado) a 11.
- La generación de configs se separó: `watch`/`egress` solo regeneran dnsmasq y
  nunca reescriben hostapd, así el canal no queda obsoleto tras un cambio de VPN.
- `install.sh`: ciclo de vida reproducible (`install|uninstall|enable|disable|status`),
  idempotente y que jamás pisa el `escama.env` del usuario (las novedades quedan
  en `escama.env.new`).

### Agregado
- `docs/VPN-EGRESS.md` en inglés; los análisis de debugging pasaron a
  `docs/diagnostics/`.

## 1.0.0 — 2026-08-14

- Consolidación de 6 scripts bash en un núcleo Python (`escama.py`) + TUI.
- Egress dinámico VPN/WAN con policy routing, kill-switch y clamp de MSS.
- Validación real del AP (`type AP`), auto-detección de roles AP/WAN, recarga
  del módulo 8192eu ante el fallo -95, y documentación ES/EN.

## Serie 0.x (historia previa al versionado)

Reconstruida desde los commits; estas versiones nunca se declararon formalmente.

### 0.4 — Instalación y autostart
- `install.sh` (en el change 1.0.0): instalación y control de arranque automático
  sin pasos manuales.
- Units de systemd `escama-ap.service` y `escama-egress.service`; el watcher de
  egress pasa a ser una unit en vez de un proceso suelto.

### 0.3 — Selección de canal
- `CHANNEL_MODE` y lectura del canal de la WAN (solo lectura) para evitar
  interferencia entre el AP y la iface cliente WiFi.

### 0.2 — Egress por VPN
- Salida de clientes por tunnel (ProtonVPN / WARP / WireGuard) con
  `EGRESS_MODE=auto|vpn|wan`, política de kill-switch y fix de la regla de
  routing `iif <ap>` (regresión documentada en `docs/diagnostics/DIAGNOSIS-FINAL.md`).

### 0.1 — Núcleo
- `escama.py` con `start|stop|restart|status|reconnect|genconfig`, validación real
  del modo AP, masquerade/NAT hacia la WAN, y `dnsmasq` sirviendo DHCP/DNS.
