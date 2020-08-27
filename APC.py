__author__ = "Tim Quan"
__copyright__ = "Copyright 2020"
__license__ = "MIT"
__version__ = "1.0"
__maintainer__ = "Tim Quan"
__status__ = "Prototype"

import wexpect
from wexpect import TIMEOUT, EOF
import logging



class pdu:
    def __init__(self, name, host, user, passw):
        self.host = host
        self.user = user
        self.passw = passw
        self.name = name
        self.__authenticate()

    def __authenticate(self):
        logging.info(f'Authenticating with {self.name}...')
        try: 
            self.session = wexpect.spawn('telnet', [self.host],timeout=10)
            self.session.logfile = open("C:/temp/apc.log", "w")
            self.session.expect('User Name : ')        
            self.session.sendline(self.user)
            self.session.expect('Password  : ')
            self.session.sendline(self.passw)   
        except TIMEOUT:
            logging.error(f'Timeout error looking for "Password  : " prompt on {self.name}')
        except EOF:
            logging.error(f'EOF exception on connection attempt to {self.name}; is it configured properly? Trying again...')
        return self.session
    
    def start_comms(self, rec = 0):
        '''Checks if a session is still alive and in a state ready to accept new commands.
        Prevents having to wait to reauthenticate every time a command is sent.'''
        if self.session.isalive():
           try: 
               self.session.expect('apc>')
               return True
           except TIMEOUT:
               rec += 1
               logging.error(f'Timeout error looking for "apc>" prompt on {self.name}.')
               logging.error(f'Failure count {rec}')
               self.session.sendline('close')
               self.session.terminate()               
               if rec < 5:                   
                   return self.start_comms(rec=rec)
        else: 
            rec += 1
            if rec < 5: 
                self.__authenticate()
                return self.start_comms(rec=rec)
        
    def turn_on_outlet(self, outlet):
        cmd = f'olOn {outlet}'
        if self.start_comms() == True:            
            success_str = 'E000: Success'
            self.session.sendline(cmd)
            try: 
                self.session.expect(success_str)
                logging.info(f'"{cmd}" executed against "{self.name}" successfully.')
                return True
            except TIMEOUT: 
                logging.error(f'"{cmd}" sent to "{self.name}", but timeout waiting for response "{success_str}"')
        else:
            logging.error(f'Unable to start communications with {self.name}. Did not attempt to execute {cmd}')

    def turn_off_outlet(self, outlet):
        cmd = f'olOff {outlet}'
        if self.start_comms() == True:
            
            success_str = 'E000: Success'
            self.session.sendline(cmd)
            try: 
                self.session.expect(success_str)
                logging.info(f'"{cmd}" executed against "{self.name}" successfully.')
                return True
            except TIMEOUT: 
                logging.error(f'"{cmd}" sent to "{self.name}", but timeout waiting for response "{success_str}"')
                logging.info(self.session.before, self.session.after)
        else:
            logging.error(f'Unable to start communications with {self.name}. Did not attempt to execute {cmd}')
    
    def get_outlet_status(self, outlet):
        cmd = f'olStatus {outlet}'
        status_str = 'undetected'
        if self.start_comms() == True:            
            success_str = 'E000: Success'
            self.session.sendline(cmd)
            try: 
                self.session.expect(success_str)
                status_str = self.session.before[
                    self.session.before.find(f'{outlet}:') + 3:]
                status_str = status_str[status_str.find(': ') + 2:]
                status_str = status_str[:10].strip(' ')
            except TIMEOUT: 
                logging.error(f'"{cmd}" sent to "{self.name}", but timeout waiting for response "{success_str}"')
        else:
            logging.error(f'Unable to start communications with {self.name}. Did not attempt to execute {cmd}')
        logging.info(f'"{self.name}" returned "{status_str}" from command "{cmd}"')
        return status_str
    
class pdu_outlet:
    def __init__(self, pdu, number):
        self.number = number   
        self.pdu = pdu

    def turn_off(self):
        self.pdu.turn_off_outlet(self.number)

    def turn_on(self):
        self.pdu.turn_on_outlet(self.number)

    def get_status(self):
        return self.pdu.get_outlet_status(self.number)
    



        
    def login(self):
        time.sleep(20)



if __name__ == "__main__":
    pass