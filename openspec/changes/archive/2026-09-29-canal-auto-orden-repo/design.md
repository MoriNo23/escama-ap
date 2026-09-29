# Design

## Context

`escama.py` (925 líneas) es la única fuente de lógica: parseo manual de argv, sin
argparse, `run()` auto-prefija sudo, y toda consulta de red se hace lanzando
subprocesos (`iw`, `ip`, `nmcli`). El layout del repo es un *sysroot mirror*
(`etc/`, `opt/` replican el filesystem destino) y se conserva. La suite
(36 tests) mockea `run()` y constantes de módulo vía `monkeypatch`; no toca el
sistema. Constraints heredados de AGENTS.md: la WAN **solo se lee** (regla de
oro), los confs de hostapd/dnsmasq son productos derivados del env, commits en
español con prefijo conventional, y `pytest` se corre SIEMPRE con el path
explícito (`python3 -m pytest tests/test_escama.py -q`) por el pitfall de
`mutants/`. Estado relevante medido: en la PC de dev solo está instalado
`escama-ap.service` (enabled); `escama-egress.service` no existe ahí. Hoy
`do_watch`/`do_egress` llaman a `generate_configs()`, que reescribe AMBOS confs
(hostapd incluido) con el `CHANNEL` del env — inocuo con canal fijo, bug latente
con canal dinámico.

## Goals / Non-Goals

**Goals:**
- Elegir canal 2.4 GHz sin solapamiento con la WAN, solo con lecturas.
- Mantener el canal estable mientras el AP está activo (watch no lo toca).
- Reemplazar la instalación a mano por `install.sh` con control de autostart.
- Dejar el repo commiteado y ordenado sin mezclar movimientos con funcionalidad.

**Non-Goals:**
- No dividir `escama.py` en paquetes (un módulo es más simple a este tamaño).
- No usar ACS de hostapd (`channel=0`): flaky en RTL8192EU y no evita el canal
  de la WAN, solo elige por ruido.
- No recanalizar en vivo ni re-elegir canal en el loop de `watch` (tira todos
  los clientes).
- No tocar `escama-tui.py` (el nuevo `CHANNEL_MODE` se edita a mano en el env).
- No reorganizar `etc/`+`opt/` (el sysroot mirror es deliberado).
- No deshabilitar el autostart en stonepi por defecto: esa máquina ES el AP.

## Decisions

**D1 — Detección del canal de la WAN con `iw dev <wan> link`.**
Parsear `freq: NNNN` de la salida; conversión 2.4 GHz: `canal = (freq - 2407)/5`,
aceptando solo 2412–2484 (fuera de rango → fallback). Es 100% lectura (cumple la
regla de oro), funciona asociado a cualquier upstream y no requiere soporte de
scan. Alternativas descartadas: `iw dev scan` sobre la WAN (más caro, puede
dar micro-cortes de asociación, más frágil en Realtek); `nmcli` (la WAN puede no
estar gestionada por NM); ACS de hostapd (Non-Goal).

**D2 — Elección determinista sobre `{1, 6, 11}`.**
Candidatos = canales del conjunto con distancia ≥ 5 al canal de la WAN; se elige
el de mayor distancia y, en empate, el menor número. Ejemplos: WAN 6 → 1,
WAN 1 → 11, WAN 4 → 11, WAN 11 → 1. Determinismo = testeable con tabla fija.
Alternativa descartada: desempate por congestión vía scan en la iface AP
(requiere la iface down, soporte scan del 8192eu, y complejidad extra) —
postergado; el requisito de spec se satisface sin él.

**D3 — `CHANNEL_MODE=auto|manual`, default `auto`, fallback a `CHANNEL`.**
Si no hay canal WAN legible (Ethernet, 5 GHz, desconectada, sin `iw`), se usa el
`CHANNEL` del env. Default `auto` porque el collision es el bug que motiva el
change; `manual` es la vía de escape exacta al comportamiento anterior.
Alternativa descartada: default `manual` — dejaría el fix apagado por defecto.

**D4 — Detección solo en `start` (heredada por `restart`/`reconnect`).**
El canal se resuelve una vez por arranque, antes de generar confs, y se loguea
(canal elegido + canal WAN o motivo del fallback, ver spec de trazabilidad).
`watch`/`egress` nunca re-evalúan canal: recanalizar desasocia a todos los
clientes. Si el upstream cambia de canal post-arranque, se ve en el próximo
restart.

