#!/bin/bash
# host-side prepareImage hook (runs after _prep_vhd_disk materialized
# "${VM_OS_NAME}.qcow2", BEFORE the VM is first started).
#
# The official 9front qcow2 already ships plan9.ini with console=0 (serial
# console), but its first boot still asks two questions (bootargs, user).
# plan9.ini(8): nobootprompt= suppresses the bootargs question, user=
# suppresses the user question. Bake both so every boot -- build and anyvm
# runtime alike -- is fully unattended on the serial console.
#
# plan9.ini lives in the 9fat FAT partition, which starts at relative
# sector 0 of the single MBR partition (type 0x39 "Plan 9"), so the Linux
# host can mount /dev/nbd0p1 as vfat directly (verified: the plan9
# disklabel in sector 1 reads "part 9fat 0 204800"). Same qemu-nbd pattern
# as hurd-builder/hooks/host_prepareImage.sh (proven on GitHub runners and
# WSL).
#
# The disk device name baked into nobootprompt matches the build/runtime
# QEMU shape: virtio-blk (-drive if=virtio) enumerates as /dev/sdF0.

set -e

echo "Preparing ${VM_OS_NAME}.qcow2 (9front) via qemu-nbd"

_qcow="${VM_OS_NAME}.qcow2"
NBD=/dev/nbd0
M_FAT="$(pwd)/mnt-plan9-9fat"

_cleanup() {
  sudo umount "$M_FAT" 2>/dev/null || true
  sudo qemu-nbd --disconnect "$NBD" 2>/dev/null || true
}
trap _cleanup EXIT

mkdir -p "$M_FAT"

sudo modprobe nbd max_part=16
sudo qemu-nbd --disconnect "$NBD" 2>/dev/null || true
sudo qemu-nbd --connect="$NBD" "$_qcow"
sudo partprobe "$NBD" 2>/dev/null || true
sleep 2

if [ ! -b "${NBD}p1" ]; then
  echo "FATAL: ${NBD}p1 did not appear (unexpected image layout)" >&2
  sudo fdisk -l "$NBD" || true
  exit 1
fi

sudo mount -t vfat "${NBD}p1" "$M_FAT"

if [ ! -e "$M_FAT/PLAN9.INI" ] && [ ! -e "$M_FAT/plan9.ini" ]; then
  echo "FATAL: no plan9.ini in the 9fat partition" >&2
  ls -la "$M_FAT" >&2 || true
  exit 1
fi

echo "--- plan9.ini before ---"
cat "$M_FAT/PLAN9.INI" 2>/dev/null || cat "$M_FAT/plan9.ini"

# Rewrite wholesale: the stock file is just bootfile+console, and a full
# rewrite is idempotent across build retries (append would duplicate keys).
sudo tee "$M_FAT/PLAN9.INI" >/dev/null <<'P9INI'
bootfile=9pc64
console=0
nobootprompt=local!/dev/sdF0/fs
user=glenda
P9INI

echo "--- plan9.ini after ---"
cat "$M_FAT/PLAN9.INI"

# Targeted syncfs of just this mount -- NEVER a bare global `sync` (WSL
# drvfs wedge; see blissos notes).
sync -f "$M_FAT" 2>/dev/null || true
sudo umount "$M_FAT"
sudo qemu-nbd --disconnect "$NBD"
trap - EXIT

sudo chmod 0666 "$_qcow" 2>/dev/null || true

echo "Image prepared:"
ls -lh "$_qcow"
