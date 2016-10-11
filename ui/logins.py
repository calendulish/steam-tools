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

import gc
import os

import bs4
import gevent

import stlib
import ui


def check_steam_login(greenlet):
    try:
        html = bs4.BeautifulSoup(greenlet.value.content, 'html.parser')
        supernav = html.find('div', class_='supernav_container')
        stlib.steam_user = supernav.find('a', class_='username').text.strip()
    except(AttributeError, IndexError):
        stlib.steam_user = None
        ui.globals.logger.error('Steam login status: Cookies not found' +
                                '\nPlease, check if you are logged in on' +
                                '\nsteampowered.com or steamcommunity.com')


def check_steamgifts_login(greenlet):
    try:
        html = bs4.BeautifulSoup(greenlet.value.content, 'html.parser')
        form = html.findAll('form')[1]
        stlib.SG_user = form.find('input', {'name': 'username'}).get('value')
    except(AttributeError, IndexError):
        stlib.SG_user = None
        ui.globals.logger.error('SteamGifts login status: Cookies not found' +
                                '\nPlease, check if you are logged in on' +
                                '\nwww.steamgifts.com')


def check_steamcompanion_login(greenlet):
    try:
        html = bs4.BeautifulSoup(greenlet.value.content, 'html.parser')
        user = html.find('div', class_='profile').find('a').text.strip()

        if not user:
            raise AttributeError

        stlib.SC_user = user
    except(AttributeError, IndexError):
        stlib.SC_user = None
        ui.globals.logger.error('SteamCompanion login status: Cookies not found' +
                                '\nPlease, check if you are logged in on' +
                                '\nsteamcompanion.com')

class Status:
    def __init__(self):
        self.window = ui.globals.Window.main
        self.steam_connected = False
        self.steamgifts_connected = False
        self.steamcompanion_connected = False

    def __steam_callback(self, greenlet):
        check_steam_login(greenlet)

        if stlib.steam_user:
            self.window.steam_login_status.set_from_file(os.path.join(self.window.icons_path,
                                                                      self.window.steam_icon_available))
            self.window.steam_login_status.set_tooltip_text("Steam Login status:\n" +
                                                            "Connected as {}".format(stlib.steam_user))
            self.steam_connected = True
        else:
            self.window.steam_login_status.set_from_file(os.path.join(self.window.icons_path,
                                                                      self.window.steam_icon_unavailable))
            self.window.steam_login_status.set_tooltip_text("Steam Login status: Cookies not found" +
                                                            "\nPlease, check if you are logged in on" +
                                                            "\nsteampowered.com or steamcommunity.com")
            self.steam_connected = False

    def __steamgifts_callback(self, greenlet):
        check_steamgifts_login(greenlet)

        if stlib.SG_user:
            self.window.SG_login_status.set_from_file(os.path.join(self.window.icons_path,
                                                                   self.window.steamgifts_icon_available))
            self.window.SG_login_status.set_tooltip_text("SteamGifts Login status:\n" +
                                                         "Connected as {}".format(stlib.SG_user))
            self.steamgifts_connected = True
        else:
            self.window.SG_login_status.set_from_file(os.path.join(self.window.icons_path,
                                                                   self.window.steamgifts_icon_unavailable))
            self.window.SG_login_status.set_tooltip_text("SteamGifts Login status: Cookies not found" +
                                                         "\nPlease, check if you are logged in on" +
                                                         "\nwww.steamgifts.com")
            self.steamgifts_connected = False

    def __steamcompanion_callback(self, greenlet):
        check_steamcompanion_login(greenlet)

        if stlib.SC_user:
            self.window.SC_login_status.set_from_file(os.path.join(self.window.icons_path,
                                                                   self.window.steamcompanion_icon_available))
            self.window.SC_login_status.set_tooltip_text("SteamCompanion Login status:\n" +
                                                         "Connected as {}".format(stlib.SC_user)
                                                         )
            self.steamcompanion_connected = True
        else:
            self.window.SC_login_status.set_from_file(os.path.join(self.window.icons_path,
                                                                   self.window.steamcompanion_icon_unavailable))
            self.window.SC_login_status.set_tooltip_text("SteamCompanion Login status: Cookies not found" +
                                                         "\nPlease, check if you are logged in on" +
                                                         "\nsteamcompanion.com")
            self.steamcompanion_connected = False

    def queue_connect(self, service_name, url):
        greenlet = gevent.Greenlet(stlib.network.try_get_response, service_name, url)
        class_name = self.__class__.__name__
        callback_function = ''.join(['_', class_name, '__', service_name, '_callback'])
        greenlet.link(eval(''.join(['self.', callback_function])))
        greenlet.start()

    def wait_queue(self):
        greenlets = []
        for object_ in gc.get_objects():
            if isinstance(object_, gevent.Greenlet):
                greenlets.append(object_)

        while True:
            try:
                if greenlets[-1].ready():
                    greenlets.pop()
                else:
                    while ui.Gtk.events_pending():
                        ui.Gtk.main_iteration()
                    gevent.sleep(0.1)
            except IndexError:
                break
