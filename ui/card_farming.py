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

import logging
import time

import stlib


class Farm:
    def __init__(self, session):
        self.logger = logging.getLogger('root')
        self.config_parser = stlib.config.Parser()
        self.network_session = stlib.network.Session(session)

    def get_badges(self, profile):
        html = self.network_session.try_get_html('steam', '{}/badges/'.format(profile))
        badges = html.findAll('div', class_='badge_title_row')

        try:
            page_count = int(html.findAll('a', class_='pagelink')[-1].text)
            self.logger.verbose('I found %d pages of badges', page_count)

            for page_number in range(2, page_count + 1):
                url = '{}/badges/?p={}'.format(profile, page_number)
                html = self.network_session.try_get_html('steam', url)
                badges.extend(html.findAll('div', class_='badge_title_row'))
        except IndexError:
            self.logger.verbose('I found only 1 page of badges')

        badge_set = {k:[] for k in ['gameID', 'gameName', 'cardCount', 'cardValue']}
        for badge in badges:
            progress = badge.find('span', class_='progress_info_bold')
            title = badge.find('div', class_='badge_title')
            title.span.unwrap()

            if not progress or 'No' in progress.text:
                try:
                    game_id = badge.find('a')['href'].split('_')[-3]
                except(TypeError, IndexError):
                    # Ignore. It's an special badge (not from games/apps)
                    continue

                card_count = 0
            else:
                card_count = int(progress.text.split(' ', 3)[0])
                game_id = badge.find('a')['href'].split('/', 3)[3]

            game_name = title.text.split('\t\t\t\t\t\t\t\t\t', 2)[1]

            badge_set['cardCount'].append(card_count)
            badge_set['gameID'].append(game_id)
            badge_set['gameName'].append(game_name)

        return badge_set

    def get_card_values(self):
        price_set = {k:[] for k in ['game', 'avg']}
        price_page = 'http://www.steamcardexchange.net/index.php?badgeprices'
        html = self.network_session.try_get_html('cardexchange', price_page)

        for game in html.findAll('tr')[1:]:
            price_set['game'].append(game.find('a').text)
            card_count = int(game.findAll('td')[1].text)
            card_price = float(game.findAll('td')[2].text[1:])
            price_set['avg'].append(card_price / card_count)

        return price_set

    def update_card_count(self, profile, game_id):
        self.logger.verbose('Updating card count')
        dry_run = self.config_parser.config.getboolean('Debug', 'DryRun', fallback=False)

        for i in range(5):
            html = self.network_session.try_get_html('steam', '{}/gamecards/{}'.format(profile, game_id))
            stats = html.find('div', class_='badge_title_stats_drops')

            if stats:
                progress = stats.find('span', class_='progress_info_bold')

                if not progress or 'No' in progress.text or dry_run:
                    return 0
                else:
                    card_count = int(progress.text.split(' ', 3)[0])
                    return card_count
            else:
                self.logger.warning('Something is wrong with the page, trying again')
                time.sleep(3)

        self.logger.error('I cannot find the progress info for this badge. (Connection problem?)')
        self.logger.error('I\'ll jump to the next this time and try again later.')
        return 0
