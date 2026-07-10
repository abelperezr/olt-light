---
sidebar_position: 5
---

# Validar una personalización

Tres niveles, del más barato al más completo. Los dos primeros no
necesitan Docker.

## Nivel 1: verificación estática

```bash
./build.sh check
```

Compila todo el código Python del overlay y corre las pruebas unitarias de
`tests/`. Como salvaguarda, también falla si aparecen en el árbol
directorios que pertenecen a las imágenes base (`yang`, `device-ext`,
`seeds`) — este repo no debe contenerlos nunca.

## Nivel 2: probar los daemons en seco

Los daemons aceptan `--dry-run`/`--once` para ejecutarse una vez sin tocar
el sistema:

```bash
PYTHONPATH=src/daemons python3 src/daemons/onu_dhcp.py --dry-run --once
```

Ten en cuenta que, fuera del modo seco, `onu_dhcp.py` crea y elimina
interfaces de red: ejecútalo dentro del contenedor o de un network
namespace de laboratorio.

## Nivel 3: smoke test

```bash
docker compose -f examples/docker-compose.yml up -d
docker compose -f examples/docker-compose.yml logs --tail=100 olt
ssh -p 2222 isadmin@localhost
```

Con la imagen recién construida arriba, verifica que los tres planos
levantan, que el eCLI responde y que los daemons aparecen en el log sin
errores. Para una validación end-to-end con BNG y Altiplano, pasa al
[laboratorio con containerlab](./deploy-lab.md).
