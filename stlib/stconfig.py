#!/usr/bin/env python
#
# Lara Maia <dev@lara.click> 2015
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

import os
from logging import getLogger
from configparser import RawConfigParser

logger = getLogger('root')

def init(fileName):
    config = RawConfigParser()
    xdg_dir = os.getenv('XDG_CONFIG_HOME', os.path.join(os.path.expanduser('~'), '.config'))
    config_file = os.path.join(xdg_dir, 'steam-tools', fileName)

    os.makedirs(os.path.dirname(config_file), exist_ok=True)

    if os.path.isfile(config_file):
        config.read(config_file)
    elif os.path.isfile(fileName):
        config.read(fileName)
    else:
        logger.critical("Configuration file not found. These is the search paths:")
        logger.critical(" - {}".format(os.path.join(os.getcwd(), 'steam-card-farming.config')))
        logger.critical(" - {}".format(config_file))
        logger.critical("Please, copy the example file or create a new with your data.")
        exit(1)

    return config
