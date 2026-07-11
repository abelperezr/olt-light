---
sidebar_position: 2
---

# Personalizar el eCLI

El eCLI es el shell estilo Lightspan que atiende SSH en el puerto 22 del
contenedor (usuario `admin`, contraseña `admin`). Emula dos
dialectos: ConfD J-style para SHELF y LT, y MD-CLI SR OS para el IHUB, con
completado por TAB y ayuda con `?`.

El código vive en `src/ecli` (el ejecutable) y `src/light_olt/` (el paquete
con la lógica). La imagen lo instala en `/usr/local/bin/ecli`; esa ruta no
se puede mover porque el sshd de la base lo usa como shell de login de los
usuarios.

## Ciclo de trabajo

```bash
# 1. edita src/ecli o los módulos del paquete
# 2. verifica y reconstruye
./build.sh check && ./build.sh
# 3. prueba
docker compose -f examples/docker-compose.yml up -d
ssh -p 2222 admin@localhost
```

Para iterar más rápido puedes montar tu copia de trabajo directamente
sobre el binario, sin reconstruir:

```yaml
# fragmento de containerlab o compose
binds:
  - ./src/ecli:/usr/local/bin/ecli:ro
```

y reiniciar el contenedor entre pruebas.

## Qué respetar

- El eCLI opera los datastores a través de `sysrepocfg`/`sysrepoctl` vía
  sudo (la base ya trae el sudoers acotado para eso). No asumas acceso
  directo al SHM de sysrepo: pertenece a root.
- El completado se apoya en un índice de esquema que la base genera al
  construirse. Si el índice no está, el eCLI cae a una tabla curada — tu
  código debe tolerar ambos casos.
- Los nombres de contexto (`Board-LT1` a `Board-LT4`, planos IHUB/SHELF/LT)
  se derivan del inventario que expone el SHELF según `OLT_LT_SLOTS`; no
  los codifiques a mano.
