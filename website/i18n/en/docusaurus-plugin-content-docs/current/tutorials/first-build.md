---
sidebar_position: 1
---

# Your first build

This tutorial takes you from zero to a customized image running. No
hardware or licenses needed: the base images are public.

## 1. Requirements

Docker and Python 3.10 or newer. That's it — the images are public, so no
GHCR authentication is required.

## 2. Pull the base images

```bash
docker pull ghcr.io/abelperezr/olt-ls:0.0.1
docker pull ghcr.io/abelperezr/olt-proxy:0.0.1
```

## 3. Clone and verify

```bash
git clone https://github.com/abelperezr/olt-light
cd olt-light
./build.sh check
```

`check` compiles the overlay's Python code and runs the unit tests. As a
guardrail, it also fails if directories that belong to the base images
(`yang`, `device-ext`, `seeds`) show up in the tree — those must never
exist in this repo.

## 4. Build your image

```bash
./build.sh
```

The result is `light-olt:dev`. The build takes seconds: it only copies the
editable layer on top of the base, which already carries everything heavy.
You can change the base and the tag without editing files:

```bash
BASE_IMAGE=ghcr.io/abelperezr/olt-ls:0.0.1 \
IMAGE_TAG=ghcr.io/my-user/my-olt:dev \
./build.sh
```

## 5. Start the example environment

The reference lab uses containerlab: OLT + NETCONF proxy + a Nokia SR OS
BNG (the BNG needs your own image and license; drop that node if you only
want the OLT + proxy pair).

```bash
cd examples
containerlab deploy -t lab.clab.yml
```

Try the eCLI:

```bash
ssh isadmin@172.30.30.10        # isadmin/isadmin
```

And NETCONF straight into a plane:

```bash
ssh -s admin@172.30.30.10 -p 833 netconf    # admin/admin
```

Altiplano points at the **proxy** IP (172.30.30.11 in the example), ports
831 and up. The topology details are in
[Deploying a lab](../how-to/deploy-lab.md).

## 6. Your first change

Edit anything under `src/` (say, the eCLI welcome banner), then repeat:

```bash
./build.sh check && ./build.sh
containerlab deploy -t examples/lab.clab.yml --reconfigure
```

That's the whole loop: edit, verify, rebuild, redeploy.
