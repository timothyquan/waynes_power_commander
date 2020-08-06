'''PRTG 
This library provides functionality to read from and manipulate PRTG servers, devices and sensors
'''

__author__ = "Tim Quan"
__copyright__ = "Copyright 2020"
__license__ = "MIT"
__version__ = "1.0.1"
__maintainer__ = "Tim Quan"
__status__ = "Production"

import requests
import xmltodict
import json
import datetime
from operator import itemgetter
import logging
import time


class PRTGServer:
    def __init__(self, host_add, url, user_name, user_passhash):
        self.host_add = host_add
        self.url = url
        self.user_name = user_name
        self. user_passhash = str(user_passhash)
        self.devices = {}

    #https://PRTGSERVER/api/table.json?content=devices&output=json&columns=tags,objid,probe,device,host&count=1000&username=admin&passhash=123456789&id=1234
    def populate_devices(self, group_id='0', tag_str=''):
        '''Populates the PRTGServer.devices property with a dictionary of dictionaries containing the devices. 
        Key is the object IDs of the devices.
        groupID is an optional parameter, when provided it will only populate by that group ID
        tagStr is an optional parameter, when provided this method will filter objects by PRTG tags.'''
        url = self.url + '/api/table.json?content=devices&output=json&count=1000&columns=tags,objid,probe,device,host'
        url += ('&username=' + self.user_name)
        url += ('&passhash=' + self.user_passhash)
        url += ('&id=' + str(group_id))

        prtg_resp = response_getter(url)
        prtg_dict = json.loads(prtg_resp.text)

        self.devices = {}
        # iterate through the devices in the dictionary
        for device in prtg_dict['devices']:
            if tag_str != '':
                if tag_str in device['tags']:  # add only devices with matching tags
                    self.devices[device['objid_raw']] = PRTGDevice(
                        self, device['objid_raw'], device['device'])
            else:  # there is no tag filter, add all devices to self.devices
                self.devices[device['objid_raw']] = PRTGDevice(
                    self, device['objid_raw'], device['device'])
        return self.devices


class PRTGObject:
    def __init__(self, server, objid, name):
        self.server = server
        self.objid = objid
        self.name = name

    def start(self):

        url = '{}/api/pause.htm?id={}&action=1&username={}&passhash={}'\
            .format(self.server.url,\
            str(self.objid),\
            self.server.user_name,\
            self.server.user_passhash)
        response_getter(url)

    def pause(self, msg=''):
        url = '{}/api/pause.htm?id={}&pausemsg={}&&action=0&username={}&passhash={}'.format(self.server.url,\
            str(self.objid),\
            msg,\
            self.server.user_name,\
            self.server.user_passhash)
        response_getter(url)

    # /api/getobjectstatus.htm?id=objectid&name=status&show=text
    def get_status(self):
        url = self.server.url + '/api/getobjectstatus.htm?name=status&show=json'
        url += ('&id=' + str(self.objid))
        url += ('&username=' + self.server.user_name)
        url += ('&passhash=' + self.server.user_passhash)
        prtg_resp = response_getter(url)
        prtg_dict = xmltodict.parse(prtg_resp.text)
        # remove superfluous text in brackets
        if str(prtg_dict['prtg']['result']).find('(') > -1:
            idxStart = str(prtg_dict['prtg']['result']).find('(')
            statusStr = str(prtg_dict['prtg']['result'])[0:idxStart]
        else:
            statusStr = prtg_dict['prtg']['result']
        return (statusStr)

    # /api/getobjectproperty.htm?id=objectid&name=tags&show=nohtmlencode
    def get_tags(self, search_val=''):
        '''Returns the tags from a PRTG object in a list, or the the optional search_val returns just a single string
        If the optional 'search_val' parameter is provided, it will only provide the value. 
        eg. if the tags string returns "'json', 'password:password', 'pearlchannel:2', 'python', 'pythonxml', 'script', 'username:user', 'xml'"
        a search_val of 'username:' will return the string value 'user'''
        url = self.server.url + '/api/getobjectproperty.htm?id=' + \
            str(self.objid) + '&name=tags&show=nohtmlencode&username=' + \
            self.server.user_name + '&passhash=' + self.server.user_passhash
        prtg_resp = response_getter(url)
        resp_dict = xmltodict.parse(prtg_resp.text)
        # get just the tags out of the dictionary to return it as a list
        tag_list = resp_dict['prtg']['result'].split(' ')
        if search_val != '':  # check if we are searching for a specific value, if so return just the value in a string
            for tag in tag_list:
                if str(search_val) in str(tag):
                    # find the position of the end of the search_val in the tag string
                    marker_end_index = tag.find(
                        search_val) + len(str(search_val))
                    # return just everything after the search_val in the tag string
                    return tag[marker_end_index:len(tag)]
        return tag_list


