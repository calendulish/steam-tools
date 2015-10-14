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
    print("Hello~wooooo. Where is the game ID?", file=sys.stderr)
    exit(1)

os.environ["SteamAppId"] = sys.argv[1]

if STEAM_API.SteamAPI_IsSteamRunning():
    STEAM_API.SteamAPI_Init()

    print("Game started.")
    while True:
        sleep(1000*1000)
else:
    print("I cannot find a Steam instance.", file=sys.stderr)
    print("Please, check if your already start your steam client.", file=sys.stderr)
    exit(1)
