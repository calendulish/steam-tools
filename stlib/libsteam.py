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

import ctypes
import os
import subprocess
import sys

import stlib

if os.name is 'posix':
    import site


def _find_libsteam():
    if os.name == 'nt':
        libsteam = 'libsteam_api.dll'

        if os.path.isfile(libsteam):
            return libsteam
        else:
            return False
    else:
        paths = [
            '/usr/share/steam-tools',
            '/usr/local/share/steam-tools',
            '/opt/steam-tools',
            ''
        ]

        for path in paths:
            libsteam_path = os.path.join(path, 'libsteam_api.so')
            if os.path.isfile(libsteam_path):
                return libsteam_path

        return False


def _find_wrapper():
    current_directory = os.path.dirname(os.path.abspath(sys.argv[0]))
    paths = [os.path.join(current_directory, 'stlib')]

    if os.name is 'posix':
        for directory in site.getsitepackages():
            paths.append(os.path.join(directory, 'stlib'))

    for path in paths:
        for ext in ['', '.exe', '.py']:
            full_path = os.path.join(path, 'libsteam_wrapper' + ext)

            if os.path.isfile(full_path):
                return full_path


def run_wrapper(app_id):
    wrapper_path = _find_wrapper()

    if not wrapper_path:
        stlib.logger.critical('Unable to find libsteam wrapper!')
        return None

    wrapper_exec = [wrapper_path, app_id, _find_libsteam()]

    if wrapper_path[-3:] != 'exe':
        wrapper_exec = ['python'] + wrapper_exec

    stlib.wrapper_process = subprocess.Popen(wrapper_exec, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def stop_wrapper():
    stlib.logger.verbose('Closing wrapper subprocess...')

    try:
        stlib.wrapper_process.terminate()
    except ProcessLookupError:
        stlib.logger.verbose('subprocess is already terminated.')
        return 1

    try:
        stlib.logger.verbose("Waiting to wrapper subprocess terminate.")
        stlib.wrapper_process.communicate(timeout=20)
    except subprocess.TimeoutExpired:
        stlib.logger.verbose("Force killing wrapper subprocess.")
        stlib.wrapper_process.kill()
        stlib.wrapper_process.communicate()

    if stlib.wrapper_process.returncode:
        return_ = 1
    else:
        return_ = 0

    stlib.wrapper_process = None
    return return_


def is_steam_running():
    steam_api = ctypes.CDLL(_find_libsteam())
    if steam_api.SteamAPI_IsSteamRunning():
        return True
    else:
        return False


def is_wrapper_running():
    if not stlib.wrapper_process or \
            stlib.wrapper_process.poll():
        return False
    else:
        return True
