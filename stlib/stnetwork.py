#!/usr/bin/env python
#
# Lara Maia <dev@lara.click> 2015 ~ 2016
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

import sys
from time import sleep
from logging import getLogger

import requests
requests.packages.urllib3.disable_warnings()

from stlib import stconfig
from stlib import stcookie
from stlib import stlogger

AGENT = {'user-agent': 'unknown/0.0.0'}
LOGGER = getLogger('root')
CONFIG = stconfig.getParser()

steamLoginPages = [
                    'https://steamcommunity.com/login/home/',
                    'https://store.steampowered.com//login/',
                ]

def tryConnect(url, data=False):
    autoRecovery = False
    attempt = 1
    while True:
        try:
            if CONFIG.getboolean('Debug', 'IntegrityCheck', fallback=False):
                LOGGER.debug("Current cookies: %s", CONFIG._sections['Cookies'])

            try:
                if not len(CONFIG._sections['Cookies']):
                    raise KeyError
            except KeyError:
                LOGGER.debug("I found no cookies in the Cookies section.")
                raise requests.exceptions.TooManyRedirects

            if data:
                response = requests.post(url,
                                         data=data,
                                         cookies=CONFIG._sections['Cookies'],
                                         headers=AGENT,
                                         timeout=10,
                                         verify=False)
            else:
                response = requests.get(url,
                                        cookies=CONFIG._sections['Cookies'],
                                        headers=AGENT,
                                        timeout=10,
                                        verify=False)

            response.raise_for_status()

            # If steam login page is found in response, throw exception.
            if any(p in str(response.content) for p in steamLoginPages):
                raise requests.exceptions.TooManyRedirects

            if autoRecovery:
                LOGGER.info("[WITH POWERS] Success!!!")
                LOGGER.info("POWERS... DESACTIVATE!")

            autoRecovery = False
            return response
        except requests.exceptions.TooManyRedirects:
            if not autoRecovery:
                LOGGER.error("Invalid or expired cookies.")
                LOGGER.info("POWERS... ACTIVATE!")
                LOGGER.info("[WITH POWERS] Trying to automagically recovery...")
                CONFIG['Cookies'] = stcookie.getCookies(url)
                stconfig.write()
                autoRecovery = True
            else:
                LOGGER.critical("I cannot recover D:")
                LOGGER.critical("(Chrome/Chromium profile not found? Cookies not found?)")
                LOGGER.critical("Please, check your configuration and update your cookies.")
                LOGGER.debug('', exc_info=True)
                sys.exit(1)
        except(requests.exceptions.HTTPError, requests.exceptions.RequestException):
            # Report to steamgifts-bump if the tradeID is incorrect"
            if "/trade/" in url: return ""
            stlogger.cmsg("The connection is refused or fails. Trying again... ({} attempt)".format(attempt), end='\r')
            attempt += 1
            LOGGER.debug('', exc_info=True)
            sleep(3)
            stlogger.cfixer('\r')

    LOGGER.critical("Cannot access the internet! Please, check your internet connection.")
    sys.exit(1)
