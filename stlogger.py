#!/usr/bin/env python
# Lara Maia <dev@lara.click> 2015

import os
import logging

def init(fileName):
    xdg_dir = os.getenv('XDG_CONFIG_HOME', os.path.join(os.path.expanduser('~'), '.config'))
    path = os.path.join(xdg_dir, 'steam-tools')

    if not os.path.isdir(path):
        os.mkdir(path)

    logger = logging.getLogger("root")
    logger.setLevel(logging.DEBUG)

    file = logging.FileHandler(os.path.join(path, fileName))
    file.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
    file.setLevel(logging.DEBUG)
    logger.addHandler(file)

    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter('%(message)s'))
    console.setLevel(logging.INFO)
    logger.addHandler(console)

    httpfile = logging.FileHandler(os.path.join(path, 'requests_'+fileName))
    httpfile.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
    httpfile.setLevel(logging.DEBUG)

    requests = logging.getLogger("requests.packages.urllib3")
    requests.setLevel(logging.DEBUG)
    requests.removeHandler("root")
    requests.addHandler(httpfile)

    return logger
