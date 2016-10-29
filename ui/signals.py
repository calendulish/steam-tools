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


import configparser
import locale
import time

import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, GLib

import stlib
import ui

switch_stats = {
    0: [lambda: stlib.steam_user, lambda: ui.card_farming_is_running],
    1: [lambda: stlib.steam_user, lambda: ui.fake_app_is_running],
    4: [lambda: stlib.ST_user, lambda: ui.steamtrades_bump_is_running],
    5: [lambda: stlib.SG_user, lambda: ui.steamgifts_join_is_running],
}


def on_window_destroy(*args):
    ui.main_window.hide()
    ui.main_window = None
    ui.application.quit()


def on_quit_activate(action, parameters):
    on_window_destroy()


def on_browser_profile_activate(action, parameters):
    ui.application.select_profile(force=True)
    ui.application.update_info_labels()

    config_parser = stlib.config.read()

    for section in config_parser.sections():
        if 'Cookies' in section:
            config_parser.remove_section(section)

    stlib.config.write()

    # FIXME
    ui.main_window.warning_label.set_text('You must restart Steam tools to use new profile')
    ui.main_window.warning_label.show()


def on_settings_activate(action, parameters):
    dialog = ui.main.SettingsDialog()
    dialog.show_all()
    dialog.run()
    dialog.destroy()


def on_about_activate(action, parameters):
    ui.main_window.about_dialog.run()
    ui.main_window.about_dialog.hide()


def on_start_clicked(button):
    current_page = ui.main_window.tabs.get_current_page()
    if current_page == 0:
        on_card_farming_start()
    elif current_page == 1:
        on_fake_app_start()
    elif current_page == 4:
        on_steamtrades_bump_start()
    elif current_page == 5:
        on_steamgifts_join_start()


def on_stop_clicked(button):
    current_page = ui.main_window.tabs.get_current_page()
    if current_page == 0:
        on_card_farming_stop()
    elif current_page == 1:
        on_fake_app_stop()
    elif current_page == 4:
        on_steamtrades_bump_stop()
    elif current_page == 5:
        on_steamgifts_join_stop()


def on_tabs_switch_page(tab, box, current_page):
    current_page_label = tab.get_tab_label(box)

    if not Gtk.Widget.is_sensitive(current_page_label):
        GLib.idle_add(ui.main_window.tabs.set_current_page, 0)
        ui.main_window.info_label.set_text('Cooming Soon...')
        ui.main_window.info_label.show()
        GLib.timeout_add_seconds(5, ui.timers.hide_info_label)

        return None

    if current_page == 6:
        GLib.idle_add(ui.main_window.tabs.set_current_page, 0)
        message = ui.main.MessageDialog(Gtk.MessageType.INFO,
                                        'SteamCompanion is down.',
                                        'SteamCompanion is closed until further notice.',
                                        'Primarily because the harddrive crashed. '
                                        'Read more at <a href="http://steamcompanion.com/">Steam Companion</a>.')
        message.show()

        return None

    if switch_stats[current_page][1]():
        ui.main_window.start.set_sensitive(False)
        ui.main_window.stop.set_sensitive(True)
    elif not switch_stats[current_page][0]():
        ui.main_window.start.set_sensitive(False)
        ui.main_window.stop.set_sensitive(False)
    else:
        ui.main_window.start.set_sensitive(True)
        ui.main_window.stop.set_sensitive(False)


def on_most_valuable_cards_first_changed(switch, state):
    ui.application.update_config('CardFarming', 'mostValuableCardsFirst', state)


def on_ST_bump_trade_id_changed(entry):
    ui.application.update_config('SteamTrades', 'tradeID', entry.get_text())


def on_ST_bump_min_time_changed(entry):
    entry.set_text(''.join([text for text in entry.get_text() if text.isdigit()]))
    ui.application.update_config('SteamTrades', 'minWaitTime', entry.get_text())


def on_ST_bump_max_time_changed(entry):
    entry.set_text(''.join([text for text in entry.get_text() if text.isdigit()]))
    ui.application.update_config('SteamTrades', 'maxWaitTime', entry.get_text())


def on_SG_join_type_list_changed(entry):
    ui.application.update_config('SteamGifts', 'typeList', entry.get_text())


def on_SG_join_developer_giveaways_changed(switch, state):
    ui.application.update_config('SteamGifts', 'developerGiveaways', state)


