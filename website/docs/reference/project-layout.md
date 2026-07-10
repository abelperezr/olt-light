---
sidebar_position: 1
---

# Estructura del proyecto

```
Dockerfile              overlay: copia src/ sobre la imagen base
build.sh                check (pruebas) + build de la imagen personalizada
pyproject.toml          metadatos del paquete light_olt
src/
  ecli                  ejecutable del eCLI (shell de login por SSH)
  light_olt/            paquete Python con la lógica del eCLI
  daemons/
    onu_dhcp.py         suscriptores DHCP de las ONUs (DORA/SARR)
    onu_optics.py       niveles ópticos por ONU (operational)
    ipfix_exporter.py   telemetría IPFIX sintética
tests/                  pruebas unitarias del overlay
examples/
  lab.clab.yml          laboratorio containerlab: BNG + OLT + proxy
  docker-compose.yml    smoke test mínimo: OLT + proxy
website/                esta documentación (Docusaurus, es/en)
```

## Rutas dentro de la imagen

El supervisor de arranque de la imagen base espera los componentes en rutas
fijas. El Dockerfile las respeta; si las cambias, los daemons no arrancan.

| Origen en el repo | Destino en la imagen |
|---|---|
| `src/ecli` | `/usr/local/bin/ecli` |
| `src/light_olt/` | `/opt/light-olt/light_olt/` |
| `src/daemons/onu_dhcp.py` | `/usr/local/bin/onu_dhcp.py` |
| `src/daemons/onu_optics.py` | `/usr/local/bin/onu_optics.py` y `/usr/local/lib/olt/onu_optics.py` |
| `src/daemons/ipfix_exporter.py` | `/usr/local/bin/ipfix_exporter` y `/usr/local/lib/olt/ipfix_exporter.py` |

## Qué no está aquí

Modelos YANG, device extensions, seeds, repos sysrepo precompilados,
allowlists de capabilities y el código del proxy viven en las imágenes
base. Ver [el límite de distribución](../explanation/public-overlay.md).
