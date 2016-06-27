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

import os
from threading import Thread

from bs4 import BeautifulSoup as bs

import stlib


class CheckLogins(Thread):
    def __init__(self, window):
        Thread.__init__(self)
        self.window = window
        self.steam_connected = False
        self.steamgifts_connected = False
        self.steamcompanion_connected = False
        self.browser_bridge = stlib.cookie.BrowserBridge()
        self.network_session = stlib.network.Session()

    def check_steam_login(self):
        self.window.statusBar.push(0, "Checking if you are logged in on Steam...")
        self.window.sLoginStatus.set_from_file(os.path.join(self.window.icons_path, self.window.steam_icon_busy))
        loginPage = 'https://store.steampowered.com/login/checkstoredlogin/?redirectURL=about'
        # FIXME: Get cookies from config file
        cookies = self.browser_bridge.get_cookies(self.window.browser_profile, loginPage)
        self.network_session.update_cookies(cookies)
        response = self.network_session.get_response(loginPage)

        try:
            # FIXME
            if type(response) == int:
                raise AttributeError

            user = bs(response.content, 'html.parser').find('a', class_='username').text.strip()
            self.window.sLoginStatus.set_from_file(
                    os.path.join(self.window.icons_path, self.window.steam_icon_available))
            self.window.sLoginStatus.set_tooltip_text("Steam Login status:\nConnected as {}".format(user))
            self.steam_connected = True
        except(AttributeError, IndexError):
            self.window.sLoginStatus.set_from_file(
                    os.path.join(self.window.icons_path, self.window.steam_icon_unavailable))
            self.window.sLoginStatus.set_tooltip_text("Steam Login status: Cookies not found" +
                                                      "\nPlease, check if you are logged in on" +
                                                      "\nsteampowered.com or steamcommunity.com")
            self.steam_connected = False

        self.window.statusBar.pop(0)

    def check_steamgifts_login(self):
        self.window.statusBar.push(0, "Checking if you are logged in on SteamGifts...")
        self.window.sgLoginStatus.set_from_file(os.path.join(self.window.icons_path, self.window.steamgifts_icon_busy))
        loginPage = 'https://www.steamgifts.com/account/profile/sync'
        # FIXME: Get cookies from config file
        cookies = self.browser_bridge.get_cookies(self.window.browser_profile, loginPage)
        self.network_session.update_cookies(cookies)
        response = self.network_session.get_response(loginPage)

        try:
            # FIXME
            if type(response) == int:
                raise AttributeError

            data = {}
            form = bs(response.content, 'html.parser').findAll('form')[1]
            user = form.find('input', {'name':'username'}).get('value')
            self.window.sgLoginStatus.set_from_file(
                    os.path.join(self.window.icons_path, self.window.steamgifts_icon_available))
            self.window.sgLoginStatus.set_tooltip_text("SteamGifts Login status:\nConnected as {}".format(user))
            self.steamgifts_connected = True
        except(AttributeError, IndexError):
            self.window.sgLoginStatus.set_from_file(
                    os.path.join(self.window.icons_path, self.window.steamgifts_icon_unavailable))
            self.window.sgLoginStatus.set_tooltip_text("SteamGifts Login status: Cookies not found" +
                                                       "\nPlease, check if you are logged in on" +
                                                       "\nwww.steamgifts.com")
            self.steamgifts_connected = False

        self.window.statusBar.pop(0)

    def check_steamcompanion_login(self):
        self.window.statusBar.push(0, "Checking if you are logged in on SteamCompanion...")
        self.window.scLoginStatus.set_from_file(
                os.path.join(self.window.icons_path, self.window.steamcompanion_icon_busy))
        loginPage = 'https://steamcompanion.com/settings'
        # FIXME: Get cookies from config file
        cookies = self.browser_bridge.get_cookies(self.window.browser_profile, loginPage)
        self.network_session.update_cookies(cookies)
        response = self.network_session.get_response(loginPage)

        try:
            # FIXME
            if type(response) == int:
                raise AttributeError

            user = bs(response.content, 'html.parser').find('div', class_='profile').find('a').text.strip()

            if not user:
                raise AttributeError

            self.window.scLoginStatus.set_from_file(
                    os.path.join(self.window.icons_path, self.window.steamcompanion_icon_available))
            self.window.scLoginStatus.set_tooltip_text("SteamCompanion Login status:\nConnected as {}".format(user))
            self.steamcompanion_connected = True
        except(AttributeError, IndexError):
            self.window.scLoginStatus.set_from_file(
                    os.path.join(self.window.icons_path, self.window.steamcompanion_icon_unavailable))
            self.window.scLoginStatus.set_tooltip_text("SteamCompanion Login status: Cookies not found" +
                                                       "\nPlease, check if you are logged in on" +
                                                       "\nsteamcompanion.com")
            self.steamcompanion_connected = False

        self.window.statusBar.pop(0)

    def run(self):
        self.check_steam_login()
        self.check_steamgifts_login()
        self.check_steamcompanion_login()
