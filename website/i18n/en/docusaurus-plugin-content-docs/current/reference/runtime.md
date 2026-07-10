---
sidebar_position: 2
---

# Runtime reference

## Ports

| Port | Service |
|---|---|
| 22 | eCLI over SSH (`isadmin`/`isadmin`, `admin`/`admin`) |
| 831 | NETCONF, IHUB plane |
| 832 | NETCONF, SHELF plane |
| 833 | NETCONF, LT1 |
| 834–836 | NETCONF, LT2–LT4 (only when the slot is enabled) |

NETCONF credentials: `admin`/`admin` on every plane. Altiplano must point
at the **proxy**, which exposes the same ports.

## OLT environment variables

| Variable | Effect |
|---|---|
| `OLT_LT_SLOTS` | Card per slot, e.g. `"1=FGLT-D,2=FWLT-C"`. Slot N listens on 832+N. |
| `OLT_LT_PLANES` | Simple alternative: number of LT planes (1–4), all of the build's type. |
| `ONU_DHCP_POLL` | DHCP daemon interval in seconds (default 20). |
| `ONU_DHCP_UPLINK` | Fallback uplink for subscribers (default `eth1`). |
| `ONU_OPTICS_ENABLED` | `0` disables optical diagnostics. |
| `IPFIX_EMU_ENABLED` | `0` disables the IPFIX exporter. |

With more than one LT plane the container needs `shm-size: 2GiB` or more.

## Proxy environment variables

| Variable | Effect |
|---|---|
| `UPSTREAM_HOST` | OLT address (emulated or real). |
| `PLANES` | `LISTEN:UPSTREAM_PORT` pairs per plane; the default covers 831–836. |
| `PROXY_USER` / `PROXY_PASSWORD` | Credentials Altiplano uses against the proxy. |
| `UPSTREAM_USER` / `UPSTREAM_PASSWORD` | Credentials the proxy uses towards the OLT. |

## Autofind ONUs

Each LT plane takes its detected-ONU inventory from an XML file:
`/seeds/onts_oper.xml` for LT1 and `/seeds/onts_oper_lt2.xml` through
`..._lt4.xml` for the clones (falling back to the global file when a
per-plane one doesn't exist). Files reload on change — bind-mount them and
edit the inventory live.

## Resource footprint

With 4 LT planes the baseline is around 1–1.5 GB of RAM. *Detected* ONUs
are cheap (~2 KB each); *active DHCP subscribers* cost more (~0.5 MB each
across threads, sockets and the macvlan). When scaling subscribers, the
first bottleneck is usually the lab's BNG, not the OLT.
