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

import datetime

import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class WindowTimers:
    def __init__(self, signals, window):
        self.signals = signals
        self.window = window
        self.fake_app_elapsed_time = 0

    def statusBar_text_pushed_timer(self, context):
        self.window.statusBar.pop(context)
        return False


    def fake_app_timer(self):
        self.fake_app_elapsed_time += 1
        if self.signals.is_fake_app_running:
            if self.signals.fake_app.poll():
                self.window.update_statusBar("This is not a valid gameID.")
                self.window.new_dialog(Gtk.MessageType.ERROR,
                                         'Fake Steam App',
                                         'This is not a valid gameID.',
                                         "Please, check if you write correctly and try again.")
                self.signals.is_fake_app_running = False
                self.window.start.set_sensitive(True)
                self.window.stop.set_sensitive(False)
                self.window.fsa_currentGame.set_text('')
                self.window.fsa_currentTime.set_text('')
                return False
            else:
                self.window.fsa_currentGame.set_text(self.signals.fake_app_id)
                self.window.fsa_currentTime.set_text(str(datetime.timedelta(seconds=self.fake_app_elapsed_time)))
                return True
        else:
            return False
