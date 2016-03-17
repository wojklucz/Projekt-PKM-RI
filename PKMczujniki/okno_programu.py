import sys
from PyQt4 import QtGui, QtCore

class Czujnik:
    nr = 1
    x = 1
    y = 1
    __isActive = False
    def __init__(self, n, wspx, wspy) :
        self.nr = n
        self.x = wspx
        self.y = wspy

class Okno(QtGui.QWidget):

    def __init__(self):
        super(Okno, self).__init__()

        self.initUI()

    def initUI(self):

        pixmap = QtGui.QPixmap("PKM_small_1200.png")

        lbl = QtGui.QLabel(self)
        lbl.setPixmap(pixmap)

        czerwony = QtGui.QPixmap("Dot_red.png")
        rozowy = QtGui.QPixmap("Dot_pink.png")
        czarny = QtGui.QPixmap("Dot_black.png")
        zielony = QtGui.QPixmap("Dot_green.png")

        self.miejsca = []
        napisy = []
        self.wejscia = []
        self.przyciski = []
        self.ost = []
        self.czujniki = []

        for i in range(4):
            napisy.append(QtGui.QLabel(self))
            napisy[i].move(30,300+i*40)
            napisy[i].setText("Pociag "+str(i+1))

            self.wejscia.append(QtGui.QLineEdit(self))
            self.wejscia[i].move(130, 300+i*40)

            self.przyciski.append(QtGui.QPushButton('Aktywuj '+str(i+1), self))
            self.przyciski[i].move(275, 300+i*40)
            self.przyciski[i].clicked.connect(self.buttonClicked)

            self.ost.append(1)

        for i in range(48):
            self.czujniki.append(Czujnik(i,1,1))
        self.wczytaj_wspolrzedne()

        for i in range(4):
            self.miejsca.append(QtGui.QLabel(self))
            self.miejsca[i].move(self.czujniki[i+1].x, self.czujniki[i+1].y)
            self.wejscia[i].setText(str(i+1))
            self.ost.append(i+1)
        self.miejsca[0].setPixmap(czerwony)
        self.miejsca[1].setPixmap(zielony)
        self.miejsca[2].setPixmap(czarny)
        self.miejsca[3].setPixmap(rozowy)

        self.setGeometry(10, 30, 1200, 540)
        self.setWindowTitle('Zapal_czujnik')
        self.setWindowIcon(QtGui.QIcon('my_icon.png'))
        self.show()

    def buttonClicked(self):

        zrodlo = self.sender()
        nr_wejscia = zrodlo.text()
        nr_wejscia = nr_wejscia[len(nr_wejscia)-1]
        nr_wejscia = int(nr_wejscia)-1
        nr = int(self.wejscia[nr_wejscia].text())
        if nr != self.ost[nr_wejscia]:
            for i in range(1,45):
                if self.czujniki[i].nr == self.ost[nr_wejscia]:
                    self.czujniki[i].isActive = False
                    self.ost[nr_wejscia] = nr
                if self.czujniki[i].nr == nr:
                    self.czujniki[i].isActive = True
                    self.miejsca[nr_wejscia].move(self.czujniki[i].x, self.czujniki[i].y)

    def wczytaj_wspolrzedne(self):
        self.czujniki[1].x = 1148
        self.czujniki[1].y = 3
        self.czujniki[2].x = 1031
        self.czujniki[2].y = 5
        self.czujniki[3].x = 433
        self.czujniki[3].y = 14
        self.czujniki[4].x = 3
        self.czujniki[4].y = 23
        self.czujniki[5].x = 433
        self.czujniki[5].y = 21
        self.czujniki[6].x = 838
        self.czujniki[6].y = 11
        self.czujniki[7].x = 865
        self.czujniki[7].y = 12
        self.czujniki[8].x = 895
        self.czujniki[8].y = 12
        self.czujniki[9].x = 920
        self.czujniki[9].y = 12
        self.czujniki[10].x = 949
        self.czujniki[10].y = 13
        self.czujniki[11].x = 974
        self.czujniki[11].y = 13
        self.czujniki[12].x = 1039
        self.czujniki[12].y = 12
        self.czujniki[13].x = 1165
        self.czujniki[13].y = 11
        self.czujniki[14].x = 1031
        self.czujniki[14].y = 19
        self.czujniki[15].x = 716
        self.czujniki[15].y = 84
        self.czujniki[16].x = 723
        self.czujniki[16].y = 203
        self.czujniki[17].x = 807
        self.czujniki[17].y = 374
        self.czujniki[18].x = 957
        self.czujniki[18].y = 379
        self.czujniki[19].x = 624
        self.czujniki[19].y = 499
        self.czujniki[20].x = 708
        self.czujniki[20].y = 98
        self.czujniki[21].x = 535
        self.czujniki[21].y = 47
        self.czujniki[22].x = 3
        self.czujniki[22].y = 48
        self.czujniki[23].x = 535
        self.czujniki[23].y = 55
        self.czujniki[24].x = 1164
        self.czujniki[24].y = 41
        self.czujniki[25].x = 1000
        self.czujniki[25].y = 45
        self.czujniki[26].x = 962
        self.czujniki[26].y = 47
        self.czujniki[27].x = 917
        self.czujniki[27].y = 54
        self.czujniki[28].x = 732
        self.czujniki[28].y = 200
        self.czujniki[29].x = 815
        self.czujniki[29].y = 369
        self.czujniki[30].x = 963
        self.czujniki[30].y = 386
        self.czujniki[31].x = 624
        self.czujniki[31].y = 508
        self.czujniki[32].x = 917
        self.czujniki[32].y = 47
        self.czujniki[33].x = 1033
        self.czujniki[33].y = 41
        self.czujniki[34].x = 1075
        self.czujniki[34].y = 34
        self.czujniki[35].x = 1180
        self.czujniki[35].y = 33
        self.czujniki[36].x = 1037
        self.czujniki[36].y = 32
        self.czujniki[37].x = 1180
        self.czujniki[37].y = 24
        self.czujniki[38].x = 1082
        self.czujniki[38].y = 29
        self.czujniki[39].x = 1026
        self.czujniki[39].y = 28
        self.czujniki[40].x = 975
        self.czujniki[40].y = 33
        self.czujniki[41].x = 1074
        self.czujniki[41].y = 24
        self.czujniki[42].x = 1098
        self.czujniki[42].y = 21
        self.czujniki[43].x = 1139
        self.czujniki[43].y = 17
        self.czujniki[44].x = 1129
        self.czujniki[44].y = 20
        self.czujniki[45].x = 443
        self.czujniki[45].y = 28
        self.czujniki[46].x = 433
        self.czujniki[46].y = 35

def main():

    app = QtGui.QApplication(sys.argv)
    okno = Okno()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
