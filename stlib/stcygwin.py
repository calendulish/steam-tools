#!/usr/bin/env python
#
# Lara Maia <dev@lara.click> 2015~2016
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
from subprocess import check_call
from logging import getLogger

from stlib import stlogger

LOGGER = getLogger('root')

if os.name == 'nt' and os.getenv('PWD'):
    from psutil import Process
    if Process(os.getppid()).parent().name() != 'console.exe':
        if os.path.isfile('winpty/console.exe'):
            stlogger.closeAll()
            ret = check_call(['winpty/console.exe', sys.executable, sys.argv[0]])
        else:
            LOGGER.critical("I cannot find some libraries needed for the steam-tools work")
            LOGGER.critical("Please, check your installation/build")
            sys.exit(1)

        sys.exit(ret)