---
name: Bug report
about: Report something that does not work as documented
title: "[bug] "
labels: bug
assignees: ''
---

## What happened

<!-- What did you expect, and what happened instead? -->

## How to reproduce

1.
2.
3.

## Environment

- Version (`escama --version`):
- Mode: sudo / rootless (`escama status` shows it):
- Debian version and kernel (`uname -a`):
- WiFi adapter / driver:
- `escama preflight` output:

```text

```

## Logs

<!-- Attach the relevant part of ~/.local/state/escama/escama-ap.log or
     /var/log/escama-ap.log. Remove passwords or keys before posting. -->

```text

```

## Golden rule check

Did escama touch the WAN interface (the one with internet)? It should only read
it. If yes, describe what changed.
