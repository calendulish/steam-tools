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

import sys

from stlib import stlogger
from stlib.stfakeapp import STFakeApp


class STConsole:
    def __init__(self, cParams):
        self.logger = stlogger.getLogger('VERBOSE')
        self.program = cParams.cli[0]
        self.cParams = cParams

        if self.program in dir(self):
            eval('self.' + self.program + '()')
        else:
            self.logger.critical("Please, check the command line.")
            self.logger.critical("The module %s don't exist", self.program)

    def fakeapp(self):
        try:
            STFA = STFakeApp()
            if STFA.is_steam_running():
                self.fake_app = STFA.run_wrapper(self.cParams.cli[1])
            else:
                self.logger.critical("Unable to locate a running instance of steam.")
                self.logger.critical("Please, start the Steam and try again.")
                sys.exit(1)
        except IndexError:
            self.logger.critical("Unable to locate the gameID.")
            self.logger.critical("Please, check the command line.")
            sys.exit(1)

        try:
            ret = self.fake_app.wait()
            sys.exit(ret)
        except KeyboardInterrupt:
            pass