class PRTGDevice(PRTGObject):
    def __init__(self, server, objid, name):
        super().__init__(server, objid, name)
        self.sensors = {}
        self.ip_address = self.get_ip()

    # https://server/api/table.json?content=sensors&output=json&count=1000&columns=tags,objid,probe,device,host&username=admin&passhash=1234&id=1234
    def populateSensors(self, tagStr=''):
        '''Populates the PRTGDevice.sensors property with a dictionary of dictionaries containing the sensors. 
        Primary index is the object IDs of the sensors.
        tagStr is an optional parameter, when provided this method will filter sensors by PRTG tags.'''

        url = self.server.url + \
            '/api/table.json?content=sensors&output=json&count=1000&columns=tags,objid,probe,sensor,host'
        url += ('&username=' + self.server.user_name)
        url += ('&passhash=' + self.server.user_passhash)
        url += ('&id=' + str(self.objid))
        prtg_resp = response_getter(url)
        prtg_dict = json.loads(prtg_resp.text)

        self.sensors = {}
        for sensor in prtg_dict['sensors']:
            if '' != tagStr and tagStr in sensor['tags']:
                self.sensors[sensor['objid']] = PRTGSensor(
                    self, sensor['objid'], sensor['sensor'])
            else:
                self.sensors[sensor['objid']] = PRTGSensor(
                    self, sensor['objid'], sensor['sensor'])
        return self.sensors

    # /api/getobjectstatus.htm?id=objectid&name=columnname
    def get_ip(self):
        '''Populates the PRTGDevice.ip_address property and returns the same as a string.'''
        url = self.server.url + '/api/getobjectstatus.htm?name=host'
        url += ('&username=' + self.server.user_name)
        url += ('&passhash=' + self.server.user_passhash)
        url += ('&id=' + str(self.objid))
        prtg_resp = response_getter(url)
        prtg_dict = xmltodict.parse(prtg_resp.text)
        try:
            self.ip_address = prtg_dict['prtg']['result']
            return prtg_dict['prtg']['result']
        except:
            logging.error('The response with ' + url +
                          ' may have contained a host.')
        return prtg_dict


