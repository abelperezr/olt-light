---
sidebar_position: 6
title: Guía del eCLI
description: Acceso, navegación y aprovisionamiento básico de una ONT desde el eCLI de Light OLT.
---

# Guía del eCLI

Esta guía está dirigida a operadores que administran Light OLT directamente desde el eCLI, sin Nokia Altiplano ni otra plataforma de gestión. Explica cómo navegar entre los contextos de la OLT y cómo crear los objetos básicos de un servicio GPON para una ONT.

:::note Antes de conectarte

- Espera entre **uno y dos minutos** después de iniciar el contenedor antes de abrir la sesión SSH en el puerto 22.
- Si solo utilizarás el eCLI, no necesitas ejecutar la imagen `olt-proxy:0.0.1`.
- La imagen ya incluye parte de la configuración que se muestra en esta guía.

:::

Conéctate con las credenciales predeterminadas:

```bash title="Conexión SSH"
ssh admin@<dirección-de-la-olt>
# Contraseña: admin
```

Usa la tecla **Tab** para completar comandos y `?` para consultar las opciones disponibles en el contexto actual.

:::warning Alcance y soporte

No todas las operaciones se han validado mediante el eCLI. El código es público y puede modificarse y reconstruirse sobre la imagen base. Esta guía describe únicamente el comportamiento implementado por Light OLT y no sustituye la guía oficial de configuración del eCLI de Nokia Lightspan FX; solicítala a tu representante de Nokia.

:::

## Contenido

