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
# The pages are in that order:
# : PG :    Module    :
# :  0 : Card Farming :
# :  1 :   SG Bump    :
# :  2 :   SG Join    :
# :  3 :   SC Join    :


import locale
import time

import ui


class StartModule:
    def __init__(self):
        self.window = ui.globals.Window.main

    def fake_app(self):
        self.window.update_status_bar("Preparing. Please wait...")
        ui.globals.FakeApp.id = self.window.fake_app_game_id.get_text().strip()

        if not ui.globals.FakeApp.id:
            self.window.update_status_bar("No AppID found!")
            self.window.new_dialog(ui.Gtk.MessageType.ERROR,
                                   'Fake Steam App',
                                   'No AppID found!',
                                   "You must specify an AppID!")
        else:
            self.window.start.set_sensitive(False)
            # Prevents bad behaviour when the user click
            # on the stop button before the fake_app is ready
            self.window.stop.set_sensitive(False)

            if ui.libsteam.is_steam_running():
                ui.globals.FakeApp.process = ui.libsteam.run_wrapper(ui.globals.FakeApp.id)
                ui.globals.FakeApp.is_running = True
                self.window.stop.set_sensitive(True)
            else:
                self.window.update_status_bar("Unable to locate a running instance of steam.")
                self.window.new_dialog(ui.Gtk.MessageType.ERROR,
                                       'Fake Steam App',
                                       'Unable to locate a running instance of steam.',
                                       "Please, start the Steam Client and try again.")
                self.window.start.set_sensitive(True)

        start_time = time.time()
        ui.GLib.timeout_add_seconds(1, ui.timers.fake_app_timer, start_time)


class StopModule:
    def __init__(self):
        self.window = ui.globals.Window.main

    def fake_app(self):
        self.window.stop.set_sensitive(False)
        # Prevents bad behaviour when the user click
        # on the start button before the fake_app is ready
        self.window.start.set_sensitive(False)
        self.window.update_status_bar("Waiting to fakeapp terminate.")
        ui.libsteam.stop_wrapper()

        if ui.globals.FakeApp.process.returncode is None:
            error = ui.globals.FakeApp.process.stderr.read()
            self.window.new_dialog(ui.Gtk.MessageType.ERROR,
                                   'Fake Steam App',
                                   'An Error occured ({}).'.format(ui.globals.FakeApp.process.returncode),
                                   error.decode(locale.getpreferredencoding()))

        ui.globals.FakeApp.is_running = False
        self.window.update_status_bar("Done!")
        self.window.start.set_sensitive(True)
        self.window.fake_app_current_game.set_text('')
        self.window.fake_app_current_time.set_text('')


class WindowSignals:
    def __init__(self):
        self.window = ui.globals.Window.main
        self.start_module = StartModule()
        self.stop_module = StopModule()

    def on_window_destroy(self, *args):
        ui.Gtk.main_quit(*args)

    def on_start_clicked(self, data):
        current_page = self.window.tabs.get_current_page()
        if current_page == 0:
            pass
        elif current_page == 1:
            self.start_module.fake_app()
        elif current_page == 2:
            pass
        elif current_page == 3:
            pass
        elif current_page == 4:
            pass

    def on_stop_clicked(self, data):
        current_page = self.window.tabs.get_current_page()
        if current_page == 0:
            pass
        elif current_page == 1:
            self.stop_module.fake_app()
        elif current_page == 2:
            pass
        elif current_page == 3:
            pass
        elif current_page == 4:
            pass

    def on_tabs_switch_page(self, object, page, current_page):
        if current_page == 0:
            pass
        elif current_page == 1:
            if ui.globals.FakeApp.is_running:
                self.window.start.set_sensitive(False)
                self.window.stop.set_sensitive(True)
            else:
                self.window.start.set_sensitive(True)
                self.window.stop.set_sensitive(False)
        elif current_page == 2:
            pass
        elif current_page == 3:
            pass
        elif current_page == 4:
            pass

    def on_status_bar_text_pushed(self, object, context, text):
        ui.GLib.timeout_add_seconds(10, ui.timers.status_bar_text_pushed_timer, context)

    def on_select_profile_button_toggled(self, object, id):
        if object.get_active():
            ui.globals.Window.profile = id
