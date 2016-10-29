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
import itertools
import random
import time

import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, GLib

import stlib
import ui


def status_bar_text_pushed_timer(context):
    ui.main_window.status_bar.pop(context)
    return False

def hide_info_label():
    ui.main_window.info_label.hide()
    return False

def card_farming_time_timer(start_time):
    if not ui.card_farming_is_running:
        return False

    elapsed_seconds = int(time.time() - start_time)
    elapsed_time = datetime.timedelta(seconds=elapsed_seconds)

    ui.main_window.card_farming_total_time.set_text(str(elapsed_time))

    if ui.card_farming_game_start_time:
        elapsed_seconds = int(time.time() - ui.card_farming_game_start_time)
        elapsed_time = datetime.timedelta(seconds=elapsed_seconds)
        ui.main_window.card_farming_current_game_time.set_text(str(elapsed_time))

    return True


def total_card_count(badges):
    generator = stlib.card_farming.get_total_card_count(badges)
    for card_count in generator:
        ui.main_window.card_farming_total_card_left.set_text('{} cards'.format(card_count))
        Gtk.main_iteration()

    return False


def card_farming_timer(dry_run, badges):
    if not ui.card_farming_is_running:
        return False

    badge = badges[stlib.card_farming.current_badge]

    # Update card drop
    # If the current game have more cards, return and wait the new loop
    # otherwise, close, go to next badge, and start new game (see bellow)
    if ui.fake_app_id:
        card_count = stlib.card_farming.get_card_count(badge, True)

        if card_count is 0:
            if not dry_run:
                stlib.libsteam.stop_wrapper()
                ui.card_farming_is_running = False

            stlib.card_farming.current_badge += 1
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


def fake_app_timer(start_time):
    if not ui.fake_app_is_running:
        return False

    elapsed_seconds = round(time.time() - start_time)
    elapsed_time = datetime.timedelta(seconds=elapsed_seconds)

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


def progress_bar_pulse(type_, progress_bar, start_time, maximum_time):
    elapsed_seconds = int(time.time() - start_time)
    time_left = datetime.timedelta(seconds=maximum_time - elapsed_seconds)

    fraction = elapsed_seconds / maximum_time
    progress_bar.set_fraction(fraction)
    progress_bar.set_text(str(time_left))

    if fraction >= 1.0:
        progress_bar.set_text('0:00:00')
        setattr(ui, type_ + '_waiting', False)
        return False
    else:
        return True


def steamtrades_bump_timer(trade_ids, MIN_wait_time, MAX_wait_time):
    if not ui.steamtrades_bump_is_running:
        return False

    if ui.steamtrades_bump_waiting:
        return True

    try:
        trade_id = trade_ids[stlib.steamtrades_bump.current_trade]
    except IndexError:
        stlib.logger.warning('There\'s nothing else to do. Stopping.')
        ui.signals.on_steamtrades_bump_stop()
        return False

    current_datetime = time.strftime('%B, %d, %Y - %H:%M:%S')
    stlib.logger.info('Bumping now! %s', current_datetime)

    response = stlib.steamtrades_bump.get_trade_page(trade_id)

    if not response:
        stlib.steamtrades_bump.current_trade += 1
        return True

    return_ = stlib.steamtrades_bump.bump(response)

    if type(return_) == int:
        MIN_wait_time = return_ * 60
        MAX_wait_time = MIN_wait_time + 400

    random_time = random.randint(MIN_wait_time, MAX_wait_time)

    start_time = time.time()

    GLib.timeout_add_seconds(1,
                             progress_bar_pulse,
                             'steamtrades_bump',
                             ui.main_window.ST_bump_progress_bar,
                             start_time,
                             random_time)

    ui.steamtrades_bump_waiting = True

    return True


def steamgifts_join_giveaway_timer(giveaway, user_points):
    if not ui.steamgifts_join_is_running:
        return False

    if ui.steamgifts_join_giveaway_waiting:
        return True

    try:
        giveaway = next(giveaway)
    except StopIteration:
        # FIXME
        stlib.logger.verbose('There\'s nothing else for type **TYPE**')
        ui.steamgifts_join_waiting = False
        return False

    giveaway_points = stlib.steamgifts_join.get_giveaway_points(giveaway)
    giveaway_name = stlib.steamgifts_join.get_giveaway_name(giveaway)

    if giveaway.find('div', class_='is-faded'):
        stlib.logger.verbose('Ignoring %s because you already joined.', giveaway_name)
        return True

    if user_points == 0:
        stlib.logger.verbose('You don\'t have more points. Waiting.')
        ui.steamgifts_join_waiting = False
        return False

    if user_points >= giveaway_points:
        points_spent = stlib.steamgifts_join.join(giveaway)
        user_points -= points_spent

        ui.main_window.SG_join_last_giveaway.set_text('{} ({}P)'.format(giveaway_name, points_spent))
        ui.main_window.SG_join_current_points.set_text('{} points'.format(user_points))

        antiban_time = random.randint(1, 15)
        start_time = time.time()

        GLib.timeout_add_seconds(1,
                                 progress_bar_pulse,
                                 'steamgifts_join_giveaway',
                                 ui.main_window.SG_join_antiban_progress_bar,
                                 start_time,
                                 antiban_time)

        ui.steamgifts_join_giveaway_waiting = True
    else:
        stlib.logger.verbose('Ignoring %s', stlib.steamgifts_join.get_giveaway_name(giveaway))
        stlib.logger.verbose('because the account don\'t have the requirements to enter.')

    return True


def steamgifts_join_timer(type, MIN_wait_time, MAX_wait_time):
    if not ui.steamgifts_join_is_running:
        return False

    if ui.steamgifts_join_waiting:
        return True

    config_parser = stlib.config.read()

    try:
        type = next(type)
    except StopIteration:
        random_time = random.randint(MIN_wait_time, MAX_wait_time)

        start_time = time.time()

        GLib.timeout_add_seconds(1,
                                 progress_bar_pulse,
                                 'steamgifts_join',
                                 ui.main_window.SG_join_progress_bar,
                                 start_time,
                                 random_time)

        ui.steamgifts_join_waiting = True

        return True

    query_url = '{}?type='.format(stlib.steamgifts_query_page)

    if type == 'wishlist':
        query_url += 'wishlist'
    elif type == 'new':
        query_url += 'new'
    elif type == 'main':
        pass
    else:
        query_url += '&q={}'.format(type)

    html = stlib.network.try_get_html('steamgifts', query_url)
    giveaway_generator = stlib.steamgifts_join.get_giveaways(html)

    if config_parser.getboolean('SteamGifts', 'developerGiveaways', fallback=True):
        pinned_generator = stlib.steamgifts_join.get_pinned_giveaways(html)
        giveaway_generator = itertools.chain(giveaway_generator, pinned_generator)

        user_points = stlib.steamgifts_join.get_user_points(html)

        GLib.timeout_add(50,
                         steamgifts_join_giveaway_timer,
                         giveaway_generator,
                         user_points)

        ui.steamgifts_join_waiting = True

    return True
