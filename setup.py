#!/usr/bin/env python

import os, sys

from distutils.core import setup
from distutils.command.build import build
from distutils.command.install_scripts import install_scripts

CMK, FORCELIN, FORCEWIN, FORCECYG = [ 0 for _ in range(4) ]

if 'CMK' in sys.argv:
    CMK=1
    sys.argv.remove('CMK')

if 'FORCELIN' in sys.argv:
    FORCELIN=1
    sys.argv.remove('FORCELIN')
elif 'FORCEWIN' in sys.argv:
    FORCEWIN=1
    sys.argv.remove('FORCEWIN')
elif 'FORCECYG' in sys.argv:
    FORCECYG=1
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
    import py2exe
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

data_files=[('lib64', ['lib64/libsteam_api.dll']),
            ('lib32', ['lib32/libsteam_api.dll'])]

winpty_files = [ 'winpty/build/console.exe',
                 'winpty/build/winpty.dll',
                 'winpty/build/winpty-agent.exe']

console_programs=['fake-steam-app.py',
                  'steam-card-farming.py',
                  'steamgifts-bump.py',
                  'steamgifts-join.py']

def py2exe_options():
    if what() == 'win' or what() == 'cyg':
        options = {'py2exe': {'bundle_files': 3,
                              'optimize': 1,
                              'compressed': 0}}

        return {'console': console_programs,
                'options': options}
    else:
        return {}

if what() == 'cyg':
    data_files.append(('winpty', winpty_files))

setup(
    name='Steam Tools',
    version='1.0',
    description="Some useful tools for use with steam client or compatible programs, websites. (Windows & Linux)",
    author='Lara Maia',
    author_email='dev@lara.click',
    url='http://github.com/ShyPixie/steam-tools',
    data_files=data_files,
    scripts=console_programs,
    packages=['stlib'],
    cmdclass = {'build': winpty,
                'install_scripts': check_ext},
    **py2exe_options()
    )
