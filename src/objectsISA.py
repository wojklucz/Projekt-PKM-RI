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

wigwagComm = {'Turn On 0': '31',
              'Turn On 1': '32',
              'Turn On 2': '33',
              'Turn On 3': '34',
              'Turn On 4': '35',
              'Turn Off': '30',
              'Get state': '39'}
rev = dict([reversed(i) for i in wigwagComm.items()])
wigwagComm.update(rev)

balisaComm = {'Turn Off': '30',
              'Set INT0': '31',
              'Set INT1': '32',
              'Set INT': '33',
              'Change INT': '34',
              'Get state': '39'}
rev = dict([reversed(i) for i in balisaComm.items()])
balisaComm.update(rev)


class PKMObject(object):
    """
    Abstract class for PKM objects
    """

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


class Wigwag(PKMObject):
    """
    Wigwag class
    """

    def __init__(self):
        PKMObject.__init__(self)
        self.type = typeDict['Wigwag']
        self.state = [0, 0, 0, 0, 0]
        self.alarm = [0, 0, 0, 0, 0]
        self.description = 'Wigwag on PKM track'

    def turnOnSingleLed(self, no):
        """
        Turning on single LED
        :param no: number of LED
        :return: list of commands
        """
        c = wigwagComm['Turn On ' + str(no)]
        self.state[no] = 1
        return [self.getHeader() + c + END]

    def turnOffSingleLed(self, no):
        """
        Turning off single LED
        :param no: number of LED
        :return: list of commands
        """
        self.state[no] = 0
        self.alarm[no] = 0
        hexNo = hex(int(''.join([str(i) for i in self.state]), 2))[2:]
        return [self.getHeader() + '0' + hexNo + END]

    def setLed(self, state):
        """
        Turning on/off set of LEDs
        :param state: state of wigwag
        :return: list of commands
        """
        self.state = state
        hexNo = hex(int(''.join([str(i) for i in self.state]), 2))[2:]
        if len(hexNo) == 1:
            return [self.getHeader() + '0' + hexNo + ' 00' + END]
        elif len(hexNo) == 2:
            return [self.getHeader() + hexNo + ' 00' + END]

    def setAlarmsLed(self, state):
        """
        Turning alarm on/off set of LEDs
        :param state: state of wigwag
        :return: list of commands
        """
        self.alarm = state
        hexNo = hex(int(''.join([str(i) for i in self.state]), 2))[2:]
        if len(hexNo) == 1:
            return [self.getHeader() + '0' + hexNo + END,
                    self.getHeader() + '00 ' + '0' + hexNo + END]
        elif len(hexNo) == 2:
            return [self.getHeader() + hexNo + END,
                    self.getHeader() + '00 ' + hexNo + END]

    def turnWigwagOff(self):
        """
        Turning wigwag off
        :return: list of commands
        """
        self.state = [0, 0, 0, 0, 0]
        self.alarm = [0, 0, 0, 0, 0]
        return [self.getHeader() + wigwagComm['Turn Off'] + END]

    def checkState(self, stats):
        """
        Checking state of switcher based on string
        :param stats: state of the switcher
        :return: state of switcher
        """
        tmp = list(bin(int(stats[0:2], 16))[2:])
        self.state = [0] * (5 - len(tmp))
        self.state.extend([int(i) for i in tmp])

        tmp = list(bin(int(stats[3:5], 16))[2:])
        self.alarm = [0] * (5 - len(tmp))
        self.alarm.extend([int(i) for i in tmp])

    def testState(self):
        """
        Testing and checking state of the switcher
        :return: state of switcher
        """
        return [self.getHeader() + wigwagComm['Get state'] + END]


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
        return [self.getHeader() + wigwagComm['Get state'] + END]



trainCommands = {'alertStop': '2180 A1 \r\n',
                 'alertStart': '2181 A0 \r\n',
                 }


