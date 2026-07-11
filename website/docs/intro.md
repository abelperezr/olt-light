---
sidebar_position: 1
slug: /
---

# Light OLT

Light OLT es un emulador de OLT Nokia Lightspan FX que corre en un
contenedor. Expone tres planos NETCONF reales (IHUB, SHELF y LT) sobre
netopeer2/sysrepo, soporta hasta cuatro tarjetas LT (FGLT-D y FWLT-C),
puertos MPM con ONUs GPON y XGS-PON, un eCLI estilo Lightspan por SSH y
daemons de emulación para DHCP de ONUs, óptica e IPFIX. Se integra
end-to-end con Nokia Altiplano Access Controller a través de un proxy
NETCONF que acompaña a la imagen.

Nokia Altiplano, sus licencias y la guía oficial de configuración del eCLI
de Nokia Lightspan no forman parte del proyecto ni de las imágenes. Debes
obtener cualquier software o documentación del fabricante por los canales
correspondientes.

Este repositorio es la **capa de personalización**: el emulador completo
viene precompilado en las imágenes base, y aquí vive únicamente lo que
puedes modificar sin romper el alineamiento con Altiplano:

- el eCLI modular,
- la emulación DHCP de las ONUs,
- los diagnósticos ópticos por ONU,
- el exportador IPFIX sintético.

Los modelos YANG, los device extensions, los seeds de fábrica y el código del
proxy **no** están en este repo; van horneados en las imágenes base
(`ghcr.io/abelperezr/olt-ls` y `ghcr.io/abelperezr/olt-proxy`, ambas
públicas). El [límite de distribución](./explanation/public-overlay.md) explica
el porqué.

Los XML de `seeds/` sí son públicos: son inventarios operativos sintéticos de
ONUs usados por el laboratorio de ejemplo, no seeds de configuración de la
plataforma.

## Por dónde empezar

- [Tu primera build](./tutorials/first-build.md): del clon al contenedor en
  cinco minutos.
- [Desplegar un laboratorio](./how-to/deploy-lab.md): containerlab con BNG, o
  docker compose para un smoke test.
- [Referencia de runtime](./reference/runtime.md): puertos, credenciales y
  variables de entorno.
- [Integración con Nokia Altiplano](./explanation/altiplano-integration.md):
  blueprint y device extensions compatibles.
