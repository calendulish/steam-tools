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

import logging
import os
import shutil
import sqlite3
import tempfile

import stlib

if os.name == 'posix':
    from Crypto.Protocol.KDF import PBKDF2
    from Crypto.Cipher import AES
else:
    import locale
    from ctypes import *
    from ctypes.wintypes import DWORD


    class DATA_BLOB(Structure):
        _fields_ = [
            ('cb_data', DWORD),
            ('pb_data', POINTER(c_char))
        ]


class BrowserBridge:
    def __init__(self):
        self.logger = logging.getLogger('root')
        self.config_parser = stlib.config.Parser()
        self.config_parser.read_config()

    def get_domain_name(self, url):
        site = url.split('//', 1)[1].split('/', 1)[0].split('.')
        if len(site) > 2 and site[-3] == 'www':
            return '.' + '.'.join(site[-2:])
        else:
            if len(site) > 2:
                return '.'.join(site[-3:])
            else:
                return '.'.join(site[-2:])

    def decrypt_data(self, encrypted_data):
        if os.name == 'nt':
            # Thanks to Crusher Joe (crusherjoe <at> eudoramail.com)
            buffer_in = c_buffer(encrypted_data, len(encrypted_data))
            blob_in = DATA_BLOB(len(encrypted_data), buffer_in)
            blob_out = DATA_BLOB()

            if windll.crypt32.CryptUnprotectData(byref(blob_in), None, None, None, None, 0x01, byref(blob_out)):
                cb_data = int(blob_out.cbData)
                pb_data = blob_out.pbData
                buffer = c_buffer(cb_data)
                windll.msvcrt.memcpy(buffer, pb_data, cb_data)
                windll.kernel32.localfree(pb_data)
                return buffer.raw.decode(locale.getpreferredencoding())
            else:
                return ""
        else:
            cipher = AES.new(PBKDF2(b'peanuts', b'saltysalt', 16, 1), AES.MODE_CBC, IV=b' ' * 16)
            decrypted = cipher.decrypt(encrypted_data[3:])
            return decrypted[:-decrypted[-1]].decode('utf-8')

    def get_cookies(self, profile, url):
        cookies = {}
        temp_dir = tempfile.mkdtemp()
        cookies_path = os.path.join(profile, 'Cookies')
        temp_cookies_path = os.path.join(temp_dir, os.path.basename(cookies_path))
        shutil.copy(cookies_path, temp_cookies_path)

        connection = sqlite3.connect(temp_cookies_path)
        query = 'SELECT name, value, encrypted_value FROM cookies WHERE host_key LIKE ?'
        for key, data, encrypted_data in connection.execute(query, (self.get_domain_name(url),)):
            if key == '_ga': continue
            if encrypted_data[:3] != b'v10' and encrypted_data[:3] != b'\x01\x00\x00':
                if data:
                    cookies[key] = data
                else:
                    cookies[key] = encrypted_data
            else:
                cookies[key] = self.decrypt_data(encrypted_data)
        connection.close()

        shutil.rmtree(temp_dir)

        return cookies

    def get_chrome_profile(self):
        if os.name == 'nt':
            data_dir = os.getenv('LOCALAPPDATA')
            chrome_dir = os.path.join(data_dir, 'Google/Chrome/User Data')
            # Fallback to Chromium
            if not os.path.isdir(chrome_dir):
                chrome_dir = os.path.join(data_dir, 'Chromium/User Data')
        else:
            data_dir = os.getenv('XDG_CONFIG_HOME', os.path.join(os.path.expanduser('~'), '.config'))
            chrome_dir = os.path.join(data_dir, 'google-chrome')
            # Fallback to Chromium
            if not os.path.isdir(chrome_dir):
                chrome_dir = os.path.join(data_dir, 'chromium')

        profile = os.path.join(chrome_dir, self.config_parser.config.get('Config', 'chromeProfile', fallback='Default'))

        if os.path.isfile(os.path.join(profile, 'Cookies')):
            pass
            # Check url and check if steam cookies exists
            # if cookies exists:
            #     update profile in the config
            #     return true
            # else:
            #     search manually (just continue)

        profiles = []
        if os.path.isdir(chrome_dir):
            for dir_name in sorted(os.listdir(chrome_dir)):
                if 'Profile' in dir_name or 'Default' in dir_name:
                    if os.path.isfile(os.path.join(chrome_dir, dir_name, 'Cookies')):
                        profiles.append(os.path.join(chrome_dir, dir_name))

        return profiles
