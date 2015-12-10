#!/usr/bin/env python
# Lara Maia <dev@lara.click> 2015

import os
from sys import argv
from time import sleep
from datetime import datetime
from random import randint
from signal import signal, SIGINT
from configparser import NoOptionError, NoSectionError
from bs4 import BeautifulSoup as bs

import stlogger
import stconfig
from stnetwork import tryConnect

logger = stlogger.init(os.path.splitext(argv[0])[0]+'.log')
config = stconfig.init(os.path.splitext(argv[0])[0]+'.config')

try:
    cookie = {'PHPSESSID': config.get('CONFIG', 'Cookie')}
    links = [l.strip() for l in config.get('CONFIG', 'Links').split(',')]
    minTime = config.getint('CONFIG', 'minTime')
    maxTime = config.getint('CONFIG', 'maxTime')
except(NoOptionError, NoSectionError):
    logger.critical("Incorrect data. Please, check your config file.")
    exit(1)

def signal_handler(signal, frame):
    print("\n")
    logger.info("Exiting...")
    exit(0)

if __name__ == "__main__":
    signal(SIGINT, signal_handler)

    while True:
        data = {}

        logger.info("Bumping now! {}".format(datetime.now()))

        for url in links:
            print("Connecting to the server", end="\r")
            page = tryConnect(url, cookies=cookie).content

            try:
                form = bs(page, 'html.parser').find('form')
                for inputs in form.findAll('input'):
                    data.update({inputs['name']:inputs['value']})

                postData = {'xsrf_token': data['xsrf_token'], 'do': 'bump_trade'}
                tryConnect(url, data=postData, cookies=cookie)

                logger.info("Bumped {}".format(url))
            except Exception:
                logger.error("An error occured for url {}".format(url))
                logger.error("Please, check if it's a valid url.")

        randomstart = randint(minTime, maxTime)
        for i in range(0, randomstart):
            print("Waiting: {:4d} seconds".format(randomstart-i), end="\r")
            sleep(1)
