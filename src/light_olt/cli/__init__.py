"""
eCLI modular para planos IHUB, SHELF y LT.

Implementa una CLI interactiva estilo ConfD/SR Linux que expone el esquema YANG
combinado de cada plano mediante sysrepo. Características:

- Navegación por modos (operacional -> configuración -> submodos) con pila de
  contextos y prompt dinámico (hostname + path + keys).
- Completion TAB/? estilo ConfD: builtins, nodos YANG, instancias existentes
  (list keys), y forward targets derivados del inventario hardware (SHELF).
- Comandos builtin operacionales: config, show, forward, ping, logout, pwd, id,
  who, help. En modo config: commit, exit, top, end, abort, no, do, show, pwd,
  help.
- Edición transaccional: candidate datastore local, commit atómico a
  running+startup vía sysrepocfg (sudo si no es root), rollback automático
  al salir sin commit.
- Commit watcher: notifica commits externos (NETCONF) emulando mensaje async
  de ConfD ("Commit performed by <user> via ssh using netconf").
- Forward CLI: desde SHELF -> `forward cli to <ihub|lt-N>` salta al plano
  destino manteniendo la sesión SSH.

Arquitectura interna
--------------------
- `ConfdCLI` : planos SHELF y LT (YANG IETF/BBF/Nokia genérico).
- `MdCli`    : plano IHUB (nokia-conf, estilo MD-CLI SR Linux).
- `Plane`    : backend sysrepo (backend.py) — cache de índices, XML, instancias.
- `EditSession` : construcción de candidate XML (editing.py).
- `resolve()` / `lookup()` : navegación de esquema con abreviación única
  (schema.py).
- `render_confd` / `render_md_flat` : formateo salida show (rendering.py).

Índice de esquema
-----------------
En build se genera `/etc/olt/cli_index_<plane>.json.gz` con yanglint
(`pyang -f jtox`). En runtime se fusiona con `fallback_tree()` (backend.py)
para reparar listas montadas (onus/onu, interfaces/interface, etc.) que
yanglint deja incompletas. La fusión da prioridad al generado, y el curado
solo rellena huecos (keys, loose, módulos).

Variables de entorno
--------------------
- `ECLI_COMMIT_POLL_SECONDS` : intervalo commit watcher (def 1.0s)
- `ECLI_SIG_CACHE_SECONDS`   : cache firma running datastore (def 0.15s)
- `ECLI_XML_CACHE_MAX`       : entradas cache XML export (def 24)
"""

from .common import ECLI_VERSION

__all__ = ["ECLI_VERSION"]
