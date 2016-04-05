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
    TYPELIST = [l.strip() for l in CONFIG.get('Config', 'typeList').split(',')]
except(NoOptionError, NoSectionError):
    TYPELIST = [ 'wishlist', 'main', 'new' ]
    CONFIG.set('Config', 'typeList', "wishlist, main, new")
    LOGGER.warn("No typeList found in the config file.")
    LOGGER.warn("Using the default: wishlist, main, new. You can edit these values.")

def signal_handler(signal, frame):
    stlogger.cfixer()
    LOGGER.info("Exiting...")
    sys.exit(0)

def steamgifts_config():
    LOGGER.info("Initializing...")
    data = {}
    sgconfigURL = "http://www.steamgifts.com/account/settings/giveaways"
    sgconfig = stnetwork.tryConnect(sgconfigURL).content
    form = bs(sgconfig, 'html.parser').find('form')
    for inputs in form.findAll('input'):
        data.update({inputs['name']:inputs['value']})
    LOGGER.debug("configData(page): %s", data)
    configData = {
                'xsrf_token': data['xsrf_token'],
                'filter_giveaways_exist_in_account': 1,
                'filter_giveaways_missing_base_game': 1,
                'filter_giveaways_level': 1
                }
    LOGGER.debug("configData(post): %s", configData)
    stnetwork.tryConnect(sgconfigURL, data=configData)

def getGiveaways(page):
    giveaways = []
    container = bs(page, 'html.parser').find('div', class_='widget-container')
    pinned = container.find('div', class_='pinned-giveaways__outer-wrap').extract()

    if CONFIG.getboolean('Config', 'DeveloperGiveaways', fallback=True):
        giveaways = pinned.findAll('div', class_='giveaway__row-outer-wrap')

    giveaways += container.findAll('div', class_='giveaway__row-outer-wrap')

    giveawaySet = {k: [] for k in ['Name', 'Query', 'Copies', 'Points', 'Level']}
    for giveaway in giveaways:
        if giveaway.find('div', class_='is-faded'): continue

        giveawaySet['Name'].append(giveaway.find('a', class_='giveaway__heading__name').text)
        giveawaySet['Query'].append(giveaway.find('a', class_='giveaway__heading__name')['href'])

        gvHeader = giveaway.find('span', class_='giveaway__heading__thin')
        if "Copies" in gvHeader.text:
            LOGGER.debug("The giveaway has more than 1 copy. Counting and fixing gvHeader.")
            giveawaySet['Copies'].append(int(''.join(filter(str.isdigit, gvHeader.text))))
            gvHeader = gvHeader.findNext('span', class_='giveaway__heading__thin')
        else:
            giveawaySet['Copies'].append(1)

        giveawaySet['Points'].append(int(''.join(filter(str.isdigit, gvHeader.text))))

        try:
            gameLevel = giveaway.find('div', class_='giveaway__column--contributor-level')
            giveawaySet['Level'].append(int(''.join(filter(str.isdigit, gameLevel.text))))
        except AttributeError:
            giveawaySet['Level'].append(0)

    return giveawaySet

if __name__ == "__main__":
    signal(SIGINT, signal_handler)
    steamgifts_config()

    while True:
        for type in TYPELIST:
            stlogger.cmsg("Connecting to the server", end='\r')
            query = "http://www.steamgifts.com/giveaways/search?type="
            if type == 'main':
                url = query
            elif type == 'wishlist':
                url = query+'wishlist'
            elif type == 'new':
                url = query+'new'
            else:
                url = query+'&q='+type

            page = stnetwork.tryConnect(url).content
            points = int(bs(page, 'html.parser').find('span', class_="nav__points").text)
            level = int(''.join(filter(str.isdigit, bs(page, 'html.parser').find('span', class_=None).text)))
            giveawaySet = getGiveaways(page)

            for index in range(len(giveawaySet['Name'])):
                if points == 0: break
                if points >= giveawaySet['Points'][index]:
                    data = {}
                    gvpage = stnetwork.tryConnect('http://steamgifts.com'+giveawaySet['Query'][index]).content
                    form = bs(gvpage, 'html.parser').find('form')
                    for inputs in form.findAll('input'):
                        data.update({inputs['name']:inputs['value']})
                    LOGGER.debug("pageData: %s", data)
                    formData = {'xsrf_token': data['xsrf_token'], 'do': 'entry_insert', 'code': data['code']}
                    LOGGER.debug("formData: %s", formData)
                    stnetwork.tryConnect('http://www.steamgifts.com/ajax.php', data=formData)
                    points -= giveawaySet['Points'][index]

                    LOGGER.info("Spent %d points in the giveaway of %s (Copies: %d)",
                                                                    giveawaySet['Points'][index],
                                                                    giveawaySet['Name'][index],
                                                                    giveawaySet['Copies'][index])
                else:
                    LOGGER.debug("Ignoring %s bacause the account don't have the requirements to enter.", giveawaySet['Name'][index])

                LOGGER.debug("C(%d) L(%d) ML(%d) P(%d) MP(%d) Q(%s)",
                                                       giveawaySet['Copies'][index],
                                                       giveawaySet['Level'][index],
                                                       level,
                                                       giveawaySet['Points'][index],
                                                       points,
                                                       giveawaySet['Query'][index])

            #except Exception:
            #LOGGER.error("An error occured for url %s", url)
            #LOGGER.error("Please, check if it's a valid url.")
            #LOGGER.debug('', exc_info=True)

        LOGGER.debug("Remaining points: %d", points)

        randomstart = randint(CONFIG.getint('Config', 'minTime', fallback=7000),
                              CONFIG.getint('Config', 'maxTime', fallback=7300))

        stlogger.cfixer('\r')
        for i in range(0, randomstart):
            stlogger.cmsg("Waiting: {:4d} seconds".format(randomstart-i), end='\r')
            sleep(1)
