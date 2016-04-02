import math
from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4.QtGui import QPixmap, QApplication, QColor


class RuchomyPociag:
    r = 5
    x = 0
    y = 0
    angle = 0

    # Inicjalizacja. Podajemy współrzędne środka, prędkość początkową i kąt. Kąt nie musi być dokładny, byle tylko pokazywał mniej
    # więcej, w którą stronę jedziemy.

    def __init__(self, xinit, yinit, veloc, ang):
        self.x = xinit
        self.y = yinit
        self.angle = math.pi*ang/180
        self.velocity = veloc

    # Poruszenie się pociągu o jeden krok. Parametr img otrzymujemy wywołując w programie:
    # geom = self.geometry()
    # self.img = QPixmap.grabWindow(QApplication.desktop().winId(), geom.x(), geom.y(), geom.width(), geom.height()).toImage()
    # Jest to obrazek okna programu.

    def move(self, img):
        r = 1
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
        red1 = QtGui.qRed(c1)/3/255 + QtGui.qGreen(c1)/3/255 + QtGui.qBlue(c1)/3/255
        red2 = QtGui.qRed(c2)/3/255 + QtGui.qGreen(c2)/3/255 + QtGui.qBlue(c2)/3/255
        red3 = QtGui.qRed(c3)/3/255 + QtGui.qGreen(c3)/3/255 + QtGui.qBlue(c3)/3/255
        red4 = QtGui.qRed(c4)/3/255 + QtGui.qGreen(c4)/3/255 + QtGui.qBlue(c4)/3/255
        red5 = QtGui.qRed(c5)/3/255 + QtGui.qGreen(c5)/3/255 + QtGui.qBlue(c5)/3/255

        while red1 > 0.9 and red3 > 0.9 and red4 > 0.9:
            self.angle += 0.001
            alfa = self.angle
            c1 = img.pixel(x + l*math.cos(alfa) + r*math.sin(alfa),
                           y - l*math.sin(alfa) + r*math.cos(alfa))
            c4 = img.pixel(x + l*math.cos(alfa) + 3*r*math.sin(alfa),
                       y - l*math.sin(alfa) + 3*r*math.cos(alfa))
            c5 = img.pixel(x + l*math.cos(alfa) - 3*r*math.sin(alfa),
                       y - l*math.sin(alfa) - 3*r*math.cos(alfa))
            c2 = img.pixel(x + l*math.cos(alfa) + (-r)*math.sin(alfa),
                           y - l*math.sin(alfa) + (-r)*math.cos(alfa))
            red2 = QtGui.qRed(c2)/3/255 + QtGui.qGreen(c2)/3/255 + QtGui.qBlue(c2)/3/255
            red1 = QtGui.qRed(c1)/3/255 + QtGui.qGreen(c1)/3/255 + QtGui.qBlue(c1)/3/255
            red4 = QtGui.qRed(c4)/3/255 + QtGui.qGreen(c4)/3/255 + QtGui.qBlue(c4)/3/255
            red5 = QtGui.qRed(c5)/3/255 + QtGui.qGreen(c5)/3/255 + QtGui.qBlue(c5)/3/255
        while red2 > 0.9 and red3 > 0.9 and red5 > 0.9:
            self.angle -= 0.001
            alfa = self.angle
            c1 = img.pixel(x + l*math.cos(alfa) + r*math.sin(alfa),
                           y - l*math.sin(alfa) + r*math.cos(alfa))
            c2 = img.pixel(x + l*math.cos(alfa) + (-r)*math.sin(alfa),
                           y - l*math.sin(alfa) + (-r)*math.cos(alfa))
            c4 = img.pixel(x + l*math.cos(alfa) + 3*r*math.sin(alfa),
                       y - l*math.sin(alfa) + 3*r*math.cos(alfa))
            c5 = img.pixel(x + l*math.cos(alfa) - 3*r*math.sin(alfa),
                       y - l*math.sin(alfa) - 3*r*math.cos(alfa))
            red1 = QtGui.qRed(c1)/3/255 + QtGui.qGreen(c1)/3/255 + QtGui.qBlue(c1)/3/255
            red2 = QtGui.qRed(c2)/3/255 + QtGui.qGreen(c2)/3/255 + QtGui.qBlue(c2)/3/255
            red4 = QtGui.qRed(c4)/3/255 + QtGui.qGreen(c4)/3/255 + QtGui.qBlue(c4)/3/255
            red5 = QtGui.qRed(c5)/3/255 + QtGui.qGreen(c5)/3/255 + QtGui.qBlue(c5)/3/255


        self.x += self.velocity * math.cos(self.angle)
        self.y -= self.velocity * math.sin(self.angle)

    def setPos(self, x, y):
        self.x = x
        self.y = y

    def setMov(self, v, alfa):
        self.velocity = v
        self.angle = alfa
