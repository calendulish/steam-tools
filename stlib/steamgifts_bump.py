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


def get_trade_page(trade_id):
    response = stlib.network.try_get_response('steamgifts', '{}/{}/'.format(stlib.steamgifts_trade_page,
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
    post_data = {'xsrf_token': data['xsrf_token'], 'do': 'bump_trade'}

    try:
        post_response = stlib.network.try_get_response('steamgifts', response.url, data=post_data)

        if 'Please wait another' in post_response.content.decode('utf-8'):
            post_html = bs4.BeautifulSoup(post_response.content, 'html.parser')
            error = post_html.find('div', class_='header__error')
            minutes_left = error.text.split(' ')[5]
            stlib.logger.warning('%s (%s) Already bumped. Waiting more %s minutes',
                                 trade_id,
                                 trade_title,
                                 minutes_left)
            return minutes_left
        else:
            response = stlib.network.try_get_response('steamgifts', 'https://www.steamgifts.com/trades')
            if trade_id in response.content.decode('utf-8'):
                stlib.logger.info('%s (%s) Bumped!', trade_id, trade_title)
                return True
            else:
                raise AttributeError
    except Exception as e:
        stlib.logger.error('ERROR: %s', e)
        stlib.logger.error('The trade %s will be ignored for now.', trade_id)
        stlib.logger.error('Please, report. (https://github.com/ShyPixie/steam-tools/issues/new)')
        return False
