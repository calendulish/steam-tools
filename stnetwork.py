#!/usr/bin/env python
# Lara Maia <dev@lara.click> 2015

from time import sleep
from logging import getLogger

import requests
import gevent
import gevent.monkey

gevent.monkey.patch_socket()
agent = {'user-agent': 'unknown/0.0.0'}
logger = getLogger('root')

def spamConnect(rtype, url_list, cookies="", data=False):
    def fetch(url):
        for loops in range(0, 4):
            try:
                if data:
                    return requests.post(url, data=data, cookies=cookies, headers=agent, timeout=10)
                else:
                    response = requests.get(url, cookies=cookies, headers=agent, timeout=10)
                    if rtype == "response":
                        return response
                    elif rtype == "text":
                        return response.text
                    elif rtype == "content":
                        return response.content
            except requests.exceptions.TooManyRedirects:
                logger.critical("Too many redirects. Please, check your configuration.")
                logger.critical("(Invalid cookie?)")
                exit(1)
            except requests.exceptions.RequestException:
                logger.error("The connection is refused or fails. Trying again...")
                sleep(3)

    greenlet = []
    for url in url_list:
        greenlet.append(gevent.spawn(fetch, url))

    gevent.joinall(greenlet)
    return [v.value for v in greenlet]

def tryConnect(url, cookies="", data=False):
    for loops in range(0 , 4):
        try:
            if data:
                return requests.post(url, data=data, cookies=cookies, headers=agent, timeout=10)
            else:
                return requests.get(url, cookies=cookies, headers=agent, timeout=10)
        except requests.exceptions.TooManyRedirects:
            logger.critical("Too many redirects. Please, check your configuration.")
            logger.critical("(Invalid cookie?)")
            exit(1)
        except requests.exceptions.RequestException:
            logger.error("The connection is refused or fails. Trying again...")
            sleep(3)

    logger.critical("Cannot access the internet! Please, check your internet connection.")
    exit(1)
