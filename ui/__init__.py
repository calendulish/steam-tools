import sys

if len(sys.argv) == 1:
    import gi

    gi.require_version('Gtk', '3.0')
    # noinspection PyUnresolvedReferences
    from gi.repository import Gtk, Gdk, GLib

# noinspection PyPep8
from ui import (console,
                logins,
                main,
                signals,
                timers,
                globals)

__all__ = ['console',
           'logins',
           'main',
           'signals',
           'timers',
           'globals']

main_window = None
