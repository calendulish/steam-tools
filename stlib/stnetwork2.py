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

from requests.utils import add_dict_to_cookiejar
from requests.exceptions import TooManyRedirects, HTTPError
from requests import Session
from stlib import stcookie

steamLoginPages = [
                    'https://steamcommunity.com/login/home/',
                    'https://store.steampowered.com//login/',
                ]

Session = Session()
Session.headers.update({'user-agent': 'unknown/0.0.0'})

def getResponse(url, data=False):
    cookies = stcookie.getCookies(url)
    add_dict_to_cookiejar(Session.cookies, cookies)

    try:
        if data:
            response = Session.post(url, data=data, timeout=10, verify="cacert.pem", stream=False)
        else:
            response = Session.get(url, timeout=10, verify="cacert.pem", stream=False)

        response.raise_for_status()
        return response
    except requests.exceptions.TooManyRedirects:
        return 1
    except requests.exceptions.HTTPError:
        return 2
