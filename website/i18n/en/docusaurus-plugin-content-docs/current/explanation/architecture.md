---
sidebar_position: 1
---

# Architecture

A real Lightspan FX OLT is not a single NETCONF device — it's several. The
shelf controller, the network card (IHUB) and each line card (LT) onboard
into Altiplano as separate devices, each with its own YANG schema. The
emulator reproduces exactly that:

```
Altiplano AC ──► olt-proxy ──► olt (light-olt)
                 831..836        ├─ IHUB   :831  (nokia-conf, SR OS)
                                 ├─ SHELF  :832  (FANT-G, ietf-hardware)
                                 ├─ LT1    :833  (FGLT-D or FWLT-C)
                                 └─ LT2-4  :834-836 (per-slot clones)
```

## The planes

Each plane is a netopeer2 instance with its own sysrepo repository and its
own YANG context (hence the `shm-size` requirement). The build's LT plane
is FGLT-D; the image also ships a precompiled FWLT-C repo that startup
clones into slots 2–4 according to `OLT_LT_SLOTS`, including MPM ports
where GPON and XGS channel terminations coexist on the same PON.

## The proxy

Altiplano validates in detail what the device announces: module revisions,
features, deviations. netopeer2 doesn't announce exactly what a real
Lightspan does, so the proxy sits in the middle and reconciles: it rewrites
hello and yang-library into the device extension's format, filters
capabilities per plane, normalizes replies, and intercepts a handful of
operations the emulator doesn't implement (the licensing subsystem's
actions, for instance, are answered locally). Without the proxy, Altiplano
onboarding fails at the alignment phase.

## The emulation daemons

On top of the planes run the daemons this repo lets you customize: the eCLI
(SSH :22), ONU DHCP (real IPoE subscribers against your BNG), per-ONU
optics and the IPFIX exporter. They all read their state from the planes'
sysrepo datastores — the same source of truth Altiplano sees.
