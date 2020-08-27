# Wayne's Power Commander

waynes_power_commander is a cli application to allow Wayne to visualize APC PDU outlet and PRTG sensor groupings/pairings, their status, and finally allow him to turn them on and off.

## Usage

Run it from terminal, or create an executable with pyinstaller.

![interface flow](https://github.com/timothyquan/waynes_power_commander/blob/master/interface_flow.png?raw=true)

## Requirements

APC interface uses telnet for broad PDU compatibility; uses wexpect:

'''
pip install wexpect
'''

Uses pandas:

'''
pip install pandas
'''

Uses tabulate to format output:

'''
pip install tabulate
'''

## License

[MIT](https://choosealicense.com/licenses/mit/)