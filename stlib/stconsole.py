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
import os
import locale
from signal import signal, SIGINT
from subprocess import Popen, PIPE

from stlib import stlogger

if os.name is 'posix':
    import site

class STConsole:
    def __init__(self, cParams):
        signal(SIGINT, self.safe_exit)
        self.logger = stlogger.getLogger('VERBOSE')
        self.program = cParams.cli[0]
        self.cParams = cParams

        if self.program in dir(self):
            eval('self.'+self.program+'()')
            self.safe_exit()
        else:
            self.logger.critical("Please, check your command line.")
            self.logger.critical("The program %s don't exist", self.program)

    def safe_exit(self, SIG=None, FRM=None):
        if 'fake_app' in dir(self):
            self.fake_app.terminate()
            self.logger.debug("Waiting to fakeapp terminate.")
            self.fake_app.wait()
            if self.fake_app.returncode and 'fake_app_stderr' in dir(self):
                error = self.fake_app_stderr.decode(locale.getpreferredencoding())
                self.logger.critical(error)
                return 1

    def find_fake_app(self):
        paths = []
        paths.append(os.path.dirname(os.path.abspath(sys.argv[0])))
        paths.append(os.path.join(paths[0], 'stlib'))

        if os.name is 'posix':
            paths.append(os.path.join(site.getsitepackages()[1], 'stlib'))

        for path in paths:
            for ext in [ '', '.exe', '.py' ]:
                full_path = os.path.join(path, 'fakeapp'+ext)

                if os.path.isfile(full_path):
                    return full_path

        self.logger.critical("I cannot found some libraries needed.")
        self.logger.critical("Please, verify your installation.")
        sys.exit(1)

    def fakeapp(self):
        fake_app_path = self.find_fake_app()

        try:
            fake_app_exec = [fake_app_path, self.cParams.cli[1]]
        except IndexError:
            return 1

        if fake_app_path[-3:] != 'exe':
            fake_app_exec = ['python']+fake_app_exec

        self.fake_app = Popen(fake_app_exec, stdout=PIPE, stderr=PIPE)
        self.fake_app_stderr = self.fake_app.communicate()[1]

        return 0
