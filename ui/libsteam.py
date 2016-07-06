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

import atexit
import ctypes
import logging
import os
import subprocess
import sys

if os.name is 'posix':
    import site

class LibSteam:
    def __init__(self):
        atexit.register(self._safe_exit)
        self.logger = logging.getLogger('root')
        self.libsteam_path = self._find_libsteam()
        self.steam_api = ctypes.CDLL(self.libsteam_path)

    def _safe_exit(self, SIG=None, FRM=None):
        self.logger.warning('Exiting...')
        if 'wrapper_process' in dir(self):
            self.wrapper_process.terminate()
            self.logger.debug("Waiting to libsteam_wrapper terminate.")
            try:
                self.wrapper_process.communicate(timeout=20)
            except subprocess.TimeoutExpired:
                self.logger.debug("Force Killing libsteam_wrapper.")
                self.wrapper_process.kill()
                self.wrapper_process.communicate()

            if self.wrapper_process.returncode:
                return 1
            else:
                return 0

    def _find_libsteam(self):
        if os.name == 'nt':
            ext = '.dll'
        else:
            ext = '.so'

        if sys.maxsize > 2 ** 32:
            libsteam_path = os.path.join('lib64', 'libsteam_api' + ext)
        else:
            libsteam_path = os.path.join('lib32', 'libsteam_api' + ext)

        if not os.path.isfile(libsteam_path):
            if os.name == 'nt':
                return False
            else:
                lib_dir = 'share/steam-tools'
                if os.path.isfile(os.path.join('/usr/local', lib_dir, libsteam_path)):
                    STEAM_API = os.path.join('/usr/local', lib_dir, libsteam_path)
                elif os.path.isfile(os.path.join('/usr', lib_dir, libsteam_path)):
                    STEAM_API = os.path.join('/usr', lib_dir, libsteam_path)
                else:
                    return False

        return libsteam_path

    def _find_wrapper(self):
        paths = []
        paths.append(os.path.dirname(os.path.abspath(sys.argv[0])))
        paths.append(os.path.join(paths[0], 'ui'))

        if os.name is 'posix':
            paths.append(os.path.join(site.getsitepackages()[1], 'stlib'))

        for path in paths:
            for ext in ['', '.exe', '.py']:
                full_path = os.path.join(path, 'libsteam_wrapper' + ext)

                if os.path.isfile(full_path):
                    return full_path

    def is_steam_running(self):
        if self.steam_api.SteamAPI_IsSteamRunning():
            return True
        else:
            return False

    def run_wrapper(self, app_id):
        wrapper_path = self._find_wrapper()
        wrapper_exec = [wrapper_path, app_id, self.libsteam_path]

        if wrapper_path[-3:] != 'exe':
            wrapper_exec = ['python'] + wrapper_exec

        self.wrapper_process = subprocess.Popen(wrapper_exec, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        return self.wrapper_process
