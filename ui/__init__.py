import sys

if len(sys.argv) == 1:
    import gi

    gi.require_version('Gtk', '3.0')
    # noinspection PyUnresolvedReferences
    from gi.repository import Gtk, Gdk, GLib


from ui import (console,
                libsteam,
                logins,
                main,
                signals,
                timers,
                card_farming,
                globals)

__all__ = ['console',
           'libsteam',
           'logins',
           'main',
           'signals',
           'timers',
           'card_farming',
           'globals']
