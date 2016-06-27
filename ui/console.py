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
import time
import logging

import stlib
import ui

class SteamTools:
    def __init__(self, cParams):
        self.logger = logging.getLogger('root')
        self.module = cParams.cli[0]
        self.parameters = cParams
        self.libsteam = ui.libsteam.LibSteam()

        if self.module in dir(self):
            eval('self.' + self.module + '()')
        else:
            self.logger.critical("Please, check the command line.")
            self.logger.critical("The module %s don't exist", self.module)

    def fakeapp(self):
        try:
            game_id = self.parameters.cli[1]
        except IndexError:
            self.logger.critical("Unable to locate the gameID.")
            self.logger.critical("Please, check the command line.")
            sys.exit(1)

        if self.libsteam.is_steam_running():
            self.logger.info("Preparing. Please wait...")
            fake_app = self.libsteam.run_wrapper(game_id)

            time.sleep(3)
            if fake_app.poll():
                self.logger.critical("This is not a valid gameID.")
                sys.exit(1)

            try:
                self.logger.info("Running {}".format(game_id))
                fake_app.wait()
            except KeyboardInterrupt:
                pass
        else:
            self.logger.critical("Unable to locate a running instance of steam.")
            self.logger.critical("Please, start Steam and try again.")
            sys.exit(1)

        sys.exit(0)
