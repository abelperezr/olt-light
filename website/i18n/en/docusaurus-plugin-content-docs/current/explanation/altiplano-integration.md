---
sidebar_position: 2
---

# Nokia Altiplano integration

Light OLT supports integration with Nokia Altiplano through the companion
NETCONF proxy image. Altiplano must connect to the **proxy**, not directly to
the OLT NETCONF ports. The proxy presents the capabilities and YANG library
expected by the device extensions.

## Supported profile

The supported profile is aligned with these 25.12 device extensions:

- `device-extension-ls-fx-fant-g-fx4-25.12-660`
- `device-extension-ls-fx-fglt-d-25.12-660`
- `device-extension-ls-fx-fwlt-c-25.12-660`
- `device-extension-ls-fx-ihub-fant-g-fx4-25.12-660`

The corresponding blueprint is:

```text
downloaded-ls-fx-25.12-25.12.2-REL_281
```

This list defines the reference combination for the integration. Other
blueprint and device-extension versions or combinations are not declared
compatible by this documentation.

## Obtaining the artifacts

Nokia Altiplano, the blueprint, and the device extensions listed above are
**not included** in this repository or in the Light OLT images. Nokia licenses,
installation packages, and official documentation are not included either.

Obtain the relevant information, software, blueprint, and device extensions
directly from Nokia through the appropriate authorized channels. Their names
are shown here only to identify the emulator's compatibility profile.

See [Deploying a lab](../how-to/deploy-lab.md) for the OLT/proxy topology and
[The distribution boundary](./public-overlay.md) for the public component
boundary.
