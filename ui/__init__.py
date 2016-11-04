import sys

from ui import console, version

__all__ = ['console', 'version']

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
steamtrades_bump_is_running = False
steamtrades_bump_waiting = False
steamgifts_join_is_running = False
steamgifts_join_waiting = False
steamgifts_join_giveaway_waiting = False
