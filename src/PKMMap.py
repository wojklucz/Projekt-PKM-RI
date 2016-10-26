#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt4.QtCore import Qt
import time as t
import math
import ruchomaKropka
from PyQt4 import QtCore
from PyQt4 import QtGui
import busControl

# Przykładowy program z kropka jadaca po linii.
# ID POCIĄGÓW:
# 2 - Wrzeszcz - Banino
# 1 - Kiełpinek - Wrzeszcz
# 0 - Wrzeszcz - Kiełpinek

class Nastawa:
    """
    Klasa nastawy zwrotnicy: ktora zwrotnica, w jaka strone i dla jakiego pociagu
    """
    nr_zwr = 0
    nr_poc = 0
    stan = True
    def __init__(self, zwr, poc, st) :
        self.nr_zwr = zwr
        self.nr_poc = poc
        self.stan = st

class Czujnik:
    """
    klasa czujnika: numer, pozycja (wspolrzedne srodka), strefa, stan
    timeout: jest to czas po jakim czujnik jest nieaktywny po zmianie stanu w celu zapobiegniecia wielokrotnych zmian
    nastawy: sterowanie za pomoca balis: nastawy, jakie zostana ustawione po przejechaniu przez czujnik
    """
    nr = 1
    x = 1
    y = 1
    pocIn = -1
    zone = 'N'
    Aktywny = False
    __isActive = False
    # do inicjalizacji podajemy numer, wspolrzedne, stan
    def __init__(self, n, wspx, wspy, czyA) :
        self.nr = n
        self.x = wspx
        self.y = wspy
        self.timeout = 0
        self.Aktywny = czyA
        self.nastawy = []

