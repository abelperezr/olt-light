---
sidebar_position: 5
---

# Validating a customization

Three levels, from cheapest to most complete. The first two don't need
Docker.

## Level 1: static checks

```bash
./build.sh check
```

Compiles all the overlay's Python code and runs the unit tests under
`tests/`. As a guardrail, it also fails if directories that belong to the
base images (`yang`, `device-ext`, `seeds`) appear in the tree — this repo
must never contain them.

## Level 2: dry-run the daemons

The daemons accept `--dry-run`/`--once` to execute once without touching
the system:

```bash
PYTHONPATH=src/daemons python3 src/daemons/onu_dhcp.py --dry-run --once
```

Keep in mind that outside dry-run, `onu_dhcp.py` creates and deletes
network interfaces: run it inside the container or a lab network
namespace.

## Level 3: smoke test

```bash
docker compose -f examples/docker-compose.yml up -d
docker compose -f examples/docker-compose.yml logs --tail=100 olt
ssh -p 2222 isadmin@localhost
```

With your freshly built image up, check that the three planes start, the
eCLI answers, and the daemons show up in the log without errors. For an
end-to-end validation with a BNG and Altiplano, move on to the
[containerlab lab](./deploy-lab.md).
