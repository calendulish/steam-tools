#!/usr/bin/env python
# Lara Maia <dev@lara.click> 2015

import sys
import requests
from time import sleep

import gevent
import gevent.monkey

gevent.monkey.patch_socket()
agent = {'user-agent': 'unknown/0.0.0'}

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
                print("Too manu redirects. Please, check your configuration.", file=sys.stderr)
                exit(1)
            except requests.exceptions.RequestException:
                print("The connection is slow. Trying again in 5 secs...")
                sleep(5)

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
            print("Too many redirects. Please, check your configuration.", file=sys.stderr)
            print("(Invalid cookie?)", file=sys.stderr)
            exit(1)
        except requests.exceptions.RequestException:
            print("The connection is refused or fails. Trying again...")
            sleep(3)

    print("Cannot access the internet! Please, check your internet connection.", file=sys.stderr)
    exit(1)
