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
import subprocess

import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib

import ui

class WindowSignals:
    def __init__(self, window):
        self.window = window
        self.timers = ui.timers.WindowTimers(self, window)
        self.libsteam = ui.libsteam.LibSteam()
        self.is_fake_app_running = False

    def on_window_destroy(self, *args):
        Gtk.main_quit(*args)

    def on_start_clicked(self, data):
        current_page = self.window.tabs.get_current_page()
        if current_page == 0:
            pass
        elif current_page == 1:
            self.window.update_statusBar("Preparing. Please wait...")
            self.fake_app_id = self.window.fsa_appID.get_text().strip()
            if not self.fake_app_id:
                self.window.update_statusBar("No AppID found!")
                self.window.new_dialog(Gtk.MessageType.ERROR,
                                         'Fake Steam App',
                                         'No AppID found!',
                                         "You must specify an AppID!")
            else:
                self.window.start.set_sensitive(False)
                # Prevents bad behaviour when the user click
                # on the stop button before the fake_app is ready
                self.window.stop.set_sensitive(False)

                if self.libsteam.is_steam_running():
                    self.fake_app = self.libsteam.run_wrapper(self.fake_app_id)
                    self.is_fake_app_running = True
                    self.window.stop.set_sensitive(True)
                else:
                    self.window.update_statusBar("Unable to locate a running instance of steam.")
                    self.window.new_dialog(Gtk.MessageType.ERROR,
                                             'Fake Steam App',
                                             'Unable to locate a running instance of steam.',
                                             "Please, start the Steam Client and try again.")
                    self.window.start.set_sensitive(True)
            #### FIXME
            self.timers.fake_app_elapsed_time = 0
            GLib.timeout_add_seconds(1, self.timers.fake_app_timer)

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
            self.window.stop.set_sensitive(False)
            # Prevents bad behaviour when the user click
            # on the start button before the fake_app is ready
            self.window.start.set_sensitive(False)
            self.is_fake_app_running = False
            self.fake_app.terminate()
            self.window.update_statusBar("Waiting to fakeapp terminate.")
            try:
                self.fake_app.communicate(timeout=20)
            except subprocess.TimeoutExpired:
                self.window.update_statusBar("Force Killing fakeapp")
                self.fake_app.kill()
                self.fake_app.communicate()

            if self.fake_app.returncode is None:
                error = self.fake_app.stderr.read()
                self.window.new_dialog(Gtk.MessageType.ERROR,
                                         'Fake Steam App',
                                         'An Error occured ({}).'.format(self.fake_app.returncode),
                                         error.decode(locale.getpreferredencoding()))
            self.window.update_statusBar("Done!")
            self.window.start.set_sensitive(True)
            self.window.fsa_currentGame.set_text('')
            self.window.fsa_currentTime.set_text('')

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
            if self.is_fake_app_running is True:
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

    def on_statusBar_text_pushed(self, object, context, text):
        GLib.timeout_add_seconds(10, self.timers.statusBar_text_pushed_timer, context)

    def on_select_profile_button_toggled(self, object, id):
        if object.get_active():
            self.window.selected_profile = id
