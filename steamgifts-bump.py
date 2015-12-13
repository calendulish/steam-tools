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

logger = stlogger.init(os.path.splitext(os.path.basename(__file__))[0]+'.log')
config = stconfig.init(os.path.splitext(os.path.basename(__file__))[0]+'.config')

try:
    cookie = {'PHPSESSID': config.get('CONFIG', 'Cookie')}
    links = [l.strip() for l in config.get('CONFIG', 'Links').split(',')]
    minTime = config.getint('CONFIG', 'minTime')
    maxTime = config.getint('CONFIG', 'maxTime')
except(NoOptionError, NoSectionError):
    logger.critical("Incorrect data. Please, check your config file.")
    exit(1)

def signal_handler(signal, frame):
    print("\n")
    logger.info("Exiting...")
    exit(0)

if __name__ == "__main__":
    signal(SIGINT, signal_handler)

    while True:
        data = {}

        logger.info("Bumping now! {}".format(datetime.now()))

        for url in links:
            print("Connecting to the server", end="\r")
            page = tryConnect(url, cookies=cookie).content

            try:
                form = bs(page, 'html.parser').find('form')
                for inputs in form.findAll('input'):
                    data.update({inputs['name']:inputs['value']})

                postData = {'xsrf_token': data['xsrf_token'], 'do': 'bump_trade'}
                tryConnect(url, data=postData, cookies=cookie)

                logger.info("Bumped {}".format(url))
            except Exception:
                logger.error("An error occured for url {}".format(url))
                logger.error("Please, check if it's a valid url.")

        randomstart = randint(minTime, maxTime)
        for i in range(0, randomstart):
            print("Waiting: {:4d} seconds".format(randomstart-i), end="\r")
            sleep(1)
