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
import sys

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
        stlib.logger.error('Steam login status: Cookies not found' +
                                '\nPlease, check if you are logged in on' +
                                '\nsteampowered.com or steamcommunity.com')


def check_steamgifts_login(greenlet):
    try:
        html = bs4.BeautifulSoup(greenlet.value.content, 'html.parser')
        form = html.findAll('form')[1]
        stlib.SG_user = form.find('input', {'name': 'username'}).get('value')
    except(AttributeError, IndexError):
        stlib.SG_user = None
        stlib.logger.error('SteamGifts login status: Cookies not found' +
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
        stlib.logger.error('SteamCompanion login status: Cookies not found' +
                                '\nPlease, check if you are logged in on' +
                                '\nsteamcompanion.com')


def connect(service_name, url):
    greenlet = gevent.Greenlet(stlib.network.try_get_response, service_name, url)
    greenlet.link(eval(''.join(['ui.logins.check_', service_name, '_login'])))
    greenlet.start()
    greenlet.join()

    return greenlet


class Status:
    def __init__(self):
        self.window = ui.main_window

    def __toggle_start_active(self, pages, state):
        for page in pages:
            if self.window.tabs.get_current_page() == page:
                self.window.start.set_sensitive(state)

    def __steam_callback(self, greenlet):
        check_steam_login(greenlet)

        if stlib.steam_user:
            self.window.steam_login_status.set_from_file(os.path.join(self.window.icons_path,
                                                                      self.window.steam_icon_available))
            self.window.steam_login_status.set_tooltip_text("Steam Login status:\n" +
                                                            "Connected as {}".format(stlib.steam_user))
            steam_connected = True
        else:
            self.window.steam_login_status.set_from_file(os.path.join(self.window.icons_path,
                                                                      self.window.steam_icon_unavailable))
            self.window.steam_login_status.set_tooltip_text("Steam Login status: Cookies not found" +
                                                            "\nPlease, check if you are logged in on" +
                                                            "\nsteampowered.com or steamcommunity.com")
            steam_connected = False

        self.__toggle_start_active([0, 1], steam_connected)

    def __steamgifts_callback(self, greenlet):
        check_steamgifts_login(greenlet)

        if stlib.SG_user:
            self.window.SG_login_status.set_from_file(os.path.join(self.window.icons_path,
                                                                   self.window.steamgifts_icon_available))
            self.window.SG_login_status.set_tooltip_text("SteamGifts Login status:\n" +
                                                         "Connected as {}".format(stlib.SG_user))
            steamgifts_connected = True
        else:
            self.window.SG_login_status.set_from_file(os.path.join(self.window.icons_path,
                                                                   self.window.steamgifts_icon_unavailable))
            self.window.SG_login_status.set_tooltip_text("SteamGifts Login status: Cookies not found" +
                                                         "\nPlease, check if you are logged in on" +
                                                         "\nwww.steamgifts.com")
            steamgifts_connected = False

        self.__toggle_start_active([2, 3], steamgifts_connected)

    def __steamcompanion_callback(self, greenlet):
        check_steamcompanion_login(greenlet)

        if stlib.SC_user:
            self.window.SC_login_status.set_from_file(os.path.join(self.window.icons_path,
                                                                   self.window.steamcompanion_icon_available))
            self.window.SC_login_status.set_tooltip_text("SteamCompanion Login status:\n" +
                                                         "Connected as {}".format(stlib.SC_user)
                                                         )
            steamcompanion_connected = True
        else:
            self.window.SC_login_status.set_from_file(os.path.join(self.window.icons_path,
                                                                   self.window.steamcompanion_icon_unavailable))
            self.window.SC_login_status.set_tooltip_text("SteamCompanion Login status: Cookies not found" +
                                                         "\nPlease, check if you are logged in on" +
                                                         "\nsteamcompanion.com")
            steamcompanion_connected = False

        self.__toggle_start_active([4], steamcompanion_connected)

    def queue_connect(self, service_name, url):
        greenlet = gevent.Greenlet(stlib.network.try_get_response, service_name, url)
        class_name = self.__class__.__name__
        callback_function = ''.join(['_', class_name, '__', service_name, '_callback'])
        greenlet.link(eval(''.join(['self.', callback_function])))
        greenlet.start()

        return None

    def wait_queue(self):
        greenlets = []
        for object_ in gc.get_objects():
            if isinstance(object_, gevent.Greenlet):
                greenlets.append(object_)

        while True:
            if not ui.main_window:
                sys.exit(0)

            try:
                if greenlets[-1].ready():
                    greenlets.pop()
                else:
                    while ui.Gtk.events_pending():
                        ui.Gtk.main_iteration()

                    gevent.sleep(0.1)
            except IndexError:
                break
