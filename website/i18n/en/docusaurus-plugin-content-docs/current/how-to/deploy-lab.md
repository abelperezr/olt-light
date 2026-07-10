---
sidebar_position: 1
---

# Deploying a lab

## With containerlab (recommended)

`examples/lab.clab.yml` brings up the full trio: SR OS BNG, OLT and NETCONF
proxy. The BNG node needs your own SR-SIM image and Nokia license (they are
not redistributable); if you don't have them, delete that node and the
link — the OLT and proxy work on their own.

```bash
cd examples
containerlab deploy -t lab.clab.yml
```

The decisions that matter in the YAML:

- **`shm-size: 4GiB`** on the OLT. Required with more than one LT plane:
  each sysrepo context consumes its own shared memory, and running short
  shows up as netopeer2 RPC timeouts.
- **`OLT_LT_SLOTS`** defines the card inventory per slot, e.g.
  `"1=FGLT-D,2=FWLT-C"`. Slot N listens for NETCONF on port 832+N. It is
  applied at startup; changing the layout is editing the variable and
  redeploying.
- **Per-plane ONU seeds**: `/seeds/onts_oper.xml` feeds LT1's autofind, and
  `/seeds/onts_oper_lt2.xml` through `..._lt4.xml` feed each clone. A clone
  without its own file inherits the global one. Files are reloaded on
  change — you can add or remove ONUs live.
- **The proxy persists its host key in `/data`**: mount a volume so
  Altiplano doesn't see the device's SSH identity change on every redeploy.

Altiplano (device-fx) points at the **proxy** IP, not the OLT: the proxy
rewrites hello and yang-library into the format the plug expects.

## With docker compose (smoke test)

To verify a customization without containerlab there is a minimal compose
file with OLT + proxy:

```bash
docker compose -f examples/docker-compose.yml up -d
docker compose -f examples/docker-compose.yml logs --tail=100 olt
ssh -p 2222 isadmin@localhost
```

You can point it at another image without editing the file:

```bash
OLT_IMAGE=light-olt:test docker compose -f examples/docker-compose.yml up -d
```
