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

import configparser
import logging
import os
import sys


class Parser:
    def __init__(self):
        self.logger = logging.getLogger('root')
        self.config = configparser.RawConfigParser()
        self.config.optionxform = str

        if os.name == 'nt':
            data_dir = os.getenv('LOCALAPPDATA')
        else:
            data_dir = os.getenv('XDG_CONFIG_HOME', os.path.join(os.path.expanduser('~'), '.config'))

        self.config_file_name = os.path.splitext(os.path.basename(sys.argv[0]))[0] + '.config'
        self.config_file_path = os.path.join(data_dir, 'steam-tools', self.config_file_name)

        os.makedirs(os.path.dirname(self.config_file_path), exist_ok=True)

        if not os.path.isfile(self.config_file_path):
            self.logger.warn("No config file found.")
            self.logger.warn("Creating a new at %s", self.config_file_path)
            self.config.add_section('Config')
            with open(self.config_file_path, 'w') as fp:
                self.config.write(fp)

    def read_config(self):
        self.config.read(self.config_file_path)

    def write_config(self):
        with open(self.config_file_path, 'w') as fp:
            self.config.write(fp)
