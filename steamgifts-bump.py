#!/usr/bin/env python
# Lara Maia <dev@lara.click> 2015

from time import sleep
from datetime import datetime
from bs4 import BeautifulSoup as bs
from random import randint
import requests
import configparser
import os, sys

config = configparser.RawConfigParser()
configfile = os.path.join(os.getenv('XDG_CONFIG_HOME'), 'steamgifts-bump.config')

if os.path.isfile(configfile):
    config.read(configfile)
else:
    print("Configuration file not found at {}".format(configfile), file=sys.stderr)
    print("Please, copy the example file or create a new with your data.", file=sys.stderr)
    exit(1)

try:
    cookie = {'PHPSESSID': config.get('CONFIG', 'Cookie')}
    links = [l.strip() for l in config.get('CONFIG', 'Links').split(',')]
    minTime = config.getint('CONFIG', 'minTime')
    maxTime = config.getint('CONFIG', 'maxTime')
except(configparser.NoOptionError, configparser.NoSectionError):
    print("Incorrect data. Please, check your config file.", file=sys.stderr)
    exit(1)

def tryConnect(url, cookies, data=False):
    loops = 0
    while True:
        try:
            if data:
                return requests.post(url, data=data, cookies=cookies)
            else:
                return requests.get(url, cookies=cookies)
        except requests.exceptions.TooManyRedirects:
            print("Too many redirects. Please, check your configuration.", file=sys.stderr)
            print("(Invalid cookie?)", file=sys.stderr)
            exit(1)
        except requests.exceptions.RequestException:
            loops += 1
            if loops > 3:
                print("Cannot access the internet! Please, check your internet connection.", file=sys.stderr)
                exit(1)
            else:
                print("The connection is refused or fails. Trying again...")
                sleep(3)

def timer():
    randomstart = randint(minTime, maxTime)
    i = 0
    while i < randomstart:
        i+=1
        print("Waiting: {:4d} seconds".format(randomstart-i), end="\r")
        sleep(1)

def bump():
    data = {}

    print("Bumping now! {}".format(datetime.now()))

    for url in links:
        print("Connecting to the server", end="\r")
        page = tryConnect(url, cookies=cookie).content

        try:
            form = bs(page, 'lxml').find('form')
            for inputs in form.findAll('input'):
                data.update({inputs['name']:inputs['value']})

            postData = {'xsrf_token': data['xsrf_token'], 'do': 'bump_trade'}
            tryConnect(url, data=postData, cookies=cookie)

            print("Bumped {}".format(url))
        except Exception:
            print("An error occured for url {}".format(url), file=sys.stderr)
            print("Please, check if it's a valid url.", file=sys.stderr)

while True:
    bump()
    timer()