class PRTGSensor(PRTGObject):
    def __init__(self, device, objid, name):
        super().__init__(device.server, objid, name)
        self.device = device

    # /api/historicdata.xml?id=6175&avg=0&columns&sdate=2019-12-21-07-19-10&edate=2019-12-21-08-59-10
    def getSingleChanValues(self, chanKey, startTime='none', endTime='none'):
        '''Takes a list of PRTG sensor values from a single channel and optional start/stop times - these should be datetime.datetime objects. 
        Returns a list of dicts containing the channel results. 
        If no start/end times are provided, returns only last good channel reading within 30 minutes prior to runtime.'''

        # start date/time - the datetime parsed into the form that can be used with the PRTG API call
        sDateStr = '&sdate=' + \
            str(startTime).replace(' ', '-').replace(':', '-')[:19]
        # end date/time - the datetime parsed into the form that can be used with the PRTG API call
        eDateStr = '&edate=' + \
            str(endTime).replace(' ', '-').replace(':', '-')[:19]

        # if theres start/stop time was not provided or was not a datetime object, the search only from (now-30minutes) to (now)
        if (not isinstance(startTime, datetime.datetime)) and (not isinstance(endTime, datetime.datetime)):
            sDateStr = '&sdate=' + str(datetime.datetime.now() + datetime.timedelta(
                minutes=-30)).replace(' ', '-').replace(':', '-')[:19]
            eDateStr = '&edate=' + \
                str(datetime.datetime.now()).replace(
                    ' ', '-').replace(':', '-')[:19]

        url = self.server.url + '/api/historicdata.xml?id=' + \
            self.objid + '&username=' + \
            self.server.userName + '&passhash=' + self.server.user_passhash + \
            '&avg=0&columns=datetime,value_,coverage&id=' + self.objid
        url += ''
        url += sDateStr
        url += eDateStr

        # make the request, then parse it to nested dictionaries
        prtg_resp = response_getter(url)
        prtg_dict = xmltodict.parse(prtg_resp.text)
        # iterate through the dictionary, find readings, match them to the chanKeys and where they match add them to a dictionary then to a list
        resList = []
        # if the total count of readings is > 1, the response will be in the form of a list of dictionaries. Otherwise, it will be a single dictionary.
        if int(prtg_dict['histdata']['@totalcount']) > 1:
            for item in prtg_dict['histdata']['item']:
                curReading = {}  # this will be the timestamp of the reading, then the values in a dictionary
                curReading['datetime'] = item['datetime']
                for value in item['value']:
                    # the @channel key is the 'name' value of the channel, #text is the actual value of the channel reading as a string
                    if str(value['@channel']).lower() in chanKey:
                        if '#text' in value.keys():  # sometimes there is no value if, eg if the sensor was down
                            curReading[str(value['@channel']).lower()
                                       ] = value['#text']
                # don't add readings if the sensor was down. maybe change this functionality in the future.
                if len(curReading) > 1:
                    resList.append(curReading)
        # is it a single reading? if so, it is a dictionary
        elif int(prtg_dict['histdata']['@totalcount']) < 1:
            for key, value in prtg_dict['histdata']['item']:
                curReading = {}  # this will be the timestamp of the reading, then the values in a dictionary
                curReading['datetime'] = item['datetime']
                if '#text' in value.keys():
                    curReading[str(value['@channel']).lower()] = value['#text']
                if len(curReading) > 1:
                    resList.append(curReading)
        try:
            resList = sorted(resList, key=itemgetter('datetime'), reverse=True)
        except:
            pass
        # if start/stop time was not provided or was not a datetime object, parse out only the last good reading
        if (not isinstance(startTime, datetime.datetime)) and (not isinstance(endTime, datetime.datetime)):
            if len(resList) < 1:
                return {}
            else:
                return resList[0]
        else:
            return resList

        #datetime = prtg_dict['histdata']['item']['datetime']


def getSensorByID(device, id):
    '''Required parameters: device (PRTGDevice object), id (the integer value of the sensor you are trying to look up) an object of class PRTGSensor'''
    # /api/getobjectproperty.htm?name=name&show=nohtmlencode
    url = device.server.url + '/api/getobjectproperty.htm?name=name&show=nohtmlencode'
    url += ('&username=' + device.server.user_name)
    url += ('&passhash=' + device.server.user_passhash)
    url += ('&id=' + str(id))
    prtg_resp = response_getter(url)
    prtg_dict = xmltodict.parse(prtg_resp.text)
    device = PRTGSensor(device, id, prtg_dict['prtg']['result'])
    return device


def getDeviceByID(prtgServer, id):
    '''This method returns an object of class PRTGDevice'''
    # /api/getobjectproperty.htm?name=name&show=nohtmlencode
    url = prtgServer.url + '/api/getobjectproperty.htm?name=name&show=nohtmlencode'
    url += ('&username=' + prtgServer.user_name)
    url += ('&passhash=' + prtgServer.user_passhash)
    url += ('&id=' + str(id))
    prtg_resp = response_getter(url)
    prtg_dict = xmltodict.parse(prtg_resp.text)
    device = PRTGDevice(prtgServer, id, prtg_dict['prtg']['result'])
    return device


def response_getter(url, attempt=0):
    '''
    This method uses requests.get in the usual way but with try/except and recursion.
    If requests.get fails the first time, it waits 1 second and tries again for up to 5 attempts.
    '''
    requests.packages.urllib3.disable_warnings()
    requests.get(url, verify=False)
    resp = ''
    try:
        resp = requests.get(url, verify=False)
    except requests.exceptions.ConnectionError:
        time.sleep(1)
        attempt = attempt+1
        if attempt <= 5:
            return response_getter(url, attempt=attempt)
        else:
            logging.error('Failed to get response from ' + url)
    return resp


if __name__ == "__main__":
    pass
