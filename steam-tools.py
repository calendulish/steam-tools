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

import gevent

import stlib
import ui

if os.name is 'posix':
    if os.getenv('DISPLAY'):
        import ui.main
    else:
        stlib.logger.warning('The DISPLAY is not set!')
        stlib.logger.warning('Use --cli <module> for the command line interface.')
        sys.exit(1)


def safe_call(call):
    try:
        return subprocess.check_call(call)
    except subprocess.CalledProcessError as e:
        return e.returncode
    except FileNotFoundError as e:
        stlib.logger.critical("I cannot find winpty. Please, check your installation.")
        stlib.logger.critical(e)
        return 1


def fix_gevent():
    gevent.sleep(0.1)
    return True


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

        return_code = safe_call(wrapper)
        sys.exit(return_code)

if __name__ == "__main__":
    aParser = argparse.ArgumentParser()
    aParser.add_argument('-c', '--cli', nargs='+')
    cParams = aParser.parse_args()

    if cParams.cli:
        ST = ui.console.SteamTools(cParams)
    else:
        ST = ui.main.SteamTools()
        ui.GLib.idle_add(fix_gevent)
        ui.Gtk.main()
