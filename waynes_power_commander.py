__author__ = "Tim Quan"
__copyright__ = "Copyright 2020"
__license__ = "MIT"
__version__ = "1.0"
__maintainer__ = "Tim Quan"
__status__ = "Production"

import yaml
import logging
from logging import handlers
logger = logging.getLogger(__name__)
from PRTG import PRTGDevice, PRTGServer
from apc_snmp import pdu, pdu_outlet
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import pandas as pd
from tabulate import tabulate
from tqdm import tqdm 
import sys


class WaynesPowerInterface():
    def __init__(self, config):        
        print('Hello, Wayne.')
        running = True
        while running == True:
            self.load_config(config)            
            while True:
                self.display_items()
                print('\nWould you like to:')
                select = input(
                    'Power something on (1), power something off (2), exit (x), or refresh (enter)?: ').lower()
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
        if type(item) is PRTGDevice:
            return item.get_status()
        elif type(item) is pdu_outlet:
            return item.get_status()
                    
    def load_config(self, config):
        '''Parses the configuration yaml, loads the device dataframe'''
        server_dict = {}
        self.device_df = pd.DataFrame()
        print('Reading configuration...')
        for server in tqdm(config['prtg_servers'], desc='Loading PRTG Servers'):
            server_dict[server] = PRTGServer(
                config['prtg_servers'][server]['host'],
                config['prtg_servers'][server]['url'],
                config['prtg_servers'][server]['username'],
                config['prtg_servers'][server]['pass']
            )
        for server in tqdm(config['pdus'], desc='Loading PDUs'):
            server_dict[server] = pdu(
                server,
                config['pdus'][server]['host'],
                config['pdus'][server]['community'],
            )

        for device in tqdm(config['devices'], desc='Loading Devices'):
            device_dict = {'device': device}
            for item in config['devices'][device]:
                server = server_dict[config['devices'][device][item]['server']]                                
                if type(server) is PRTGServer:
                    device_dict[item] = PRTGDevice(
                        server,
                        config['devices'][device][item]['objid'],
                        item)
                elif type(server) is pdu:
                    device_dict[item] = pdu_outlet(
                        server,
                        config['devices'][device][item]['objid'])

            self.device_df = self.device_df.append(
                device_dict, ignore_index=True)
        self.device_df = self.device_df.reindex(sorted(self.device_df), axis=1)                            
    def display_items(self): 
        tqdm.pandas(desc='Checking status')
        status_df = self.device_df.iloc[:, 1:].progress_applymap(self.get_status)
        tabulated = tabulate(pd.concat([self.device_df.iloc[:, 0:1],
                         status_df], axis=1, sort=False),
                         headers='keys', tablefmt='pretty')                         
        print('\nHere are the devices: \n')
        print(tabulated)                                          

    def power_on(self, item):
        '''Accepts either a PRTG device or PDU outlet and powers it on
        This is to facilitate the use of the dataframe.applymap method'''
        if type(item) is PRTGDevice:
            item.start() 
        elif type(item) is pdu_outlet:
            item.turn_on()

    def power_off(self, item):
        '''Accepts either a PRTG device or PDU outlet and powers it off
        This is to facilitate the use of the dataframe.applymap method'''
        if type(item) is PRTGDevice:
            item.pause() 
        elif type(item) is pdu_outlet:
            item.turn_off()

    def power_toggle(self, power_on):
        onoff = {True: 'on', False: 'off'}
        ran = False
        print(f'\nOk Wayne, lets turn some equipment {onoff[power_on]}.')
        select = input(
            'From the list above you can enter the index number of a piece of equipment (#), multiple indices seperated by commas (#,#,#), all listed devices (a): ').lower()
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
                        self.device_df.iloc[int(idx):int(idx)]
                        select_idxs.append(int(idx))   
                except (KeyError, ValueError,IndexError):
                    pass
        if len(select_idxs) > 0:
            tqdm.pandas(desc=f'Powering {onoff[power_on]}')     
            if power_on:                
                self.device_df.iloc[select_idxs, 1:].progress_applymap(self.power_on)
            else:
                self.device_df.iloc[select_idxs, 1:].progress_applymap(self.power_off)
            return ran

def setup_logging(logger_name, log_path,  log_level):
    '''Accepts a logger_name, path, and logging level
    ('debug', 'info', 'warn', 'error', 'critical')'''

    log_levels = { 'debug' : logging.DEBUG,
        'info' : logging.INFO,
        'warn' : logging.WARN,
        'error' : logging.ERROR,
        'critical' : logging.CRITICAL
    }

    logger = logging.getLogger(logger_name)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    logging.basicConfig(level=log_levels[log_level],
        format="%(asctime)s [%(levelname)s] %(message)s")

    log_file_handler = handlers.RotatingFileHandler(log_path, maxBytes=1048576, backupCount=5)
    log_file_handler.setFormatter(formatter)
    log_file_handler.setLevel(log_levels[log_level])

    log_console_handler = logging.StreamHandler(sys.stdout)
    log_console_handler.setFormatter(formatter)
    log_console_handler.setLevel(log_levels[log_level])

    logger.addHandler(log_file_handler)
    logger.addHandler(log_console_handler)
    logger.setLevel(log_levels[log_level])


    return logger

if __name__ == "__main__":
    with open(r'settings.yaml') as file:
        config = yaml.full_load(file)
        
    logger = setup_logging(__name__, 
        config['logFile'], 
        config['debugLevel'])

    WaynesPowerInterface(config)