class Train(object):
    """
    PKM Train class
    """

    def __init__(self, adr):
        """
        Constructor
        """
        self.velocity = 0
        self.direction = True
        self.description = ''
        self.address = adr
        self.state = False

    def changeSpeed(self, param):
        """
        Changing speed of train by keyboard
        :param param: plus or minus
        :return: command for velocity change
        """
        if self.direction:
            v = self.velocity
        else:
            v = - self.velocity
        if param:
            v += 1
        else:
            v += -1
        if v == 16:
            v = 15
        elif v == -16:
            v = -15
        if v < 0:
            return self.changeVelocity(abs(v), False)
        else:
            return self.changeVelocity(abs(v), True)

    def getSpeed(self):
        """
        Getting velocity fo slider
        :return: velocity in range (-6,+6)
        """
        if self.direction:
            return self.velocity
        else:
            return -self.velocity

    def setState(self, rec):
        """
        Setting state, depending on received massage
        Locomotive information normal locomotive
            P - parity bit
            GA - XpressNet device address
            P+0x60+GA 0xE4 Identification Speed FKTA FKTB X-Or
            Identyfication: 0000 BFFF (B=0 loco_free B=1 loco_another_dev)
                                      (FFF = 000 14 speed step)
                                      (FFF = 001 27 speed step)
                                      (FFF = 010 28 speed step)
                                      (FFF = 100 128 speed step)
            Speed 0DSS SSSS (D=1 forward, D=0 reverse)
            Function Byte A: status of the functions 0 to 4. 0 0 0 F0 F4 F3 F2 F1
            Function Byte B: status of the functions 5 to 12 F12 F11 F10 F9 F8 F7 F6 F5
        Locomotive is being operated by another device response
            P+0x60+GA 0xE3 0x40 Addr_High Addr_Low X-Or
        Locomotive is available for operation
            P+0x60+GA 0x83 Loco_addr Loco_data_1 Loco_data_2 X-Or
        Locomotive is being operated by another device
            P+0x60+GA 0xA3 Loco_addr Loco_data_1 Loco_data_2 X-Or
        Locomotive is available for operation
            P+0x60+GA 0x84 Loco_addr Loco_data_1 Loco_data_2 ModSel X-Or
        Locomotive is being operated by another device
            P+0x60+GA 0xA4 Loco_addr Loco_data_1 Loco_data_2 ModSel X-Or
        :param rec: received massage
        """
        # TODO parsowanie odpowiedzi
        #rec[rec.find('\xE4'):]

        pass

    def checkState(self):
        """
        Generating query
        0xE3 0x00 AddrH AddrL [XOR]	 	Locomotive information request
        :return: query checking state of train
        """
        command = 'E3 00 00 '
        if len(hex(self.address)) == 3:
            command += '0' + hex(self.address)[2] + ' '
        elif len(hex(self.address)) == 4:
            command += '0' + hex(self.address)[2:] + ' '
        xor = 0xE3 ^ 0x00 ^ 0x00 ^ self.address
        command += hex(xor)[2:] + '\r\n'
        return command

    def changeVelocity(self, v, d):
        """
        Creates a command for velocity change
        :param v: speed of train 0-13
        0xE4 0x10 AddrH AddrL Speed [XOR]	 	Locomotive speed and direction operation - 14 speed step
	    0xE4 0x11 AddrH AddrL Speed [XOR]	 	Locomotive speed and direction operation - 27 speed step
	    0xE4 0x12 AddrH AddrL Speed [XOR]	 	Locomotive speed and direction operation - 28 speed step
	    0xE4 0x13 AddrH AddrL Speed [XOR]	 	Locomotive speed and direction operation - 128
	    0x80 0x80	 	Stop all locomotives request (emergency stop)
	    0x91 loco_addr [XOR]	2	Emergency stop a locomotive
	    0x92 AddrH AddrL [XOR]
        :return: command for velocity changing
        testowo :  'E41000038C7B'
        MAC 00:04:A3:7E:86:A7
        """
        self.velocity = v
        self.direction = d
        command = 'E4 10 00 '
        xor = 0xE4 ^ 0x10 ^ 0x00 ^ self.address
        if len(hex(self.address)) == 3:
            command += '0' + hex(self.address)[2] + ' '
        elif len(hex(self.address)) == 4:
            command += '0' + hex(self.address)[2:] + ' '
        if self.direction:
            command += '8' + hex(v)[2:]
            xor ^= 8 * 16 + v
        else:
            command += '0' + hex(v)[2:]
            xor ^= v
        command += ' ' + hex(xor)[2:] + '\r\n'
        return command