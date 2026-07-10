---
sidebar_position: 2
---

# Referencia de runtime

## Puertos

| Puerto | Servicio |
|---|---|
| 22 | eCLI por SSH (`isadmin`/`isadmin`, `admin`/`admin`) |
| 831 | NETCONF plano IHUB |
| 832 | NETCONF plano SHELF |
| 833 | NETCONF LT1 |
| 834–836 | NETCONF LT2–LT4 (solo si el slot está habilitado) |

Credenciales NETCONF: `admin`/`admin` en todos los planos. Altiplano debe
apuntar al **proxy**, que expone los mismos puertos.

## Variables de entorno de la OLT

| Variable | Efecto |
|---|---|
| `OLT_LT_SLOTS` | Tarjeta por slot, ej. `"1=FGLT-D,2=FWLT-C"`. El slot N escucha en 832+N. |
| `OLT_LT_PLANES` | Alternativa simple: número de planos LT (1–4), todos del tipo del build. |
| `ONU_DHCP_POLL` | Intervalo del daemon DHCP en segundos (default 20). |
| `ONU_DHCP_UPLINK` | Uplink de respaldo para los suscriptores (default `eth1`). |
| `ONU_OPTICS_ENABLED` | `0` desactiva los diagnósticos ópticos. |
| `IPFIX_EMU_ENABLED` | `0` desactiva el exportador IPFIX. |

Con más de un plano LT el contenedor necesita `shm-size: 2GiB` o más.

## Variables de entorno del proxy

| Variable | Efecto |
|---|---|
| `UPSTREAM_HOST` | IP de la OLT (emulada o real). |
| `PLANES` | Pares `ESCUCHA:PUERTO_UPSTREAM` por plano; el default cubre 831–836. |
| `PROXY_USER` / `PROXY_PASSWORD` | Credenciales que Altiplano usa contra el proxy. |
| `UPSTREAM_USER` / `UPSTREAM_PASSWORD` | Credenciales del proxy hacia la OLT. |

## ONUs autofind

Cada plano LT toma su inventario de ONUs detectadas de un XML:
`/seeds/onts_oper.xml` para LT1 y `/seeds/onts_oper_lt2.xml` a
`..._lt4.xml` para los clones (con fallback al global si el archivo por
plano no existe). Los archivos se recargan al cambiar — puedes editar el
inventario en caliente montándolos por bind.

## Huella de recursos

Con 4 planos LT el baseline ronda 1–1.5 GB de RAM. Las ONUs *detectadas*
son baratas (~2 KB cada una); los suscriptores *DHCP activos* cuestan más
(~0.5 MB cada uno entre hilos, sockets y macvlan). El primer límite al
escalar suscriptores suele ser el BNG del laboratorio, no la OLT.
