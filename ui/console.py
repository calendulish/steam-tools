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
        ui.logins.check_steam_login()

        ui.globals.logger.info('Hello {}'.format(ui.globals.Logins.steam_user))

        ui.card_farming.get_badges()

        if self.config_parser.getboolean('Config', 'MostValuableFirst', fallback=True):
            ui.card_farming.get_card_prices()

        ui.globals.logger.warning('Ready to start.')
        game_count = len(ui.globals.CardFarming.badge_set['gameID'])

        for index in range(game_count):
            if ui.globals.CardFarming.badge_set['cardCount'][index] < 1:
                ui.globals.logger.verbose('%s have no cards to drop. Ignoring.',
                                          ui.globals.CardFarming.badge_set['gameName'][index])
                continue

            stlib.logger.console_fixer()
            ui.globals.logger.info('Starting game %s (%s)',
                                   ui.globals.CardFarming.badge_set['gameName'][index],
                                   ui.globals.CardFarming.badge_set['gameID'][index])
            dry_run = self.config_parser.getboolean('Debug', 'DryRun', fallback=False)

            if not dry_run:
                if not ui.libsteam.is_steam_running():
                    ui.globals.logger.critical('Unable to locate a running instance of steam.')
                    ui.globals.logger.critical('Please, start Steam and try again.')
                    sys.exit(1)

                ui.globals.logger.info('Preparing. Please wait...')
                ui.libsteam.run_wrapper(ui.globals.CardFarming.badge_set['gameID'][index])
                ui.globals.logger.info('Running {}'.format(ui.globals.CardFarming.badge_set['gameID'][index]))

            while True:
                card_count = ui.globals.CardFarming.badge_set['cardCount'][index]
                stlib.logger.console_msg('{:2d} cards drop remaining. Waiting...'.format(card_count), end='\r')
                ui.globals.logger.verbose('Waiting card drop loop')
                ui.globals.logger.trace("Current: %s", [ui.globals.CardFarming.badge_set[i][index]
                                                        for i, v in ui.globals.CardFarming.badge_set.items()])

                for i in range(40):
                    if not dry_run and ui.globals.FakeApp.process.poll():
                        stlib.logger.console_fixer()
                        ui.globals.logger.critical(ui.globals.FakeApp.process.stderr.read().decode('utf-8'))
                        sys.exit(1)

                    try:
                        time.sleep(1)
                    except KeyboardInterrupt:
                        sys.exit(0)

                stlib.logger.console_fixer('\r')
                stlib.logger.console_msg('Checking if game have more cards drops...', end='\r')
                ui.card_farming.update_card_count(index)
                stlib.logger.console_fixer('\r')

                if ui.globals.CardFarming.badge_set['cardCount'][index] < 1:
                    stlib.logger.console_fixer('\r')
                    ui.globals.logger.warning('No more cards to drop.')
                    break

            ui.globals.logger.info('Closing %s', ui.globals.CardFarming.badge_set['gameName'][index])

            if not dry_run:
                ui.libsteam.stop_wrapper()

        ui.globals.logger.warning('There\'s nothing else to do. Leaving.')

    def __fakeapp(self):
        try:
            ui.globals.FakeApp.id = self.parameters.cli[1]
        except IndexError:
            ui.globals.logger.critical("Unable to locate the gameID.")
            ui.globals.logger.critical("Please, check the command line.")
            sys.exit(1)

        if ui.libsteam.is_steam_running():
            ui.globals.logger.info("Preparing. Please wait...")
            ui.libsteam.run_wrapper(ui.globals.FakeApp.id)

            time.sleep(3)
            if ui.globals.FakeApp.process.poll():
                ui.globals.logger.critical("This is not a valid gameID.")
                sys.exit(1)

            try:
                ui.globals.logger.info("Running {}".format(ui.globals.FakeApp.id))
                ui.globals.FakeApp.process.wait()
            except KeyboardInterrupt:
                pass
        else:
            ui.globals.logger.critical("Unable to locate a running instance of steam.")
            ui.globals.logger.critical("Please, start Steam and try again.")
            sys.exit(1)

        sys.exit(0)
