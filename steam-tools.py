#!/usr/bin/env python
# Lara Maia <dev@lara.click> 2015

from gi.repository import Gtk, GObject
import subprocess
import fcntl
import os

global sgb_process
global scf_process

class Terminal:
    def __init__(self, process, view):
        self.process = process
        self.view = view

        self.sub_proc = subprocess.Popen(process, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.sub_outp = ""

        self.gosource = GObject.timeout_add(100, self.update_terminal)

# FIXME: http://bugs.python.org/issue18823
    def non_block_read(self, output):
        fd = output.fileno()
        fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
        try:
            return output.read().decode('utf-8')
        except Exception:
            return ''

    def update_terminal(self):
        buffer = self.view.get_buffer()
        buffer.insert_at_cursor(self.non_block_read(self.sub_proc.stdout))
        iter = buffer.get_end_iter()
        self.view.scroll_to_iter(iter, 0, False, 0.5, 0.5)
        return self.sub_proc.poll() is None

    def stop(self):
        GObject.source_remove(self.gosource)
        self.sub_proc.terminate()
        self.sub_proc.wait()

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
        self.sgb_stop_button = Gtk.Button(label="Stop")

        self.sgb_terminalView = Gtk.TextView()
        self.sgb_scroll = Gtk.ScrolledWindow(hexpand=True, vexpand=True)
        self.sgb_scroll.add(self.sgb_terminalView)

        self.steamgifts_bump.attach(self.sgb_start_button, 0, 0, 1, 1)
        self.steamgifts_bump.attach(self.sgb_stop_button, 1, 0, 1, 1)
        self.steamgifts_bump.attach(self.sgb_scroll, 0, 1, 2, 2)
        self.notebook.append_page(self.steamgifts_bump, Gtk.Label("SteamGifts Bump"))

        self.steam_card_farming = Gtk.Grid()
        self.steam_card_farming.set_border_width(10)

        self.scf_start_button = Gtk.Button(label="Start")
        self.scf_stop_button = Gtk.Button(label="Stop")

        self.scf_terminalView = Gtk.TextView()
        self.scf_scroll = Gtk.ScrolledWindow(hexpand=True, vexpand=True)
        self.scf_scroll.add(self.scf_terminalView)

        self.steam_card_farming.attach(self.scf_start_button, 0, 0, 1, 1)
        self.steam_card_farming.attach(self.scf_stop_button, 1, 0, 1, 1)
        self.steam_card_farming.attach(self.scf_scroll, 0, 1, 2, 2)
        self.notebook.append_page(self.steam_card_farming, Gtk.Label("Steam Card Farming"))

        self.connect("delete-event", Gtk.main_quit)

        self.sgb_start_button.connect("clicked", self.sgb_start_button_clicked)
        self.sgb_stop_button.connect("clicked", self.sgb_stop_button_clicked)

        self.scf_start_button.connect("clicked", self.scf_start_button_clicked)
        self.scf_stop_button.connect("clicked", self.scf_stop_button_clicked)

        self.status = Gtk.Statusbar()
        self.status_context = self.status.get_context_id("st")
        self.status.push(self.status_context, "This is an extremely experimental interface")
        self.box.pack_start(self.status, False, False, 0)
        self.add(self.box)
        self.show_all()

    def sgb_start_button_clicked(self, button):
        global sgb_process
        process = ['python', '-u', os.path.join(os.getcwd(), 'steamgifts-bump.py')]
        sgb_process = Terminal(process, self.sgb_terminalView)

    def sgb_stop_button_clicked(self, button):
        global sgb_process
        sgb_process.stop()

    def scf_start_button_clicked(self, button):
        global scf_process
        process = ['python', '-u', os.path.join(os.getcwd(), 'steam-card-farming.py')]
        scf_process = Terminal(process, self.scf_terminalView)

    def scf_stop_button_clicked(self, button):
        global scf_process
        scf_process.stop()

if __name__ == "__main__":
    window = SteamTools()
    Gtk.main()
