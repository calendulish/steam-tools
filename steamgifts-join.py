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

def steamgifts_config():
    logger.info("Initializing...")
    data = {}
    sgconfigURL = "http://www.steamgifts.com/account/settings/giveaways"
    sgconfig = tryConnect(sgconfigURL, cookies=cookie).content
    form = bs(sgconfig, 'html.parser').find('form')
    for inputs in form.findAll('input'):
        data.update({inputs['name']:inputs['value']})
    logger.debug("configData(page): {}".format(data))
    configData = {
                'xsrf_token': data['xsrf_token'],
                'filter_giveaways_exist_in_account': 1,
                'filter_giveaways_missing_base_game': 1,
                'filter_giveaways_level': 1
                }
    logger.debug("configData(post): {}".format(configData))
    tryConnect(sgconfigURL, data=configData, cookies=cookie)

if __name__ == "__main__":
    signal(SIGINT, signal_handler)
    steamgifts_config()

    while True:
        for url in links:
            logger.info("Connecting to {}".format(url))
            page = tryConnect(url, cookies=cookie).content

            try:
                giveawayList = []

                container = bs(page, 'html.parser').find('div', class_='widget-container')
                for div in container.findAll('div', class_=None):
                    if div.find('div', class_='giveaway__row-outer-wrap'):
                        giveawayList.append(div)

                for giveaway in giveawayList[1].findAll('div', class_='giveaway__row-outer-wrap'):
                    myPoints = int(bs(page, 'html.parser').find('span', class_="nav__points").text)
                    myLevel = int(''.join(filter(str.isdigit, bs(page, 'html.parser').find('span', class_=None).text)))
                    if myPoints == 0:
                        break

                    gameName = giveaway.find('a', class_='giveaway__heading__name').text
                    gameQuery = giveaway.find('a', class_='giveaway__heading__name')['href']
                    gamePoints = int(''.join(filter(lambda x: x.isdigit(), giveaway.find('span', class_='giveaway__heading__thin').text)))

                    try:
                        gameLevel = int(''.join(filter(lambda x: x.isdigit(), giveaway.find('div', class_='giveaway__column--contributor-level').text)))
                    except AttributeError:
                        gameLevel = 0

                    # Check for points, and if we already enter.
                    if myPoints >= gamePoints and not giveaway.find('div', class_='is-faded'):
                        data = {}
                        gvpage = tryConnect("http://steamgifts.com"+gameQuery, cookies=cookie).content
                        form = bs(gvpage, 'html.parser').find('form')
                        for inputs in form.findAll('input'):
                            data.update({inputs['name']:inputs['value']})
                        logger.debug("pageData: {}".format(data))
                        formData = {'xsrf_token': data['xsrf_token'], 'do': 'entry_insert', 'code': data['code']}
                        logger.debug("formData: {}".format(formData))
                        tryConnect("http://www.steamgifts.com/ajax.php", data=formData, cookies=cookie)

                        logger.info("Spent {} points in the giveaway of {}".format(gamePoints, gameName))
                    else:
                        logger.debug("Ignoring {} bacause the account don't have the requirements to enter.".format(gameName))

                    logger.debug("L({}) ML({}) P({}) MP({}) Q({})".format(gameLevel, myLevel, gamePoints, myPoints, gameQuery))

            except Exception as e:
                logger.error("An error occured for url {}".format(url))
                logger.error("Please, check if it's a valid url.")
                logger.warning(e)

            print('')

        logger.debug("Remaining points: {}".format(myPoints))
        randomstart = randint(minTime, maxTime)
        for i in range(0, randomstart):
            print("Waiting: {:4d} seconds".format(randomstart-i), end="\r")
            sleep(1)
