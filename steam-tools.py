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

import argparse
import logging
import os
import subprocess
import sys

import stlib
import ui

LOGGER = stlib.logger.get_logger('VERBOSE')

if os.name is 'posix':
    if os.getenv('DISPLAY'):
        import ui.main
    else:
        LOGGER.warning('The DISPLAY is not set!')
        LOGGER.warning('Use --cli <module> for the commmand line interface.')
        sys.exit(1)


def safeCall(call):
    try:
        return subprocess.check_call(call)
    except subprocess.CalledProcessError as e:
        return e.returncode
    except FileNotFoundError as e:
        LOGGER.critical("I cannot find winpty. Please, check your installation.")
        LOGGER.critical(e)
        return 1


# if is executing from a Cygwin console:
if os.name is 'nt' and os.getenv('PWD'):
    # noinspection PyUnresolvedReferences
    import psutil

    interpreter = psutil.Process(os.getppid())
    shell = interpreter.parent()

    if shell.name() != 'console.exe':
        logging.shutdown()

        wrapper = ['winpty/console.exe', sys.executable]

        # If is not a compiled version
        if sys.executable != sys.argv[0]:
            wrapper.append(sys.argv[0])

        if len(sys.argv) != 1:
            wrapper.extend(sys.argv[1:])

        return_code = safeCall(wrapper)
        sys.exit(return_code)

if __name__ == "__main__":
    network_session = stlib.network.Session(None)
    main_session = network_session.new_session()

    aParser = argparse.ArgumentParser()
    aParser.add_argument('-c', '--cli', nargs='+')
    cParams = aParser.parse_args()

    if cParams.cli:
        ST = ui.console.SteamTools(main_session, cParams)
    else:
        ST = ui.main.SteamTools(main_session)
        ui.Gtk.main()
