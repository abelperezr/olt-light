---
sidebar_position: 1
---

# Desplegar un laboratorio

## Con containerlab (recomendado)

`examples/lab.clab.yml` levanta el trío completo: BNG SR OS, OLT y proxy
NETCONF. El nodo del BNG requiere tu propia imagen SR-SIM y licencia de
Nokia (no son redistribuibles); si no las tienes, borra ese nodo y el link
— la OLT y el proxy funcionan solos.

```bash
cd examples
containerlab deploy -t lab.clab.yml
```

Las decisiones importantes del YAML:

- **`shm-size: 4GiB`** en la OLT. Obligatorio con más de un plano LT: cada
  contexto sysrepo consume su propia memoria compartida, y quedarse corto
  se manifiesta como timeouts de RPC en netopeer2.
- **`OLT_LT_SLOTS`** define el inventario de tarjetas por slot, por ejemplo
  `"1=FGLT-D,2=FWLT-C"`. El slot N escucha NETCONF en el puerto 832+N. Se
  aplica al arranque; cambiar de layout es editar la variable y redesplegar.
- **Seeds de ONUs por plano**: `/seeds/onts_oper.xml` alimenta el autofind
  de LT1, y `/seeds/onts_oper_lt2.xml` a `..._lt4.xml` el de cada clon. Si
  un clon no tiene archivo propio, hereda el global. Los archivos se
  recargan solos al cambiar su mtime — puedes agregar o quitar ONUs en
  caliente.
- **`config-bng/bng.txt`** contiene la configuración de arranque de ejemplo
  para el BNG SR OS. La imagen y la licencia del BNG no se distribuyen.
- **El proxy persiste su host key en `/data`**: monta un volumen para que
  Altiplano no vea cambiar la identidad SSH del equipo en cada redeploy.

Altiplano (device-fx) se apunta a la IP del **proxy**, no a la OLT:
el proxy reescribe hello y yang-library al formato que el plug espera.
Consulta [Integración con Nokia Altiplano](../explanation/altiplano-integration.md)
para el blueprint y los device extensions compatibles.

## Con docker compose (smoke test)

Para verificar una personalización sin containerlab hay un compose mínimo
con OLT + proxy:

```bash
docker compose -f examples/docker-compose.yml up -d
docker compose -f examples/docker-compose.yml logs --tail=100 olt
ssh -p 2222 admin@localhost
```

Se puede apuntar a otra imagen sin editar el archivo:

```bash
OLT_IMAGE=light-olt:test docker compose -f examples/docker-compose.yml up -d
```
