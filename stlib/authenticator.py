#!/usr/bin/env python
#
# Lara Maia <dev@lara.click> 2016
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

import base64
import codecs
import tempfile
import hashlib
import hmac
import io
import json
import locale
import os
import tarfile
import time
import subprocess
import xml.etree.ElementTree
import zlib

import requests
from bs4 import BeautifulSoup as bs

import stlib
import ui

if stlib.gui_mode:
    import gi

    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk

STEAM_ALPHABET = ['2', '3', '4', '5', '6', '7', '8', '9',
                  'B', 'C', 'D', 'F', 'G', 'H', 'J', 'K',
                  'M', 'N', 'P', 'Q', 'R', 'T', 'V', 'W',
                  'X', 'Y']


def __run_adb(params):
    data = subprocess.check_output(
        [stlib.SA_adb_path ] + params,
        stderr=subprocess.STDOUT
    )

    return data.decode(locale.getpreferredencoding())


def __get_data_from_authenticator(path):
    try:
        data = __run_adb([
            'shell',
            'su -c "cat {}"'.format(os.path.join(stlib.SA_auth_path, path))
        ])
    except subprocess.CalledProcessError:
        stlib.logger.error('Unable to get data from %s', path)

        return None

    if 'No such file' in data:
        stlib.logger.critical('Something wrong with the Steam Mobile App.')

        return None

    return data


def __get_server_time():
    query_time_url = 'https://api.steampowered.com/ITwoFactorService/QueryTime/v1'
    response = stlib.network.get_response(query_time_url, empty_post=True)
    server_time = int(response.json()['response']['server_time'])

    return server_time + response.elapsed.seconds

def phone_exists():
    try:
        __run_adb(['shell', 'true'])
    except subprocess.CalledProcessError:
        return False
    else:
        return True


def phone_is_rooted():
    try:
        data = __run_adb(['shell', 'su', '-c', 'true'])
    except subprocess.CalledProcessError:
        return False
    else:
        return True


def get_userid(nickname):
    response = stlib.network.get_response('{}/{}/?{}={}'.format(stlib.api_query_uri,
                                                                'steamid',
                                                                'nickname',
                                                                 nickname))
    return response.content


def get_code(secret):
    server_time = __get_server_time()
    msg = int(server_time / 30).to_bytes(8, 'big')
    key = base64.b64decode(secret)
    auth = hmac.new(key, msg, hashlib.sha1)
    digest = auth.digest()
    start = digest[19] & 0xF
    code = digest[start:start + 4]
    auth_code_raw = int(codecs.encode(code, 'hex'), 16) & 0x7FFFFFFF

    auth_code = []
    for i in range(5):
        auth_code.append(STEAM_ALPHABET[int(auth_code_raw % len(STEAM_ALPHABET))])
        auth_code_raw /= len(STEAM_ALPHABET)

    return ''.join(auth_code), server_time


def get_secret(type_):
    for i in range(2):
        try:
            data = __get_data_from_authenticator('files/Steamguard-*')
            return json.loads(data)[type_]
        except (ValueError, TypeError, KeyError):
            stlib.logger.verbose('Unable to get {}. Trying again.'.format(type_))
            time.sleep(1)

    stlib.logger.verbose('Unable to get the {}.'.format(type_))

    return None


def get_device_id():
    data = __get_data_from_authenticator('shared_prefs/steam.uuid.xml')

    if data:
        return xml.etree.ElementTree.fromstring(data)[0].text
    else:
        return None


def create_time_hash(time, tag, secret):
    key = base64.b64decode(secret)
    msg = time.to_bytes(8, 'big') + codecs.encode(tag)
    auth = hmac.new(key, msg, hashlib.sha1)
    code = base64.b64encode(auth.digest())

    return codecs.decode(code)


def get_trades(secret, cookies):
    server_time = __get_server_time()

    payload = {'p':get_device_id(),
               'a':get_key('steamid'),
               'k':create_time_hash(server_time, 'conf', secret),
               't':server_time,
               'm':'android',
               'tag':'conf'}

    response = requests.get('https://steamcommunity.com/mobileconf/conf',
                            params=payload,
                            cookies=cookies)

    page = bs(response.content, 'html.parser')

    trades = {k:[] for k in ['accept', 'cancel', 'trade_id', 'trade_key', 'description']}
    for item in page.findAll('div', class_='mobileconf_list_entry'):
        trades['accept'].append(item['data-accept'])
        trades['cancel'].append(item['data-cancel'])
        trades['trade_id'].append(item['data-confid'])
        trades['trade_key'].append(item['data-key'])
        trades['description'].append(str(item.find('div', class_='mobileconf_list_entry_description')).strip())

    return trades


def finalize_trade(cookies, secret, trade_id, trade_key, do='cancel'):
    server_time = __get_server_time()

    payload = {'p':get_device_id(),
               'a':get_key('steamid'),
               'k':create_time_hash(server_time, 'conf', secret),
               't':server_time,
               'm':'android',
               'tag':'conf',
               'cid':trade_id,
               'ck':trade_key,
               'op':do}

    response = requests.get('https://steamcommunity.com/mobileconf/ajaxop',
                            params=payload,
                            cookies=cookies)

    response.raise_for_status()

    return response
