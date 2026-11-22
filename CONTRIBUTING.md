# Contributing to escama-ap

Thanks for helping. This project is small and deliberately dependency-free.

## Development setup

- Python 3.11+ (`tomllib` is stdlib from 3.11). No build step: run the scripts
  directly from the repo.
- Runtime requirements stay outside the repo: `hostapd`, `dnsmasq`, `iw`,
  `nmcli`, `iptables`, `whiptail` (TUI only) and `qrencode` (optional).
- Install the test runner with `python -m pip install pytest`.

## Tests

```
python3 -m pytest tests/test_escama.py -q
```

Always pass the explicit path: `mutants/tests/test_escama.py` shares the
basename and breaks collection with a bare `python3 -m pytest`.

Tests mock `run()`/`subprocess`/`os` through an autouse fixture. They must
never touch the real AP or WAN interfaces. Mutation testing is manual:
`mutmut run` (configuration in `setup.cfg`).

## Conventions

- Commits: Spanish, lowercase, conventional prefix (`feat:`, `fix:`, `docs:`,
  `test:`, `chore:`, `refactor:`).
- Code and docstrings in Spanish; functions and variables in `snake_case`.
- `docs/` is English, `docs-es/` is Spanish. Keep both in sync.
- `VERSION` is the single source of truth: never hardcode a version in an
  executable. Every behavior change adds a reasoned semver bump task and a
  `CHANGELOG.md` entry.
- Behavior changes go through OpenSpec: `/openspec-propose`, then
  `/openspec-apply-change`. Validate with `openspec validate <change> --strict`.

## Pull request checklist

- [ ] `python3 -m pytest tests/test_escama.py -q` passes.
- [ ] New behavior has tests and, when user-visible, a spec scenario.
- [ ] `CHANGELOG.md` and the semver bump task are present.
- [ ] Both language docs were updated when documentation changed.
- [ ] `openspec validate <change> --strict` is clean.
- [ ] No generated conf was edited by hand: change `etc/escama/escama.toml`
      and run `escama genconfig`.

## GitHub maintenance (maintainers)

- Repository settings: homepage points to this README, topics describe the
  stack, and private vulnerability reporting must stay enabled (see
  `SECURITY.md`). The social preview uses
  `docs/logo/social-1280x640.png` and is uploaded in Settings, not via API.
- Dependabot is configured in `.github/dependabot.yml`; GitHub Actions updates
  are grouped into one weekly PR. There is no `pip` ecosystem because the
  project has no Python manifest.
- Discussions and Wiki stay disabled: `docs/`, `docs-es/` and issues are the
  single source of truth. Do not duplicate documentation in GitHub features.
- Branch protection requiring a green CI check is recommended on `master`;
  it is a manual settings decision, not something this repo changes on its own.
- Releases are created from `VERSION` + `CHANGELOG.md` after the bump, so the
  release badge in the README always resolves.
