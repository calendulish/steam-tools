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

CONFIG = stconfig.getParser()
LOGGER = stlogger.getLogger(CONFIG.get('Debug', 'logFileLevel', fallback='verbose'))

try:
    TYPELIST = [l.strip() for l in CONFIG.get('Config', 'typeList').split(',')]
except(NoOptionError, NoSectionError):
    TYPELIST = [ 'wishlist', 'single', 'raffle' ]
    CONFIG.set('Config', 'typeList', "wishlist, single")
    LOGGER.warning("No typeList found in the config file.")
    LOGGER.warning("Using the default: wishlist, single. You can edit these values.")

def signal_handler(signal, frame):
    stlogger.cfixer()
    LOGGER.warning("Exiting...")
    sys.exit(0)

def getGiveaways(page):
    giveaways = []
    # STUB: pinned ?
    container = bs(page, 'html.parser').find('section', class_='col-2-3')

    giveaways += container.findAll('div', class_='giveaway-links')
    giveawaySet = {k: [] for k in ['Name', 'Query', 'Copies', 'Points']}

    for giveaway in giveaways:
        try:
            # Already joined.
            giveaway['style']
            continue
        except KeyError:
            pass

        infoRaw = giveaway.find('p', class_='game-name')
        infoArray = infoRaw.text.split('\t\t\t\t\t\t\t\t\t')

        try:
            infoType = infoRaw.find('a').find('span', class_='has-tip')['title']

            if 'Contributor' or 'Group' in infoType:
                # FIXME: Ignore all Contributor/Group giveaways for now
                LOGGER.verbose("Ignoring {} giveaway".format(infoType))
                continue
        except TypeError:
            pass

        if not infoArray[0][1:]:
            infoArray = infoArray[1:]

        gvName = infoArray[0][1:].split('(')[0][:-1]
        try:
            giveawaySet['Copies'].append(int(infoRaw.find('span', class_='copies').text[:-1]))
            gvName = ''.join(gvName.split(' ')[1:])
            LOGGER.verbose("The giveaway %s has more than 1 copy. Counting and fixing gvName.", gvName)
        except AttributeError:
            giveawaySet['Copies'].append(1)

        giveawaySet['Name'].append(gvName)

        try:
            giveawaySet['Points'].append(int(infoArray[0][1:].split('(')[-1][:-3]))
        except:
            giveawaySet['Points'].append(int(infoArray[1][1:].split('(')[-1][:-3]))

        giveawaySet['Query'].append(giveaway['data-href'])

        # STUB: gameLevel ?

    return giveawaySet

if __name__ == "__main__":
    signal(SIGINT, signal_handler)

    while True:
        for type in TYPELIST:
            stlogger.cmsg("Connecting to the server", end='\r')
            query = "https://steamcompanion.com/gifts/search/?state=open&type=all&games=you"
            if type == 'main':
                url = query
            elif type == 'wishlist':
                url = query+'&wishlist=true'
            elif type == 'single':
                url = query+'&mode=single'
            elif type == 'raffle':
                url = query+'&mode=raffle'
            else:
                url = query+'&search='+type

            for pageNumber in range(1, CONFIG.getint('Config', 'maxPages', fallback=5)):
                if pageNumber != 1:
                    try:
                        pagination = bs(page, 'html.parser').find('ul', class_="pagination").text
                        if points == 0 or not "Next" in pagination:
                            break
                    except AttributeError:
                        # Only the first page
                        break

                LOGGER.verbose("Checking page %d", pageNumber)

                page = stnetwork.tryConnect(url+'&page='+str(pageNumber)).content
                points = int(bs(page, 'html.parser').find('span', class_="points").text)
                giveawaySet = getGiveaways(page)

                for index in range(len(giveawaySet['Name'])):
                    if points >= giveawaySet['Points'][index]:
                        data = {}
                        gvPage = stnetwork.tryConnect(giveawaySet['Query'][index]).content
                        form = bs(gvPage, 'html.parser').find('form')

                        try:
                            for inputs in form.findAll('input'):
                                data.update({inputs['name']:inputs['value']})
                        except AttributeError:
                            LOGGER.verbose("Ignoring %s because you don't have the requirements to enter.", giveawaySet['Name'][index])
                            LOGGER.verbose("(Missing base Game?)")
                            continue

                        formData = { 'script': 'enter',
                                     'hashID': giveawaySet['Query'][index].split('/')[4],
                                     'token': '',
                                     'action': 'enter_giveaway'}

                        response = stnetwork.tryConnect('https://steamcompanion.com/gifts/steamcompanion.php',
                                                        data=formData, headers={'X-Requested-With': 'XMLHttpRequest'})

                        points -= giveawaySet['Points'][index]

                        LOGGER.info("Spent %d points in the giveaway of %s (Copies: %d)",
                                                                        giveawaySet['Points'][index],
                                                                        giveawaySet['Name'][index],
                                                                        giveawaySet['Copies'][index])

                        if points == 0:
                            break

                        sleep(randint(5, 20))
                    else:
                        LOGGER.verbose("Ignoring %s bacause you don't have points to enter.", giveawaySet['Name'][index])

                    LOGGER.trace("C(%d) P(%d) MP(%d) Q(%s)",
                                            giveawaySet['Copies'][index],
                                            giveawaySet['Points'][index],
                                            points,
                                            giveawaySet['Query'][index])

        randomstart = randint(CONFIG.getint('Config', 'minTime', fallback=7000),
                              CONFIG.getint('Config', 'maxTime', fallback=7300))

        stlogger.cfixer('\r')
        for i in range(0, randomstart):
            stlogger.cmsg("Waiting: {:4d} seconds".format(randomstart-i), end='\r')
            sleep(1)
