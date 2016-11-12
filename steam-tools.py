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

# MUST be ALWAYS the first import
# noinspection PyUnresolvedReferences
import ui.fix_std

import argparse
import os
import sys

import stlib

if __name__ == "__main__":
    print('Steam Tools version {}'.format(ui.version.__VERSION__))
    print('Copyright (C) 2016 Lara Maia - <dev@lara.click>\n')

    aParser = argparse.ArgumentParser()
    aParser.add_argument('-c', '--cli', nargs='+')
    cParams = aParser.parse_args()

    try:
        if cParams.cli:
            if os.name is 'nt' and os.getenv('PWD'):
                stlib.logger.warning('Running steam tools from custom console is not supported.')
                stlib.logger.warning('Some problems may occur.')

            ST = ui.console.SteamTools(cParams)
        else:
            if os.name is 'posix' and not os.getenv('DISPLAY'):
                stlib.logger.error('The DISPLAY is not set!')
                stlib.logger.error('Use -c / --cli <module> for the command line interface.')
                sys.exit(1)

            ST = ui.main.SteamTools()
            ST.run()
    except KeyboardInterrupt:
        sys.exit(0)
