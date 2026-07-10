---
sidebar_position: 1
---

# Arquitectura

Una OLT Lightspan FX real no es un solo equipo NETCONF: son varios. El
controlador de shelf, la tarjeta de red (IHUB) y cada tarjeta de línea (LT)
se integran en Altiplano como devices separados, cada uno con su propio
esquema YANG. El emulador reproduce exactamente eso:

```
Altiplano AC ──► olt-proxy ──► olt (light-olt)
                 831..836        ├─ IHUB   :831  (nokia-conf, SR OS)
                                 ├─ SHELF  :832  (FANT-G, ietf-hardware)
                                 ├─ LT1    :833  (FGLT-D o FWLT-C)
                                 └─ LT2-4  :834-836 (clones por slot)
```

## Los planos

Cada plano es una instancia de netopeer2 con su propio repositorio sysrepo
y su propio contexto YANG (de ahí el requisito de `shm-size`). El plano LT
del build es FGLT-D; la imagen trae además un repo FWLT-C precompilado que
el arranque clona a los slots 2–4 según `OLT_LT_SLOTS`, incluyendo puertos
MPM donde conviven channel terminations GPON y XGS sobre el mismo PON.

## El proxy

Altiplano valida al detalle qué anuncia el equipo: revisiones de módulos,
features, deviations. netopeer2 no anuncia exactamente lo mismo que un
Lightspan real, así que el proxy se sienta en medio y reconcilia: reescribe
hello y yang-library al formato del device extension, filtra capabilities
por plano, normaliza respuestas e intercepta un puñado de operaciones que
el emulador no implementa (por ejemplo, los actions del subsistema de
licencias, que responde localmente). Sin el proxy, el onboarding en
Altiplano falla en la fase de alineamiento.

## Los daemons de emulación

Sobre los planos corren los daemons que este repo te deja personalizar: el
eCLI (SSH :22), el DHCP de ONUs (suscriptores IPoE reales contra tu BNG),
la óptica por ONU y el exportador IPFIX. Todos leen su estado de los
datastores sysrepo de los planos — la misma fuente de verdad que ve
Altiplano.
