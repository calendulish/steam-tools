#!/usr/bin/env python
# Lara Maia <dev@lara.click> 2015

import requests
from bs4 import BeautifulSoup as bs
from time import sleep
import os, sys
from signal import signal, SIGINT
import subprocess

import stlogger
import stconfig
from stnetwork import tryConnect, spamConnect

logger = stlogger.init(os.path.splitext(sys.argv[0])[0]+'.log')
config = stconfig.init(os.path.splitext(sys.argv[0])[0]+'.config')

try:
    cookies = {'sessionid': config.get('COOKIES', 'SessionID'), 'steamLogin': config.get('COOKIES', 'SteamLogin')}
    profile = "http://steamcommunity.com/id/" + config.get('UserInfo', 'ProfileName')
    sort = config.getboolean('CONFIG', 'MostValuableFirst')
except(configparser.NoOptionError, configparser.NoSectionError):
    logger.critical("Incorrect data. Please, check your config file.")
    exit(1)

def signal_handler(signal, frame):
    print("\n")
    logger.info("Exiting...")
    exit(0)

if __name__ == "__main__":
    signal(SIGINT, signal_handler)

    logger.info("Digging your badge list...")
    fullPage = tryConnect(profile+"/badges/", cookies=cookies).content
    pageCount = bs(fullPage, 'html.parser').findAll('a', class_='pagelink')
    if pageCount:
        badges = []
        for currentPage in range(1, int(pages[-1].text)):
            page = tryConnect(profile+"/badges/?p="+str(currentPage), cookies=cookies).content
            badges += bs(page, 'html.parser').findAll('div', class_='badge_title_row')
    else:
        badges = bs(fullPage, 'html.parser').findAll('div', class_='badge_title_row')

    if not badges:
        logger.critical("Something is wrong! (Invalid profile name?)")
        exit(1)

    logger.info("Checking if we are logged.")
    if not bs(fullPage, 'html.parser').findAll('div', class_='profile_xp_block_right'):
        logger.critical("You are not logged into steam! (Invalid cookies?)")
        exit(1)

    logger.info("Getting badges info...")
    badgeSet = {}
    badgeSet['gameID'   ] = []
    badgeSet['gameName' ] = []
    badgeSet['cardCount'] = []
    badgeSet['cardURL'  ] = []
    badgeSet['cardValue'] = []
    for badge in badges:
        progress = badge.find('span', class_='progress_info_bold')
        title = badge.find('div', class_='badge_title')
        title.span.unwrap()

        if not progress or "No" in progress.text: continue

        badgeSet['cardCount'].append(int(progress.text.split(' ', 3)[0]))
        badgeSet['gameID'].append(badge.find('a')['href'].split('/', 3)[3])
        badgeSet['gameName'].append(title.text.split('\t\t\t\t\t\t\t\t\t', 2)[1])
        badgeSet['cardURL'].append("http://api.enhancedsteam.com/market_data/average_card_price/?appid="+badgeSet['gameID'][-1]+"&cur=usd")

    logger.info("Getting cards values...")
    badgeSet['cardValue'] = [float(v) for v in spamConnect('text', badgeSet['cardURL'])]

    if sort:
        order = sorted(range(0, len(badgeSet['cardValue'])), key=lambda key: badgeSet['cardValue'][key], reverse=True)
        for item, value in badgeSet.items():
            badgeSet[item] = [value[i] for i in order]

    logger.info("Ready to start.")
    for index in range(0, len(badgeSet['gameID'])):
        logger.info("Starting game {} ({})".format(badgeSet['gameName'][index], badgeSet['gameID'][index]))
        fakeApp = subprocess.Popen(['python', 'fake-steam-app.py', badgeSet['gameID'][index]], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        while True:
            print("{:2d} cards drop remaining. Waiting... {:7s}".format(badgeSet['cardCount'][index], ' '), end='\r')
            for i in range(0, 60):
                if fakeApp.poll():
                    print("\n")
                    logger.critical(fakeApp.stderr.read().decode('utf-8'))
                    exit(1)
                sleep(1)

            print("Checking if game have more cards drops...", end='\r')
            badge = tryConnect(profile+"/gamecards/"+badgeSet['gameID'][index], cookies=cookies).content
            badgeSet['cardCount'][index] = bs(badge, 'html.parser').find('span', class_="progress_info_bold")
            if not badgeSet['cardCount'][index] or "No" in badgeSet['cardsCount'][index].text:
                print("\n")
                logger.info("The game has no more cards to drop.)
                break
            else:
                badgeSet['cardCount'][index] = int(badgeSet['cardCount'][index].text.split(' ', 3)[0])

        logger.info("Closing {}".format(badgeSet['gameName'][index]))
        fakeApp.terminate()
        fakeApp.wait()

    logger.info("There's nothing else we can do. Leaving.")
