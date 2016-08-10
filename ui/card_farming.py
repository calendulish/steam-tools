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

import time

import stlib
import ui


def get_badges(add_prices=True):
    stlib.logger.console_msg('Getting badges info...', end='\r')
    profile = '{}/?redirectURL=id/{}'.format(ui.globals.Logins.steam_check_page,
                                             ui.globals.Logins.steam_user)
    html = stlib.network.try_get_html('steam', '{}/badges/'.format(profile))
    badges = html.findAll('div', class_='badge_title_row')

    stlib.logger.console_msg('Searching for badges...', end='\r')
    try:
        page_count = int(html.findAll('a', class_='pagelink')[-1].text)
        ui.globals.logger.verbose('I found %d pages of badges', page_count)

        for page_number in range(2, page_count + 1):
            url = '{}/badges/?p={}'.format(profile, page_number)
            html = stlib.network.try_get_html('steam', url)
            badges.extend(html.findAll('div', class_='badge_title_row'))
    except IndexError:
        ui.globals.logger.verbose('I found only 1 page of badges')

    stlib.logger.console_msg('Searching card list...', end='\r')
    for badge in badges:
        progress = badge.find('span', class_='progress_info_bold')
        title = badge.find('div', class_='badge_title')
        title.span.unwrap()

        if not progress or 'No' in progress.text:
            # Ignore all already completed badges
            continue
        else:
            card_count = int(progress.text.split(' ', 3)[0])
            game_id = badge.find('a')['href'].split('/', 3)[3]

        game_name = title.text.split('\t\t\t\t\t\t\t\t\t', 2)[1]

        ui.globals.CardFarming.badge_set['cardCount'].append(card_count)
        ui.globals.CardFarming.badge_set['gameID'].append(game_id)
        ui.globals.CardFarming.badge_set['gameName'].append(game_name)

        stlib.logger.console_fixer('\r')
        stlib.logger.console_msg('I found {} cards in the {}({}) badge'.format(card_count,
                                                                               game_name,
                                                                               game_id),
                                 end='\r')

    if add_prices:
        get_card_prices()

    stlib.logger.console_fixer()


def get_card_prices():
    stlib.logger.console_fixer('\r')
    stlib.logger.console_msg('Getting cards values...', end='\r')

    config_parser = stlib.config.read()
    price_page = 'http://www.steamcardexchange.net/index.php?badgeprices'
    html = stlib.network.get_html(price_page)

    for game in html.findAll('tr')[1:]:
        ui.globals.CardFarming.price_set['game'].append(game.find('a').text)
        card_count = int(game.findAll('td')[1].text)
        card_price = float(game.findAll('td')[2].text[1:])
        ui.globals.CardFarming.price_set['avg'].append(card_price / card_count)

    # Add prices to ui.globals.CardFarming.badge_set
    stlib.logger.console_msg('Adding prices to their respective games...', end='\r')
    for game in ui.globals.CardFarming.badge_set['gameName']:
        avg_price = ui.globals.CardFarming.price_set['avg'][ui.globals.CardFarming.price_set['game'].index(game)]

        try:
            ui.globals.CardFarming.badge_set['cardValue'].append(avg_price)
        except ValueError:
            ui.globals.CardFarming.badge_set['cardValue'].append(0)

        stlib.logger.console_msg('{} worth currently {} (avg)'.format(game, avg_price),
                                 end='\r')

    if config_parser.getboolean('Config', 'MostValuableFirst', fallback=True):
        stlib.logger.console_msg('Rearranging cards to get the most valuable first...', end='\r')
        cards_count = len(ui.globals.CardFarming.badge_set['cardValue'])
        cards_order = sorted(range(cards_count),
                             key=lambda key: ui.globals.CardFarming.badge_set['cardValue'][key],
                             reverse=True)

        # reorder all items from ui.globals.CardFarming.badge_set
        for item, value in ui.globals.CardFarming.badge_set.items():
            ui.globals.CardFarming.badge_set[item] = [value[index] for index in cards_order]


def update_card_count(index):
    ui.globals.logger.verbose('Updating card count')
    config_parser = stlib.config.read()
    game_id = ui.globals.CardFarming.badge_set['gameID'][index]
    dry_run = config_parser.getboolean('Debug', 'DryRun', fallback=False)
    profile = '{}/?redirectURL=id/{}'.format(ui.globals.Logins.steam_check_page,
                                             ui.globals.Logins.steam_user)

    for i in range(5):
        html = stlib.network.try_get_html('steam', '{}/gamecards/{}'.format(profile, game_id))
        stats = html.find('div', class_='badge_title_stats_drops')

        if stats:
            progress = stats.find('span', class_='progress_info_bold')

            if not progress or 'No' in progress.text or dry_run:
                ui.globals.CardFarming.badge_set['cardCount'][index] = 0
                return None
            else:
                card_count = int(progress.text.split(' ', 3)[0])
                ui.globals.CardFarming.badge_set['cardCount'][index] = card_count
                return None
        else:
            ui.globals.logger.warning('Something is wrong with the page, trying again')
            time.sleep(3)

    ui.globals.logger.error('I cannot find the progress info for this badge. (Connection problem?)')
    ui.globals.logger.error('I\'ll jump to the next this time and try again later.')

    ui.globals.CardFarming.badge_set['cardCount'][index] = 0
