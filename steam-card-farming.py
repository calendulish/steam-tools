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
from subprocess import Popen, PIPE
from time import sleep
from signal import signal, SIGINT
from configparser import NoOptionError, NoSectionError
from bs4 import BeautifulSoup as bs

from stlib import stlogger
from stlib import stconfig
from stlib import stnetwork
from stlib import stcygwin

LOGGER = stlogger.getLogger()
CONFIG = stconfig.getParser()

mostValuableFirst = CONFIG.getboolean('Config', 'MostValuableFirst', fallback=True)
integrityCheck = CONFIG.getboolean('Debug', "IntegrityCheck", fallback=False)
dryRun = CONFIG.getboolean('Debug', "DryRun", fallback=False)

def signal_handler(signal, frame):
    stlogger.cfixer()
    LOGGER.info("Exiting...")
    sys.exit(0)

def getBadges():
    fullPage = stnetwork.tryConnect(profile+"/badges/").content
    html = bs(fullPage, 'html.parser')
    badges = []

    try:
        pageCount = int(html.findAll('a', class_='pagelink')[-1].text)
        LOGGER.debug("I found %d pages of badges", pageCount)
        for currentPage in range(1, pageCount):
            page = stnetwork.tryConnect(profile+"/badges/?p="+str(currentPage)).content
            badges.append(bs(page, 'html.parser').findAll('div', class_='badge_title_row'))
    except IndexError:
        LOGGER.debug("I found only 1 pages of badges")
        badges = html.findAll('div', class_='badge_title_row')

    badgeSet = {k: [] for k in ['gameID', 'gameName', 'cardCount', 'cardValue']}
    for badge in badges:
        progress = badge.find('span', class_='progress_info_bold')
        title = badge.find('div', class_='badge_title')
        title.span.unwrap()

        if not progress or "No" in progress.text:
            try:
                badgeSet['gameID'].append(badge.find('a')['href'].split('_')[-3])
            except(TypeError, IndexError):
                # Ignore. It's an special badge (not from games/apps)
                continue
            badgeSet['cardCount'].append(0)
        else:
            badgeSet['cardCount'].append(int(progress.text.split(' ', 3)[0]))
            badgeSet['gameID'].append(badge.find('a')['href'].split('/', 3)[3])

        badgeSet['gameName'].append(title.text.split('\t\t\t\t\t\t\t\t\t', 2)[1])

    return badgeSet

def getValues():
    priceSet = {k: [] for k in ['game', 'avg']}
    pricesPage = stnetwork.tryConnect("http://www.steamcardexchange.net/index.php?badgeprices").content
    for game in bs(pricesPage, 'html.parser').findAll('tr')[1:]:
        priceSet['game'].append(game.find('a').text)
        cardCount = int(game.findAll('td')[1].text)
        cardPrice = float(game.findAll('td')[2].text[1:])
        priceSet['avg'].append(cardPrice / cardCount)

    return priceSet

def updateCardCount(gameID):
    LOGGER.debug("Updating card count")

    page = stnetwork.tryConnect(profile+"/gamecards/"+gameID).content
    progress = bs(page, 'html.parser').find('span', class_="progress_info_bold")
    if not progress or "No" in progress.text or dryRun:
        return 0
    else:
        return int(progress.text.split(' ', 3)[0])

if __name__ == "__main__":
    signal(SIGINT, signal_handler)

    stlogger.cmsg("Searching for your username...", end='\r')
    loginPage = stnetwork.tryConnect('http://store.steampowered.com/about/').content
    username = bs(loginPage, 'html.parser').find('a', class_='username').text.strip()
    profile = "http://steamcommunity.com/id/"+username

    stlogger.cfixer('\r')
    stlogger.cmsg("Hello {}!".format(username))
    stlogger.cfixer()
    LOGGER.info("Getting badges info...")
    badgeSet = getBadges()

    if mostValuableFirst:
        LOGGER.info("Getting cards values...")
        priceSet = getValues()
        for game in badgeSet['gameName']:
            try:
                badgeSet['cardValue'].append(priceSet['avg'][priceSet['game'].index(game)])
            except ValueError:
                badgeSet['cardValue'].append(0)
    else:
        badgeSet['cardValue'] = [ 0 for _ in badgeSet['gameID'] ]

    if integrityCheck:
        LOGGER.debug("Checking consistency of dictionaries...")
        rtest = [ len(badgeSet[i]) for i,v in badgeSet.items() ]
        if len(set(rtest)) == 1:
            LOGGER.debug("Looks good.")
        else:
            LOGGER.debug("Very strange: %s", rtest)
            sys.exit(1)

    if mostValuableFirst:
        LOGGER.info("Getting highest card value...")
        if integrityCheck: LOGGER.debug("OLD: %s", badgeSet)
        order = sorted(range(0, len(badgeSet['cardValue'])), key=lambda key: badgeSet['cardValue'][key], reverse=True)
        for item, value in badgeSet.items():
            badgeSet[item] = [value[i] for i in order]
        if integrityCheck:
            LOGGER.debug("NEW: %s", badgeSet)

    LOGGER.info("Ready to start.")
    for index in range(0, len(badgeSet['gameID'])):
        if badgeSet['cardCount'][index] < 1:
            LOGGER.debug("%s have no cards to drop. Ignoring.", badgeSet['gameName'][index])
            continue

        stlogger.cfixer()
        LOGGER.info("Starting game %s (%s)", badgeSet['gameName'][index], badgeSet['gameID'][index])
        if not dryRun:
            if os.path.isfile('fake-steam-app.exe'):
                fakeApp = Popen(['fake-steam-app.exe', badgeSet['gameID'][index]], stdout=PIPE, stderr=PIPE)
            else:
                fakeApp = Popen(['python', 'fake-steam-app.py', badgeSet['gameID'][index]], stdout=PIPE, stderr=PIPE)

        while True:
            stlogger.cmsg("{:2d} cards drop remaining. Waiting...".format(badgeSet['cardCount'][index]), end='\r')
            LOGGER.debug("Waiting cards drop loop")
            if integrityCheck: LOGGER.debug("Current: %s", [badgeSet[i][index] for i,v in badgeSet.items()])
            for i in range(40):
                if not dryRun and fakeApp.poll():
                    stlogger.cfixer()
                    LOGGER.critical(fakeApp.stderr.read().decode('utf-8'))
                    sys.exit(1)
                sleep(1)
            stlogger.cfixer('\r')
            stlogger.cmsg("Checking if game have more cards drops...", end='\r')
            badgeSet['cardCount'][index] = updateCardCount(badgeSet['gameID'][index])

            if badgeSet['cardCount'][index] < 1:
                stlogger.cfixer()
                LOGGER.info("%s have no cards to drop. Ignoring.", badgeSet['gameName'][index])
                break
            stlogger.cfixer('\r')

        LOGGER.info("Closing %s", badgeSet['gameName'][index])

        if not dryRun:
            fakeApp.terminate()
            fakeApp.wait()

    LOGGER.info("There's nothing else we can do. Leaving.")