def on_SG_join_min_time_changed(entry):
    entry.set_text(''.join([text for text in entry.get_text() if text.isdigit()]))
    ui.application.update_config('SteamGifts', 'minWaitTime', entry.get_text())


def on_SG_join_max_time_changed(entry):
    entry.set_text(''.join([text for text in entry.get_text() if text.isdigit()]))
    ui.application.update_config('SteamGifts', 'maxWaitTime', entry.get_text())


def on_card_farming_start():
    ui.main_window.start.set_sensitive(False)
    ui.main_window.stop.set_sensitive(False)
    config_parser = stlib.config.read()
    dry_run = config_parser.getboolean('Debug', 'dryRun', fallback=False)

    if ui.fake_app_is_running:
        message = ui.main.MessageDialog(Gtk.MessageType.ERROR,
                                        'Card Farming',
                                        'Please, stop the Fake App',
                                        'Unable to start Card Farming if a fake app is already running.')
        message.show()
        ui.main_window.start.set_sensitive(True)
        return None

    if stlib.libsteam.is_steam_running():
        ui.application.update_status_bar("Preparing. Please wait...")
        ui.main_window.spinner.start()
        ui.card_farming_is_running = True

        badge_pages = stlib.card_farming.get_badge_page_count()
        badges = []
        for page in range(1, badge_pages + 1):
            badges.extend(stlib.card_farming.get_badges(page))

        badges = stlib.card_farming.remove_completed_badges(badges)
        cards_info = stlib.card_farming.get_cards_info()

        if config_parser.getboolean('CardFarming', 'mostValuableCardsFirst', fallback=True):
            badges = stlib.card_farming.order_by_most_valuable(cards_info, badges)

        stlib.logger.warning('Ready to start.')
        ui.application.update_status_bar('Ready.')
        ui.main_window.spinner.stop()

        start_time = time.time()
        GLib.timeout_add_seconds(1, ui.timers.card_farming_time_timer, start_time)

        ui.main_window.card_farming_total_card_left.set_text('Counting...')
        GLib.idle_add(ui.timers.total_card_count, badges)

        ui.timers.card_farming_timer(dry_run, badges)
        GLib.timeout_add_seconds(40, ui.timers.card_farming_timer, dry_run, badges)

        ui.main_window.stop.set_sensitive(True)
    else:
        ui.application.update_status_bar("Unable to locate a running instance of steam.")
        message = ui.main.MessageDialog(Gtk.MessageType.ERROR,
                                        'Card Farming',
                                        'Unable to locate a running instance of steam.',
                                        "Please, start the Steam Client and try again.")
        message.show()
        ui.main_window.start.set_sensitive(True)


def on_card_farming_stop():
    ui.main_window.start.set_sensitive(False)
    ui.main_window.stop.set_sensitive(False)

    ui.application.update_status_bar("Waiting to card farming terminate.")
    ui.card_farming_is_running = False
    stlib.card_farming.current_badge = 0
    stlib.libsteam.stop_wrapper()
    ui.fake_app_is_running = False
    ui.fake_app_id = None
    ui.main_window.fake_app_current_game.set_text('')
    ui.main_window.fake_app_current_time.set_text('')
    ui.main_window.card_farming_current_game.set_text('')
    ui.main_window.card_farming_card_left.set_text('')
    ui.main_window.card_farming_current_game_time.set_text('')
    ui.main_window.card_farming_total_time.set_text('')

    ui.application.update_status_bar("Done!")
    ui.main_window.start.set_sensitive(True)


def on_fake_app_start():
    ui.main_window.start.set_sensitive(False)
    ui.main_window.stop.set_sensitive(False)

    ui.application.update_status_bar("Preparing. Please wait...")
    ui.main_window.spinner.start()
    ui.fake_app_id = ui.main_window.fake_app_game_id.get_text().strip()

    if not ui.fake_app_id:
        ui.application.update_status_bar("No AppID found!")
        message = ui.main.MessageDialog(Gtk.MessageType.ERROR,
                                        'Fake Steam App',
                                        'No AppID found!',
                                        "You must specify an AppID!")
        message.show()
        ui.main_window.start.set_sensitive(True)
    else:
        if stlib.libsteam.is_steam_running():
            stlib.libsteam.run_wrapper(ui.fake_app_id)
            ui.fake_app_is_running = True
            ui.main_window.stop.set_sensitive(True)
        else:
            ui.application.update_status_bar("Unable to locate a running instance of steam.")
            message = ui.main.MessageDialog(Gtk.MessageType.ERROR,
                                            'Fake Steam App',
                                            'Unable to locate a running instance of steam.',
                                            "Please, start the Steam Client and try again.")
            message.show()
            ui.main_window.start.set_sensitive(True)

    ui.main_window.spinner.stop()
    start_time = time.time()
    GLib.timeout_add_seconds(1, ui.timers.fake_app_timer, start_time)


