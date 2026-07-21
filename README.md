# Light OLT customization layer

[Español](#español) · [English](#english) · [Docs](https://abelperezr.github.io/olt-light/docs/)

> **Si no necesitas modificar el eCLI ni los daemons, solo descarga las imágenes base y funcionan directamente.** Para más información sobre las imágenes, consulta la [documentación](https://abelperezr.github.io/olt-light/docs/) (español e inglés).
>
> **If you don't need to modify the eCLI or daemons, just pull the base images and they work out of the box.** For more information about the images, see the [documentation](https://abelperezr.github.io/olt-light/en/docs/) (English and Spanish).

This is the public, editable layer of the Light OLT emulator. The heavy part
of the emulator (NETCONF planes, YANG schema, factory seeds, startup logic) ships
prebuilt in the base images; this repo carries the four pieces you are meant
to hack on:

- the modular eCLI,
- ONU DHCP emulation,
- ONU optical diagnostics,
- synthetic IPFIX export.

No YANG modules, device extensions, factory seeds or proxy source live here.
The XML files under `seeds/` are editable, synthetic ONU inventory fixtures
for the example lab, not platform configuration. See [NOTICE.md](NOTICE.md)
for the distribution boundary.

## Español

Ni el repositorio ni las imágenes incluyen Nokia Altiplano, licencias de
Altiplano o la guía oficial de configuración del eCLI de Nokia Lightspan. El
software y la documentación del fabricante deben obtenerse por los canales
correspondientes.

### Inicio rápido

Requisitos: Docker y Python 3.10+. Las imágenes son públicas, no hace falta
autenticarse en GHCR.

```bash
docker pull ghcr.io/abelperezr/olt-light:0.0.1
docker pull ghcr.io/abelperezr/olt-proxy:0.0.1

./build.sh check     # pruebas locales
./build.sh           # construye light-olt:dev sobre la base
```

Para levantar un laboratorio completo (OLT + proxy + BNG) usa el ejemplo de
containerlab:

```bash
cd examples
containerlab deploy -t lab.clab.yml
ssh admin@<ip-olt>          # eCLI (admin/admin)
```

También hay un `examples/docker-compose.yml` mínimo (OLT + proxy) para un
smoke test rápido sin containerlab.

La imagen personalizada se llama `light-olt:dev` por defecto. Puedes cambiar
la base y el tag sin editar archivos:

```bash
BASE_IMAGE=ghcr.io/abelperezr/olt-light:0.0.1 \
IMAGE_TAG=ghcr.io/mi-usuario/mi-olt:dev \
./build.sh
```

La [documentación completa](https://abelperezr.github.io/olt-light/docs/)
cubre cómo añadir comandos al eCLI, cambiar el comportamiento DHCP, ajustar
la óptica o extender los registros IPFIX.

## English

Neither the repository nor the container images include Nokia Altiplano
software, Altiplano licenses, or the official Nokia Lightspan eCLI
configuration guide. Obtain any required vendor software and documentation
through the appropriate channels.

### Quick start

Requirements: Docker and Python 3.10+. The images are public — no GHCR
login needed.

```bash
docker pull ghcr.io/abelperezr/olt-light:0.0.1
docker pull ghcr.io/abelperezr/olt-proxy:0.0.1

./build.sh check     # local tests
./build.sh           # builds light-olt:dev on top of the base
```

To bring up a full lab (OLT + proxy + BNG) use the containerlab example:

```bash
cd examples
containerlab deploy -t lab.clab.yml
ssh admin@<olt-ip>          # eCLI (admin/admin)
```

A minimal `examples/docker-compose.yml` (OLT + proxy) is also included for a
quick smoke test without containerlab.

The customized image is tagged `light-olt:dev` by default. Override the base
and the output tag through environment variables:

```bash
BASE_IMAGE=ghcr.io/abelperezr/olt-light:0.0.1 \
IMAGE_TAG=ghcr.io/my-user/my-olt:dev \
./build.sh
```

The [full documentation](https://abelperezr.github.io/olt-light/en/docs/)
covers adding eCLI commands, changing DHCP behavior, tuning optical
diagnostics, and extending IPFIX records.

## What stays in the base images

The OLT and proxy base images are separate artifacts. This repository does
not expose their YANG models, device extensions, factory/platform seeds,
proxy source, or startup internals. See [NOTICE.md](NOTICE.md).

## License

The source code in this repository is MIT licensed. The base container
images and the files inside them may be governed by separate terms.
