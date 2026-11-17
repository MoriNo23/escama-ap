# AGENTS.md — escama-ap

Convertidor de interfaz WiFi a Access Point (hostapd + dnsmasq + NAT masquerade) para
Debian/Linux. El AP emite el SSID `escama`; el tráfico de clientes sale por la WAN
(`-o WAN_IFACE`), o por un tunnel VPN si `EGRESS_MODE=auto` y hay uno arriba. Única
fuente de lógica: `opt/escama/escama.py`. La config vive en `etc/escama/escama.toml`
(editar ahí, NUNCA los confs generados).

## Dev environment
- Python 3.13. Sin build step: no hay setup.py/pyproject/Makefile, se ejecuta directo.
- Requirements de sistema (no en repo): `hostapd`, `dnsmasq`, `iw`, `nmcli`,
  `iptables`, `whiptail` (solo TUI). `nmcli` e `iw` NO están en este equipo de dev.
- Driver RTL8192EU DKMS compilado con `CONFIG_AP_MODE=y`; si falta, hostapd falla con
  "Operation not supported" y `reload_module_if_needed()` hace `rmmod`+`modprobe`.
- `mutmut` en `~/.local/bin/mutmut` (mutation testing). `mutants/` es scratch, gitignored.
- Symlinks `escama`/`escama-tui` → `/usr/local/bin` y `~/.local/bin` (creados a mano;
  no hay script de install en el repo).

## Build & test
Desde la raíz del repo:
  python3 -m pytest tests/test_escama.py -q        # 105 tests, ~22s, sin root
Los tests mockean `run()`/`os`/`subprocess` → NO tocan `stonepi`/`wn8200nd`.
  mutmut run                                       # lee setup.cfg (source_paths + tests_dir)
NO corras `python3 -m pytest` (sin path): `mutants/tests/test_escama.py` tiene el mismo
basename y rompe la colección (import mismatch). Usa siempre el path explícito.

## Conventions
- Commits: español, lowercase, prefijo conventional — `feat(scope):`, `fix+feat:`,
  `docs:`, `test:`, `chore:`, `refactor:`.
- Docs: `docs/` = inglés, `docs-es/` = español (roles invertidos en 2026-08).
- Código y docstrings en español; funciones/vars `snake_case`.
- CLI: parseo manual de `argv` en `main(args=None)` (NO argparse). Subcomandos de
  `escama.py`: `start|stop|restart|status|reconnect|genconfig|egress|watch`.
  Ambos CLIs aceptan `--help|-h|help` y `--version|-v|version` (requisito no negociable).
- `run()` auto-prefija `sudo` si `os.geteuid() != 0`. Path real de confs: `/etc/escama/*`.
- Config: `DEFAULTS` (en escama.py) + `load_env()` mergea `escama.toml` por encima.
- `log()` escribe a `/var/log/escama-ap.log` + syslog + print; envuelto en
  try/except para nunca crashear.

## Versionado (obligatorio)
- **Fuente única**: el archivo `VERSION` en la raíz. `escama.py`, `escama-tui.py`
  e `install.sh` la leen en runtime. Prohibido hardcodear la versión en cualquier
  ejecutable (hay un test que lo falla). Si no se encuentra el archivo, degradar
  a `desconocido`, nunca a un número viejo.
- **Bump por change**: todo change que altere comportamiento incluye en su
  `tasks.md` un paso de bump semver razonado — patch = corrige algo que ya violaba
  su spec, minor = requisito nuevo compatible, major = ruptura de contrato — **y**
  su entrada en `CHANGELOG.md`. El bump ocurre antes de archivar el change.
- `CHANGELOG.md` cubre también la serie 0.x (historia previa al versionado).

## Pitfalls
- REGLA DE ORO: la WAN (`stonepi` por defecto) SOLO se lee, NUNCA se modifica
  (ni `ip addr del`, ni `nmcli`, ni `hostapd`) salvo que el env lo diga.
- `hostapd-escama.conf` y `dnsmasq-escama.conf` se GENERAN con `genconfig` desde el env.
  Nunca editar a mano; editar `escama.toml` y correr `escama.py genconfig`.
- No hardcodees la WAN en iptables: usa `WAN_IFACE` del env (`-o <WAN_IFACE>`),
  así el NAT sobrevive a cambiar la WAN o a un tunnel VPN arriba.
- Repo con cambios sin commitear: `escama.toml` tiene `AP_IFACE=stonepi` /
  `WAN_IFACE=wn8200nd` (invertidos vs DEFAULTS). No asumas que `master` los refleja
  hasta que se haga commit.
- `detect_ap_iface()`/`detect_wan_iface()` son nuevos (sin commitear en escama.py);
  si los tocás, verificá que los 105 tests sigan en verde con el path explícito.

## Hermes skills (globales, `~/.hermes/skills/`)
Skills versionadas del stack del host, instaladas a nivel global de Hermes (no en el repo).
**Ante cualquier tarea sobre los componentes de abajo, cargá la skill correspondiente
con `skill_view(name=...)` ANTES de actuar** (la skill lleva la referencia operacional,
known-issues y fuentes versionadas; no operar de memoria). Se cargan por coincidencia
de tarea pero la carga explícita es obligatoria en este proyecto. Paquete origen:
`linux-stack-agent-skills` v1.1.0. Verificadas con `hermes skills list` (status `enabled`).

| Skill (cargar antes de tocar) | Componente cubierto (versión del host) |
|---|---|
| `iptables-debian13` | iptables 1.8.11 (nf_tables) en Debian 13 — firewalls, NAT, reglas |
| `iproute2-6-15` | iproute2 6.15.0 + libbpf 1.5.0 — `ip`, rutas, políticas |
| `whiptail-0-52-25` | whiptail/newt 0.52.25 — solo TUI `escama-tui.py` |
| `systemd-257` | systemd 257.13 — units `escama-ap.service`, `escama-egress.service` |
| `pytest-9-0-3` | pytest 9.0.3 — suite `tests/test_escama.py`, 105 tests |
| `mutmut-3-7-0` | mutmut 3.7.0 — mutation testing, `setup.cfg` |

Cada skill: `SKILL.md` + `references/{operational-reference,known-issues,sources}.md`.
RTL8192EU/Realtek NO incluido (excluido del pack por decisión del usuario).
