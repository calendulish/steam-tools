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

import bs4

import stlib

current_trade = 0


def get_trade_page(trade_id):
    response = stlib.network.try_get_response('steamtrades', '{}/{}/'.format(stlib.steamtrades_trade_page,
                                                                             trade_id))

    if not response:
        stlib.logger.warning('The trade ID %s is not valid.', trade_id)
        return None

    return response


def get_trade_id(response):
    trade_id = response.url.split('/')[4]
    return trade_id


def get_trade_title(response):
    trade_title = os.path.basename(response.url).replace('-', ' ')
    return trade_title


def bump(response):
    trade_id = get_trade_id(response)
    trade_title = get_trade_title(response)
    html = bs4.BeautifulSoup(response.content, 'html.parser')
    form = html.find('form')
    data = dict([(inputs['name'], inputs['value']) for inputs in form.findAll('input')])
    post_data = {'code': data['code'], 'xsrf_token': data['xsrf_token'], 'do': 'trade_bump'}

    post_response = stlib.network.try_get_response('steamtrades',
                                                   'https://www.steamtrades.com/ajax.php',
                                                   data=post_data)

    if 'Please wait another' in post_response.content.decode('utf-8'):
        post_html = bs4.BeautifulSoup(post_response.content, 'html.parser')
        error = post_response.json()['popup_heading_h2'][0]
        minutes_left = int(error.split(' ')[3])
        stlib.logger.warning('%s (%s) Already bumped. Waiting more %d minutes',
                             trade_id,
                             trade_title,
                             minutes_left)
        return minutes_left
    else:
        response = stlib.network.try_get_response('steamtrades', stlib.steamtrades_trade_page[:-1] + 's')

        if trade_id in response.content.decode('utf-8'):
            stlib.logger.info('%s (%s) Bumped!', trade_id, trade_title)
            return True
        else:
            stlib.logger.critical('Something is wrong with %s (%s)', trade_id, trade_title)
            return False
