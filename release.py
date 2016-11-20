#!/usr/bin/python3
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

import glob
import importlib.machinery
import os
import shutil
import subprocess
import sys
import tempfile
import time

__version_module_path__ = os.path.join('ui', 'version.py')
__version_class__ = importlib.machinery.SourceFileLoader('version', __version_module_path__)
version = __version_class__.load_module()

script_path = os.path.dirname(os.path.abspath(sys.argv[0]))
build_path = os.path.join(script_path, 'dist')
release_path = os.path.join(script_path, 'release')
temporary_path = tempfile.mktemp(prefix='steam_tools_release_')


# noinspection PyShadowingNames
def update_version():
    global version
    __version_module_path__ = os.path.join(build_path, 'version.pyc')
    __version_class__ = importlib.machinery.SourcelessFileLoader('version', __version_module_path__)

    try:
        __version_module__ = __version_class__.load_module()

        for var in dir(__version_module__):
            setattr(version, var, eval('__version_module__.' + var))
    except FileNotFoundError:
        setattr(version, '__VERSION_EXTRA__', 'Linux')

    version.__VERSION__ = '{}.{}.{} {}'.format(version.__VERSION_MAJOR__,
                                               version.__VERSION_MINOR__,
                                               version.__VERSION_REVISION__,
                                               version.__VERSION_EXTRA__)


def safe_call(call):
    try:
        print('Calling:', ' '.join(call))
        subprocess.check_call(call)
    except subprocess.CalledProcessError as e:
        print("command: {}\nrcode: {}".format(call, e.returncode))
        sys.exit(1)
    except FileNotFoundError as e:
        print("Something is missing in your system for make an complete release")
        print("command: {}".format(call))
        print(e)
        sys.exit(1)


def build(current_system, current_arch):
    print("\n--------------------------------------------")
    print("Build Configuration:")
    print(" - System: {}".format(current_system))
    print(" - Architecture: {} bits".format(current_arch))
    print(" - Version: {}.{}.{}\n".format(version.__VERSION_MAJOR__,
                                          version.__VERSION_MINOR__,
                                          version.__VERSION_REVISION__))

    for timer in range(5, 0, -1):
        print('Starting in', timer, end='\r')
        time.sleep(1)
    print('\n')

    if current_system == 'Linux':
        if os.name == 'nt' and not os.getenv('PWD'):
            interpreter = ['C:\\msys64\\usr\\bin\\python3.4.exe', '-u']
        else:
            interpreter = ['/usr/bin/python3', '-u']

        params = ['setup.py', 'sdist']
        archive_extension_ = '.tar.gz'

        if not os.path.isfile(interpreter[0]):
            print('Linux Python interpreter not found.')
            print('Cannot build for Linux. Ignoring.')
            return None

        print('Building...')
        safe_call(interpreter + params)

        update_version()
    else:
        if os.name == 'posix' and not sys.platform == 'cygwin':
            print('You cannot build steam tools for Windows from Linux. Ignoring.')
            return None

        interpreter = [os.path.join('scripts', 'build.cmd')]

#        if current_arch == 64:
#            params = ['Python34-x64']
#            print(">>>>>>>>>> OS 64 --- Python34-x64:")
#            print (os.environ['PYTHONPATH'])
#        else:
#            print(">>>>>>>>>> OS 32 --- Python34:")
#            params = ['Python34']
#            print (os.environ['PYTHONPATH'])

        params = [os.environ['PYTHONPATH']]
        print(">>>>>>>>>> params: ",params)
        
        archive_extension_ = '.zip'

        print('Building...')
        safe_call(interpreter + params)

        update_version()

        safe_call([os.path.join('scripts', 'package.cmd'),
                   '-'.join(version.__VERSION__.split(' '))])

    archive_name_ = 'Steam Tools-{}'.format('-'.join(version.__VERSION__.split(' ')))
    archive_in_path_ = os.path.join('dist', archive_name_ + archive_extension_)
    archive_out_path_ = os.path.join(temporary_path, archive_name_ + archive_extension_)
    shutil.move(archive_in_path_, archive_out_path_)

    return archive_out_path_


if __name__ == '__main__':
    builds = {'Windows': [32, 64],
              'Linux': ['all']}

    zip_file_paths = []

    if os.path.isdir(release_path):
        shutil.rmtree(release_path)

    if not os.path.isdir(temporary_path):
        os.makedirs(temporary_path)

    for system, archs in builds.items():
        for arch in archs:
            os.system('git clean -fdx')
            archive_path = build(system, arch)
            zip_file_paths.append(archive_path)

    print('Releasing...')

    if not os.path.isdir(release_path):
        os.makedirs(release_path)

    for path in zip_file_paths:
        if path:
            shutil.move(path, release_path)

    print('Done.')
