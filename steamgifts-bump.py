#!/usr/bin/env python
# Lara Maia <dev@lara.click> 2015

from time import sleep
from datetime import datetime
from bs4 import BeautifulSoup as bs
from random import randint
import requests
import stconfig
import os, sys
from signal import signal, SIGINT

config = stconfig.init(os.path.splitext(sys.argv[0])[0]+'.config')

try:
    cookie = {'PHPSESSID': config.get('CONFIG', 'Cookie')}
    agent = {'user-agent': 'unknown/0.0.0'}
    links = [l.strip() for l in config.get('CONFIG', 'Links').split(',')]
    minTime = config.getint('CONFIG', 'minTime')
    maxTime = config.getint('CONFIG', 'maxTime')
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

def timer():
    randomstart = randint(minTime, maxTime)
    for i in range(0, randomstart):
        print("Waiting: {:4d} seconds".format(randomstart-i), end="\r")
        sleep(1)

def signal_handler(signal, frame):
    print("Exiting...")
    exit(0)

def bump():
    data = {}

    print("Bumping now! {}".format(datetime.now()))

    for url in links:
        print("Connecting to the server", end="\r")
        page = tryConnect(url, cookies=cookie).content

        try:
            form = bs(page, 'html.parser').find('form')
            for inputs in form.findAll('input'):
                data.update({inputs['name']:inputs['value']})

            postData = {'xsrf_token': data['xsrf_token'], 'do': 'bump_trade'}
            tryConnect(url, data=postData, cookies=cookie)

            print("Bumped {}".format(url))
        except Exception:
            print("An error occured for url {}".format(url), file=sys.stderr)
            print("Please, check if it's a valid url.", file=sys.stderr)

signal(SIGINT, signal_handler)

while True:
    bump()
    timer()
