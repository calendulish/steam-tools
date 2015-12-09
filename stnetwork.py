#!/usr/bin/env python
# Lara Maia <dev@lara.click> 2015

import sys
import requests
from time import sleep

agent = {'user-agent': 'unknown/0.0.0'}

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
