__author__ = "Tim Quan"
__copyright__ = "Copyright 2020"
__license__ = "MIT"
__version__ = "1.0"
__maintainer__ = "Tim Quan"
__status__ = "Prototype"

import yaml
from pprint import pprint
import logging
from time import sleep
import threading


class WaynesPowerInterface():
    def __init__(self, config):
        print('Hello, Wayne.')
        running = True
        while running == True:
            print('Here are the current loaded objects and their status: ')
            self.load_config(config)
            self.display_items()
            while True:
                print('Would you like to.....')
                select = input(
                    'Power something on (1), power something off (2), exit (x)?: ').lower()
                if select == '1' or select == '2':
                    if self.power_toggle(select == '1'):
                        break
                elif select == 'x':
                    running = False
                    break
        print('Goodbye, Wayne.')

    def load_config(self, config):
        print('Loading configuration and checking status....')


    def display_items(self):
        print('Here are the items: ')

    def power_toggle(self, power_on):
        onoff = {True: 'on', False: 'off'}
        ran = False        
        print(f'\nOk Wayne, lets turn some equipment {onoff[power_on]}.')
        select = input(
            'From the list above you can enter the index number of a piece of equipment (#), multiple indices seperated by commas (#,#,#), all listed items (a): ').lower()
        try:             
            print(f'Ok, that is a single integer, {int(select)}.')
            ran = True
        except ValueError: 
            if select == 'a':
                if 'y' == input(f'Are you sure you would like to turn ALL items {onoff[power_on]}? (y) to continue: '):
                    print(f'Ok, turning all items {onoff[power_on]}')
                ran = True
            elif ',' in select:
                print('Very good, that is multiple items: ', select.split(','))
                ran = True        
        return ran


if __name__ == "__main__":
    with open(r'settings.yaml') as file:
        config = yaml.full_load(file)

    logging.basicConfig(filename=config['logFile'],
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')

    WaynesPowerInterface(config)
