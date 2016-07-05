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
import time

import requests
from bs4 import BeautifulSoup as bs

import stlib


class Session:
    def __init__(self, session):
        self.session = session
        self.logger = logging.getLogger('root')
        self.config_parser = stlib.config.Parser()
        self.browser_bridge = stlib.cookie.BrowserBridge()

    def new_session(self):
        self.session = requests.Session()
        self.session.headers.update({'user-agent':'Unknown/0.0.0'})

        return self.session

    def update_headers(self, data):
        self.session.headers.update(data)

    def update_cookies(self, cookies):
        self.session.cookies = requests.utils.cookiejar_from_dict(cookies)

    def get_response(self, url, data=None, timeout=10, verify='cacert.pem', stream=False):
        if data:
            response = self.session.post(url, data=data, timeout=timeout, verify=verify, stream=stream)
        else:
            response = self.session.get(url, timeout=timeout, verify=verify, stream=stream)

        response.raise_for_status()
        return response

    def try_get_response(self, service_name, url):
        auto_recovery = False

        for i in range(1, 4):
            try:
                self.config_parser.read_config()
                cookies = self.config_parser.config._sections[service_name + 'Cookies']
                self.update_cookies(cookies)
                response = self.get_response(url)
            except(requests.exceptions.TooManyRedirects, KeyError):
                if not auto_recovery:
                    self.logger.error('Unable to find cookies in the config file')
                    self.logger.error('Trying to auto recovery')
                    auto_recovery = True
                    cookies = self.browser_bridge.get_cookies(url)

                    self.config_parser.config[service_name + 'Cookies'] = cookies
                    self.config_parser.write_config()
                    self.update_cookies(cookies)
                else:
                    self.logger.error('Unable to get cookies.')
                    return None
            except(requests.exceptions.ConnectionError,
                   requests.exceptions.RequestException,
                   requests.exceptions.Timeout):
                self.logger.error('Unable to connect. Trying again... ({}/3)'.format(i))
                time.sleep(3)
            else:
                return response