**D5 — Split de `generate_configs()` en hostapd/dnsmasq (bug latente).**
Hoy `watch`/`egress` regeneran ambos confs. Con canal dinámico eso regeneraría
`hostapd-escama.conf` con el `CHANNEL` estático del env, y un restart posterior
levantaría el canal viejo. Se separa en dos funciones: hostapd (recibe el canal
ya resuelto) y dnsmasq (DNS/MTU según kind). `watch`/`egress` SOLO regeneran
dnsmasq. `genconfig` y `start` generan ambos (con el canal resuelto en `start`,
literal del env en `genconfig`, que es "regenerar desde el env").
Alternativa descartada: persistir el canal en el state file y leerlo desde la
generación — acopla un producto del env a estado de runtime y ensucia `genconfig`.

**D6 — `install.sh`: bash puro, subcomandos, tolerante a componentes ausentes.**
`install|uninstall|enable|disable|status` + `--help|-h` (requisito no negociable
del proyecto: ambos CLIs aceptan help/version; el instalador sigue la misma
línea). Requiere root (mensaje claro si no). Detalles: `ln -sf` para symlinks
(idempotente), env instalado con no-sobrescritura (backup `.new` si existe),
`systemctl daemon-reload` tras instalar units, y cada operación de unit tolera
"unit ausente" con warning en vez de error (la PC de dev no tiene
`escama-egress.service`). Alternativa descartada: Makefile — un script con
subcomandos es autodocumentado y natural con sudo.

**D7 — Higiene de repo en fases, sin mezclar tipos de cambio.**
Orden estricto: (1) commitear el working tree pendiente TAL CUAL está hoy
(`escama.py`+`tests` en un commit feat/test; `escama.env` en uno chore) — sin
eso, cualquier `mv` posterior es indistinguible de un cambio funcional;
(2) feature de canal + tests; (3) `install.sh` + README; (4) movimientos de
docs (los 4 análisis de la raíz → `docs/diagnostics/`, manteniendo nombres por
las referencias cruzadas; actualizar las 2 referencias de `escama.py` a
`DIAGNOSIS-FINAL.md`), traducción de `docs/VPN-EGRESS.md`, fixes de README
(36 tests, sin `PYTHONPATH`), `AGENTS.md` y `openspec/` commiteados;
`.gitignore` + `.opencode/`, `.pi/` (tooling de harness, se ignora; también se
limpia el patrón inútil `/var/log/...`).

**D8 — Tests con el patrón vigente.**
Nuevos tests en `tests/test_escama.py` mockeando `run()` para `iw dev link`
(tabla D2 completa + fallbacks + 5 GHz + fuera de rango), `CHANNEL_MODE=manual`
(sin llamada a la WAN), y watch que no regenera hostapd. Ojo: los tests
existentes de `do_start`/`do_stop` parchean `generate_configs` por nombre — el
split D5 obliga a ajustar esos mocks (tarea explícita). Después del feature:
correr mutmut (setup.cfg ya apunta al source) y pytest SIEMPRE con path
explícito.

## Risks / Trade-offs

- [Upgrade cambia el canal silenciosamente con default `auto`] → es el
  comportamiento buscado; fallback a `CHANNEL` cuando no hay detección y
  `CHANNEL_MODE=manual` documentado en env y README como escape exacto.
- [`iw` no existe en un host (p. ej. la PC de dev)] → mismo camino de fallback
  a `CHANNEL`; `run()` ya tolera comandos ausentes con `check=False`.
- [Freq reportada fuera de 2412–2484] → validación de rango antes de convertir;
  fuera de rango = fallback, nunca canal calculado absurdo.
- [Split D5 rompe mocks existentes de `generate_configs`] → se ajustan en la
  misma tarea del split, suite en verde antes y después (path explícito).
- [install.sh toca el sistema con sudo] → solo crea/remueve archivos propios y
  usa systemctl sobre units propios; nunca modifica la WAN (regla de oro aplica
  también al instalador); `uninstall` conserva env y logs.

## Migration Plan

1. Commit del working tree pendiente (fase 0, antes de todo).
2. Feature canal (D1–D5) + tests → suite verde con path explícito.
3. `install.sh` + README + moves de docs (commits separados por tipo).
4. Ops: `systemctl disable --now escama-ap.service` en la PC de dev (no depende
   de `install.sh`; puede hacerse ya), y `install.sh disable` como forma
   reproducible en cualquier máquina. stonepi queda `enabled` salvo decisión
   contraria.
Rollback: `CHANNEL_MODE=manual` restaura el canal fijo; el resto son commits
revertibles; `install.sh uninstall` remueve la instalación nueva.

## Open Questions

- ¿Desactivar también el autostart en stonepi, o solo en la PC de dev?
  (Default asumido: stonepi queda `enabled` — es el servidor del AP. El
  `install.sh disable` permite cambiarlo en un paso sin tocar código.)
- ¿Traducir los 4 documentos de diagnóstico al inglés al moverlos a
  `docs/diagnostics/`? (Default asumido: quedan como registro histórico, en el
  idioma en que se escribieron.)
