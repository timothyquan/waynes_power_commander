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
from PRTG import PRTGDevice, PRTGServer
import pandas as pd


class WaynesPowerInterface():
    def __init__(self, config):
        print('Hello, Wayne.')
        running = True
        while running == True:
            self.load_config(config)
            self.display_items()
            while True:
                print('\nWould you like to:')
                select = input(
                    'Power something on (1), power something off (2), exit (x)?: ').lower()
                if select == '1' or select == '2':
                    if self.power_toggle(select == '1'):
                        break
                elif select == 'x':
                    running = False
                    break
        print('Goodbye, Wayne.')

    def get_status(self, item):
        '''Returns the status of either a PRTGDevice or PDU outlet
        This is to facilitate the use of the dataframe.applymap method'''
        return item.get_status()

    def load_config(self, config):
        '''Parses the configuration yaml, loads the device dataframe'''
        server_dict = {}
        self.device_df = pd.DataFrame()
        print('Loading configuration and checking status....')
        for server in config['prtg_servers']:
            server_dict[server] = PRTGServer(
                config['prtg_servers'][server]['host'],
                config['prtg_servers'][server]['url'],
                config['prtg_servers'][server]['username'],
                config['prtg_servers'][server]['pass']
            )

        for device in config['devices']:
            device_dict = {'device': device}
            for item in config['devices'][device]:
                device_dict[item] = PRTGDevice(
                    server_dict[config['devices'][device][item]['server']],
                    config['devices'][device][item]['objid'],
                    item
                )
            self.device_df = self.device_df.append(
                device_dict, ignore_index=True)

    def display_items(self):
        print('Here are the items: \n')
        status_df = self.device_df.iloc[:, 1:].applymap(self.get_status)
        print(pd.concat([self.device_df.iloc[:, 0:1],
                         status_df], axis=1, sort=False))

    def power_on(self, item):
        '''Accepts either a PRTG device or PDU outlet and powers it on
        This is to facilitate the use of the dataframe.applymap method'''
        item.start() 

    def power_off(self, item):
        '''Accepts either a PRTG device or PDU outlet and powers it off
        This is to facilitate the use of the dataframe.applymap method'''
        item.pause() 

    def power_toggle(self, power_on):
        onoff = {True: 'on', False: 'off'}
        ran = False
        print(f'\nOk Wayne, lets turn some equipment {onoff[power_on]}.')
        select = input(
            'From the list above you can enter the index number of a piece of equipment (#), multiple indices seperated by commas (#,#,#), all listed items (a): ').lower()
        select_idxs = []
        try:
            self.device_df.iloc[int(select), :]
            select_idxs.append(int(select))
            ran = True
        except (KeyError, ValueError,IndexError):
            if select == 'a':
                select_idxs = list(range(0, len(self.device_df)))
            elif ',' in select:
                try:
                    for idx in select.split(','):
                        self.device_df.iloc[int(select):int(select)]
                        select_idxs.append(idx)                    
                except (KeyError, ValueError,IndexError):
                    pass
        if len(select_idxs) > 0:
            if power_on:                
                self.device_df.iloc[select_idxs, 1:].applymap(self.power_on)
            else:
                self.device_df.iloc[select_idxs, 1:].applymap(self.power_off)
            return ran

if __name__ == "__main__":
    with open(r'settings.yaml') as file:
        config = yaml.full_load(file)

    logging.basicConfig(filename=config['logFile'],
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')

    WaynesPowerInterface(config)
