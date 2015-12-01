#!/usr/bin/env python
# Lara Maia <dev@lara.click> 2015

from bs4 import BeautifulSoup as bs
import requests
import configparser
import os, sys

config = configparser.RawConfigParser()
configfile = os.path.join(os.getenv('XDG_CONFIG_HOME', os.path.expanduser('~/.config')), 'steamgifts-join.config')

if os.path.isfile(configfile):
    config.read(configfile)
elif os.path.isfile('steamgifts-join.config'):
    config.read('steamgifts-join.config')
else:
    print("Configuration file not found at {}".format(configfile), file=sys.stderr)
    print("Please, copy the example file or create a new with your data.", file=sys.stderr)
    exit(1)

try:
    cookie = {'PHPSESSID': config.get('CONFIG', 'Cookie')}
    agent = {'user-agent': 'unknown/0.0.0'}
except(configparser.NoOptionError, configparser.NoSectionError):
    print("Incorrect data. Please, check your config file.", file=sys.stderr)
    exit(1)

def tryConnect(url, cookies, data=False):
    for loops in range(0 , 4):
        try:
            if data:
                return requests.post(url, data=data, cookies=cookies, headers=agent, timeout=10)
            else:
                return requests.get(url, cookies=cookies, headers=agent, timeout=10)
        except requests.exceptions.TooManyRedirects:
            print("Too many redirects. Please, check your configuration.", file=sys.stderr)
            print("(Invalid cookie?)", file=sys.stderr)
            exit(1)
        except requests.exceptions.RequestException:
            print("The connection is refused or fails. Trying again...")
            sleep(3)

    print("Cannot access the internet! Please, check your internet connection.", file=sys.stderr)
    exit(1)

def join():
    data = {}

    url = 'http://www.steamgifts.com/giveaways/search?type=wishlist'

    print("Connecting to the server")
    page = tryConnect(url, cookies=cookie).content

    try:
        giveawayList = []
        container = bs(page, 'html.parser').find('div', class_='widget-container')
        for div in container.findAll('div', class_=None):
            if div.find('div', class_='giveaway__row-outer-wrap'):
                giveawayList.append(div)

        for giveaway in giveawayList[1].findAll('div', class_='giveaway__row-outer-wrap'):
            gameName = giveaway.find('a', class_='giveaway__heading__name').text
            gameURL = giveaway.find('a', class_='giveaway__heading__name')['href']
            gamePoints = giveaway.find('span', class_='giveaway__heading__thin').text

            try:
                gameLevel = giveaway.find('div', class_='giveaway__column--contributor-level').text
            except AttributeError:
                gameLevel = "Level 0+"

            if giveaway.find('div', class_='giveaway__column--contributor-level--negative'):
                gameCanEnter = "CanEnter: No"
            else:
                gameCanEnter = "CanEnter: Yes"

            ### STUB ###
            print(gameName)
            print(gameURL)
            print(gamePoints)
            print(gameLevel)
            print(gameCanEnter)

            print('\n')

        print(' *** Hey, don\'t use this yet! ***\n\n')
        ### STUB ###

    except Exception as e:
        print(e, file=sys.stderr)

join()
