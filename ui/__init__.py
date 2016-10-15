import sys

if len(sys.argv) == 1:
    import gi

    gi.require_version('Gtk', '3.0')
    # noinspection PyUnresolvedReferences
    from gi.repository import Gtk, Gdk, GLib, Gio

# noinspection PyPep8
from ui import (console,
                main,
                signals,
                timers)

__all__ = ['console',
           'main',
           'signals',
           'timers']

main_window = None
application = None
selected_profile_id = 0

card_farming_is_running = False
card_farming_game_start_time = None
fake_app_is_running = False
fake_app_id = None
