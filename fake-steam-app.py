#!/usr/bin/env python
# Lara Maia <dev@lara.click> 2015

import os, sys
from time import sleep
from signal import signal, SIGINT

from ctypes import CDLL

if os.name == 'nt':
    ext = '.dll'
else:
    ext = '.so'

if sys.maxsize > 2**32:
    STEAM_API = CDLL('lib64/libsteam_api' + ext)
else:
    STEAM_API = CDLL('lib32/libsteam_api' + ext)

if len(sys.argv) < 2:
    print("Hello~wooooo. Where is the game ID?", file=sys.stderr)
    exit(1)

def signal_handler(signal, frame):
    print("Exiting...")
    exit(0)

if __name__ == "__main__":
    signal(SIGINT, signal_handler)
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
