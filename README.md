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

## Flashing Firmware

### Prerequisites

- Python 3 with `esptool` installed:
  ```bash
  pip install esptool
  ```
- Your gotchi connected via USB

### Steps

1. **Download the latest release binary**

   From GitHub Releases:
   ```bash
   gh release download v0.0.69 --pattern "*.bin" --dir ./firmware
   ```

   Or grab it directly from the repo:
   ```bash
   # Latest binary for a device
   cp lilGotchi/latest.bin ./gotchiOS.bin
   ```

2. **Find your device's COM/serial port**

   ```bash
   # Windows
   powershell.exe -Command "Get-WMIObject Win32_SerialPort | Select DeviceID, Description"

   # macOS / Linux
   ls /dev/tty.usb* /dev/ttyACM* /dev/ttyUSB* 2>/dev/null
   ```

3. **Erase flash (recommended for clean install)**

   ```bash
   python -m esptool --port <PORT> erase_flash
   ```

4. **Flash the firmware**

   ```bash
   python -m esptool --port <PORT> --baud 460800 write_flash 0x0 gotchiOS.bin
   ```

5. The device will reset automatically and boot into the new firmware.

## Adding a New Device

1. Create a new directory at the repo root (e.g. `myDevice/`)
2. Add a `firmware.json` manifest, `latest.bin`, and `versions/` folder
3. Create a GitHub release with the binary attached
4. Sync to the server via `POST /api/v1/firmware/sync`
