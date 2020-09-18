# Wayne's Power Commander

waynes_power_commander is a cli application to allow Wayne to visualize APC PDU outlet and PRTG sensor groupings/pairings, their status, and finally allow him to turn them on and off.

## Usage

Run it from terminal, or create an executable with pyinstaller.

![interface flow](https://github.com/timothyquan/waynes_power_commander/blob/master/interface_flow.png?raw=true)

## Requirements

This has been tested with APC PDU models AP8959NA3, AP8959. OIDs from APC powernet432.mib, https://www.apc.com/shop/mk/en/products/PowerNet-MIB-v4-3-3/P-SFPMIB433,(iso.org.dod.internet.private.enterprises.apc.products.hardware.rPDU) 

apc_snmp uses pysnmp:

'''
pip install pysnmp
'''

Uses pandas:

'''
pip install pandas
'''

Uses tabulate to format output:

'''
pip install tabulate
'''

Uses tqdm for progress bars:

'''
pip install tqdm
'''



## License

[MIT](https://choosealicense.com/licenses/mit/)