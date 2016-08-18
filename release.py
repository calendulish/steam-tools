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

import os, sys
import shutil
from time import sleep
from subprocess import check_call, CalledProcessError

WIN32 = 'C:\\Python34\\python.exe'
WIN64 = 'C:\\Python34-x64\\python.exe'
CYG32 = '/cygdrive/c/Python34/python.exe'
CYG64 = '/cygdrive/c/Python34-x64/python.exe'
LINALL = '/usr/bin/python3'
CMAKE = '/usr/bin/make'

if os.name == 'nt' and os.getenv('PWD') \
   or 'cygwin' in sys.platform:
    WCOM = [ '/cygdrive/c/Windows/System32/cmd.exe' ]
    CCOM = []
    CCOMPARAMS = []
else:
    WCOM = [ 'C:\\Windows\\System32\\cmd.exe' ]
    CCOM = [ 'C:\\cygwin64\\bin\\mintty.exe' ]
    CCOMPARAMS = [ '-w', 'hide', '-l', '-', '-e' ]

WCOMPARAMS = [ '/C' ]

def safeCall(call):
    program = [ p for p in call if p is not '' ]

    try:
        print('\n\nCalling {}\n\n'.format(program))
        check_call(program)
    except CalledProcessError as e:
        print("command: {}\nrcode: {}".format(program, e.returncode))
        sys.exit(1)
    except FileNotFoundError as e:
        print("Something is missing in your system for make an complete release")
        print("command: {}".format(program))
        print(e)
        sys.exit(1)

def build(version, system, arch):
    try:
        interpreter = eval(system+str(arch))
    except NameError:
        return

    print("\n--------------------------------------------")
    print("Build Configuration:")
    print(" - ST Version: {}".format(version))
    print(" - System: {}".format(system))
    print(" - Architecture: {} bits\n".format(arch))
    sleep(3)

    if system == 'LIN':
        com = CCOM+CCOMPARAMS
        startDir = os.path.dirname(os.path.abspath(sys.argv[0]))
        setup_options = [ 'build',
                          'install',
                          '--root', os.path.join(startDir, 'dist'),
                          '--install-data', '.',
                          '--install-scripts', '.',
                          '--install-lib', '.',
                          'FORCELIN' ]
    elif system == 'WIN':
        com = WCOM+WCOMPARAMS
        setup_options = [ 'py2exe', 'FORCEWIN' ]
    else:
        com = CCOM+CCOMPARAMS
        mkcall = [ CMAKE, 'PYTHONPATH='+os.path.dirname(interpreter) ]
        if arch == 32:
            mkcall += [ 'FORCE32BITS=1' ]

        print("Building...")
        safeCall(com+mkcall+['clean'])
        safeCall(com+mkcall)
        return

    print("Building...")
    pycall = [interpreter, '-u', 'setup.py']
    safeCall(com+pycall+setup_options)

def archive(version, system, arch):
    startDir = os.path.dirname(os.path.abspath(sys.argv[0]))
    outDir = os.path.join(startDir, 'dist')
    archiveName = 'steam_tools_'+version+'_'+system+'_'+str(arch)
    archiveDir = os.path.join(startDir, archiveName)

    if not os.path.isdir(outDir):
        return

    print('Preparing for archive')

    if os.path.isfile(archiveDir+'.zip'):
        os.remove(archiveDir+'.zip')

    if os.path.isdir(archiveDir):
        shutil.rmtree(archiveDir)

    os.rename(outDir, archiveDir)
    shutil.make_archive(archiveName, 'zip', startDir, os.path.basename(archiveDir))
    shutil.rmtree(archiveDir)
    print('Archiving complete: {}'.format(archiveDir+'.zip'))

if __name__ == "__main__":
    if sys.version_info[0] < 3:
        print("You must execute in python 3+")
        sys.exit(1)

    if len(sys.argv) < 2:
        print("Please, define the version")
        sys.exit(1)

    if sys.argv[1] == 'clean':
        for file in os.listdir(os.path.dirname(os.path.abspath(sys.argv[0]))):
            if '.zip' in file:
                os.remove(file)
        print("Done!")
        sys.exit(0)

    for system in [ 'WIN', 'CYG', 'LIN' ]:
        for arch in [ 32, 64, 'ALL' ]:
            shutil.rmtree('dist', ignore_errors=True)
            shutil.rmtree('build', ignore_errors=True)
            build(sys.argv[1], system, arch)
            archive(sys.argv[1], system, arch)
