# Distribution boundary

This repository contains only the user-customizable overlay for Light OLT.
It does not contain Nokia YANG modules, device extensions, factory or platform
seed data, precompiled sysrepo repositories, capability allowlists, or proxy
source.
It also does not include Nokia Altiplano software or licenses, the official
Nokia Lightspan eCLI configuration guide, or any other vendor documentation.

The repository does include synthetic ONU operational-inventory XML fixtures
under `seeds/`. They are example lab inputs created for this project and are
not exports of the base image's factory or configuration datastores.

The base images are separate artifacts:

- `ghcr.io/abelperezr/olt-ls:0.0.1`
- `ghcr.io/abelperezr/olt-proxy:0.0.1`

Access to an image does not grant rights to redistribute files contained in
that image. Image publishers and users are responsible for verifying the
licenses and permissions that apply to their use.

Nokia and Lightspan are trademarks of Nokia Corporation. This project is an
independent emulator customization layer and is not endorsed by Nokia.
