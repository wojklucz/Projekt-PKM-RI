# coding=utf-8
__author__ = 'mikhael'
# !/usr/bin/env python
# Based on a very simple serial terminal
# (C)2002-2011 Chris Liechti <cliechti:gmx.net>

import sys
import serial
import threading
from serial.tools.list_ports import comports
from objectsISA import *
from time import sleep
from PyQt4.QtCore import *
import winsound

class CommunicationModule(QObject):
    """
    Class of communication with agents
    :param port: Name of serial port, default = COM3
    :param baudRate: Bound rate, default = 500000 bps
    :param parity: parity: (None, Even, Odd, Space, Mark), default = None
    :param rtscts: RTS/CTS flow control, default = False
    :param xonxoff: Software flow control, default = False
    :param echo: Local echo, , default = False
    :param convert_outgoing: converting encoding of read data, default = 1
    :param repr_mode: debug received data (0: just print what is received;
                    1: escape non-printable characters, do newlines as unusual;
                    2: escape non-printable characters, newlines too;
                    3: hex dump everything), default = 0
    """
    def __init__(self, port, baudRate, parity = serial.PARITY_NONE, rtscts=False, xonxoff=False,
                 echo=False, convert_outgoing=1, repr_mode=0):
        QObject.__init__(self)
        try:
            self.serial = serial.serial_for_url(port, baudRate, parity=parity,
                                                rtscts=rtscts, xonxoff=xonxoff,
                                                timeout=1)
        except AttributeError:
            # happens when the installed pyserial is older than 2.5. use the
            # Serial class directly then.
            self.serial = serial.Serial(port, baudRate, parity=parity,
                                        rtscts=rtscts, xonxoff=xonxoff,
                                        timeout=1)
        self.echo = echo
        self.repr_mode = repr_mode
        self.convert_outgoing = convert_outgoing
        self.newline = (0, 1, 2)[self.convert_outgoing]
        self.dtr_state = True
        self.rts_state = True
        self.break_state = False
        ####################
        self.alive = True
        self.transmitter_thread = None
        self.receiver_thread = None
        self.log = list()
        #self.xlogger = xLogger("logger")
        self.switchersLst = []
        self.wigwagsLst = []
        self.balisesLst = []
        self.sendCommandLog = []


    @staticmethod
    def getPortList():
        """
        Get and list ports
        """
        lst = []
        if comports:
            for port, desc, hwid in sorted(comports()):
                # sys.stderr.write('--- %-20s %s\n' % (port, desc))
                lst.append(port)
        return lst

    def _start_reader(self):
        """
        Start reader thread
        """
        self._reader_alive = True
        # start serial->console thread
        self.receiver_thread = threading.Thread(target=self.reader)
        self.receiver_thread.setDaemon(True)
        self.receiver_thread.start()

    def _stop_reader(self):
        """
        Stop reader thread only, wait for clean exit of thread
        """
        self._reader_alive = False
        self.receiver_thread.join()

    def start(self):
        """
        Starting reading thread, and writing thread
        """
        self._start_reader()
        self.transmitter_thread = threading.Thread(target=self.writer)
        self.transmitter_thread.setDaemon(True)
        self.transmitter_thread.start()

    def stop(self):
        """
        Killing the threads
        """
        self.alive = False

    def join(self, transmit_only=False):
        """
        Wait until the thread terminates. This blocks the calling thread until
        the thread whose join() method is called terminates either normally or
        through an unhandled exception – or until the optional timeout occurs.
        :param transmit_only: both threads?
        """
        self.transmitter_thread.join()
        if not transmit_only:
            self.receiver_thread.join()

    def reader(self):
        """
        Loop and copy serial port to console
        """
        try:
            command = ''
            while self.alive and self._reader_alive:
                #time = datetime.datetime.now() grupa Adrian - czas z balisy
                data = self.serial.read()
                command += data
                if data == '\r':
                    command = command.strip()
                    ##self.xlogger.warning('ISA Read: ' + str(time.hour) + ':' + str(time.minute) + ':' + str(time.second) + ':' + str(time.microsecond) + command) grupa Adrian
                    #self.xlogger.warning('ISA Read: ' + command)
                    if command:
                        self.log.append(command.strip())
                        if command[0] == '>':
                            try:
                                typo = typeDict[command[1:3]]
                                zone = zoneDict[command[3:5]]
                                address = int(command[5:9], 16)

                                if typo == 'Switcher':
                                    for el in self.switchersLst:
                                        if el.zone == zone and el.deviceNo == address:
                                            el.checkState(command[10:])
                                elif typo == 'Wigwag':
                                    for el in self.wigwagsLst:
                                        if el.zone == zone and el.deviceNo == address:
                                            el.checkState(command[10:])
                                elif typo == 'Balisa'  or command[1:3] == '43':#balisa kiełpinek:
                                    for el in self.balisesLst:
                                        if el.zone == zone and el.deviceNo == address:
                                            msg = el.checkState(command[10:])
                                            if el.state['int0']:
                                                winsound.Beep(2500, 100)
                                            else:
                                                winsound.Beep(1000, 100)
                                            # time = datetime.datetime.now() #adrian
                                            # print('time sec',time.second)
                                            # print('mili ',time.microsecond)
                                            # print('zone',el.zone) #grupa Adrian
                                            # print('device number',el.deviceNo) #grupa Adrian
                                            # print()
                                            # print(msg)
                                            self.emit(SIGNAL("balisa_int"), el)
                            except:
                                print command+' dafuq'
                    command = ''
        except serial.SerialException:
            self.alive = False
            raise

    def writer(self):
        """
        Loop and write lines from terminal to serial port
        """
        try:
            while self.alive:
                line = sys.stdin.readline()
                if line.find(EXIT) >= 0:
                    self.stop()
                    self.alive = False
                    break
                else:
                    line = line.replace('\n', '\r')
                    self.serial.write(line)
                    #self.xlogger.info(line)
        except:
            #self.xlogger.error('Exception')
            self.alive = False
            raise

    def writeCommand(self, command):
        """
        Writing command to serial port
        :param command: command to write
        """
        try:
            if not self.sendCommandLog:
                for c in command:
                    self.serial.write(c)
                    # #self.xlogger.warning('ISA Send: ' + c)
                    self.sendCommandLog.append(command)
                    sleep(0.2)
            elif not command == self.sendCommandLog[-1]:
                for c in command:
                    self.serial.write(c)
                    # #self.xlogger.warning('ISA Send: ' + c)
                    self.sendCommandLog.append(command)
                    sleep(0.2)

        except:
            #self.xlogger.error('Exception in writing command')
            self.alive = False
            raise

    def turnAgentsOff(self):
        """
        Turning all agents off, especially switchers
        """
        self.writeCommand(['>1F000000 30\r'])

    def saveAgentsStates(self):
        """
        Saving all agents states to their memory
        """
        self.writeCommand(['>1F000000 73\r'])

    def scanElements(self):
        """
        Scanning whole network and reading elements
        """
        self.log = []
        self.writeCommand(['>1F000000 39\r'])
        sleep(1)
        self.log = list(set(self.log))
        self.log.sort()
        for el in self.log:
            if el[0] == '>':
                try:
                    typo = typeDict[el[1:3]]
                    zone = zoneDict[el[3:5]]
                    address = int(el[5:9], 16)
                    if typo == 'Switcher':
                        sw = Switcher()
                        sw.zone = zone
                        sw.deviceNo = address
                        sw.checkState(el[el.find(' ')+1:])
                        self.switchersLst.append(sw)
                    elif typo == 'Balisa' or '43' in el[1:3]:
                        ba = Balisa()
                        ba.zone = zone
                        ba.deviceNo = address
                        #ba.checkState(el[el.find(' ')+1:])
                        self.balisesLst.append(ba)
                except Exception:
                    print 'dupa'
                    #self.xlogger.error('Element ' + el[1:] + 'found, but address is incorrect.')
        self.log = []
        return self.switchersLst, self.wigwagsLst, self.balisesLst