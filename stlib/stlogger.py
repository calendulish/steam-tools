#!/usr/bin/env python
#
# Lara Maia <dev@lara.click> 2015
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
import codecs
import logging
import logging.handlers

sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())

def init(fileName):
    if os.name == 'nt':
        conf_dir = 'APPDATA'
    else:
        conf_dir = '.config'

    xdg_dir = os.getenv('XDG_CONFIG_HOME', os.path.join(os.path.expanduser('~'), conf_dir))
    path = os.path.join(xdg_dir, 'steam-tools')

    os.makedirs(path, exist_ok=True)

    logger = logging.getLogger("root")
    logger.setLevel(logging.DEBUG)

    file = logging.handlers.RotatingFileHandler(os.path.join(path, fileName), backupCount=1, encoding='utf-8')
    file.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
    file.setLevel(logging.DEBUG)
    file.doRollover()
    logger.addHandler(file)

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(logging.Formatter('%(message)s'))
    console.setLevel(logging.INFO)
    logger.addHandler(console)

    httpfile = logging.handlers.RotatingFileHandler(os.path.join(path, 'requests_'+fileName), backupCount=1, encoding='utf-8')
    httpfile.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
    httpfile.setLevel(logging.DEBUG)
    httpfile.doRollover()

    requests = logging.getLogger("requests.packages.urllib3")
    requests.setLevel(logging.DEBUG)
    requests.removeHandler("root")
    requests.addHandler(httpfile)

    return logger
