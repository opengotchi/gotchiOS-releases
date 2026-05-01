#!/usr/bin/env python3
"""
gotchiOS — standalone bulk apps uploader.

Builds a LittleFS image from a local apps/ directory and flashes it to the
'storage' partition (offset 0x412000) on a connected ESP32-S3 running gotchiOS.

The device's storage partition must already exist (it does, on any device
flashed with the standard gotchiOS firmware). This tool only rewrites that
partition — it does not touch the bootloader, partition table, or app firmware.

Usage:
    python upload_apps.py --port /dev/cu.usbmodem1101
    python upload_apps.py --port COM5 --apps-dir ./my-apps

Requirements:
    pip install esptool littlefs-python

WARNING: this overwrites every file in /littlefs/ on the device. Apps you
installed over Wi-Fi or MQTT, plus saved theme/pet stats in /littlefs/config/,
will be lost. Back them up first if you care.
"""

import argparse
import os
import subprocess
import sys

PARTITION_OFFSET = 0x412000
PARTITION_SIZE   = 0x3EE000          # ~4 MB, must match partitions.csv
BLOCK_SIZE       = 4096
BLOCK_COUNT      = PARTITION_SIZE // BLOCK_SIZE
EXCLUDE_DIRS     = {"__pycache__", "icons"}


def build_image(apps_dir, out_path):
    from littlefs import LittleFS

    fs = LittleFS(block_size=BLOCK_SIZE, block_count=BLOCK_COUNT)
    fs.mkdir("/apps")
    fs.mkdir("/config")

    count = 0

    for fname in sorted(os.listdir(apps_dir)):
        fpath = os.path.join(apps_dir, fname)
        if os.path.isfile(fpath) and fname.endswith(".py"):
            with open(fpath, "rb") as f:
                data = f.read()
            with fs.open("/apps/" + fname, "wb") as f:
                f.write(data)
            print(f"  + /apps/{fname:<24} ({len(data)} bytes)")
            count += 1

    for sub in sorted(os.listdir(apps_dir)):
        sub_path = os.path.join(apps_dir, sub)
        if not os.path.isdir(sub_path) or sub in EXCLUDE_DIRS:
            continue
        fs.mkdir("/apps/" + sub)
        for fname in sorted(os.listdir(sub_path)):
            fpath = os.path.join(sub_path, fname)
            if os.path.isfile(fpath):
                with open(fpath, "rb") as f:
                    data = f.read()
                with fs.open(f"/apps/{sub}/{fname}", "wb") as f:
                    f.write(data)
                print(f"  + /apps/{sub}/{fname:<20} ({len(data)} bytes)")
                count += 1

    if count == 0:
        sys.exit(f"ERROR: no .py files or asset subdirectories found in {apps_dir}")

    with open(out_path, "wb") as f:
        f.write(fs.context.buffer)
    print(f"\nBuilt LittleFS image: {out_path} "
          f"({count} files, {len(fs.context.buffer):,} bytes)")
    return count


def main():
    p = argparse.ArgumentParser(
        description="Bulk-upload apps to a gotchiOS device's LittleFS storage partition.")
    p.add_argument("--port", required=True,
                   help="Serial port (e.g. /dev/cu.usbmodem1101, /dev/ttyACM0, COM5)")
    p.add_argument("--apps-dir", default="apps",
                   help="Directory containing .py apps and asset subfolders (default: ./apps)")
    p.add_argument("--keep-image", action="store_true",
                   help="Keep the built storage.bin next to this script after flashing")
    p.add_argument("--baud", default="460800",
                   help="Flash baud rate (default: 460800)")
    args = p.parse_args()

    apps_dir = os.path.abspath(args.apps_dir)
    if not os.path.isdir(apps_dir):
        sys.exit(f"ERROR: apps directory not found: {apps_dir}")

    try:
        import littlefs  # noqa: F401
    except ImportError:
        sys.exit("ERROR: littlefs-python not installed.\n"
                 "  pip install littlefs-python")

    here = os.path.dirname(os.path.abspath(__file__))
    img_path = os.path.join(here, "storage.bin")

    build_image(apps_dir, img_path)

    print(f"\nFlashing to 0x{PARTITION_OFFSET:x} on {args.port}...")
    subprocess.run([
        sys.executable, "-m", "esptool",
        "--chip", "esp32s3",
        "--port", args.port,
        "--baud", args.baud,
        "--before", "usb_reset",
        "--after", "hard_reset",
        "write_flash", hex(PARTITION_OFFSET), img_path,
    ], check=True)

    if not args.keep_image:
        os.remove(img_path)

    print("\nDone — reboot the device. The launcher will rescan and show the new app list.")


if __name__ == "__main__":
    main()
