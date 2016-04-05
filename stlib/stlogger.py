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
import codecs
import locale
import logging
import logging.handlers
from shutil import get_terminal_size

def encoder(buffer, error='replace'):
    writer = codecs.getwriter(locale.getpreferredencoding())
    return writer(buffer, error)

def cfixer(end='\n'):
    tsize = get_terminal_size()[0]
    print(('{:'+str(tsize-1)+'s}').format(''), end=end, flush=True)

def cmsg(*objs, sep='', end='\n', out=sys.stdout):
    print(*objs, sep=sep, end=end, file=encoder(out.buffer), flush=True)

def getLogger():
    if os.name == 'nt':
        dataDir = os.getenv('LOCALAPPDATA')
    else:
        dataDir = os.getenv('XDG_CONFIG_HOME', os.path.join(os.path.expanduser('~'), '.config'))

    logFile = os.path.splitext(os.path.basename(sys.argv[0]))[0]+'.log'
    logPath = os.path.join(dataDir, 'steam-tools')
    os.makedirs(logPath, exist_ok=True)

    logger = logging.getLogger("root")
    logger.setLevel(logging.DEBUG)

    file = logging.handlers.RotatingFileHandler(os.path.join(logPath, logFile), backupCount=1, encoding='utf-8')
    file.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
    file.setLevel(logging.DEBUG)
    file.doRollover()
    logger.addHandler(file)

    console = logging.StreamHandler(encoder(sys.stdout.buffer))
    console.setFormatter(logging.Formatter('%(message)s'))
    console.setLevel(logging.INFO)
    logger.addHandler(console)

    httpfile = logging.handlers.RotatingFileHandler(os.path.join(logPath, 'requests_'+logFile), backupCount=1, encoding='utf-8')
    httpfile.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
    httpfile.setLevel(logging.DEBUG)
    httpfile.doRollover()
    logger.addHandler(httpfile)

    requests = logging.getLogger("requests.packages.urllib3")
    requests.setLevel(logging.DEBUG)
    requests.removeHandler("root")
    requests.addHandler(httpfile)

    return logger

def closeAll():
    logger = logging.getLogger('root')
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)
