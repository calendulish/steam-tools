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
import textwrap

import stlib

if __name__ == "__main__":
    stlib.logging.console_msg('Steam Tools version {}'.format(ui.version.__VERSION__))
    stlib.logging.console_msg('Copyright (C) 2016 Lara Maia - <dev@lara.click>\n')

    command_parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=textwrap.dedent('''
                Available modules for console mode:
                    - cardfarming
                    - fakeapp <game id>
                    - steamtrades_bump
                    - steamgifts_join
                       '''))

    command_parser.add_argument('-c', '--cli',
                                choices=['cardfarming', 'fakeapp', 'steamtrades_bump', 'steamgifts_join', 'authenticator'],
                                metavar='module [options]',
                                action='store',
                                nargs=1,
                                help='Start module without GUI (console mode)',
                                dest='module')
    command_parser.add_argument('options',
                                nargs='*',
                                help=argparse.SUPPRESS)

    command_params = command_parser.parse_args()

    try:
        if command_params.module:
            if os.name is 'nt' and os.getenv('PWD'):
                stlib.logger.warning('Running steam tools from custom console is not supported on Windows.')
                stlib.logger.warning('Some problems may occur.')

            ST = ui.console.SteamTools(command_params)
        else:
            if os.name is 'posix' and not os.getenv('DISPLAY'):
                stlib.logger.error('The DISPLAY is not set!')
                stlib.logger.error('Use -c / --cli <module> for the command line interface.')
                sys.exit(1)

            ST = ui.main.SteamTools()
            ST.run()
    except KeyboardInterrupt:
        sys.exit(0)
