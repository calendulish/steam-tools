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

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class SignalHandler:
    def on_window_destroy(self, widget):
        Gtk.main_quit()

    def on_tray_button_press_event(self, widget):
        pass

    def on_tray_activate(self, widget):
        pass

    def on_tray_popup_menu(self, widget):
        pass

    def on_tabs_change_current_page(self, widget):
        pass

    def on_tabs_focus_tab(self, widget):
        pass

    def on_tabs_select_page(self, widget):
        pass

class SteamTools:
    def main(self):
        builder = Gtk.Builder()
        builder.add_from_file("interface.xml")
        builder.connect_signals(SignalHandler())

        window = builder.get_object("mainWindow")
        window.set_default_size(640, 480)
        window.show_all()

if __name__ == "__main__":
    st = SteamTools()
    st.main()
    Gtk.main()
