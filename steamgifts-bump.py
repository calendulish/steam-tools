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

import os
from time import sleep
from datetime import datetime
from random import randint
from signal import signal, SIGINT
from configparser import NoOptionError, NoSectionError
from bs4 import BeautifulSoup as bs

from stlib import stlogger
from stlib.stconfig import get_config_path, read_config
from stlib.stnetwork import tryConnect

loggerFile = os.path.basename(__file__)[:-3]+'.log'
configFile = os.path.basename(__file__)[:-3]+'.config'

logger = stlogger.init(loggerFile)
config = read_config(configFile)

try:
    tradeID = [l.strip() for l in config.get('Config', 'tradeID').split(',')]
except(NoOptionError, NoSectionError):
    tradeID = [ 'EXAMPLEID1', 'EXAMPLEID2' ]
    config.set('Config', 'tradeID', "EXAMPLEID1, EXAMPLEID2")
    logger.warn("No tradeID found in the config file. Using EXAMPLEID's.")
    logger.warn("Please, edit the auto-generated config file after this run.")

def signal_handler(signal, frame):
    stlogger.cfixer()
    logger.info("Exiting...")
    exit(0)

if __name__ == "__main__":
    signal(SIGINT, signal_handler)

    while True:
        data = {}

        logger.info("Bumping now! %s", datetime.now())

        for id in tradeID:
            stlogger.cmsg("Connecting to the server", end='\r')
            url = "http://www.steamgifts.com/trade/"+id+'/'
            response = tryConnect(configFile, url)

            try:
                page = response.content
            except AttributeError:
                logger.error("tradeID %s is incorrect. Ignoring.", id)
                logger.error("Please, update your config file at %s", get_config_path(configFile))
                continue

            url = response.url
            title = os.path.basename(url).replace('-', ' ')

            try:
                form = bs(page, 'html.parser').find('form')
                for inputs in form.findAll('input'):
                    data.update({inputs['name']:inputs['value']})

                postData = {'xsrf_token': data['xsrf_token'], 'do': 'bump_trade'}
                ret = tryConnect(configFile, url, data=postData).content
                if 'Please wait' in ret.decode('utf-8'):
                    logger.warning('%s (%s) Already bumped. Please wait. %12s', id, title, '')
                else:
                    tradePage = tryConnect(configFile, 'http://www.steamgifts.com/trades').content
                    if id in tradePage.decode('utf-8'):
                        logger.info("%s (%s) Bumped! %12s", id, title, '')
                    else:
                        raise Exception
            except Exception:
                logger.error("An error occured for ID %s %12s", id, '')
                logger.error("Please, check if it's a valid ID.")
                logger.debug('', exc_info=True)

        randomstart = randint(config.getint('Config', 'minTime', fallback=3700), config.getint('Config', 'maxTime', fallback=4100))
        for i in range(0, randomstart):
            stlogger.cmsg("Waiting: {:4d} seconds".format(randomstart-i), end='\r')
            sleep(1)
