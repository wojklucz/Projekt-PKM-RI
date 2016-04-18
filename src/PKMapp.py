# coding=utf-8
"""
Main application in our solution.
"""

import terminal
from loadData import *
from PyQt4 import uic
from PyQt4.QtGui import QMainWindow, QApplication, QTableWidgetItem, QPushButton
import functools

typeDict = {'00': 'None',
            '01': 'Switcher',
            '02': 'Wigwag',
            '03': 'Balisa',
            '04': 'Multiswitcher'}

class PKMwin(QMainWindow):

    terminale = None
    balisesLst = []
    switchersLst = []
    dataLoaded = dataLoader()
    dataLoaded.load()
    balisesLst = dataLoaded.balisesLst
    switchersLst = dataLoaded.switchersLst

    def __init__(self):
        QMainWindow.__init__(self)
        uic.loadUi('PKMInterface.ui', self)
        self.lastWidth = self.width()
        self.lastHeight = self.height()
        try:
            self.terminale = terminal.CommunicationModule('COM6', 500000, 'N')
            self.printFromConsole("Terminal configured")
        except:
            self.printFromConsole("No terminal")

        if self.terminale:
            self.terminale.start()
            for bal in self.balisesLst:
                self.terminale.writeCommand(bal.setINT0(1))

            for swi in self.switchersLst:
                self.terminale.writeCommand(swi.switchRight())
                sleep(0.1)
                self.terminale.writeCommand(swi.powerOff())

        if self.terminale:
            self.scanAll()
        self.switchTable.setRowCount(0)
        self.baliseTable.setRowCount(0)
        self.reloadBalisesTable()
        self.reloadSwitchersTable()


        #------------------Insert map widget------------
        #self.horizontalLayout.addWidget(???)
        #===============================================


        self.resizeEvent = (lambda old_method: (lambda event: (self._on_resized(event), old_method(event))[-1]))(self.resizeEvent)
        self.baliseTable.resizeColumnsToContents()
        self.switchTable.resizeColumnsToContents()
        if self.terminale:
            QObject.connect(self.terminale, SIGNAL("balisa_int"), self.balisaInterrupt)
        pass

    def printFromConsole(self, text):
        self.comField.setText(self.comField.toPlainText() + text + '\n')

    def _on_resized(self,event):
        widthDif = self.width() - self.lastWidth
        heightDif = self.height() - self.lastHeight
        self.switchLabel.move(self.switchLabel.pos().x()+widthDif,self.switchLabel.pos().y())
        self.switchTable.move(self.switchTable.pos().x()+widthDif,self.switchTable.pos().y())
        self.switchTable.resize(self.switchTable.width(),self.switchTable.height()+heightDif)
        self.baliseLabel.move(self.baliseLabel.pos().x()+widthDif,self.baliseLabel.pos().y())
        self.baliseTable.move(self.baliseTable.pos().x()+widthDif,self.baliseTable.pos().y())
        self.baliseTable.resize(self.baliseTable.width(),self.baliseTable.height()+heightDif)
        self.comField.move(self.comField.pos().x(),self.comField.pos().y()+heightDif)
        self.comField.resize(self.comField.width()+widthDif,self.comField.height())
        self.lastWidth = self.width()
        self.lastHeight = self.height()

    def reloadBalisesTable(self):
        self.baliseTable.setRowCount(0)
        row = 0
        for b in self.balisesLst:
            self.baliseTable.insertRow(row)
            item = QTableWidgetItem()
            item.setText(b.deviceNo.__str__())
            self.baliseTable.setItem(row,0,item)
            item2 = QTableWidgetItem()
            if b.state['int0']:
                t = "On"
            else:
                t = "Off"
            item2.setText(t)
            self.baliseTable.setItem(row,1,item2)
            item3 = QTableWidgetItem()
            item3.setText(b.zone)
            self.baliseTable.setItem(row,2,item3)
            row = row + 1

    def reloadSwitchersTable(self):
        self.switchTable.setRowCount(0)
        row = 0
        for s in self.switchersLst:
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
        for el in self.switchersLst:
            if switch.compare(el):
                if self.terminale:
                    self.terminale.writeCommand(el.switch())
                    sleep(0.1)
                    self.terminale.writeCommand(el.powerOff())
                break

        self.reloadSwitchersTable()
        self.printFromConsole("SWITCHER CHANGED")

    def reloadStatus(self):
        self.reloadBalisesTable()
        self.reloadSwitchersTable()

    def scanAll(self):
        if self.terminale:
            (sLst, wLst, bLst) = self.terminale.scanElements()
            for bal in bLst:
                for BALISE in self.balisesLst:
                    if bal.compare(BALISE):
                        BALISE.state = bal.state
                        break
            for swi in sLst:
                for SWITCH in self.switchersLst:
                    if swi.compare(SWITCH):
                        SWITCH.setState(swi.state)
                        break
        else:
            self.printFromConsole('No terminal')

    def balisaInterrupt(self, bal):
        for balisa in self.balisesLst:
            if balisa.compare(bal):
                balisa.state = bal.state
                self.switchTable.setRowCount(0)
                self.baliseTable.setRowCount(0)
                self.reloadBalisesTable()
                self.reloadSwitchersTable()
                if bal.state['int0']:
                    stan = 'True'
                else:
                    stan = 'False'
                self.printFromConsole('Balisa no '+str(bal.deviceNo)+' '+stan)
                break

if __name__ == '__main__':
    qApp = QApplication(sys.argv)
    mw = PKMwin()
    mw.show()
    # if PKMwin.terminale:
    #     PKMwin.terminale.stop()
    #     PKMwin.terminale.turnAgentsOff()
    sys.exit(qApp.exec_())

