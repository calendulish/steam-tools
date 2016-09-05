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
import stlib


class WindowSignals:
    def __init__(self):
        self.window = ui.globals.Window.main
        self.config_parser = stlib.config.read()

    def on_window_destroy(self, *args):
        self.window.main_window.hide()
        ui.Gtk.main_quit(*args)

    def on_about_activate(self, button):
        self.window.about_dialog.run()
        self.window.about_dialog.hide()

    def on_start_clicked(self, button):
        current_page = self.window.tabs.get_current_page()
        if current_page == 0:
            self.on_card_farming_start()
        elif current_page == 1:
            self.on_fake_app_start()
        elif current_page == 2:
            pass
        elif current_page == 3:
            pass
        elif current_page == 4:
            pass

    def on_stop_clicked(self, button):
        current_page = self.window.tabs.get_current_page()
        if current_page == 0:
            self.on_card_farming_stop()
        elif current_page == 1:
            self.on_fake_app_stop()
        elif current_page == 2:
            pass
        elif current_page == 3:
            pass
        elif current_page == 4:
            pass

    def on_tabs_switch_page(self, tab, box, current_page):
        if current_page == 0:
            if ui.globals.CardFarming.is_running:
                self.window.start.set_sensitive(False)
                self.window.stop.set_sensitive(True)
            else:
                self.window.start.set_sensitive(True)
                self.window.stop.set_sensitive(False)
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

    def on_card_farming_start(self):
        self.window.start.set_sensitive(False)
        self.window.stop.set_sensitive(False)
        dry_run = self.config_parser.getboolean('Debug', 'DryRun', fallback=False)

        if ui.globals.FakeApp.is_running:
            self.window.new_dialog(ui.Gtk.MessageType.ERROR,
                                   'Card Farming',
                                   'Please, stop the Fake App',
                                   'Unable to start Card Farming if a fake app is already running.')
            self.window.start.set_sensitive(True)
            return None

        if ui.libsteam.is_steam_running():
            self.window.update_status_bar("Preparing. Please wait...")
            self.window.spinner.start()
            ui.globals.CardFarming.is_running = True

            # FIXME: Very slow function for GUI mode
            ui.card_farming.get_badges()

            if self.config_parser.getboolean('Config', 'MostValuableFirst', fallback=True):
                ui.card_farming.get_card_prices()

            ui.globals.logger.warning('Ready to start.')
            self.window.spinner.stop()

            start_time = time.time()
            ui.GLib.timeout_add_seconds(1, ui.timers.card_farming_time_timer, start_time)

            ui.timers.card_farming_timer(dry_run)
            ui.GLib.timeout_add_seconds(40, ui.timers.card_farming_timer)

            self.window.stop.set_sensitive(True)
        else:
            self.window.update_status_bar("Unable to locate a running instance of steam.")
            self.window.new_dialog(ui.Gtk.MessageType.ERROR,
                                   'Card Farming',
                                   'Unable to locate a running instance of steam.',
                                   "Please, start the Steam Client and try again.")
            self.window.start.set_sensitive(True)

    def on_card_farming_stop(self):
        self.window.start.set_sensitive(False)
        self.window.stop.set_sensitive(False)

        self.window.update_status_bar("Waiting to card farming terminate.")
        ui.globals.CardFarming.is_running = False
        ui.libsteam.stop_wrapper()
        ui.globals.FakeApp.is_running = False
        ui.globals.FakeApp.id = None
        self.window.fake_app_current_game.set_text('')
        self.window.fake_app_current_time.set_text('')
        self.window.card_farming_current_game.set_text('')
        self.window.card_farming_card_left.set_text('')
        self.window.card_farming_current_game_time.set_text('')
        self.window.card_farming_total_time.set_text('')

        self.window.update_status_bar("Done!")
        self.window.start.set_sensitive(True)

    def on_fake_app_start(self):
        self.window.start.set_sensitive(False)
        self.window.stop.set_sensitive(False)

        self.window.update_status_bar("Preparing. Please wait...")
        self.window.spinner.start()
        ui.globals.FakeApp.id = self.window.fake_app_game_id.get_text().strip()

        if not ui.globals.FakeApp.id:
            self.window.update_status_bar("No AppID found!")
            self.window.new_dialog(ui.Gtk.MessageType.ERROR,
                                   'Fake Steam App',
                                   'No AppID found!',
                                   "You must specify an AppID!")
            self.window.start.set_sensitive(True)
        else:
            if ui.libsteam.is_steam_running():
                ui.libsteam.run_wrapper(ui.globals.FakeApp.id)
                ui.globals.FakeApp.is_running = True
                self.window.stop.set_sensitive(True)
            else:
                self.window.update_status_bar("Unable to locate a running instance of steam.")
                self.window.new_dialog(ui.Gtk.MessageType.ERROR,
                                       'Fake Steam App',
                                       'Unable to locate a running instance of steam.',
                                       "Please, start the Steam Client and try again.")
                self.window.start.set_sensitive(True)

        self.window.spinner.stop()
        start_time = time.time()
        ui.GLib.timeout_add_seconds(1, ui.timers.fake_app_timer, start_time)

    def on_fake_app_stop(self):
        self.window.stop.set_sensitive(False)
        self.window.start.set_sensitive(False)

        if ui.globals.CardFarming.is_running:
            self.window.new_dialog(ui.Gtk.MessageType.ERROR,
                                   'Fake Steam App',
                                   'This function is not available now',
                                   'Unable to stop Fake App because it was started by Card Farming module.\n' +
                                   'If you want to run a Fake App, stop the Card Farming module first.')
            self.window.stop.set_sensitive(True)
            return None

        self.window.update_status_bar("Waiting to fakeapp terminate.")
        ui.libsteam.stop_wrapper()

        if ui.globals.FakeApp.process.returncode is None:
            error = ui.globals.FakeApp.process.stderr.read()
            self.window.new_dialog(ui.Gtk.MessageType.ERROR,
                                   'Fake Steam App',
                                   'An Error occured ({}).'.format(ui.globals.FakeApp.process.returncode),
                                   error.decode(locale.getpreferredencoding()))

        ui.globals.FakeApp.is_running = False
        ui.globals.FakeApp.id = None
        self.window.fake_app_current_game.set_text('')
        self.window.fake_app_current_time.set_text('')

        self.window.update_status_bar("Done!")
        self.window.start.set_sensitive(True)

    @staticmethod
    def on_status_bar_text_pushed(status_bar, context, text):
        ui.GLib.timeout_add_seconds(10, ui.timers.status_bar_text_pushed_timer, context)

    @staticmethod
    def on_select_profile_button_toggled(radio_button, profile_id):
        if radio_button.get_active():
            ui.globals.Window.profile = profile_id
