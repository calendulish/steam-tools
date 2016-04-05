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

import os, sys
from time import sleep
from datetime import datetime
from random import randint
from signal import signal, SIGINT
from configparser import NoOptionError, NoSectionError
from bs4 import BeautifulSoup as bs

from stlib import stlogger
from stlib import stconfig
from stlib import stnetwork
from stlib import stcygwin

LOGGER = stlogger.getLogger()
CONFIG = stconfig.getParser()

try:
    TRADEID = [l.strip() for l in CONFIG.get('Config', 'tradeID').split(',')]
except(NoOptionError, NoSectionError):
    TRADEID = [ 'EXAMPLEID1', 'EXAMPLEID2' ]
    CONFIG.set('Config', 'tradeID', "EXAMPLEID1, EXAMPLEID2")
    LOGGER.warn("No tradeID found in the config file. Using EXAMPLEID's.")
    LOGGER.warn("Please, edit the auto-generated config file after this run.")

def signal_handler(signal, frame):
    stlogger.cfixer()
    LOGGER.info("Exiting...")
    sys.exit(0)

def bumpTrade(id, response):
    try:
        page = response.content
    except AttributeError:
        LOGGER.error("tradeID %s is incorrect. Ignoring.", id)
        LOGGER.error("Please, update your config file at %s", stconfig.getPath())
        return

    url = response.url
    title = os.path.basename(url).replace('-', ' ')
    form = bs(page, 'html.parser').find('form')
    data = dict([ (inputs['name'], inputs['value']) for inputs in form.findAll('input') ])
    postData = {'xsrf_token': data['xsrf_token'], 'do': 'bump_trade'}

    try:
        ret = stnetwork.tryConnect(url, data=postData).content
        stlogger.cfixer('\r')
        if 'Please wait' in ret.decode('utf-8'):
            LOGGER.warning('%s (%s) Already bumped. Please wait.', id, title)
        else:
            tradePage = stnetwork.tryConnect('http://www.steamgifts.com/trades').content
            if id in tradePage.decode('utf-8'):
                LOGGER.info("%s (%s) Bumped!", id, title)
            else:
                raise Exception
    except Exception:
        stlogger.cfixer('\r')
        LOGGER.error("An error occured for ID %s", id)
        LOGGER.error("Please, check if it's a valid ID.")
        LOGGER.debug('', exc_info=True)

if __name__ == "__main__":
    signal(SIGINT, signal_handler)

    while True:
        LOGGER.info("Bumping now! %s", datetime.now())

        for id in TRADEID:
            stlogger.cmsg("Connecting to the server", end='\r')
            url = "http://www.steamgifts.com/trade/"+id+'/'
            response = stnetwork.tryConnect(url)

            bumpTrade(id, response)

        randomstart = randint(CONFIG.getint('Config', 'minTime', fallback=3700), CONFIG.getint('Config', 'maxTime', fallback=4100))
        for i in range(0, randomstart):
            stlogger.cmsg("Waiting: {:4d} seconds".format(randomstart-i), end='\r')
            sleep(1)
