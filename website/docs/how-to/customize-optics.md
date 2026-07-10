---
sidebar_position: 4
---

# Personalizar óptica e IPFIX

## Diagnósticos ópticos por ONU

`src/daemons/onu_optics.py` publica niveles ópticos (potencia RX/TX, bias,
temperatura, distancia) como estado operational por cada ONU
**autenticada** en el plano LT. Es lo que responde cuando Altiplano o tu
NMS consultan los diagnósticos de una ONT.

Los valores son sintéticos pero coherentes: si quieres simular una fibra
degradada, una ONT lejana o valores fuera de umbral para probar alarmas,
este es el archivo a editar. Se desactiva con `ONU_OPTICS_ENABLED=0`.

## Telemetría IPFIX

`src/daemons/ipfix_exporter.py` lee la configuración IPFIX aceptada por
YANG en el plano LT y exporta registros sintéticos hacia el collector que
esa configuración indique — útil para probar pipelines de telemetría sin
tráfico real.

Se desactiva con `IPFIX_EMU_ENABLED=0`, y las variables `IPFIX_EMU_*`
ajustan cadencia y volumen de los registros (los defaults están documentados
en la cabecera del propio archivo).

## Nota sobre las rutas

`ipfix_exporter.py` y `onu_optics.py` se instalan **dos veces** en la
imagen: como ejecutables en `/usr/local/bin/` y como módulos importables en
`/usr/local/lib/olt/` (el daemon de óptica importa el exportador). El
Dockerfile ya mantiene ambas copias sincronizadas; si montas tu copia de
trabajo por bind para iterar, monta las dos rutas.
