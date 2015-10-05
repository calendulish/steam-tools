#!/usr/bin/env python
# Lara Maia <dev@lara.click> 2015
# TODO: external config file with parser

from time import sleep
from datetime import datetime
from bs4 import BeautifulSoup as bs
from random import randint
import requests

#### CONFIG ####

cookie = {'PHPSESSID': '473824825792389534795236472374623568234'}
links = [ "http://www.example.com/link1", "http://www.example.com/link2" ]

################

def timer():
    maxStart = 4100
    minStart = 3700
    randomstart = randint(minStart, maxStart)
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
