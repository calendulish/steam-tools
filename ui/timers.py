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

import stlib
import ui


def status_bar_text_pushed_timer(context):
    window = ui.globals.Window.main
    window.status_bar.pop(context)
    return False


def card_farming_time_timer(start_time):
    window = ui.globals.Window.main
    elapsed_seconds = int(time.time() - start_time)
    elapsed_time = datetime.timedelta(seconds=elapsed_seconds)

    if ui.globals.CardFarming.is_running:
        window.card_farming_total_time.set_text(str(elapsed_time))

        if ui.globals.CardFarming.game_start_time:
            elapsed_seconds = int(time.time() - ui.globals.CardFarming.game_start_time)
            elapsed_time = datetime.timedelta(seconds=elapsed_seconds)
            window.card_farming_current_game_time.set_text(str(elapsed_time))

        return True
    else:
        return False

def total_card_count():
    window = ui.globals.Window.main
    generator = stlib.card_farming.get_total_card_count()
    for card_count in generator:
        window.card_farming_total_card_left.set_text('{} cards'.format(card_count))
        ui.Gtk.main_iteration()

    return False

def card_farming_timer(dry_run, badges, badge_current, cards_info):
    window = ui.globals.Window.main
    badge = badges[badge_current]

    if ui.globals.CardFarming.is_running:
        # Update card drop
        # If the current game have more cards, return and wait the new loop
        # otherwise, close, go to next badge, and start new game (see bellow)
        if ui.globals.FakeApp.id:
            window.update_status_bar('Checking if the game has more cards to drop.')
            card_count = stlib.card_farming.get_card_count(badge, True)

            if card_count is 0:
                if not dry_run:
                    ui.libsteam.stop_wrapper()
                    ui.globals.FakeApp.is_running = False

                badge_current += 1
            else:
                return True

        # Start new game because the last check don't found more cards or a fake id
        if not dry_run:
            ui.globals.logger.info('Preparing. Please wait...')
            ui.globals.FakeApp.id = stlib.card_farming.get_game_id(badge)

            window.card_farming_current_game.set_text(stlib.card_farming.get_game_name(badge))
            window.card_farming_card_left.set_text('{} cards'.format(stlib.card_farming.get_card_count(badge)))

            ui.globals.CardFarming.game_start_time = time.time()
            ui.libsteam.run_wrapper(ui.globals.FakeApp.id)
            ui.globals.FakeApp.is_running = True
            ui.globals.logger.info('Running {}'.format(ui.globals.FakeApp.id))
            ui.GLib.timeout_add_seconds(1, fake_app_timer, ui.globals.CardFarming.game_start_time)
        return True
    else:
        return False


def fake_app_timer(start_time):
    window = ui.globals.Window.main
    elapsed_seconds = round(time.time() - start_time)
    elapsed_time = datetime.timedelta(seconds=elapsed_seconds)

    if ui.globals.FakeApp.is_running:
        if not ui.libsteam.is_wrapper_running():
            window.update_status_bar("This is not a valid gameID.")
            window.new_dialog(ui.Gtk.MessageType.ERROR,
                              'Fake Steam App',
                              'This is not a valid gameID.',
                              "Please, check if you write correctly and try again.")

            ui.globals.FakeApp.is_running = False
            window.start.set_sensitive(True)
            window.stop.set_sensitive(False)
            window.fake_app_current_game.set_text('')
            window.fake_app_current_time.set_text('')

            return False
        else:
            window.fake_app_current_game.set_text(ui.globals.FakeApp.id)
            window.fake_app_current_time.set_text(str(elapsed_time))

            return True
    else:
        return False
