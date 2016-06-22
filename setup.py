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
from distutils.command.build import build
from distutils.command.install_scripts import install_scripts
from distutils.core import setup

CMK, FORCELIN, FORCEWIN, FORCECYG = [0 for _ in range(4)]

if 'CMK' in sys.argv:
    CMK = 1
    sys.argv.remove('CMK')

if 'FORCELIN' in sys.argv:
    FORCELIN = 1
    sys.argv.remove('FORCELIN')
elif 'FORCEWIN' in sys.argv:
    FORCEWIN = 1
    sys.argv.remove('FORCEWIN')
elif 'FORCECYG' in sys.argv:
    FORCECYG = 1
    sys.argv.remove('FORCECYG')


def what():
    if os.name == 'nt':
        if os.getenv('PWD'):
            ret = 'cyg'
        else:
            ret = 'win'
    else:
        ret = 'lin'

    if FORCELIN:
        ret = 'lin'
    elif FORCEWIN:
        ret = 'win'
    elif FORCECYG:
        ret = 'cyg'

    return ret


if what() == 'win' or what() == 'cyg':
    import site
    import shutil
    import tempfile
    import atexit
    import textwrap
    # noinspection PyUnresolvedReferences
    import py2exe
    import requests.certs
    from compileall import compile_file
    from py_compile import compile
elif 'py2exe' in sys.argv:
    print("You cannot use py2exe without a Windows Python")
    print("Rerun with the correct python version")
    sys.exit(1)


class check_ext(install_scripts):
    def run(self):
        install_scripts.run(self)
        for script in self.get_outputs():
            if script.endswith('.py') and os.name != 'nt':
                os.rename(script, script[:-3])


class winpty(build):
    def run(self):
        if what() == 'cyg':
            if not CMK:
                print("You are using Cygwin")
                print("Use `make' command instead of setup.py")
                print("E.g.: make PYTHONPATH=/cygdrive/c/Python34")
                sys.exit(1)

        build.run(self)


data_files = [('lib64', ['lib64/libsteam_api.dll',
                         'lib64/libsteam_api.so']),
              ('lib32', ['lib32/libsteam_api.dll',
                         'lib32/libsteam_api.so']),
              ('', ['interface.xml'])]

winpty_files = ['winpty/build/console.exe',
                'winpty/build/winpty.dll',
                'winpty/build/winpty-agent.exe']

console_programs = ['steam-tools.py']

def py2exe_options():
    if what() == 'win' or what() == 'cyg':
        options = {'py2exe':{'bundle_files':3,
                             'optimize':1,
                             'compressed':0,
                             'packages':'gi'}}

        return {'console':[{'script':'steam-tools.py',
                            # 'icon_resources': [(1, 'steam-tools.ico')]
                            },
                           {'script':'stlib/libsteam_wrapper.py'}],
                'options':options}
    else:
        return {}


def fix_cacert():
    requests_path = os.path.dirname(requests.__file__)
    cacert_file = os.path.join(requests_path, 'cacert.pem')
    certs_wrapper = os.path.join(requests_path, 'certs.py')

    if os.path.isfile(certs_wrapper + '.bak'):
        os.remove(certs_wrapper + '.bak')

    os.rename(certs_wrapper, certs_wrapper + '.bak')

    def fallback():
        os.remove(certs_wrapper)
        os.rename(certs_wrapper + '.bak', certs_wrapper)
        compile_file(certs_wrapper, force=True, quiet=1)

    atexit.register(fallback)

    with open(certs_wrapper, 'w') as f:
        f.write(textwrap.dedent("""\
            import os, sys

            def where():
                return os.path.join(os.path.dirname(sys.executable), 'cacert.pem')
        """))

    compile_file(certs_wrapper, force=True, quiet=1)

    data_files.append(('', [cacert_file]))

    if what() == 'cyg':
        data_files.append(('winpty', winpty_files))


def fix_gtk():
    gnome_dir = os.path.join(site.getsitepackages()[1], 'gnome')

    gtk_dirs = ['lib\\girepository-1.0',
                'share\\icons',
                'share\\themes\\MS-Windows-XP']

    for _file in os.listdir(gnome_dir):
        if _file.endswith('.dll'):
            data_files.append(('', [os.path.join(gnome_dir, _file)]))

    for _dir in gtk_dirs:
        for root, dirs, files in os.walk(os.path.join(gnome_dir, _dir)):
            for _file in files:
                data_files.append((root[len(gnome_dir) + 1:], [os.path.join(root, _file)]))


def fix_libsteam():
    tempDir = tempfile.mkdtemp()
    temp_libsteam = os.path.join(tempDir, 'libsteam_wrapper.py')

    shutil.copyfile('stlib/libsteam_wrapper.py', temp_libsteam)
    compiled_libsteam = compile(temp_libsteam)
    os.rename(compiled_libsteam, os.path.join(tempDir, 'libsteam_wrapper.pyc'))

    data_files.append(('', ['libsteam_wrapper.pyc']))


if what() == 'cyg' or what() == 'win':
    fix_cacert()
    fix_gtk()
    fix_libsteam()

if what() == 'cyg':
    data_files.append(('winpty', winpty_files))

setup(
        name='Steam Tools',
        version='GIT',
        description="Some useful tools for use with steam client or compatible programs, websites. (Windows & Linux)",
        author='Lara Maia',
        author_email='dev@lara.click',
        url='http://github.com/ShyPixie/steam-tools',
        license='GPL',
        data_files=data_files,
        scripts=console_programs,
        packages=['stlib'],
        cmdclass={'build':winpty,
                  'install_scripts':check_ext},
        **py2exe_options()
)
