# gotchiOS Releases

Public firmware binaries for gotchiOS OTA updates across multiple devices.

Source code: [opengotchi/gotchiOS](https://github.com/opengotchi/gotchiOS) (private)

## Structure

```
<device>/
  firmware.json           <- manifest with all versions + metadata
  latest.bin              <- always points to the latest release
  versions/
    v0.0.69/
      gotchiOS-v0.0.69.bin
    ...
```

## Devices

| Device | Directory | Latest |
|--------|-----------|--------|
| lilGotchi | `lilGotchi/` | v0.0.69 |

## Adding a New Device

1. Create a new directory at the repo root (e.g. `myDevice/`)
2. Add a `firmware.json` manifest, `latest.bin`, and `versions/` folder
3. Create a GitHub release with the binary attached
4. Sync to the server via `POST /api/v1/firmware/sync`
