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

CMK, FORCELIN, FORCEWIN, FORCECYG, FORCE64, FORCE32 = [0 for _ in range(6)]

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

if 'FORCE64' in sys.argv:
    FORCE64 = 1
    sys.argv.remove('FORCE64')
elif 'FORCE32' in sys.argv:
    FORCE32 = 1
    sys.argv.remove('FORCE32')


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


def arch():
    if sys.maxsize > 2 ** 32:
        ret = 64
    else:
        ret = 32

    if FORCE64:
        ret = 64
    elif FORCE32:
        ret = 32

    return ret


if what() == 'win' or what() == 'cyg':
    import site
    import atexit
    import textwrap
    # noinspection PyUnresolvedReferences
    import py2exe
    import requests.certs
    from compileall import compile_file

    if sys.maxsize > 2 ** 32:
        site.addsitedir('lib64')
    else:
        site.addsitedir('lib32')
elif 'py2exe' in sys.argv:
    print("You cannot use py2exe without a Windows Python")
    print("Rerun with the correct python version")
    sys.exit(1)


class CheckExtension(install_scripts):
    def run(self):
        install_scripts.run(self)
        for script in self.get_outputs():
            if script.endswith('.py') and os.name != 'nt':
                os.rename(script, script[:-3])


class Winpty(build):
    def run(self):
        if what() == 'cyg':
            if not CMK:
                print("You are using Cygwin")
                print("Use `make' command instead of setup.py")
                print("E.g.: make PYTHONPATH=/cygdrive/c/Python34")
                sys.exit(1)

        build.run(self)


data_files = [('lib64', [os.path.join('lib64', 'libsteam_api.dll'),
                         os.path.join('lib64', 'libsteam_api.so')]),
              ('lib32', [os.path.join('lib32', 'libsteam_api.dll'),
                         os.path.join('lib32', 'libsteam_api.so')]),
              ('ui', ['ui/interface.xml'])]

# Include icons
icons_path = os.path.join('ui', 'icons')
for icon in os.listdir(icons_path):
    data_files.append((icons_path, [os.path.join(icons_path, icon)]))

winpty_build_path = os.path.join('winpty', 'build')
winpty_files = [os.path.join(winpty_build_path, 'console.exe'),
                os.path.join(winpty_build_path, 'winpty.dll'),
                os.path.join(winpty_build_path, 'winpty-agent.exe')]

console_programs = ['steam-tools.py']


def py2exe_options():
    if what() == 'win' or what() == 'cyg':
        options = {'py2exe': {'bundle_files': 3,
                              'optimize': 1,
                              'compressed': 0,
                              'packages': ['pygobject',
                                           'psutil',
                                           'requests',
                                           'beautifulsoup4']}}

        return {'console': [{'script': 'steam-tools.py',
                             # 'icon_resources': [(1, 'steam-tools.ico')]
                             },
                            {'script': 'libsteam_wrapper.py'}],
                'options': options}
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
    if arch() == 64:
        gnome_dir = os.path.join('lib64', 'gnome')
    else:
        gnome_dir = os.path.join('lib32', 'gnome')

    gtk_dirs = [os.path.join('lib', 'girepository-1.0'),
                os.path.join('share', 'icons')]

    for _file in os.listdir(gnome_dir):
        if _file.endswith('.dll'):
            data_files.append(('', [os.path.join(gnome_dir, _file)]))

    for _dir in gtk_dirs:
        for root, dirs, files in os.walk(os.path.join(gnome_dir, _dir)):
            for _file in files:
                data_files.append((root[len(gnome_dir) + 1:], [os.path.join(root, _file)]))


if what() == 'cyg' or what() == 'win':
    fix_cacert()
    fix_gtk()

if what() == 'cyg':
    data_files.append(('winpty', winpty_files))

setup(name='Steam Tools',
      version='GIT',
      description="Some useful tools for use with steam client or compatible programs, websites. (Windows & Linux)",
      author='Lara Maia',
      author_email='dev@lara.click',
      url='http://github.com/ShyPixie/steam-tools',
      license='GPL',
      data_files=data_files,
      scripts=console_programs,
      packages=['stlib'],
      cmdclass={'build': Winpty,
                'install_scripts': CheckExtension},
      requires=['pygobject',
                'requests',
                'beautifulsoup4',
                'pycrypto'],
      **py2exe_options())
