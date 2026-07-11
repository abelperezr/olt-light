---
sidebar_position: 6
---

# Solución de problemas

## El build falla en `check`

Lee la primera línea del error: o es un fallo de sintaxis/prueba en tu
código (el traceback apunta al archivo), o es la salvaguarda de directorios
restringidos — elimina `yang/`, `device-ext/` o `proxy/cap_allow/` del árbol;
no pertenecen a este repo. `seeds/` puede contener únicamente los inventarios
operativos sintéticos de ONUs del laboratorio.

## netopeer2 responde con timeouts o los planos no levantan

Casi siempre es memoria compartida insuficiente. Con más de un plano LT el
contenedor necesita `shm-size: 2GiB` o más. Verifica dentro del contenedor
con `df -h /dev/shm`.

## Una ONU no aparece

Las ONUs *detectadas* (autofind) vienen del XML del plano correspondiente:
`/seeds/onts_oper.xml` para LT1, `/seeds/onts_oper_ltN.xml` para los
clones. Revisa que el archivo esté montado en la ruta del plano correcto y
que los nombres de channel termination del XML coincidan con los del plano
(un CT `CT_LT2_...` en el archivo de LT1 crea una interfaz fantasma, no una
ONU visible).

## No sale DHCP hacia el BNG

Crear la ONT no basta: el daemon descubre suscriptores por el servicio L2
(vlan-sub-interface) encima de la UNI. Diagnostica con el modo seco:

```bash
docker exec <olt> python3 /usr/local/bin/onu_dhcp.py --dry-run --once
```

Si descubre el suscriptor pero no hay ACK en los logs, captura en el uplink
y revisa el BNG — el DISCOVER ya está saliendo.

## Altiplano no completa el onboarding

Confirma que el device en Altiplano apunta al **proxy** y no a la OLT
directa, y que el volumen `/data` del proxy persiste (si el host key SSH
cambia entre despliegues, Altiplano rechaza la conexión hasta actualizar la
huella).
