#!/usr/bin/env python
# Lara Maia <dev@lara.click> 2015

from gevent.pool import Pool
import gevent.monkey

import sys
import requests
from time import sleep

gevent.monkey.patch_socket()
agent = {'user-agent': 'unknown/0.0.0'}

def spamGet(url_list):
    def fetch(url):
        for loops in range(0, 4):
            try:
                ret.append(float(requests.get(url, timeout=10).text))
            except requests.exceptions.ReadTimeout:
                print("The connection is slow. Trying again in 5 secs...")
                sleep(5)

    ret = []
    pool = Pool(50)
    for url in url_list:
        pool.spawn(fetch, url)
    pool.join()
    return ret

def tryConnect(url, cookies="", data=False):
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
