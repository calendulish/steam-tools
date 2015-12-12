#!/usr/bin/env python
#
# Lara Maia <dev@lara.click> 2015
#
# The Steam Tools is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# The Steam Tools is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see http://www.gnu.org/licenses/.
#

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
        if not STEAM_API.SteamAPI_Init():
            print("I cannot find a game with that ID. Exiting.")
            exit(1)

        print("Game started.")
        while True:
            sleep(1)
    else:
        print("I cannot find a Steam instance.", file=sys.stderr)
        print("Please, check if your already start your steam client.", file=sys.stderr)
        exit(1)