class Map(QtGui.QWidget):
    """
    glowny widget mapy
    :param busControl: kontroler szeregowy (do balis i zwrotnic)
    :param kom: obiekt kontrolera pociagow
    """
    def __init__(self,busControl,kom):
        super(Map, self).__init__()

        self.busControl = busControl
        self.kom = kom
        # skala mapy (do rysowania)
        self.scaleObr = 1
        self.xsize = 10
        self.skala = 1
        self.czasyStania = [0, 0, 0]
        self.czasyStaniaPocz = [0, 0, 0]
        # zliczanie przejazdow przez konktetne balisy (do zatrzymywania pociagow)
        self.przejazdyW = 0
        self.przejazdyK = 0
        self.przejazdyS = 0
        self.przejazdyT = 0
        self.przejazdyI = 0
        self.przejazdyE = 0
        self.przejazdyB = 0
        self.stopped = [False, False, False]
        self.pociagi = [1, 2, 3]
        # stacja, na ktorej stoi pociag. Od stacji zalezy dalszy kierunek ruchu
        self.stacja = ['', '', '', '']
        self.zwrotnica = [1,1]
        self.rects = []
        self.trains = []
        # tablica kolorow kropok udajacych pociagi. dany kolor przechowywany razem z pociagiem w liscie self.trains
        self.colours = ["#EE0000",
                        "#00EE00",
                        "#0000EE",
                        "#888800",
                        "#00EEEE"]
        # Tutaj wrzucamy pociagi.
        self.addTrain(1190, 35, 15, 180, 'forward', 2)
        self.addTrain(602, 505, 17, 0, 'backward', 1)
        self.addTrain(1187, 15, 10, 180, 'forward', 0)
        # ---------------------------------------------------------
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.tick)
        self.initUI()
        self.geomOld = self.geometry()
        self.img = 0
        self.saved = 0
        self.repaint()
        self.timer.start(100)

        # zmienne do ustawiania timerow do zatrzymywania sie na Strzyzy i Osowie (nie ma dzialajacych balis blisko stacji)
        # w ogolnosci timerPocz inicjujemy przez czas obecny + czas oczekiwania, a timer przez czas obecny
        # potem w f-cji tick() ponownie ustawiamy zmienna timer (i nie timerPocz). Gdy timer przekroczy timerPocz, czas uplynal
        self.secondsForOsowaPeron = 19.56
        self.secondsForStrzyza = 24.01
        self.osowaStopTimer = 0
        self.osowaStopTimerPocz = 0
        self.osowaTimerZalaczony = 0
        self.strzyzaTimer = 0
        self.strzyzaTimerPocz = 0
        self.strzyzaTimerZalaczony = 0

    def addTrain(self, x, y, vel, ang, dir, col):
        """
        dodanie pociagu do mapy. Pociagi przechowywane w zmiennej self.trains w formie [pociag, kolor kropki na mapie].
        kierunek podany nie ma znaczenia - jest to w zasadzie bardziej intuicyjna wartosc 0/1 jest potrzebny do zmiany kierunku
        jazdy przy zawracaniu na koncu trasu
        :param x: wspolrzedna poczatkowa x
        :param y: wspolrzedna poczatkowa y
        :param vel: predkosc maksymalna poczatkowa
        :param ang: kat jazdy
        :param dir: kierunek (forward, backward)
        :param col: kolor (indeks w tablicy kolorow)
        :return: None
        """
        self.trains.append([ruchomaKropka.RuchomyPociag(x, y, vel, ang, dir), self.colours[col]])

    def tick(self):
        """
        funkcja wywolywana na kazdy obieg timera (0.01s)
        :return: None
        """
        # odswierzenie obrazu
        self.repaint()
        # Kolejne cykle symuacji
        if self.saved >= 5:
            for train, _ in self.trains:
                train.move(self.img)
                train.updateSpeed()
        # reset timeoutow (czasow dezaktywacji) po ich uplynieciu (potem mozna sprawdzac, czy jest 0 na timeoucie: jesli jest to mozna aktywowac ponownie)
        for czujnik in self.czujniki:
            if czujnik.timeout < t.time():
                czujnik.timeout = 0
        # timer do zatrzymania na Osowie. Jako, ze nie ma balis, to trzeba po przejechaniu przez najblizsza odczekac czas jaki pociagowi zajmie dojazd na peron
        if not self.osowaTimerZalaczony == 0:
            if self.osowaStopTimerPocz - self.osowaStopTimer > 0.:
                self.osowaStopTimer = t.time()
            else:
                if self.osowaTimerZalaczony == 1:
                    self.czasyStania[2] = t.time()
                    self.czasyStaniaPocz[2] = t.time() + 10
                    self.stacja[2] = 'F'

                self.osowaTimerZalaczony = 0
        # podobnie jak na Osowie, timer dla Strzyzy od strony Kielpinka
        if not self.strzyzaTimerZalaczony == 0:
            if self.strzyzaTimerPocz - self.strzyzaTimer > 0.:
                self.strzyzaTimer = t.time()
            else:
                if self.strzyzaTimerZalaczony == 1:
                    self.czasyStania[0] = t.time()
                    self.czasyStaniaPocz[0] = t.time() + 10
                    self.stacja[0] = 'T'
                if self.strzyzaTimerZalaczony == 2:
                    self.czasyStania[1] = t.time()
                    self.czasyStaniaPocz[1] = t.time() + 15
                    self.stacja[1] = 'T'
                self.strzyzaTimerZalaczony = 0
        # timer stania: na poczatku wysylamy sygnal stop, po uplynieciu jedziemy dalej (kierunek zalezny od stacji)
        for i in range(self.czasyStania.__len__()):
            if self.czasyStaniaPocz[i] - self.czasyStania[i] > 0.:
                self.czasyStania[i] = t.time()
                if not self.stopped[i]:
                    self.kom.set_speed(self.pociagi[i], 'stop')
                    self.kom.set_speed(self.pociagi[i], 'stop')
                    self.kom.set_speed(self.pociagi[i], 'stop')
                    self.trains[i][0].zahamujSie()
                    self.stopped[i] = True
            else:
                if self.stacja[i] == 'W':
                    self.kom.set_speed(self.pociagi[i], 'przod')
                    self.kom.set_speed(self.pociagi[i], 'przod')
                    self.kom.set_speed(self.pociagi[i], 'przod')
                    if self.trains[i][0].dir == 'backward':
                        self.trains[i][0].dir = 'forward'
                        self.trains[i][0].turnAround()
                    self.stacja[i] = ''
                    self.trains[i][0].ruszSie()
                    self.stopped[i] = False
                elif self.stacja[i] == 'K':
                    self.kom.set_speed(self.pociagi[i], 'tyl')
                    self.kom.set_speed(self.pociagi[i], 'tyl')
                    self.kom.set_speed(self.pociagi[i], 'tyl')
                    if self.trains[i][0].dir == 'forward':
                        self.trains[i][0].dir = 'backward'
                        self.trains[i][0].turnAround()
                    self.stacja[i] = ''
                    self.trains[i][0].ruszSie()
                    self.stopped[i] = False
                elif self.stacja[i] == 'S':
                    self.kom.set_speed(self.pociagi[i], 'przod')
                    self.kom.set_speed(self.pociagi[i], 'przod')
                    self.kom.set_speed(self.pociagi[i], 'przod')
                    if self.trains[i][0].dir == 'backward':
                        self.trains[i][0].dir = 'forward'
                        self.trains[i][0].turnAround()
                    self.stacja[i] = ''
                    self.trains[i][0].ruszSie()
                    self.stopped[i] = False
                elif self.stacja[i] == 'T':
                    self.kom.set_speed(self.pociagi[i], 'tyl')
                    self.kom.set_speed(self.pociagi[i], 'tyl')
                    self.kom.set_speed(self.pociagi[i], 'tyl')
                    if self.trains[i][0].dir == 'forward':
                        self.trains[i][0].dir = 'backward'
                        self.trains[i][0].turnAround()
                    self.stacja[i] = ''
                    self.trains[i][0].ruszSie()
                    self.stopped[i] = False
                elif self.stacja[i] == 'E':
                    self.kom.set_speed(self.pociagi[i], 'przod')
                    self.kom.set_speed(self.pociagi[i], 'przod')
                    self.kom.set_speed(self.pociagi[i], 'przod')
                    if self.trains[i][0].dir == 'backward':
                        self.trains[i][0].dir = 'forward'
                        self.trains[i][0].turnAround()
                    self.stacja[i] = ''
                    self.trains[i][0].ruszSie()
                    self.stopped[i] = False
                elif self.stacja[i] == 'F':
                    self.kom.set_speed(self.pociagi[i], 'wolnoprzod')
                    self.kom.set_speed(self.pociagi[i], 'wolnoprzod')
                    self.kom.set_speed(self.pociagi[i], 'wolnoprzod')
                    if self.trains[i][0].dir == 'backward':
                        self.trains[i][0].dir = 'forward'
                        self.trains[i][0].turnAround()
                    self.stacja[i] = ''
                    self.trains[i][0].maxVel = 5
                    self.trains[i][0].ruszSie()
                    self.stopped[i] = False
                elif self.stacja[i] == 'B':
                    self.kom.set_speed(self.pociagi[i], 'tyl')
                    self.kom.set_speed(self.pociagi[i], 'tyl')
                    self.kom.set_speed(self.pociagi[i], 'tyl')
                    self.trains[2][0].setPos((self.czujniki[3].x*self.xsize+40), (self.czujniki[3].y*self.xsize+30))
                    if self.trains[i][0].dir == 'forward':
                        self.trains[i][0].dir = 'backward'
                        self.trains[i][0].turnAround()
                    self.stacja[i] = ''
                    self.trains[i][0].maxVel = 10
                    self.trains[i][0].ruszSie()
                    self.stopped[i] = False

        self.timer.start(10)


    def initUI(self):
        """
        obsluga czujnikow
        :return: None
        """

        # self.przyciskCzujnik.clicked.connect(self.aktywacjaCzujnika)
        self.czujniki=[]
        for i in range(46):
            self.czujniki.append(Czujnik(i,1,1, False))
        self.wczytaj_wspolrzedne()
        self.ostatniCzujnik = 0

        #obsluga zwrotnic
        # self.przyciskZwrotnica.clicked.connect(self.aktywacjaZwrotnicy)

        self.zwrotnice=[]
        for i in range(34):
            self.zwrotnice.append(busControl.mapSwitchRightDict[i])
        # print self.zwrotnice[0], self.zwrotnice[0]

        self.zastosujNastawy(34, 0)
        self.zastosujNastawy(18, 1)
        self.zastosujNastawy(12, 2)
        #parametry okna
        self.setFixedWidth(13000)
        self.setFixedHeight(5400)

    def paintEvent(self, e):
        """
        rysowanie obrazka: sa 2 obrazki. Jeden widzimy na ekranie, ktory mozna przeskalowac i drugi po ktorym jezdza kropki, ktorego przeskalowac sie nie da (bo nie ma po co)
        ten dla kropek nigdy nie jest widoczny i jest uaktualniany tylko gdy nastapi zmiana stanu torow (np. zmiana zwrotnicy)
        :param e: event
        """

        pixmap = QtGui.QPixmap(QtCore.QSize(13000, 5400))
        if self.saved <= 5:
            qp = QtGui.QPainter(pixmap)
            self.drawAll(qp, False)
            qp.end()
            self.img = pixmap.toImage()
            self.saved += 1
        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawAll(qp, True)
        qp.end()


    def resizeEvent(self,resizeEvent):
        """
        zmiana zmiennych skali po przeskalowaniu obrazka
        nowe wygenerowanie prostokatow do aktywacji balis (balisy sa aktywowane po kliknieciu w najwiekszy prostokat ktorego moga byc przekatna
        :param resizeEvent: event
        """
        #self.setGeometry(10, 30, 6000, 2700)
        geom = self.geometry()
        # self.xsize = min(geom.height()/540., geom.width()/1200.)
        self.geomOld = geom
        self.saved = 3
        # Tu przeskalowujemy pociagi
        for train,_ in self.trains:
            train.x *= self.xsize/self.skala
            train.y *= self.xsize/self.skala
            train.velocity *= self.xsize/self.skala
        self.skala = self.xsize
        self.rects = []
        self.makeRects()
        self.repaint()

    def linia(self,qp, ax, ay, bx, by, xsize):
        """
        wyrysowanie linii
        """
        qp.drawLine(ax*xsize, ay*xsize, bx*xsize, by*xsize)

    def krzywa(self, qp, p0x, p0y, p1x, p1y, p2x, p2y, p3x, p3y, xsize):
        """
        wyrysowanie krzywej. Parametry: p0x, p0y - początek krzywej, p3x, p3y - koniec krzywej
        """
        p0 = QtCore.QPointF(p0x*xsize, p0y*xsize)
        p1 = QtCore.QPointF(p1x*xsize, p1y*xsize)
        p2 = QtCore.QPointF(p2x*xsize, p2y*xsize)
        p3 = QtCore.QPointF(p3x*xsize, p3y*xsize)
        cubicPath = QtGui.QPainterPath(p0)
        cubicPath.cubicTo(p1,p2,p3)
        qp.drawPath(cubicPath);

    def BluePen(self, qp, pen):
        blue = QtGui.QColor(0, 0, 255)
        pen.setColor(blue)
        qp.setPen(pen)

    def GrayPen(self, qp, pen):
        gray = QtGui.QColor(200, 200, 200)
        pen.setColor(gray)
        qp.setPen(pen)

    def drawAll(self, qp, scaled):
        """
        rysowanie mapy
        :param qp: obiekt typu QPainter
        :param scaled: True/False. Czy obraz jest przeskalowany
        :return: None
        """

        xsize = self.xsize
        if scaled:
            xsize *= self.scaleObr
        color = QtGui.QColor(255, 255, 255)
        color.setNamedColor('#FFFFFF')
        qp.setPen(color)

        qp.fillRect(0, 0, 1210*xsize, 540*xsize, color)

        color = QtGui.QColor(0, 0, 0)
        color.setNamedColor('#000000')
        qp.setPen(color)
        pen =QtGui.QPen()
        if scaled:
            pen.setWidth(1)
        else:
            pen.setWidth(4)

        qp.setPen(pen)

        qp.setBrush(QtGui.QColor(255, 255, 255, 0))

        #rysowanie czujnika
        if scaled:
            for i in range(46):
                if not self.czujniki[i].Aktywny:
                    continue
                if self.czujniki[i].zone == 'N':
                    continue
                color = QtGui.QColor(0, 255, 0)
                if self.czujniki[i].aktywnyZerem:
                    color.setNamedColor('#FF0000')
                else:
                    color.setNamedColor('#0000FF')
                qp.setPen(color)
                qp.setBrush(Qt.green)
                qp.drawEllipse(self.czujniki[i].x*xsize-4*xsize, self.czujniki[i].y*xsize-4*xsize, 8*xsize, 8*xsize)
                if not self.czujniki[i].nr == 1:
                    qp.drawText(self.czujniki[i].x*xsize-4*xsize, self.czujniki[i].y*xsize-4*xsize, str(self.czujniki[i].nr)+str(self.czujniki[i].zone))
                else:
                    qp.drawText(self.czujniki[i].x*xsize-4*xsize, self.czujniki[i].y*xsize-4*xsize, str(i))

        qp.setBrush(QtGui.QColor(255, 255, 255, 0))
        color = QtGui.QColor(0, 0, 0)
        color.setNamedColor('#000000')
        if scaled:
            pen.setWidth(1)
        else:
            pen.setWidth(4)
        qp.setPen(pen)

        # rysowanie fragmentow torow bez zwrotnic:
        qp.drawLine(503*xsize, 505*xsize, 662*xsize, 504*xsize)
        qp.drawLine(553*xsize, 511*xsize, 662*xsize, 509*xsize)
        qp.drawLine(680*xsize, 504*xsize, 768*xsize, 503*xsize)
        qp.drawLine(680*xsize, 509*xsize, 768*xsize, 507*xsize)
        qp.drawLine(844*xsize, 472*xsize, 888*xsize, 444*xsize)
        qp.drawLine(846*xsize, 477*xsize, 888*xsize, 450*xsize)
        self.krzywa(qp, 768, 503, 802, 496, 827, 483, 844, 472, xsize)
        self.krzywa(qp, 768, 507, 804, 502, 829, 487, 846, 477, xsize)
        qp.drawLine(888*xsize, 444*xsize, 963*xsize, 383*xsize)
        qp.drawLine(888*xsize, 450*xsize, 966*xsize, 387*xsize)
        self.krzywa(qp, 963, 383, 1007, 353, 1059, 344, 1085, 350, xsize)
        self.krzywa(qp, 1085, 350, 1108, 354, 1135, 370, 1147, 394, xsize)
        self.krzywa(qp, 966, 387, 1007, 358, 1059, 349, 1085, 355, xsize)
        self.krzywa(qp, 1085, 355, 1108, 360, 1135, 378, 1145, 404, xsize)
        self.krzywa(qp, 1147, 394, 1160, 415, 1158, 443, 1127, 461, xsize)
        self.krzywa(qp, 1145, 404, 1152, 420, 1148, 440, 1127, 454, xsize)
        self.krzywa(qp, 1127, 461, 1021, 522, 884, 482, 811, 375, xsize)
        self.krzywa(qp, 1127, 454, 1021, 517, 889, 475, 818, 374, xsize)
        self.krzywa(qp, 811, 375, 766, 309, 712, 206, 713, 117, xsize)
        self.krzywa(qp, 818, 374, 771, 309, 727, 206, 721, 155, xsize)
        self.krzywa(qp, 727, 86, 741, 65, 767, 58, 775, 60, xsize)
        self.krzywa(qp, 721, 155, 715, 114, 728, 72, 775, 65, xsize)
        self.krzywa(qp, 775, 60, 816, 58, 871, 54, 921, 52, xsize)
        self.krzywa(qp, 775, 65, 816, 63, 871, 59, 921, 56, xsize)
        self.krzywa(qp, 720, 91, 720, 75, 733, 56, 759, 42, xsize)
        self.krzywa(qp, 759, 42, 771, 30, 781, 24, 807, 24, xsize)
        qp.drawLine(807*xsize, 24*xsize, 1046*xsize, 22*xsize)
        self.krzywa(qp, 712, 105, 702, 70, 693, 56, 641, 52, xsize)
        qp.drawLine(641*xsize, 52*xsize, 563*xsize, 52*xsize)
        qp.drawLine(549*xsize, 52*xsize, 25*xsize, 52*xsize)
        qp.drawLine(549*xsize, 57*xsize, 25*xsize, 58*xsize)
        qp.drawLine(7*xsize, 36*xsize, 720*xsize, 30*xsize)
        qp.drawLine(8*xsize, 42*xsize, 720*xsize, 36*xsize)
        self.krzywa(qp, 720, 30, 750, 28, 756, 49, 785, 46, xsize)
        self.krzywa(qp, 718, 36, 748, 33, 754, 55, 783, 52, xsize)
        qp.drawLine(785*xsize, 46*xsize, 885*xsize, 41*xsize)
        qp.drawLine(783*xsize, 52*xsize, 885*xsize, 47*xsize)
        qp.drawLine(909*xsize, 40*xsize, 1031*xsize, 33*xsize)
        qp.drawLine(909*xsize, 45*xsize, 972*xsize, 43*xsize)
        qp.drawLine(24*xsize, 21*xsize, 649*xsize, 19*xsize)
        qp.drawLine(24*xsize, 26*xsize, 649*xsize, 24*xsize)
        self.krzywa(qp, 649, 19, 723, 13, 793, 3, 821, 8, xsize)
        qp.drawLine(821*xsize, 8*xsize, 1100*xsize, 10*xsize)
        self.krzywa(qp, 649, 24, 723, 18, 793, 11, 821, 14, xsize)
        qp.drawLine(821*xsize, 14*xsize, 1045*xsize, 16*xsize)
        self.linia(qp, 5, 26, 16, 26, xsize)
        self.linia(qp, 5, 52, 16, 52, xsize)
        self.linia(qp, 1009, 41, 993, 42, xsize)
        self.linia(qp, 1035,44, 1050, 44, xsize)
        self.linia(qp, 993, 48, 1050, 50, xsize)
        self.linia(qp, 1050, 38, 1126, 35, xsize)
        self.linia(qp, 1080, 32, 1156, 30, xsize)
        self.linia(qp, 1050, 32, 1065, 32, xsize)
        self.linia(qp, 1079, 28, 1091, 28, xsize)
        self.linia(qp, 1070, 22, 1091, 22, xsize)
        self.linia(qp, 1115, 21, 1124, 21, xsize)
        self.linia(qp, 1070, 16, 1102, 16, xsize)
        self.linia(qp, 1115, 27, 1124, 27, xsize)
        #self.linia(qp, 1080, 32, 1153, 30)
        self.linia(qp, 1073, 43, 1126, 40, xsize)
        self.linia(qp, 1073, 50, 1137, 45, xsize)
        self.linia(qp, 1122, 10, 1133, 10, xsize)
        self.linia(qp, 1122, 16, 1134, 16, xsize)
        self.linia(qp, 1142, 26, 1153, 26, xsize)
        self.linia(qp, 1157, 44, 1204, 44, xsize)
        self.linia(qp, 1143, 35, 1206, 35, xsize)
        self.linia(qp, 1172, 30, 1206, 29, xsize)
        self.linia(qp, 1142, 20, 1201, 20, xsize)
        self.linia(qp, 1152, 15, 1202, 15, xsize)
        self.linia(qp, 1152, 9, 1201, 4, xsize)
        self.linia(qp, 950, 53, 973, 50, xsize)
        self.linia(qp, 1167, 4, 1172, 48, xsize)
        if scaled:
            pen.setWidth(1)
        else:
            pen.setWidth(4)
        qp.setPen(pen)
        # Koniec rysowania torow bez zwrotnic

        #rysowanie fragmentow torow ze zwrotnicami:
        self.BluePen(qp, pen)
        #zwrotnica nr 0
        for i in range(0,34):
            # qp.drawRect(self.rects[i])
            TF = ""
            if self.zwrotnice[i]:
                TF = "T"
            else:
                TF = "F"
            qp.drawText(self.rects[i].x(), self.rects[i].y(), str(i)+TF)
        if self.zwrotnice[0]:
            self.GrayPen(qp, pen)
            self.linia(qp, 1172, 30, 1153, 26, xsize)
            self.BluePen(qp, pen)
            self.linia(qp, 1172, 30, 1153, 30, xsize)
        else:
            self.GrayPen(qp, pen)
            self.linia(qp, 1172, 30, 1153, 30, xsize)
            self.BluePen(qp, pen)
            self.linia(qp, 1172, 30, 1153, 26, xsize)
        #zwrotnica nr 1
        if self.zwrotnice[1]:
            self.GrayPen(qp, pen)
            self.linia(qp, 16, 26, 24, 26, xsize)
            self.BluePen(qp, pen)
            self.linia(qp, 16, 26, 24, 21, xsize)
        else:
            self.GrayPen(qp, pen)
            self.linia(qp, 16, 26, 24, 21, xsize)
            self.BluePen(qp, pen)
            self.linia(qp, 16, 26, 24, 26, xsize)
        #zwrotnica nr 2
        if self.zwrotnice[2]:
            self.GrayPen(qp, pen)
            self.linia(qp, 16, 52, 25, 58, xsize)
            self.BluePen(qp, pen)
            self.linia(qp, 16, 52, 26, 52, xsize)
        else:
            self.GrayPen(qp, pen)
            self.linia(qp, 16, 52, 26, 52, xsize)
            self.BluePen(qp, pen)
            self.linia(qp, 16, 52, 25, 58, xsize)
        #zwrotnica nr 3
        if self.zwrotnice[3]:
            self.GrayPen(qp, pen)
            self.linia(qp, 563, 52, 549, 57, xsize)
            self.BluePen(qp, pen)
            self.linia(qp, 563, 52, 549, 52, xsize)
        else:
            self.GrayPen(qp, pen)
            self.linia(qp, 563, 52, 549, 52, xsize)
            self.BluePen(qp, pen)
            self.linia(qp, 563, 52, 549, 57, xsize)
        #zwrotnica nr 4
        if self.zwrotnice[4]:
            self.GrayPen(qp, pen)
            self.linia(qp, 713, 117, 720, 99, xsize)
            self.BluePen(qp, pen)
            self.linia(qp, 713, 117, 712, 104, xsize)
        else:
            self.GrayPen(qp, pen)
            self.linia(qp, 713, 117, 712, 104, xsize)
            self.BluePen(qp, pen)
            self.linia(qp, 713, 117, 720, 99, xsize)
        #zwrotnica nr 5
        if self.zwrotnice[5]:
            self.GrayPen(qp, pen)
            self.linia(qp, 720, 99, 727, 86, xsize)
            self.BluePen(qp, pen)
            self.linia(qp, 720, 99, 720, 91, xsize)
        else:
            self.GrayPen(qp, pen)
            self.linia(qp, 720, 99, 720, 91, xsize)
            self.BluePen(qp, pen)
            self.linia(qp, 720, 99, 727, 86, xsize)
        #zwrotnica nr 6 #672,507
        if self.zwrotnice[6]:
            self.GrayPen(qp, pen)
            self.linia(qp, 662, 504, 671, 506, xsize)
            self.BluePen(qp, pen)
            self.linia(qp, 662, 504, 671, 504, xsize)
        else:
            self.GrayPen(qp, pen)
            self.linia(qp, 662, 504, 671, 504, xsize)
            self.BluePen(qp, pen)
            self.linia(qp, 662, 504, 671, 506, xsize)
        #zwrotnica nr 7
        if self.zwrotnice[7]:
            self.GrayPen(qp, pen)
            self.linia(qp, 680, 504, 671, 506, xsize)
            self.BluePen(qp, pen)
            self.linia(qp, 680, 504, 671, 504, xsize)
        else:
            self.GrayPen(qp, pen)
            self.linia(qp, 680, 504, 671, 504, xsize)
            self.BluePen(qp, pen)
            self.linia(qp, 680, 504, 671, 506, xsize)
        #zwrotnica nr 8
        if self.zwrotnice[8]:
            self.GrayPen(qp, pen)
            self.linia(qp, 680, 509, 671, 506, xsize)
            self.BluePen(qp, pen)
            self.linia(qp, 680, 509, 671, 509, xsize)
        else:
            self.GrayPen(qp, pen)
            self.linia(qp, 680, 509, 671, 509, xsize)
            self.BluePen(qp, pen)
            self.linia(qp, 680, 509, 671, 506, xsize)
        #zwrotnica nr 9
        if self.zwrotnice[9]:
            self.GrayPen(qp, pen)
            self.linia(qp, 662, 509, 671, 506, xsize)
            self.BluePen(qp, pen)
            self.linia(qp, 662, 509, 671, 509, xsize)
        else:
            self.GrayPen(qp, pen)
            self.linia(qp, 662, 509, 671, 509, xsize)
            self.BluePen(qp, pen)
            self.linia(qp, 662, 509, 671, 506, xsize)
        #zwrotnica nr 10
        if self.zwrotnice[10]:
            self.GrayPen(qp, pen)
            self.linia(qp, 884, 47, 909, 45, xsize)
            self.BluePen(qp, pen)
            self.linia(qp, 897, 43, 909, 45, xsize)
        else:
            self.GrayPen(qp, pen)
            self.linia(qp, 897, 43, 909, 45, xsize)
            self.BluePen(qp, pen)
            self.linia(qp, 884, 47, 909, 45, xsize)
        #zwrotnica nr 11
        if self.zwrotnice[11]:
            self.GrayPen(qp, pen)
            self.linia(qp, 885, 41, 909, 40, xsize)
            self.BluePen(qp, pen)
            self.linia(qp, 885, 41, 897, 43, xsize)
        else:
            self.GrayPen(qp, pen)
            self.linia(qp, 885, 41, 897, 43, xsize)
            self.BluePen(qp, pen)
            self.linia(qp, 885, 41, 909, 40, xsize)
        #zwrotnica nr 12
        if self.zwrotnice[12]:
            self.GrayPen(qp, pen)
            self.linia(qp, 950, 53, 921, 52, xsize)
            self.BluePen(qp, pen)
            self.linia(qp, 950, 53, 920, 56, xsize)
        else:
            self.GrayPen(qp, pen)
            self.linia(qp, 950, 53, 920, 56, xsize)
            self.BluePen(qp, pen)
            self.linia(qp, 950, 53, 921, 52, xsize)
        #zwrotnica nr 13
        if self.zwrotnice[13]:
            self.GrayPen(qp, pen)
            self.linia(qp, 973, 50, 993, 48, xsize)
            self.BluePen(qp, pen)
            self.linia(qp, 973, 50, 983, 46, xsize)
        else:
            self.GrayPen(qp, pen)
            self.linia(qp, 973, 50, 983, 46, xsize)
            self.BluePen(qp, pen)
            self.linia(qp, 973, 50, 993, 48, xsize)
        #zwrotnica nr 14
        if self.zwrotnice[14]:
            self.GrayPen(qp, pen)
            self.linia(qp, 993, 42, 983, 46, xsize)
            self.BluePen(qp, pen)
            self.linia(qp, 993, 42, 972, 43, xsize)
        else:
            self.GrayPen(qp, pen)
            self.linia(qp, 993, 42, 972, 43, xsize)
            self.BluePen(qp, pen)
            self.linia(qp, 993, 42, 983, 46, xsize)
        #zwrotnica nr 15
        if self.zwrotnice[15]:
            self.GrayPen(qp, pen)
            self.linia(qp, 1009, 41, 1035, 44, xsize)
            self.BluePen(qp, pen)
            self.linia(qp, 1009, 41, 1031, 38, xsize)
        else:
            self.GrayPen(qp, pen)
            self.linia(qp, 1009, 41, 1031, 38, xsize)
            self.BluePen(qp, pen)
            self.linia(qp, 1009, 41, 1035, 44, xsize)
        #zwrotnica nr 16
        if self.zwrotnice[16]:
            self.GrayPen(qp, pen)
            self.linia(qp, 1050, 32, 1040, 35, xsize)
            self.BluePen(qp, pen)
            self.linia(qp, 1050, 32, 1031, 33, xsize)
        else:
            self.GrayPen(qp, pen)
            self.linia(qp, 1050, 32, 1031, 33, xsize)
            self.BluePen(qp, pen)
            self.linia(qp, 1050, 32, 1040, 35, xsize)
        #zwrotnica nr 17
        if self.zwrotnice[17]:
            self.GrayPen(qp, pen)
            self.linia(qp, 1031, 38, 1050, 38, xsize)
            self.BluePen(qp, pen)
            self.linia(qp, 1031, 38, 1040, 35, xsize)
        else:
            self.GrayPen(qp, pen)
            self.linia(qp, 1031, 38, 1040, 35, xsize)
            self.BluePen(qp, pen)
            self.linia(qp, 1031, 38, 1050, 38, xsize)
        #zwrotnica nr 18
        if self.zwrotnice[18]:
            self.GrayPen(qp, pen)
            self.linia(qp, 1046, 22, 1077, 22, xsize)
            self.BluePen(qp, pen)
            self.linia(qp, 1046, 22, 1058, 19, xsize)
        else:
            self.GrayPen(qp, pen)
            self.linia(qp, 1046, 22, 1058, 19, xsize)
            self.BluePen(qp, pen)
            self.linia(qp, 1046, 22, 1077, 22, xsize)
        #zwrotnica nr 19
        if self.zwrotnice[19]:
            self.GrayPen(qp, pen)
            self.linia(qp, 1070, 16, 1058, 19, xsize)
            self.BluePen(qp, pen)
            self.linia(qp, 1070, 16, 1041, 16, xsize)
        else:
            self.GrayPen(qp, pen)
            self.linia(qp, 1070, 16, 1041, 16, xsize)
            self.BluePen(qp, pen)
            self.linia(qp, 1070, 16, 1058, 19, xsize)
        #zwrotnica nr 20
        if self.zwrotnice[20]:
            self.GrayPen(qp, pen)
            self.linia(qp, 1073, 50, 1061, 47, xsize)
            self.BluePen(qp, pen)
            self.linia(qp, 1073, 50, 1050, 50, xsize)
        else:
            self.GrayPen(qp, pen)
            self.linia(qp, 1073, 50, 1050, 50, xsize)
            self.BluePen(qp, pen)
            self.linia(qp, 1073, 50, 1061, 47, xsize)
        #zwrotnica nr 21
        if self.zwrotnice[21]:
            self.GrayPen(qp, pen)
            self.linia(qp, 1050, 44, 1061, 47, xsize)
            self.BluePen(qp, pen)
            self.linia(qp, 1050, 44, 1073, 43, xsize)
        else:
            self.GrayPen(qp, pen)
            self.linia(qp, 1050, 44, 1073, 43, xsize)
            self.BluePen(qp, pen)
            self.linia(qp, 1050, 44, 1061, 47, xsize)
        #zwrotnica nr 22
        if self.zwrotnice[22]:
            self.GrayPen(qp, pen)
            self.linia(qp, 1065, 32, 1080, 32, xsize)
            self.BluePen(qp, pen)
            self.linia(qp, 1065, 32, 1079, 28, xsize)
        else:
            self.GrayPen(qp, pen)
            self.linia(qp, 1065, 32, 1079, 28, xsize)
            self.BluePen(qp, pen)
            self.linia(qp, 1065, 32, 1080, 32, xsize)
        #zwrotnica nr 23
        if self.zwrotnice[23]:
            self.GrayPen(qp, pen)
            self.linia(qp, 1091, 28, 1115, 27, xsize)
            self.BluePen(qp, pen)
            self.linia(qp, 1091, 28, 1103, 25, xsize)
        else:
            self.GrayPen(qp, pen)
            self.linia(qp, 1091, 28, 1103, 25, xsize)
            self.BluePen(qp, pen)
            self.linia(qp, 1091, 28, 1115, 27, xsize)
        #zwrotnica nr 24
        if self.zwrotnice[24]:
            self.GrayPen(qp, pen)
            self.linia(qp, 1115, 21, 1091, 22, xsize)
            self.BluePen(qp, pen)
            self.linia(qp, 1115, 21, 1103, 25, xsize)
        else:
            self.GrayPen(qp, pen)
            self.linia(qp, 1115, 21, 1103, 25, xsize)
            self.BluePen(qp, pen)
            self.linia(qp, 1115, 21, 1091, 22, xsize)
        #zwrotnica nr 25
        if self.zwrotnice[25]:
            self.GrayPen(qp, pen)
            self.linia(qp, 1102, 16, 1122, 16, xsize)
            self.BluePen(qp, pen)
            self.linia(qp, 1102, 16, 1112, 13, xsize)
        else:
            self.GrayPen(qp, pen)
            self.linia(qp, 1102, 16, 1112, 13, xsize)
            self.BluePen(qp, pen)
            self.linia(qp, 1102, 16, 1122, 16, xsize)
        #zwrotnica nr 26
        if self.zwrotnice[26]:
            self.GrayPen(qp, pen)
            self.linia(qp, 1122, 10, 1100, 10, xsize)
            self.BluePen(qp, pen)
            self.linia(qp, 1122, 10, 1112, 13, xsize)
        else:
            self.GrayPen(qp, pen)
            self.linia(qp, 1122, 10, 1112, 13, xsize)
            self.BluePen(qp, pen)
            self.linia(qp, 1122, 10, 1100, 10, xsize)
        #zwrotnica nr 27
        if self.zwrotnice[27]:
            self.GrayPen(qp, pen)
            self.linia(qp, 1152, 15, 1134, 16, xsize)
            self.BluePen(qp, pen)
            self.linia(qp, 1152, 15, 1142, 13, xsize)
        else:
            self.GrayPen(qp, pen)
            self.linia(qp, 1152, 15, 1142, 13, xsize)
            self.BluePen(qp, pen)
            self.linia(qp, 1152, 15, 1134, 16, xsize)
        #zwrotnica nr 28
        if self.zwrotnice[28]:
            self.GrayPen(qp, pen)
            self.linia(qp, 1133, 10, 1142, 13, xsize)
            self.BluePen(qp, pen)
            self.linia(qp, 1133, 10, 1152, 9, xsize)
        else:
            self.GrayPen(qp, pen)
            self.linia(qp, 1133, 10, 1152, 9, xsize)
            self.BluePen(qp, pen)
            self.linia(qp, 1133, 10, 1142, 13, xsize)
        #zwrotnica nr 29
        if self.zwrotnice[29]:
            self.GrayPen(qp, pen)
            self.linia(qp, 1124, 21, 1132, 24, xsize)
            self.BluePen(qp, pen)
            self.linia(qp, 1124, 21, 1142, 20, xsize)
        else:
            self.GrayPen(qp, pen)
            self.linia(qp, 1124, 21, 1142, 20, xsize)
            self.BluePen(qp, pen)
            self.linia(qp, 1124, 21, 1132, 24, xsize)
        #zwrotnica nr 30
        if self.zwrotnice[30]:
            self.GrayPen(qp, pen)
            self.linia(qp, 1142, 26, 1132, 24, xsize)
            self.BluePen(qp, pen)
            self.linia(qp, 1142, 26, 1124, 27, xsize)
        else:
            self.GrayPen(qp, pen)
            self.linia(qp, 1142, 26, 1124, 27, xsize)
            self.BluePen(qp, pen)
            self.linia(qp, 1142, 26, 1132, 24, xsize)
        #zwrotnica nr 31
        if self.zwrotnice[31]:
            self.GrayPen(qp, pen)
            self.linia(qp, 1143, 35, 1135, 37, xsize)
            self.BluePen(qp, pen)
            self.linia(qp, 1143, 35, 1126, 35, xsize)
        else:
            self.GrayPen(qp, pen)
            self.linia(qp, 1143, 35, 1126, 35, xsize)
            self.BluePen(qp, pen)
            self.linia(qp, 1143, 35, 1135, 37, xsize)
        #zwrotnica nr 32
        if self.zwrotnice[32]:
            self.GrayPen(qp, pen)
            self.linia(qp, 1126, 40, 1142, 40, xsize)
            self.BluePen(qp, pen)
            self.linia(qp, 1126, 40, 1135, 37, xsize)
        else:
            self.GrayPen(qp, pen)
            self.linia(qp, 1126, 40, 1135, 37, xsize)
            self.BluePen(qp, pen)
            self.linia(qp, 1126, 40, 1142, 40, xsize)
        #zwrotnica nr 33
        if self.zwrotnice[33]:
            self.GrayPen(qp, pen)
            self.linia(qp, 1157, 44, 1137, 45, xsize)
            self.BluePen(qp, pen)
            self.linia(qp, 1157, 44, 1142, 40, xsize)
        else:
            self.GrayPen(qp, pen)
            self.linia(qp, 1157, 44, 1142, 40, xsize)
            self.BluePen(qp, pen)
            self.linia(qp, 1157, 44, 1137, 45, xsize)

        # Koniec rysowania torow ze zwrotnicami
        # if scaled:
        #     for i in range(0,34):
        #         qp.drawRect(self.rects[i])
        if self.saved >= 5:
            # Tu rysujemy kropki oznaczajace pociagi.
            for train, colour in self.trains:
                color.setNamedColor(colour)
                qp.setPen(color)
                qp.setBrush(color)
                if scaled:
                    r = (train.r-3) * self.scaleObr + 3
                    x = (train.x - r/2)*self.scaleObr
                    y = (train.y - r/2)*self.scaleObr - 0.1/self.scaleObr
                else:
                    x = (train.x - train.r/2)
                    y = (train.y - train.r/2)
                    r = train.r
                qp.drawEllipse(x, y, r, r)

    def plus(self):
        """
        powiekszenie mapy
        :return: wartosc boolowska mowiaca czy osiagnieto maksymalne przyblizenie
        """
        isNotMax = self.scaleObr < 0.9
        if self.scaleObr < 1:
            self.scaleObr += 0.1
            self.setFixedWidth(13000*self.scaleObr)
            self.setFixedHeight(5400*self.scaleObr)
        self.repaint()
        return isNotMax

    def minus(self):
        """
        pomniejszenie mapy
        :return: wartosc boolowska mowiaca czy osiagnieto maksymalne oddalenie
        """
        isNotMin = self.scaleObr > 0.3
        if self.scaleObr > 0.2:
            self.scaleObr -= 0.1
            self.setFixedWidth(13000*self.scaleObr)
            self.setFixedHeight(5400*self.scaleObr)
        self.repaint()
        return isNotMin

    def aktywacjaCzujnika(self, id, zone):
        """
        aktywowanie czujnika na mapie (wyswietlenie zielonego kola)
        :param id: id czujnika na makiecie
        :param zone: strefa czujnika na makiecie
        :return: ID najblizszej kropki, id czujnika w tablicy
        """
        found = False
        czx = 0
        czy = 0
        czid = 0
        for i in range(0,self.czujniki.__len__()):
            czujnik = self.czujniki[i]
            if czujnik.nr == id and czujnik.zone == zone:
                czx = czujnik.x*self.xsize
                czy = czujnik.y*self.xsize
                czid = i
                found = True
                break
        if self.czujniki[czid].timeout == 0:
            self.czujniki[czid].Aktywny = not self.czujniki[czid].Aktywny
        minOdl = 10e15
        myT = -1
        if not found:
            return czid, myT
        for i in range(0,self.trains.__len__()):
            train = self.trains[i][0]
            odl = ((train.x - czx)**2 + (train.y - czy)**2)**0.5
            if odl < minOdl:
                minOdl = odl
                myT = i
        return czid, myT

    def zastosujNastawy(self, czj, poc):
        """
        zastosowanie nastaw dla danej pary czujnik, pociag
        :param czj: czujnik
        :param poc: powiazany z nim pociag
        :return: None
        """
        for nastawa in self.czujniki[czj].nastawy:
            if nastawa.nr_poc == poc or nastawa.nr_poc == -1:
                zwr = nastawa.nr_zwr
                if self.zwrotnice[zwr] != nastawa.stan:
                    self.switchSwitcher(zwr)

    def wczytaj_wspolrzedne(self):
        """
        rozmieszczenie na mapie balis, dodanie nastaw w razie aktywacji (-1 przy id pociagu oznacza 'kazdy')
        :return: None
        """
        self.czujniki[0].x = 1151
        self.czujniki[0].y = 9
        self.czujniki[0].nr = 502
        self.czujniki[0].zone = 'W'

        self.czujniki[1].x = 1034
        self.czujniki[1].y = 10
        self.czujniki[1].nr = 503
        self.czujniki[1].zone = 'W'

        self.czujniki[2].x = 437
        self.czujniki[2].y = 20
        self.czujniki[2].nr = 302
        self.czujniki[2].zone = 'B'

        self.czujniki[3].x = 7
        self.czujniki[3].y = 26
        self.czujniki[3].nr = 301
        self.czujniki[3].zone = 'B'
        self.czujniki[3].nastawy.append(Nastawa(1, -1, True))
        self.czujniki[3].nastawy.append(Nastawa(26, -1, False))
        self.czujniki[3].nastawy.append(Nastawa(27, -1, True))
        self.czujniki[3].nastawy.append(Nastawa(28, -1, False))

        self.czujniki[4].x = 437
        self.czujniki[4].y = 25
        self.czujniki[4].nr = 303
        self.czujniki[4].zone = 'B'

        self.czujniki[5].x = 841
        self.czujniki[5].y = 14
        self.czujniki[5].nr = 606
        self.czujniki[5].zone = 'W'

        self.czujniki[6].x = 868
        self.czujniki[6].y = 14
        self.czujniki[6].nr = 605
        self.czujniki[6].zone = 'W'

        self.czujniki[7].x = 898
        self.czujniki[7].y = 15
        self.czujniki[7].nr = 604
        self.czujniki[7].zone = 'W'

        self.czujniki[8].x = 923
        self.czujniki[8].y = 15
        self.czujniki[8].nr = 603
        self.czujniki[8].zone = 'W'

        self.czujniki[9].x = 952
        self.czujniki[9].y = 15
        self.czujniki[9].nr = 602
        self.czujniki[9].zone = 'W'

        self.czujniki[10].x = 977
        self.czujniki[10].y = 15
        self.czujniki[10].nr = 601
        self.czujniki[10].zone = 'W'

        self.czujniki[11].x = 1042
        self.czujniki[11].y = 16
        self.czujniki[11].nr = 504
        self.czujniki[11].zone = 'W'

        self.czujniki[12].x = 1169
        self.czujniki[12].y = 15
        self.czujniki[12].nr = 501
        self.czujniki[12].zone = 'W'
        self.czujniki[12].nastawy.append(Nastawa(27, -1, False))
        self.czujniki[12].nastawy.append(Nastawa(28, -1, False))
        self.czujniki[12].nastawy.append(Nastawa(1, -1, False))
        self.czujniki[12].nastawy.append(Nastawa(19, -1, True))

        self.czujniki[13].x = 1035
        self.czujniki[13].y = 22
        self.czujniki[13].nr = 104
        self.czujniki[13].aktywnyZerem = True
        self.czujniki[13].zone = 'W'

        self.czujniki[14].x = 720
        self.czujniki[14].y = 88
        self.czujniki[14].nr = 101
        self.czujniki[14].aktywnyZerem = True
        self.czujniki[14].zone = 'S'

        self.czujniki[15].x = 727
        self.czujniki[15].y = 206
        self.czujniki[15].nr = 103
        self.czujniki[15].aktywnyZerem = True
        self.czujniki[15].zone = 'S'

        self.czujniki[16].x = 812
        self.czujniki[16].y = 376

        self.czujniki[17].x = 962
        self.czujniki[17].y = 384
        self.czujniki[17].nr = 103
        self.czujniki[17].aktywnyZerem = True
        self.czujniki[17].zone = 'K'
        self.czujniki[17].nastawy.append(Nastawa(6, -1, True))
        self.czujniki[17].nastawy.append(Nastawa(7, -1, True))


        self.czujniki[18].x = 627
        self.czujniki[18].y = 504
        self.czujniki[18].nr = 102
        self.czujniki[18].aktywnyZerem = True
        self.czujniki[18].zone = 'K'
        self.czujniki[18].nastawy.append(Nastawa(6, -1, False))
        self.czujniki[18].nastawy.append(Nastawa(8, -1, False))

        self.czujniki[19].x = 711
        self.czujniki[19].y = 101
        self.czujniki[19].nr = 102
        self.czujniki[19].aktywnyZerem = True
        self.czujniki[19].zone = 'S'


        self.czujniki[20].x = 538
        self.czujniki[20].y = 52

        self.czujniki[21].x = 7
        self.czujniki[21].y = 52
        self.czujniki[21].nr = 313
        self.czujniki[21].zone = 'B'

        self.czujniki[22].x = 538
        self.czujniki[22].y = 57

        self.czujniki[23].x = 1169
        self.czujniki[23].y = 44
        self.czujniki[23].nr = 101
        self.czujniki[23].aktywnyZerem = True
        self.czujniki[23].zone = 'W'

        self.czujniki[24].x = 1003
        self.czujniki[24].y = 48
        self.czujniki[24].nr = 106
        self.czujniki[24].aktywnyZerem = True
        self.czujniki[24].zone = 'W'

        self.czujniki[25].x = 965
        self.czujniki[25].y = 51
        self.czujniki[25].nr = 108
        self.czujniki[25].aktywnyZerem = True
        self.czujniki[25].zone = 'W'

        self.czujniki[26].x = 920
        self.czujniki[26].y = 56
        self.czujniki[26].nr = 109
        self.czujniki[26].aktywnyZerem = True
        self.czujniki[26].zone = 'W'
        self.czujniki[26].nastawy.append(Nastawa(12, -1, True))

        self.czujniki[27].x = 733
        self.czujniki[27].y = 205
        self.czujniki[27].nr = 104
        self.czujniki[27].aktywnyZerem = True
        self.czujniki[27].zone = 'S'
        self.czujniki[27].nastawy.append(Nastawa(12, -1, True))
        self.czujniki[27].nastawy.append(Nastawa(14, -1, False))
        self.czujniki[27].nastawy.append(Nastawa(13, -1, True))
        self.czujniki[27].nastawy.append(Nastawa(15, -1, True))
        self.czujniki[27].nastawy.append(Nastawa(12, -1, True))
        self.czujniki[27].nastawy.append(Nastawa(17, -1, False))
        self.czujniki[27].nastawy.append(Nastawa(31, -1, True))

        self.czujniki[28].x = 818
        self.czujniki[28].y = 374
        self.czujniki[28].nr = 0
        self.czujniki[28].zone = 'S'

        self.czujniki[29].x = 965
        self.czujniki[29].y = 388
        self.czujniki[29].nr = 104
        self.czujniki[29].aktywnyZerem = True
        self.czujniki[29].zone = 'K'

        self.czujniki[30].x = 627
        self.czujniki[30].y = 510
        self.czujniki[30].nr = 101
        self.czujniki[30].aktywnyZerem = True
        self.czujniki[30].zone = 'K'

        self.czujniki[31].x = 920
        self.czujniki[31].y = 52
        self.czujniki[31].nr = 110
        self.czujniki[31].aktywnyZerem = True
        self.czujniki[31].zone = 'W'

        self.czujniki[32].x = 1037
        self.czujniki[32].y = 44
        self.czujniki[32].nr = 105
        self.czujniki[32].aktywnyZerem = True
        self.czujniki[32].zone = 'W'

        self.czujniki[33].x = 1079
        self.czujniki[33].y = 37

        self.czujniki[34].x = 1183
        self.czujniki[34].y = 35
        self.czujniki[34].nr = 102
        self.czujniki[34].aktywnyZerem = True
        self.czujniki[34].zone = 'W'
        self.czujniki[34].nastawy.append(Nastawa(31, -1, False))
        self.czujniki[34].nastawy.append(Nastawa(32, -1, True))
        self.czujniki[34].nastawy.append(Nastawa(21, -1, True))
        self.czujniki[34].nastawy.append(Nastawa(15, -1, False))
        self.czujniki[34].nastawy.append(Nastawa(32, -1, True))
        self.czujniki[34].nastawy.append(Nastawa(13, -1, True))
        self.czujniki[34].nastawy.append(Nastawa(14, -1, False))
        self.czujniki[34].nastawy.append(Nastawa(12, -1, False))
        self.czujniki[34].nastawy.append(Nastawa(5, -1, False))
        self.czujniki[34].nastawy.append(Nastawa(4, -1, False))

        self.czujniki[35].x = 1040
        self.czujniki[35].y = 35
        self.czujniki[35].nr = 307
        self.czujniki[35].aktywnyZerem = True
        self.czujniki[35].zone = 'W'

        self.czujniki[36].x = 1183
        self.czujniki[36].y = 30
        self.czujniki[36].nr = 301
        self.czujniki[36].aktywnyZerem = True
        self.czujniki[36].zone = 'W'
        self.czujniki[36].nastawy.append(Nastawa(0, 3, True))
        self.czujniki[36].nastawy.append(Nastawa(22, 3, False))
        self.czujniki[36].nastawy.append(Nastawa(16, 3, True))
        self.czujniki[36].nastawy.append(Nastawa(11, 3, False))

        self.czujniki[37].x = 1084
        self.czujniki[37].y = 32
        self.czujniki[37].nr = 305
        self.czujniki[37].aktywnyZerem = True
        self.czujniki[37].zone = 'W'

        self.czujniki[38].x = 1030
        self.czujniki[38].y = 33
        self.czujniki[38].nr = 308
        self.czujniki[38].aktywnyZerem = True
        self.czujniki[38].zone = 'W'
        self.czujniki[38].nastawy.append(Nastawa(29, 3, True))
        self.czujniki[38].nastawy.append(Nastawa(22, 3, True))
        self.czujniki[38].nastawy.append(Nastawa(23, 3, True))
        self.czujniki[38].nastawy.append(Nastawa(24, 3, True))

        self.czujniki[39].x = 971
        self.czujniki[39].y = 43
        self.czujniki[39].nr = 309
        self.czujniki[39].aktywnyZerem = True
        self.czujniki[39].zone = 'W'

        self.czujniki[40].x = 1077
        self.czujniki[40].y = 29
        self.czujniki[40].nr = 306
        self.czujniki[40].aktywnyZerem = True
        self.czujniki[40].zone = 'W'

        self.czujniki[41].x = 1101
        self.czujniki[41].y = 25
        self.czujniki[41].nr = 304
        self.czujniki[41].aktywnyZerem = True
        self.czujniki[41].zone = 'W'

        self.czujniki[42].x = 1141
        self.czujniki[42].y = 20
        self.czujniki[42].nr = 302
        self.czujniki[42].aktywnyZerem = True
        self.czujniki[42].zone = 'W'
        self.czujniki[42].nastawy.append(Nastawa(29, 3, True))
        self.czujniki[42].nastawy.append(Nastawa(24, 3, False))
        self.czujniki[42].nastawy.append(Nastawa(18, 3, False))

        self.czujniki[43].x = 1131
        self.czujniki[43].y = 24
        self.czujniki[43].nr = 303
        self.czujniki[43].aktywnyZerem = True
        self.czujniki[43].zone = 'W'

        self.czujniki[44].x = 437
        self.czujniki[44].y = 32
        self.czujniki[44].nr = 101
        self.czujniki[44].zone = 'B'

        self.czujniki[45].x = 437
        self.czujniki[45].y = 38
        self.czujniki[45].nr = 102
        self.czujniki[45].zone = 'B'

    def switchSwitcher(self, number):
        """
        zmiana stanu zwrotnicy
        :param number: numer zwrotnicy
        :return: None
        """
        self.zwrotnice[number] = not self.zwrotnice[number]
        self.busControl.changeSwitcherByMap(number)
        self.saved = 3

    def switchSwitcherOnlyOnMap(self, number):
        """
        zmiana stanu zwrotnicy, ale tylko na mapie
        :param number: numer zwrotnicy
        :return: None
        """
        self.zwrotnice[number] = not self.zwrotnice[number]
        self.saved = 3

    def makeRects(self):
        """
        zdefiniowanie prostokatow do aktywacji balis:
        balisy moga byc aktywowane przez klikniecie na odpowiednie miejsce na mapie, ta funkcja definiuje te miejsca
        :return: None
        """
        self.rects.append(QtCore.QRect(1153*self.xsize*self.scaleObr, 26*self.xsize*self.scaleObr, 19*self.xsize*self.scaleObr, 4*self.xsize*self.scaleObr))
        self.rects.append(QtCore.QRect(16*self.xsize*self.scaleObr, 21*self.xsize*self.scaleObr, 8*self.xsize*self.scaleObr, 5*self.xsize*self.scaleObr))
        self.rects.append(QtCore.QRect(16*self.xsize*self.scaleObr, 52*self.xsize*self.scaleObr, 10*self.xsize*self.scaleObr, 6*self.xsize*self.scaleObr))
        self.rects.append(QtCore.QRect(549*self.xsize*self.scaleObr, 52*self.xsize*self.scaleObr, 14*self.xsize*self.scaleObr, 5*self.xsize*self.scaleObr))
        self.rects.append(QtCore.QRect(712*self.xsize*self.scaleObr, 99*self.xsize*self.scaleObr, 8*self.xsize*self.scaleObr, 18*self.xsize*self.scaleObr))
        self.rects.append(QtCore.QRect(720*self.xsize*self.scaleObr, 86*self.xsize*self.scaleObr, 7*self.xsize*self.scaleObr, 13*self.xsize*self.scaleObr))
        self.rects.append(QtCore.QRect(662*self.xsize*self.scaleObr, 504*self.xsize*self.scaleObr, 9*self.xsize*self.scaleObr, 2*self.xsize*self.scaleObr))
        self.rects.append(QtCore.QRect(671*self.xsize*self.scaleObr, 504*self.xsize*self.scaleObr, 9*self.xsize*self.scaleObr, 2*self.xsize*self.scaleObr))
        self.rects.append(QtCore.QRect(671*self.xsize*self.scaleObr, 506*self.xsize*self.scaleObr, 9*self.xsize*self.scaleObr, 3*self.xsize*self.scaleObr))
        self.rects.append(QtCore.QRect(662*self.xsize*self.scaleObr, 506*self.xsize*self.scaleObr, 9*self.xsize*self.scaleObr, 3*self.xsize*self.scaleObr))
        self.rects.append(QtCore.QRect(884*self.xsize*self.scaleObr, 43*self.xsize*self.scaleObr, 25*self.xsize*self.scaleObr, 4*self.xsize*self.scaleObr))
        self.rects.append(QtCore.QRect(885*self.xsize*self.scaleObr, 40*self.xsize*self.scaleObr, 24*self.xsize*self.scaleObr, 3*self.xsize*self.scaleObr))
        self.rects.append(QtCore.QRect(920*self.xsize*self.scaleObr, 52*self.xsize*self.scaleObr, 54*self.xsize*self.scaleObr, 6*self.xsize*self.scaleObr))
        self.rects.append(QtCore.QRect(973*self.xsize*self.scaleObr, 46*self.xsize*self.scaleObr, 20*self.xsize*self.scaleObr, 4*self.xsize*self.scaleObr))
        self.rects.append(QtCore.QRect(972*self.xsize*self.scaleObr, 42*self.xsize*self.scaleObr, 21*self.xsize*self.scaleObr, 4*self.xsize*self.scaleObr))
        self.rects.append(QtCore.QRect(1009*self.xsize*self.scaleObr, 38*self.xsize*self.scaleObr, 24*self.xsize*self.scaleObr, 6*self.xsize*self.scaleObr))
        self.rects.append(QtCore.QRect(1031*self.xsize*self.scaleObr, 32*self.xsize*self.scaleObr, 19*self.xsize*self.scaleObr, 3*self.xsize*self.scaleObr))
        self.rects.append(QtCore.QRect(1031*self.xsize*self.scaleObr, 38*self.xsize*self.scaleObr, 19*self.xsize*self.scaleObr, 3*self.xsize*self.scaleObr))
        self.rects.append(QtCore.QRect(1046*self.xsize*self.scaleObr, 19*self.xsize*self.scaleObr, 31*self.xsize*self.scaleObr, 3*self.xsize*self.scaleObr))
        self.rects.append(QtCore.QRect(1041*self.xsize*self.scaleObr, 16*self.xsize*self.scaleObr, 29*self.xsize*self.scaleObr, 3*self.xsize*self.scaleObr))
        self.rects.append(QtCore.QRect(1050*self.xsize*self.scaleObr, 47*self.xsize*self.scaleObr, 23*self.xsize*self.scaleObr, 3*self.xsize*self.scaleObr))
        self.rects.append(QtCore.QRect(1050*self.xsize*self.scaleObr, 43*self.xsize*self.scaleObr, 23*self.xsize*self.scaleObr, 3*self.xsize*self.scaleObr))
        self.rects.append(QtCore.QRect(1065*self.xsize*self.scaleObr, 28*self.xsize*self.scaleObr, 15*self.xsize*self.scaleObr, 4*self.xsize*self.scaleObr))
        self.rects.append(QtCore.QRect(1091*self.xsize*self.scaleObr, 25*self.xsize*self.scaleObr, 24*self.xsize*self.scaleObr, 3*self.xsize*self.scaleObr))
        self.rects.append(QtCore.QRect(1091*self.xsize*self.scaleObr, 21*self.xsize*self.scaleObr, 24*self.xsize*self.scaleObr, 4*self.xsize*self.scaleObr))
        self.rects.append(QtCore.QRect(1102*self.xsize*self.scaleObr, 13*self.xsize*self.scaleObr, 20*self.xsize*self.scaleObr, 3*self.xsize*self.scaleObr))
        self.rects.append(QtCore.QRect(1100*self.xsize*self.scaleObr, 10*self.xsize*self.scaleObr, 22*self.xsize*self.scaleObr, 3*self.xsize*self.scaleObr))
        self.rects.append(QtCore.QRect(1134*self.xsize*self.scaleObr, 13*self.xsize*self.scaleObr, 18*self.xsize*self.scaleObr, 3*self.xsize*self.scaleObr))
        self.rects.append(QtCore.QRect(1133*self.xsize*self.scaleObr, 9*self.xsize*self.scaleObr, 19*self.xsize*self.scaleObr, 4*self.xsize*self.scaleObr))
        self.rects.append(QtCore.QRect(1124*self.xsize*self.scaleObr, 20*self.xsize*self.scaleObr, 18*self.xsize*self.scaleObr, 4*self.xsize*self.scaleObr))
        self.rects.append(QtCore.QRect(1124*self.xsize*self.scaleObr, 24*self.xsize*self.scaleObr, 18*self.xsize*self.scaleObr, 3*self.xsize*self.scaleObr))
        self.rects.append(QtCore.QRect(1126*self.xsize*self.scaleObr, 35*self.xsize*self.scaleObr, 17*self.xsize*self.scaleObr, 2*self.xsize*self.scaleObr))
        self.rects.append(QtCore.QRect(1126*self.xsize*self.scaleObr, 37*self.xsize*self.scaleObr, 18*self.xsize*self.scaleObr, 3*self.xsize*self.scaleObr))
        self.rects.append(QtCore.QRect(1137*self.xsize*self.scaleObr, 40*self.xsize*self.scaleObr, 20*self.xsize*self.scaleObr, 5*self.xsize*self.scaleObr))

    def ustawHamowanie(self, bal):
        """
        wlaczenie hamowania (lub timera do hamowania) dla danego pociagu po przejechaniu przez czujnik.
        Identyfikacja pociagu przez zliczanie przejazdow i parzystosc lub podzielnosc przez 4
        :param bal: aktywowany czujnik
        :return: None
        """
        if bal == 34:
            self.przejazdyW += 1
            if (self.przejazdyW - 2)%4 == 0:
                self.czasyStania[1] = t.time()
                self.czasyStaniaPocz[1] = t.time() + 10
                self.stacja[1] = 'W'
                self.trains[1][0].setPos((self.czujniki[34].x*self.xsize+40), (self.czujniki[34].y*self.xsize+20))
            elif (self.przejazdyW)%4 == 0:
                self.czasyStania[0] = t.time()
                self.czasyStaniaPocz[0] = t.time() + 10
                self.stacja[0] = 'W'
                self.trains[0][0].setPos((self.czujniki[34].x*self.xsize+40), (self.czujniki[34].y*self.xsize+20))
        elif bal == 15:
            self.przejazdyS += 1
            if (self.przejazdyS)%2 == 0:
                self.czasyStania[1] = t.time()
                self.czasyStaniaPocz[1] = t.time() + 15
                self.stacja[1] = 'S'
                self.trains[1][0].setPos((self.czujniki[15].x*self.xsize+50), (self.czujniki[15].y*self.xsize+50))
            elif (self.przejazdyS)%2 == 1:
                self.czasyStania[0] = t.time()
                self.czasyStaniaPocz[0] = t.time() + 10
                self.stacja[0] = 'S'
                self.trains[0][0].setPos((self.czujniki[15].x*self.xsize+50), (self.czujniki[15].y*self.xsize+50))
        elif bal == 28:
            self.przejazdyT += 1
            if self.przejazdyT%4 == 0:
                self.czasyStania[0] = t.time()
                self.czasyStaniaPocz[0] = t.time() + 10
                self.stacja[0] = 'T'
                self.trains[0][0].setPos((self.czujniki[27].x*self.xsize+15), (self.czujniki[27].y*self.xsize+60))
            elif self.przejazdyT%4 == 2:
                self.czasyStania[1] = t.time()
                self.czasyStaniaPocz[1] = t.time() + 15
                self.stacja[1] = 'T'
                self.trains[1][0].setPos((self.czujniki[27].x*self.xsize+15), (self.czujniki[27].y*self.xsize+60))
        elif bal == 18:
            self.przejazdyK += 1
            if (self.przejazdyK - 2)%4 == 0:
                self.czasyStania[0] = t.time()
                self.czasyStaniaPocz[0] = t.time() + 10
                self.stacja[0] = 'K'
                self.trains[0][0].setPos((self.czujniki[18].x*self.xsize+40), (self.czujniki[18].y*self.xsize+55))
            elif (self.przejazdyK)%4 == 0:
                self.czasyStania[1] = t.time()
                self.czasyStaniaPocz[1] = t.time() + 10
                self.stacja[1] = 'K'
                self.trains[1][0].setPos((self.czujniki[18].x*self.xsize+40), (self.czujniki[18].y*self.xsize+55))
        elif bal == 3:
            self.przejazdyB += 1
            if (self.przejazdyB)%2 == 1:
                self.osowaStopTimer = t.time()
                self.osowaStopTimerPocz = t.time() #+ self.secondsForOsowaCostam
                self.osowaTimerZalaczony = 2
                self.trains[2][0].setPos((self.czujniki[3].x*self.xsize+40), (self.czujniki[3].y*self.xsize+30))
        elif bal == 12:
            self.przejazdyE += 1
            if (self.przejazdyE)%2 == 0:
                self.czasyStania[2] = t.time()
                self.czasyStaniaPocz[2] = t.time() + 10
                self.stacja[2] = 'E'
                self.trains[2][0].setPos((self.czujniki[12].x*self.xsize+40), (self.czujniki[12].y*self.xsize+40))
        elif bal == 4:
            self.osowaStopTimer = t.time()
            self.osowaStopTimerPocz = t.time() + self.secondsForOsowaPeron
            self.osowaTimerZalaczony = 1
        elif bal == 29:
            self.przejazdyI += 1
            self.strzyzaTimer = t.time()
            self.strzyzaTimerPocz = t.time() + self.secondsForStrzyza
            if (self.przejazdyI)%2 == 0:
                self.strzyzaTimerZalaczony = 1
                self.trains[0][0].setPos((self.czujniki[29].x*self.xsize+20), (self.czujniki[29].y*self.xsize+20))
                self.trains[0][0].angle = math.pi/4
            elif (self.przejazdyI)%2 == 1:
                self.trains[1][0].setPos((self.czujniki[29].x*self.xsize+20), (self.czujniki[29].y*self.xsize+20))
                self.trains[1][0].angle = math.pi/4
                self.strzyzaTimerZalaczony = 2

    def mousePressEvent(self, event):
        """
        klikniecie mysza: sprawdzenie, czy nastapilo wewnatrz prostokata aktywujacego balise. Jesli tak to przelacz balise.
        :param event: mouse event
        :return: None
        """
        rectangle = []
        pt = event.pos()
        for i in range(0,34):
            if self.rects[i].contains(pt):
                self.switchSwitcher(i)
