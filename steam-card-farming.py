#!/usr/bin/env python
# Lara Maia <dev@lara.click> 2015

import configparser
import requests
from bs4 import BeautifulSoup as bs
import os

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
except(configparser.NoOptionError):
    print("Incorrect data. Please, check your config file.")
    exit(1)

print("Digging your badge list...")
fullPage = requests.get(profile+"/badges/", cookies=cookies).content
pageCount = bs(fullPage, 'lxml').findAll('a', class_='pagelink')
if pageCount:
	currentPage = 1
	badges = []
	while currentPage <= int(pages[-1].text):
		page = requests.get(profile+"/badges/?p="+str(currentPage), cookies=cookies).content
		badges += bs(page, 'lxml').findAll('div', class_='badge_title_stats')
		currentPage += 1
else:
	badges = bs(fullPage, 'lxml').findAll('div', class_='badge_title_stats')

if not badges:
	print("Something is wrong! (Invalid profile name?)")
	exit(1)

print("Checking if we are logged.")
if not bs(fullPage, 'lxml').findAll('div', class_='profile_xp_block_right'):
	print("You are not logged into steam! (Invalid cookies?)")
	exit(1)

print("Counting Cards...")
for badge in badges:
	cardsCount = badge.find('span', class_='progress_info_bold')
	if not cardsCount or "No" in cardsCount.text: continue
	gameId = badge.find('a')['href'].split('/', 3)[3]
	print("GameId {} has {}".format(gameId, cardsCount.text))
