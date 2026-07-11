---
sidebar_position: 2
---

# Customizing the eCLI

The eCLI is the Lightspan-style shell served over SSH on the container's
port 22 (username `admin`, password `admin`). It emulates two
dialects: ConfD J-style for SHELF and LT, and SR OS MD-CLI for the IHUB,
with TAB completion and `?` help.

The code lives in `src/ecli` (the executable) and `src/light_olt/` (the
package with the logic). The image installs it at `/usr/local/bin/ecli`;
that path can't move because the base image's sshd uses it as the login
shell for both users.

## Working loop

```bash
# 1. edit src/ecli or the package modules
# 2. verify and rebuild
./build.sh check && ./build.sh
# 3. try it
docker compose -f examples/docker-compose.yml up -d
ssh -p 2222 admin@localhost
```

For faster iteration, mount your working copy straight over the binary and
just restart the container between tries:

```yaml
# containerlab or compose fragment
binds:
  - ./src/ecli:/usr/local/bin/ecli:ro
```

## What to respect

- The eCLI operates the datastores through `sysrepocfg`/`sysrepoctl` via
  sudo (the base ships a scoped sudoers for exactly that). Don't assume
  direct access to the sysrepo SHM: it belongs to root.
- Completion relies on a schema index the base image generates at build
  time. Without the index, the eCLI falls back to a curated table — your
  code must tolerate both cases.
- Context names (`Board-LT1` through `Board-LT4`, the IHUB/SHELF/LT planes)
  are derived from the inventory the SHELF exposes based on
  `OLT_LT_SLOTS`; don't hardcode them.
