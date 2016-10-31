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
import sys

import bs4
import gevent

import stlib
import ui

if stlib.gui_mode:
    import gi

    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk


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


def check_steamtrades_login(greenlet):
    try:
        html = bs4.BeautifulSoup(greenlet.value.content, 'html.parser')
        avatar = html.find('a', class_='nav_avatar')

        if not avatar:
            raise AttributeError

        user_id = avatar['href'].split('/')[2]
        # FIXME: get username from steamapi
        stlib.ST_user = user_id
    except(AttributeError, IndexError):
        stlib.ST_user = None
        stlib.logger.error('SteamTrades login status: Cookies not found' +
                           '\nPlease, check if you are logged in on' +
                           '\nwww.steamtrades.com')


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


def queue_connect(service_name, callback=None, wait=False):
    if not callback:
        callback = eval(''.join(['check_', service_name, '_login']))

    url = eval(''.join(['stlib.', service_name, '_check_page']))

    greenlet = gevent.Greenlet(stlib.network.try_get_response, service_name, url)
    greenlet.link(callback)
    greenlet.start()

    if wait:
        try:
            greenlet.join()
        except KeyboardInterrupt:
            sys.exit(0)

    return greenlet


def get_queue():
    greenlets = []

    for object_ in gc.get_objects():
        if isinstance(object_, gevent.Greenlet):
            greenlets.append(object_)

    return greenlets


def wait_queue(greenlets=None):
    if not greenlets:
        greenlets = get_queue()

    try:
        while True:
            # Kill all greenlets before exit
            if not ui.main_window.get_window():
                raise SystemExit

            try:
                if greenlets[-1].ready():
                    greenlets.pop()
                else:
                    if stlib.gui_mode:
                        while Gtk.events_pending():
                            Gtk.main_iteration()

                    gevent.sleep(0.1)
            except IndexError:
                break
    except(KeyboardInterrupt, SystemExit):
        for greenlet in greenlets:
            greenlet.kill()

        sys.exit(0)
