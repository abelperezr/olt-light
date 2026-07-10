---
sidebar_position: 4
---

# Customizing optics and IPFIX

## Per-ONU optical diagnostics

`src/daemons/onu_optics.py` publishes optical levels (RX/TX power, bias,
temperature, distance) as operational state for every **authenticated** ONU
on the LT plane. It's what answers when Altiplano or your NMS queries an
ONT's diagnostics.

The values are synthetic but coherent: to simulate a degraded fiber, a
far-away ONT, or out-of-threshold values for alarm testing, this is the
file to edit. Disable it with `ONU_OPTICS_ENABLED=0`.

## IPFIX telemetry

`src/daemons/ipfix_exporter.py` reads the YANG-accepted IPFIX configuration
on the LT plane and exports synthetic records to whatever collector that
configuration points at — handy for testing telemetry pipelines without
real traffic.

Disable it with `IPFIX_EMU_ENABLED=0`; the `IPFIX_EMU_*` variables tune
record cadence and volume (defaults are documented in the file's header).

## A note on paths

`ipfix_exporter.py` and `onu_optics.py` are installed **twice** in the
image: as executables under `/usr/local/bin/` and as importable modules
under `/usr/local/lib/olt/` (the optics daemon imports the exporter). The
Dockerfile keeps both copies in sync; if you bind-mount your working copy
to iterate, mount both paths.
