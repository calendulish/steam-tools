#!/usr/bin/env python
#
# Lara Maia <dev@lara.click> 2015
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

from gi.repository import Gtk, Gdk, GLib, Vte
from signal import SIGKILL
import sys, os

global sgb_process
global scf_process

class Terminal(Vte.Terminal):
    def __init__(self):
        Vte.Terminal.__init__(self)
        self.set_cursor_shape(Vte.CursorShape.UNDERLINE)
        self.set_color_foreground(Gdk.RGBA(0, 1, 0, 1))

    def run(self, process):
        proc_info = self.spawn_sync(
            Vte.PtyFlags.DEFAULT,
            os.getcwd(),
            process,
            [],
            GLib.SpawnFlags.DO_NOT_REAP_CHILD,
            None,
            None,
        )
        return proc_info

# FIXME: I cannot append something to the widget without a
# child process to handle the output. This is an ugly solution.
    def write(self, text):
        text = '\n *** '+text+' ***\n'
        self.run(['/usr/bin/printf', text])

    def stop(self, term, info):
        try:
            os.kill(info[1], SIGKILL)
        except(ProcessLookupError, NameError):
            term.write("The process is not started.")

class SteamTools(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Steam Tools")
        self.set_border_width(10)
        self.set_default_size(700, 600)

        self.headerbar = Gtk.HeaderBar(show_close_button=True)
        self.headerbar.props.title = self.get_title()
        self.headerbar.props.subtitle = "Lara Maia <dev@lara.click>"
        self.set_titlebar(self.headerbar)

        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self.notebook = Gtk.Notebook()
        self.box.pack_start(self.notebook, True, True, 0)

        self.steamgifts_bump = Gtk.Grid()
        self.steamgifts_bump.set_border_width(10)

        self.sgb_start_button = Gtk.Button(label="Start")
        self.sgb_stop_button = Gtk.Button(label="Stop", sensitive=False)

        self.sgb_terminal = Terminal()
        self.sgb_scroll = Gtk.ScrolledWindow(hexpand=True, vexpand=True)
        self.sgb_scroll.add(self.sgb_terminal)

        self.steamgifts_bump.attach(self.sgb_start_button, 0, 0, 1, 1)
        self.steamgifts_bump.attach(self.sgb_stop_button, 1, 0, 1, 1)
        self.steamgifts_bump.attach(self.sgb_scroll, 0, 1, 2, 2)
        self.notebook.append_page(self.steamgifts_bump, Gtk.Label("SteamGifts Bump"))

        self.steam_card_farming = Gtk.Grid()
        self.steam_card_farming.set_border_width(10)

        self.scf_start_button = Gtk.Button(label="Start")
        self.scf_stop_button = Gtk.Button(label="Stop", sensitive=False)

        self.scf_terminal = Terminal()
        self.scf_scroll = Gtk.ScrolledWindow(hexpand=True, vexpand=True)
        self.scf_scroll.add(self.scf_terminal)

        self.steam_card_farming.attach(self.scf_start_button, 0, 0, 1, 1)
        self.steam_card_farming.attach(self.scf_stop_button, 1, 0, 1, 1)
        self.steam_card_farming.attach(self.scf_scroll, 0, 1, 2, 2)
        self.notebook.append_page(self.steam_card_farming, Gtk.Label("Steam Card Farming"))

        self.connect("delete-event", Gtk.main_quit)

        self.sgb_start_button.connect("clicked", self.sgb_start_button_clicked)
        self.sgb_stop_button.connect("clicked", self.sgb_stop_button_clicked)
        self.sgb_terminal.connect("child-exited", self.terminal_child_exited)

        self.scf_start_button.connect("clicked", self.scf_start_button_clicked)
        self.scf_stop_button.connect("clicked", self.scf_stop_button_clicked)
        self.scf_terminal.connect("child-exited", self.terminal_child_exited)

        self.status = Gtk.Statusbar()
        self.status_context = self.status.get_context_id("st")
        self.status.push(self.status_context, "This is an extremely experimental interface")
        self.box.pack_start(self.status, False, False, 0)
        self.add(self.box)
        self.show_all()

    def sgb_start_button_clicked(self, button):
        global sgb_process
        process = [sys.executable, '-u', os.path.join(os.getcwd(), 'steamgifts-bump.py')]
        sgb_process = self.sgb_terminal.run(process)
        self.sgb_start_button.set_sensitive(False)
        self.sgb_stop_button.set_sensitive(True)

    def sgb_stop_button_clicked(self, button):
        self.sgb_terminal.stop(self.sgb_terminal, sgb_process)
        self.sgb_start_button.set_sensitive(True)
        self.sgb_stop_button.set_sensitive(False)

    def scf_start_button_clicked(self, button):
        global scf_process
        process = [sys.executable, '-u', os.path.join(os.getcwd(), 'steam-card-farming.py')]
        scf_process = self.scf_terminal.run(process)
        self.scf_start_button.set_sensitive(False)
        self.scf_stop_button.set_sensitive(True)

    def scf_stop_button_clicked(self, button):
        self.scf_terminal.stop(self.scf_terminal, scf_process)
        self.scf_start_button.set_sensitive(True)
        self.scf_stop_button.set_sensitive(False)

    def terminal_child_exited(self, term, status):
        if status: term.write("Process Terminated.")

if __name__ == "__main__":
    window = SteamTools()
    Gtk.main()
