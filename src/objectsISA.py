# -*- coding: utf8 -*-
"""
PKM Objects
"""
from __builtin__ import object

__author__ = 'mikhael'
from time import gmtime, strftime

EXIT = 'Exit'
BEGIN = '>'
END = '\r'

typeDict = {'None': '00',
            'Switcher': '01',
            'Wigwag': '02',
            'Balisa': '03',
            'Multiswitcher': '04'}
rev = dict([reversed(i) for i in typeDict.items()])
typeDict.update(rev)

zoneDict = {u'None': '00',
            u'Strzyża': '01',
            u'Kiełpinek': '02',
            u'Rębiechowo': '03',
            u'Banino': '04',
            u'Wrzeszcz': '05'}
rev = dict([reversed(i) for i in zoneDict.items()])
zoneDict.update(rev)

switcherState = {1: 'Left', 0: 'Unknown', -1: 'Right'}
switcherComm = {'Left': '31',
                'Right': '32',
                'Power Off': '30',
                'Get state': '39'}
rev = dict([reversed(i) for i in switcherComm.items()])
switcherComm.update(rev)

balisaComm = {'Turn Off': '30',
              'Set INT0': '31',
              'Set INT1': '32',
              'Set INT': '33',
              'Change INT': '34',
              'Get state': '39'}
rev = dict([reversed(i) for i in balisaComm.items()])
balisaComm.update(rev)


class PKMObject(object):

    def __init__(self):
        self.zone = zoneDict['None']
        self.type = typeDict['None']
        self.deviceNo = 0  # int
        self.state = None
        self.description = 'PKM object'
        self.mapPosition = (0, 0)

    def __str__(self):
        return str(self.deviceNo) + ' ' + self.description

    def __cmp__(self, other):
        return cmp(int(self.deviceNo) + 10000 * int(self.type),
                   int(other.deviceNo) + 10000 * int(other.type))

    def compare(self, other):
        return self.zone == other.zone and self.deviceNo == other.deviceNo \
               and self.type == other.type

    def getHeader(self):
        """
        Getting header of command
        :return: Header of command '>00115555 '
        """

        s = hex(self.deviceNo)[2:]
        return BEGIN + self.type + zoneDict[self.zone] + ''.join(
            ['0'] * (4 - len(s))) + s + ' '

    def setAddress(self, zone, address):
        """
        Setting address of device
        :param zone: Zone of device
        :param address: Number of device
        :return: list of commands
        """
        command = self.getHeader() + '61 '
        self.zone = zoneDict[zone]
        self.deviceNo = int(address)
        hexAddress = ''.join(['0'] * (4 - len(hex(self.deviceNo)[2:]))) + hex(
            self.deviceNo)[2:]
        addressStr = zone + ' ' + hexAddress[0:2] + ' ' + hexAddress[2:4]
        return [command + addressStr + END]

    def rememberState(self):
        """
        Remembering of current device state
        :return: list of commands
        """
        return [self.getHeader() + '73 ' + END]

    def powerOff(self):
        """
         Turning element off
        """
        return [self.getHeader() + '30 ' + END]

    def getTableData(self):
        """
        Getting data for table
        """
        return [self.zone, self.deviceNo, str(self.state),
                str(self.mapPosition), self.description]


class Switcher(PKMObject):
    """
    Switcher class
    """

    def __init__(self):
        PKMObject.__init__(self)
        self.type = typeDict['Switcher']
        self.state = switcherState[0]
        self.limiter = switcherState[0]
        self.description = 'Switcher on PKM track'
        self.orientation = 0 # Od Wrzeszczaw stronę Strzyży

    def switchLeft(self):
        """
        Switch left
        :return: list of commands
        """
        self.state = switcherState[1]
        return [self.getHeader() + switcherComm['Left'] + END]

            #    self.getHeader() + switcherComm['Power Off'] + END]

    def switchRight(self):
        """
        Switch left
        :return: list of commands
        """
        self.state = switcherState[-1]
        return [self.getHeader() + switcherComm['Right'] + END]
                #self.getHeader() + switcherComm['Power Off'] + END]

    def switch(self):
        """
        Switch to the opposite state
        :return: list of commands
        """
        if self.state == switcherState[1]:
            return self.switchRight()
        else:
            return self.switchLeft()

    def setState(self, state):
        """
        Setting state
        :param state: 'Left', 'None', 'Right'
        :return: command to set desired state
        """
        if state == switcherState[1]:
            return self.switchLeft()
        elif state == switcherState[-1]:
            return self.switchRight()
        else:
            return None

    def checkState(self, stat):
        """
        Checking state of the switcher and writing by string
        :param stat: String of state
        """
        if stat[0:2] == '0F':
            self.state = switcherState[1]
        elif stat[0:2] == '10':
            self.state = switcherState[-1]
        else:
            self.state = switcherState[0]
        if stat[6:8] == '80':
            self.limiter = switcherState[1]
        elif stat[6:8] == '40':
            self.limiter = switcherState[-1]
        else:
            self.state = switcherState[0]

    def getWrittenState(self, stat):
        """
        Checking state of the switcher and writing by string
        :param stat: String of state
        """
        if stat[0:2] == '31':
            self.state = switcherState[1]
        elif stat[0:2] == '32':
            self.state = switcherState[-1]
        else:
            self.state = switcherState[0]

    def testState(self):
        """
        Checking state of switcher
        :return: list of commands
        """
        return [self.getHeader() + switcherComm['Get state'] + END]


