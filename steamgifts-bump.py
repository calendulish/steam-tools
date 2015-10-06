#!/usr/bin/env python
# Lara Maia <dev@lara.click> 2015

from time import sleep
from datetime import datetime
from bs4 import BeautifulSoup as bs
from random import randint
import requests
import configparser
import os

from gi.repository import Gtk

config = configparser.ConfigParser()
configfile = os.path.join(os.getenv('XDG_CONFIG_HOME'), 'steamgifts-bump.config')

if os.path.isfile(configfile):
    config.read(configfile)
else:
    print("Configuration file not found at {}".format(configfile))
    print("Please, copy the example file or create a new with your data.")
    exit(1)

try:
    cookie = {'PHPSESSID': config.get('CONFIG', 'Cookie')}
    links = [l.strip() for l in config.get('CONFIG', 'Links').split(',')]
    minTime = config.get('CONFIG', 'minTime')
    maxTime = config.get('CONFIG', 'maxTime')
except(configparser.NoOptionError):
    print("Incorrect data. Please, check your config file.")
    exit(1)

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
        try:
            print("Connecting to the server", end="\r")
            page = requests.get(url, cookies=cookie).content
        except(requests.exceptions.TooManyRedirects):
            print("Too many redirects. Please, check your configuration.")
            print("(Invalid cookie?)")
            exit(1)

        form = bs(page, 'lxml').find('form')
        for inputs in form.findAll('input'):
                data.update({inputs['name']:inputs['value']})

        postData = {'xsrf_token': data['xsrf_token'], 'do': 'bump_trade'}
        requests.post(url, data=postData, cookies=cookie)

        print("Bumped {}".format(url))

while True:
    bump()
    timer()
