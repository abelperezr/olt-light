---
sidebar_position: 3
---

# El límite de distribución

Este proyecto se publica en dos piezas deliberadamente separadas.

**Las imágenes base** (`olt-ls`, `olt-proxy`) contienen los modelos YANG de
Nokia, los device extensions, los seeds de fábrica y los repos sysrepo
precompilados. Esos artefactos son necesarios para que Altiplano acepte al
emulador como un Lightspan, pero no son nuestros para redistribuir como
fuente: viven horneados dentro de las imágenes y no se publican en ningún
repositorio.

**Tampoco se distribuyen productos ni documentación del fabricante.** El
proyecto y sus imágenes no incluyen Nokia Altiplano, licencias de Altiplano ni
la guía oficial de configuración del eCLI de Nokia Lightspan. La compatibilidad
con Altiplano no implica que el controlador forme parte del emulador.

**Este repositorio** contiene solo la capa de comportamiento: eCLI, DHCP,
óptica e IPFIX. Es código propio, con licencia MIT, y está diseñado para
que puedas modificarlo sin acercarte al límite: nada de lo que edites aquí
requiere tocar YANG ni los seeds de fábrica de la plataforma. Los XML públicos
de `seeds/` son solo inventarios operativos sintéticos de ONUs para el
laboratorio de ejemplo.

La imagen base ya incluye implementaciones funcionales de esos componentes,
pero el build de este repositorio parte de `olt-ls` y las reemplaza en las
rutas que usa el runtime. En particular, `src/ecli` sustituye
`/usr/local/bin/ecli` y `src/light_olt/` se instala en `/opt/light-olt/`.
El arranque, SSH y los planos NETCONF se heredan de la base, así que la imagen
resultante ejecuta el eCLI modificado sin tener que reconstruir los YANG ni
los repositorios sysrepo.

La separación también protege la estabilidad. El alineamiento con Altiplano
(revisiones, features, deviations, NACM) es frágil por diseño — cambiarlo
"un poquito" rompe el onboarding de formas difíciles de depurar. Al dejarlo
sellado en la base, una personalización del overlay nunca puede romper la
integración.

`./build.sh check` refuerza el límite en la práctica: falla si detecta en
el árbol directorios que pertenecen a la base (`yang`, `device-ext`,
`proxy/cap_allow`). Si tu contribución los necesita, el lugar correcto es una
conversación en los issues, no un pull request.

Nokia y Lightspan son marcas de Nokia Corporation. Este es un proyecto
independiente y no está avalado por Nokia.
