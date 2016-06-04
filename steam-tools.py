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

import sys
from argparse import ArgumentParser

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject

from stlib.checklogins import checkLogins
from stlib.stconsole import STConsole

class WindowSignals:
    def __init__(self, parent):
        self.parent = parent

    def on_window_destroy(self, *args):
        Gtk.main_quit(*args)

class SteamTools:
    def __init__(self):
        builder = Gtk.Builder()
        builder.add_from_file("interface.xml")
        builder.connect_signals(WindowSignals(self))

        for _object in builder.get_objects():
            if issubclass(type(_object), Gtk.Buildable):
                name = Gtk.Buildable.get_name(_object)
                setattr(self, name, _object)

        self.mainWindow.show_all()

        self.logins = checkLogins(self)
        self.logins.start()

if __name__ == "__main__":
    aParser = ArgumentParser()
    aParser.add_argument('-c', '--cli', nargs='+')
    cParams = aParser.parse_args()

    if cParams.cli:
        STC = STConsole(cParams)
        sys.exit(0)

    GObject.threads_init()
    st = SteamTools()
    Gtk.main()
