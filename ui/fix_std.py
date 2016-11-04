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

import os
import sys
import logging


logging.STDERR = 55
logging.addLevelName(logging.STDERR, 'STDERR')

logger = logging.getLogger('SteamTools')
logger.stderr = lambda msg, *args: logger._log(logging.STDERR, msg, args)


if os.name is 'nt':
    import ctypes
    # noinspection PyUnresolvedReferences
    import psutil
    import tempfile
    import warnings


    class HoleToLogger(object):
        def write(self, text):
            logger.stderr(text)

        def flush(self):
            pass
            
    class HormHole(object):
        def write(self, text):
            pass

        def flush(self):
            pass

    interpreter = psutil.Process(os.getppid())
    shell = interpreter.parent()

    # Running from Windows without terminal
    if not shell or shell.name() == 'svchost.exe':
        # Bypass py2exe BlackHole
        sys.stdout = HormHole()
        sys.stderr = HoleToLogger()

        # Hide console window
        console = ctypes.windll.kernel32.GetConsoleWindow()
        ctypes.windll.user32.ShowWindow(console, 0)
        ctypes.windll.kernel32.CloseHandle(console)
