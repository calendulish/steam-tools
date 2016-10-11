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

import json
import os
import sys
import time

import gevent

import stlib
import ui


class SteamTools:
    def __init__(self, console_params):
        self.config_parser = stlib.config.read()
        self.module = console_params.cli[0]
        self.parameters = console_params

        self.select_profile()

        class_name = self.__class__.__name__
        module_function = ''.join(['_', class_name, '__', self.module])

        if module_function in dir(self):
            eval(''.join(['self.', module_function, '()']))
        else:
            ui.globals.logger.critical("Please, check the command line.")
            ui.globals.logger.critical("The module %s don't exist", self.module)

    def select_profile(self):
        if not self.config_parser.has_option('Config', 'chromeProfile'):
            profiles = stlib.browser.get_chrome_profile()

            if not len(profiles):
                ui.globals.logger.error('I cannot find your chrome/Chromium profile')
                ui.globals.logger.error('Some functions will be disabled.')
            elif len(profiles) == 1:
                profile_name = os.path.join(stlib.browser.get_chrome_dir(), profiles[0])
                self.config_parser.set('Config', 'chromeProfile', profile_name)
                stlib.config.write()
            else:
                selected_profile = 0
                ui.globals.logger.warning("Who are you?")
                for i in range(len(profiles)):
                    with open(os.path.join(stlib.browser.get_chrome_dir(), profiles[i], 'Preferences')) as prefs_file:
                        prefs = json.load(prefs_file)

                    try:
                        account_name = prefs['account_info'][0]['full_name']
                    except KeyError:
                        account_name = prefs['profile']['name']

                    profile_name = profiles[i]
                    ui.globals.logger.warning('  - [%d] %s (%s)',
                                              i + 1,
                                              account_name,
                                              profile_name)

                while True:
                    try:
                        user_input = input("Please, input an number [1-{}]:".format(len(profiles)))
                        selected_profile = int(user_input) - 1
                        if selected_profile >= len(profiles) or selected_profile < 0:
                            raise ValueError
                    except ValueError:
                        ui.globals.logger.error('Please, choose an valid option.')
                        continue

                    print(selected_profile)
                    print(profiles[selected_profile])
                    ui.globals.logger.warning("Okay, I'll remember that next time.")
                    break

                self.config_parser.set('Config', 'chromeProfile', profiles[selected_profile])
                stlib.config.write()

    def __cardfarming(self):
        greenlet = gevent.Greenlet(stlib.network.try_get_response,
                                   'steam',
                                   stlib.steam_check_page)
        greenlet.link(ui.logins.check_steam_login)
        greenlet.start()
        greenlet.join()

        if not stlib.steam_user:
            sys.exit(1)

        ui.globals.logger.info('Hello {}'.format(stlib.steam_user))

        if stlib.libsteam.is_steam_running():
            stlib.logger.info('Preparing. Please wait...')
            badge_pages = stlib.card_farming.get_badge_page_count()
            badges = []
            for page in range(1, badge_pages+1):
                badges.extend(stlib.card_farming.get_badges(page))

            badges = stlib.card_farming.remove_completed_badges(badges)
            cards_info = stlib.card_farming.get_cards_info()

            if self.config_parser.getboolean('Config', 'MostValuableFirst', fallback=True):
                badges = stlib.card_farming.order_by_most_valuable(cards_info, badges)

            ui.globals.logger.warning('Ready to start.')

            for badge in badges:
                game_name = stlib.card_farming.get_game_name(badge)
                game_id = stlib.card_farming.get_game_id(badge)
                stlib.logger.info('Starting game %s (%s)', game_name, game_id)
                stlib.libsteam.run_wrapper(game_id)

                while True:
                    card_count = stlib.card_farming.get_card_count(badge, False)
                    stlib.logging.console_msg('{:2d} cards drop remaining. Waiting...'.format(card_count), end='\r')
                    stlib.logger.verbose('Waiting card drop loop')

                    for i in range(40):
                        if stlib.wrapper_process.poll():
                            stlib.logging.console_fixer()
                            stlib.logger.critical(stlib.wrapper_process.stderr.read().decode('utf-8'))
                            sys.exit(1)

                        try:
                            time.sleep(1)
                        except KeyboardInterrupt:
                            sys.exit(0)

                    stlib.logging.console_fixer('\r')
                    stlib.logging.console_msg('Checking if game have more cards drops...', end='\r')
                    card_count = stlib.card_farming.get_card_count(badge, True)

                    if card_count is 0:
                        stlib.logging.console_fixer('\r')
                        stlib.logger.warning('No more cards to drop.')
                        stlib.logger.info('Closing %s', game_name)
                        stlib.libsteam.stop_wrapper()
                        break
        else:
            stlib.logger.error('Unable to locate a running instance of steam.')
            stlib.logger.error('Please, start the Steam Client and try again.')
            sys.exit(1)

        stlib.logger.warning('There\'s nothing else to do. Leaving.')

    def __fakeapp(self):
        try:
            ui.globals.FakeApp.id = self.parameters.cli[1]
        except IndexError:
            ui.globals.logger.critical("Unable to locate the gameID.")
            ui.globals.logger.critical("Please, check the command line.")
            sys.exit(1)

        if stlib.libsteam.is_steam_running():
            ui.globals.logger.info("Preparing. Please wait...")
            stlib.libsteam.run_wrapper(ui.globals.FakeApp.id)

            time.sleep(3)
            if stlib.wrapper_process.poll():
                ui.globals.logger.critical("This is not a valid gameID.")
                sys.exit(1)

            try:
                ui.globals.logger.info("Running {}".format(ui.globals.FakeApp.id))
                stlib.wrapper_process.wait()
            except KeyboardInterrupt:
                pass
        else:
            ui.globals.logger.critical("Unable to locate a running instance of steam.")
            ui.globals.logger.critical("Please, start Steam and try again.")
            sys.exit(1)

        sys.exit(0)
