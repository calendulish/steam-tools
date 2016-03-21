#!/usr/bin/env python

import os
from distutils.core import setup
if os.name == 'nt':
    import py2exe

data_files=[('lib64', ['lib64/libsteam_api.dll']),
            ('lib32', ['lib32/libsteam_api.dll']),
            ]
            
console_programs=['fake-steam-app.py',
                  'steam-card-farming.py',
                  'steamgifts-bump.py',
                  'steamgifts-join.py',
                    ]

py2exe_options = {'py2exe': {
                          'bundle_files': 3,
                          'optimize': 1,
                          'compressed': 0,
                          },
                }

setup(
    name='Steam Tools',
    version='1.0',
    description="Some useful tools for use with steam client or compatible programs, websites. (Windows & Linux)",
    author='Lara Maia',
    author_email='dev@lara.click',
    url='http://github.com/ShyPixie/steam-tools',
    options = py2exe_options,
    data_files=data_files,
    console=console_programs,
    )