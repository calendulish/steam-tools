#!/usr/bin/env python

import os
from distutils.core import setup
from distutils.command.install_scripts import install_scripts
if os.name == 'nt':
    import py2exe

class check_ext(install_scripts):
    def run(self):
        install_scripts.run(self)
        for script in self.get_outputs():
            if script.endswith('.py') and os.name != 'nt':
                os.rename(script, script[:-3])

data_files=[('lib64', ['lib64/libsteam_api.dll']),
            ('lib32', ['lib32/libsteam_api.dll']),]

console_programs=['fake-steam-app.py',
                  'steam-card-farming.py',
                  'steamgifts-bump.py',
                  'steamgifts-join.py',
                    ]

def py2exe_options():
    if os.name == 'nt':
        options = {'py2exe': {'bundle_files': 3,
                              'optimize': 1,
                              'compressed': 0,},}

        return {'console': console_programs,
                'options': options,}
    else:
        return {}

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
    cmdclass = {'install_scripts': check_ext},
    **py2exe_options()
    )
