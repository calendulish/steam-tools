#  Keep the import order, please

import atexit
import sys

import gevent.monkey

gevent.monkey.patch_all()

if len(sys.argv) == 1:
    gui_mode = True
else:
    gui_mode = False

# noinspection PyPep8
from stlib import (logging,
                   config,
                   network,
                   browser,
                   libsteam,
                   logins,
                   card_farming,
                   steamtrades_bump,
                   steamgifts_join)

__all__ = ['logging',
           'config',
           'network',
           'browser',
           'libsteam',
           'logins',
           'card_farming',
           'steamtrades_bump',
           'steamgifts_join']

logger = logging.get_logger()
wrapper_process = None


def __safe_exit():
    logging.console_fixer()
    logger.warning('Exiting...')

    if wrapper_process:
        return libsteam.stop_wrapper()


atexit.register(__safe_exit)

steam_login_page = 'https://steamcommunity.com/login/checkstoredlogin'
steam_check_page = '{}/?redirectURL=discussions'.format(steam_login_page)
steamgifts_check_page = 'https://www.steamgifts.com/account/profile/sync'
steamgifts_query_page = 'https://www.steamgifts.com/giveaways/search'
steamtrades_check_page = 'https://www.steamtrades.com/legal/privacy-policy'
steamtrades_trade_page = 'https://www.steamtrades.com/trade/'
steamcompanion_check_page = 'https://steamcompanion.com/settings'

steam_user = None
SG_user = None
ST_user = None
SC_user = None


def steam_profile():
    return '{}/?redirectURL=id/{}'.format(steam_login_page, steam_user)
