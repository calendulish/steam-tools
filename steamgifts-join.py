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
from sys import argv
from signal import signal, SIGINT
from configparser import NoOptionError, NoSectionError
from bs4 import BeautifulSoup as bs

import stlogger
import stconfig
from stnetwork import tryConnect

logger = stlogger.init(os.path.splitext(argv[0])[0]+'.log')
config = stconfig.init(os.path.splitext(argv[0])[0]+'.config')

try:
    cookie = {'PHPSESSID': config.get('CONFIG', 'Cookie')}
except(NoOptionError, NoSectionError):
    logger.critical("Incorrect data. Please, check your config file.")
    exit(1)

def signal_handler(signal, frame):
    print("\n")
    logger.info("Exiting...")
    exit(0)

if __name__ == "__main__":
    signal(SIGINT, signal_handler)

    data = {}

    url = 'http://www.steamgifts.com/giveaways/search?type=wishlist'

    logger.info("Connecting to the server")
    page = tryConnect(url, cookies=cookie).content

    try:
        giveawayList = []
        container = bs(page, 'html.parser').find('div', class_='widget-container')
        for div in container.findAll('div', class_=None):
            if div.find('div', class_='giveaway__row-outer-wrap'):
                giveawayList.append(div)

        for giveaway in giveawayList[1].findAll('div', class_='giveaway__row-outer-wrap'):
            gameName = giveaway.find('a', class_='giveaway__heading__name').text
            gameURL = giveaway.find('a', class_='giveaway__heading__name')['href']
            gamePoints = giveaway.find('span', class_='giveaway__heading__thin').text

            try:
                gameLevel = giveaway.find('div', class_='giveaway__column--contributor-level').text
            except AttributeError:
                gameLevel = "Level 0+"

            if giveaway.find('div', class_='giveaway__column--contributor-level--negative'):
                gameCanEnter = "CanEnter: No"
            else:
                gameCanEnter = "CanEnter: Yes"

            ### STUB ###
            print(gameName)
            print(gameURL)
            print(gamePoints)
            print(gameLevel)
            print(gameCanEnter)

            print('\n')

        print(' *** Hey, don\'t use this yet! ***\n\n')
        ### STUB ###

    except Exception as e:
        logger.critical(e)
        exit(1)
