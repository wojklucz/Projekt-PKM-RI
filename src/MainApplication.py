# coding=utf-8
"""
Moduł zawierający główną aplikację wraz z GUI. Całość pisana na pythona 2.7
"""

from PyQt4 import uic,QtGui
from busControl import *
from PyQt4.QtGui import QMainWindow, QApplication, QTableWidgetItem, QPushButton, QPalette
import functools
import PKMMap
import trainCommunicator
import time

class PKMwindow(QMainWindow):
    """
    Klasa głównego okna prgramu. Interfejs graficzny jest wczytywany z pliku 'PKMInterface.ui'.
    """
    def __init__(self):
        QMainWindow.__init__(self)
        uic.loadUi('PKMInterface.ui', self)
        self.setWindowTitle('PKMapp')
        self.setWindowIcon(QtGui.QIcon('my_icon.png'))
        self.lastWidth = self.width()
        self.lastHeight = self.height()

        self.timeLapse = None
        launchTime = time.time()
        try:
            self.kom = trainCommunicator.TrainCommunicator()
            self.kom.connect('192.168.0.200', 5550)
            print "Trains connected."
        except:
            print "Can't connect to trains"

        self.controller = BusControl(self)
        self.switchTable.setRowCount(0)
        self.reloadSwitchersTable()

        launchTime = time.time() - launchTime
        print "Launching time: ",launchTime,"s."

        #------------------map widget------------
        self.rk = PKMMap.Map(self.controller,self.kom)
        self.rk.scaleObr = 0.5
        self.rk.plus()
        self.scrollArea.setWidget(self.rk)
        self.scrollArea.setBackgroundRole(QPalette.Dark)
        self.scrollArea.setWidgetResizable(True)
        self.rk.setFocus()
        #===============================================

        #dołączanie funkcji do przycisków
        self.trainSpeedButton.clicked.connect(self.trainButton)
        self.haltAllButton.clicked.connect(self.stopAll)
        self.backButton.clicked.connect(lambda: self.controlTrain("tyl"))
        self.haltButton.clicked.connect(lambda: self.controlTrain("stop"))
        self.forwardButton.clicked.connect(lambda: self.controlTrain("przod"))
        self.biggerButton.clicked.connect(self.biggerScreen)
        self.smallerButton.clicked.connect(self.smallerScreen)

        #inicjalizacja comboBox'ów
        trainNumbers = ['1','2','3','6']
        self.trainNoCombo.clear()
        self.trainNoCombo.addItems(trainNumbers)
        self.trainNoCombo.setCurrentIndex(0)

        self.resizeEvent = (lambda old_method: (lambda event: (self._on_resized(event), old_method(event))[-1]))(self.resizeEvent)
        self.switchTable.resizeColumnsToContents()

        #Odbieranie sygnału przerwania z balisy
        if self.controller.terminale:
            QObject.connect(self.controller.terminale, SIGNAL("balisa_int"), self.balisaInterrupt)
        pass

    def biggerScreen(self):
        """
        Przybliżenie mapy.
        :return: None
        """
        self.biggerButton.setEnabled(self.rk.plus())
        self.smallerButton.setEnabled(True)

    def smallerScreen(self):
        """
        Oddalanie mapy.
        :return: None
        """
        self.smallerButton.setEnabled(self.rk.minus())
        self.biggerButton.setEnabled(True)

    def controlTrain(self,dir):
        """
        Metoda powiązana z przyciskami "forward","backward" i "stop". Pozwala użytkownikowi na ustalenie który pociąg jak jeździ.
        Pociągi, do których ma zostać to zastosowane są oznaczone w checkBoksach: oneCheck, twoCheck, threeCheck.
        :param dir: jeden ze stringów 'przod','tyl','stop', które określają kierunek ruchu pociągu.
        :return: None
        """
        trainsChecks = []
        if self.oneCheck.isChecked(): trainsChecks.append(1)
        if self.twoCheck.isChecked(): trainsChecks.append(2)
        if self.threeCheck.isChecked(): trainsChecks.append(3)
        for trainNo in trainsChecks:
            try:
                self.kom.set_speed(trainNo,dir)
                if dir == 'stop':
                    self.rk.trains[trainNo-1][0].zahamujSie()
                elif dir == 'przod':
                    if self.rk.trains[trainNo-1][0].dir == 'backward':
                        self.rk.trains[trainNo-1][0].dir = 'forward'
                        self.rk.trains[trainNo-1][0].turnAround()
                    self.rk.trains[trainNo-1][0].ruszSie()
                elif dir == 'tyl':
                    if self.rk.trains[trainNo-1][0].dir == 'forward':
                        self.rk.trains[trainNo-1][0].dir = 'backward'
                        self.rk.trains[trainNo-1][0].turnAround()
                    self.rk.trains[trainNo-1][0].ruszSie()
            except:
                print("Not connected to train ",trainNo)

    def stopAll(self):
        """
        Nadanie wszystkim pociągom prędkości zerowej.
        :return: None
        """
        for trainNo in [1,2,3,6]:
            self.kom.set_speed(trainNo,"stop")
            try:
                self.rk.trains[trainNo-1][0].zahamujSie()
            except:
                pass

    def trainButton(self):
        """
        Pociągowi wskazanemu w polu trainNoCombo zostanie nadana prędkość wpisana w polu speedInput. Tylko do testów prędkości.
        :return: None
        """
        trainNo = int(self.trainNoCombo.currentText())
        speed = str(self.speedInput.text())
        self.kom.set_sped(trainNo,speed)

    def _on_resized(self,event):
        """
        Metoda zmieniająca rozmiary i położenie elementów przy zmianie wielkości okna.
        :param event: _on_resized
        :return: None
        """
        widthDif = self.width() - self.lastWidth
        heightDif = self.height() - self.lastHeight
        self.lastWidth = self.width()
        self.lastHeight = self.height()
        self.switchLabel.move(self.switchLabel.pos().x()+widthDif,self.switchLabel.pos().y())
        self.switchTable.move(self.switchTable.pos().x()+widthDif,self.switchTable.pos().y())
        self.switchTable.resize(self.switchTable.width(),self.switchTable.height()+heightDif)
        self.trainControlGroup.move(self.trainControlGroup.pos().x(),self.trainControlGroup.pos().y()+heightDif)
        self.trainControlGroup.resize(self.trainControlGroup.width()+widthDif,self.trainControlGroup.height())
        self.scrollArea.resize(self.scrollArea.width()+widthDif,self.scrollArea.height()+heightDif)
        self.haltAllButton.move(self.haltAllButton.pos().x()+widthDif,self.haltAllButton.pos().y()+heightDif)
        self.mapControlGroup.move(self.mapControlGroup.pos().x() + widthDif,self.mapControlGroup.pos().y() + heightDif)
        self.customSpeedBox.move(self.customSpeedBox.pos().x() + widthDif,self.customSpeedBox.pos().y() + heightDif)
        self.rk.show()

    def reloadSwitchersTable(self):
        """
        Załadowanie stanów zwrotnic do tabeli ze zwrotnicami.
        :return: None
        """
        self.switchTable.setRowCount(0)
        row = 0
        for s in self.controller.switchersLst:
            self.switchTable.insertRow(row)
            btn = QPushButton(self.switchTable)
            btn.setText('.')
            btn.setMaximumWidth(30)
            btn.clicked.connect(functools.partial(self.changeSwitcher, s))
            self.switchTable.setCellWidget(row, 0, btn)
            item = QTableWidgetItem()
            item.setText(s.deviceNo.__str__())
            self.switchTable.setItem(row,1,item)
            item2 = QTableWidgetItem()
            item2.setText(s.state.__str__())
            self.switchTable.setItem(row,2,item2)
            item3 = QTableWidgetItem()
            item3.setText(s.zone)
            self.switchTable.setItem(row,3,item3)
            row = row + 1

    def changeSwitcher(self,switch):
        """
        Zmiana pozycji zwrotnicy. Uaktualnia stan w tabeli zwrotnic i na mapie.
        :param switch: obiekt klasy Switcher
        :return: None
        """
        self.controller.changeSwitcher(switch)
        self.rk.switchSwitcherOnlyOnMap(BusControl.invMapNumToDevNoAndZoneDict[(switch.deviceNo,switch.zone)])
        self.updateSwitcherTable(switch)

    def balisaInterrupt(self, bal):
        """
        Reakcja na przerwanie od balisy. Zapala balisę na mapie i aktywuje nastawy powiązane z tą balisą (jelśi są).
        :param bal: obiekt klasy Balisa.
        :return: None
        """
        czid, myT = self.rk.aktywacjaCzujnika(bal.deviceNo,bal.zone[0])
        if not self.rk.czujniki[czid].timeout == 0:
            return
        if not self.rk.czujniki[czid].Aktywny:
            self.rk.zastosujNastawy(czid, myT)
        if czid == 4:
            if self.rk.czujniki[czid].Aktywny:
                self.rk.ustawHamowanie(czid)
        if not self.rk.czujniki[czid].Aktywny:
            self.rk.ustawHamowanie(czid)
        if bal.deviceNo == 603:
            print time.time()
            if self.timeLapse == None:
                self.timeLapse = time.time()
            else:
                self.timeLapse = time.time() - self.timeLapse
                print "Time: ",self.timeLapse
                self.timeLapse = None
        print "Aktywacja balisy: ",(bal.deviceNo,bal.zone[0])
        if (bal.deviceNo == 301 and bal.zone[0] == u'B') or (bal.deviceNo == 501 and bal.zone[0] == u'W'):
            self.rk.czujniki[czid].timeout = time.time() + 0.05
        else:
            self.rk.czujniki[czid].timeout = time.time() + 0.5


    def updateSwitcherTable(self,sw):
        """
        Uaktualnienie wiersza w tabeli zwrotnic odnoszącego sie do wskazanej zwotnicy.
        :param sw: obiekt klasy Switcher
        :return: None
        """
        rows = self.switchTable.rowCount()
        for i in range(0,rows,1):
            if int(self.switchTable.item(i, 1).text()) == sw.deviceNo and sw.zone == self.switchTable.item(i, 3).text():
                item2 = QTableWidgetItem()
                item2.setText(sw.state.__str__())
                self.switchTable.setItem(i,2,item2)
                break
        print("SWITCHER CHANGED")

if __name__ == '__main__':
    #uruchomienie programu
    qApp = QApplication(sys.argv)
    mw = PKMwindow()
    mw.show()
    sys.exit(qApp.exec_())

