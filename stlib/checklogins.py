#!/usr/bin/env python
#
# Lara Maia <dev@lara.click> 2015 ~ 2016
#
# The Steam Tools is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# The Steam Tools is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see http://www.gnu.org/licenses/.
#

from threading import Thread
from bs4 import BeautifulSoup as bs

from stlib import stnetwork2 as stnetwork

class checkLogins(Thread):
    def __init__(self, parent):
        Thread.__init__(self)
        self.stwindow = parent
        self.sLoginConnected = False
        self.sgLoginConnected = False
        self.scLoginConnected = False

    def check_steam_login(self):
        self.stwindow.statusBar.push(0, "Checking if you are logged in on Steam...")
        self.stwindow.sLoginStatus.set_from_file("icons/steam_yellow.png")
        loginPage = 'https://store.steampowered.com/login/checkstoredlogin/?redirectURL=about'
        response = stnetwork.getResponse(loginPage)

        try:
            if type(response) == int:
                raise AttributeError

            user = bs(response.content, 'html.parser').find('a', class_='username').text.strip()
            self.stwindow.sLoginStatus.set_from_file("icons/steam_green.png")
            self.stwindow.sLoginStatus.set_tooltip_text("Steam Login status:\nConnected as {}".format(user))
            self.sLoginConnected = True
        except(AttributeError, IndexError):
            self.stwindow.sLoginStatus.set_from_file("icons/steam_red.png")
            self.stwindow.sLoginStatus.set_tooltip_text("Steam Login status: Cookies not found"+
                                               "\nPlease, check if you are logged in on"+
                                               "\nsteampowered.com or steamcommunity.com")
            self.sLoginConnected = False

        self.stwindow.statusBar.pop(0)

    def check_steamgifts_login(self):
        self.stwindow.statusBar.push(0, "Checking if you are logged in on SteamGifts...")
        self.stwindow.sgLoginStatus.set_from_file("icons/sg_yellow.png")
        loginPage = 'https://www.steamgifts.com/account/profile/sync'
        response = stnetwork.getResponse(loginPage)

        try:
            if type(response) == int:
                raise AttributeError

            data = {}
            form = bs(response.content, 'html.parser').findAll('form')[1]
            user = form.find('input', {'name': 'username'}).get('value')
            self.stwindow.sgLoginStatus.set_from_file("icons/sg_green.png")
            self.stwindow.sgLoginStatus.set_tooltip_text("SteamGifts Login status:\nConnected as {}".format(user))
            self.sgLoginConnected = True
        except(AttributeError, IndexError):
            self.stwindow.sgLoginStatus.set_from_file("icons/sg_red.png")
            self.stwindow.sgLoginStatus.set_tooltip_text("SteamGifts Login status: Cookies not found"+
                                               "\nPlease, check if you are logged in on"+
                                               "\nwww.steamgifts.com")
            self.sgLoginConnected = False

        self.stwindow.statusBar.pop(0)

    def check_steamcompanion_login(self):
        self.stwindow.statusBar.push(0, "Checking if you are logged in on SteamCompanion...")
        self.stwindow.scLoginStatus.set_from_file("icons/sc_yellow.png")
        loginPage = 'https://steamcompanion.com/settings'
        response = stnetwork.getResponse(loginPage)

        try:
            if type(response) == int:
                raise AttributeError

            user = bs(response.content, 'html.parser').find('div', class_='profile').find('a').text.strip()
            self.stwindow.scLoginStatus.set_from_file("icons/sc_green.png")
            self.stwindow.scLoginStatus.set_tooltip_text("SteamCompanion Login status:\nConnected as {}".format(user))
            self.scLoginConnected = True
        except(AttributeError, IndexError):
            self.stwindow.scLoginStatus.set_from_file("icons/sc_red.png")
            self.stwindow.scLoginStatus.set_tooltip_text("SteamCompanion Login status: Cookies not found"+
                                               "\nPlease, check if you are logged in on"+
                                               "\nsteamcompanion.com")
            self.scLoginConnected = False

        self.stwindow.statusBar.pop(0)

    def run(self):
        self.check_steam_login()
        self.check_steamgifts_login()
        self.check_steamcompanion_login()
