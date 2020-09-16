__author__ = "Tim Quan"
__copyright__ = "Copyright 2020"
__license__ = "MIT"
__version__ = "1.0"
__maintainer__ = "Tim Quan"
__status__ = "Production"

import logging
from pysnmp.entity.rfc3413.oneliner import cmdgen
from pysnmp.proto import rfc1902

class pdu:
    def __init__(self, name, host, community):
        
        self.host = host
        self.community = community
        self.name = name

    def turn_on_outlet(self, outlet):
        errorIndication, errorStatus, errorIndex, varBinds = cmdgen.CommandGenerator().setCmd(
            cmdgen.CommunityData(self.community),
            cmdgen.UdpTransportTarget((self.host, 161)),
            ((1,3,6,1,4,1,318,1,1,12,3,3,1,1,4,outlet), rfc1902.Integer(1))
            )
        if errorIndication is not None:
            logging.error(f'Failed to set ON on {self.name}, outlet {outlet}:')
            logging.error(errorIndication)
        
    def turn_off_outlet(self, outlet):
        errorIndication, errorStatus, errorIndex, varBinds = cmdgen.CommandGenerator().setCmd(
            cmdgen.CommunityData(self.community),
            cmdgen.UdpTransportTarget((self.host, 161)),
            ((1,3,6,1,4,1,318,1,1,12,3,3,1,1,4,outlet), rfc1902.Integer(2))
            )

        if errorIndication is not None:
            logging.error(f'Failed to set OFF on {self.name}, outlet {outlet}:')
            logging.error(errorIndication)
          
    def get_outlet_status(self, outlet):
        errorIndication, errorStatus, errorIndex, varBinds = cmdgen.CommandGenerator().getCmd(
            cmdgen.CommunityData(self.community),
            cmdgen.UdpTransportTarget((self.host, 161)),
            (1,3,6,1,4,1,318,1,1,12,3,5,1,1,4,outlet))
        if errorIndication is not None:
            logging.error(f'Failed status lookup on {self.name}, outlet {outlet}:')
            logging.error(errorIndication)
        
        val = 0
        for oid,v in varBinds:
            val = int(v)            
        return  ['Unknown', 'On', 'Off'][val]

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
   

if __name__ == "__main__":
    pass