def on_fake_app_stop():
    ui.main_window.stop.set_sensitive(False)
    ui.main_window.start.set_sensitive(False)

    if ui.card_farming_is_running:
        message = ui.main.MessageDialog(Gtk.MessageType.ERROR,
                                        'Fake Steam App',
                                        'This function is not available now',
                                        'Unable to stop Fake App because it was started by Card Farming module.\n' +
                                        'If you want to run a Fake App, stop the Card Farming module first.')
        message.show()
        ui.main_window.stop.set_sensitive(True)
        return None

    ui.application.update_status_bar("Waiting to fakeapp terminate.")
    stlib.libsteam.stop_wrapper()

    if stlib.wrapper_process.returncode is None:
        error = stlib.wrapper_process.stderr.read()
        message = ui.main.MessageDialog(Gtk.MessageType.ERROR,
                                        'Fake Steam App',
                                        'An Error occured ({}).'.format(stlib.wrapper_process.returncode),
                                        error.decode(locale.getpreferredencoding()))
        message.show()

    ui.fake_app_is_running = False
    ui.fake_app_id = None
    ui.main_window.fake_app_current_game.set_text('')
    ui.main_window.fake_app_current_time.set_text('')

    ui.application.update_status_bar("Done!")
    ui.main_window.start.set_sensitive(True)


def on_steamtrades_bump_start():
    config_parser = stlib.config.read()

    ui.main_window.start.set_sensitive(False)
    ui.main_window.stop.set_sensitive(False)

    ui.application.update_status_bar('Preparing. Please wait...')
    ui.main_window.spinner.start()
    ui.steamtrades_bump_is_running = True

    config = config_parser.get('SteamTrades', 'tradeID')
    trade_ids = [line.strip() for line in config.split(',')]

    MIN_wait_time = config_parser.getint('SteamTrades', 'minWaitTime')
    MAX_wait_time = config_parser.getint('SteamTrades', 'maxWaitTime')

    stlib.logger.warning('Ready to start.')
    ui.application.update_status_bar('Ready.')
    ui.main_window.spinner.stop()

    GLib.timeout_add_seconds(
            1,
            ui.timers.steamtrades_bump_timer,
            trade_ids,
            MIN_wait_time,
            MAX_wait_time
    )

    ui.main_window.stop.set_sensitive(True)


def on_steamtrades_bump_stop():
    ui.steamtrades_bump_is_running = False
    ui.main_window.start.set_sensitive(True)
    ui.main_window.stop.set_sensitive(False)
    ui.main_window.ST_bump_progress_bar.set_fraction(0)
    stlib.steamtrades_bump.current_trade = 0


def on_steamgifts_join_start():
    config_parser = stlib.config.read()

    ui.main_window.start.set_sensitive(False)
    ui.main_window.stop.set_sensitive(False)

    ui.application.update_status_bar('Preparing. Please wait...')
    ui.main_window.spinner.start()
    ui.steamgifts_join_is_running = True

    config = config_parser.get('SteamGifts', 'typeList')
    type_generator = (line.strip() for line in config.split(','))

    MIN_wait_time = config_parser.getint('SteamGifts', 'minWaitTime')
    MAX_wait_time = config_parser.getint('SteamGifts', 'maxWaitTime')

    stlib.logger.warning('Ready to start.')
    ui.application.update_status_bar('Ready.')
    ui.main_window.spinner.stop()

    GLib.timeout_add(
            100,
            ui.timers.steamgifts_join_timer,
            type_generator,
            MIN_wait_time,
            MAX_wait_time
    )

    ui.main_window.stop.set_sensitive(True)


def on_steamgifts_join_stop():
    ui.steamgifts_join_is_running = False
    ui.main_window.start.set_sensitive(True)
    ui.main_window.stop.set_sensitive(False)
    ui.main_window.SG_join_progress_bar.set_fraction(0)


def on_status_bar_text_pushed(status_bar, context, text):
    GLib.timeout_add_seconds(10, ui.timers.status_bar_text_pushed_timer, context)


def on_select_profile_button_toggled(radio_button, profile_id):
    if radio_button.get_active():
        ui.selected_profile_id = profile_id
