#  Keep the import order, please

import atexit

import gevent.monkey

gevent.monkey.patch_all()

# noinspection PyPep8
from stlib import (logging,
                   config,
                   network,
                   browser,
                   libsteam,
                   card_farming,
                   steamgifts_bump)

__all__ = ['logging',
           'config',
           'network',
           'browser',
           'libsteam',
           'card_farming',
           'steamgifts_bump']

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
SG_check_page = 'https://www.steamgifts.com/account/profile/sync'
SC_check_page = 'https://steamcompanion.com/settings'

steam_user = None
SG_user = None
SC_user = None


def steam_profile():
    return '{}/?redirectURL=id/{}'.format(steam_login_page, steam_user)
