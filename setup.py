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
    elif sys.platform == 'cygwin':
        ret = 'cyg'
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
    if 'build' in sys.argv or 'install' in sys.argv:
        print("You cannot use build/install command with {}".format(what()))
        sys.exit(1)

    if os.name == 'posix':
        print("You cannot build for cygwin using linux python")
        print("Use `make' command instead of setup.py")
        print("E.g.: make PYTHONPATH=/cygdrive/c/Python34")
        sys.exit(1)

    import site
    import atexit
    import shutil
    import tempfile
    import textwrap
    # noinspection PyUnresolvedReferences
    import py2exe
    import requests.certs
    from compileall import compile_file

    temporary_directory = tempfile.mktemp()
    shutil.copytree('gi_repository', os.path.join(temporary_directory, 'gi'))
    site.addsitedir(temporary_directory)
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


if what() == 'win' or what() == 'cyg':
    if arch() == 64:
        data_files = [('lib64', [os.path.join('lib64', 'libsteam_api.dll')])]
    else:
        data_files = [('lib32', [os.path.join('lib32', 'libsteam_api.dll')])]
else:
    if arch() == 64:
        data_files = [('', [os.path.join('lib64', 'libsteam_api.so')])]
    else:
        data_files = [('', [os.path.join('lib32', 'libsteam_api.so')])]

data_files.append(('ui', [os.path.join('ui', 'interface.xml'),
                          os.path.join('ui', 'interface.css'),
                          os.path.join('ui', 'menu.xml')]))

# Include icons
icons_path = os.path.join('ui', 'icons')
for icon in os.listdir(icons_path):
    if os.path.isfile(os.path.join(icons_path, icon)):
        data_files.append((icons_path, [os.path.join(icons_path, icon)]))

# Include winpty files
if what() == 'cyg':
    winpty_build_path = os.path.join('winpty', 'build')
    data_files.append(('winpty', [os.path.join(winpty_build_path, 'console.exe'),
                                  os.path.join(winpty_build_path, 'winpty.dll'),
                                  os.path.join(winpty_build_path, 'winpty-agent.exe')]))

console_programs = ['steam-tools.py']


def py2exe_options():
    if what() == 'win' or what() == 'cyg':
        options = {'py2exe': {'bundle_files': 3,
                              'optimize': 1,
                              'compressed': 0,
                              'packages': ['pygobject',
                                           'psutil',
                                           'requests',
                                           'gevent',
                                           'beautifulsoup4']}}

        return {'console': [{'script': 'steam-tools.py',
                             'icon_resources': [(1, os.path.join('ui', 'icons', 'steam-tools.ico'))]
                             },
                            {'script': os.path.join('stlib', 'libsteam_wrapper.py')}],
                'options': options}
    else:
        return {}


def fix_gevent():
    for site_ in site.getsitepackages():
        full_path = os.path.join(site_, 'gevent')
        if os.path.isdir(full_path):
            for file_ in os.listdir(full_path):
                if file_ == '_util_py2.py':
                    os.remove(os.path.join(full_path, file_))

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


def fix_gtk():
    if arch() == 64:
        gnome_dir = os.path.join('lib64', 'gnome')
    else:
        gnome_dir = os.path.join('lib32', 'gnome')

    gtk_dirs = [os.path.join('gi_repository'),
                os.path.join('ui', 'icons')]

    for file_ in os.listdir(gnome_dir):
        if file_.endswith('.dll'):
            data_files.append(('', [os.path.join(gnome_dir, file_)]))

    for dir_ in gtk_dirs:
        for root, dirs, files in os.walk(dir_):
            for file_ in files:
                data_files.append((root[len(gnome_dir) + 1:], [os.path.join(root, file_)]))


if what() == 'cyg' or what() == 'win':
    fix_cacert()
    fix_gtk()
    fix_gevent()

setup(name='Steam Tools',
      version='GIT',
      description="Some useful tools for use with steam client or compatible programs, websites. (Windows & Linux)",
      author='Lara Maia',
      author_email='dev@lara.click',
      url='http://github.com/ShyPixie/steam-tools',
      license='GPL',
      data_files=data_files,
      scripts=console_programs,
      packages=['stlib',
                'ui'],
      cmdclass={'build': Winpty,
                'install_scripts': CheckExtension},
      requires=['pygobject',
                'requests',
                'gevent',
                'beautifulsoup4',
                'pycrypto'],
      **py2exe_options())
