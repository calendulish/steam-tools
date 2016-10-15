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

import datetime
import time

import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, GLib

import stlib
import ui


def status_bar_text_pushed_timer(context):
    ui.main_window.status_bar.pop(context)
    return False


def card_farming_time_timer(start_time):
    elapsed_seconds = int(time.time() - start_time)
    elapsed_time = datetime.timedelta(seconds=elapsed_seconds)

    if ui.card_farming_is_running:
        ui.main_window.card_farming_total_time.set_text(str(elapsed_time))

        if ui.card_farming_game_start_time:
            elapsed_seconds = int(time.time() - ui.card_farming_game_start_time)
            elapsed_time = datetime.timedelta(seconds=elapsed_seconds)
            ui.main_window.card_farming_current_game_time.set_text(str(elapsed_time))

        return True
    else:
        return False


def total_card_count(badges):
    generator = stlib.card_farming.get_total_card_count(badges)
    for card_count in generator:
        ui.main_window.card_farming_total_card_left.set_text('{} cards'.format(card_count))
        Gtk.main_iteration()

    return False


def card_farming_timer(dry_run, badges, badge_current):
    badge = badges[badge_current]

    if ui.card_farming_is_running:
        # Update card drop
        # If the current game have more cards, return and wait the new loop
        # otherwise, close, go to next badge, and start new game (see bellow)
        if ui.fake_app_id:
            card_count = stlib.card_farming.get_card_count(badge, True)

            if card_count is 0:
                if not dry_run:
                    stlib.libsteam.stop_wrapper()
                    ui.card_farming_is_running = False

                badge_current += 1
            else:
                return True

        # Start new game because the last check don't found more cards or a fake id
        if not dry_run:
            stlib.logger.info('Preparing. Please wait...')
            ui.fake_app_id = stlib.card_farming.get_game_id(badge)

            ui.main_window.card_farming_current_game.set_text(stlib.card_farming.get_game_name(badge))
            ui.main_window.card_farming_card_left.set_text('{} cards'.format(stlib.card_farming.get_card_count(badge)))

            ui.card_farming_game_start_time = time.time()
            stlib.libsteam.run_wrapper(ui.fake_app_id)
            ui.fake_app_is_running = True
            stlib.logger.info('Running {}'.format(ui.fake_app_id))
            GLib.timeout_add_seconds(1, fake_app_timer, ui.card_farming_game_start_time)
        return True
    else:
        return False


def fake_app_timer(start_time):
    elapsed_seconds = round(time.time() - start_time)
    elapsed_time = datetime.timedelta(seconds=elapsed_seconds)

    if ui.fake_app_is_running:
        if not stlib.libsteam.is_wrapper_running():
            ui.application.update_status_bar("This is not a valid gameID.")
            message = ui.main.MessageDialog(Gtk.MessageType.ERROR,
                                            'Fake Steam App',
                                            'This is not a valid gameID.',
                                            "Please, check if you write correctly and try again.")
            message.show()

            ui.fake_app_is_running = False
            ui.main_window.start.set_sensitive(True)
            ui.main_window.stop.set_sensitive(False)
            ui.main_window.fake_app_current_game.set_text('')
            ui.main_window.fake_app_current_time.set_text('')

            return False
        else:
            ui.main_window.fake_app_current_game.set_text(ui.fake_app_id)
            ui.main_window.fake_app_current_time.set_text(str(elapsed_time))

            return True
    else:
        return False
