---
sidebar_position: 3
---

# Customizing ONU DHCP

`src/daemons/onu_dhcp.py` is what makes ONUs "exist" to your BNG: for each
discovered subscriber it creates a macvlan interface with the ONU's MAC and
runs the real DHCP exchange (DORA for v4, SARR for v6) out of the OLT's
uplink. From the BNG's point of view it looks exactly like an IPoE
subscriber.

## How it discovers subscribers

The daemon polls the LT plane's running config (every 20 s by default)
looking for **vlan-sub-interfaces** — the `l2-user` created by Altiplano's
VLAN service. Creating the ONT alone does not trigger DHCP: the L2 service
on top of the UNI is required, with a `frame-processing-profile` that
resolves to an outer VLAN. With that, the daemon resolves the wiring
against the IHUB's v-VPLS and starts the client.

## Testing without touching anything

Dry-run mode shows what would be discovered and which interface it would
use, without creating any interface or sending packets:

```bash
PYTHONPATH=src/daemons python3 src/daemons/onu_dhcp.py --dry-run --once
```

It's the first diagnostic tool when "no DHCP is going out": in one shot it
tells you whether the VSI exists, which VLAN it resolved, and which uplink
it would use. Keep in mind that outside dry-run the daemon creates and
deletes network interfaces: run it inside the container or a lab network
namespace.

## Environment knobs

| Variable | Effect |
|---|---|
| `ONU_DHCP_POLL` | Reconciliation interval in seconds (default 20). |
| `ONU_DHCP_UPLINK` | Egress interface when the wire can't be derived from the IHUB (default `eth1`). |

Set them on the OLT node of your containerlab or compose YAML, next to
`OLT_LT_SLOTS`.

## Working loop

```bash
# edit src/daemons/onu_dhcp.py
./build.sh check && ./build.sh
# redeploy and watch the daemon logs
docker logs -f <olt> 2>&1 | grep onu-dhcp
```

A healthy log sequence is: `uplink map`, then `mac=... wire=...` per
subscriber, `macvlan suXXXXXXXX over ...`, and finally
`DHCPv4 ACK <ip> (server ..., lease ...)`. If you see the `wire=` line but
never the ACK, the DISCOVER is going out and the problem is on the BNG
side.
