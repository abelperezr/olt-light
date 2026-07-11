---
sidebar_position: 1
slug: /
---

# Light OLT

Light OLT is a Nokia Lightspan FX OLT emulator that runs in a container.
It exposes three real NETCONF planes (IHUB, SHELF and LT) on
netopeer2/sysrepo, supports up to four LT cards (FGLT-D and FWLT-C), MPM
ports with GPON and XGS-PON ONUs, a Lightspan-style eCLI over SSH, and
emulation daemons for ONU DHCP, optics and IPFIX. It integrates end-to-end
with Nokia Altiplano Access Controller through a companion NETCONF proxy.

Nokia Altiplano, its licenses, and the official Nokia Lightspan eCLI
configuration guide are not included in this project or its container images.
Obtain any required vendor software and documentation through the appropriate
channels.

This repository is the **customization layer**: the full emulator ships
prebuilt in the base images, and only the parts you can safely modify live
here:

- the modular eCLI,
- ONU DHCP emulation,
- per-ONU optical diagnostics,
- the synthetic IPFIX exporter.

YANG models, device extensions, seeds and the proxy source are **not** in
this repo; they ship baked into the base images
(`ghcr.io/abelperezr/olt-ls` and `ghcr.io/abelperezr/olt-proxy`, both
public). The [distribution boundary](./explanation/public-overlay.md) explains
why.

## Where to start

- [Your first build](./tutorials/first-build.md): from clone to container in
  five minutes.
- [Deploying a lab](./how-to/deploy-lab.md): containerlab with a BNG, or docker
  compose for a smoke test.
- [Runtime reference](./reference/runtime.md): ports, credentials and
  environment variables.
