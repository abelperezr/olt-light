---
sidebar_position: 2
---

# El límite de distribución

Este proyecto se publica en dos piezas deliberadamente separadas.

**Las imágenes base** (`olt-ls`, `olt-proxy`) contienen los modelos YANG de
Nokia, los device extensions, los seeds de fábrica y los repos sysrepo
precompilados. Esos artefactos son necesarios para que Altiplano acepte al
emulador como un Lightspan, pero no son nuestros para redistribuir como
fuente: viven horneados dentro de las imágenes y no se publican en ningún
repositorio.

**Este repositorio** contiene solo la capa de comportamiento: eCLI, DHCP,
óptica e IPFIX. Es código propio, con licencia MIT, y está diseñado para
que puedas modificarlo sin acercarte al límite: nada de lo que edites aquí
requiere tocar YANG ni seeds.

La separación también protege la estabilidad. El alineamiento con Altiplano
(revisiones, features, deviations, NACM) es frágil por diseño — cambiarlo
"un poquito" rompe el onboarding de formas difíciles de depurar. Al dejarlo
sellado en la base, una personalización del overlay nunca puede romper la
integración.

`./build.sh check` refuerza el límite en la práctica: falla si detecta en
el árbol directorios que pertenecen a la base (`yang`, `device-ext`,
`seeds`). Si tu contribución los necesita, el lugar correcto es una
conversación en los issues, no un pull request.

Nokia y Lightspan son marcas de Nokia Corporation. Este es un proyecto
independiente y no está avalado por Nokia.
