#!/bin/sh

udevadm control --reload

libcamera-hello --list-cameras -n -v

libcamera-hello -o wtf.png

#su lig
python snapper.py

