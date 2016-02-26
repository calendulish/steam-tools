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
import subprocess
from time import sleep
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
    cookies = config._sections['Cookies']
    sort = config.getboolean('Config', 'MostValuableFirst')
    icheck = config.getboolean('Debug', "IntegrityCheck")
    dryrun = config.getboolean('Debug', "DryRun")
except(NoOptionError, NoSectionError):
    logger.critical("Incorrect data. (Updated with the new options?)")
    logger.critical("Please, check your config file.")
    logger.debug('', exc_info=True)
    exit(1)

def signal_handler(signal, frame):
    stlogger.cfixer()
    logger.info("Exiting...")
    exit(0)

if __name__ == "__main__":
    signal(SIGINT, signal_handler)

    stlogger.cmsg("Searching for your username...", end='\r')
    loginPage = tryConnect(configFile, 'http://store.steampowered.com/about/').content
    username = bs(loginPage, 'html.parser').find('a', class_='username').text.strip()
    profile = "http://steamcommunity.com/id/"+username
    stlogger.cmsg("Hello {}!{:25s}!".format(username, ''), end='\r')
    stlogger.cfixer()

    logger.info("Digging your badge list...")
    fullPage = tryConnect(configFile, profile+"/badges/").content
    pageCount = bs(fullPage, 'html.parser').findAll('a', class_='pagelink')
    if pageCount:
        logger.debug("I found %d pages of badges", pages[-1].text)
        badges = []
        for currentPage in range(1, int(pages[-1].text)):
            page = tryConnect(configFile, profile+"/badges/?p="+str(currentPage)).content
            badges += bs(page, 'html.parser').findAll('div', class_='badge_title_row')
    else:
        logger.debug("I found only 1 pages of badges")
        badges = bs(fullPage, 'html.parser').findAll('div', class_='badge_title_row')

    if not badges:
        logger.critical("Something is very wrong! Please report with the log file")
        logger.debug(fullPage)
        exit(1)

    logger.info("Getting badges info...")
    badgeSet = {}
    badgeSet['gameID'   ] = []
    badgeSet['gameName' ] = []
    badgeSet['cardCount'] = []
    badgeSet['cardValue'] = []
    for badge in badges:
        progress = badge.find('span', class_='progress_info_bold')
        title = badge.find('div', class_='badge_title')
        title.span.unwrap()

        if not progress or "No" in progress.text:
            logger.debug("%s have no cards to drop. Ignoring.", title.text.split('\t\t\t\t\t\t\t\t\t', 2)[1])
            continue

        badgeSet['cardCount'].append(int(progress.text.split(' ', 3)[0]))
        badgeSet['gameID'].append(badge.find('a')['href'].split('/', 3)[3])
        badgeSet['gameName'].append(title.text.split('\t\t\t\t\t\t\t\t\t', 2)[1])

    if sort:
        logger.info("Getting cards values...")
        pricesSet = {}
        pricesSet['game'] = []
        pricesSet['avg'] = []
        pricesPage = tryConnect(configFile, "http://www.steamcardexchange.net/index.php?badgeprices").content
        for game in bs(pricesPage, 'html.parser').findAll('tr')[1:]:
            pricesSet['game'].append(game.find('a').text)
            pricesSet['avg'].append(float(game.find('td').findNext('td').findNext('td').text[1:]))

        badgeSet['cardValue'] = [ pricesSet['avg'][pricesSet['game'].index(game)] for game in badgeSet['gameName'] ]
    else:
        badgeSet['cardValue'] = [ 0 for _ in badgeSet['gameID'] ]

    if icheck:
        logger.debug("Checking consistency of dictionaries...")
        rtest = [ len(badgeSet[i]) for i,v in badgeSet.items() ]
        if len(set(rtest)) == 1:
            logger.debug("Looks good.")
        else:
            logger.debug("Very strange: %s", rtest)
            exit(1)

    if sort:
        logger.info("Getting highest card value...")
        if icheck: logger.debug("OLD: %s", badgeSet)
        order = sorted(range(0, len(badgeSet['cardValue'])), key=lambda key: badgeSet['cardValue'][key], reverse=True)
        for item, value in badgeSet.items():
            badgeSet[item] = [value[i] for i in order]
        if icheck:
            logger.debug("NEW: %s", badgeSet)

    logger.info("Ready to start.")
    for index in range(0, len(badgeSet['gameID'])):
        stlogger.cfixer()
        logger.info("Starting game %s (%s)", badgeSet['gameName'][index], badgeSet['gameID'][index])
        if not dryrun:
            fakeApp = subprocess.Popen(['python', 'fake-steam-app.py', badgeSet['gameID'][index]], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        while True:
            stlogger.cmsg("{:2d} cards drop remaining. Waiting... {:7s}".format(badgeSet['cardCount'][index], ' '), end='\r')
            logger.debug("Waiting cards drop loop")
            if icheck: logger.debug("Current: %s", [badgeSet[i][index] for i,v in badgeSet.items()])
            for i in range(0, 30):
                if not dryrun and fakeApp.poll():
                    stlogger.cfixer()
                    logger.critical(fakeApp.stderr.read().decode('utf-8'))
                    exit(1)
                sleep(1)

            stlogger.cmsg("Checking if game have more cards drops...", end='\r')
            logger.debug("Updating cards count")
            if icheck: logger.debug("OLD: %d", badgeSet['cardCount'][index])
            badge = tryConnect(configFile, profile+"/gamecards/"+badgeSet['gameID'][index]).content
            badgeSet['cardCount'][index] = bs(badge, 'html.parser').find('span', class_="progress_info_bold")
            if icheck: logger.debug("NEW: %d", badgeSet['cardCount'][index])
            if dryrun: badgeSet['cardCount'][index] = ""
            if not badgeSet['cardCount'][index] or "No" in badgeSet['cardCount'][index].text:
                stlogger.cfixer()
                logger.info("The game has no more cards to drop.")
                break
            else:
                badgeSet['cardCount'][index] = int(badgeSet['cardCount'][index].text.split(' ', 3)[0])

        logger.info("Closing %s", badgeSet['gameName'][index])
        if not dryrun:
            fakeApp.terminate()
            fakeApp.wait()

    logger.info("There's nothing else we can do. Leaving.")
