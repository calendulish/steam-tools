import sys

import gevent

from stlib import gui_mode
from ui import console, version

__all__ = ['console', 'version']

if len(sys.argv) == 1:
    import gi

    gi.require_version('Gtk', '3.0')

    from gi.repository import Gtk

    from ui import (main,
                    signals,
                    timers)

    __all__.extend(['main',
                    'signals',
                    'timers'])

def update_main_loop():
    gevent.sleep(0.001)

    if gui_mode:
        Gtk.main_iteration()

main_window = None
application = None
selected_profile_id = 0

card_farming_is_running = False
card_farming_game_start_time = None
fake_app_is_running = False
fake_app_id = None
steamtrades_bump_is_running = False
steamtrades_bump_waiting = False
steamgifts_join_is_running = False
steamgifts_join_waiting = False
steamgifts_join_giveaway_waiting = False
