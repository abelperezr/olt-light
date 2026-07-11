---
sidebar_position: 2
---

# Integración con Nokia Altiplano

Light OLT soporta integración con Nokia Altiplano mediante el proxy NETCONF
incluido como imagen complementaria. Altiplano debe conectarse al **proxy**, no
directamente a los puertos NETCONF de la OLT. El proxy presenta las
capabilities y la YANG library esperadas por los device extensions.

## Perfil compatible

El perfil soportado está alineado con los siguientes device extensions 25.12:

- `device-extension-ls-fx-fant-g-fx4-25.12-660`
- `device-extension-ls-fx-fglt-d-25.12-660`
- `device-extension-ls-fx-fwlt-c-25.12-660`
- `device-extension-ls-fx-ihub-fant-g-fx4-25.12-660`

El blueprint correspondiente es:

```text
downloaded-ls-fx-25.12-25.12.2-REL_281
```

Esta lista define la combinación de referencia para la integración. Otras
versiones o combinaciones de blueprint y device extensions no se declaran
compatibles en esta documentación.

## Obtención de los artefactos

Nokia Altiplano, el blueprint y los device extensions anteriores **no están
incluidos** en este repositorio ni en las imágenes de Light OLT. Tampoco se
incluyen licencias, paquetes de instalación ni documentación oficial de Nokia.

La información, el software, el blueprint y los device extensions deben
obtenerse directamente a través de Nokia y de los canales autorizados que
correspondan. Los nombres se muestran aquí únicamente para identificar el
perfil de compatibilidad del emulador.

Consulta [Desplegar un laboratorio](../how-to/deploy-lab.md) para la topología
OLT/proxy y [El límite de distribución](./public-overlay.md) para conocer qué
componentes son públicos.
