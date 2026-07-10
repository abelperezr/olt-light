---
sidebar_position: 3
---

# Personalizar el DHCP de las ONUs

`src/daemons/onu_dhcp.py` hace que las ONUs "existan" para tu BNG: por cada
suscriptor descubierto crea una interfaz macvlan con la MAC de la ONU y
ejecuta el intercambio DHCP real (DORA en v4, SARR en v6) por el uplink de
la OLT. Del lado del BNG se ve exactamente como un suscriptor IPoE.

## Cómo descubre suscriptores

El daemon sondea el running del plano LT (cada 20 s por defecto) buscando
**vlan-sub-interfaces** — el `l2-user` que crea el servicio VLAN de
Altiplano. Crear la ONT sola no dispara DHCP: hace falta el servicio L2
encima de la UNI, con un `frame-processing-profile` que resuelva a una
VLAN externa. Con eso el daemon resuelve el cableado contra el v-VPLS del
IHUB y levanta el cliente.

## Probar sin tocar nada

El modo seco muestra qué descubriría y qué interfaz usaría, sin crear
ninguna interfaz ni enviar paquetes:

```bash
PYTHONPATH=src/daemons python3 src/daemons/onu_dhcp.py --dry-run --once
```

Es la primera herramienta de diagnóstico cuando "no sale DHCP": te dice en
un solo tiro si el VSI existe, qué VLAN resolvió y por qué uplink saldría.
Recuerda que el daemon crea y elimina interfaces de red: pruébalo dentro
del contenedor o de un network namespace de laboratorio, no directamente
sobre tu máquina de trabajo.

## Ajustes por entorno

| Variable | Efecto |
|---|---|
| `ONU_DHCP_POLL` | Intervalo de reconciliación en segundos (default 20). |
| `ONU_DHCP_UPLINK` | Interfaz de salida cuando el wire no se puede derivar del IHUB (default `eth1`). |

Se definen en el nodo de la OLT del YAML de containerlab o compose, junto a
`OLT_LT_SLOTS`.

## Ciclo de trabajo

```bash
# edita src/daemons/onu_dhcp.py
./build.sh check && ./build.sh
# redespliega y mira los logs del daemon
docker logs -f <olt> 2>&1 | grep onu-dhcp
```

La secuencia sana en el log es: `uplink map`, luego `mac=... wire=...` por
suscriptor, `macvlan suXXXXXXXX sobre ...` y finalmente
`DHCPv4 ACK <ip> (server ..., lease ...)`. Si ves el `wire=` pero nunca el
ACK, el DISCOVER está saliendo y el problema está del lado del BNG.
