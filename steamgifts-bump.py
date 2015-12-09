#!/usr/bin/env python
# Lara Maia <dev@lara.click> 2015

from time import sleep
from datetime import datetime
from bs4 import BeautifulSoup as bs
from random import randint
import os, sys
from signal import signal, SIGINT

import stconfig
from stnetwork import tryConnect

config = stconfig.init(os.path.splitext(sys.argv[0])[0]+'.config')

try:
    cookie = {'PHPSESSID': config.get('CONFIG', 'Cookie')}
    links = [l.strip() for l in config.get('CONFIG', 'Links').split(',')]
    minTime = config.getint('CONFIG', 'minTime')
    maxTime = config.getint('CONFIG', 'maxTime')
except(configparser.NoOptionError, configparser.NoSectionError):
    print("Incorrect data. Please, check your config file.", file=sys.stderr)
    exit(1)

def signal_handler(signal, frame):
    print("Exiting...")
    exit(0)

if __name__ == "__main__":
    signal(SIGINT, signal_handler)

    while True:
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

        randomstart = randint(minTime, maxTime)
        for i in range(0, randomstart):
            print("Waiting: {:4d} seconds".format(randomstart-i), end="\r")
            sleep(1)