class Multiswitcher(Switcher):
    """
    Crossswicther on Kiełpinek
    """

    def __init__(self):
        """
        Constructor
        :param lst: list of switchers
        """
        Switcher.__init__(self)
        self.type = typeDict['Multiswitcher']
        self.swLst = []
        self.state = switcherState[0]
        self.description = 'Multiswitcher on PKM track'

    def switchStraight(self):
        """
        Switch straight
        :return: list of commands
        """
        lst = []
        self.state = switcherState[1]
        for sw in self.swLst:
            if sw.deviceNo == 1:
                lst.extend(sw.switchRight())
                lst.extend(sw.powerOff())
            elif sw.deviceNo == 2:
                lst.extend(sw.switchLeft())
                lst.extend(sw.powerOff())
            elif sw.deviceNo == 11:
                lst.extend(sw.switchRight())
                lst.extend(sw.powerOff())
            elif sw.deviceNo == 12:
                lst.extend(sw.switchLeft())
                lst.extend(sw.powerOff())
        return lst

    def switchCross(self):
        """
        Switching cross
        """
        lst = []
        self.state = switcherState[-1]
        for sw in self.swLst:
            if sw.deviceNo == 1:
                lst.extend(sw.switchLeft())
                lst.extend(sw.powerOff())
            elif sw.deviceNo == 2:
                lst.extend(sw.switchRight())
                lst.extend(sw.powerOff())
            elif sw.deviceNo == 11:
                lst.extend(sw.switchLeft())
                lst.extend(sw.powerOff())
            elif sw.deviceNo == 12:
                lst.extend(sw.switchRight())
                lst.extend(sw.powerOff())
        return lst

    def switch(self):
        if self.state == switcherState[-1]:
            return self.switchStraight()
        else:
            return self.switchCross()


class Balisa(PKMObject):
    """
    Balisa class
    """

    def __init__(self):
        PKMObject.__init__(self)
        self.type = typeDict['Balisa']
        self.int0 = 0
        self.int1 = 0
        self.value = 0
        self.state = {'int0': False, 'int1': False}
        self.logInt0 = []
        self.logInt1 = []
        self.description = 'Balisa on PKM track'

    def setINT0(self, threshold):
        """
        Turn on and set threshold of INT0; Analog input of balisa os from 0
        to 15 Volts; A/C converter has 8 bits.
        :param threshold: float from 0 to 15 Volts
        """
        self.int0 = threshold
        tr = hex(int(255 * threshold / 15))[2:]
        return [self.getHeader() + ' ' + balisaComm['Set INT0'] + ' '
                + ''.join(['0'] * (2 - len(tr))) + tr + END]

    def setINT1(self, threshold):
        """
        Turn on and set threshold of INT1; Analog input of balisa os from 0
        to 15 Volts; A/C converter has 8 bits.
        :param threshold: float from 0 to 15 Volts
        """
        self.int1 = threshold
        tr = hex(int(255 * threshold / 15))[2:]
        return [self.getHeader() + ' ' + balisaComm['Set INT1'] + ' '
                + ''.join(['0'] * (2 - len(tr))) + tr + END]

    def setINT(self, threshold):
        """
        Turn on and set threshold of INT0 and INT1; Analog input of balisa
        os from 0 to 15; Volts; A/C converter has 8 bits.
        :param threshold: float from 0 to 15 Volts
        """
        self.int0 = threshold
        self.int1 = threshold
        tr = hex(int(255 * threshold / 15))[2:]
        return [self.getHeader() + ' ' + balisaComm['Set INT']
                + ' ' + ''.join(['0'] * (2 - len(tr))) + tr + END]

    def changeThreshold(self, threshold):
        """
        Only change both thresholds
        :param threshold: float from 0 to 15 Volts
        """
        self.int0 = threshold
        self.int1 = threshold
        tr = hex(int(255 * threshold / 15))[2:]
        return [self.getHeader() + ' ' + balisaComm['Change INT']
                + ' ' + ''.join(['0'] * (2 - len(tr))) + tr + END]

    def turnOffINT(self):
        """
        Turning both INT off
        """
        self.int0 = None
        self.int1 = None
        return [self.getHeader() + ' ' + balisaComm['Turn Off'] + ' ' + END]

    def setInts(self, state):
        """
        Setting state of balisa
        :param state: (int0, int1)
        :return: command to set
        """
        return self.setINT(state[0]).extend(self.setINT1(state[1]))

    def checkState(self, stats):
        """
        Checking state of balisa based on string
        :param stats: state of the balisa
        :return: state of balisa
        """
        time = strftime("%H:%M:%S:%MS", gmtime())
        bw, bd, bc, ba = stats[0:2], stats[3:5], stats[6:8], stats[9:11]
        stan = bin(int(bc, 16))[2:]
        if len(stan) < 8:
            stan = '0' * (8 - len(stan)) + stan
        if bw == '31':
            self.int0 = int(bd, 16)
            self.logInt0.append((time, bool(int(stan[-8]))))
        if bw == '32':
            self.int1 = int(bd, 16)
            self.logInt1.append((time, bool(int(stan[-7]))))
        if bw == '33':
            self.int0 = int(bd, 16)
            self.int1 = int(bd, 16)
            self.logInt0.append((time, bool(int(stan[-8]))))
            self.logInt1.append((time, bool(int(stan[-7]))))
        self.state = {'int0': bool(int(stan[-8])), 'int1': bool(int(stan[-7]))}
        self.value = (16 * int(ba, 16)) / 255
        return time, self.state

    def testState(self):
        """
        Testing and checking state of the switcher
        :return: state of switcher
        """
        return [self.getHeader() + END]
