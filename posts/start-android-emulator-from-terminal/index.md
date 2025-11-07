---
title: "Start the android emulator from terminal"
date: 2018-08-14
tags: android linux osx shell
---

I needed a way to start my android emulator without opening Android Studio.

First i tried to run the avd with the standard emulator command but that didn't worked.
```
$ emulator -avd Pixel_XL_API_25
PANIC: Missing emulator engine program for 'x86' CPU.
```
So i searched the web and found out that i need to run some other emulator and symlink it somewhere else.
I dind't liked the idea.
My next thought was "What is android studio doing?". I watched my processes and started the emulator from Android Studio.
```
$ ps aux  grep qemu
... /usr/lib/android-sdk/emulator/qemu/linux-x86_64/qemu-system-x86_64 -netdelay none -netspeed full -no-snapshot-load -avd Pixel_XL_API_25
```
Nice this looks promising.
```
$ /usr/lib/android-sdk/emulator/qemu/linux-x86_64/qemu-system-x86_64 -netdelay none -netspeed full -no-snapshot-load -avd Pixel_XL_API_25
/usr/lib/android-sdk/emulator/qemu/linux-x86_64/qemu-system-x86_64: error while loading shared libraries: libc++.so.1: cannot open shared object file: No such file or directory
```
Well it looks like Android Studio provides its own libraries and we need to prepare our environment so that the emulator can start properly.
```
$ xargs --null --max-args=1 < /proc/ID_THE_OUR_QEMU_PROCESS/environ
# i will only show you the necessary lines
# ...
LD_LIBRARY_PATH=/usr/lib/android-sdk/emulator/lib64/qt/lib:/usr/lib/android-sdk/emulator/lib64/libstdc++:/usr/lib/android-sdk/emulator/lib64/gles_angle11:/usr/lib/android-sdk/emulator/lib64/gles_angle9:/usr/lib/android-sdk/emulator/lib64/gles_angle:/usr/lib/android-sdk/emulator/lib64/gles_swiftshader:/usr/lib/android-sdk/emulator/lib64
ANDROID_EMULATOR_LAUNCHER_DIR=/usr/lib/android-sdk/emulator
# ...
```
With that information i created a launch script for my emulator.
```
#!/usr/bin/env bash
export ANDROID_EMULATOR_LAUNCHER_DIR=/usr/lib/android-sdk/emulator
export LD_LIBRARY_PATH=/usr/lib/android-sdk/emulator/lib64/qt/lib:/usr/lib/android-sdk/emulator/lib64/libstdc++:/usr/lib/android-sdk/emulator/lib64/gles_angle11:/usr/lib/android-sdk/emulator/lib64/gles_angle9:/usr/lib/android-sdk/emulator/lib64/gles_angle:/usr/lib/android-sdk/emulator/lib64/gles_swiftshader:/usr/lib/android-sdk/emulator/lib64

EMULATOR86="$ANDROID_HOME/emulator/qemu/linux-x86_64/qemu-system-x86_64"
EMULATOR="$ANDROID_HOME/tools/emulator"
DEVICE=`$EMULATOR -list-avds | tail -1`

RUN="$EMULATOR86 -netdelay none -netspeed full -no-snapshot-load -avd $DEVICE"

echo "Run $RUN"

$RUN
```
