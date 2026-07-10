---
sidebar_position: 2
---

# The distribution boundary

This project ships in two deliberately separate pieces.

**The base images** (`olt-ls`, `olt-proxy`) contain the Nokia YANG models,
device extensions, factory seeds and precompiled sysrepo repositories.
Those artifacts are what makes Altiplano accept the emulator as a
Lightspan, but they are not ours to redistribute as source: they live baked
inside the images and are not published in any repository.

**This repository** contains only the behavior layer: eCLI, DHCP, optics
and IPFIX. It's our own code, MIT licensed, and designed so you can modify
it without ever approaching the boundary: nothing you edit here requires
touching YANG or seeds.

The split also protects stability. The Altiplano alignment (revisions,
features, deviations, NACM) is fragile by design — changing it "just a
little" breaks onboarding in ways that are painful to debug. Keeping it
sealed in the base means an overlay customization can never break the
integration.

`./build.sh check` enforces the boundary in practice: it fails if it finds
directories that belong to the base (`yang`, `device-ext`, `seeds`) in the
tree. If your contribution needs them, the right place is a conversation in
the issues, not a pull request.

Nokia and Lightspan are trademarks of Nokia Corporation. This is an
independent project and is not endorsed by Nokia.
