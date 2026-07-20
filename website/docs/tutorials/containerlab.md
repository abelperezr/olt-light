---
sidebar_position: 2
title: Containerlab
description: Despliega Light OLT y un BNG Nokia SR OS en un laboratorio Containerlab.
---

# Desplegar Light OLT con Containerlab

En este tutorial prepararás un laboratorio con Light OLT conectada a un BNG Nokia SR OS. El proxy NETCONF es opcional y solo se necesita para integrar la OLT con Nokia Altiplano.

## 1. Requisitos

- Docker.
- Python 3.10 o superior.
- Containerlab.
- Una imagen de Nokia SR-SIM y su licencia si utilizarás el BNG del ejemplo.

## 2. Descargar las imágenes base

Descarga la imagen de la OLT:

```bash
docker pull ghcr.io/abelperezr/olt-ls:0.0.1
```

Si utilizarás Nokia Altiplano, descarga también el proxy NETCONF:

```bash
docker pull ghcr.io/abelperezr/olt-proxy:0.0.1
```

## 3. Clonar el repositorio

```bash
git clone https://github.com/abelperezr/olt-light.git
cd olt-light
```

## 4. Preparar la carpeta del laboratorio

Crea la estructura del laboratorio y copia los inventarios de ONTs:

```bash
mkdir -p clab/config-bng clab/configs/license
cp -R seeds clab/
```

El repositorio contiene en `examples/config-bng/` una configuración de referencia para un BNG Nokia SR OS. Cópiala junto con la topología de ejemplo:

```bash
cp examples/config-bng/bng.txt clab/config-bng/
cp examples/lab.clab.yml clab/
```

Copia tu licencia de SR-SIM en la ruta que espera la topología:

```bash
cp <ruta-de-la-licencia>/SR_SIM_license.txt clab/configs/license/
```

Edita `clab/lab.clab.yml` antes de desplegarlo:

1. Sustituye `<your-registry>/srsim:25.10.r2` por el nombre de tu imagen SR-SIM.
2. Cambia la imagen del nodo `olt` de `light-olt:dev` a `ghcr.io/abelperezr/olt-ls:0.0.1`.
3. Cambia los dos bind mounts de `../seeds/` a `./seeds/`, porque en este tutorial los inventarios están dentro de `clab/`.
4. Si no utilizarás Nokia Altiplano, elimina el nodo completo `olt-proxy` de la topología.

## 5. Habilitar persistencia de la OLT (opcional)

Crea el directorio persistente:

```bash
mkdir -p clab/persist/olt/repo
```

Después, descomenta este bind mount en el nodo `olt` de `clab/lab.clab.yml`:

```yaml
- ./persist/olt/repo:/persist/repo
```

Si utilizarás el proxy, crea también su directorio de datos para conservar la identidad SSH entre despliegues:

```bash
mkdir -p clab/persist/olt-proxy/data
```

## 6. Desplegar el laboratorio

```bash
cd clab
sudo containerlab deploy -t lab.clab.yml
```

## 7. Configurar la OLT

- Sin Nokia Altiplano, continúa con la [Guía del eCLI](../how-to/cli-guide.md).
- Con Nokia Altiplano, continúa con [Integración con Nokia Altiplano](../explanation/altiplano-integration.md).

## 8. Validar las ONTs autenticadas

Sigue los eventos del daemon `onu-dhcp`, sustituyendo el marcador por el nombre del contenedor de la OLT:

```bash
docker logs -f <nombre-contenedor-olt> 2>&1 | grep onu-dhcp
```

Por ejemplo, si el contenedor se llama `olt`:

```bash
docker logs -f olt 2>&1 | grep onu-dhcp
```

Cuando una VSI tenga una v-VPLS habilitada y el BNG conceda una dirección, el log mostrará el uplink seleccionado con `via=v-vpls` y los mensajes `DHCPv4 ACK` o `DHCPv6 REPLY`.
