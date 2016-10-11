#  Keep the import order, please

import gevent.monkey

gevent.monkey.patch_all()

from stlib import (logging,
                   config,
                   network,
                   browser,
                   card_farming)

__all__ = ['logger',
           'config',
           'network',
           'browser',
           'card_farming']

logger = logging.get_logger()

steam_login_page = 'https://steamcommunity.com/login/checkstoredlogin'
steam_check_page = '{}/?redirectURL=discussions'.format(steam_login_page)
SG_check_page = 'https://www.steamgifts.com/account/profile/sync'
SC_check_page = 'https://steamcompanion.com/settings'

steam_user = None
SG_user = None
SC_user = None

steam_profile = lambda: '{}/?redirectURL=id/{}'.format(steam_login_page, steam_user)
