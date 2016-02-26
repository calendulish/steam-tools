#!/usr/bin/env python
#
# Lara Maia <dev@lara.click> 2016
#
# The Steam Tools is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#k
# The Steam Tools is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see http://www.gnu.org/licenses/.
#

import os
import tempfile
import sqlite3
import json
from shutil import copy, rmtree
from logging import getLogger

from stlib.stconfig import read_config, write_config

logger = getLogger('root')

if os.name == 'nt':
    from ctypes import *
    from ctypes.wintypes import DWORD
    localfree = windll.kernel32.LocalFree
    memcpy = cdll.msvcrt.memcpy
    CryptUnprotectData = windll.crypt32.CryptUnprotectData

    class DATA_BLOB(Structure):
        _fields_ = [
                ("cbData", DWORD),
                ("pbData", POINTER(c_char))
            ]

    # Thanks to Crusher Joe (crusherjoe <at> eudoramail.com)
    # Adapted from here: http://article.gmane.org/gmane.comp.python.ctypes/420
    def win32CryptUnprotectData(evalue):
        bufferIn = c_buffer(evalue, len(evalue))
        blobIn = DATA_BLOB(len(evalue), bufferIn)
        blobOut = DATA_BLOB()

        if CryptUnprotectData(byref(blobIn), None, None, None, None, 0x01, byref(blobOut)):
            cbData = int(blobOut.cbData)
            pbData = blobOut.pbData
            buffer = c_buffer(cbData)
            memcpy(buffer, pbData, cbData)
            localfree(pbData);
            return buffer.raw
        else:
            return ""
else:
    # pycrypto
    from Crypto.Protocol.KDF import PBKDF2
    from Crypto.Cipher import AES

def find_chrome_profile(config):
    if os.name == 'nt':
        xdg_dir = os.getenv('LOCALAPPDATA')
        chrome_dir = os.path.join(xdg_dir, 'Google/Chrome/User Data')
        # Fallback to Chromium
        if not os.path.isdir(chrome_dir):
            chrome_dir = os.path.join(xdg_dir, 'Chromium/User Data')
    else:
        xdg_dir = os.getenv('XDG_CONFIG_HOME', os.path.join(os.path.expanduser('~'), '.config'))
        chrome_dir = os.path.join(xdg_dir, 'google-chrome')
        # Fallback to Chromium
        if not os.path.isdir(chrome_dir):
            chrome_dir = os.path.join(xdg_dir, 'chromium')

    profiles = []
    for dirname in sorted(os.listdir(chrome_dir)):
        if 'Profile' in dirname or 'Default' in dirname:
            if os.path.isfile(os.path.join(chrome_dir, dirname, 'Cookies')):
                profiles.append(os.path.join(chrome_dir, dirname))

    if not len(profiles):
        logger.error("[WITH POWERS] I cannot find your Chrome/Chromium profile")
        return None
    elif len(profiles) == 1:
        return profiles[0]
    else:
        profile = os.path.join(chrome_dir, config.get('Config', 'chromeProfile'))
        if os.path.isfile(os.path.join(profile, 'Cookies')):
            return profile

        logger.info(" Who are you?")
        for i in range(len(profiles)):
            with open(os.path.join(profiles[i], 'Preferences')) as prefs_file:
                prefs = json.load(prefs_file)
            logger.info('  - [%d] %s (%s)',
                        i+1,
                        prefs['account_info'][0]['full_name'],
                        os.path.basename(profiles[i]))

        while True:
            try:
                opc = int(input("Please, input an number [1-{}]:".format(len(profiles))))
                if opc > len(profiles) or opc < 1:
                    raise(ValueError)
            except ValueError:
                logger.info('Please, choose an valid option.')
                continue
            logger.info("Okay, I'm remember that.")
            break

        return profiles[opc-1]

def chrome_decrypt(evalue):
    if os.name == 'nt':
        return win32CryptUnprotectData(evalue).decode('utf-8')
    else:
        cipher = AES.new(PBKDF2(b'peanuts', b'saltysalt', 16, 1), AES.MODE_CBC, IV=b' '*16)
        decrypted = cipher.decrypt(evalue[3:])
        return decrypted[:-decrypted[-1]].decode('utf-8')

def get_steam_cookies(config_file, domain):
    config = read_config(config_file)

    cookies = {}
    profile = find_chrome_profile(config)
    query = 'SELECT name, value, encrypted_value FROM cookies WHERE host_key LIKE ?'

    if profile:
        config['Config']['chromeProfile'] = os.path.basename(profile)
        write_config(config_file)
    else:
        return cookies

    tempdir = tempfile.mkdtemp()
    cookies_path = os.path.join(profile, 'Cookies')
    temp_cookies_path = os.path.join(tempdir, os.path.basename(cookies_path))
    copy(cookies_path, temp_cookies_path)

    connection = sqlite3.connect(temp_cookies_path)
    for key, value, evalue in connection.execute(query, (domain,)):
        if key == '_ga': continue
        if evalue[:3] != b'v10' and evalue[:3] != b'\x01\x00\x00':
            if value:
                cookies[key] = value
            else:
                cookies[key] = evalue
        else:
            cookies[key] = chrome_decrypt(evalue)
    connection.close()

    rmtree(tempdir)

    return cookies
