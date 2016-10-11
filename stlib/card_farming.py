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


def get_steam_profile():
    return '{}/?redirectURL=id/{}'.format(ui.globals.Logins.steam_check_page,
                                          ui.globals.Logins.steam_user)


def remove_completed_badges(badges):
    new_badges = []
    for badge in badges:
        if get_card_count(badge) != 0:
            new_badges.append(badge)

    return new_badges


def get_badge_page_count():
    profile = get_steam_profile()
    html = stlib.network.try_get_html('steam', '{}/badges/'.format(profile))

    try:
        page_count = int(html.findAll('a', class_='pagelink')[-1].text)
    except:
        page_count = 1

    return page_count


def get_badges(page):
    profile = get_steam_profile()
    html = stlib.network.try_get_html('steam', '{}/badges/?p={}'.format(profile, page))

    return html.findAll('div', class_='badge_title_row')

def get_game_name(badge):
    title = badge.find('div', class_='badge_title')

    return title.text.split('\t\t\t\t\t\t\t\t\t', 2)[1]


def get_game_id(badge):
    try:
        game_href = badge.find('a')['href']
    except TypeError:
        # FIXME: It's a foil badge. The game id is above the badge_title_row...
        return str(000000)

    try:
        game_id = game_href.split('/', 3)[3]
    except IndexError:
        # Possibly a game without cards
        # TODO: This can speed up the remove_completed_badges?
        game_id = game_href.split('_', 6)[4]

    return str(game_id)


def get_card_count(badge, update_from_web=False):
    if update_from_web:
        profile = get_steam_profile()
        game_id = get_game_id(badge)
        html = stlib.network.try_get_html('steam', '{}/gamecards/{}'.format(profile, game_id))
        stats = html.find('div', class_='badge_title_stats_drops')
        progress = stats.find('span', class_='progress_info_bold')
    else:
        progress = badge.find('span', class_='progress_info_bold')

    if not progress or 'No' in progress.text:
        return 0
    else:
        return int(progress.text.split(' ', 3)[0])


def get_cards_info():
    cards_info = {k: [] for k in ['game_name', 'card_count', 'badge_price']}
    html = stlib.network.get_html('http://www.steamcardexchange.net/index.php?badgeprices')

    for info in html.findAll('tr')[1:]:
        cards_info['game_name'].append(info.find('a').text)
        cards_info['card_count'].append(int(info.findAll('td')[1].text))
        cards_info['badge_price'].append(float(info.findAll('td')[2].text[1:]))

    return cards_info


def get_badge_price(cards_info, badge):
    try:
        price_index = cards_info['game_name'].index(get_game_name(badge))
        return cards_info['badge_price'][price_index]
    except ValueError:
        return 0


def get_badge_cards_count(cards_info, badge):
    return cards_info['card_count'][cards_info['game_name'].index(get_game_name(badge))]


def get_total_card_count():
    badges_page_count = get_badge_page_count()

    card_count = 0
    for page in range(1, badges_page_count+1):
        badges = get_badges(page)
        for badge in badges:
            card_count += get_card_count(badge)
            yield card_count


def order_by_most_valuable(cards_info, badges):
    prices = [get_badge_price(cards_info, badge) for badge in badges]
    badges_count = len(badges)
    badges_order = sorted(range(badges_count),
                          key=lambda key: prices[key],
                          reverse=True)
    ordered_badges = []

    for price in prices:
        ordered_badges = [badges[index] for index in badges_order]

    return ordered_badges
