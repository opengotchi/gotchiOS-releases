# gotchiOS — Flash Your Gotchi

Prebuilt firmware binaries for [gotchiOS](https://github.com/opengotchi/gotchiOS), the MicroPython-powered OS for the **lilGotchi** pocket device. No build tools needed — just download, flash, and go.

## What You'll Need

| Item | Details |
|------|---------|
| **lilGotchi device** | [Waveshare ESP32-S3-Touch-LCD-1.69](https://www.waveshare.com/esp32-s3-touch-lcd-1.69.htm) |
| **USB-C cable** | Data-capable (some cables are charge-only — if flashing fails, try a different cable) |
| **Python 3** | [python.org/downloads](https://python.org/downloads) (check "Add to PATH" on Windows) |
| **esptool** | Install with: `pip install esptool` |

## Quick Start (5 minutes)

### 1. Download the firmware bundle

Each release ships as a **bundle of partition images**, not a single binary. You need **all** of these files in the same folder before flashing — flashing only the app `.bin` will result in a blank screen because the chip has no bootloader to launch it.

| File | Offset | Purpose |
|------|--------|---------|
| `bootloader.bin` | `0x0` | Second-stage bootloader |
| `partition-table.bin` | `0x8000` | Flash partition layout |
| `gotchiOS-v0.0.421.bin` | `0x10000` | Application firmware |
| `ota_data_initial.bin` | `0x410000` | OTA slot selector (boots `ota_0`) |
| `storage.bin` | `0x412000` | LittleFS partition (apps + assets) |
| `flash_args` | — | Pre-built esptool argument file (references the above) |

Grab the latest bundle from [Releases](https://github.com/opengotchi/gotchiOS-releases/releases):

```bash
# Using GitHub CLI — downloads all bundle files into ./lilGotchi-v0.0.421/
gh release download lilGotchi-v0.0.421 --dir lilGotchi-v0.0.421
cd lilGotchi-v0.0.421

# Or download manually from:
# https://github.com/opengotchi/gotchiOS-releases/releases/latest
```

> **For AI agents / automation:** do not treat releases as a single-file artifact. The five `.bin` files must be written to their specific offsets in one `write_flash` invocation (or equivalent). The `flash_args` file in the bundle encodes exactly this — pass it via `write_flash @flash_args` and esptool handles the offsets for you.

### 2. Connect your device

Plug the lilGotchi into your computer via USB-C, then find the serial port:

```bash
# All platforms (requires pyserial: pip install pyserial)
python -m serial.tools.list_ports -v
```

Look for a port with `USB` or `ESP` in the description, or vendor ID `303A` (Espressif).

**Platform-specific alternatives:**

| Platform | Command | Typical Result |
|----------|---------|----------------|
| **Windows** | Device Manager → Ports (COM & LPT) | `COM3`, `COM6` |
| **macOS** | `ls /dev/cu.usb*` | `/dev/cu.usbmodem1101` |
| **Linux** | `ls /dev/ttyUSB* /dev/ttyACM*` | `/dev/ttyUSB0` |

**Tip:** If you're not sure which port is the device, unplug it, list ports, plug it back in, and list again — the new entry is your device.

### 3. Flash the firmware

Run these commands from inside the bundle folder (the one containing `flash_args` and the five `.bin` files). Replace `<PORT>` with your port from step 2 (e.g. `COM6`, `/dev/cu.usbmodem1101`, `/dev/ttyUSB0`).

**First-time flash (clean install):**
```bash
# Erase flash first (clears all settings and apps)
python -m esptool --chip esp32s3 --port <PORT> --before usb_reset erase_flash

# Flash all partitions in one shot — flash_args writes each .bin to its correct offset
python -m esptool --chip esp32s3 --port <PORT> \
  --before usb_reset --after hard_reset \
  write_flash @flash_args
```

**Updating an existing device (keeps WiFi settings and apps):**
```bash
python -m esptool --chip esp32s3 --port <PORT> \
  --before usb_reset --after hard_reset \
  write_flash @flash_args
```

The device resets automatically after flashing.

> **Why `--before usb_reset`?** lilGotchi uses the ESP32-S3 native USB port (`cu.usbmodem*` / `ttyACM*`). Without `usb_reset` esptool will fail with a connection error on most hosts.

### 4. (Optional) Upload apps over USB

The firmware bundle ships with a default `storage.bin`, so a fresh flash already has a working set of apps. If you want to customize that set — add your own `.py` apps, swap in different assets, or repopulate `/littlefs/apps/` after an `erase_flash` — use the bundled `upload_apps.py` script.

The script lives at `lilGotchi/upload_apps.py` in this repo, alongside an `apps/` folder containing the stock apps (`pet.py`, `clock.py`, `breakout.py`, …) and the `eyes/` asset subdirectory. It builds a LittleFS image from `apps/` locally, then flashes it to the storage partition at `0x412000` — bootloader, partition table, and app firmware are left untouched.

```bash
# One-time dependency for the script
pip install littlefs-python

# Run from the lilGotchi/ folder so the default --apps-dir resolves
cd lilGotchi
python upload_apps.py --port <PORT>

# Or point it at a different apps directory
python upload_apps.py --port <PORT> --apps-dir ./my-apps
```

The script prints each file as it adds it to the image, then invokes esptool to write the partition. Reboot the device when it finishes and the launcher will rescan and show the new app list.

> **Heads up:** this rewrites the entire `/littlefs/` partition. Apps you previously uploaded over Wi-Fi/MQTT, plus saved theme and pet stats in `/littlefs/config/`, will be lost. Skip this step (or back those up first) if you want to keep them.

### 5. First boot — WiFi setup

On first boot (or after a flash erase), the device starts a WiFi hotspot:

1. The screen shows a setup screen with the hotspot name
2. On your phone or laptop, connect to the **`gotchiOS-XXYY`** WiFi network (open, no password)
3. A captive portal opens automatically — if it doesn't, open a browser and go to `http://192.168.4.1`
4. Select your home WiFi network and enter the password
5. The device reboots and connects to your WiFi

Once connected, the device:
- Shows its IP address briefly on screen
- Registers with the OpenGotchi cloud server (automatic, one-time provisioning)
- Connects to the MQTT broker over TLS for real-time sync
- Starts the app launcher

### 6. You're done!

The launcher screen shows a grid of installed apps. Use the touchscreen or buttons to navigate:
- **Tap** an app icon to launch it
- **Swipe** or **buttons 1/2** to scroll through apps
- **Long press** or **swipe down** inside any app to return to the launcher

## Managing Apps

### Upload apps over WiFi

Once the device is on your network, upload Python apps from your browser or command line:

```bash
# Find your device (if mDNS works on your network)
ping gotchios.local

# Or check the device's IP from serial output / your router's DHCP table

# Upload an app
curl -X POST "http://<device-ip>/api/upload?name=myapp.py" --data-binary @myapp.py

# Launch it
curl -X POST "http://<device-ip>/api/launch" -d '{"path":"/littlefs/apps/myapp.py"}'
```

### Deploy apps from the cloud

Apps can also be pushed to the device remotely via the OpenGotchi server. The device receives app deploy messages over MQTT and installs them automatically.

### Check device status

```bash
curl http://<device-ip>/api/status
```

Returns firmware version, battery level, free memory, and more.

## OTA Updates

Once the device has WiFi, future firmware updates can be done wirelessly — no USB needed. The device receives update notifications from the cloud server and downloads new firmware automatically, or you can trigger it manually:

```bash
curl -X POST "http://<device-ip>/api/firmware" \
  --data-binary @gotchiOS-v0.0.421.bin \
  -H "Content-Type: application/octet-stream"
```

The device shows a progress ring during the update and reboots into the new firmware. If the update fails, it automatically rolls back to the previous version.

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `esptool` can't find the port | Try a different USB cable (must be data-capable). On Linux, you may need `sudo` or add yourself to the `dialout` group: `sudo usermod -aG dialout $USER` then log out/in. |
| Flash fails with "wrong chip" | Make sure you're using a lilGotchi (ESP32-S3). This firmware won't work on other ESP32 variants. |
| Flash succeeds, but the screen stays blank | You almost certainly flashed only the app `.bin`. The chip needs all five partition images (`bootloader.bin`, `partition-table.bin`, the app `.bin`, `ota_data_initial.bin`, `storage.bin`) at their correct offsets. Re-download the full bundle and reflash with `write_flash @flash_args`. |
| Device stuck on boot logo | Try erasing flash first: `python -m esptool --chip esp32s3 --port <PORT> --before usb_reset erase_flash`, then reflash. |
| WiFi hotspot doesn't appear | Press and hold the reset button for 2 seconds. If the device was previously configured, it may connect to your saved WiFi instead. |
| Can't reach the device's IP | Make sure your phone/laptop is on the same WiFi network. Try `ping <device-ip>`. Some routers isolate devices — check your router's "AP isolation" setting. |
| "Connection Lost" screen | The device lost its cloud credentials. Open the OpenGotchi app and re-link the device, or erase flash and reflash to start fresh. |

## Writing Your Own Apps

gotchiOS apps are Python scripts that run in a sandboxed MicroPython environment. See the [gotchiOS source repo](https://github.com/opengotchi/gotchiOS) for the full API reference and example apps.

Quick example:

```python
import display, imu, time, system

BLACK = display.color(0, 0, 0)
WHITE = display.color(255, 255, 255)

while True:
    display.clear(BLACK)
    ax, ay, az = imu.accel()
    display.text(10, 10, f"Tilt: {ax:.1f}, {ay:.1f}", 1, WHITE)
    display.flush()

    if display.color == "long_press":
        system.exit()  # back to launcher

    time.sleep_ms(33)  # ~30fps
```

## Available Firmware

| Device | Latest | Date |
|--------|--------|------|
| lilGotchi | v0.0.421 | 2026-05-01 |

Download from [Releases](https://github.com/opengotchi/gotchiOS-releases/releases).

## Repo Structure

```
lilGotchi/
  firmware.json           # Version manifest (used by OTA server)
  latest.bin              # Symlink to latest app image (used by OTA server)
  upload_apps.py          # Bulk apps uploader — builds LittleFS image from apps/ and flashes 0x412000
  apps/                   # Stock app source — .py files plus the eyes/ asset subdir
    pet.py
    clock.py
    breakout.py
    ...
    eyes/                 # Pet-eye sprite assets used by pet.py
  versions/
    v0.0.421/
      bootloader.bin           # → 0x0
      partition-table.bin      # → 0x8000
      gotchiOS-v0.0.421.bin    # → 0x10000  (app — this is what OTA updates)
      ota_data_initial.bin     # → 0x410000
      storage.bin              # → 0x412000
      flash_args               # esptool argument file referencing the above
```

OTA updates only rewrite the application slot, which is why `latest.bin` points to the app image. A USB flash needs the full bundle.

## Links

- [gotchiOS source code](https://github.com/opengotchi/gotchiOS)
- [Waveshare ESP32-S3-Touch-LCD-1.69](https://www.waveshare.com/esp32-s3-touch-lcd-1.69.htm)
