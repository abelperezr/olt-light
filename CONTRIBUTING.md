# Contributing

Contributions are welcome as long as they stay inside the public
customization boundary — this repo is the editable layer, not the emulator.

## Before opening a pull request

1. Don't add YANG modules, device extensions, seed exports, capability
   allowlists, or anything copied out of the base images. `./build.sh check`
   enforces this.
2. Keep `/usr/local/bin/ecli` compatible with the base image.
3. Don't move the daemon paths — the base image's startup supervisor expects
   them exactly where the Dockerfile puts them.
4. Add or update tests for behavior changes.
5. Update both the Spanish and English docs.

Run the quality gate before pushing:

```bash
./build.sh check
cd website
npm ci
npm run build
```

Keep commits focused, and say in the message what changes for the user,
which plane it touches, and how you verified it.
