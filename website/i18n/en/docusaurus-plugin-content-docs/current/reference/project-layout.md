---
sidebar_position: 1
---

# Project layout

```
.github/workflows/
  pages.yml             builds and deploys the documentation to Pages
Dockerfile              overlay: copies src/ on top of the base image
build.sh                check (tests) + build of the customized image
pyproject.toml          light_olt package metadata
README.md               introduction and quick start
NOTICE.md               distribution boundary and third-party notices
src/
  ecli                  eCLI executable (SSH login shell)
  light_olt/            Python package with the eCLI logic
  daemons/
    onu_dhcp.py         ONU DHCP subscribers (DORA/SARR)
    onu_optics.py       per-ONU optical levels (operational)
    ipfix_exporter.py   synthetic IPFIX telemetry
tests/                  overlay unit tests
seeds/
  onts_oper.xml         synthetic ONU inventory for LT1
  onts_oper_gpon_xgs.xml
                        synthetic GPON/XGS-PON inventory for LT2
examples/
  lab.clab.yml          containerlab lab: BNG + OLT + proxy
  docker-compose.yml    minimal smoke test: OLT + proxy
  config-bng/
    bng.txt             example Nokia SR OS BNG configuration
website/                this documentation (Docusaurus, es/en)
```

The files under `seeds/` are editable operational-inventory fixtures for the
lab. They are not exports of the base image's factory seeds.
`examples/config-bng/bng.txt` configures the example BNG node; users must
provide their own Nokia SR OS image and license.

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

YANG models, device extensions, factory or configuration seeds, precompiled
sysrepo repositories, capability allowlists and the proxy source live in the
base images. See [the distribution boundary](../explanation/public-overlay.md).
