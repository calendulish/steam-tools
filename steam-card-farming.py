#!/usr/bin/env python
# Lara Maia <dev@lara.click> 2015

import configparser
import requests
from bs4 import BeautifulSoup as bs
from time import sleep
import os
import subprocess

config = configparser.RawConfigParser()
configfile = os.path.join(os.getenv('XDG_CONFIG_HOME'), 'steam-card-farming.config')

if os.path.isfile(configfile):
    config.read(configfile)
else:
    print("Configuration file not found at {}".format(configfile))
    print("Please, copy the example file or create a new with your data.")
    exit(1)

try:
    cookies = {'sessionid': config.get('COOKIES', 'SessionID'), 'steamLogin': config.get('COOKIES', 'SteamLogin')}
    profile = "http://steamcommunity.com/id/" + config.get('UserInfo', 'ProfileName')
    sort = config.getboolean('CONFIG', 'MostValuableFirst')
except(configparser.NoOptionError, configparser.NoSectionError):
    print("Incorrect data. Please, check your config file.")
    exit(1)

def tryGet(url, cookies):
    loops = 0
    while True:
        try:
            return requests.get(url, cookies=cookies)
        except requests.exceptions.TooManyRedirects:
            print("Too many redirects. Please, check your configuration.")
            print("(Invalid cookie?)")
            exit(1)
        except requests.exceptions.RequestException:
            loops += 1
            if loops > 3:
                print("Cannot access the internet! Please, check your internet connection.")
                exit(1)
            else:
                print("The connection is refused or fails. Trying again...")
                sleep(3)


print("Digging your badge list...")
fullPage = tryGet(profile+"/badges/", cookies=cookies).content
pageCount = bs(fullPage, 'lxml').findAll('a', class_='pagelink')
if pageCount:
    currentPage = 1
    badges = []
    while currentPage <= int(pages[-1].text):
        page = tryGet(profile+"/badges/?p="+str(currentPage), cookies=cookies).content
        badges += bs(page, 'lxml').findAll('div', class_='badge_title_row')
        currentPage += 1
else:
    badges = bs(fullPage, 'lxml').findAll('div', class_='badge_title_row')

if not badges:
    print("Something is wrong! (Invalid profile name?)")
    exit(1)

print("Checking if we are logged.")
if not bs(fullPage, 'lxml').findAll('div', class_='profile_xp_block_right'):
    print("You are not logged into steam! (Invalid cookies?)")
    exit(1)

print("Gettings badges info...", end='\r')
badgeSet = []
cardsValue = 0.0
count = 0
for badge in badges:
    count += 1
    if sort:
        print("Getting badges info and cards values... {} %".format(int((count/len(badges))*100)), end='\r')
    cardsCount = badge.find('span', class_='progress_info_bold')
    if not cardsCount or "No" in cardsCount.text: continue
    cardsCount = int(cardsCount.text.split(' ', 3)[0])
    gameId = badge.find('a')['href'].split('/', 3)[3]
    gameName = badge.find('div', class_='badge_title')
    gameName.span.unwrap()
    gameName = gameName.text.split('\t\t\t\t\t\t\t\t\t', 2)[1]
    if sort:
        cardsValue = float(tryGet("http://api.enhancedsteam.com/market_data/average_card_price/?appid="+gameId+"&cur=usd").text)
    badgeSet.append([gameName, gameId, cardsCount, cardsValue])

if sort:
    badgeSet = sorted(badgeSet, key=lambda badge: badge[3], reverse=True)

print("\nReady to start.")
for gameName, gameId, cardsCount, cardsValue in badgeSet:
    print("Starting game {} ({})".format(gameName, gameId))
    fakeApp = subprocess.Popen(['python', 'fake-steam-app.py', gameId], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    while True:
        print("{:2d} cards drop remaining. Waiting... {:7s}".format(cardsCount, ' '), end='\r')
        sleep(60)
        print("Checking if game have more cards drops...", end='\r')
        badge = tryGet(profile+"/gamecards/"+gameId, cookies=cookies).content
        cardsCount = bs(badge, 'lxml').find('span', class_="progress_info_bold")
        if not cardsCount or "No" in cardsCount.text:
            print("The game has no more cards to drop.{:8s}".format(' '), end='')
            break
        else:
            cardsCount = int(cardsCount.text.split(' ', 3)[0])

    print("\nClosing {}".format(gameName))
    fakeApp.terminate()
    fakeApp.wait()

print("There's nothing else we can do. Leaving.")
exit(0)
