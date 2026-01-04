#!/bin/bash

# Start CachyOS VM for hackmud bot
# Increased memory from 4G to 8G for stability

qemu-system-x86_64 \
    -enable-kvm \
    -m 8G \
    -smp 4 \
    -cpu host \
    -drive file=/home/jacob/VMs/cachyos/disk.qcow2,format=qcow2,if=virtio \
    -net nic,model=virtio \
    -net user,hostfwd=tcp::2222-:22 \
    -vga virtio \
    -display sdl,gl=on \
    -usb \
    -device usb-tablet
