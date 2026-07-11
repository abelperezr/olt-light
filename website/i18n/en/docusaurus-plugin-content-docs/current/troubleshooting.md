---
sidebar_position: 6
---

# Troubleshooting

## The build fails at `check`

Read the first line of the error: it's either a syntax/test failure in your
code (the traceback points at the file), or the restricted-directory
guardrail — remove `yang/`, `device-ext/` or `proxy/cap_allow/` from the tree;
they don't belong in this repo. `seeds/` may contain only the lab's synthetic
ONU operational inventories.

## netopeer2 times out or the planes don't start

Almost always insufficient shared memory. With more than one LT plane the
container needs `shm-size: 2GiB` or more. Check inside the container with
`df -h /dev/shm`.

## An ONU doesn't show up

*Detected* (autofind) ONUs come from the corresponding plane's XML:
`/seeds/onts_oper.xml` for LT1, `/seeds/onts_oper_ltN.xml` for the clones.
Verify the file is mounted at the right plane's path and that the channel
termination names in the XML match that plane (a `CT_LT2_...` in LT1's file
creates a phantom interface, not a visible ONU).

## No DHCP towards the BNG

Creating the ONT isn't enough: the daemon discovers subscribers through the
L2 service (vlan-sub-interface) on top of the UNI. Diagnose with dry-run:

```bash
docker exec <olt> python3 /usr/local/bin/onu_dhcp.py --dry-run --once
```

If it discovers the subscriber but there's never an ACK in the logs,
capture on the uplink and check the BNG — the DISCOVER is already leaving.

## Altiplano doesn't complete onboarding

Confirm the Altiplano device points at the **proxy**, not the OLT directly,
and that the proxy's `/data` volume persists (if the SSH host key changes
between deploys, Altiplano refuses the connection until the fingerprint is
updated).
