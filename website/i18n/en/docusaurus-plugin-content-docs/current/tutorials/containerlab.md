---
sidebar_position: 2
title: Containerlab
description: Deploy Light OLT and a Nokia SR OS BNG in a Containerlab lab.
---

# Deploy Light OLT with Containerlab

In this tutorial, you will prepare a lab with Light OLT connected to a Nokia SR OS BNG. The NETCONF proxy is optional and is only required when integrating the OLT with Nokia Altiplano.

## 1. Requirements

- Docker.
- Python 3.10 or newer.
- Containerlab.
- A Nokia SR-SIM image and license if you will use the example BNG.

## 2. Pull the base images

Pull the OLT image:

```bash
docker pull ghcr.io/abelperezr/olt-ls:0.0.1
```

If you will use Nokia Altiplano, also pull the NETCONF proxy:

```bash
docker pull ghcr.io/abelperezr/olt-proxy:0.0.1
```

## 3. Clone the repository

```bash
git clone https://github.com/abelperezr/olt-light.git
cd olt-light
```

## 4. Prepare the lab directory

Create the lab structure and copy the ONT inventories:

```bash
mkdir -p clab/config-bng clab/configs/license
cp -R seeds clab/
```

The repository contains a reference Nokia SR OS BNG configuration under `examples/config-bng/`. Copy it together with the example topology:

```bash
cp examples/config-bng/bng.txt clab/config-bng/
cp examples/lab.clab.yml clab/
```

Copy your SR-SIM license to the path expected by the topology:

```bash
cp <license-path>/SR_SIM_license.txt clab/configs/license/
```

Edit `clab/lab.clab.yml` before deploying it:

1. Replace `<your-registry>/srsim:25.10.r2` with your SR-SIM image name.
2. Change the `olt` node image from `light-olt:dev` to `ghcr.io/abelperezr/olt-ls:0.0.1`.
3. Change both bind mounts from `../seeds/` to `./seeds/`, because this tutorial places the inventories inside `clab/`.
4. If you will not use Nokia Altiplano, remove the entire `olt-proxy` node from the topology.

## 5. Enable OLT persistence (optional)

Create the persistent directory:

```bash
mkdir -p clab/persist/olt/repo
```

Then uncomment this bind mount in the `olt` node of `clab/lab.clab.yml`:

```yaml
- ./persist/olt/repo:/persist/repo
```

If you will use the proxy, also create its data directory to preserve its SSH identity between deployments:

```bash
mkdir -p clab/persist/olt-proxy/data
```

## 6. Deploy the lab

```bash
cd clab
sudo containerlab deploy -t lab.clab.yml
```

## 7. Configure the OLT

- Without Nokia Altiplano, continue with the [eCLI guide](../how-to/cli-guide.md).
- With Nokia Altiplano, continue with [Nokia Altiplano integration](../explanation/altiplano-integration.md).

## 8. Validate authenticated ONTs

Follow the `onu-dhcp` daemon events, replacing the placeholder with the OLT container name:

```bash
docker logs -f <olt-container-name> 2>&1 | grep onu-dhcp
```

For example, if the container is named `olt`:

```bash
docker logs -f olt 2>&1 | grep onu-dhcp
```

When a VSI has an enabled v-VPLS and the BNG grants an address, the log shows the selected uplink with `via=v-vpls` and the `DHCPv4 ACK` or `DHCPv6 REPLY` messages.
