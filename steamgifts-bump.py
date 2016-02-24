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
from stlib import stconfig
from stlib.stnetwork import tryConnect

loggerFile = os.path.basename(__file__)[:-3]+'.log'
configFile = os.path.basename(__file__)[:-3]+'.config'

logger = stlogger.init(loggerFile)
config = read_config(configFile)

try:
    cookie = dict(config.items('Cookies'))
    links = [l.strip() for l in config.get('Config', 'Links').split(',')]
    minTime = config.getint('Config', 'minTime')
    maxTime = config.getint('Config', 'maxTime')
    icheck = config.getboolean('Debug', 'IntegrityCheck')
except(NoOptionError, NoSectionError):
    logger.critical("Incorrect data. Please, check your config file.")
    logger.debug('', exc_info=True)
    exit(1)

def signal_handler(signal, frame):
    print("\n")
    logger.info("Exiting...")
    exit(0)

if __name__ == "__main__":
    signal(SIGINT, signal_handler)

    while True:
        data = {}

        logger.info("Bumping now! %s", datetime.now())

        for url in links:
            print("Connecting to the server", end="\r")
            page = tryConnect(configFile, url).content

            try:
                form = bs(page, 'html.parser').find('form')
                for inputs in form.findAll('input'):
                    data.update({inputs['name']:inputs['value']})

                postData = {'xsrf_token': data['xsrf_token'], 'do': 'bump_trade'}
                tryConnect(configFile, url, data=postData)

                logger.info("Bumped %s", url)
            except Exception:
                logger.error("An error occured for url %s", url)
                logger.error("Please, check if it's a valid url.")
                logger.debug('', exc_info=True)

        randomstart = randint(minTime, maxTime)
        for i in range(0, randomstart):
            print("Waiting: {:4d} seconds".format(randomstart-i), end="\r")
            sleep(1)
