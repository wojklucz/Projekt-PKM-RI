import math
import threading
from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4.QtGui import QPixmap, QApplication, QColor
from scipy.signal import lti, step
from scipy import linspace
import time as t

# klasa kropki na mapie udajacej pociag. Zadna z funkcji w tej klasie nie odpowiada za sterowanie realnym pociagiem. Powinny byc wywolywane razem z
# f-cjami sterujacymi pociagami
class RuchomyPociag(threading.Thread):
    r = 10
    x = 0
    y = 0
    angle = 0

    def __init__(self, xinit, yinit, veloc, ang, direction):
        """
        Inicjalizacja. Podajemy wspolrzedne srodka, predkosc poczatkowa i kat. Kat nie musi byc dokladny, byle tylko pokazywal mniej
        wiecej, w ktora strone jedziemy.
        :param xinit: wspolrzedna x srodka
        :param yinit: wspolrzedna y srodka
        :param veloc: predkosc poczatkowa
        :param ang: kat
        :param direction: kierunek ruchu
        """
        threading.Thread.__init__(self)
        self.licznik = t.time()
        self.hamuj = False
        self.ruszaj = False
        self.dir = direction
        numR = 0.5869
        denR = [8.4184, 5.00, 3.000]
        tfR = lti(numR, denR)
        self.czas = 5.
        self.maxVel = veloc

        tR, stepR = step(tfR, T = linspace(0, self.czas, self.czas*100))
        self.model = {}
        self.modelRev = {}
        for i in range(tR.__len__()):
            time = round(100*tR[i])/100
            val = round(1000*stepR[i])/1000
            self.model[ time ] = val
            self.modelRev[ val ] = time

        czasHalf = self.czas/2.
        self.model [czasHalf] = (self.model [czasHalf - 0.01] + self.model [czasHalf + 0.01])/2

        self.time = 0
        self.brakingVel = 0
        self.x = xinit
        self.y = yinit
        self.angle = math.pi*ang/180
        self.velocity = 0

    def move(self, img):
        """
        Poruszenie sie pociagu o jeden krok.
        Pociag obraca sie podazajac za czarna linia torow. Odwraca sie od bialego, nie do czarnego, wiec np. niebieski fragment toru tez zadziala
        Po przyjechaniu do konca toru odbija sie i wraca
        :param img:  obrazek widgeta mapy.
        :return: None
        """
        r = 0.5
        l = self.r+1
        alfa = self.angle
        x = self.x
        y = self.y
        c1 = img.pixel(x + l*math.cos(alfa) + r*math.sin(alfa),
                       y - l*math.sin(alfa) + r*math.cos(alfa))
        c2 = img.pixel(x + l*math.cos(alfa) - r*math.sin(alfa),
                       y - l*math.sin(alfa) - r*math.cos(alfa))
        c3 = img.pixel(x + l*math.cos(alfa),
                       y - l*math.sin(alfa))
        c4 = img.pixel(x + l*math.cos(alfa) + 3*r*math.sin(alfa),
                       y - l*math.sin(alfa) + 3*r*math.cos(alfa))
        c5 = img.pixel(x + l*math.cos(alfa) - 3*r*math.sin(alfa),
                       y - l*math.sin(alfa) - 3*r*math.cos(alfa))
        c6 = img.pixel(x + l*math.cos(alfa) + 5*r*math.sin(alfa),
                       y - l*math.sin(alfa) + 5*r*math.cos(alfa))
        c7 = img.pixel(x + l*math.cos(alfa) - 5*r*math.sin(alfa),
                       y - l*math.sin(alfa) - 5*r*math.cos(alfa))
        red1 = QtGui.qRed(c1)/3./255 + QtGui.qGreen(c1)/3./255 + QtGui.qBlue(c1)/3./255
        red2 = QtGui.qRed(c2)/3./255 + QtGui.qGreen(c2)/3./255 + QtGui.qBlue(c2)/3./255
        red3 = QtGui.qRed(c3)/3./255 + QtGui.qGreen(c3)/3./255 + QtGui.qBlue(c3)/3./255
        red4 = QtGui.qRed(c4)/3./255 + QtGui.qGreen(c4)/3./255 + QtGui.qBlue(c4)/3./255
        red5 = QtGui.qRed(c5)/3./255 + QtGui.qGreen(c5)/3./255 + QtGui.qBlue(c5)/3./255
        red6 = QtGui.qRed(c6)/3./255 + QtGui.qGreen(c6)/3./255 + QtGui.qBlue(c6)/3./255
        red7 = QtGui.qRed(c7)/3./255 + QtGui.qGreen(c7)/3./255 + QtGui.qBlue(c7)/3./255

        while red1 > 0.9 and red3 > 0.9 and red4 > 0.9 and red6 > 0.9:
            self.angle += 0.001
            self.angle %= 2*math.pi
            alfa = self.angle
            c1 = img.pixel(x + l*math.cos(alfa) + r*math.sin(alfa),
                       y - l*math.sin(alfa) + r*math.cos(alfa))
            c2 = img.pixel(x + l*math.cos(alfa) - r*math.sin(alfa),
                           y - l*math.sin(alfa) - r*math.cos(alfa))
            c4 = img.pixel(x + l*math.cos(alfa) + 3*r*math.sin(alfa),
                           y - l*math.sin(alfa) + 3*r*math.cos(alfa))
            c5 = img.pixel(x + l*math.cos(alfa) - 3*r*math.sin(alfa),
                           y - l*math.sin(alfa) - 3*r*math.cos(alfa))
            c6 = img.pixel(x + l*math.cos(alfa) + 5*r*math.sin(alfa),
                           y - l*math.sin(alfa) + 5*r*math.cos(alfa))
            c7 = img.pixel(x + l*math.cos(alfa) - 5*r*math.sin(alfa),
                           y - l*math.sin(alfa) - 5*r*math.cos(alfa))
            red1 = QtGui.qRed(c1)/3./255 + QtGui.qGreen(c1)/3./255 + QtGui.qBlue(c1)/3./255
            red2 = QtGui.qRed(c2)/3./255 + QtGui.qGreen(c2)/3./255 + QtGui.qBlue(c2)/3./255
            red4 = QtGui.qRed(c4)/3./255 + QtGui.qGreen(c4)/3./255 + QtGui.qBlue(c4)/3./255
            red5 = QtGui.qRed(c5)/3./255 + QtGui.qGreen(c5)/3./255 + QtGui.qBlue(c5)/3./255
            red6 = QtGui.qRed(c6)/3./255 + QtGui.qGreen(c6)/3./255 + QtGui.qBlue(c6)/3./255
            red7 = QtGui.qRed(c7)/3./255 + QtGui.qGreen(c7)/3./255 + QtGui.qBlue(c7)/3./255
        while red2 > 0.9 and red3 > 0.9 and red5 > 0.9 and red7 > 0.9:
            self.angle -= 0.001
            self.angle %= 2*math.pi
            alfa = self.angle
            c1 = img.pixel(x + l*math.cos(alfa) + r*math.sin(alfa),
                       y - l*math.sin(alfa) + r*math.cos(alfa))
            c2 = img.pixel(x + l*math.cos(alfa) - r*math.sin(alfa),
                           y - l*math.sin(alfa) - r*math.cos(alfa))
            c4 = img.pixel(x + l*math.cos(alfa) + 3*r*math.sin(alfa),
                           y - l*math.sin(alfa) + 3*r*math.cos(alfa))
            c5 = img.pixel(x + l*math.cos(alfa) - 3*r*math.sin(alfa),
                           y - l*math.sin(alfa) - 3*r*math.cos(alfa))
            c6 = img.pixel(x + l*math.cos(alfa) + 5*r*math.sin(alfa),
                           y - l*math.sin(alfa) + 5*r*math.cos(alfa))
            c7 = img.pixel(x + l*math.cos(alfa) - 5*r*math.sin(alfa),
                           y - l*math.sin(alfa) - 5*r*math.cos(alfa))
            red1 = QtGui.qRed(c1)/3./255 + QtGui.qGreen(c1)/3./255 + QtGui.qBlue(c1)/3./255
            red2 = QtGui.qRed(c2)/3./255 + QtGui.qGreen(c2)/3./255 + QtGui.qBlue(c2)/3./255
            red4 = QtGui.qRed(c4)/3./255 + QtGui.qGreen(c4)/3./255 + QtGui.qBlue(c4)/3./255
            red5 = QtGui.qRed(c5)/3./255 + QtGui.qGreen(c5)/3./255 + QtGui.qBlue(c5)/3./255
            red6 = QtGui.qRed(c6)/3./255 + QtGui.qGreen(c6)/3./255 + QtGui.qBlue(c6)/3./255
            red7 = QtGui.qRed(c7)/3./255 + QtGui.qGreen(c7)/3./255 + QtGui.qBlue(c7)/3./255


        self.x += self.velocity * math.cos(self.angle)
        self.y -= self.velocity * math.sin(self.angle)

    def setPos(self, x, y):
        """
        Ustawienie kropki na dane wspolrzedne
        :param x: wspolrzedna x
        :param y: wspolrzedna y
        :return: None
        """
        self.x = x
        self.y = y

    def turnAround(self):
        """
        Obrot o 180 stopni
        :return: None
        """
        self.angle = (math.pi + self.angle)%(2*math.pi)

    def ruszSie(self):
        """
        Ruszenie do przodu
        :return: None
        """
        self.velocity = round((self.velocity/self.maxVel)*1000)/1000
        self.hamuj = False
        self.ruszaj = True
        self.time = self.modelRev[ self.velocity ]
        self.licznik = t.time() - self.time

    def zahamujSie(self):
        """
        hamowanie
        nazwa brakingVel jest mylaca: zmienna odnosi sie do czasu kiedy odp skokowa miala wartosc obecnej predkosci.
        Lub czasu ostatniej, gdy predkosc sie ustabilizowala
        :return: None
        """
        prop = 10
        self.velocity = round((self.velocity/prop)*1000)/1000
        self.ruszaj = False
        self.hamuj = True
        self.brakingVel = self.time
        self.licznik = t.time()
        self.time = 0

    def updateSpeed(self):
        """
        zmiana predkosci przy ruszaniu i hamowaniu na podstawie modelu
        :return: None
        """
        self.time = round((self.time)*100)/100
        if self.ruszaj:
            self.velocity = self.maxVel * self.model[self.time]
            self.time = t.time() - self.licznik
        elif self.hamuj:
            try:
                if not self.velocity == 0:
                    self.velocity = self.maxVel * self.model[round((self.brakingVel - self.time*2)*100.)/100.]
                else:
                    self.hamuj = False
            except:
                self.velocity = 0
        if self.ruszaj or self.hamuj:
            self.time = t.time() - self.licznik
        if self.time >= self.czas:
            self.ruszaj = False
            self.time = self.czas