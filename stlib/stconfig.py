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

import os, sys
from logging import getLogger
from configparser import RawConfigParser

LOGGER = getLogger('root')
CONFIG = RawConfigParser()
CONFIG.optionxform=str

def getPath():
    if os.name == 'nt':
        dataDir = os.getenv('LOCALAPPDATA')
    else:
        dataDir = os.getenv('XDG_CONFIG_HOME', os.path.join(os.path.expanduser('~'), '.config'))

    configFile = os.path.basename(sys.argv[0])[:-3]+'.config'
    configPath = os.path.join(dataDir, 'steam-tools', configFile)
    os.makedirs(os.path.dirname(configPath), exist_ok=True)

    if os.path.isfile(configFile):
        return configFile
    else:
        if not os.path.isfile(configPath):
            LOGGER.warn("No config file found.")
            LOGGER.warn("Creating a new at %s", configPath)
            CONFIG.add_section('Config')
            with open(configPath, 'w') as fp:
                CONFIG.write(fp)

        return configPath

def getParser():
    CONFIG.read(getPath())
    return CONFIG

def write():
    with open(getPath(), 'w') as fp:
        CONFIG.write(fp)
