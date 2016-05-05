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

CONFIG = stconfig.getParser()
LOGGER = stlogger.getLogger(CONFIG.get('Debug', 'logFileLevel', fallback='verbose'))

mostValuableFirst = CONFIG.getboolean('Config', 'MostValuableFirst', fallback=True)
dryRun = CONFIG.getboolean('Debug', "DryRun", fallback=False)

def signal_handler(signal, frame):
    stlogger.cfixer()
    LOGGER.warning("Exiting...")
    sys.exit(0)

def getBadges(profile):
    fullPage = stnetwork.tryConnect(profile+"/badges/").content
    html = bs(fullPage, 'html.parser')
    badges = []

    try:
        pageCount = int(html.findAll('a', class_='pagelink')[-1].text)
        LOGGER.verbose("I found %d pages of badges", pageCount)
        for currentPage in range(1, pageCount):
            page = stnetwork.tryConnect(profile+"/badges/?p="+str(currentPage)).content
            badges.append(bs(page, 'html.parser').findAll('div', class_='badge_title_row'))
    except IndexError:
        LOGGER.verbose("I found only 1 pages of badges")
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

def updateCardCount(profile, gameID):
    LOGGER.verbose("Updating card count")

    for i in range(5):
        page = stnetwork.tryConnect(profile+"/gamecards/"+gameID).content
        pageData = bs(page, 'html.parser')
        stats = pageData.find('div', class_="badge_title_stats_drops")

        if stats:
            progress = stats.find('span', class_="progress_info_bold")
            if not progress or "No" in progress.text or dryRun:
                return 0
            else:
                return int(progress.text.split(' ', 3)[0])
        else:
            LOGGER.warning("Something is wrong with the page, trying again")
            sleep(3)

    LOGGER.error("I cannot find the progress info for this badge. (Connection problem?)")
    LOGGER.error("I'll jump to the next this time and try again later.")
    return 0

def findFakeSteamApp():
    paths = os.path.dirname(os.path.abspath(sys.argv[0]))+os.pathsep+os.environ['PATH']

    for path in paths.split(os.pathsep):
        for ext in [ '', '.exe', '.py' ]:
            fullPath = os.path.join(path, 'fake-steam-app'+ext)

            if os.path.isfile(fullPath):
                return fullPath

    LOGGER.critical("I cannot find the fake-steam-app. Please, verify your installation.")
    sys.exit(1)

if __name__ == "__main__":
    signal(SIGINT, signal_handler)

    stlogger.cmsg("Searching for your username...", end='\r')
    loginPage = stnetwork.tryConnect('https://store.steampowered.com/login/checkstoredlogin/?redirectURL=about').content
    username = bs(loginPage, 'html.parser').find('a', class_='username').text.strip()
    profile = "https://steamcommunity.com/login/checkstoredlogin/?redirectURL=id/"+username

    stlogger.cfixer('\r')
    stlogger.cmsg("Hello {}!".format(username))
    stlogger.cfixer()
    LOGGER.info("Getting badges info...")
    badgeSet = getBadges(profile)

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

    if mostValuableFirst:
        LOGGER.info("Getting highest card value...")
        LOGGER.trace("OLD: %s", badgeSet)

        order = sorted(range(0, len(badgeSet['cardValue'])), key=lambda key: badgeSet['cardValue'][key], reverse=True)

        for item, value in badgeSet.items():
            badgeSet[item] = [value[i] for i in order]

        LOGGER.trace("NEW: %s", badgeSet)

    LOGGER.warning("Ready to start.")
    for index in range(0, len(badgeSet['gameID'])):
        if badgeSet['cardCount'][index] < 1:
            LOGGER.verbose("%s have no cards to drop. Ignoring.", badgeSet['gameName'][index])
            continue

        stlogger.cfixer()
        LOGGER.info("Starting game %s (%s)", badgeSet['gameName'][index], badgeSet['gameID'][index])
        if not dryRun:
            fakeAppPath = findFakeSteamApp()
            fakeAppExec = [fakeAppPath, badgeSet['gameID'][index]]

            if fakeAppPath[-3:] != 'exe':
                fakeAppExec = ['python']+fakeAppExec

            fakeApp = Popen(fakeAppExec, stdout=PIPE, stderr=PIPE)


        while True:
            stlogger.cmsg("{:2d} cards drop remaining. Waiting...".format(badgeSet['cardCount'][index]), end='\r')
            LOGGER.verbose("Waiting cards drop loop")
            LOGGER.trace("Current: %s", [badgeSet[i][index] for i,v in badgeSet.items()])

            for i in range(40):
                if not dryRun and fakeApp.poll():
                    stlogger.cfixer()
                    LOGGER.critical(fakeApp.stderr.read().decode('utf-8'))
                    sys.exit(1)
                sleep(1)
            stlogger.cfixer('\r')

            stlogger.cmsg("Checking if game have more cards drops...", end='\r')
            badgeSet['cardCount'][index] = updateCardCount(profile, badgeSet['gameID'][index])

            if badgeSet['cardCount'][index] < 1:
                stlogger.cfixer('\r')
                LOGGER.warning("No more cards to drop.")
                break
            stlogger.cfixer('\r')

        LOGGER.info("Closing %s", badgeSet['gameName'][index])

        if not dryRun:
            fakeApp.terminate()
            fakeApp.wait()

    LOGGER.warning("There's nothing else we can do. Leaving.")
