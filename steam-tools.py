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
from datetime import timedelta
from argparse import ArgumentParser
import locale

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, GLib, Gdk

from stlib.checklogins import checkLogins
from stlib.stconsole import STConsole
from stlib.stfakeapp import STFakeApp

# The pages are in that order:
# : PG :    Module    :
# :  0 : Card Farming :
# :  1 :   SG Bump    :
# :  2 :   SG Join    :
# :  3 :   SC Join    :
class WindowSignals:
    def __init__(self, parent):
        self.stwindow = parent
        self.is_fake_app_running = False

    def on_window_destroy(self, *args):
        Gtk.main_quit(*args)

    def on_start_clicked(self, data):
        current_page = self.stwindow.tabs.get_current_page()
        if current_page == 0:
            pass
        elif current_page == 1:
            self.stwindow.update_statusBar("FakeAppWait", "Preparing. Please wait...")
            self.fake_app_id = self.stwindow.fsa_appID.get_text().strip()
            if not self.fake_app_id:
                self.stwindow.update_statusBar("NoAppID", "No AppID found!")
                self.stwindow.new_dialog(Gtk.MessageType.ERROR,
                                         'Fake Steam App',
                                         'No AppID found!',
                                         "You must specify an AppID!")
            else:
                self.stwindow.start.set_sensitive(False)
                # Prevents bad behaviour when the user click
                # on the stop button before the fake_app is ready
                self.stwindow.stop.set_sensitive(False)
                STFA = STFakeApp()
                if STFA.is_steam_running():
                    self.fake_app = STFA.run_wrapper(self.fake_app_id)
                    self.is_fake_app_running = True
                    self.stwindow.stop.set_sensitive(True)
                    self.stwindow.update_statusBar("FakeAppRunning", "The fake app is running.")
                else:
                    self.stwindow.update_statusBar("NoSteamInstance", "Unable to locate a running instance of steam.")
                    self.stwindow.new_dialog(Gtk.MessageType.ERROR,
                                             'Fake Steam App',
                                             'Unable to locate a running instance of steam.',
                                             "Please, start the Steam Client and try again.")
                    self.stwindow.start.set_sensitive(True)

            self.fake_app_elapsed_time = 0
            GLib.timeout_add_seconds(1, self.fake_app_timer)

        elif current_page == 2:
            pass
        elif current_page == 3:
            pass
        elif current_page == 4:
            pass

    def on_stop_clicked(self, data):
        current_page = self.stwindow.tabs.get_current_page()
        if current_page == 0:
            pass
        elif current_page == 1:
            self.stwindow.stop.set_sensitive(False)
            # Prevents bad behaviour when the user click
            # on the start button before the fake_app is ready
            self.stwindow.start.set_sensitive(False)
            self.is_fake_app_running = False
            self.fake_app.terminate()
            self.stwindow.update_statusBar("WaitingFakeApp", "Waiting to fakeapp terminate.")
            try:
                self.fake_app.communicate(timeout=20)
            except TimeoutExpired:
                self.stwindow.update_statusBar("KillingFAkeApp", "Force Killing fakeapp")
                self.fake_app.kill()
                self.fake_app.communicate()

            if self.fake_app.returncode is None:
                error = self.fake_app.stderr.read()
                self.stwindow.new_dialog(Gtk.MessageType.ERROR,
                                         'Fake Steam App',
                                         'An Error occured ({}).'.format(self.fake_app.returncode),
                                         error.decode(locale.getpreferredencoding()))
            self.stwindow.update_statusBar("FakeAppStopped", "Done!")
            self.stwindow.start.set_sensitive(True)
            self.stwindow.fsa_currentGame.set_text('')
            self.stwindow.fsa_currentTime.set_text('')

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
                self.stwindow.start.set_sensitive(False)
                self.stwindow.stop.set_sensitive(True)
            else:
                self.stwindow.start.set_sensitive(True)
                self.stwindow.stop.set_sensitive(False)
        elif current_page == 2:
            pass
        elif current_page == 3:
            pass
        elif current_page == 4:
            pass

    def on_statusBar_text_pushed(self, object, context, text):
        GLib.timeout_add_seconds(10, self.statusBar_text_pushed_timer, context)

    def statusBar_text_pushed_timer(self, context):
        self.stwindow.statusBar.pop(context)
        return False

    def fake_app_timer(self):
        self.fake_app_elapsed_time += 1
        if self.is_fake_app_running:
            if self.fake_app.poll():
                self.stwindow.update_statusBar("gameIDInvalid", "This is not a valid gameID.")
                self.stwindow.new_dialog(Gtk.MessageType.ERROR,
                                         'Fake Steam App',
                                         'This is not a valid gameID.',
                                         "Please, check if you write correctly and try again.")
                self.is_fake_app_running = False
                self.stwindow.start.set_sensitive(True)
                self.stwindow.stop.set_sensitive(False)
                self.stwindow.fsa_currentGame.set_text('')
                self.stwindow.fsa_currentTime.set_text('')
                return False
            else:
                self.stwindow.fsa_currentGame.set_text(self.fake_app_id)
                self.stwindow.fsa_currentTime.set_text(str(timedelta(seconds=self.fake_app_elapsed_time)))
                return True
        else:
            return False


class SteamTools:
    def __init__(self):
        builder = Gtk.Builder()
        builder.add_from_file("interface.xml")
        builder.connect_signals(WindowSignals(self))

        for _object in builder.get_objects():
            if issubclass(type(_object), Gtk.Buildable):
                name = Gtk.Buildable.get_name(_object)
                setattr(self, name, _object)

        self.fsa_currentGame.modify_fg(Gtk.StateFlags.NORMAL, Gdk.color_parse('black'))
        self.fsa_currentTime.modify_fg(Gtk.StateFlags.NORMAL, Gdk.color_parse('black'))

        self.mainWindow.show_all()

        self.logins = checkLogins(self)
        self.logins.start()

    def update_statusBar(self, context, message):
        id = self.statusBar.get_context_id(context)
        self.statusBar.push(id, message)

    def new_dialog(self, msg_type, title, markup, secondary_markup=None):
        dialog = Gtk.MessageDialog(transient_for=self.mainWindow,
                                   flags=Gtk.DialogFlags.MODAL,
                                   destroy_with_parent=True,
                                   type=msg_type,
                                   buttons=Gtk.ButtonsType.OK,
                                   text=markup)
        dialog.set_title(title)
        dialog.format_secondary_markup(secondary_markup)
        dialog.connect('response', lambda d,_: d.destroy())
        dialog.show()

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
