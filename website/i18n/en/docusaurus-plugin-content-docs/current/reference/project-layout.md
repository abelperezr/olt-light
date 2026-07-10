---
sidebar_position: 1
---

# Project layout

```
Dockerfile              overlay: copies src/ on top of the base image
build.sh                check (tests) + build of the customized image
pyproject.toml          light_olt package metadata
src/
  ecli                  eCLI executable (SSH login shell)
  light_olt/            Python package with the eCLI logic
  daemons/
    onu_dhcp.py         ONU DHCP subscribers (DORA/SARR)
    onu_optics.py       per-ONU optical levels (operational)
    ipfix_exporter.py   synthetic IPFIX telemetry
tests/                  overlay unit tests
examples/
  lab.clab.yml          containerlab lab: BNG + OLT + proxy
  docker-compose.yml    minimal smoke test: OLT + proxy
website/                this documentation (Docusaurus, es/en)
```

## Paths inside the image

The base image's startup supervisor expects components at fixed paths. The
Dockerfile honors them; move them and the daemons won't start.

| Repo source | Image destination |
|---|---|
| `src/ecli` | `/usr/local/bin/ecli` |
| `src/light_olt/` | `/opt/light-olt/light_olt/` |
| `src/daemons/onu_dhcp.py` | `/usr/local/bin/onu_dhcp.py` |
| `src/daemons/onu_optics.py` | `/usr/local/bin/onu_optics.py` and `/usr/local/lib/olt/onu_optics.py` |
| `src/daemons/ipfix_exporter.py` | `/usr/local/bin/ipfix_exporter` and `/usr/local/lib/olt/ipfix_exporter.py` |

## What is not here

YANG models, device extensions, seeds, precompiled sysrepo repositories,
capability allowlists and the proxy source live in the base images. See
[the distribution boundary](../explanation/public-overlay.md).
