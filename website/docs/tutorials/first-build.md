---
sidebar_position: 1
---

# Tu primera build

En este tutorial partes de cero y terminas con una imagen personalizada
corriendo. No hace falta hardware ni licencias: las imágenes base son
públicas.

## 1. Requisitos

Docker y Python 3.10 o superior. Nada más — las imágenes son públicas, así
que no necesitas autenticarte en GHCR.

## 2. Descargar las imágenes base

```bash
docker pull ghcr.io/abelperezr/olt-ls:0.0.1
docker pull ghcr.io/abelperezr/olt-proxy:0.0.1
```

## 3. Clonar y verificar

```bash
git clone https://github.com/abelperezr/olt-light
cd olt-light
./build.sh check
```

`check` compila el código Python del overlay y corre las pruebas unitarias.
También verifica, como salvaguarda, que nadie haya metido en el árbol
directorios que pertenecen a las imágenes base (`yang`, `device-ext`,
`proxy/cap_allow`): esos no deben existir en este repo. Los inventarios ONU
sintéticos de `seeds/` son parte intencional del ejemplo.

## 4. Construir tu imagen

```bash
./build.sh
```

El resultado es `light-olt:dev`. El build tarda segundos: solo se copia la
capa editable sobre la base, que ya trae todo lo pesado. Puedes cambiar la
base y el tag sin tocar archivos:

```bash
BASE_IMAGE=ghcr.io/abelperezr/olt-ls:0.0.1 \
IMAGE_TAG=ghcr.io/mi-usuario/mi-olt:dev \
./build.sh
```

## 5. Iniciar el entorno de ejemplo

El laboratorio de referencia usa containerlab: OLT + proxy NETCONF + un BNG
Nokia SR OS (para el BNG necesitas tu propia imagen y licencia; puedes
quitar ese nodo si solo quieres la pareja OLT + proxy).

```bash
cd examples
containerlab deploy -t lab.clab.yml
```

Prueba el eCLI:

```bash
ssh admin@172.30.30.10          # admin/admin
```

Y NETCONF directo a un plano:

```bash
ssh -s admin@172.30.30.10 -p 833 netconf    # admin/admin
```

Altiplano se apunta a la IP del **proxy** (172.30.30.11 en el ejemplo),
puertos 831 en adelante. El detalle de la topología está en
[Desplegar un laboratorio](../how-to/deploy-lab.md).

## 6. Tu primer cambio

Edita cualquier archivo bajo `src/` (por ejemplo, el mensaje de bienvenida
del eCLI), y repite:

```bash
./build.sh check && ./build.sh
containerlab deploy -t examples/lab.clab.yml --reconfigure
```

Ese es el ciclo completo: editar, verificar, reconstruir, redesplegar.
