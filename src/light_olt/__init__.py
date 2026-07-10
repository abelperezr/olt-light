"""
Light OLT — Capa de personalización pública para el emulador OLT.

Este paquete expone la CLI interactiva (eCLI) y los daemons auxiliares que
extienden la imagen base del emulador sin modificar su código fuente.

Componentes principales
-----------------------
- **light_olt.cli** : CLI interactiva multi-plano (IHUB, SHELF, LT) con
  sintaxis estilo ConfD/SR Linux, soporte de configuración transaccional,
  completion TAB y forward entre planos.
- **light_olt.daemons.onu_dhcp** : Emulación de suscriptores IPoE (DORA
  DHCPv4 / SARR DHCPv6) sobre macvlan, con Option 82 y autenticación ESM.
- **light_olt.daemons.ipfix_exporter** : Exportador IPFIX sintético que
  convierte la configuración YANG (ietf-ipfix-psamp) en telemetría Nokia
  Lightspan hacia colectores Pazel/ClickHouse.
- **light_olt.daemons.onu_optics** : Generador de diagnósticos ópticos
  operacionales por ONU (tx-bias, rx/tx-power, temperatura) con valores
  deterministas por serial y jitter temporal.

Arquitectura
------------
La imagen base provee sysrepo + netopeer2 + YANGs Nokia/BBF/IETF. Esta capa
añade:

1. **Planos CLI** : Cada plano (ihub, shelf, lt[N]) expone su propio puerto
   NETCONF (831/832/833...) y repo sysrepo independiente (/repo/ihub,
   /repo/shelf, /repo/lt...). La CLI navega el esquema YANG combinado
   (índice generado en build + fallback curado) y serializa ediciones vía
   sysrepocfg (con sudo cuando corre como usuario no root).

2. **Daemons de plano de datos** : Corren como procesos largos en el
   contenedor, leen running datastore vía sysrepocfg, derivan estado
   (suscriptores, inventario, contadores) y lo inyectan en operational
   datastore usando `oper_push` (igual que el autofind de Altiplano).

3. **Inventario compartido** : `ipfix_exporter` construye el inventario de
   PONs/ONUs (configurado + seed fallback) con gate de autenticación;
   `onu_optics` y `onu_dhcp` reutilizan esa lógica para coherencia.

Variables de entorno clave
--------------------------
- `ECLI_COMMIT_POLL_SECONDS` : polling commit watcher (def 1.0s)
- `ONU_DHCP_POLL` : reconciliación suscriptores (def 20s)
- `IPFIX_EMU_INTERVAL_SECS` : ciclo exportación IPFIX (def 15s)
- `ONU_OPTICS_REFRESH_SECS` : refresco diagnósticos ópticos (def 30s)
- `SYSREPO_REPOSITORY_PATH` / `SYSREPO_SHM_PREFIX` : inyectados por plano

Puntos de entrada
-----------------
- `light-olt` (console script) -> `light_olt.cli.main:main`
- `onu_dhcp.py` / `ipfix_exporter.py` / `onu_optics.py` : ejecutables directos
"""

__all__ = ["cli"]
