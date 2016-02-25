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
from random import randint
from signal import signal, SIGINT
from configparser import NoOptionError, NoSectionError
from bs4 import BeautifulSoup as bs

from stlib import stlogger
from stlib.stconfig import read_config
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
    logger.critical("Incorrect data. (Updated with the new options?)")
    logger.critical("Please, check your config file.")
    logger.debug('', exc_info=True)
    exit(1)

def signal_handler(signal, frame):
    stlogger.cfixer()
    logger.info("Exiting...")
    exit(0)

def steamgifts_config():
    logger.info("Initializing...")
    data = {}
    sgconfigURL = "http://www.steamgifts.com/account/settings/giveaways"
    sgconfig = tryConnect(configFile, sgconfigURL).content
    form = bs(sgconfig, 'html.parser').find('form')
    for inputs in form.findAll('input'):
        data.update({inputs['name']:inputs['value']})
    logger.debug("configData(page): %s", data)
    configData = {
                'xsrf_token': data['xsrf_token'],
                'filter_giveaways_exist_in_account': 1,
                'filter_giveaways_missing_base_game': 1,
                'filter_giveaways_level': 1
                }
    logger.debug("configData(post): %s", configData)
    tryConnect(configFile, sgconfigURL, data=configData)

if __name__ == "__main__":
    signal(SIGINT, signal_handler)
    steamgifts_config()

    while True:
        for url in links:
            logger.info("Connecting to %s", url)
            page = tryConnect(configFile, url).content

            try:
                giveawayList = []
                myPoints = int(bs(page, 'html.parser').find('span', class_="nav__points").text)
                myLevel = int(''.join(filter(str.isdigit, bs(page, 'html.parser').find('span', class_=None).text)))

                container = bs(page, 'html.parser').find('div', class_='widget-container')
                for div in container.findAll('div', class_=None):
                    if div.find('div', class_='giveaway__row-outer-wrap'):
                        giveawayList.append(div)

                try:
                    giveawayList[1]
                except IndexError:
                    logger.debug("No giveaways found at %s", url)
                    continue

                for giveaway in giveawayList[1].findAll('div', class_='giveaway__row-outer-wrap'):
                    if myPoints == 0:
                        break

                    gameName = giveaway.find('a', class_='giveaway__heading__name').text
                    gameQuery = giveaway.find('a', class_='giveaway__heading__name')['href']
                    gvHeader = giveaway.find('span', class_='giveaway__heading__thin')

                    if "Copies" in gvHeader.text:
                        logger.debug("The giveaway has more than 1 copy. Counting and fixing gvHeader.")
                        gameCopies = int(''.join(filter(lambda x: x.isdigit(), gvHeader.text)))
                        gvHeader = gvHeader.findNext('span', class_='giveaway__heading__thin')
                    else:
                        gameCopies = 1

                    gamePoints = int(''.join(filter(lambda x: x.isdigit(), gvHeader.text)))

                    try:
                        gameLevel = int(''.join(filter(lambda x: x.isdigit(), giveaway.find('div', class_='giveaway__column--contributor-level').text)))
                    except AttributeError:
                        gameLevel = 0

                    # Check for points, and if we already enter.
                    if myPoints >= gamePoints and not giveaway.find('div', class_='is-faded'):
                        data = {}
                        gvpage = tryConnect(configFile, "http://steamgifts.com"+gameQuery).content
                        form = bs(gvpage, 'html.parser').find('form')
                        for inputs in form.findAll('input'):
                            data.update({inputs['name']:inputs['value']})
                        logger.debug("pageData: %s", data)
                        formData = {'xsrf_token': data['xsrf_token'], 'do': 'entry_insert', 'code': data['code']}
                        logger.debug("formData: %s", formData)
                        tryConnect(configFile, "http://www.steamgifts.com/ajax.php", data=formData)
                        myPoints -= gamePoints

                        logger.info("Spent %d points in the giveaway of %s (Copies: %d)", gamePoints, gameName, gameCopies)
                    else:
                        logger.debug("Ignoring %s bacause the account don't have the requirements to enter.", gameName)

                    logger.debug("C(%d) L(%d) ML(%d) P(%d) MP(%d) Q(%s)", gameCopies, gameLevel, myLevel, gamePoints, myPoints, gameQuery)

            except Exception:
                logger.error("An error occured for url %s", url)
                logger.error("Please, check if it's a valid url.")
                logger.debug('', exc_info=True)

            stlogger.cfixer()

        logger.debug("Remaining points: %d", myPoints)
        randomstart = randint(minTime, maxTime)
        for i in range(0, randomstart):
            stlogger.cmsg("Waiting: {:4d} seconds".format(randomstart-i), end='\r')
            sleep(1)
