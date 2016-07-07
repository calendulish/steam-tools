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

import configparser
import json
import logging
import os
import sys
import time

import stlib
import ui


class SteamTools:
    def __init__(self, session, cParams):
        self.logger = logging.getLogger('root')
        self.config_parser = stlib.config.Parser()
        self.module = cParams.cli[0]
        self.parameters = cParams
        self.libsteam = ui.libsteam.LibSteam()
        self.farm = ui.card_farming.Farm(session)
        self.network_session = stlib.network.Session(session)
        self.browser_bridge = stlib.cookie.BrowserBridge()
        self.check = ui.logins.CheckLogins(session)

        self.select_profile()

        if self.module in dir(self):
            eval('self.' + self.module + '()')
        else:
            self.logger.critical("Please, check the command line.")
            self.logger.critical("The module %s don't exist", self.module)

    def select_profile(self):
        self.config_parser.read_config()

        try:
            profile_name = self.config_parser.config.get('Config', 'chromeProfile')
        except configparser.NoOptionError:
            profiles = self.browser_bridge.get_chrome_profile()

            if not len(profiles):
                self.logger.error('I cannot find your chrome/Chromium profile')
                self.logger.error('Some functions will be disabled.')
            elif len(profiles) == 1:
                self.config_parser.config.set('Config', 'chromeProfile', profiles[0])
                self.config_parser.write_config()
            else:
                self.logger.warning("Who are you?")
                for i in range(len(profiles)):
                    with open(os.path.join(profiles[i], 'Preferences')) as prefs_file:
                        prefs = json.load(prefs_file)

                    try:
                        profile_name = prefs['account_info'][0]['full_name']
                    except KeyError:
                        profile_name = prefs['profile']['name']

                    self.logger.warning('  - [%d] %s (%s)',
                                        i + 1,
                                        profile_name,
                                        os.path.basename(profiles[i]))

                while True:
                    try:
                        user_input = input("Please, input an number [1-{}]:".format(len(profiles)))
                        selected_profile = int(user_input - 1)
                        if selected_profile >= len(profiles) or selected_profile < 0:
                            raise ValueError
                    except ValueError:
                        self.logger.error('Please, choose an valid option.')
                        continue

                    self.logger.warning("Okay, I'll remember that next time.")
                    break

                self.config_parser.config.set('Config', 'chromeProfile', profiles[selected_profile -1])
                self.config_parser.write_config()

    def cardfarming(self):
        user = self.check.steam_login()

        profile = 'https://steamcommunity.com/login/checkstoredlogin/?redirectURL=id/' + user

        self.logger.info('Hello {}'.format(user))
        self.logger.info('Getting badges info...')

        badge_set = self.farm.get_badges(profile)

        if self.config_parser.config.getboolean('Config', 'MostValuableFirst', fallback=True):
            self.logger.info('Getting cards values...')
            price_set = self.farm.get_card_values()

            for game in badge_set['gameName']:
                try:
                    badge_set['cardValue'].append(price_set['avg'][price_set['game'].index(game)])
                except ValueError:
                    badge_set['cardValue'].append(0)

            self.logger.info('Rearranging cards')
            cards_count = len(badge_set['cardValue'])
            cards_order = sorted(range(cards_count),
                                 key=lambda key: badge_set['cardValue'][key],
                                 reverse=True)

            for item, value in badge_set.items():
                badge_set[item] = [value[index] for index in cards_order]
        else:
            badge_set['cardValue'] = [0 for _ in badge_set['gameID']]

        self.logger.warning('Ready to start.')
        game_count = len(badge_set['gameID'])

        for index in range(game_count):
            if badge_set['cardCount'][index] < 1:
                self.logger.verbose('%s have no cards to drop. Ignoring.', badge_set['gameName'][index])
                continue

            self.logger.info('Starting game %s (%s)', badge_set['gameName'][index], badge_set['gameID'][index])
            dry_run = self.config_parser.config.getboolean('Debug', 'DryRun', fallback=False)

            if not dry_run:
                if not self.libsteam.is_steam_running():
                    self.logger.critical('Unable to locate a running instance of steam.')
                    self.logger.critical('Please, start Steam and try again.')
                    sys.exit(1)

                self.logger.info('Preparing. Please wait...')
                fake_app = self.libsteam.run_wrapper(badge_set['gameID'][index])
                self.logger.info('Running {}'.format(badge_set['gameID'][index]))

            while True:
                card_count = badge_set['cardCount'][index]
                stlib.logger.console_msg('{:2d} cards drop remaining. Waiting...'.format(card_count), end='\r')
                self.logger.verbose('Waiting card drop loop')
                self.logger.trace("Current: %s", [badge_set[i][index] for i, v in badge_set.items()])

                for i in range(40):
                    if not dry_run and fake_app.poll():
                        stlib.logger.console_fixer()
                        self.logger.critical(fake_app.stderr.read().decode('utf-8'))
                        sys.exit(1)

                    try:
                        time.sleep(1)
                    except KeyboardInterrupt:
                        sys.exit(0)

                stlib.logger.console_fixer('\r')
                stlib.logger.console_msg('Checking if game have more cards drops...', end='\r')
                badge_set['cardCount'][index] = self.farm.update_card_count(profile, badge_set['gameID'][index])
                stlib.logger.console_fixer('\r')

                if badge_set['cardCount'][index] < 1:
                    stlib.logger.console_fixer('\r')
                    self.logger.warning('No more cards to drop.')
                    break

            self.logger.info('Closing %s', badge_set['gameName'][index])

            if not dry_run:
                self.libsteam.stop_wrapper(fake_app)

        self.logger.warning('There\'s nothing else to do. Leaving.')

    def fakeapp(self):
        try:
            game_id = self.parameters.cli[1]
        except IndexError:
            self.logger.critical("Unable to locate the gameID.")
            self.logger.critical("Please, check the command line.")
            sys.exit(1)

        if self.libsteam.is_steam_running():
            self.logger.info("Preparing. Please wait...")
            fake_app = self.libsteam.run_wrapper(game_id)

            time.sleep(3)
            if fake_app.poll():
                self.logger.critical("This is not a valid gameID.")
                sys.exit(1)

            try:
                self.logger.info("Running {}".format(game_id))
                fake_app.wait()
            except KeyboardInterrupt:
                pass
        else:
            self.logger.critical("Unable to locate a running instance of steam.")
            self.logger.critical("Please, start Steam and try again.")
            sys.exit(1)

        sys.exit(0)
