# coding=utf-8
import terminal
from loadData import *
from objectsISA import *

#Słownik służący do uzgodnienia położenia zwrotnic na mapie z rzeczywistym ich ułożeniem.
mapSwitchRightDict = {
    1 : False,
    2 : False,
    3 : True,
    4 : False,
    5 : True,
    6 : True,
    7 : False,
    8 : True,
    9 : False,
    10 : False,
    11 : False,
    12 : False,
    13 : False,
    14 : True,
    15 : True,
    16 : True,
    17 : False,
    18 : True,
    19 : True,
    20 : False,
    21 : False,
    22 : False,
    23 : True,
    24 : False,
    25 : False,
    26 : False,
    27 : False,
    28 : False,
    29 : False,
    30 : False,
    31 : True,
    32 : False,
    33 : True,
    0 : True
}

class BusControl:
    """
    Klasa odpowiedzialna za wykonywanie operacji na zwrotnicach i balisach - dokonuje inicjalizacji ich pracy.
    :param myParent: przechowuje wskaźnik do obiektu klasy PKMwindow, głównej klasy w programie.
    """
    def __init__(self,myParent):

        self.dataLoaded = dataLoader()
        self.dataLoaded.load()
        self.balisesLst = self.dataLoaded.balisesLst
        self.switchersLst = self.dataLoaded.switchersLst
        self.myParent = myParent
        try:
            self.terminale = terminal.CommunicationModule('COM6', 500000, 'N')
            print("Terminal configured")
        except:
            self.terminale = None
            print("No terminal")

        if self.terminale:
            self.terminale.start()
            print "! Initializing balises and switchers !"
            for bal in self.balisesLst:
                self.terminale.writeCommand(bal.setINT0(1))
                print "Set int0 for balisa: ",bal.deviceNo,bal.zone
            for swi in self.switchersLst:
                if swi.deviceNo == 104 and swi.zone == u'Wrzeszcz':
                    self.terminale.writeCommand(swi.switchLeft())
                else:
                    self.terminale.writeCommand(swi.switchRight())
                sleep(0.1)
                print "Set right switcher: ",swi.deviceNo,swi.zone
                self.terminale.writeCommand(swi.powerOff())

            self.scanAllBalises()

    #Słownik służący do powiązania numerów zwrotnic z PKMMap z polami deviceNo i zone klasy Switcher.
    mapNumToDevNoAndZoneDict = {
        1 : (507,u'Banino'),
        2 : (313,u'Banino'),
        3 : (312,u'Banino'),
        4 : (102,u'Strzyża'),
        5 : (101,u'Strzyża'),
        6 : (11,u'Kiełpinek'),
        7 : (2,u'Kiełpinek'),
        8 : (1,u'Kiełpinek'),
        9 : (12,u'Kiełpinek'),
        10 : (310,u'Wrzeszcz'),
        11 : (311,u'Wrzeszcz'),
        12 : (111,u'Wrzeszcz'),
        13 : (110,u'Wrzeszcz'),
        14 : (109,u'Wrzeszcz'),
        15 : (108,u'Wrzeszcz'),
        16 : (307,u'Wrzeszcz'),
        17 : (308,u'Wrzeszcz'),
        18 : (309,u'Wrzeszcz'),
        19 : (506,u'Wrzeszcz'),
        20 : (105,u'Wrzeszcz'),
        21 : (107,u'Wrzeszcz'),
        22 : (306,u'Wrzeszcz'),
        23 : (305,u'Wrzeszcz'),
        24 : (304,u'Wrzeszcz'),
        25 : (505,u'Wrzeszcz'),
        26 : (504,u'Wrzeszcz'),
        27 : (501,u'Wrzeszcz'),
        28 : (503,u'Wrzeszcz'),
        29 : (303,u'Wrzeszcz'),
        30 : (302,u'Wrzeszcz'),
        31 : (103,u'Wrzeszcz'),
        32 : (102,u'Wrzeszcz'),
        33 : (101,u'Wrzeszcz'),
        0 : (301,u'Wrzeszcz')
    }
    #Słownik odwrotny, sprzężony z powyższym
    invMapNumToDevNoAndZoneDict = {v: k for k, v in mapNumToDevNoAndZoneDict.items()}

    def changeSwitcher(self,switch):
        """
        Metoda odpowiedzialna za przestawienie zwrotnicy.
        :param switch: obiekt klasy Switcher, który ma zostać przestawiony
        :return: None
        """
        for el in self.switchersLst:
            if switch.compare(el):
                if self.terminale:
                    self.terminale.writeCommand(el.switch())
                    sleep(0.1)
                    self.terminale.writeCommand(el.powerOff())
                break

    def changeSwitcherByMap(self,number):
        """
        Metoda odpowiedzialna za przestawienie zwrotnicy na podstawie numeru zwrotnicy z mapy.
        :param number: int, numer zwrotnicy na mapie
        :return: None
        """
        s = Switcher()
        (s.deviceNo, s.zone) = self.mapNumToDevNoAndZoneDict[number]
        for el in self.switchersLst:
            if s.compare(el):
                self.myParent.updateSwitcherTable(el)
                if self.terminale:
                    self.terminale.writeCommand(el.switch())
                    sleep(0.1)
                    self.terminale.writeCommand(el.powerOff())
                break

    def scanAllBalises(self):
        """
        Metoda skanująca stan wszystkich balis i uaktualniająca go w polu balisesLst
        :return: None
        """
        if self.terminale:
            (sLst, wLst, bLst) = self.terminale.scanElements()
            for bal in bLst:
                for BALISE in self.balisesLst:
                    if bal.compare(BALISE):
                        BALISE.state = bal.state
                        break
        else:
            print('No terminal')