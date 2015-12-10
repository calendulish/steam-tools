#!/usr/bin/env python
# Lara Maia <dev@lara.click> 2015

import os, sys
import logging
from configparser import RawConfigParser

logger = logging.getLogger('root')

def init(fileName):
    config = RawConfigParser()
    xdg_dir = os.getenv('XDG_CONFIG_HOME', os.path.join(os.path.expanduser('~'), '.config'))
    config_file = os.path.join(xdg_dir, 'steam-tools', fileName)

    if not os.path.isdir(os.path.dirname(config_file)):
        os.mkdir(os.path.dirname(config_file))

    if os.path.isfile(config_file):
        config.read(config_file)
    elif os.path.isfile(fileName):
        config.read(fileName)
    else:
        logger.critical("Configuration file not found. These is the search paths:")
        logger.critical(" - {}".format(os.path.join(os.getcwd(), 'steam-card-farming.config')))
        logger.critical(" - {}".format(config_file))
        logger.critical("Please, copy the example file or create a new with your data.")
        exit(1)

    return config
