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

import codecs
import locale
import logging
import logging.handlers
import os
import shutil
import sys
import tempfile

# NEVER import full stlib module here!!! (cyclic)
from stlib import config as stconfig


class ColoredFormatter(logging.Formatter):
    def format(self, log):
        color_map = {
            'INFO': 37,
            'WARNING': 33,
            'ERROR': 35,
            'CRITICAL': 31,
        }

        color_number = color_map.get(log.levelname, 37)

        if os.name == 'nt' and not os.getenv('PWD'):
            msg = ' --> {}'.format(log.getMessage())
        else:
            msg = '\033[32m --> \033[{}m{}\033[m'.format(color_number, log.getMessage())

        return msg.replace('\n', '\n     ')


def encoder(buffer, error='replace'):
    writer = codecs.getwriter(locale.getpreferredencoding())
    return writer(buffer, error)


def console_fixer(end='\n'):
    tsize = shutil.get_terminal_size()[0]
    print(('{:' + str(tsize - 1) + 's}').format(''), end=end, flush=True)


def console_msg(*objs, sep='', end='\n', out=sys.stdout):
    if end == '\r':
        console_fixer(end)

    print(*objs, sep=sep, end=end, file=encoder(out.buffer), flush=True)


# noinspection PyProtectedMember
def get_logger():
    config_parser = stconfig.read()
    data_dir = tempfile.gettempdir()

    log_file_name = os.path.splitext(os.path.basename(sys.argv[0]))[0] + '.log'
    log_file_path = os.path.join(data_dir, 'steam-tools')
    os.makedirs(log_file_path, exist_ok=True)

    logging.VERBOSE = 15
    logging.TRACE = 5
    logging.addLevelName(logging.VERBOSE, 'VERBOSE')
    logging.addLevelName(logging.TRACE, 'TRACE')

    console_level = config_parser.get('Debug', 'consoleLevel', fallback='info')
    log_file_level = config_parser.get('Debug', 'logFileLevel', fallback='verbose')

    # --- Internal logger control --- #
    logger = logging.getLogger('SteamTools')
    logger.verbose = lambda msg, *args: logger._log(logging.VERBOSE, msg, args)
    logger.trace = lambda msg, *args: logger._log(logging.TRACE, msg, args)
    logger.setLevel(logging.TRACE)
    # --- ~ --- ~ --- ~ --- ~ --- ~ --- #

    # --- Logfile Handler --- #
    log_file = logging.handlers.RotatingFileHandler(os.path.join(log_file_path, log_file_name),
                                                    backupCount=1,
                                                    encoding='utf-8')
    log_file.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
    log_file.setLevel(eval('logging.' + log_file_level.upper()))
    log_file.doRollover()
    logger.addHandler(log_file)
    # --- ~ --- ~ --- ~ --- ~ #

    # --- Console Handler --- #
    console = logging.StreamHandler(encoder(sys.stdout.buffer))
    console.setFormatter(ColoredFormatter())
    console.setLevel(eval('logging.' + console_level.upper()))
    logger.addHandler(console)
    # --- ~ --- ~ --- ~ --- ~ #

    # --- Requests Logfile handler --- #
    httpfile = logging.handlers.RotatingFileHandler(os.path.join(log_file_path, 'requests_' + log_file_name),
                                                    backupCount=1,
                                                    encoding='utf-8')
    httpfile.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
    httpfile.setLevel(logging.DEBUG)
    httpfile.doRollover()

    requests = logging.getLogger("requests.packages.urllib3")
    requests.setLevel(logging.DEBUG)
    # requests.removeHandler('SteamTools')
    requests.addHandler(httpfile)
    # --- ~ --- ~ --- ~ --- ~ --- ~ --- #

    # -- stlib --- #
    stlib = logging.getLogger('stlib')
    stlib.setLevel(logging.DEBUG)
    stlib.addHandler(console)

    return logger
