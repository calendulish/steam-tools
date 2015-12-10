#!/usr/bin/env python
# Lara Maia <dev@lara.click> 2015

import requests
from bs4 import BeautifulSoup as bs
from time import sleep
import os, sys
from signal import signal, SIGINT
import subprocess

import stconfig
from stnetwork import tryConnect, spamGet

config = stconfig.init(os.path.splitext(sys.argv[0])[0]+'.config')

try:
    cookies = {'sessionid': config.get('COOKIES', 'SessionID'), 'steamLogin': config.get('COOKIES', 'SteamLogin')}
    profile = "http://steamcommunity.com/id/" + config.get('UserInfo', 'ProfileName')
    sort = config.getboolean('CONFIG', 'MostValuableFirst')
except(configparser.NoOptionError, configparser.NoSectionError):
    print("Incorrect data. Please, check your config file.", file=sys.stderr)
    exit(1)

def signal_handler(signal, frame):
    print("Exiting...")
    exit(0)

if __name__ == "__main__":
    signal(SIGINT, signal_handler)

    print("Digging your badge list...")
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
        print("Something is wrong! (Invalid profile name?)", file=sys.stderr)
        exit(1)

    print("Checking if we are logged.")
    if not bs(fullPage, 'html.parser').findAll('div', class_='profile_xp_block_right'):
        print("You are not logged into steam! (Invalid cookies?)", file=sys.stderr)
        exit(1)

    print("Gettings badges info...", end='\r')
    badgeSet = []
    cardsCounts = []
    cardsUrls = []
    gamesId = []
    gamesName = []
    for badge in badges:
        cardsCount = badge.find('span', class_='progress_info_bold')
        if not cardsCount or "No" in cardsCount.text: continue
        cardsCount.append(int(cardsCount.text.split(' ', 3)[0]))
        gameId = badge.find('a')['href'].split('/', 3)[3]
        gamesId.append(gameId)
        gameName = badge.find('div', class_='badge_title')
        gameName.span.unwrap()
        gamesName.append(gameName.text.split('\t\t\t\t\t\t\t\t\t', 2)[1])
        cardsUrls.append("http://api.enhancedsteam.com/market_data/average_card_price/?appid="+gameId+"&cur=usd")

    cardsValue = spamGet(cardsUrls)
    for i in range(0, len(gamesId)):
        badgeSet.append([gamesName[i], gamesId[i], cardsCounts[i], cardsValue[i]])

    if sort:
        badgeSet = sorted(badgeSet, key=lambda badge: badge[3], reverse=True)

    print("\nReady to start.")
    for gameName, gameId, cardsCount, cardsValue in badgeSet:
        print("Starting game {} ({})".format(gameName, gameId))
        fakeApp = subprocess.Popen(['python', 'fake-steam-app.py', gameId], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        while True:
            print("{:2d} cards drop remaining. Waiting... {:7s}".format(cardsCount, ' '), end='\r')
            for i in range(0, 60):
                if fakeApp.poll():
                    print("\n{}".format(fakeApp.stderr.read().decode('utf-8)')), file=sys.stderr, end='')
                    exit(1)
                sleep(1)

            print("Checking if game have more cards drops...", end='\r')
            badge = tryConnect(profile+"/gamecards/"+gameId, cookies=cookies).content
            cardsCount = bs(badge, 'html.parser').find('span', class_="progress_info_bold")
            if not cardsCount or "No" in cardsCount.text:
                print("The game has no more cards to drop.{:8s}".format(' '), end='')
                break
            else:
                cardsCount = int(cardsCount.text.split(' ', 3)[0])

        print("\nClosing {}".format(gameName))
        fakeApp.terminate()
        fakeApp.wait()

    print("There's nothing else we can do. Leaving.")
