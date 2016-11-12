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

import compileall
import importlib.machinery
import os
import sys
from distutils.command.install_scripts import install_scripts
from distutils.core import setup

__version_module_path__ = os.path.join('ui', 'version.py')
__version_class__ = importlib.machinery.SourceFileLoader('version', __version_module_path__)
version = __version_class__.load_module()

FORCELIN, FORCEWIN, FORCE64, FORCE32 = [0 for _ in range(4)]

if 'FORCELIN' in sys.argv:
    FORCELIN = 1
    sys.argv.remove('FORCELIN')
elif 'FORCEWIN' in sys.argv:
    FORCEWIN = 1
    sys.argv.remove('FORCEWIN')

if 'FORCE64' in sys.argv:
    FORCE64 = 1
    sys.argv.remove('FORCE64')
elif 'FORCE32' in sys.argv:
    FORCE32 = 1
    sys.argv.remove('FORCE32')


def what():
    if FORCEWIN or (os.name == 'nt' and not FORCELIN):
        return 'win'
    else:
        return 'lin'


def arch():
    if FORCE64 or (sys.maxsize > 2 ** 32 and not FORCE32):
        return 64
    else:
        return 32


libdir = 'lib' + str(arch())

if what() == 'win':
    if 'build' in sys.argv or 'install' in sys.argv:
        print("You cannot use build/install command with {}".format(what()))
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

    # Fix site for gi.repository
    temporary_site = tempfile.mktemp()
    shutil.copytree('gi_repository', os.path.join(temporary_site, 'gi'))
    site.addsitedir(temporary_site)
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


if what() == 'win':
    data_files = [('', [os.path.join(libdir, 'libsteam_api.dll')])]
else:
    data_files = [('', [os.path.join(libdir, 'libsteam_api.so')])]

data_files.append(('ui', [os.path.join('ui', 'interface.xml'),
                          os.path.join('ui', 'interface.css'),
                          os.path.join('ui', 'menu.xml')]))

# Include icons
icons_path = os.path.join('ui', 'icons')
for icon in os.listdir(icons_path):
    if os.path.isfile(os.path.join(icons_path, icon)):
        data_files.append((icons_path, [os.path.join(icons_path, icon)]))


def py2exe_options():
    if what() == 'win':
        packages = ['gi',
                    'psutil',
                    'requests',
                    'gevent',
                    'bs4']

        py2exe_options_ = {'bundle_files': 3,
                           'optimize': 1,
                           'compressed': 0,
                           'packages': packages}

        program_icon = os.path.join('ui', 'icons', 'steam-tools.ico')

        main_script = {'script': 'steam-tools.py',
                       'icon_resources': [(1, program_icon)],
                       'copyright': 'Copyright (C) 2016 Lara Maia',
                       'version': '{}.{}.{}'.format(version.__VERSION_MAJOR__,
                                                    version.__VERSION_MINOR__,
                                                    version.__VERSION_REVISION__),
                       }

        libsteam_script = {'script': os.path.join('stlib', 'libsteam_wrapper.py')}

        options = {'py2exe': py2exe_options_}

        return {'console': [main_script, libsteam_script],
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
    # Add dlls
    for file_ in os.listdir(libdir):
        if file_.endswith('.dll'):
            data_files.append(('', [os.path.join(libdir, file_)]))
        elif file_.endswith('.pyd'):
            shutil.copy(os.path.join(libdir, file_),
                        os.path.join(temporary_site, 'gi'))

    # Add typelib
    typelib_directory = os.path.join(libdir, 'girepository-1.0')
    for file_ in os.listdir(typelib_directory):
        if file_.endswith('.typelib'):
            data_files.append((os.path.join('lib', 'girepository-1.0'),
                               [os.path.join(typelib_directory, file_)]))

    # Add icons
    for root, dirs, files in os.walk(os.path.join('ui', 'icons', 'Adwaita')):
        icons_path = os.path.join('share', 'icons', 'Adwaita', root[17:])
        for file_ in files:
            data_files.append((icons_path, [os.path.join(root, file_)]))


if what() == 'win':
    fix_cacert()
    fix_gtk()
    fix_gevent()

version_extra = what().upper() + str(arch())

with open('version.py', 'w') as file_:
    file_.write('__VERSION_EXTRA__ = "{}"'.format(version_extra))

compileall.compile_file('version.py', legacy=True)
os.remove('version.py')
data_files.append(('', ['version.pyc']))

setup(
        name='Steam Tools',

        version='{}.{}.{}-{}'.format(version.__VERSION_MAJOR__,
                                     version.__VERSION_MINOR__,
                                     version.__VERSION_REVISION__,
                                     version_extra),

        description="Some useful tools for use with steam client or compatible programs, websites. (Windows & Linux)",
        author='Lara Maia',
        author_email='dev@lara.click',
        url='http://github.com/ShyPixie/steam-tools',
        license='GPL',
        data_files=data_files,

        scripts=['steam-tools.py'],

        packages=['stlib',
                  'ui'],

        cmdclass={'install_scripts': CheckExtension},

        requires=['pygobject',
                  'requests',
                  'gevent',
                  'beautifulsoup4',
                  'pycrypto'],

        **py2exe_options()
)
