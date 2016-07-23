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

import stlib
import ui


def check_steam_login():
    ui.globals.logger.info("Checking if you are logged in on Steam...")
    login_page = 'https://store.steampowered.com/login/checkstoredlogin/?redirectURL=about'
    html = stlib.network.try_get_html('steam', login_page)

    try:
        ui.globals.Logins.steam_user = html.find('a', class_='username').text.strip()
    except(AttributeError, IndexError):
        ui.globals.Logins.steam_user = None
        ui.globals.logger.error('Steam login status: Cookies not found' +
                                '\nPlease, check if you are logged in on' +
                                '\nsteampowered.com or steamcommunity.com')


def check_steamgifts_login():
    login_page = 'https://www.steamgifts.com/account/profile/sync'
    html = stlib.network.try_get_html('steamGifts', login_page)

    try:
        form = html.findAll('form')[1]
        ui.globals.Logins.steamgifts_user = form.find('input', {'name': 'username'}).get('value')
    except(AttributeError, IndexError):
        ui.globals.Logins.steam_user = None
        ui.globals.logger.error('SteamGifts login status: Cookies not found' +
                                '\nPlease, check if you are logged in on' +
                                '\nwww.steamgifts.com')


def check_steamcompanion_login():
    html = stlib.network.try_get_html('steamCompanion', 'https://steamcompanion.com/settings')

    try:
        user = html.find('div', class_='profile').find('a').text.strip()

        if not user:
            raise AttributeError

        ui.globals.Logins.steamcompanion_user = user
    except(AttributeError, IndexError):
        ui.globals.Logins.steamcompanion_user = None
        ui.globals.logger.error('SteamCompanion login status: Cookies not found' +
                                '\nPlease, check if you are logged in on' +
                                '\nsteamcompanion.com')


class CheckStatus(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.window = ui.globals.Window.main
        self.steam_connected = False
        self.steamgifts_connected = False
        self.steamcompanion_connected = False

    def steam_login_status(self):
        status_context = self.window.update_status_bar("Checking if you are logged in on Steam...")
        self.window.steam_login_status.set_from_file(os.path.join(self.window.icons_path, self.window.steam_icon_busy))

        check_steam_login()

        if ui.globals.Logins.steam_user:
            self.window.steam_login_status.set_from_file(os.path.join(self.window.icons_path,
                                                                      self.window.steam_icon_available))
            self.window.steam_login_status.set_tooltip_text("Steam Login status:\n" +
                                                            "Connected as {}".format(ui.globals.Logins.steam_user))
            self.steam_connected = True
        else:
            self.window.steam_login_status.set_from_file(os.path.join(self.window.icons_path,
                                                                      self.window.steam_icon_unavailable))
            self.window.steam_login_status.set_tooltip_text("Steam Login status: Cookies not found" +
                                                            "\nPlease, check if you are logged in on" +
                                                            "\nsteampowered.com or steamcommunity.com")
            self.steam_connected = False

        self.window.status_bar.pop(status_context)

    def SG_login_status(self):
        status_context = self.window.update_status_bar("Checking if you are logged in on SteamGifts...")
        self.window.SG_login_status.set_from_file(os.path.join(self.window.icons_path,
                                                               self.window.steamgifts_icon_busy))

        check_steamgifts_login()

        if ui.globals.Logins.steamgifts_user:
            self.window.SG_login_status.set_from_file(os.path.join(self.window.icons_path,
                                                                   self.window.steamgifts_icon_available))
            self.window.SG_login_status.set_tooltip_text("SteamGifts Login status:\n" +
                                                         "Connected as {}".format(ui.globals.Logins.steamgifts_user))
            self.steamgifts_connected = True
        else:
            self.window.SG_login_status.set_from_file(os.path.join(self.window.icons_path,
                                                                   self.window.steamgifts_icon_unavailable))
            self.window.SG_login_status.set_tooltip_text("SteamGifts Login status: Cookies not found" +
                                                         "\nPlease, check if you are logged in on" +
                                                         "\nwww.steamgifts.com")
            self.steamgifts_connected = False

        self.window.status_bar.pop(status_context)

    def SC_login_status(self):
        status_context = self.window.update_status_bar("Checking if you are logged in on SteamCompanion...")
        self.window.SC_login_status.set_from_file(os.path.join(self.window.icons_path,
                                                               self.window.steamcompanion_icon_busy))

        check_steamcompanion_login()

        if ui.globals.Logins.steamcompanion_user:
            self.window.SC_login_status.set_from_file(os.path.join(self.window.icons_path,
                                                                   self.window.steamcompanion_icon_available))
            self.window.SC_login_status.set_tooltip_text("SteamCompanion Login status:\n" +
                                                         "Connected as {}".format(ui.globals.Logins.steamcompanion_user)
                                                         )
            self.steamcompanion_connected = True
        else:
            self.window.SC_login_status.set_from_file(os.path.join(self.window.icons_path,
                                                                   self.window.steamcompanion_icon_unavailable))
            self.window.SC_login_status.set_tooltip_text("SteamCompanion Login status: Cookies not found" +
                                                         "\nPlease, check if you are logged in on" +
                                                         "\nsteamcompanion.com")
            self.steamcompanion_connected = False

        self.window.status_bar.pop(status_context)

    def run(self):
        self.steam_login_status()
        self.SG_login_status()
        self.SC_login_status()
