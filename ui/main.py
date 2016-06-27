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


import json
import locale
import os

import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

import stlib
import ui.signals

class SteamTools:
    def __init__(self):
        builder = Gtk.Builder()
        builder.add_from_file('ui/interface.xml')
        builder.connect_signals(ui.signals.WindowSignals(self))

        for _object in builder.get_objects():
            if issubclass(type(_object), Gtk.Buildable):
                name = Gtk.Buildable.get_name(_object)
                setattr(self, name, _object)

        self.fsa_currentGame.modify_fg(Gtk.StateFlags.NORMAL, Gdk.color_parse('black'))
        self.fsa_currentTime.modify_fg(Gtk.StateFlags.NORMAL, Gdk.color_parse('black'))

        self.icons_path = 'ui/icons'

        self.steam_icon_available = 'steam_green.png'
        self.steam_icon_busy = 'steam_yellow.png'
        self.steam_icon_unavailable = 'steam_red.png'

        self.steamgifts_icon_available = 'steamgifts_green.png'
        self.steamgifts_icon_busy = 'steamgifts_yellow.png'
        self.steamgifts_icon_unavailable = 'steamgifts_red.png'

        self.steamcompanion_icon_available = 'steamcompanion_green.png'
        self.steamcompanion_icon_busy = 'steamcompanion_yellow.png'
        self.steamcompanion_icon_unavailable = 'steamcompanion_red.png'

        self.mainWindow.show_all()

        self.browser_bridge = stlib.cookie.BrowserBridge()

        profiles = self.browser_bridge.get_chrome_profile()
        if not len(profiles):
            self.update_statusbar('NoChromeProfile', 'I cannot find your chrome/Chromium profile')
            self.new_dialog(Gtk.MesageType.ERROR,
                            'checkcookies',
                            'I cannot find your Chrome/Chromium profile',
                            'Some functions will be disabled.')
            return False
        elif len(profiles) == 1:
            pass
            # CONFIG.set('Config', 'chromeProfile', profiles[0])
        else:
            self.selectProfile_dialog.add_button('Ok', 1)
            self.selected_profile = 0

            temp_radiobutton = None
            for i in range(len(profiles)):
                with open(os.path.join(profiles[i], 'Preferences')) as prefs_file:
                    prefs = json.load(prefs_file)

                temp_radiobutton = Gtk.RadioButton.new_with_label_from_widget(temp_radiobutton,
                                                                              '{} ({})'.format(prefs['account_info'][0][
                                                                                                   'full_name'],
                                                                                               os.path.basename(
                                                                                                       profiles[i])))

                temp_radiobutton.connect('toggled', ui.signals.WindowSignals(self).on_select_profile_button_toggled, i)
                self.radiobutton_box.pack_start(temp_radiobutton, False, False, 0)

            self.selectProfile_dialog.show_all()
            self.selectProfile_dialog.run()
            self.selectProfile_dialog.destroy()

        # FIXME: update config with the selected profile
        self.browser_profile = profiles[self.selected_profile]

        self.logins = ui.logins.CheckLogins(self)
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
        dialog.connect('response', lambda d, _:d.destroy())
        dialog.show()
