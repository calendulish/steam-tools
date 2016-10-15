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

import random

import stlib
import ui


class SteamToolsWindow(ui.Gtk.ApplicationWindow):
    def __init__(self, parent):
        super().__init__(title='Steam Tools', application=parent)
        ui.main_window = self
        self.set_default_size(640, 480)
        self.set_resizable(False)
        self.set_position(ui.Gtk.WindowPosition.CENTER)
        self.set_show_menubar(True)

        builder = ui.Gtk.Builder()
        builder.add_from_file('ui/interface.xml')
        builder.connect_signals(ui.signals)

        for _object in builder.get_objects():
            if issubclass(type(_object), ui.Gtk.Buildable):
                name = ui.Gtk.Buildable.get_name(_object)
                setattr(self, name, _object)

        del self.main_window
        self.main_box.reparent(self)

        self.fake_app_current_game.modify_fg(ui.Gtk.StateFlags.NORMAL, ui.Gdk.color_parse('black'))
        self.fake_app_current_time.modify_fg(ui.Gtk.StateFlags.NORMAL, ui.Gdk.color_parse('black'))
        self.browser_profile.modify_fg(ui.Gtk.StateFlags.NORMAL, ui.Gdk.color_parse('black'))


class SteamTools(ui.Gtk.Application):
    def __init__(self):
        super().__init__(application_id='click.lara.SteamTools')
        ui.GLib.set_application_name('Steam Tools')
        self.config_parser = stlib.config.read()
        ui.application = self
        self.window = None

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

    def do_activate(self):
        if not self.window:
            self.window = SteamToolsWindow(self)
        else:
            stlib.logger.error('Already started.')
            return None

        MVCF_config = self.config_parser.getboolean('CardFarming', 'mostValuableCardsFirst', fallback=True)
        self.window.most_valuable_cards_first.set_active(MVCF_config)
        del MVCF_config

        self.window.present()

        self.select_profile()

        self.window.browser_profile.set_text('{} ({})'.format(stlib.browser.get_account_name(),
                                                              stlib.browser.get_profile_name()))

        self.window.spinner.start()
        ui.logins.queue_connect("steam", stlib.steam_check_page)
        ui.logins.queue_connect("steamgifts", stlib.SG_check_page)
        # ui.logins.queue_connect("steamcompanion", stlib.SC_check_page)
        ui.logins.wait_queue()
        self.window.spinner.stop()

    def do_startup(self):
        ui.Gtk.Application.do_startup(self)

        builder = ui.Gtk.Builder()
        builder.add_from_file('ui/menu.xml')
        menu_bar = builder.get_object('menu_bar')
        self.set_menubar(menu_bar)

        menu_items = ['quit',
                      'browser_profile',
                      'settings',
                      'about']

        for item in menu_items:
            action = ui.Gio.SimpleAction.new(item, None)
            action_handler = ['ui.signals.on_', item, '_activate']
            action.connect('activate', eval(''.join(action_handler)))
            self.add_action(action)

    def select_profile(self):
        stlib.config.read()

        if not self.config_parser.has_option('Config', 'browserProfile'):
            profiles = stlib.browser.get_profiles()

            if not len(profiles):
                self.update_status_bar('I cannot find your chrome/Chromium profile')
                self.new_dialog(ui.Gtk.MesageType.ERROR,
                                'Network Error',
                                'I cannot find your Chrome/Chromium profile',
                                'Some functions will be disabled.')
            elif len(profiles) == 1:
                self.config_parser.set('Config', 'browserProfile', profiles[0])
                stlib.config.write()
            else:
                self.window.select_profile_dialog.add_button('Ok', 1)

                temp_radiobutton = None
                for i in range(len(profiles)):
                    account_name = stlib.browser.get_account_name(profile_name=profiles[i])
                    temp_radiobutton = ui.Gtk.RadioButton.new_with_label_from_widget(temp_radiobutton,
                                                                                     '{} ({})'.format(account_name,
                                                                                                      profiles[i]))

                    temp_radiobutton.connect('toggled', ui.signals.on_select_profile_button_toggled, i)
                    self.window.radiobutton_box.pack_start(temp_radiobutton, False, False, 0)

                self.window.select_profile_dialog.show_all()
                self.window.select_profile_dialog.run()
                self.window.select_profile_dialog.destroy()

                self.config_parser.set('Config', 'browserProfile', profiles[ui.selected_profile_id])
                stlib.config.write()

    def update_status_bar(self, message):
        message_id = random.randrange(500)
        self.window.status_bar.push(message_id, message)

        return message_id

    def new_dialog(self, msg_type, title, markup, secondary_markup=None):
        dialog = ui.Gtk.MessageDialog(transient_for=self.window,
                                      flags=ui.Gtk.DialogFlags.MODAL,
                                      destroy_with_parent=True,
                                      type=msg_type,
                                      buttons=ui.Gtk.ButtonsType.OK,
                                      text=markup)
        dialog.set_title(title)
        dialog.format_secondary_markup(secondary_markup)
        dialog.connect('response', lambda d, _: d.destroy())
        dialog.show()
