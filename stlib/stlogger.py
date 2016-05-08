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
import tempfile
from shutil import get_terminal_size

class ColoredFormatter(logging.Formatter):
    def format(self, log):
        colorMap = {
            'INFO': 37,
            'WARNING': 33,
            'ERROR': 35,
            'CRITICAL': 31,
        }

        colorNumber = colorMap.get(log.levelname, 37)

        if os.name == 'nt' and not os.getenv('PWD'):
            msg = ' --> {}'.format(log.getMessage())
        else:
            msg = '\033[32m --> \033[{}m{}\033[m'.format(colorNumber, log.getMessage())

        return msg

def encoder(buffer, error='replace'):
    writer = codecs.getwriter(locale.getpreferredencoding())
    return writer(buffer, error)

def cfixer(end='\n'):
    tsize = get_terminal_size()[0]
    print(('{:'+str(tsize-1)+'s}').format(''), end=end, flush=True)

def cmsg(*objs, sep='', end='\n', out=sys.stdout):
    print(*objs, sep=sep, end=end, file=encoder(out.buffer), flush=True)

def getLogger(logFileLevel):
    dataDir = tempfile.gettempdir()

    logFileName = os.path.splitext(os.path.basename(sys.argv[0]))[0]+'.log'
    logFilePath = os.path.join(dataDir, 'steam-tools')
    os.makedirs(logFilePath, exist_ok=True)

    logging.VERBOSE = 15
    logging.TRACE = 5
    logging.addLevelName(logging.VERBOSE, 'VERBOSE')
    logging.addLevelName(logging.TRACE, 'TRACE')

    ### --- Internal logger control --- ###
    logger = logging.getLogger("root")
    logger.verbose = lambda msg, *args: logger._log(logging.VERBOSE, msg, args)
    logger.trace = lambda msg, *args: logger._log(logging.TRACE, msg, args)
    logger.setLevel(logging.TRACE)
    ### ### ### ### ### ### ### ### ### ###

    ### --- Logfile Handler --- ###
    logFile = logging.handlers.RotatingFileHandler(os.path.join(logFilePath, logFileName),
                                                   backupCount=1,
                                                   encoding='utf-8')
    logFile.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
    logFile.setLevel(eval('logging.'+logFileLevel.upper()))
    logFile.doRollover()
    logger.addHandler(logFile)
    ### ### ### ### ### ### ### ###

    ### --- Console Handler --- ###
    console = logging.StreamHandler(encoder(sys.stdout.buffer))
    console.setFormatter(ColoredFormatter())
    console.setLevel(logging.INFO)
    logger.addHandler(console)
    ### ### ### ### ### ### ### ###

    ### --- Requests Logfile handler --- ###
    httpfile = logging.handlers.RotatingFileHandler(os.path.join(logFilePath, 'requests_'+logFileName),
                                                    backupCount=1,
                                                    encoding='utf-8')
    httpfile.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
    httpfile.setLevel(logging.DEBUG)
    httpfile.doRollover()

    requests = logging.getLogger("requests.packages.urllib3")
    requests.setLevel(logging.DEBUG)
    requests.removeHandler("root")
    requests.addHandler(httpfile)
    ### ### ### ### ### ### ### ### ### ###

    return logger

def closeAll():
    logger = logging.getLogger('root')
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)
