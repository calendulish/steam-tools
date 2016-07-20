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
import time

import ui


def status_bar_text_pushed_timer(context):
    window = ui.globals.Window.main
    window.status_bar.pop(context)
    return False


def fake_app_timer(start_time):
    window = ui.globals.Window.main
    elapsed_seconds = round(time.time() - start_time)
    elapsed_time = datetime.timedelta(seconds=elapsed_seconds)

    if ui.globals.FakeApp.is_running:
        if not ui.libsteam.is_wrapper_running():
            window.update_status_bar("This is not a valid gameID.")
            window.new_dialog(ui.Gtk.MessageType.ERROR,
                              'Fake Steam App',
                              'This is not a valid gameID.',
                              "Please, check if you write correctly and try again.")

            ui.globals.FakeApp.is_running = False
            window.start.set_sensitive(True)
            window.stop.set_sensitive(False)
            window.fake_app_current_game.set_text('')
            window.fake_app_current_time.set_text('')

            return False
        else:
            window.fake_app_current_game.set_text(ui.globals.FakeApp.id)
            window.fake_app_current_time.set_text(str(elapsed_time))

            return True
    else:
        return False
