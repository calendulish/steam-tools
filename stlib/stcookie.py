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
from shutil import copy, rmtree

if os.name == 'nt':
    from ctypes import *
    from ctypes.wintypes import DWORD
    localfree = windll.kernel32.LocalFree
    memcpy = cdll.msvcrt.memcpy
    CryptUnprotectData = windll.crypt32.CryptUnprotectData

    XDG_DIR = os.getenv('LOCALAPPDATA')
    COOKIES_DIR = os.path.join(XDG_DIR, 'Google/Chrome/User data/Default')

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

    XDG_DIR = os.getenv('XDG_CONFIG_HOME', os.path.join(os.path.expanduser('~'), '.config'))
    COOKIES_DIR = os.path.join(XDG_DIR, 'google-chrome/Profile 1')

COOKIES_PATH = os.path.join(COOKIES_DIR, "Cookies")

def chrome_decrypt(evalue):
    if os.name == 'nt':
        return win32CryptUnprotectData(evalue).decode('utf-8')
    else:
        cipher = AES.new(PBKDF2(b'peanuts', b'saltysalt', 16, 1), AES.MODE_CBC, IV=b' '*16)
        decrypted = cipher.decrypt(evalue[3:])
        return decrypted[:-decrypted[-1]].decode('utf-8')

def get_steam_cookies(domain):
    query = 'SELECT name, value, encrypted_value FROM cookies WHERE host_key LIKE ?'

    tempdir = tempfile.mkdtemp()
    temp_COOKIES_PATH = os.path.join(tempdir, os.path.basename(COOKIES_PATH))
    copy(COOKIES_PATH, temp_COOKIES_PATH)

    cookies = {}
    connection = sqlite3.connect(temp_COOKIES_PATH)
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
