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

logger = logging.getLogger(__name__)

if os.name == 'nt':
    data_dir = os.getenv('LOCALAPPDATA')
else:
    data_dir = os.getenv('XDG_CONFIG_HOME', os.path.join(os.path.expanduser('~'), '.config'))

config_file_name = os.path.splitext(os.path.basename(sys.argv[0]))[0] + '.config'
config_file_path = os.path.join(data_dir, 'steam-tools', config_file_name)

config_parser = configparser.RawConfigParser()
config_parser.optionxform = str

os.makedirs(os.path.dirname(config_file_path), exist_ok=True)

if not os.path.isfile(config_file_path):
    logger.warn("No config file found.")
    logger.warn("Creating a new at %s", config_file_path)

    config_parser.add_section('Config')
    config_parser.add_section('Debug')
    config_parser.add_section('CardFarming')
    config_parser.add_section('SteamTrades')

    with open(config_file_path, 'w') as FP:
        config_parser.write(FP)


def read():
    config_parser.read(config_file_path)
    return config_parser


def write():
    with open(config_file_path, 'w') as config_file:
        config_parser.write(config_file)
