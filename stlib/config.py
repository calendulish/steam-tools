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

LOGGER = logging.getLogger(__name__)

if os.name == 'nt':
    DATA_DIR = os.getenv('LOCALAPPDATA')
else:
    DATA_DIR = os.getenv('XDG_CONFIG_HOME', os.path.join(os.path.expanduser('~'), '.config'))

CONFIG_FILE_NAME = os.path.splitext(os.path.basename(sys.argv[0]))[0] + '.config'
CONFIG_FILE_PATH = os.path.join(DATA_DIR, 'steam-tools', CONFIG_FILE_NAME)

CONFIG_PARSER = configparser.RawConfigParser()
CONFIG_PARSER.optionxform = str

os.makedirs(os.path.dirname(CONFIG_FILE_PATH), exist_ok=True)

if not os.path.isfile(CONFIG_FILE_PATH):
    LOGGER.warn("No config file found.")
    LOGGER.warn("Creating a new at %s", CONFIG_FILE_PATH)

    CONFIG_PARSER.add_section('Config')

    with open(CONFIG_FILE_PATH, 'w') as FP:
        CONFIG_PARSER.write(FP)


def read():
    CONFIG_PARSER.read(CONFIG_FILE_PATH)
    return CONFIG_PARSER


def write():
    with open(CONFIG_FILE_PATH, 'w') as config_file:
        CONFIG_PARSER.write(config_file)