1. [Consultar la configuración de un contexto](#consultar-la-configuración-de-un-contexto).
2. [Cambiar de contexto en la OLT](#cambiar-de-contexto-en-la-olt).
3. [Cambiar el nombre del sistema](#cambiar-el-nombre-del-sistema).
4. [Consultar los puertos uplink](#consultar-los-puertos-uplink).
5. [Consultar el VPLS de gestión](#consultar-el-vpls-de-gestión).
6. [Consultar el IES de gestión](#consultar-el-ies-de-gestión).
7. [Crear la v-VPLS para la VLAN de la ONT](#crear-la-v-vpls-para-la-vlan-de-la-ont).
8. [Configurar un puerto PON](#configurar-un-puerto-pon).
9. [Crear la plantilla de ONU](#crear-la-plantilla-de-onu).
10. [Aprovisionar una ONT](#aprovisionar-una-ont).
11. [Crear los perfiles de servicio](#crear-los-perfiles-de-servicio).
12. [Crear el servicio de usuario de capa 2](#crear-el-servicio-de-usuario-de-capa-2).
13. [Aplicar el ejemplo de configuración completa](#ejemplo-de-configuración-completa).

## Consultar la configuración de un contexto

```text title="Comandos"
show full-configuration
```

## Cambiar de contexto en la OLT

```text title="Comandos"
forward cli to lt-1
```

Sustituye `lt-1` por `ihub`, `lt-2`, `lt-3` o `lt-4` para abrir otro contexto disponible.

## Cambiar el nombre del sistema

```text title="Comandos"
config
system hostname OLT-LAB
```

## Consultar los puertos uplink

Ejecuta esta sección en el contexto **IHUB**; consulta [Cambiar de contexto en la OLT](#cambiar-de-contexto-en-la-olt).

La imagen incluye los puertos `1/2/1` y `1/1/1`. El siguiente bloque muestra la configuración predeterminada de `1/2/1`. Para otras opciones, consulta la documentación de Nokia SR OS.

```text title="Configuración predeterminada"
port-id 1/2/1 { }
admin-state { enable }
description "10/100/Gig Ethernet TX" { }
forwarding-scope { load-sharing }
ethernet { }
ethernet { autonegotiate true }
ethernet { dot1q-etype 0x8100 }
ethernet { mode access }
ethernet { encap-type dot1q }
ethernet { speed 1000 }
ethernet { category regular }
ethernet { remark false }
ethernet { use-vlan-dot1q-etype false }
ethernet { hold-time }
ethernet { hold-time units seconds }
ethernet { lldp }
ethernet { lldp dest-mac nearest-bridge }
ethernet { lldp dest-mac nearest-bridge notification false }
ethernet { lldp dest-mac nearest-bridge port-id-subtype tx-local }
ethernet { lldp dest-mac nearest-bridge receive false }
ethernet { lldp dest-mac nearest-bridge transmit false }
ethernet { lldp dest-mac nearest-bridge tx-tlvs }
ethernet { lldp dest-mac nearest-bridge tx-tlvs port-desc false }
ethernet { lldp dest-mac nearest-bridge tx-tlvs sys-name false }
ethernet { lldp dest-mac nearest-bridge tx-tlvs sys-desc false }
ethernet { lldp dest-mac nearest-bridge tx-tlvs sys-cap false }
ethernet { lldp dest-mac nearest-bridge tx-mgmt-address system }
ethernet { lldp dest-mac nearest-bridge tx-mgmt-address system admin-state disable }
ethernet { lldp dest-mac nearest-bridge tx-mgmt-address system-ipv6 }
ethernet { lldp dest-mac nearest-bridge tx-mgmt-address system-ipv6 admin-state disable }
ethernet { lldp dest-mac nearest-bridge tx-mgmt-address node-ipv4 }
ethernet { lldp dest-mac nearest-bridge tx-mgmt-address node-ipv4 admin-state disable }
ethernet { lldp dest-mac nearest-bridge tx-mgmt-address node-ipv6 }
ethernet { lldp dest-mac nearest-bridge tx-mgmt-address node-ipv6 admin-state disable }
ethernet { lldp dest-mac nearest-non-tpmr }
ethernet { lldp dest-mac nearest-non-tpmr notification false }
ethernet { lldp dest-mac nearest-non-tpmr port-id-subtype tx-local }
ethernet { lldp dest-mac nearest-non-tpmr receive false }
ethernet { lldp dest-mac nearest-non-tpmr transmit false }
ethernet { lldp dest-mac nearest-non-tpmr tx-tlvs }
ethernet { lldp dest-mac nearest-non-tpmr tx-tlvs port-desc false }
ethernet { lldp dest-mac nearest-non-tpmr tx-tlvs sys-name false }
ethernet { lldp dest-mac nearest-non-tpmr tx-tlvs sys-desc false }
ethernet { lldp dest-mac nearest-non-tpmr tx-tlvs sys-cap false }
ethernet { lldp dest-mac nearest-non-tpmr tx-mgmt-address system }
ethernet { lldp dest-mac nearest-non-tpmr tx-mgmt-address system admin-state disable }
ethernet { lldp dest-mac nearest-non-tpmr tx-mgmt-address system-ipv6 }
ethernet { lldp dest-mac nearest-non-tpmr tx-mgmt-address system-ipv6 admin-state disable }
ethernet { lldp dest-mac nearest-non-tpmr tx-mgmt-address node-ipv4 }
ethernet { lldp dest-mac nearest-non-tpmr tx-mgmt-address node-ipv4 admin-state disable }
ethernet { lldp dest-mac nearest-non-tpmr tx-mgmt-address node-ipv6 }
ethernet { lldp dest-mac nearest-non-tpmr tx-mgmt-address node-ipv6 admin-state disable }
ethernet { lldp dest-mac nearest-customer }
ethernet { lldp dest-mac nearest-customer notification false }
ethernet { lldp dest-mac nearest-customer port-id-subtype tx-local }
ethernet { lldp dest-mac nearest-customer receive false }
ethernet { lldp dest-mac nearest-customer transmit false }
ethernet { lldp dest-mac nearest-customer tx-tlvs }
ethernet { lldp dest-mac nearest-customer tx-tlvs port-desc false }
ethernet { lldp dest-mac nearest-customer tx-tlvs sys-name false }
ethernet { lldp dest-mac nearest-customer tx-tlvs sys-desc false }
ethernet { lldp dest-mac nearest-customer tx-tlvs sys-cap false }
ethernet { lldp dest-mac nearest-customer tx-mgmt-address system }
ethernet { lldp dest-mac nearest-customer tx-mgmt-address system admin-state disable }
ethernet { lldp dest-mac nearest-customer tx-mgmt-address system-ipv6 }
ethernet { lldp dest-mac nearest-customer tx-mgmt-address system-ipv6 admin-state disable }
ethernet { lldp dest-mac nearest-customer tx-mgmt-address node-ipv4 }
ethernet { lldp dest-mac nearest-customer tx-mgmt-address node-ipv4 admin-state disable }
ethernet { lldp dest-mac nearest-customer tx-mgmt-address node-ipv6 }
ethernet { lldp dest-mac nearest-customer tx-mgmt-address node-ipv6 admin-state disable }
```

## Consultar el VPLS de gestión

Ejecuta esta consulta en **IHUB**. La imagen incluye el VPLS `vpls-MGMT` con la siguiente configuración predeterminada:

```text title="Configuración predeterminada"
service { vpls "vpls-MGMT" }
service { vpls "vpls-MGMT" service-id 50 }
service { vpls "vpls-MGMT" customer "1" }
service { vpls "vpls-MGMT" admin-state enable }
service { vpls "vpls-MGMT" service-mtu 1514 }
service { vpls "vpls-MGMT" m-vpls false }
service { vpls "vpls-MGMT" sgt-qos 1 }
service { vpls "vpls-MGMT" storm-control false }
service { vpls "vpls-MGMT" user-user-com false }
service { vpls "vpls-MGMT" v-vpls true }
service { vpls "vpls-MGMT" vlan 50 }
service { vpls "vpls-MGMT" fdb }
service { vpls "vpls-MGMT" fdb table }
service { vpls "vpls-MGMT" fdb table high-wmark 95 }
service { vpls "vpls-MGMT" fdb table low-wmark 90 }
service { vpls "vpls-MGMT" fdb table size 16384 }
service { vpls "vpls-MGMT" fdb mac-learning }
service { vpls "vpls-MGMT" fdb mac-learning learning true }
service { vpls "vpls-MGMT" fdb mac-learning aging true }
service { vpls "vpls-MGMT" fdb mac-learning local-age-time 300 }
service { vpls "vpls-MGMT" fdb mac-learning remote-age-time 900 }
service { vpls "vpls-MGMT" stp }
service { vpls "vpls-MGMT" stp admin-state disable }
service { vpls "vpls-MGMT" stp forward-delay 15 }
service { vpls "vpls-MGMT" stp hello-time 2 }
service { vpls "vpls-MGMT" stp hold-count 6 }
service { vpls "vpls-MGMT" stp maximum-age 20 }
service { vpls "vpls-MGMT" stp mode rstp }
service { vpls "vpls-MGMT" stp mst-maximum-hops 20 }
service { vpls "vpls-MGMT" stp priority 32768 }
service { vpls "vpls-MGMT" sap 1/2/1:50 }
service { vpls "vpls-MGMT" sap 1/2/1:50 admin-state enable }
service { vpls "vpls-MGMT" sap 1/2/1:50 enable-stats false }
service { vpls "vpls-MGMT" sap 1/2/1:50 stp }
service { vpls "vpls-MGMT" sap 1/2/1:50 stp admin-state disable }
service { vpls "vpls-MGMT" sap 1/2/1:50 stp auto-edge true }
service { vpls "vpls-MGMT" sap 1/2/1:50 stp edge-port false }
service { vpls "vpls-MGMT" sap 1/2/1:50 stp link-type pt-pt }
service { vpls "vpls-MGMT" sap 1/2/1:50 stp path-cost 10 }
service { vpls "vpls-MGMT" sap 1/2/1:50 stp priority 128 }
service { vpls "vpls-MGMT" sap 1/2/1:50 stp root-guard false }
service { vpls "vpls-MGMT" sap 1/2/1:50 fdb }
service { vpls "vpls-MGMT" sap 1/2/1:50 fdb mac-learning }
service { vpls "vpls-MGMT" sap 1/2/1:50 fdb mac-learning learning true }
service { vpls "vpls-MGMT" sap 1/2/1:50 fdb mac-learning aging true }
service { vpls "vpls-MGMT" sap 1/2/1:50 eth-cfm }
service { vpls "vpls-MGMT" sap 1/2/1:50 eth-cfm ais-enable false }
service { vpls "vpls-MGMT" ingress }
service { vpls "vpls-MGMT" ingress qos 1 }
service { vpls "vpls-MGMT" mac-move }
service { vpls "vpls-MGMT" mac-move allow-res-res false }
service { vpls "vpls-MGMT" mac-move allow-res-reg true }
service { vpls "vpls-MGMT" mac-move allow-reg-res false }
service { vpls "vpls-MGMT" mac-move log-enable false }
```

## Consultar el IES de gestión

Ejecuta esta consulta en **IHUB**. La imagen incluye el IES `MGMT` con la siguiente configuración predeterminada:

```text title="Configuración predeterminada"
A:admin@iHUB-OLT-LAB# service ies MGMT
[gl:configure service ies MGMT]
A:admin@iHUB-OLT-LAB# info flat
    service-name "MGMT" { }
    service-id 9999 { }
    customer "1" { }
    admin-state { enable }
    interface "to_BNG" { }
    interface "to_BNG" { admin-state enable }
    interface "to_BNG" { loopback false }
    interface "to_BNG" { oamsave false }
    interface "to_BNG" { sap 1/5/1:50 }
    interface "to_BNG" { sap 1/5/1:50 admin-state enable }
    interface "to_BNG" { ipv4 }
    interface "to_BNG" { ipv4 icmp }
    interface "to_BNG" { ipv4 icmp mask-reply true }
    interface "to_BNG" { ipv4 icmp ttl-expired }
    interface "to_BNG" { ipv4 icmp ttl-expired admin-state enable }
    interface "to_BNG" { ipv4 icmp ttl-expired number 100 }
    interface "to_BNG" { ipv4 icmp ttl-expired seconds 10 }
    interface "to_BNG" { ipv4 icmp unreachables }
    interface "to_BNG" { ipv4 icmp unreachables admin-state enable }
    interface "to_BNG" { ipv4 icmp unreachables number 100 }
    interface "to_BNG" { ipv4 icmp unreachables seconds 10 }
    interface "to_BNG" { ipv4 bfd }
    interface "to_BNG" { ipv4 bfd admin-state disable }
    interface "to_BNG" { ipv4 bfd transmit-interval 100 }
    interface "to_BNG" { ipv4 bfd receive 100 }
    interface "to_BNG" { ipv4 bfd multiplier 3 }
    interface "to_BNG" { ipv4 primary }
    interface "to_BNG" { ipv4 primary address 192.168.0.2 }
    interface "to_BNG" { ipv4 primary prefix-length 24 }
    interface "to_BNG" { ipv4 primary broadcast host-ones }
    interface "to_BNG" { ipv4 neighbor-discovery }
    interface "to_BNG" { ipv4 neighbor-discovery timeout 600 }
    interface "to_BNG" { ipv4 neighbor-discovery local-proxy-arp false }
    interface "to_BNG" { ipv4 neighbor-discovery limit }
    interface "to_BNG" { ipv4 neighbor-discovery limit log-only false }
    interface "to_BNG" { ipv4 neighbor-discovery limit threshold 90 }
    interface "to_BNG" { ipv4 dhcp }
    interface "to_BNG" { ipv4 dhcp admin-state disable }
    interface "to_BNG" { ipv4 dhcp src-ip-addr auto }
    interface "to_BNG" { ipv4 dhcp option-82 }
    interface "to_BNG" { ipv4 dhcp option-82 action keep }
    interface "to_BNG" { ipv4 dhcp lease-populate }
    interface "to_BNG" { ipv4 dhcp lease-populate max-leases 20480 }
    ingress { }
    ingress { qos 1 }
```

## Crear la v-VPLS para la VLAN de la ONT

El daemon `onu-dhcp` solo materializa un abonado cuando la VLAN de su VSI coincide con una v-VPLS habilitada en el IHUB. La v-VPLS también debe tener un SAP habilitado sobre un puerto físico incluido en el mapa de uplinks. En este ejemplo, el puerto `1/2/1` corresponde a `eth1` y la VLAN del abonado es la `10`.

```text title="Flujo del tráfico"
VSI_ONT-01_VEIP_HSI (VLAN 10)
             │
             ▼
onu-dhcp detecta la VSI habilitada
             │
             ▼
IHUB v-VPLS VLAN 10 → SAP 1/2/1:10
             │
             ▼
interfaz Linux eth1.10 + macvlan del abonado
             │
             ▼
DHCP DORA hacia el BNG
             │
             ▼
BNG recibe la petición
```

Ejecuta estos comandos en el contexto **IHUB**, dentro de `configure global`:

```text title="Comandos"
forward cli to ihub
configure global
service vpls 10
admin-state enable
service-name "10"
service-id 10
customer 1
admin-state enable
storm-control false
user-user-com false
v-vpls true
vlan 10
sap 1/2/1:10 admin-state enable
exit
mac-move allow-res-res false
mac-move allow-res-reg true
mac-move allow-reg-res false
commit
```

El resultado de `info flat` debe incluir:

```text title="Salida de verificación"
[gl:configure service vpls 10]
A:admin@iHUB-OLT-LAB# info flat
    service-name "10" { }
    service-id 10 { }
    customer "1" { }
    admin-state { enable }
    storm-control { false }
    user-user-com { false }
    v-vpls { true }
    vlan 10 { }
    sap 1/2/1:10 { }
    sap 1/2/1:10 { admin-state enable }
    mac-move { }
    mac-move { allow-res-res false }
    mac-move { allow-res-reg true }
    mac-move { allow-reg-res false }
```

## Configurar un puerto PON

Ejecuta las siguientes tareas en el contexto de la **LT** que contiene el puerto PON.

### Crear el transceptor SFP

```text title="Comandos"
config
hardware component PONSFP_1 class transceiver
parent C1
parent-rel-pos 1
model-name 3FE53441AA
```

#### Verificar el SFP

```text title="Salida de verificación"
OLT-LAB.LT1(config-component-PONSFP_1)# show full-configuration
component PONSFP_1
 class transceiver
 parent C1
 parent-rel-pos 1
 model-name 3FE53441AA
!
```

### Asociar el enlace PON al SFP

```text title="Comandos"
config
hardware component PON_1_GPON class transceiver-link-gpon
parent PONSFP_1
parent-rel-pos 1
```

#### Verificar el enlace PON

```text title="Salida de verificación"
OLT-LAB.LT1(config-component-PON_1_GPON)# show full-configuration
component PON_1_GPON
 class transceiver-link-gpon
 parent PONSFP_1
 parent-rel-pos 1
!
```

### Crear el channel group

```text title="Comandos"
config
interfaces interface LT1_PON1 type channel-group
enabled
channel-group polling-period 100
channel-group raman-mitigation raman-none
channel-group system-id 00000
```

#### Verificar el channel group

```text title="Salida de verificación"
OLT-LAB.LT1(config-interface-LT1_PON1)# show full-configuration
interface LT1_PON1
 type channel-group
 enabled true
 channel-group
  polling-period 100
  raman-mitigation raman-none
  system-id 00000
 !
!
```

### Crear el perfil de mapeo de colas

```text title="Comandos"
tm-profiles tc-id-2-queue-id-mapping-profile DEFAULT_TC_TO_8Queues
mapping-entry 0
local-queue-id 0
exit
mapping-entry 1
local-queue-id 1
exit
mapping-entry 2
local-queue-id 2
exit
mapping-entry 3
local-queue-id 3
exit
mapping-entry 4
local-queue-id 4
exit
mapping-entry 5
local-queue-id 5
exit
mapping-entry 6
local-queue-id 6
exit
mapping-entry 7
local-queue-id 7
```

### Crear la channel partition

```text title="Comandos"
config
interfaces interface LT1_PON1_CPART_GPON type channel-partition 
enabled true
channel-partition channel-group-ref LT1_PON1
channel-partition channel-partition-index 1
channel-partition downstream-fec true
channel-partition closest-onu-distance 0
channel-partition maximum-differential-xpon-distance 20
channel-partition authentication-method as-per-v-ani-expected
channel-partition multicast-aes-indicator false
channel-partition early-fetch-onu-loid-info false
```

#### Verificar la channel partition

```text title="Salida de verificación"
LT1-GPON(config-interface-LT1_PON1_CPART_GPON)# show full-configuration
interface LT1_PON1_CPART_GPON
 type channel-partition
 enabled true
 channel-partition
  channel-group-ref LT1_PON1
  channel-partition-index 1
  downstream-fec true
  closest-onu-distance 0
  maximum-differential-xpon-distance 20
  multicast-aes-indicator false
  early-fetch-onu-loid-info false
 !
!
```

### Crear el channel pair

```text title="Comandos"
interfaces interface LT1_PON1_CPAIR_GPON
type channel-pair
enabled true
channel-pair channel-group-ref LT1_PON1
channel-pair channel-partition-ref LT1_PON1_CPART_GPON
channel-pair channel-pair-type gpon
channel-pair gpon-pon-id-interval 10
multicast-cac max-group-number no-limit
multicast-cac max-multicast-rate-limit no-limit
multicast-cac multicast-rate-limit-exceed-action best-effort
```

#### Verificar el channel pair

```text title="Salida de verificación"
OLT-LAB.LT1(config-interface-LT1_PON1_CPAIR_GPON)# show full-configuration
interface LT1_PON1_CPAIR_GPON
 type channel-pair
 enabled true
 channel-pair
  channel-group-ref LT1_PON1
  channel-partition-ref LT1_PON1_CPART_GPON
  channel-pair-type gpon
  gpon-pon-id-interval 10
 !
 multicast-cac
  max-group-number no-limit
  max-multicast-rate-limit no-limit
  multicast-rate-limit-exceed-action best-effort
 !
!
```

### Crear la channel termination

```text title="Comandos"
config
interfaces interface CT_LT1_PON1_1_GPON
description LT1_PON1
type channel-termination
enabled true
port-layer-if PON_1_GPON
channel-termination channel-pair-ref LT1_PON1_CPAIR_GPON
channel-termination channel-termination-type gpon
channel-termination gpon-pon-id 00000000000000
channel-termination ber-calc-period 10
channel-termination location inside-olt
channel-termination laser-on-by-default true
```

```text title="Comandos"
OLT-LAB.LT1(config-interface-CT_LT1_PON1_1_GPON)# show full-configuration
interface CT_LT1_PON1_1_GPON
 description LT1_PON1
 type channel-termination
 enabled true
 port-layer-if PON_1_GPON
 channel-termination
  channel-pair-ref LT1_PON1_CPAIR_GPON
  channel-termination-type gpon
  gpon-pon-id 00000000000000
  ber-calc-period 10
  location inside-olt
  laser-on-by-default true
 !
!
```

### Consultar la LT en el IHUB

Ejecuta esta consulta en **IHUB**.

```text title="Comandos"
forward cli to ihub
configure global
```

La imagen crea `LT1` como una tarjeta **FGLT-D**. Esta es la configuración predeterminada de su puerto en el IHUB:

```text title="Configuración predeterminada"
[gl:configure port 1/8/1]
A:admin@iHUB-OLT-LAB# info flat
    port-id 1/8/1 { }
    admin-state { enable }
    description "10/20/40 Gig Ethernet LT" { }
    forwarding-scope { load-sharing }
    ethernet { }
    ethernet { autonegotiate true }
    ethernet { dot1q-etype 0x8100 }
    ethernet { mode access }
    ethernet { encap-type dot1q }
    ethernet { category residential }
    ethernet { remark false }
    ethernet { use-vlan-dot1q-etype false }
    ethernet { hold-time }
    ethernet { hold-time units seconds }
    ethernet { lldp }
    ethernet { lldp dest-mac nearest-bridge }
    ethernet { lldp dest-mac nearest-bridge notification false }
    ethernet { lldp dest-mac nearest-bridge port-id-subtype tx-local }
    ethernet { lldp dest-mac nearest-bridge receive false }
    ethernet { lldp dest-mac nearest-bridge transmit false }
    ethernet { lldp dest-mac nearest-bridge tx-tlvs }
    ethernet { lldp dest-mac nearest-bridge tx-tlvs port-desc false }
    ethernet { lldp dest-mac nearest-bridge tx-tlvs sys-name false }
    ethernet { lldp dest-mac nearest-bridge tx-tlvs sys-desc false }
    ethernet { lldp dest-mac nearest-bridge tx-tlvs sys-cap false }
    ethernet { lldp dest-mac nearest-bridge tx-mgmt-address system }
    ethernet { lldp dest-mac nearest-bridge tx-mgmt-address system admin-state disable }
    ethernet { lldp dest-mac nearest-bridge tx-mgmt-address system-ipv6 }
    ethernet { lldp dest-mac nearest-bridge tx-mgmt-address system-ipv6 admin-state disable }
    ethernet { lldp dest-mac nearest-bridge tx-mgmt-address node-ipv4 }
    ethernet { lldp dest-mac nearest-bridge tx-mgmt-address node-ipv4 admin-state disable }
    ethernet { lldp dest-mac nearest-bridge tx-mgmt-address node-ipv6 }
    ethernet { lldp dest-mac nearest-bridge tx-mgmt-address node-ipv6 admin-state disable }
    ethernet { lldp dest-mac nearest-non-tpmr }
    ethernet { lldp dest-mac nearest-non-tpmr notification false }
    ethernet { lldp dest-mac nearest-non-tpmr port-id-subtype tx-local }
    ethernet { lldp dest-mac nearest-non-tpmr receive false }
    ethernet { lldp dest-mac nearest-non-tpmr transmit false }
    ethernet { lldp dest-mac nearest-non-tpmr tx-tlvs }
    ethernet { lldp dest-mac nearest-non-tpmr tx-tlvs port-desc false }
    ethernet { lldp dest-mac nearest-non-tpmr tx-tlvs sys-name false }
    ethernet { lldp dest-mac nearest-non-tpmr tx-tlvs sys-desc false }
    ethernet { lldp dest-mac nearest-non-tpmr tx-tlvs sys-cap false }
    ethernet { lldp dest-mac nearest-non-tpmr tx-mgmt-address system }
    ethernet { lldp dest-mac nearest-non-tpmr tx-mgmt-address system admin-state disable }
    ethernet { lldp dest-mac nearest-non-tpmr tx-mgmt-address system-ipv6 }
    ethernet { lldp dest-mac nearest-non-tpmr tx-mgmt-address system-ipv6 admin-state disable }
    ethernet { lldp dest-mac nearest-non-tpmr tx-mgmt-address node-ipv4 }
    ethernet { lldp dest-mac nearest-non-tpmr tx-mgmt-address node-ipv4 admin-state disable }
    ethernet { lldp dest-mac nearest-non-tpmr tx-mgmt-address node-ipv6 }
    ethernet { lldp dest-mac nearest-non-tpmr tx-mgmt-address node-ipv6 admin-state disable }
    ethernet { lldp dest-mac nearest-customer }
    ethernet { lldp dest-mac nearest-customer notification false }
    ethernet { lldp dest-mac nearest-customer port-id-subtype tx-local }
    ethernet { lldp dest-mac nearest-customer receive false }
    ethernet { lldp dest-mac nearest-customer transmit false }
    ethernet { lldp dest-mac nearest-customer tx-tlvs }
    ethernet { lldp dest-mac nearest-customer tx-tlvs port-desc false }
    ethernet { lldp dest-mac nearest-customer tx-tlvs sys-name false }
    ethernet { lldp dest-mac nearest-customer tx-tlvs sys-desc false }
    ethernet { lldp dest-mac nearest-customer tx-tlvs sys-cap false }
    ethernet { lldp dest-mac nearest-customer tx-mgmt-address system }
    ethernet { lldp dest-mac nearest-customer tx-mgmt-address system admin-state disable }
    ethernet { lldp dest-mac nearest-customer tx-mgmt-address system-ipv6 }
    ethernet { lldp dest-mac nearest-customer tx-mgmt-address system-ipv6 admin-state disable }
    ethernet { lldp dest-mac nearest-customer tx-mgmt-address node-ipv4 }
    ethernet { lldp dest-mac nearest-customer tx-mgmt-address node-ipv4 admin-state disable }
    ethernet { lldp dest-mac nearest-customer tx-mgmt-address node-ipv6 }
    ethernet { lldp dest-mac nearest-customer tx-mgmt-address node-ipv6 admin-state disable }
```

## Crear la plantilla de ONU

Ejecuta esta tarea en el contexto de la **LT**. La plantilla define los clasificadores, las políticas QoS, el T-CONT, el GEM port y las interfaces base de una ONU Nokia genérica.

```text title="Comandos"
config
onus onu GENERIC-NOKIA usage node-template-usage
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit_marking_untag_write_pbit0 filter-operation match-all-filter
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit_marking_untag_write_pbit0 match-criteria untagged
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit_marking_untag_write_pbit0 classifier-action-entry-cfg pbit-marking pbit-marking-cfg pbit-marking-list 0 pbit-value 0
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit_marking_copy_pbit0 filter-operation match-all-filter
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit_marking_copy_pbit0 match-criteria tag 0 in-pbit-list 0
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit_marking_copy_pbit0 match-criteria dscp-range any
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit_marking_copy_pbit0 classifier-action-entry-cfg pbit-marking pbit-marking-cfg pbit-marking-list 0 pbit-value 0
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit_marking_copy_pbit1 filter-operation match-all-filter
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit_marking_copy_pbit1 match-criteria tag 0 in-pbit-list 1
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit_marking_copy_pbit1 match-criteria dscp-range any
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit_marking_copy_pbit1 classifier-action-entry-cfg pbit-marking pbit-marking-cfg pbit-marking-list 0 pbit-value 1
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit_marking_copy_pbit2 filter-operation match-all-filter
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit_marking_copy_pbit2 match-criteria tag 0 in-pbit-list 2
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit_marking_copy_pbit2 match-criteria dscp-range any
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit_marking_copy_pbit2 classifier-action-entry-cfg pbit-marking pbit-marking-cfg pbit-marking-list 0 pbit-value 2
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit_marking_copy_pbit3 filter-operation match-all-filter
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit_marking_copy_pbit3 match-criteria tag 0 in-pbit-list 3
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit_marking_copy_pbit3 match-criteria dscp-range any
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit_marking_copy_pbit3 classifier-action-entry-cfg pbit-marking pbit-marking-cfg pbit-marking-list 0 pbit-value 3
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit_marking_copy_pbit4 filter-operation match-all-filter
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit_marking_copy_pbit4 match-criteria tag 0 in-pbit-list 4
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit_marking_copy_pbit4 match-criteria dscp-range any
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit_marking_copy_pbit4 classifier-action-entry-cfg pbit-marking pbit-marking-cfg pbit-marking-list 0 pbit-value 4
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit_marking_copy_pbit5 filter-operation match-all-filter
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit_marking_copy_pbit5 match-criteria tag 0 in-pbit-list 5
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit_marking_copy_pbit5 match-criteria dscp-range any
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit_marking_copy_pbit5 classifier-action-entry-cfg pbit-marking pbit-marking-cfg pbit-marking-list 0 pbit-value 5
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit_marking_copy_pbit6 filter-operation match-all-filter
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit_marking_copy_pbit6 match-criteria tag 0 in-pbit-list 6
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit_marking_copy_pbit6 match-criteria dscp-range any
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit_marking_copy_pbit6 classifier-action-entry-cfg pbit-marking pbit-marking-cfg pbit-marking-list 0 pbit-value 6
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit_marking_copy_pbit7 filter-operation match-all-filter
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit_marking_copy_pbit7 match-criteria tag 0 in-pbit-list 7
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit_marking_copy_pbit7 match-criteria dscp-range any
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit_marking_copy_pbit7 classifier-action-entry-cfg pbit-marking pbit-marking-cfg pbit-marking-list 0 pbit-value 7
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit2tc_pbit0_to_tc0 filter-operation match-all-filter
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit2tc_pbit0_to_tc0 match-criteria pbit-marking-list 0 pbit-value 0
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit2tc_pbit0_to_tc0 classifier-action-entry-cfg scheduling-traffic-class scheduling-traffic-class 0
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit2tc_pbit1_to_tc0 filter-operation match-all-filter
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit2tc_pbit1_to_tc0 match-criteria pbit-marking-list 0 pbit-value 1
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit2tc_pbit1_to_tc0 classifier-action-entry-cfg scheduling-traffic-class scheduling-traffic-class 0
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit2tc_pbit2_to_tc0 filter-operation match-all-filter
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit2tc_pbit2_to_tc0 match-criteria pbit-marking-list 0 pbit-value 2
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit2tc_pbit2_to_tc0 classifier-action-entry-cfg scheduling-traffic-class scheduling-traffic-class 0
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit2tc_pbit3_to_tc0 filter-operation match-all-filter
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit2tc_pbit3_to_tc0 match-criteria pbit-marking-list 0 pbit-value 3
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit2tc_pbit3_to_tc0 classifier-action-entry-cfg scheduling-traffic-class scheduling-traffic-class 0
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit2tc_pbit4_to_tc0 filter-operation match-all-filter
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit2tc_pbit4_to_tc0 match-criteria pbit-marking-list 0 pbit-value 4
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit2tc_pbit4_to_tc0 classifier-action-entry-cfg scheduling-traffic-class scheduling-traffic-class 0
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit2tc_pbit5_to_tc0 filter-operation match-all-filter
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit2tc_pbit5_to_tc0 match-criteria pbit-marking-list 0 pbit-value 5
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit2tc_pbit5_to_tc0 classifier-action-entry-cfg scheduling-traffic-class scheduling-traffic-class 0
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit2tc_pbit6_to_tc0 filter-operation match-all-filter
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit2tc_pbit6_to_tc0 match-criteria pbit-marking-list 0 pbit-value 6
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit2tc_pbit6_to_tc0 classifier-action-entry-cfg scheduling-traffic-class scheduling-traffic-class 0
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit2tc_pbit7_to_tc0 filter-operation match-all-filter
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit2tc_pbit7_to_tc0 match-criteria pbit-marking-list 0 pbit-value 7
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit2tc_pbit7_to_tc0 classifier-action-entry-cfg scheduling-traffic-class scheduling-traffic-class 0
onus onu GENERIC-NOKIA root policies policy HSI_TC0 classifiers pbit_marking_untag_write_pbit0
onus onu GENERIC-NOKIA root policies policy HSI_TC0 classifiers pbit_marking_copy_pbit0
onus onu GENERIC-NOKIA root policies policy HSI_TC0 classifiers pbit_marking_copy_pbit1
onus onu GENERIC-NOKIA root policies policy HSI_TC0 classifiers pbit_marking_copy_pbit2
onus onu GENERIC-NOKIA root policies policy HSI_TC0 classifiers pbit_marking_copy_pbit3
onus onu GENERIC-NOKIA root policies policy HSI_TC0 classifiers pbit_marking_copy_pbit4
onus onu GENERIC-NOKIA root policies policy HSI_TC0 classifiers pbit_marking_copy_pbit5
onus onu GENERIC-NOKIA root policies policy HSI_TC0 classifiers pbit_marking_copy_pbit6
onus onu GENERIC-NOKIA root policies policy HSI_TC0 classifiers pbit_marking_copy_pbit7
onus onu GENERIC-NOKIA root policies policy HSI_TC0_tc classifiers pbit2tc_pbit0_to_tc0
onus onu GENERIC-NOKIA root policies policy HSI_TC0_tc classifiers pbit2tc_pbit1_to_tc0
onus onu GENERIC-NOKIA root policies policy HSI_TC0_tc classifiers pbit2tc_pbit2_to_tc0
onus onu GENERIC-NOKIA root policies policy HSI_TC0_tc classifiers pbit2tc_pbit3_to_tc0
onus onu GENERIC-NOKIA root policies policy HSI_TC0_tc classifiers pbit2tc_pbit4_to_tc0
onus onu GENERIC-NOKIA root policies policy HSI_TC0_tc classifiers pbit2tc_pbit5_to_tc0
onus onu GENERIC-NOKIA root policies policy HSI_TC0_tc classifiers pbit2tc_pbit6_to_tc0
onus onu GENERIC-NOKIA root policies policy HSI_TC0_tc classifiers pbit2tc_pbit7_to_tc0
onus onu GENERIC-NOKIA root qos-policy-profiles policy-profile Q_HSI_TC0 policy-list HSI_TC0
onus onu GENERIC-NOKIA root qos-policy-profiles policy-profile Q_HSI_TC0 policy-list HSI_TC0_tc
onus onu GENERIC-NOKIA root tm-profiles tc-id-2-queue-id-mapping-profile TC2Q_Profile_Single-TC mapping-entry 0 local-queue-id 0
onus onu GENERIC-NOKIA root tm-profiles tc-id-2-queue-id-mapping-profile TC2Q_Profile_8-TC mapping-entry 0 local-queue-id 0
onus onu GENERIC-NOKIA root tm-profiles tc-id-2-queue-id-mapping-profile TC2Q_Profile_8-TC mapping-entry 1 local-queue-id 1
onus onu GENERIC-NOKIA root tm-profiles tc-id-2-queue-id-mapping-profile TC2Q_Profile_8-TC mapping-entry 2 local-queue-id 2
onus onu GENERIC-NOKIA root tm-profiles tc-id-2-queue-id-mapping-profile TC2Q_Profile_8-TC mapping-entry 3 local-queue-id 3
onus onu GENERIC-NOKIA root tm-profiles tc-id-2-queue-id-mapping-profile TC2Q_Profile_8-TC mapping-entry 4 local-queue-id 4
onus onu GENERIC-NOKIA root tm-profiles tc-id-2-queue-id-mapping-profile TC2Q_Profile_8-TC mapping-entry 5 local-queue-id 5
onus onu GENERIC-NOKIA root tm-profiles tc-id-2-queue-id-mapping-profile TC2Q_Profile_8-TC mapping-entry 6 local-queue-id 6
onus onu GENERIC-NOKIA root tm-profiles tc-id-2-queue-id-mapping-profile TC2Q_Profile_8-TC mapping-entry 7 local-queue-id 7
onus onu GENERIC-NOKIA root voip-configuration-characteristics configuration-method omci
onus onu GENERIC-NOKIA root xpongemtcont tconts tcont TCONT_VEIP_HSI interface-reference ANI
onus onu GENERIC-NOKIA root xpongemtcont tconts tcont TCONT_VEIP_HSI tm-root queue 0 priority 1
onus onu GENERIC-NOKIA root xpongemtcont tconts tcont TCONT_VEIP_HSI tm-root queue 0 weight 1
onus onu GENERIC-NOKIA root xpongemtcont tconts tcont TCONT_VEIP_HSI tm-root tc-id-2-queue-id-mapping-profile-name TC2Q_Profile_Single-TC
onus onu GENERIC-NOKIA root xpongemtcont gemports gemport GEM0_VEIP_HSI interface VSI_VEIP_HSI
onus onu GENERIC-NOKIA root xpongemtcont gemports gemport GEM0_VEIP_HSI traffic-class 0
onus onu GENERIC-NOKIA root xpongemtcont gemports gemport GEM0_VEIP_HSI tcont-ref TCONT_VEIP_HSI
onus onu GENERIC-NOKIA root hardware component CHASSIS class chassis
onus onu GENERIC-NOKIA root hardware component CHASSIS admin-state unlocked
onus onu GENERIC-NOKIA root hardware component CAGE class cage
onus onu GENERIC-NOKIA root hardware component CAGE parent CHASSIS
onus onu GENERIC-NOKIA root hardware component CAGE parent-rel-pos 0
onus onu GENERIC-NOKIA root hardware component SFP class transceiver
onus onu GENERIC-NOKIA root hardware component SFP parent CAGE
onus onu GENERIC-NOKIA root hardware component SFP parent-rel-pos 0
onus onu GENERIC-NOKIA root hardware component ANIPORT class transceiver-link
onus onu GENERIC-NOKIA root hardware component ANIPORT parent SFP
onus onu GENERIC-NOKIA root hardware component ANIPORT parent-rel-pos 1
onus onu GENERIC-NOKIA root hardware component UNI_LAN1 class rj45
onus onu GENERIC-NOKIA root hardware component UNI_LAN1 parent CHASSIS
onus onu GENERIC-NOKIA root hardware component UNI_LAN1 parent-rel-pos 1
onus onu GENERIC-NOKIA root hardware component UNI_LAN1 omci-identifier-helper virtual-board-number 1
onus onu GENERIC-NOKIA root hardware component UNI_LAN2 class rj45
onus onu GENERIC-NOKIA root hardware component UNI_LAN2 parent CHASSIS
onus onu GENERIC-NOKIA root hardware component UNI_LAN2 parent-rel-pos 2
onus onu GENERIC-NOKIA root hardware component UNI_LAN2 omci-identifier-helper virtual-board-number 1
onus onu GENERIC-NOKIA root hardware component UNI_LAN3 class rj45
onus onu GENERIC-NOKIA root hardware component UNI_LAN3 parent CHASSIS
onus onu GENERIC-NOKIA root hardware component UNI_LAN3 parent-rel-pos 3
onus onu GENERIC-NOKIA root hardware component UNI_LAN3 omci-identifier-helper virtual-board-number 1
onus onu GENERIC-NOKIA root hardware component UNI_LAN4 class rj45
onus onu GENERIC-NOKIA root hardware component UNI_LAN4 parent CHASSIS
onus onu GENERIC-NOKIA root hardware component UNI_LAN4 parent-rel-pos 4
onus onu GENERIC-NOKIA root hardware component UNI_LAN4 omci-identifier-helper virtual-board-number 1
onus onu GENERIC-NOKIA root hardware component UNI_VEIP class virtual-port
onus onu GENERIC-NOKIA root hardware component UNI_VEIP parent CHASSIS
onus onu GENERIC-NOKIA root hardware component UNI_VEIP parent-rel-pos 1
onus onu GENERIC-NOKIA root hardware component UNI_TEL1 class rj11
onus onu GENERIC-NOKIA root hardware component UNI_TEL1 parent CHASSIS
onus onu GENERIC-NOKIA root hardware component UNI_TEL1 parent-rel-pos 1
onus onu GENERIC-NOKIA root interfaces interface ENET_LAN1 type ethernetCsmacd
onus onu GENERIC-NOKIA root interfaces interface ENET_LAN1 enabled false
onus onu GENERIC-NOKIA root interfaces interface ENET_LAN1 port-layer-if UNI_LAN1
onus onu GENERIC-NOKIA root interfaces interface ENET_LAN1 ethernet auto-negotiation status enabled
onus onu GENERIC-NOKIA root interfaces interface ENET_LAN1 ethernet auto-negotiation duplex full
onus onu GENERIC-NOKIA root interfaces interface ENET_LAN1 ethernet auto-negotiation speed eth-if-speed-1gb
onus onu GENERIC-NOKIA root interfaces interface ENET_LAN2 type ethernetCsmacd
onus onu GENERIC-NOKIA root interfaces interface ENET_LAN2 enabled false
onus onu GENERIC-NOKIA root interfaces interface ENET_LAN2 port-layer-if UNI_LAN2
onus onu GENERIC-NOKIA root interfaces interface ENET_LAN2 ethernet auto-negotiation status enabled
onus onu GENERIC-NOKIA root interfaces interface ENET_LAN2 ethernet auto-negotiation duplex full
onus onu GENERIC-NOKIA root interfaces interface ENET_LAN2 ethernet auto-negotiation speed eth-if-speed-1gb
onus onu GENERIC-NOKIA root interfaces interface ENET_LAN3 type ethernetCsmacd
onus onu GENERIC-NOKIA root interfaces interface ENET_LAN3 enabled false
onus onu GENERIC-NOKIA root interfaces interface ENET_LAN3 port-layer-if UNI_LAN3
onus onu GENERIC-NOKIA root interfaces interface ENET_LAN3 ethernet auto-negotiation status enabled
onus onu GENERIC-NOKIA root interfaces interface ENET_LAN3 ethernet auto-negotiation duplex full
onus onu GENERIC-NOKIA root interfaces interface ENET_LAN3 ethernet auto-negotiation speed eth-if-speed-1gb
onus onu GENERIC-NOKIA root interfaces interface ENET_LAN4 type ethernetCsmacd
onus onu GENERIC-NOKIA root interfaces interface ENET_LAN4 enabled false
onus onu GENERIC-NOKIA root interfaces interface ENET_LAN4 port-layer-if UNI_LAN4
onus onu GENERIC-NOKIA root interfaces interface ENET_LAN4 ethernet auto-negotiation status enabled
onus onu GENERIC-NOKIA root interfaces interface ENET_LAN4 ethernet auto-negotiation duplex full
onus onu GENERIC-NOKIA root interfaces interface ENET_LAN4 ethernet auto-negotiation speed eth-if-speed-1gb
onus onu GENERIC-NOKIA root interfaces interface ENET_VEIP type onu-v-vrefpoint
onus onu GENERIC-NOKIA root interfaces interface ENET_VEIP enabled false
onus onu GENERIC-NOKIA root interfaces interface ENET_VEIP port-layer-if UNI_VEIP
onus onu GENERIC-NOKIA root interfaces interface ENET_VEIP onu-v-vrefpoint related-onu ANI
onus onu GENERIC-NOKIA root interfaces interface POTS_TEL1 type voiceFXS
onus onu GENERIC-NOKIA root interfaces interface POTS_TEL1 enabled false
onus onu GENERIC-NOKIA root interfaces interface POTS_TEL1 port-layer-if UNI_TEL1
onus onu GENERIC-NOKIA root interfaces interface ANI type ani
onus onu GENERIC-NOKIA root interfaces interface ANI port-layer-if ANIPORT
onus onu GENERIC-NOKIA root interfaces interface ANI performance pm-counter-size 32bit-performance-monitoring
onus onu GENERIC-NOKIA root interfaces interface ANI ani multicast-gemport ANI_2046 mc-gemport-id 2046
onus onu GENERIC-NOKIA root interfaces interface ANI ani multicast-gemport ANI_2046 is-broadcast true
onus onu GENERIC-NOKIA root interfaces interface VSI_VEIP_HSI type vlan-sub-interface
onus onu GENERIC-NOKIA root interfaces interface VSI_VEIP_HSI ingress-qos-policy-profile Q_HSI_TC0
onus onu GENERIC-NOKIA root interfaces interface VSI_VEIP_HSI subif-lower-layer interface ENET_VEIP
onus onu GENERIC-NOKIA root interfaces interface VSI_VEIP_HSI inline-frame-processing ingress-rule rule single-tagged priority 100
onus onu GENERIC-NOKIA root interfaces interface VSI_VEIP_HSI inline-frame-processing ingress-rule rule single-tagged flexible-match match-criteria tag 0 dot1q-tag tag-type c-vlan
onus onu GENERIC-NOKIA root interfaces interface VSI_VEIP_HSI inline-frame-processing ingress-rule rule single-tagged flexible-match match-criteria tag 0 dot1q-tag vlan-id 10
onus onu GENERIC-NOKIA root interfaces interface VSI_VEIP_HSI inline-frame-processing ingress-rule rule single-tagged flexible-match match-criteria tag 0 dot1q-tag pbit any
onus onu GENERIC-NOKIA root interfaces interface VSI_VEIP_HSI inline-frame-processing ingress-rule rule single-tagged flexible-match match-criteria tag 0 dot1q-tag dei any
onus onu GENERIC-NOKIA root interfaces interface VSI_VEIP_HSI inline-frame-processing ingress-rule rule single-tagged ingress-rewrite pop-tags 1
onus onu GENERIC-NOKIA root interfaces interface VSI_VEIP_HSI inline-frame-processing ingress-rule rule single-tagged ingress-rewrite push-tag 0 dot1q-tag tag-type c-vlan
onus onu GENERIC-NOKIA root interfaces interface VSI_VEIP_HSI inline-frame-processing ingress-rule rule single-tagged ingress-rewrite push-tag 0 dot1q-tag vlan-id 10
onus onu GENERIC-NOKIA root interfaces interface VSI_VEIP_HSI inline-frame-processing ingress-rule rule single-tagged ingress-rewrite push-tag 0 dot1q-tag pbit-marking-index 0
onus onu GENERIC-NOKIA root interfaces interface VSI_VEIP_HSI inline-frame-processing ingress-rule rule single-tagged ingress-rewrite push-tag 0 dot1q-tag dei-from-tag-index 0
onus onu GENERIC-NOKIA root interfaces interface VSI_VEIP_HSI inline-frame-processing ingress-rule rule single-tagged auto-instantiate false
onus onu GENERIC-NOKIA root interfaces interface VSI_VEIP_HSI auto-instantiate false
onus onu GENERIC-NOKIA root routing control-plane-protocols control-plane-protocol static default-route static-routes ipv4 route 0.0.0.0/0 next-hop next-hop-address 0.0.0.1
onus onu GENERIC-NOKIA root system dns-resolver server pridns udp-and-tcp address 0.0.0.0
onus onu GENERIC-NOKIA root system dns-resolver server backupdns udp-and-tcp address 0.0.0.0
onus onu GENERIC-NOKIA root ptp-ccsa-profiles ptp-ccsa-port-profile default domain 0
onus onu GENERIC-NOKIA root ptp-ccsa-profiles ptp-ccsa-port-profile default master-only true
onus onu GENERIC-NOKIA root ptp-ccsa-profiles ptp-ccsa-port-profile default dest-mac-addr-forwardable forwardable
onus onu GENERIC-NOKIA root ptp-ccsa-profiles ptp-ccsa-port-profile default log-anno-interval -3
onus onu GENERIC-NOKIA root ptp-ccsa-profiles ptp-ccsa-port-profile default log-sync-interval -4
onus onu GENERIC-NOKIA root ptp-ccsa-profiles ptp-ccsa-port-profile default log-delay-interval 0
onus onu GENERIC-NOKIA root ptp-ccsa-profiles ptp-ccsa-port-profile default step-mode one-step
onus onu GENERIC-NOKIA root ptp-g8275dot1-profiles ptp-g8275dot1-port-profile default domain 24
onus onu GENERIC-NOKIA root ptp-g8275dot1-profiles ptp-g8275dot1-port-profile default master-only true
onus onu GENERIC-NOKIA root ptp-g8275dot1-profiles ptp-g8275dot1-port-profile default dest-mac-addr-forwardable forwardable
onus onu GENERIC-NOKIA root ptp-g8275dot1-profiles ptp-g8275dot1-port-profile default log-anno-interval -3
onus onu GENERIC-NOKIA root ptp-g8275dot1-profiles ptp-g8275dot1-port-profile default log-sync-interval -4
onus onu GENERIC-NOKIA root ptp-g8275dot1-profiles ptp-g8275dot1-port-profile default log-delay-interval -4
onus onu GENERIC-NOKIA root ptp-g8275dot1-profiles ptp-g8275dot1-port-profile default step-mode one-step
```

### Verificar la plantilla de ONU

```text title="Comandos"
OLT-02.LT1(config-onu-GENERIC-NOKIA)# show full-configuration
onu GENERIC-NOKIA
 usage node-template-usage
 root
  classifiers
   classifier-entry pbit_marking_untag_write_pbit0
    filter-operation match-all-filter
    match-criteria untagged
    classifier-action-entry-cfg
     action-type pbit-marking
     pbit-marking-cfg pbit-marking-list 0
      pbit-value 0
     !
    !
   !
   classifier-entry pbit_marking_copy_pbit0
    filter-operation match-all-filter
    match-criteria
     tag 0
      in-pbit-list 0
     !
     dscp-range any
    !
    classifier-action-entry-cfg
     action-type pbit-marking
     pbit-marking-cfg pbit-marking-list 0
      pbit-value 0
     !
    !
   !
   classifier-entry pbit_marking_copy_pbit1
    filter-operation match-all-filter
    match-criteria
     tag 0
      in-pbit-list 1
     !
     dscp-range any
    !
    classifier-action-entry-cfg
     action-type pbit-marking
     pbit-marking-cfg pbit-marking-list 0
      pbit-value 1
     !
    !
   !
   classifier-entry pbit_marking_copy_pbit2
    filter-operation match-all-filter
    match-criteria
     tag 0
      in-pbit-list 2
     !
     dscp-range any
    !
    classifier-action-entry-cfg
     action-type pbit-marking
     pbit-marking-cfg pbit-marking-list 0
      pbit-value 2
     !
    !
   !
   classifier-entry pbit_marking_copy_pbit3
    filter-operation match-all-filter
    match-criteria
     tag 0
      in-pbit-list 3
     !
     dscp-range any
    !
    classifier-action-entry-cfg
     action-type pbit-marking
     pbit-marking-cfg pbit-marking-list 0
      pbit-value 3
     !
    !
   !
   classifier-entry pbit_marking_copy_pbit4
    filter-operation match-all-filter
    match-criteria
     tag 0
      in-pbit-list 4
     !
     dscp-range any
    !
    classifier-action-entry-cfg
     action-type pbit-marking
     pbit-marking-cfg pbit-marking-list 0
      pbit-value 4
     !
    !
   !
   classifier-entry pbit_marking_copy_pbit5
    filter-operation match-all-filter
    match-criteria
     tag 0
      in-pbit-list 5
     !
     dscp-range any
    !
    classifier-action-entry-cfg
     action-type pbit-marking
     pbit-marking-cfg pbit-marking-list 0
      pbit-value 5
     !
    !
   !
   classifier-entry pbit_marking_copy_pbit6
    filter-operation match-all-filter
    match-criteria
     tag 0
      in-pbit-list 6
     !
     dscp-range any
    !
    classifier-action-entry-cfg
     action-type pbit-marking
     pbit-marking-cfg pbit-marking-list 0
      pbit-value 6
     !
    !
   !
   classifier-entry pbit_marking_copy_pbit7
    filter-operation match-all-filter
    match-criteria
     tag 0
      in-pbit-list 7
     !
     dscp-range any
    !
    classifier-action-entry-cfg
     action-type pbit-marking
     pbit-marking-cfg pbit-marking-list 0
      pbit-value 7
     !
    !
   !
   classifier-entry pbit2tc_pbit0_to_tc0
    filter-operation match-all-filter
    match-criteria pbit-marking-list 0
     pbit-value 0
    !
    classifier-action-entry-cfg
     action-type scheduling-traffic-class
     scheduling-traffic-class 0
    !
   !
   classifier-entry pbit2tc_pbit1_to_tc0
    filter-operation match-all-filter
    match-criteria pbit-marking-list 0
     pbit-value 1
    !
    classifier-action-entry-cfg
     action-type scheduling-traffic-class
     scheduling-traffic-class 0
    !
   !
   classifier-entry pbit2tc_pbit2_to_tc0
    filter-operation match-all-filter
    match-criteria pbit-marking-list 0
     pbit-value 2
    !
    classifier-action-entry-cfg
     action-type scheduling-traffic-class
     scheduling-traffic-class 0
    !
   !
   classifier-entry pbit2tc_pbit3_to_tc0
    filter-operation match-all-filter
    match-criteria pbit-marking-list 0
     pbit-value 3
    !
    classifier-action-entry-cfg
     action-type scheduling-traffic-class
     scheduling-traffic-class 0
    !
   !
   classifier-entry pbit2tc_pbit4_to_tc0
    filter-operation match-all-filter
    match-criteria pbit-marking-list 0
     pbit-value 4
    !
    classifier-action-entry-cfg
     action-type scheduling-traffic-class
     scheduling-traffic-class 0
    !
   !
   classifier-entry pbit2tc_pbit5_to_tc0
    filter-operation match-all-filter
    match-criteria pbit-marking-list 0
     pbit-value 5
    !
    classifier-action-entry-cfg
     action-type scheduling-traffic-class
     scheduling-traffic-class 0
    !
   !
   classifier-entry pbit2tc_pbit6_to_tc0
    filter-operation match-all-filter
    match-criteria pbit-marking-list 0
     pbit-value 6
    !
    classifier-action-entry-cfg
     action-type scheduling-traffic-class
     scheduling-traffic-class 0
    !
   !
   classifier-entry pbit2tc_pbit7_to_tc0
    filter-operation match-all-filter
    match-criteria pbit-marking-list 0
     pbit-value 7
    !
    classifier-action-entry-cfg
     action-type scheduling-traffic-class
     scheduling-traffic-class 0
    !
   !
  !
  policies
   policy HSI_TC0
    classifiers name pbit_marking_untag_write_pbit0
    classifiers name pbit_marking_copy_pbit0
    classifiers name pbit_marking_copy_pbit1
    classifiers name pbit_marking_copy_pbit2
    classifiers name pbit_marking_copy_pbit3
    classifiers name pbit_marking_copy_pbit4
    classifiers name pbit_marking_copy_pbit5
    classifiers name pbit_marking_copy_pbit6
    classifiers name pbit_marking_copy_pbit7
   !
   policy HSI_TC0_tc
    classifiers name pbit2tc_pbit0_to_tc0
    classifiers name pbit2tc_pbit1_to_tc0
    classifiers name pbit2tc_pbit2_to_tc0
    classifiers name pbit2tc_pbit3_to_tc0
    classifiers name pbit2tc_pbit4_to_tc0
    classifiers name pbit2tc_pbit5_to_tc0
    classifiers name pbit2tc_pbit6_to_tc0
    classifiers name pbit2tc_pbit7_to_tc0
   !
  !
  qos-policy-profiles policy-profile Q_HSI_TC0
   policy-list name HSI_TC0
   policy-list name HSI_TC0_tc
  !
  tm-profiles
   tc-id-2-queue-id-mapping-profile TC2Q_Profile_Single-TC
    mapping-entry
     traffic-class-id 0
     local-queue-id 0
    !
   !
   tc-id-2-queue-id-mapping-profile TC2Q_Profile_8-TC
    mapping-entry
     traffic-class-id 0
     local-queue-id 0
    !
    mapping-entry
     traffic-class-id 1
     local-queue-id 1
    !
    mapping-entry
     traffic-class-id 2
     local-queue-id 2
    !
    mapping-entry
     traffic-class-id 3
     local-queue-id 3
    !
    mapping-entry
     traffic-class-id 4
     local-queue-id 4
    !
    mapping-entry
     traffic-class-id 5
     local-queue-id 5
    !
    mapping-entry
     traffic-class-id 6
     local-queue-id 6
    !
    mapping-entry
     traffic-class-id 7
     local-queue-id 7
    !
   !
  !
  voip-configuration-characteristics configuration-method omci
  xpongemtcont
   tconts tcont TCONT_VEIP_HSI
    interface-reference ANI
    tm-root
     queue
      local-queue-id 0
      priority 1
      weight 1
     !
     tc-id-2-queue-id-mapping-profile-name TC2Q_Profile_Single-TC
    !
   !
   gemports gemport GEM0_VEIP_HSI
    interface VSI_VEIP_HSI
    traffic-class 0
    tcont-ref TCONT_VEIP_HSI
   !
  !
  hardware
   component UNI_LAN1
    class rj45
    parent CHASSIS
    parent-rel-pos 1
    omci-identifier-helper virtual-board-number 1
   !
   component UNI_LAN2
    class rj45
    parent CHASSIS
    parent-rel-pos 2
    omci-identifier-helper virtual-board-number 1
   !
   component UNI_LAN3
    class rj45
    parent CHASSIS
    parent-rel-pos 3
    omci-identifier-helper virtual-board-number 1
   !
   component UNI_LAN4
    class rj45
    parent CHASSIS
    parent-rel-pos 4
    omci-identifier-helper virtual-board-number 1
   !
   component UNI_VEIP
    class virtual-port
    parent CHASSIS
    parent-rel-pos 1
   !
   component UNI_TEL1
    class rj11
    parent CHASSIS
    parent-rel-pos 1
   !
   component SFP
    class transceiver
    parent CAGE
    parent-rel-pos 0
   !
   component ANIPORT
    class transceiver-link
    parent SFP
    parent-rel-pos 1
   !
   component CHASSIS
    class chassis
    admin-state unlocked
   !
   component CAGE
    class cage
    parent CHASSIS
    parent-rel-pos 0
   !
  !
  interfaces
   interface ENET_LAN1
    type ethernetCsmacd
    enabled false
    port-layer-if UNI_LAN1
    ethernet auto-negotiation
     status enabled
     duplex full
     speed eth-if-speed-1gb
    !
   !
   interface ENET_LAN2
    type ethernetCsmacd
    enabled false
    port-layer-if UNI_LAN2
    ethernet auto-negotiation
     status enabled
     duplex full
     speed eth-if-speed-1gb
    !
   !
   interface ENET_LAN3
    type ethernetCsmacd
    enabled false
    port-layer-if UNI_LAN3
    ethernet auto-negotiation
     status enabled
     duplex full
     speed eth-if-speed-1gb
    !
   !
   interface ENET_LAN4
    type ethernetCsmacd
    enabled false
    port-layer-if UNI_LAN4
    ethernet auto-negotiation
     status enabled
     duplex full
     speed eth-if-speed-1gb
    !
   !
   interface ENET_VEIP
    type onu-v-vrefpoint
    enabled false
    port-layer-if UNI_VEIP
    onu-v-vrefpoint related-onu ANI
   !
   interface POTS_TEL1
    type voiceFXS
    enabled false
    port-layer-if UNI_TEL1
   !
   interface ANI
    type ani
    port-layer-if ANIPORT
    performance pm-counter-size 32bit-performance-monitoring
    ani multicast-gemport ANI_2046
     mc-gemport-id 2046
     is-broadcast true
    !
   !
   interface VSI_VEIP_HSI
    type vlan-sub-interface
    ingress-qos-policy-profile Q_HSI_TC0
    subif-lower-layer interface ENET_VEIP
    inline-frame-processing ingress-rule rule single-tagged
     priority 100
     flexible-match match-criteria tag 0
      dot1q-tag
       tag-type c-vlan
       vlan-id 10
       pbit any
       dei any
      !
     !
     ingress-rewrite
      pop-tags 1
      push-tag 0
       dot1q-tag
        tag-type c-vlan
        vlan-id 10
        pbit-marking-index 0
        dei-from-tag-index 0
       !
      !
     !
     auto-instantiate false
    !
    auto-instantiate false
   !
  !
  routing control-plane-protocols control-plane-protocol
   type static
   name default-route
   static-routes ipv4 route
    destination-prefix 0.0.0.0/0
    next-hop next-hop-address 0.0.0.1
   !
  !
  system dns-resolver
   server pridns
    udp-and-tcp address 0.0.0.0
   !
   server backupdns
    udp-and-tcp address 0.0.0.0
   !
  !
  ptp-ccsa-profiles ptp-ccsa-port-profile default
   domain 0
   master-only true
   dest-mac-addr-forwardable forwardable
   log-anno-interval -3
   log-sync-interval -4
   log-delay-interval 0
   step-mode one-step
  !
  ptp-g8275dot1-profiles ptp-g8275dot1-port-profile default
   domain 24
   master-only true
   dest-mac-addr-forwardable forwardable
   log-anno-interval -3
   log-sync-interval -4
   log-delay-interval -4
   step-mode one-step
  !
 !
!
```

## Aprovisionar una ONT

Ejecuta estas tareas en el contexto de la **LT** correspondiente. Sustituye los nombres, identificadores y el número de serie de ejemplo por los de tu laboratorio.

### Consultar ONTs no aprovisionadas

```text title="Comandos"
show interfaces-state interface CT_LT1_PON1_1_GPON channel-termination onus-present-on-local-channel-termination
```

### Crear la interfaz V-ANI

```text title="Comandos"
interfaces interface ONT-01 type v-ani
enabled true
performance enable false
v-ani onu-id 0
v-ani channel-partition LT1_PON1_CPART_GPON
v-ani expected-serial-number ALCL00000002
v-ani preferred-channel-pair LT1_PON1_CPAIR_GPON
v-ani upstream-fec true
v-ani management-gemport-aes-indicator false
v-ani tod-enable false
v-ani onu-name ONT-01
```

#### Verificar la V-ANI

```text title="Salida de verificación"
OLT-02.LT1(config-interface-ONT-01)# show full-configuration
interface ONT-01
 type v-ani
 enabled true
 performance enable false
 v-ani
  onu-id 0
  channel-partition LT1_PON1_CPART_GPON
  expected-serial-number ALCL00000002
  preferred-channel-pair LT1_PON1_CPAIR_GPON
  upstream-fec true
  management-gemport-aes-indicator false
  tod-enable false
  onu-name ONT-01
 !
```

### Crear los nodos del scheduler

```text title="Comandos"
interfaces interface LT1_PON1_CPART_GPON
tm-root scheduler-node ONT-01 scheduling-level 1 
exit
tm-root scheduler-node ONT-01 child-scheduler-nodes ONT-01_VEIP priority 0 weight 1
exit
tm-root scheduler-node ONT-01_VEIP scheduling-level 2 contains-queues true
exit
tm-root scheduler-node ONT-01_VEIP queue local-queue-id 0 priority 0 weight 1
exit
tm-root child-scheduler-nodes ONT-01 priority 0 weight 1
exit
tm-root tc-id-2-queue-id-mapping-profile-name DEFAULT_TC_TO_8Queues
```

#### Verificar los nodos del scheduler

```text title="Salida de verificación"
LT1-GPON(config-interface-LT1_PON1_CPART_GPON)# show full-configuration
interface LT1_PON1_CPART_GPON
 type channel-partition
 enabled true
 tm-root
  scheduler-node ONT-01
   scheduling-level 1
   child-scheduler-nodes ONT-01_VEIP
    priority 0
    weight 1
   !
  !
  scheduler-node ONT-01_VEIP
   scheduling-level 2
   contains-queues true
   queue
    local-queue-id 0
    priority 0
    weight 1
   !
  !
  child-scheduler-nodes ONT-01
   priority 0
   weight 1
  !
  tc-id-2-queue-id-mapping-profile-name DEFAULT_TC_TO_8Queues
 !
 channel-partition
  channel-group-ref LT1_PON1
  channel-partition-index 1
  downstream-fec true
  closest-onu-distance 0
  maximum-differential-xpon-distance 20
  authentication-method as-per-v-ani-expected
  multicast-aes-indicator false
  early-fetch-onu-loid-info false
 !
!
```

### Crear el perfil de suscriptor

Crea este perfil una sola vez por LT y reutilízalo para las ONTs que compartan los mismos identificadores de suscriptor.

```text title="Comandos"
subscriber-profiles subscriber-profile test
circuit-id 1
remote-id 1
subscriber-id 1
```

### Crear la interfaz V-ENET

```text title="Comandos"
interfaces interface VENET_ONT-01_VEIP type olt-v-enet
enabled true
mac-learning max-number-mac-addresses 4
egress-tm-objects root-if-name LT1_PON1_CPART_GPON scheduler-node-name ONT-01_VEIP 
olt-v-enet lower-layer-interface ONT-01 protocol-identifier-helper slot-id 14 port-id 1
```

#### Verificar la V-ENET

```text title="Salida de verificación"
OLT-02.LT1(config-interface-VENET_ONT-01_VEIP)# show full-configuration
interface VENET_ONT-01_VEIP
 type olt-v-enet
 enabled true
 mac-learning max-number-mac-addresses 4
 egress-tm-objects
  root-if-name LT1_PON1_CPART_GPON
  scheduler-node-name ONT-01_VEIP
 !
 olt-v-enet
  lower-layer-interface ONT-01
  protocol-identifier-helper
   slot-id 14
   port-id 1
  !
 !
```

### Instanciar la ONU desde la plantilla

```text title="Comandos"
onus onu ONT-01 
usage node-from-template-usage
template-parameters template-ref GENERIC-NOKIA
template-parameters interfaces interface template-ref ANI
template-parameters hardware-config hardware template-ref SFP
tca-monitoring-enabled false
exit
template-parameters hardware-config hardware template-ref CHASSIS admin-state unlocked
```

#### Verificar la instancia de ONU

```text title="Salida de verificación"
OLT-02.LT1(config-onu-ONT-01)# show full-configuration
onu ONT-01
 usage node-from-template-usage
 template-parameters
  template-ref GENERIC-NOKIA
  interfaces interface template-ref ANI
  hardware-config
   hardware
    template-ref SFP
    tca-monitoring-enabled false
   !
   hardware
    template-ref CHASSIS
    admin-state unlocked
   !
  !
 !
!
```

## Crear los perfiles de servicio

Ejecuta estas tareas en el contexto de la **LT**. Los perfiles son reutilizables: créalos una vez y aplícalos a las ONTs que compartan el servicio.

### Perfil de control de aprendizaje MAC

```text title="Comandos"
forwarding mac-learning-control-profiles mac-learning-control-profile mlcp1
mac-learning-rule user-port
mac-can-not-move-to [ user-port subtended-node-port ]
exit
mac-learning-rule subtended-node-port
mac-can-not-move-to [ user-port subtended-node-port ]
commit
```

#### Verificar el perfil de aprendizaje MAC

```text title="Salida de verificación"
LT1-GPON(config-mac-learning-control-profile-mlcp1)# show full-configuration
mac-learning-control-profile mlcp1
 mac-learning-rule
  receiving-interface-usage user-port
  mac-can-not-move-to [ user-port subtended-node-port ]
 !
 mac-learning-rule
  receiving-interface-usage subtended-node-port
  mac-can-not-move-to [ user-port subtended-node-port ]
 !
!
```

### Base de datos de forwarding

```text title="Comandos"
forwarding forwarding-databases forwarding-database FWD_DB_HSI
max-number-mac-addresses 4294967295
aging-timer 300
mac-learning-control mac-learning-control-profile mlcp1
mac-learning-control generate-mac-learning-alarm true
```

#### Verificar la base de datos de forwarding

```text title="Salida de verificación"
OLT-02.LT1(config)# forwarding forwarding-databases forwarding-database FWD_DB_HSI
OLT-02.LT1(config-forwarding-database-FWD_DB_HSI)# show full-configuration
forwarding-database FWD_DB_HSI
 max-number-mac-addresses 4294967295
 aging-timer 300
 mac-learning-control
  mac-learning-control-profile mlcp1
  generate-mac-learning-alarm true
 !
!
```

### Perfil split-horizon

:::warning Valores sin autocompletado
En este contexto, `user-port` y `[ user-port subtended-node-port ]` deben escribirse completos.
:::

```text title="Comandos"
forwarding split-horizon-profiles split-horizon-profile spl1
split-horizon user-port
out-interface-usage [ user-port subtended-node-port ]
exit
split-horizon subtended-node-port
out-interface-usage [ user-port subtended-node-port ]
```

#### Verificar el perfil split-horizon

```text title="Salida de verificación"
LT1-GPON(config-split-horizon-profile-spl1)# show full-configuration
split-horizon-profile spl1
 split-horizon
  in-interface-usage user-port
  out-interface-usage [ user-port subtended-node-port ]
 !
 split-horizon
  in-interface-usage subtended-node-port
  out-interface-usage [ user-port subtended-node-port ]
 !
!
```

### Perfil de políticas de flooding

```text title="Comandos"
forwarding flooding-policies-profiles flooding-policies-profile drop_all
flooding-policy dn_drop
in-interface-usages interface-usages [ network-port ]
destination-address any-frame
out-interface-usages interface-usages [ subtended-node-port ]
exit
flooding-policy up_drop
in-interface-usages interface-usages [ user-port ]
destination-address any-multicast-mac-address
discard
```

#### Verificar las políticas de flooding

```text title="Salida de verificación"
LT1-GPON(config-flooding-policies-profile-drop_all)# show full-configuration
flooding-policies-profile drop_all
 flooding-policy dn_drop
  in-interface-usages interface-usages network-port
  destination-address any-frame
  out-interface-usages interface-usages subtended-node-port
 !
 flooding-policy up_drop
  in-interface-usages interface-usages user-port
  destination-address any-multicast-mac-address
  discard
 !
!
```

### Perfil de procesamiento de trama para una VLAN

:::warning Valores sin autocompletado
Escribe completos `c-vlan`, `parameter-vlan-id`, `any` y `vlan-id-from-match`; el eCLI no los propone mediante autocompletado.
:::

```text title="Comandos"
frame-processing-profiles frame-processing-profile CC-SINGLE-VLAN-PROFILE
priority 100
match-criteria tag 0
tag-type c-vlan
vlan-id parameter-vlan-id
pbit any
dei any
exit
ingress-rewrite pop-tags 1
ingress-rewrite copy-from-tags-to-marking-list 0
pbit-marking-index 0
dei-marking-index 0
exit
egress-rewrite push-tag 0
tag-type c-vlan
vlan-id vlan-id-from-match
pbit-marking-index 0
dei-marking-index  0
```

#### Verificar el perfil de una VLAN

```text title="Salida de verificación"
LT1-GPON(config)# frame-processing-profiles frame-processing-profile CC-SINGLE-VLAN-PROFILE
LT1-GPON(config-frame-processing-profile-CC-SINGLE-VLAN-PROFILE)# show full-configuration
frame-processing-profile CC-SINGLE-VLAN-PROFILE
 priority 100
 match-criteria tag 0
  tag-type c-vlan
  vlan-id parameter-vlan-id
  pbit any
  dei any
 !
 ingress-rewrite
  copy-from-tags-to-marking-list
   tag-index 0
   pbit-marking-index 0
   dei-marking-index 0
  !
  pop-tags 1
 !
 egress-rewrite push-tag 0
  tag-type c-vlan
  vlan-id vlan-id-from-match
  pbit-marking-index 0
  dei-marking-index 0
 !
!
```

### Perfil de marcado P-bit para tramas con una etiqueta

```text title="Comandos"
frame-processing-profiles frame-processing-profile Single_Tagged_PBIT_Marking_Done
priority 100
match-criteria tag 0
tag-type c-vlan
vlan-id parameter-vlan-id
pbit any
dei any
exit
ingress-rewrite pop-tags 1
egress-rewrite push-tag 0
tag-type c-vlan
vlan-id vlan-id-from-match
pbit-marking-index 0
dei-marking-index 0
```

#### Verificar el perfil de marcado P-bit

```text title="Salida de verificación"
LT1-GPON(config-frame-processing-profile-Single_Tagged_PBIT_Marking_Done)# show full-configuration
frame-processing-profile Single_Tagged_PBIT_Marking_Done
 priority 100
 match-criteria tag 0
  tag-type c-vlan
  vlan-id parameter-vlan-id
  pbit any
  dei any
 !
 ingress-rewrite pop-tags 1
 egress-rewrite push-tag 0
  tag-type c-vlan
  vlan-id vlan-id-from-match
  pbit-marking-index 0
  dei-marking-index 0
 !
!
```

### Subinterfaz VLAN de red

```text title="Comandos"
interfaces interface NTW_VSI_HSI
type vlan-sub-interface
enabled
interface-usage interface-usage network-port
mac-learning mac-learning-enable true    
subif-lower-layer interface BP_Eth
frame-processing-profile-ref CC-SINGLE-VLAN-PROFILE
tag-0 vlan-id 100
```

#### Verificar la subinterfaz VLAN de red

```text title="Salida de verificación"
LT1-GPON(config-push-tag-0)# interfaces interface NTW_VSI_HSI
LT1-GPON(config-interface-NTW_VSI_HSI)# show full-configuration
interface NTW_VSI_HSI
 type vlan-sub-interface
 enabled true
 interface-usage interface-usage network-port
 mac-learning mac-learning-enable true
 subif-lower-layer interface BP_Eth
 frame-processing-profile-ref CC-SINGLE-VLAN-PROFILE
 tag-0 vlan-id 100
!
```

### Perfil de forwarder

```text title="Comandos"
forwarding forwarders forwarder FWD_HSI 
ports port NTW_PORT_HSI sub-interface NTW_VSI_HSI
flooding-policies flooding-policies-profile drop_all
mac-learning forwarding-database FWD_DB_HSI
split-horizon-profiles split-horizon-profile spl1
l2-dhcpv4-relay downstream-broadcast-flooding false
arp-security downstream-arp-broadcast secured-with-fallback-to-layer2
ND-security downstream-ns-multicast secured-forwarding
```

#### Verificar el forwarder

```text title="Salida de verificación"
OLT-02.LT1(config)# forwarding forwarders forwarder FWD_HSI
LT1-GPON(config-forwarder-FWD_HSI)# show full-configuration
forwarder FWD_HSI
 ports port NTW_PORT_HSI
  sub-interface NTW_VSI_HSI
 !
 flooding-policies flooding-policies-profile drop_all
 mac-learning forwarding-database FWD_DB_HSI
 split-horizon-profiles split-horizon-profile spl1
 l2-dhcpv4-relay downstream-broadcast-flooding false
 arp-security downstream-arp-broadcast secured-with-fallback-to-layer2
 ND-security downstream-ns-multicast secured-forwarding
!
LT1-GPON(config-forwarder-FWD_HSI)#
```

### Perfil DHCPv4

```text title="Comandos"
l2-dhcpv4-relay-profiles l2-dhcpv4-relay-profile DHCP_Default
max-packet-size 1500
option82-format suboptions [ circuit-id remote-id ]
option82-format default-circuit-id-syntax Access_Node_ID:Chassis:Port:OnuID:v-ani:olt-v-enet
option82-format start-numbering-from-zero false
option82-format use-leading-zeroes false
```

#### Verificar el perfil DHCPv4

```text title="Salida de verificación"
LT1-GPON(config-l2-dhcpv4-relay-profile-DHCP_Default)# show full-configuration
l2-dhcpv4-relay-profile DHCP_Default
 max-packet-size 1500
 option82-format
  suboptions [ circuit-id remote-id ]
  default-circuit-id-syntax Access_Node_ID:Chassis:Port:OnuID:v-ani:olt-v-enet
  start-numbering-from-zero false
  use-leading-zeroes false
 !
!
```

### Perfil DHCPv6

```text title="Comandos"
dhcpv6-ldra-profiles dhcpv6-ldra-profile DHCPv6_Default
options option [ interface-id remote-id vendor-specific-information ]
options default-interface-id-syntax Access_Node_ID:Chassis:Port:OnuID:v-ani:olt-v-enet
options default-remote-id-syntax pon-id
options start-numbering-from-zero false
options use-leading-zeroes false
options xpon-access-loop-characteristics [ xpon-tree-maximum-data-rate-upstream onu-maximum-data-rate-upstream xpon-tree-maximum-data-rate-downstream onu-peak-data-rate-downstream ]
```

#### Verificar el perfil DHCPv6

```text title="Salida de verificación"
LT1-GPON(config)# dhcpv6-ldra-profiles dhcpv6-ldra-profile DHCPv6_Default
LT1-GPON(config-dhcpv6-ldra-profile-DHCPv6_Default)# show full-configuration
dhcpv6-ldra-profile DHCPv6_Default
 options
  option [ interface-id remote-id vendor-specific-information ]
  default-interface-id-syntax Access_Node_ID:Chassis:Port:OnuID:v-ani:olt-v-enet
  default-remote-id-syntax pon-id
  start-numbering-from-zero false
  use-leading-zeroes false
  xpon-access-loop-characteristics [ xpon-tree-maximum-data-rate-upstream onu-maximum-data-rate-upstream xpon-tree-maximum-data-rate-downstream onu-peak-data-rate-downstream ]
 !
!
```

### Perfil PPPoE

```text title="Comandos"
pppoe-profiles pppoe-profile PPPoE_Default
pppoe-vendor-specific-tag subtag [ circuit-id remote-id ]
pppoe-vendor-specific-tag default-remote-id-syntax Access_Node_ID:Chassis:Port:OnuID:v-ani:olt-v-enet
pppoe-vendor-specific-tag start-numbering-from-zero false
pppoe-vendor-specific-tag use-leading-zeroes false
```

#### Verificar el perfil PPPoE

```text title="Salida de verificación"
LT1-GPON(config-pppoe-profile-PPPoE_Default)# show full-configuration
pppoe-profile PPPoE_Default
 pppoe-vendor-specific-tag
  subtag [ circuit-id remote-id ]
  default-remote-id-syntax Access_Node_ID:Chassis:Port:OnuID:v-ani:olt-v-enet
  start-numbering-from-zero false
  use-leading-zeroes false
 !
!
```

### Perfil vectorial de la VSI

```text title="Comandos"
vsi-vector-profiles vsi-vector-profile default
ipv4-security prevent-ipv4-address-spoofing true
ipv4-security learn-addresses-from-dhcp
ipv4-security max-address no-limit
l2-dhcpv4-relay enable true
l2-dhcpv4-relay trusted-port false
l2-dhcpv4-relay profile-ref DHCP_Default
dhcpv6-ldra enable true
dhcpv6-ldra trusted-port true
dhcpv6-ldra profile-ref DHCPv6_Default
pppoe enable true
pppoe profile-ref PPPoE_Default
interface-usage interface-usage user-port
```

#### Verificar el perfil vectorial

```text title="Salida de verificación"
LT1-GPON(config-vsi-vector-profile-default)# show full-configuration
vsi-vector-profile default
 l2-dhcpv4-relay
  enable true
  trusted-port false
  profile-ref DHCP_Default
 !
 dhcpv6-ldra
  enable true
  trusted-port true
  profile-ref DHCPv6_Default
 !
 pppoe
  enable true
  profile-ref PPPoE_Default
 !
 interface-usage interface-usage user-port
 ipv4-security
  prevent-ipv4-address-spoofing true
  learn-addresses-from-dhcp
  max-address no-limit
 !
!
```

### Descriptor de tráfico upstream

```text title="Comandos"
xpongemtcont traffic-descriptor-profiles traffic-descriptor-profile 100M_UP
fixed-bandwidth 0
assured-bandwidth 0
maximum-bandwidth 100000000
jitter-tolerance 16
```

#### Verificar el descriptor de tráfico

```text title="Salida de verificación"
LT1-GPON(config)# xpongemtcont traffic-descriptor-profiles traffic-descriptor-profile 100M_UP
LT1-GPON(config-traffic-descriptor-profile-100M_UP)# show full-configuration
traffic-descriptor-profile 100M_UP
 fixed-bandwidth 0
 assured-bandwidth 0
 maximum-bandwidth 100000000
 jitter-tolerance 16
!
LT1-GPON(config-traffic-descriptor-profile-100M_UP)# show full-configuration
traffic-descriptor-profile 100M_UP
 fixed-bandwidth 0
 assured-bandwidth 0
 maximum-bandwidth 100000000
 jitter-tolerance 16
!
```

### Clasificadores QoS

La jerarquía es: **perfil de política QoS → políticas → clasificadores**. Los siguientes clasificadores asignan todos los valores P-bit a la clase de tráfico 0 y conservan o escriben el marcado P-bit.

```text title="Comandos"
classifiers classifier-entry pbit0_to_TC0
filter-operation match-all-filter
match-criteria pbit-marking-list 0
pbit-value 0
exit
classifier-action-entry-cfg scheduling-traffic-class
scheduling-traffic-class 0
exit
exit
classifiers classifier-entry pbit1_to_TC0
filter-operation match-all-filter
match-criteria pbit-marking-list 0
pbit-value 1
exit
classifier-action-entry-cfg scheduling-traffic-class
scheduling-traffic-class 0
exit
exit
classifiers classifier-entry pbit2_to_TC0
filter-operation match-all-filter
match-criteria pbit-marking-list 0
pbit-value 2
exit
classifier-action-entry-cfg scheduling-traffic-class
scheduling-traffic-class 0
exit
exit
classifiers classifier-entry pbit3_to_TC0
filter-operation match-all-filter
match-criteria pbit-marking-list 0
pbit-value 3
exit
classifier-action-entry-cfg scheduling-traffic-class
scheduling-traffic-class 0
exit
exit
classifiers classifier-entry pbit4_to_TC0
filter-operation match-all-filter
match-criteria pbit-marking-list 0
pbit-value 4
exit
classifier-action-entry-cfg scheduling-traffic-class
scheduling-traffic-class 0
exit
exit
classifiers classifier-entry pbit5_to_TC0
filter-operation match-all-filter
match-criteria pbit-marking-list 0
pbit-value 5
exit
classifier-action-entry-cfg scheduling-traffic-class
scheduling-traffic-class 0
exit
exit
classifiers classifier-entry pbit6_to_TC0
filter-operation match-all-filter
match-criteria pbit-marking-list 0
pbit-value 6
exit
classifier-action-entry-cfg scheduling-traffic-class
scheduling-traffic-class 0
exit
exit
classifiers classifier-entry pbit7_to_TC0
filter-operation match-all-filter
match-criteria pbit-marking-list 0
pbit-value 7
exit
classifier-action-entry-cfg scheduling-traffic-class
scheduling-traffic-class 0
exit
exit
```

```text title="Comandos"
classifiers classifier-entry untag_pbit_hsi_tc0
filter-operation match-all-filter
vlans untagged
classifier-action-entry-cfg pbit-marking
pbit-marking-cfg pbit-marking-list 0
pbit-value 0
```

```text title="Comandos"
classifier-entry copy_tag_pbit0
filter-operation match-all-filter
match-criteria
tag 0
in-pbit-list 0
exit
dscp-range any
any-protocol
exit
classifier-action-entry-cfg
action-type pbit-marking
pbit-marking-cfg pbit-marking-list 0
pbit-value 0
```

```text title="Comandos"
classifier-entry copy_tag_pbit1
filter-operation match-all-filter
match-criteria
tag 0
in-pbit-list 1
exit
dscp-range any
any-protocol
exit
classifier-action-entry-cfg
action-type pbit-marking
pbit-marking-cfg pbit-marking-list 0
pbit-value 1
```

```text title="Comandos"
classifier-entry copy_tag_pbit2
filter-operation match-all-filter
match-criteria
tag 0
in-pbit-list 2
exit
dscp-range any
any-protocol
exit
classifier-action-entry-cfg
action-type pbit-marking
pbit-marking-cfg pbit-marking-list 0
pbit-value 2
```

```text title="Comandos"
classifier-entry copy_tag_pbit3
filter-operation match-all-filter
match-criteria
tag 0
in-pbit-list 3
exit
dscp-range any
any-protocol
exit
classifier-action-entry-cfg
action-type pbit-marking
pbit-marking-cfg pbit-marking-list 0
pbit-value 3
```

```text title="Comandos"
classifier-entry copy_tag_pbit4
filter-operation match-all-filter
match-criteria
tag 0
in-pbit-list 4
exit
dscp-range any
any-protocol
exit
classifier-action-entry-cfg
action-type pbit-marking
pbit-marking-cfg pbit-marking-list 0
pbit-value 4
```

```text title="Comandos"
classifier-entry copy_tag_pbit5
filter-operation match-all-filter
match-criteria
tag 0
in-pbit-list 5
exit
dscp-range any
any-protocol
exit
classifier-action-entry-cfg
action-type pbit-marking
pbit-marking-cfg pbit-marking-list 0
pbit-value 5
```

```text title="Comandos"
classifier-entry copy_tag_pbit6
filter-operation match-all-filter
match-criteria
tag 0
in-pbit-list 6
exit
dscp-range any
any-protocol
exit
classifier-action-entry-cfg
action-type pbit-marking
pbit-marking-cfg pbit-marking-list 0
pbit-value 6
```

```text title="Comandos"
classifier-entry copy_tag_pbit7
filter-operation match-all-filter
match-criteria
tag 0
in-pbit-list 7
exit
dscp-range any
any-protocol
exit
classifier-action-entry-cfg
action-type pbit-marking
pbit-marking-cfg pbit-marking-list 0
pbit-value 7
```

### Políticas QoS

```text title="Comandos"
policies policy pbit0-7_to_TC0
classifiers pbit0_to_TC0
exit
classifiers pbit1_to_TC0
exit
classifiers pbit2_to_TC0
exit
classifiers pbit3_to_TC0
exit
classifiers pbit4_to_TC0
exit
classifiers pbit5_to_TC0
exit
classifiers pbit6_to_TC0
exit
classifiers pbit7_to_TC0
```

```text title="Comandos"
policies policy untag_tag_pbit_hsi_tc0
classifiers untag_pbit_hsi_tc0
exit
classifiers copy_tag_pbit0
exit
classifiers copy_tag_pbit1
exit
classifiers copy_tag_pbit2
exit
classifiers copy_tag_pbit3
exit
classifiers copy_tag_pbit4
exit
classifiers copy_tag_pbit5
exit
classifiers copy_tag_pbit6
exit
classifiers copy_tag_pbit7
```

### Perfiles de políticas QoS

```text title="Comandos"
qos-policy-profiles policy-profile DS_HSI_TC0
policy-list pbit0-7_to_TC0
exit
```

```text title="Comandos"
qos-policy-profiles policy-profile US_HSI_TC0
policy-list untag_tag_pbit_hsi_tc0
```

## Crear el servicio de usuario de capa 2

### Crear el T-CONT

```text title="Comandos"
xpongemtcont tconts tcont TCONT_ONT-01_VEIP_HSI
alloc-id 256
interface-reference ONT-01
traffic-descriptor-profile-ref 100M_UP
```

#### Verificar el T-CONT

```text title="Salida de verificación"
OLT-02.LT1(config)# xpongemtcont tconts tcont TCONT_ONT-01_VEIP_HSI
OLT-02.LT1(config-tcont-TCONT_ONT-01_VEIP_HSI)# show full-configuration
tcont TCONT_ONT-01_VEIP_HSI
 alloc-id 256
 interface-reference ONT-01
 traffic-descriptor-profile-ref 100M_UP
!
```

### Crear la VSI de usuario

```text title="Comandos"
interfaces interface VSI_ONT-01_VEIP_HSI
type vlan-sub-interface
enabled true
performance enable false
mac-learning max-number-mac-addresses 4
mac-learning mac-learning-enable true
ingress-qos-policy-profile US_HSI_TC0
egress-qos-policy-profile DS_HSI_TC0
subif-lower-layer interface VENET_ONT-01_VEIP
frame-processing-profile-ref Single_Tagged_PBIT_Marking_Done
tag-0 vlan-id 10
subscriber-profile profile test
vector-profile default
```

#### Verificar la VSI

```text title="Salida de verificación"
OLT-02.LT1(config-interface-VSI_ONT-01_VEIP_HSI)# show full-configuration
interface VSI_ONT-01_VEIP_HSI
 description
 type vlan-sub-interface
 enabled true
 performance enable false
 mac-learning
  max-number-mac-addresses 4
  mac-learning-enable true
 !
 ingress-qos-policy-profile US_HSI_TC0
 egress-qos-policy-profile DS_HSI_TC0
 subif-lower-layer interface VENET_ONT-01_VEIP
 frame-processing-profile-ref Single_Tagged_PBIT_Marking_Done
 tag-0 vlan-id 10
 subscriber-profile profile HSI_ONT-01
 vector-profile default
!
```

### Crear el GEM port

```text title="Comandos"
xpongemtcont gemports gemport GEM0_ONT-01_VEIP_HSI
gemport-id 256
interface VSI_ONT-01_VEIP_HSI
traffic-class 0
downstream-aes-indicator false
upstream-aes-indicator false
exit
```

#### Verificar el GEM port

```text title="Salida de verificación"
OLT-02.LT1(config)# xpongemtcont gemports gemport GEM0_ONT-01_VEIP_HSI
OLT-02.LT1(config-gemport-GEM0_ONT-01_VEIP_HSI)# show full-configuration
gemport GEM0_ONT-01_VEIP_HSI
 gemport-id 256
 interface VSI_ONT-01_VEIP_HSI
 traffic-class 0
 downstream-aes-indicator false
 upstream-aes-indicator false
!
```

### Añadir el puerto de usuario al forwarder

```text title="Comandos"
forwarding forwarders forwarder FWD_HSI
forwarding forwarders forwarder FWD_HSI ports port USR_PORT_ONT-01_VEIP_HSI sub-interface VSI_ONT-01_VEIP_HSI
```

### Completar la ONT

```text title="Comandos"
onus onu ONT-01
template-parameters tconts tcont template-ref TCONT_VEIP_HSI id 256
exit
template-parameters gemports gemport template-ref GEM0_VEIP_HSI id 256
template-parameters interfaces interface template-ref ENET_VEIP admin true
template-parameters interfaces interface template-ref VSI_VEIP_HSI pm-enable false vsi ingress-rule single-tagged match-criteria-tag-0-vlan-id 10 ingress-rewrite-tag-0-vlan-id 10
exit
template-parameters interfaces interface template-ref VSI_VEIP_HSI vsi ingress-qos-policy-profile Q_HSI_TC0
```

#### Verificar la ONT

```text title="Salida de verificación"
LT1-GPON(config-onu-ONT-01)# show full-configuration
onu ONT-01
 usage node-from-template-usage
 template-parameters
  template-ref GENERIC-NOKIA
  tconts tcont
   template-ref TCONT_VEIP_HSI
   id 256
  !
  gemports gemport
   template-ref GEM0_VEIP_HSI
   id 256
  !
  interfaces
   interface template-ref ANI
   interface
    template-ref ENET_VEIP
    admin true
   !
   interface
    template-ref VSI_VEIP_HSI
    pm-enable false
    vsi
     ingress-rule single-tagged
      match-criteria-tag-0-vlan-id 10
      ingress-rewrite-tag-0-vlan-id 10
     !
     ingress-qos-policy-profile Q_HSI_TC0
    !
   !
  !
  hardware-config
   hardware
    template-ref SFP
    tca-monitoring-enabled false
   !
   hardware
    template-ref CHASSIS
    admin-state unlocked
   !
  !
 !
!
```

## Ejemplo de configuración completa

Este bloque reúne todos los perfiles y objetos necesarios para crear una ONT con los nombres y valores del laboratorio de ejemplo.

```text title="Comandos"
forward cli to lt-1
config
hardware component PONSFP_1 class transceiver
parent C1
parent-rel-pos 1
model-name 3FE53441AA
exit
hardware component PON_1_GPON class transceiver-link-gpon
parent PONSFP_1
parent-rel-pos 1
exit
interfaces interface LT1_PON1 type channel-group
enabled
channel-group polling-period 100
channel-group raman-mitigation raman-none
channel-group system-id 00000
exit
tm-profiles tc-id-2-queue-id-mapping-profile DEFAULT_TC_TO_8Queues
mapping-entry 0
local-queue-id 0
exit
mapping-entry 1
local-queue-id 1
exit
mapping-entry 2
local-queue-id 2
exit
mapping-entry 3
local-queue-id 3
exit
mapping-entry 4
local-queue-id 4
exit
mapping-entry 5
local-queue-id 5
exit
mapping-entry 6
local-queue-id 6
exit
mapping-entry 7
local-queue-id 7
exit
interfaces interface LT1_PON1_CPART_GPON type channel-partition 
enabled true
channel-partition channel-group-ref LT1_PON1
channel-partition channel-partition-index 1
channel-partition downstream-fec true
channel-partition closest-onu-distance 0
channel-partition maximum-differential-xpon-distance 20
channel-partition authentication-method as-per-v-ani-expected
channel-partition multicast-aes-indicator false
channel-partition early-fetch-onu-loid-info false
exit
interfaces interface LT1_PON1_CPAIR_GPON
type channel-pair
enabled true
channel-pair channel-group-ref LT1_PON1
channel-pair channel-partition-ref LT1_PON1_CPART_GPON
channel-pair channel-pair-type gpon
channel-pair gpon-pon-id-interval 10
multicast-cac max-group-number no-limit
multicast-cac max-multicast-rate-limit no-limit
multicast-cac multicast-rate-limit-exceed-action best-effort
exit
interfaces interface CT_LT1_PON1_1_GPON
description LT1_PON1
type channel-termination
enabled true
port-layer-if PON_1_GPON
channel-termination channel-pair-ref LT1_PON1_CPAIR_GPON
channel-termination channel-termination-type gpon
channel-termination gpon-pon-id 00000000000000
channel-termination ber-calc-period 10
channel-termination location inside-olt
channel-termination laser-on-by-default true
exit
onus onu GENERIC-NOKIA usage node-template-usage
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit_marking_untag_write_pbit0 filter-operation match-all-filter
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit_marking_untag_write_pbit0 match-criteria untagged
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit_marking_untag_write_pbit0 classifier-action-entry-cfg pbit-marking pbit-marking-cfg pbit-marking-list 0 pbit-value 0
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit_marking_copy_pbit0 filter-operation match-all-filter
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit_marking_copy_pbit0 match-criteria tag 0 in-pbit-list 0
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit_marking_copy_pbit0 match-criteria dscp-range any
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit_marking_copy_pbit0 classifier-action-entry-cfg pbit-marking pbit-marking-cfg pbit-marking-list 0 pbit-value 0
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit_marking_copy_pbit1 filter-operation match-all-filter
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit_marking_copy_pbit1 match-criteria tag 0 in-pbit-list 1
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit_marking_copy_pbit1 match-criteria dscp-range any
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit_marking_copy_pbit1 classifier-action-entry-cfg pbit-marking pbit-marking-cfg pbit-marking-list 0 pbit-value 1
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit_marking_copy_pbit2 filter-operation match-all-filter
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit_marking_copy_pbit2 match-criteria tag 0 in-pbit-list 2
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit_marking_copy_pbit2 match-criteria dscp-range any
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit_marking_copy_pbit2 classifier-action-entry-cfg pbit-marking pbit-marking-cfg pbit-marking-list 0 pbit-value 2
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit_marking_copy_pbit3 filter-operation match-all-filter
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit_marking_copy_pbit3 match-criteria tag 0 in-pbit-list 3
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit_marking_copy_pbit3 match-criteria dscp-range any
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit_marking_copy_pbit3 classifier-action-entry-cfg pbit-marking pbit-marking-cfg pbit-marking-list 0 pbit-value 3
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit_marking_copy_pbit4 filter-operation match-all-filter
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit_marking_copy_pbit4 match-criteria tag 0 in-pbit-list 4
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit_marking_copy_pbit4 match-criteria dscp-range any
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit_marking_copy_pbit4 classifier-action-entry-cfg pbit-marking pbit-marking-cfg pbit-marking-list 0 pbit-value 4
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit_marking_copy_pbit5 filter-operation match-all-filter
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit_marking_copy_pbit5 match-criteria tag 0 in-pbit-list 5
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit_marking_copy_pbit5 match-criteria dscp-range any
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit_marking_copy_pbit5 classifier-action-entry-cfg pbit-marking pbit-marking-cfg pbit-marking-list 0 pbit-value 5
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit_marking_copy_pbit6 filter-operation match-all-filter
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit_marking_copy_pbit6 match-criteria tag 0 in-pbit-list 6
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit_marking_copy_pbit6 match-criteria dscp-range any
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit_marking_copy_pbit6 classifier-action-entry-cfg pbit-marking pbit-marking-cfg pbit-marking-list 0 pbit-value 6
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit_marking_copy_pbit7 filter-operation match-all-filter
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit_marking_copy_pbit7 match-criteria tag 0 in-pbit-list 7
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit_marking_copy_pbit7 match-criteria dscp-range any
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit_marking_copy_pbit7 classifier-action-entry-cfg pbit-marking pbit-marking-cfg pbit-marking-list 0 pbit-value 7
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit2tc_pbit0_to_tc0 filter-operation match-all-filter
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit2tc_pbit0_to_tc0 match-criteria pbit-marking-list 0 pbit-value 0
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit2tc_pbit0_to_tc0 classifier-action-entry-cfg scheduling-traffic-class scheduling-traffic-class 0
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit2tc_pbit1_to_tc0 filter-operation match-all-filter
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit2tc_pbit1_to_tc0 match-criteria pbit-marking-list 0 pbit-value 1
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit2tc_pbit1_to_tc0 classifier-action-entry-cfg scheduling-traffic-class scheduling-traffic-class 0
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit2tc_pbit2_to_tc0 filter-operation match-all-filter
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit2tc_pbit2_to_tc0 match-criteria pbit-marking-list 0 pbit-value 2
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit2tc_pbit2_to_tc0 classifier-action-entry-cfg scheduling-traffic-class scheduling-traffic-class 0
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit2tc_pbit3_to_tc0 filter-operation match-all-filter
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit2tc_pbit3_to_tc0 match-criteria pbit-marking-list 0 pbit-value 3
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit2tc_pbit3_to_tc0 classifier-action-entry-cfg scheduling-traffic-class scheduling-traffic-class 0
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit2tc_pbit4_to_tc0 filter-operation match-all-filter
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit2tc_pbit4_to_tc0 match-criteria pbit-marking-list 0 pbit-value 4
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit2tc_pbit4_to_tc0 classifier-action-entry-cfg scheduling-traffic-class scheduling-traffic-class 0
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit2tc_pbit5_to_tc0 filter-operation match-all-filter
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit2tc_pbit5_to_tc0 match-criteria pbit-marking-list 0 pbit-value 5
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit2tc_pbit5_to_tc0 classifier-action-entry-cfg scheduling-traffic-class scheduling-traffic-class 0
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit2tc_pbit6_to_tc0 filter-operation match-all-filter
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit2tc_pbit6_to_tc0 match-criteria pbit-marking-list 0 pbit-value 6
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit2tc_pbit6_to_tc0 classifier-action-entry-cfg scheduling-traffic-class scheduling-traffic-class 0
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit2tc_pbit7_to_tc0 filter-operation match-all-filter
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit2tc_pbit7_to_tc0 match-criteria pbit-marking-list 0 pbit-value 7
onus onu GENERIC-NOKIA root classifiers classifier-entry pbit2tc_pbit7_to_tc0 classifier-action-entry-cfg scheduling-traffic-class scheduling-traffic-class 0
onus onu GENERIC-NOKIA root policies policy HSI_TC0 classifiers pbit_marking_untag_write_pbit0
onus onu GENERIC-NOKIA root policies policy HSI_TC0 classifiers pbit_marking_copy_pbit0
onus onu GENERIC-NOKIA root policies policy HSI_TC0 classifiers pbit_marking_copy_pbit1
onus onu GENERIC-NOKIA root policies policy HSI_TC0 classifiers pbit_marking_copy_pbit2
onus onu GENERIC-NOKIA root policies policy HSI_TC0 classifiers pbit_marking_copy_pbit3
onus onu GENERIC-NOKIA root policies policy HSI_TC0 classifiers pbit_marking_copy_pbit4
onus onu GENERIC-NOKIA root policies policy HSI_TC0 classifiers pbit_marking_copy_pbit5
onus onu GENERIC-NOKIA root policies policy HSI_TC0 classifiers pbit_marking_copy_pbit6
onus onu GENERIC-NOKIA root policies policy HSI_TC0 classifiers pbit_marking_copy_pbit7
onus onu GENERIC-NOKIA root policies policy HSI_TC0_tc classifiers pbit2tc_pbit0_to_tc0
onus onu GENERIC-NOKIA root policies policy HSI_TC0_tc classifiers pbit2tc_pbit1_to_tc0
onus onu GENERIC-NOKIA root policies policy HSI_TC0_tc classifiers pbit2tc_pbit2_to_tc0
onus onu GENERIC-NOKIA root policies policy HSI_TC0_tc classifiers pbit2tc_pbit3_to_tc0
onus onu GENERIC-NOKIA root policies policy HSI_TC0_tc classifiers pbit2tc_pbit4_to_tc0
onus onu GENERIC-NOKIA root policies policy HSI_TC0_tc classifiers pbit2tc_pbit5_to_tc0
onus onu GENERIC-NOKIA root policies policy HSI_TC0_tc classifiers pbit2tc_pbit6_to_tc0
onus onu GENERIC-NOKIA root policies policy HSI_TC0_tc classifiers pbit2tc_pbit7_to_tc0
onus onu GENERIC-NOKIA root qos-policy-profiles policy-profile Q_HSI_TC0 policy-list HSI_TC0
onus onu GENERIC-NOKIA root qos-policy-profiles policy-profile Q_HSI_TC0 policy-list HSI_TC0_tc
onus onu GENERIC-NOKIA root tm-profiles tc-id-2-queue-id-mapping-profile TC2Q_Profile_Single-TC mapping-entry 0 local-queue-id 0
onus onu GENERIC-NOKIA root tm-profiles tc-id-2-queue-id-mapping-profile TC2Q_Profile_8-TC mapping-entry 0 local-queue-id 0
onus onu GENERIC-NOKIA root tm-profiles tc-id-2-queue-id-mapping-profile TC2Q_Profile_8-TC mapping-entry 1 local-queue-id 1
onus onu GENERIC-NOKIA root tm-profiles tc-id-2-queue-id-mapping-profile TC2Q_Profile_8-TC mapping-entry 2 local-queue-id 2
onus onu GENERIC-NOKIA root tm-profiles tc-id-2-queue-id-mapping-profile TC2Q_Profile_8-TC mapping-entry 3 local-queue-id 3
onus onu GENERIC-NOKIA root tm-profiles tc-id-2-queue-id-mapping-profile TC2Q_Profile_8-TC mapping-entry 4 local-queue-id 4
onus onu GENERIC-NOKIA root tm-profiles tc-id-2-queue-id-mapping-profile TC2Q_Profile_8-TC mapping-entry 5 local-queue-id 5
onus onu GENERIC-NOKIA root tm-profiles tc-id-2-queue-id-mapping-profile TC2Q_Profile_8-TC mapping-entry 6 local-queue-id 6
onus onu GENERIC-NOKIA root tm-profiles tc-id-2-queue-id-mapping-profile TC2Q_Profile_8-TC mapping-entry 7 local-queue-id 7
onus onu GENERIC-NOKIA root voip-configuration-characteristics configuration-method omci
onus onu GENERIC-NOKIA root xpongemtcont tconts tcont TCONT_VEIP_HSI interface-reference ANI
onus onu GENERIC-NOKIA root xpongemtcont tconts tcont TCONT_VEIP_HSI tm-root queue 0 priority 1
onus onu GENERIC-NOKIA root xpongemtcont tconts tcont TCONT_VEIP_HSI tm-root queue 0 weight 1
onus onu GENERIC-NOKIA root xpongemtcont tconts tcont TCONT_VEIP_HSI tm-root tc-id-2-queue-id-mapping-profile-name TC2Q_Profile_Single-TC
onus onu GENERIC-NOKIA root xpongemtcont gemports gemport GEM0_VEIP_HSI interface VSI_VEIP_HSI
onus onu GENERIC-NOKIA root xpongemtcont gemports gemport GEM0_VEIP_HSI traffic-class 0
onus onu GENERIC-NOKIA root xpongemtcont gemports gemport GEM0_VEIP_HSI tcont-ref TCONT_VEIP_HSI
onus onu GENERIC-NOKIA root hardware component CHASSIS class chassis
onus onu GENERIC-NOKIA root hardware component CHASSIS admin-state unlocked
onus onu GENERIC-NOKIA root hardware component CAGE class cage
onus onu GENERIC-NOKIA root hardware component CAGE parent CHASSIS
onus onu GENERIC-NOKIA root hardware component CAGE parent-rel-pos 0
onus onu GENERIC-NOKIA root hardware component SFP class transceiver
onus onu GENERIC-NOKIA root hardware component SFP parent CAGE
onus onu GENERIC-NOKIA root hardware component SFP parent-rel-pos 0
onus onu GENERIC-NOKIA root hardware component ANIPORT class transceiver-link
onus onu GENERIC-NOKIA root hardware component ANIPORT parent SFP
onus onu GENERIC-NOKIA root hardware component ANIPORT parent-rel-pos 1
onus onu GENERIC-NOKIA root hardware component UNI_LAN1 class rj45
onus onu GENERIC-NOKIA root hardware component UNI_LAN1 parent CHASSIS
onus onu GENERIC-NOKIA root hardware component UNI_LAN1 parent-rel-pos 1
onus onu GENERIC-NOKIA root hardware component UNI_LAN1 omci-identifier-helper virtual-board-number 1
onus onu GENERIC-NOKIA root hardware component UNI_LAN2 class rj45
onus onu GENERIC-NOKIA root hardware component UNI_LAN2 parent CHASSIS
onus onu GENERIC-NOKIA root hardware component UNI_LAN2 parent-rel-pos 2
onus onu GENERIC-NOKIA root hardware component UNI_LAN2 omci-identifier-helper virtual-board-number 1
onus onu GENERIC-NOKIA root hardware component UNI_LAN3 class rj45
onus onu GENERIC-NOKIA root hardware component UNI_LAN3 parent CHASSIS
onus onu GENERIC-NOKIA root hardware component UNI_LAN3 parent-rel-pos 3
onus onu GENERIC-NOKIA root hardware component UNI_LAN3 omci-identifier-helper virtual-board-number 1
onus onu GENERIC-NOKIA root hardware component UNI_LAN4 class rj45
onus onu GENERIC-NOKIA root hardware component UNI_LAN4 parent CHASSIS
onus onu GENERIC-NOKIA root hardware component UNI_LAN4 parent-rel-pos 4
onus onu GENERIC-NOKIA root hardware component UNI_LAN4 omci-identifier-helper virtual-board-number 1
onus onu GENERIC-NOKIA root hardware component UNI_VEIP class virtual-port
onus onu GENERIC-NOKIA root hardware component UNI_VEIP parent CHASSIS
onus onu GENERIC-NOKIA root hardware component UNI_VEIP parent-rel-pos 1
onus onu GENERIC-NOKIA root hardware component UNI_TEL1 class rj11
onus onu GENERIC-NOKIA root hardware component UNI_TEL1 parent CHASSIS
onus onu GENERIC-NOKIA root hardware component UNI_TEL1 parent-rel-pos 1
onus onu GENERIC-NOKIA root interfaces interface ENET_LAN1 type ethernetCsmacd
onus onu GENERIC-NOKIA root interfaces interface ENET_LAN1 enabled false
onus onu GENERIC-NOKIA root interfaces interface ENET_LAN1 port-layer-if UNI_LAN1
onus onu GENERIC-NOKIA root interfaces interface ENET_LAN1 ethernet auto-negotiation status enabled
onus onu GENERIC-NOKIA root interfaces interface ENET_LAN1 ethernet auto-negotiation duplex full
onus onu GENERIC-NOKIA root interfaces interface ENET_LAN1 ethernet auto-negotiation speed eth-if-speed-1gb
onus onu GENERIC-NOKIA root interfaces interface ENET_LAN2 type ethernetCsmacd
onus onu GENERIC-NOKIA root interfaces interface ENET_LAN2 enabled false
onus onu GENERIC-NOKIA root interfaces interface ENET_LAN2 port-layer-if UNI_LAN2
onus onu GENERIC-NOKIA root interfaces interface ENET_LAN2 ethernet auto-negotiation status enabled
onus onu GENERIC-NOKIA root interfaces interface ENET_LAN2 ethernet auto-negotiation duplex full
onus onu GENERIC-NOKIA root interfaces interface ENET_LAN2 ethernet auto-negotiation speed eth-if-speed-1gb
onus onu GENERIC-NOKIA root interfaces interface ENET_LAN3 type ethernetCsmacd
onus onu GENERIC-NOKIA root interfaces interface ENET_LAN3 enabled false
onus onu GENERIC-NOKIA root interfaces interface ENET_LAN3 port-layer-if UNI_LAN3
onus onu GENERIC-NOKIA root interfaces interface ENET_LAN3 ethernet auto-negotiation status enabled
onus onu GENERIC-NOKIA root interfaces interface ENET_LAN3 ethernet auto-negotiation duplex full
onus onu GENERIC-NOKIA root interfaces interface ENET_LAN3 ethernet auto-negotiation speed eth-if-speed-1gb
onus onu GENERIC-NOKIA root interfaces interface ENET_LAN4 type ethernetCsmacd
onus onu GENERIC-NOKIA root interfaces interface ENET_LAN4 enabled false
onus onu GENERIC-NOKIA root interfaces interface ENET_LAN4 port-layer-if UNI_LAN4
onus onu GENERIC-NOKIA root interfaces interface ENET_LAN4 ethernet auto-negotiation status enabled
onus onu GENERIC-NOKIA root interfaces interface ENET_LAN4 ethernet auto-negotiation duplex full
onus onu GENERIC-NOKIA root interfaces interface ENET_LAN4 ethernet auto-negotiation speed eth-if-speed-1gb
onus onu GENERIC-NOKIA root interfaces interface ENET_VEIP type onu-v-vrefpoint
onus onu GENERIC-NOKIA root interfaces interface ENET_VEIP enabled false
onus onu GENERIC-NOKIA root interfaces interface ENET_VEIP port-layer-if UNI_VEIP
onus onu GENERIC-NOKIA root interfaces interface ENET_VEIP onu-v-vrefpoint related-onu ANI
onus onu GENERIC-NOKIA root interfaces interface POTS_TEL1 type voiceFXS
onus onu GENERIC-NOKIA root interfaces interface POTS_TEL1 enabled false
onus onu GENERIC-NOKIA root interfaces interface POTS_TEL1 port-layer-if UNI_TEL1
onus onu GENERIC-NOKIA root interfaces interface ANI type ani
onus onu GENERIC-NOKIA root interfaces interface ANI port-layer-if ANIPORT
onus onu GENERIC-NOKIA root interfaces interface ANI performance pm-counter-size 32bit-performance-monitoring
onus onu GENERIC-NOKIA root interfaces interface ANI ani multicast-gemport ANI_2046 mc-gemport-id 2046
onus onu GENERIC-NOKIA root interfaces interface ANI ani multicast-gemport ANI_2046 is-broadcast true
onus onu GENERIC-NOKIA root interfaces interface VSI_VEIP_HSI type vlan-sub-interface
onus onu GENERIC-NOKIA root interfaces interface VSI_VEIP_HSI ingress-qos-policy-profile Q_HSI_TC0
onus onu GENERIC-NOKIA root interfaces interface VSI_VEIP_HSI subif-lower-layer interface ENET_VEIP
onus onu GENERIC-NOKIA root interfaces interface VSI_VEIP_HSI inline-frame-processing ingress-rule rule single-tagged priority 100
onus onu GENERIC-NOKIA root interfaces interface VSI_VEIP_HSI inline-frame-processing ingress-rule rule single-tagged flexible-match match-criteria tag 0 dot1q-tag tag-type c-vlan
onus onu GENERIC-NOKIA root interfaces interface VSI_VEIP_HSI inline-frame-processing ingress-rule rule single-tagged flexible-match match-criteria tag 0 dot1q-tag vlan-id 10
onus onu GENERIC-NOKIA root interfaces interface VSI_VEIP_HSI inline-frame-processing ingress-rule rule single-tagged flexible-match match-criteria tag 0 dot1q-tag pbit any
onus onu GENERIC-NOKIA root interfaces interface VSI_VEIP_HSI inline-frame-processing ingress-rule rule single-tagged flexible-match match-criteria tag 0 dot1q-tag dei any
onus onu GENERIC-NOKIA root interfaces interface VSI_VEIP_HSI inline-frame-processing ingress-rule rule single-tagged ingress-rewrite pop-tags 1
onus onu GENERIC-NOKIA root interfaces interface VSI_VEIP_HSI inline-frame-processing ingress-rule rule single-tagged ingress-rewrite push-tag 0 dot1q-tag tag-type c-vlan
onus onu GENERIC-NOKIA root interfaces interface VSI_VEIP_HSI inline-frame-processing ingress-rule rule single-tagged ingress-rewrite push-tag 0 dot1q-tag vlan-id 10
onus onu GENERIC-NOKIA root interfaces interface VSI_VEIP_HSI inline-frame-processing ingress-rule rule single-tagged ingress-rewrite push-tag 0 dot1q-tag pbit-marking-index 0
onus onu GENERIC-NOKIA root interfaces interface VSI_VEIP_HSI inline-frame-processing ingress-rule rule single-tagged ingress-rewrite push-tag 0 dot1q-tag dei-from-tag-index 0
onus onu GENERIC-NOKIA root interfaces interface VSI_VEIP_HSI inline-frame-processing ingress-rule rule single-tagged auto-instantiate false
onus onu GENERIC-NOKIA root interfaces interface VSI_VEIP_HSI auto-instantiate false
onus onu GENERIC-NOKIA root routing control-plane-protocols control-plane-protocol static default-route static-routes ipv4 route 0.0.0.0/0 next-hop next-hop-address 0.0.0.1
onus onu GENERIC-NOKIA root system dns-resolver server pridns udp-and-tcp address 0.0.0.0
onus onu GENERIC-NOKIA root system dns-resolver server backupdns udp-and-tcp address 0.0.0.0
onus onu GENERIC-NOKIA root ptp-ccsa-profiles ptp-ccsa-port-profile default domain 0
onus onu GENERIC-NOKIA root ptp-ccsa-profiles ptp-ccsa-port-profile default master-only true
onus onu GENERIC-NOKIA root ptp-ccsa-profiles ptp-ccsa-port-profile default dest-mac-addr-forwardable forwardable
onus onu GENERIC-NOKIA root ptp-ccsa-profiles ptp-ccsa-port-profile default log-anno-interval -3
onus onu GENERIC-NOKIA root ptp-ccsa-profiles ptp-ccsa-port-profile default log-sync-interval -4
onus onu GENERIC-NOKIA root ptp-ccsa-profiles ptp-ccsa-port-profile default log-delay-interval 0
onus onu GENERIC-NOKIA root ptp-ccsa-profiles ptp-ccsa-port-profile default step-mode one-step
onus onu GENERIC-NOKIA root ptp-g8275dot1-profiles ptp-g8275dot1-port-profile default domain 24
onus onu GENERIC-NOKIA root ptp-g8275dot1-profiles ptp-g8275dot1-port-profile default master-only true
onus onu GENERIC-NOKIA root ptp-g8275dot1-profiles ptp-g8275dot1-port-profile default dest-mac-addr-forwardable forwardable
onus onu GENERIC-NOKIA root ptp-g8275dot1-profiles ptp-g8275dot1-port-profile default log-anno-interval -3
onus onu GENERIC-NOKIA root ptp-g8275dot1-profiles ptp-g8275dot1-port-profile default log-sync-interval -4
onus onu GENERIC-NOKIA root ptp-g8275dot1-profiles ptp-g8275dot1-port-profile default log-delay-interval -4
onus onu GENERIC-NOKIA root ptp-g8275dot1-profiles ptp-g8275dot1-port-profile default step-mode one-step
exit
interfaces interface ONT-01 type v-ani
enabled true
performance enable false
v-ani onu-id 0
v-ani channel-partition LT1_PON1_CPART_GPON
v-ani expected-serial-number ALCL00000002
v-ani preferred-channel-pair LT1_PON1_CPAIR_GPON
v-ani upstream-fec true
v-ani management-gemport-aes-indicator false
v-ani tod-enable false
v-ani onu-name ONT-01
exit
interfaces interface LT1_PON1_CPART_GPON
tm-root scheduler-node ONT-01 scheduling-level 1 
exit
tm-root scheduler-node ONT-01 child-scheduler-nodes ONT-01_VEIP priority 0 weight 1
exit
tm-root scheduler-node ONT-01_VEIP scheduling-level 2 contains-queues true
exit
tm-root scheduler-node ONT-01_VEIP queue local-queue-id 0 priority 0 weight 1
exit
tm-root child-scheduler-nodes ONT-01 priority 0 weight 1
exit
tm-root tc-id-2-queue-id-mapping-profile-name DEFAULT_TC_TO_8Queues
exit
subscriber-profiles subscriber-profile test
circuit-id 1
remote-id 1
subscriber-id 1
exit
interfaces interface VENET_ONT-01_VEIP type olt-v-enet
enabled true
mac-learning max-number-mac-addresses 4
egress-tm-objects root-if-name LT1_PON1_CPART_GPON scheduler-node-name ONT-01_VEIP 
olt-v-enet lower-layer-interface ONT-01 protocol-identifier-helper slot-id 14 port-id 1
exit
onus onu ONT-01 
usage node-from-template-usage
template-parameters template-ref GENERIC-NOKIA
template-parameters interfaces interface template-ref ANI
template-parameters hardware-config hardware template-ref SFP
tca-monitoring-enabled false
exit
template-parameters hardware-config hardware template-ref CHASSIS admin-state unlocked
exit
exit
forwarding mac-learning-control-profiles mac-learning-control-profile mlcp1
mac-learning-rule user-port
mac-can-not-move-to [ user-port subtended-node-port ]
exit
mac-learning-rule subtended-node-port
mac-can-not-move-to [ user-port subtended-node-port ]
exit
exit
forwarding forwarding-databases forwarding-database FWD_DB_HSI
max-number-mac-addresses 4294967295
aging-timer 300
mac-learning-control mac-learning-control-profile mlcp1
mac-learning-control generate-mac-learning-alarm true
exit
forwarding split-horizon-profiles split-horizon-profile spl1
split-horizon user-port
out-interface-usage [ user-port subtended-node-port ]
exit
split-horizon subtended-node-port
out-interface-usage [ user-port subtended-node-port ]
exit
exit
forwarding flooding-policies-profiles flooding-policies-profile drop_all
flooding-policy dn_drop
in-interface-usages interface-usages [ network-port ]
destination-address any-frame
out-interface-usages interface-usages [ subtended-node-port ]
exit
flooding-policy up_drop
in-interface-usages interface-usages [ user-port ]
destination-address any-multicast-mac-address
discard
exit
exit
frame-processing-profiles frame-processing-profile CC-SINGLE-VLAN-PROFILE
priority 100
match-criteria tag 0
tag-type c-vlan
vlan-id parameter-vlan-id
pbit any
dei any
exit
ingress-rewrite pop-tags 1
ingress-rewrite copy-from-tags-to-marking-list 0
pbit-marking-index 0
dei-marking-index 0
exit
egress-rewrite push-tag 0
tag-type c-vlan
vlan-id vlan-id-from-match
pbit-marking-index 0
dei-marking-index 0
exit
exit
frame-processing-profiles frame-processing-profile Single_Tagged_PBIT_Marking_Done
priority 100
match-criteria tag 0
tag-type c-vlan
vlan-id parameter-vlan-id
pbit any
dei any
exit
ingress-rewrite pop-tags 1
egress-rewrite push-tag 0
tag-type c-vlan
vlan-id vlan-id-from-match
pbit-marking-index 0
dei-marking-index 0
exit
exit
interfaces interface NTW_VSI_HSI
type vlan-sub-interface
enabled
interface-usage interface-usage network-port
mac-learning mac-learning-enable true    
subif-lower-layer interface BP_Eth
frame-processing-profile-ref CC-SINGLE-VLAN-PROFILE
tag-0 vlan-id 100
exit
forwarding forwarders forwarder FWD_HSI 
ports port NTW_PORT_HSI sub-interface NTW_VSI_HSI
flooding-policies flooding-policies-profile drop_all
mac-learning forwarding-database FWD_DB_HSI
split-horizon-profiles split-horizon-profile spl1
l2-dhcpv4-relay downstream-broadcast-flooding false
arp-security downstream-arp-broadcast secured-with-fallback-to-layer2
ND-security downstream-ns-multicast secured-forwarding
exit
l2-dhcpv4-relay-profiles l2-dhcpv4-relay-profile DHCP_Default
max-packet-size 1500
option82-format suboptions [ circuit-id remote-id ]
option82-format default-circuit-id-syntax Access_Node_ID:Chassis:Port:OnuID:v-ani:olt-v-enet
option82-format start-numbering-from-zero false
option82-format use-leading-zeroes false
exit
dhcpv6-ldra-profiles dhcpv6-ldra-profile DHCPv6_Default
options option [ interface-id remote-id vendor-specific-information ]
options default-interface-id-syntax Access_Node_ID:Chassis:Port:OnuID:v-ani:olt-v-enet
options default-remote-id-syntax pon-id
options start-numbering-from-zero false
options use-leading-zeroes false
options xpon-access-loop-characteristics [ xpon-tree-maximum-data-rate-upstream onu-maximum-data-rate-upstream xpon-tree-maximum-data-rate-downstream onu-peak-data-rate-downstream ]
exit
pppoe-profiles pppoe-profile PPPoE_Default
pppoe-vendor-specific-tag subtag [ circuit-id remote-id ]
pppoe-vendor-specific-tag default-remote-id-syntax Access_Node_ID:Chassis:Port:OnuID:v-ani:olt-v-enet
pppoe-vendor-specific-tag start-numbering-from-zero false
pppoe-vendor-specific-tag use-leading-zeroes false
exit
vsi-vector-profiles vsi-vector-profile default
ipv4-security prevent-ipv4-address-spoofing true
ipv4-security learn-addresses-from-dhcp
ipv4-security max-address no-limit
l2-dhcpv4-relay enable true
l2-dhcpv4-relay trusted-port false
l2-dhcpv4-relay profile-ref DHCP_Default
dhcpv6-ldra enable true
dhcpv6-ldra trusted-port true
dhcpv6-ldra profile-ref DHCPv6_Default
pppoe enable true
pppoe profile-ref PPPoE_Default
interface-usage interface-usage user-port
exit
xpongemtcont traffic-descriptor-profiles traffic-descriptor-profile 100M_UP
fixed-bandwidth 0
assured-bandwidth 0
maximum-bandwidth 100000000
jitter-tolerance 16
exit
classifiers classifier-entry pbit0_to_TC0
filter-operation match-all-filter
match-criteria pbit-marking-list 0
pbit-value 0
exit
classifier-action-entry-cfg scheduling-traffic-class
scheduling-traffic-class 0
exit
exit
classifiers classifier-entry pbit1_to_TC0
filter-operation match-all-filter
match-criteria pbit-marking-list 0
pbit-value 1
exit
classifier-action-entry-cfg scheduling-traffic-class
scheduling-traffic-class 0
exit
exit
classifiers classifier-entry pbit2_to_TC0
filter-operation match-all-filter
match-criteria pbit-marking-list 0
pbit-value 2
exit
classifier-action-entry-cfg scheduling-traffic-class
scheduling-traffic-class 0
exit
exit
classifiers classifier-entry pbit3_to_TC0
filter-operation match-all-filter
match-criteria pbit-marking-list 0
pbit-value 3
exit
classifier-action-entry-cfg scheduling-traffic-class
scheduling-traffic-class 0
exit
exit
classifiers classifier-entry pbit4_to_TC0
filter-operation match-all-filter
match-criteria pbit-marking-list 0
pbit-value 4
exit
classifier-action-entry-cfg scheduling-traffic-class
scheduling-traffic-class 0
exit
exit
classifiers classifier-entry pbit5_to_TC0
filter-operation match-all-filter
match-criteria pbit-marking-list 0
pbit-value 5
exit
classifier-action-entry-cfg scheduling-traffic-class
scheduling-traffic-class 0
exit
exit
classifiers classifier-entry pbit6_to_TC0
filter-operation match-all-filter
match-criteria pbit-marking-list 0
pbit-value 6
exit
classifier-action-entry-cfg scheduling-traffic-class
scheduling-traffic-class 0
exit
exit
classifiers classifier-entry pbit7_to_TC0
filter-operation match-all-filter
match-criteria pbit-marking-list 0
pbit-value 7
exit
classifier-action-entry-cfg scheduling-traffic-class
scheduling-traffic-class 0
exit
exit
classifiers classifier-entry untag_pbit_hsi_tc0
filter-operation match-all-filter
vlans untagged
classifier-action-entry-cfg pbit-marking
pbit-marking-cfg pbit-marking-list 0
pbit-value 0
exit
exit
exit
classifiers classifier-entry copy_tag_pbit0
filter-operation match-all-filter
match-criteria tag 0
in-pbit-list 0
exit
dscp-range any
any-protocol
exit
classifier-action-entry-cfg pbit-marking
pbit-marking-cfg pbit-marking-list 0
pbit-value 0
exit
exit
exit
classifiers classifier-entry copy_tag_pbit1
filter-operation match-all-filter
match-criteria
tag 0
in-pbit-list 1
exit
dscp-range any
any-protocol
exit
classifier-action-entry-cfg pbit-marking
pbit-marking-cfg pbit-marking-list 0
pbit-value 1
exit
exit
exit
classifiers classifier-entry copy_tag_pbit2
filter-operation match-all-filter
match-criteria
tag 0
in-pbit-list 2
exit
dscp-range any
any-protocol
exit
classifier-action-entry-cfg pbit-marking
pbit-marking-cfg pbit-marking-list 0
pbit-value 2
exit
exit
exit
classifiers classifier-entry copy_tag_pbit3
filter-operation match-all-filter
match-criteria
tag 0
in-pbit-list 3
exit
dscp-range any
any-protocol
exit
classifier-action-entry-cfg pbit-marking
pbit-marking-cfg pbit-marking-list 0
pbit-value 3
exit
exit
exit
classifiers classifier-entry copy_tag_pbit4
filter-operation match-all-filter
match-criteria
tag 0
in-pbit-list 4
exit
dscp-range any
any-protocol
exit
classifier-action-entry-cfg pbit-marking
pbit-marking-cfg pbit-marking-list 0
pbit-value 4
exit
exit
exit
classifiers classifier-entry copy_tag_pbit5
filter-operation match-all-filter
match-criteria
tag 0
in-pbit-list 5
exit
dscp-range any
any-protocol
exit
classifier-action-entry-cfg pbit-marking
pbit-marking-cfg pbit-marking-list 0
pbit-value 5
exit
exit
exit
classifiers classifier-entry copy_tag_pbit6
filter-operation match-all-filter
match-criteria
tag 0
in-pbit-list 6
exit
dscp-range any
any-protocol
exit
classifier-action-entry-cfg pbit-marking
pbit-marking-cfg pbit-marking-list 0
pbit-value 6
exit
exit
exit
classifiers classifier-entry copy_tag_pbit7
filter-operation match-all-filter
match-criteria
tag 0
in-pbit-list 7
exit
dscp-range any
any-protocol
exit
classifier-action-entry-cfg pbit-marking
pbit-marking-cfg pbit-marking-list 0
pbit-value 7
exit
exit
exit
policies policy pbit0-7_to_TC0
classifiers pbit0_to_TC0
exit
classifiers pbit1_to_TC0
exit
classifiers pbit2_to_TC0
exit
classifiers pbit3_to_TC0
exit
classifiers pbit4_to_TC0
exit
classifiers pbit5_to_TC0
exit
classifiers pbit6_to_TC0
exit
classifiers pbit7_to_TC0
exit
exit
policies policy untag_tag_pbit_hsi_tc0
classifiers untag_pbit_hsi_tc0
exit
classifiers copy_tag_pbit0
exit
classifiers copy_tag_pbit1
exit
classifiers copy_tag_pbit2
exit
classifiers copy_tag_pbit3
exit
classifiers copy_tag_pbit4
exit
classifiers copy_tag_pbit5
exit
classifiers copy_tag_pbit6
exit
classifiers copy_tag_pbit7
exit
exit
qos-policy-profiles policy-profile DS_HSI_TC0
policy-list pbit0-7_to_TC0
exit
qos-policy-profiles policy-profile US_HSI_TC0
policy-list untag_tag_pbit_hsi_tc0
exit
xpongemtcont tconts tcont TCONT_ONT-01_VEIP_HSI
alloc-id 256
interface-reference ONT-01
traffic-descriptor-profile-ref 100M_UP
exit
interfaces interface VSI_ONT-01_VEIP_HSI
type vlan-sub-interface
enabled true
performance enable false
mac-learning max-number-mac-addresses 4
mac-learning mac-learning-enable true
ingress-qos-policy-profile US_HSI_TC0
egress-qos-policy-profile DS_HSI_TC0
subif-lower-layer interface VENET_ONT-01_VEIP
frame-processing-profile-ref Single_Tagged_PBIT_Marking_Done
tag-0 vlan-id 10
subscriber-profile profile test
vector-profile default
exit
xpongemtcont gemports gemport GEM0_ONT-01_VEIP_HSI
gemport-id 256
interface VSI_ONT-01_VEIP_HSI
traffic-class 0
downstream-aes-indicator false
upstream-aes-indicator false
exit
forwarding forwarders forwarder FWD_HSI
forwarding forwarders forwarder FWD_HSI ports port USR_PORT_ONT-01_VEIP_HSI sub-interface VSI_ONT-01_VEIP_HSI
exit
onus onu ONT-01
template-parameters tconts tcont template-ref TCONT_VEIP_HSI id 256
exit
template-parameters gemports gemport template-ref GEM0_VEIP_HSI id 256
template-parameters interfaces interface template-ref ENET_VEIP admin true
template-parameters interfaces interface template-ref VSI_VEIP_HSI pm-enable false vsi ingress-rule single-tagged match-criteria-tag-0-vlan-id 10 ingress-rewrite-tag-0-vlan-id 10
exit
template-parameters interfaces interface template-ref VSI_VEIP_HSI vsi ingress-qos-policy-profile Q_HSI_TC0
commit
```

El `commit` puede tardar un momento mientras se validan y aplican todos los objetos. Cuando termine, sal del modo de configuración y vuelve al contexto **Shelf**. Desde allí, abre el IHUB y crea la v-VPLS de la VLAN del abonado:

```text title="Comandos en el IHUB"
forward cli to ihub
configure global
service vpls 10
admin-state enable
service-name "10"
service-id 10
customer 1
admin-state enable
storm-control false
user-user-com false
v-vpls true
vlan 10
sap 1/2/1:10 admin-state enable
exit
mac-move allow-res-res false
mac-move allow-res-reg true
mac-move allow-reg-res false
commit
```
