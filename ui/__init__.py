import sys

from ui import console

__all__ = ['console']

if len(sys.argv) == 1:
    from ui import (main,
                    signals,
                    timers)

    __all__.extend(['main',
                    'signals',
                    'timers'])

main_window = None
application = None
selected_profile_id = 0

card_farming_is_running = False
card_farming_game_start_time = None
fake_app_is_running = False
fake_app_id = None
