#!/usr/bin/env python
# Lara Maia <dev@lara.click> 2015

from ctypes import CDLL
from time import sleep
import os, sys

if sys.maxsize > 2**32:
    STEAM_API = CDLL('lib64/libsteam_api.so')
else:
    STEAM_API = CDLL('lib32/libsteam_api.so')

if len(sys.argv) < 2:
    print("Hello~wooooo. Where is the game ID?")
    exit(1)

os.environ["SteamAppId"] = sys.argv[1]

STEAM_API.SteamAPI_Init()

print("Game started.")
while True:
    sleep(1000*1000)
