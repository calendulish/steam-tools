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

import os
import random

import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, GLib, Gdk, Gio

import stlib
import ui
import ui.gtk_markup_substring


class SteamToolsWindow(Gtk.ApplicationWindow):
    def __init__(self, parent):
        super().__init__(title='Steam Tools', application=parent)
        ui.main_window = self
        self.set_icon_from_file(os.path.join('ui', 'icons', 'steam-tools.ico'))
        self.set_default_size(640, 480)
        self.set_resizable(False)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_show_menubar(True)

        builder = Gtk.Builder()
        builder.add_from_file(os.path.join('ui', 'interface.xml'))
        builder.connect_signals(ui.signals)

        for _object in builder.get_objects():
            if issubclass(type(_object), Gtk.Buildable):
                name = Gtk.Buildable.get_name(_object)
                _object.set_name(name)
                setattr(self, name, _object)

        style_file = Gio.File.new_for_path(os.path.join('ui', 'interface.css'))
        self.style_provider = Gtk.CssProvider()
        self.style_provider.load_from_file(style_file)

        self.style_context = Gtk.StyleContext()
        self.style_context.add_provider_for_screen(
            Gdk.Screen.get_default(),
            self.style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        ui.gtk_markup_substring.set_from_css(
                self.version_label,
                styles=('text', 'version'),
                params=('Steam Tools', ui.__VERSION__)
        )

        del self.main_window
        self.main_box.reparent(self)

        self.fake_app_current_game.modify_fg(Gtk.StateFlags.NORMAL, Gdk.color_parse('black'))
        self.fake_app_current_time.modify_fg(Gtk.StateFlags.NORMAL, Gdk.color_parse('black'))
        self.warning_label.modify_fg(Gtk.StateFlags.NORMAL, Gdk.color_parse('white'))
        self.warning_label.modify_bg(Gtk.StateFlags.NORMAL, Gdk.color_parse('darkred'))


class SteamTools(Gtk.Application):
    def __init__(self):
        super().__init__(application_id='click.lara.SteamTools')
        GLib.set_application_name('Steam Tools')
        self.config_parser = stlib.config.read()
        ui.application = self
        self.window = None

        self.icons_path = os.path.join('ui', 'icons')

        self.steam_icon_available = 'steam_green.png'
        self.steam_icon_busy = 'steam_yellow.png'
        self.steam_icon_unavailable = 'steam_red.png'

        self.SG_icon_available = 'steamgifts_green.png'
        self.SG_icon_busy = 'steamgifts_yellow.png'
        self.SG_icon_unavailable = 'steamgifts_red.png'

        self.SC_icon_available = 'steamcompanion_green.png'
        self.SC_icon_busy = 'steamcompanion_yellow.png'
        self.SC_icon_unavailable = 'steamcompanion_red.png'

        self.ST_icon_available = 'steamtrades_green.png'
        self.ST_icon_busy = 'steamtrades_yellow.png'
        self.ST_icon_unavailable = 'steamtrades_red.png'

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
        self.update_info_labels()
        self.do_login_check()

    def do_startup(self):
        Gtk.Application.do_startup(self)

        builder = Gtk.Builder()
        builder.add_from_file(os.path.join('ui', 'menu.xml'))
        menu_bar = builder.get_object('menu_bar')
        self.set_menubar(menu_bar)

        menu_items = ['quit',
                      'browser_profile',
                      'settings',
                      'about']

        for item in menu_items:
            action = Gio.SimpleAction.new(item, None)
            action_handler = ['ui.signals.on_', item, '_activate']
            action.connect('activate', eval(''.join(action_handler)))
            self.add_action(action)

    def do_login_check(self):
        self.window.spinner.start()
        stlib.logins.queue_connect('steam', self.do_steam_login)
        stlib.logins.queue_connect('steamgifts', self.do_steamgifts_login)
        stlib.logins.queue_connect('steamtrades', self.do_steamtrades_login)
        stlib.logins.wait_queue()
        self.window.spinner.stop()

    def do_steam_login(self, greenlet):
        stlib.logins.check_steam_login(greenlet)

        if stlib.steam_user:
            ui.main_window.steam_login_status.set_from_file(os.path.join(self.icons_path, self.steam_icon_available))
            ui.main_window.steam_login_status.set_tooltip_text("Steam Login status:\n" +
                                                               "Connected as {}".format(stlib.steam_user))
            steam_connected = True
        else:
            ui.main_window.steam_login_status.set_from_file(os.path.join(self.icons_path, self.steam_icon_unavailable))
            ui.main_window.steam_login_status.set_tooltip_text("Steam Login status: Cookies not found" +
                                                               "\nPlease, check if you are logged in on" +
                                                               "\nsteampowered.com or steamcommunity.com")
            steam_connected = False

        self._check_start_depends([0, 1], steam_connected)

    def do_steamgifts_login(self, greenlet):
        stlib.logins.check_steamgifts_login(greenlet)

        if stlib.SG_user:
            ui.main_window.SG_login_status.set_from_file(os.path.join(self.icons_path, self.SG_icon_available))
            ui.main_window.SG_login_status.set_tooltip_text("SteamGifts Login status:\n" +
                                                            "Connected as {}".format(stlib.SG_user))
            SG_connected = True
        else:
            ui.main_window.SG_login_status.set_from_file(os.path.join(self.icons_path, self.SG_icon_unavailable))
            ui.main_window.SG_login_status.set_tooltip_text("SteamGifts Login status: Cookies not found" +
                                                            "\nPlease, check if you are logged in on" +
                                                            "\nwww.steamgifts.com")
            SG_connected = False

        self._check_start_depends([3], SG_connected)

    def do_steamtrades_login(self, greenlet):
        stlib.logins.check_steamtrades_login(greenlet)

        if stlib.ST_user:
            ui.main_window.ST_login_status.set_from_file(os.path.join(self.icons_path, self.ST_icon_available))
            ui.main_window.ST_login_status.set_tooltip_text("SteamTrades Login status:\n" +
                                                            "Connected as {}".format(stlib.ST_user))
            ST_connected = True
        else:
            ui.main_window.ST_login_status.set_from_file(os.path.join(self.icons_path, self.ST_icon_unavailable))
            ui.main_window.ST_login_status.set_tooltip_text("SteamTrades Login status: Cookies not found" +
                                                            "\nPlease, check if you are logged in on" +
                                                            "\nwww.steamtrades.com")
            ST_connected = False

        self._check_start_depends([2], ST_connected)

    def do_steamcompanion_login(self, greenlet):
        stlib.logins.check_steamcompanion_login(greenlet)

        if stlib.SC_user:
            ui.main_window.SC_login_status.set_from_file(os.path.join(self.icons_path, self.SC_icon_available))
            ui.main_window.SC_login_status.set_tooltip_text("SteamCompanion Login status:\n" +
                                                            "Connected as {}".format(stlib.SC_user))
            SC_connected = True
        else:
            ui.main_window.SC_login_status.set_from_file(os.path.join(self.icons_path, self.SC_icon_unavailable))
            ui.main_window.SC_login_status.set_tooltip_text("SteamCompanion Login status: Cookies not found" +
                                                            "\nPlease, check if you are logged in on" +
                                                            "\nsteamcompanion.com")
            SC_connected = False

        self._check_start_depends([4], SC_connected)

    def select_profile(self, force=False):
        stlib.config.read()
        dialog = SelectProfileDialog()
        ui.selected_profile_id = 0

        if force or not self.config_parser.has_option('Config', 'browserProfile'):
            profiles = stlib.browser.get_profiles()

            if not len(profiles):
                self.update_status_bar('I cannot find your chrome/Chromium profile')
                message = MessageDialog(Gtk.MesageType.ERROR,
                                        'Network Error',
                                        'I cannot find your Chrome/Chromium profile',
                                        'Some functions will be disabled.')
                message.show()
            elif len(profiles) == 1:
                self.config_parser.set('Config', 'browserProfile', profiles[0])
                stlib.config.write()
            else:
                temp_radiobutton = None
                for i in range(len(profiles)):
                    account_name = stlib.browser.get_account_name(profile_name=profiles[i])
                    temp_radiobutton = Gtk.RadioButton.new_with_label_from_widget(temp_radiobutton,
                                                                                  '{} ({})'.format(account_name,
                                                                                                   profiles[i]))

                    temp_radiobutton.connect('toggled', ui.signals.on_select_profile_button_toggled, i)
                    dialog.radio_button_box.pack_start(temp_radiobutton, False, False, 5)

                dialog.show_all()
                dialog.run()
                dialog.destroy()

                self.config_parser.set('Config', 'browserProfile', profiles[ui.selected_profile_id])
                stlib.config.write()

    def update_status_bar(self, message):
        message_id = random.randrange(500)
        self.window.status_bar.push(message_id, message)

        return message_id

    def update_info_labels(self):
        ui.gtk_markup_substring.set_from_css(
                self.window.browser_label,
                styles=('text', 'browser', 'text'),
                params=('Using', 'Google Chrome', 'Profile')
        )

        ui.gtk_markup_substring.set_from_css(
                self.window.browser_profile,
                styles=('text', 'account', 'text', 'profile', 'text'),
                params=('Cookies from', stlib.browser.get_account_name(), '(', stlib.browser.get_profile_name(), ')')
        )

    def _check_start_depends(self, pages, state):
        for page in pages:
            if self.window.tabs.get_current_page() == page:
                self.window.start.set_sensitive(state)


class SettingsDialog(Gtk.Dialog):
    log_levels_id = {
        'verbose': 0,
        'info': 1,
        'warning': 2,
        'error': 3,
        'critical': 4,
    }

    log_levels_name = dict(enumerate(log_levels_id.keys()))

    def __init__(self):
        super().__init__()
        self.set_default_size(300, 300)
        self.set_title('Steam Tools Settings')
        self.set_transient_for(ui.main_window)
        self.set_modal(True)
        self.set_destroy_with_parent(True)
        self.set_resizable(False)
        self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.add_button(button_text='_OK', response_id=Gtk.ResponseType.OK)
        self.add_button(button_text='_Cancel', response_id=Gtk.ResponseType.CANCEL)

        self.config_parser = stlib.config.read()

        self.content_area = self.get_content_area()
        self.content_area.set_orientation(Gtk.Orientation.VERTICAL)
        self.content_area.set_spacing(5)
        self.content_area.set_margin_left(10)
        self.content_area.set_margin_right(10)
        self.content_area.set_margin_top(10)
        self.content_area.set_margin_bottom(10)

        frame = Gtk.Frame(label='Global Settings')
        frame.set_label_align(0.1, 0.5)
        frame.set_margin_top(10)
        frame.set_margin_bottom(5)
        self.content_area.pack_start(frame, False, False, 0)

        self.main_box = Gtk.Box()
        self.main_box.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.main_box.set_homogeneous(True)
        self.main_box.set_margin_left(10)
        self.main_box.set_margin_right(10)
        self.main_box.set_margin_top(10)
        self.main_box.set_margin_bottom(10)
        frame.add(self.main_box)

        box = Gtk.Box()
        box.set_orientation(Gtk.Orientation.VERTICAL)
        box.set_homogeneous(True)
        box.set_spacing(3)
        self.main_box.pack_start(box, False, True, 0)

        label = Gtk.Label()
        label.set_text('Dry run:')
        label.set_halign(Gtk.Align.START)
        box.pack_start(label, False, False, 0)

        label = Gtk.Label()
        label.set_text('Console level:')
        label.set_halign(Gtk.Align.START)
        box.pack_start(label, False, False, 0)

        label = Gtk.Label()
        label.set_text('Log file level:')
        label.set_halign(Gtk.Align.START)
        box.pack_start(label, False, False, 0)

        box = Gtk.Box()
        box.set_orientation(Gtk.Orientation.VERTICAL)
        box.set_homogeneous(True)
        box.set_spacing(3)
        self.main_box.pack_start(box, False, True, 0)

        self.dry_run = Gtk.ComboBoxText()
        box.pack_start(self.dry_run, False, False, 0)

        self.console_log_level = Gtk.ComboBoxText()
        box.pack_start(self.console_log_level, False, False, 0)

        self.log_file_level = Gtk.ComboBoxText()
        box.pack_start(self.log_file_level, False, False, 0)

        self.connect('response', self.on_response)

        self.get_options()

    def on_response(self, dialog, response):
        if response == Gtk.ResponseType.OK:
            self.set_options()

        dialog.destroy()

    def set_options(self):
        selected = bool(self.dry_run.get_active())
        self.config_parser.set('Debug', 'dryRun', selected)

        selected = self.log_levels_name[self.console_log_level.get_active()]
        self.config_parser.set('Debug', 'consoleLevel', selected)

        selected = self.log_levels_name[self.log_file_level.get_active()]
        self.config_parser.set('Debug', 'logFileLevel', selected)

        stlib.config.write()

    def get_options(self):
        self.dry_run.append_text('False')
        self.dry_run.append_text('True')

        config = self.config_parser.getboolean('Debug', 'dryRun', fallback=False)
        self.dry_run.set_active(int(config))

        self.console_log_level.append_text('verbose')
        self.console_log_level.append_text('info')
        self.console_log_level.append_text('warning')
        self.console_log_level.append_text('error')
        self.console_log_level.append_text('critical')

        config = self.config_parser.get('Debug', 'consoleLevel', fallback='info')
        self.console_log_level.set_active(self.log_levels_id[config])

        self.log_file_level.append_text('verbose')
        self.log_file_level.append_text('info')
        self.log_file_level.append_text('warning')
        self.log_file_level.append_text('error')
        self.log_file_level.append_text('critical')

        config = self.config_parser.get('Debug', 'logFileLevel', fallback='verbose')
        self.log_file_level.set_active(self.log_levels_id[config])


class MessageDialog(Gtk.MessageDialog):
    def __init__(self, message_type, title, markup, secondary_markup=None):
        super().__init__(buttons=Gtk.ButtonsType.OK, type=message_type)
        self.set_title(title)
        self.set_transient_for(ui.main_window)
        self.set_modal(True)
        self.set_destroy_with_parent(True)
        self.set_resizable(False)
        self.set_deletable(False)
        self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.set_markup("<span size='large'>{}</span>".format(markup))
        self.format_secondary_markup(secondary_markup)
        self.connect('response', self.on_response)

    def on_response(self, dialog, response):
        dialog.destroy()


class SelectProfileDialog(Gtk.Dialog):
    def __init__(self):
        super().__init__()
        self.set_default_size(-1, 200)
        self.set_title('Select a profile')
        self.set_transient_for(ui.main_window)
        self.set_modal(True)
        self.set_destroy_with_parent(True)
        self.set_resizable(False)
        self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.set_deletable(False)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.add_button(button_text='_OK', response_id=Gtk.ResponseType.OK)
        self.connect('response', self.on_response)

        self.content_area = self.get_content_area()
        self.content_area.set_orientation(Gtk.Orientation.VERTICAL)
        self.content_area.set_spacing(5)
        self.content_area.set_margin_left(10)
        self.content_area.set_margin_right(10)
        self.content_area.set_margin_top(10)
        self.content_area.set_margin_bottom(10)

        label_who_are = Gtk.Label('Who are you?')
        self.content_area.pack_start(label_who_are, False, False, 0)

        label_select_option = Gtk.Label('Please, select an option bellow')
        self.content_area.pack_start(label_select_option, False, False, 0)

        frame = Gtk.Frame(label='Chrome/Chromium Profiles:')
        frame.set_label_align(0.1, 0.5)
        frame.set_margin_top(10)
        frame.set_margin_bottom(5)
        self.content_area.pack_start(frame, False, False, 0)

        self.radio_button_box = Gtk.Box()
        self.radio_button_box.set_orientation(Gtk.Orientation.VERTICAL)
        frame.add(self.radio_button_box)

    def on_response(self, dialog, response):
        if response == Gtk.ResponseType.OK:
            stlib.logger.info('Browser profile selected')
            dialog.destroy()
        else:
            return True
