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

import stlib

giveaway_type = None


def type_generator(type_list):
    for line in type_list.split(','):
        yield line.strip()


def configure():
    config_url = 'https://www.steamgifts.com/account/settings/giveaways'
    html = stlib.network.try_get_html('steamgifts', config_url)
    form = html.find('form')
    data = dict([(inputs['name'], inputs['value']) for inputs in form.findAll('input')])

    post_data = {'xsrf_token': data['xsrf_token'],
                 'filter_giveaways_exist_in_account': 1,
                 'filter_giveaways_missing_base_game': 1,
                 'filter_giveaways_level': 1}

    stlib.network.try_get_response('steamgifts', config_url, data=post_data)

    return None


def get_user_points(html=None):
    if not html:
        html = stlib.network.try_get_html('steamgifts', stlib.steamgifts_check_page)

    points = html.find('span', class_="nav__points")
    return int(points.text)


def get_user_level(html):
    level = html.find('span', class_=None)
    return int(''.join(filter(str.isdigit, level)))


def get_pinned_giveaways(html):
    container = html.find('div', class_='widget-container')
    pinned_giveaways = []

    try:
        pinned_widget = container.find('div', class_='pinned-giveaways__outer-wrap')
        pinned_giveaways = pinned_widget.findAll('div', class_='giveaway__row-outer-wrap')

        if not pinned_giveaways:
            raise AttributeError
    except AttributeError:
        stlib.logger.error('Cannot found any developer giveaways. Ignoring.')

    for pinned_giveaway in pinned_giveaways:
        yield pinned_giveaway


def get_giveaways(html):
    container = html.find('div', class_='widget-container')
    head = container.find('div', class_='page__heading')
    giveaways = head.findAllNext('div', class_='giveaway__row-outer-wrap')

    for giveaway in giveaways:
        yield giveaway


def get_giveaway_name(giveaway):
    head = giveaway.find('a', class_='giveaway__heading__name')
    return head.text


def get_giveaway_query(giveaway):
    head = giveaway.find('a', class_='giveaway__heading__name')
    return head['href']


def get_giveaway_copies(giveaway):
    head = giveaway.find('span', class_='giveaway__heading__thin')

    if 'Copies' in head.text:
        copies = ''.join(filter(str.isdigit, head.text))
    else:
        copies = 1

    return int(copies)


def get_giveaway_points(giveaway):
    head = giveaway.find('span', class_='giveaway__heading__thin')

    # If the game have more than 1 copies, the head must be fixed
    if 'Copies' in head.text:
        head = head.findNext('span', class_='giveaway__heading__thin')

    points = ''.join(filter(str.isdigit, head.text))

    return int(points)


def get_giveaway_level(giveaway):
    try:
        level_column = giveaway.find('div', class_='giveaway__column--contributor-level')
        level = ''.join(filter(str.isdigit, level_column.text))
    except AttributeError:
        level = 0

    return int(level)


def join(giveaway):
    giveaway_points = get_giveaway_points(giveaway)
    giveaway_name = get_giveaway_name(giveaway)
    giveaway_copies = get_giveaway_copies(giveaway)
    query_url = 'https://steamgifts.com' + get_giveaway_query(giveaway)
    html = stlib.network.try_get_html('steamgifts', query_url)
    sidebar = html.find('div', class_='sidebar')
    form = sidebar.find('form')
    points_spent = 0

    try:
        data = dict([(inputs['name'], inputs['value']) for inputs in form.findAll('input')])

        post_data = {'xsrf_token': data['xsrf_token'],
                     'do': 'entry_insert',
                     'code': data['code']}
    except (KeyError, AttributeError):
        stlib.logger.error('%s has expired. Ignoring.', giveaway_name)
        return points_spent

    stlib.network.try_get_response('steamgifts', 'https://www.steamgifts.com/ajax.php', data=post_data)
    points_spent = giveaway_points

    stlib.logger.info('Spent %d points in the giveaway of %s (Copies: %d)',
                      giveaway_points,
                      giveaway_name,
                      giveaway_copies)

    return points_spent
