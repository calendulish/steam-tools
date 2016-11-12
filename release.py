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

import glob
import importlib.machinery
import os
import shutil
import subprocess
import sys
import tempfile
import time

__version_module_path__ =  os.path.join('ui', 'version.py')
__version_class__ = importlib.machinery.SourceFileLoader('version', __version_module_path__)
version = __version_class__.load_module()

script_path = os.path.dirname(os.path.abspath(sys.argv[0]))
build_path = os.path.join(script_path, 'dist')
release_path = os.path.join(script_path, 'release')
temporary_path = tempfile.mktemp(prefix='steam_tools_release_')


def update_version():
    global version
    __version_module_path__ = os.path.join(build_path, 'version.pyc')
    __version_class__ = importlib.machinery.SourcelessFileLoader('version', __version_module_path__)

    try:
        __version_module__ = __version_class__.load_module()

        for var in dir(__version_module__):
            setattr(version, var, eval('__version_module__.' + var))
    except FileNotFoundError:
        setattr(version, '__VERSION_EXTRA__', 'LIN ALL')

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


def build(system, arch):
    print("\n--------------------------------------------")
    print("Build Configuration:")
    print(" - System: {}".format(system))
    print(" - Version: {}.{}.{} {}".format(version.__VERSION_MAJOR__,
                                           version.__VERSION_MINOR__,
                                           version.__VERSION_REVISION__,
                                           system + str(arch)))
    print(" - Architecture: {} bits\n".format(arch))

    for timer in range(5, 0, -1):
        print('Starting in', timer, end='\r')
        time.sleep(1)
    print('\n')

    if system == 'lin':
        console = ['/cygdrive/c/cygwin64/bin/mintty.exe']
        params = ['-w', 'hide', '-l', '-', '-e']
        interpreter = ['/usr/bin/python3', '-u', 'setup.py']

        setup_options = ['build',
                         'install',
                         '--root', build_path,
                         '--install-data', '.',
                         '--install-scripts', '.',
                         '--install-lib', '.',
                         'FORCELIN']
    elif system == 'win':
        console = ['/cygdrive/c/Windows/System32/cmd.exe']
        params = ['/C']

        if arch == 64:
            interpreter = ['C:\\Python34-x64\\python', '-u', 'setup.py']
        else:
            interpreter = ['C:\\Python34\\python', '-u', 'setup.py', 'FORCE32']


        setup_options = ['py2exe',
                         'FORCEWIN']
    else:
        console = ['/cygdrive/c/cygwin64/bin/mintty.exe']
        params = ['-w', 'hide', '-l', '-', '-e']
        interpreter = ['/usr/bin/make']

        if arch is 64:
            setup_options = ['PYTHONPATH=/cygdrive/c/Python34-x64']
        else:
            setup_options = ['PYTHONPATH=/cygdrive/c/Python34', 'FORCE32BITS=1']

        safe_call(console + params + interpreter + setup_options + ['clean'])

    print('Building...')
    safe_call(console + params + interpreter + setup_options)

    # The linux build in the zip file is not an real package.
    # It's just an portable version for easy access.
    # For real packages, use distribution packages.
    if system == 'lin':
        os.remove(glob.glob(os.path.join('dist', '*.egg-info'))[0])
        os.remove(os.path.join('dist', 'version.pyc'))
        shutil.rmtree(os.path.join('dist', 'ui', '__pycache__'))
        shutil.rmtree(os.path.join('dist', 'stlib', '__pycache__'))
        shutil.move(os.path.join('dist', 'steam-tools'),
                    os.path.join('dist', 'steam-tools.py'))


def archive(name):
    print('Creating archiving for', name)

    zip_file_name = name + '.zip'
    output_path = os.path.join(script_path, zip_file_name)

    if not os.path.isdir(temporary_path):
        os.makedirs(temporary_path)

    shutil.move(build_path, name)
    shutil.make_archive(name, 'zip', script_path, name)
    shutil.move(output_path, temporary_path)
    shutil.rmtree(os.path.join(script_path, name))

    return os.path.join(temporary_path, zip_file_name)


if __name__ == '__main__':
    if not sys.platform == 'cygwin':
        print('Please, run through cygiwn')
        sys.exit(1)

    builds = { 'win': [ 32, 64 ],
               'lin': [ 'all' ]}

    zip_file_paths = []

    if os.path.isdir(release_path):
        shutil.rmtree(release_path)

    for system, archs in builds.items():
        for arch in archs:
            os.system('git clean -fdx')
            build(system, arch)
            update_version()
            archive_name =  'Steam Tools {}'.format(version.__VERSION__)
            zip_file_paths.append(archive(archive_name))

    print('Releasing...')

    if not os.path.isdir(release_path):
        os.makedirs(release_path)

    for path in zip_file_paths:
        shutil.move(path, release_path)

    print('Done.')
