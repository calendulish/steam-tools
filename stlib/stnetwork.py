#!/usr/bin/env python
#
# Lara Maia <dev@lara.click> 2015
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

from time import sleep
from logging import getLogger

import requests

from stlib.stconfig import read_config, write_config
from stlib.stcookie import get_steam_cookies

agent = {'user-agent': 'unknown/0.0.0'}
logger = getLogger('root')
steamLoginPages = [
                    'https://steamcommunity.com/login/home/',
                    'https://store.steampowered.com//login/',
                ]

def tryConnect(config_file, url, data=False):
    config = read_config(config_file)
    autorecovery = False

    while True:
        try:
            if config.getboolean('Debug', 'IntegrityCheck'):
                logger.debug("Current cookies: %s", config._sections['Cookies'])

            if not len(config._sections['Cookies']):
                logger.debug("I found no cookie in the config sections.")
                raise requests.exceptions.TooManyRedirects

            if data:
                response = requests.post(url, data=data, cookies=config._sections['Cookies'], headers=agent, timeout=10)
            else:
                response = requests.get(url, cookies=config._sections['Cookies'], headers=agent, timeout=10)

            response.raise_for_status()

            # If steam login page is found in response, throw exception.
            if any(p in str(response.content) for p in steamLoginPages):
                raise requests.exceptions.TooManyRedirects

            if autorecovery:
                logger.info("[WITH POWERS] Success!!!")
                logger.info("POWERS... DESACTIVATE!")

            autorecovery = False
            return response
        except requests.exceptions.TooManyRedirects:
            if not autorecovery:
                logger.error("Invalid or expired cookies.")
                logger.info("POWERS... ACTIVATE!")
                logger.info("[WITH POWERS] Trying to automagically recovery...")
                config['Cookies'] = get_steam_cookies(config_file, url)
                write_config(config_file)
                autorecovery = True
            else:
                logger.critical("I cannot recover D:")
                logger.critical("(Chrome/Chromium profile not found? Cookies not found?)")
                logger.critical("Please, check your configuration and update your cookies.")
                logger.debug('', exc_info=True)
                exit(1)
        except(requests.exceptions.HTTPError, requests.exceptions.RequestException):
            logger.error("The connection is refused or fails. Trying again...")
            logger.debug('', exc_info=True)
            sleep(3)

    logger.critical("Cannot access the internet! Please, check your internet connection.")
    exit(1)
