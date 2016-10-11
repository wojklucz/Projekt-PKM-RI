# coding=utf-8

from terminal import *
import xml.dom.minidom as md


class dataLoader():
    """
    Klasa odpowiadająca za załadowanie danych balis i zwrotnic z pliku config_al.xml .
    """
    def __init__(self):
        self.switchersLst =[]
        self.balisesLst = []

    def load(self):
        """
        Jedyna metoda klasy, ładuje dane z pliku do pól switchersLst i balisesLst.
        :return: None
        """

        fileName = "config_al.xml"

        tree = md.parse(fileName)
        tags = ['switcher', 'balisa']
        lst = [[], []]
        for i in range(2):
            for el in tree.getElementsByTagName(tags[i]):
                if i == 0:
                    element = Switcher()
                    orie = str(el.getAttribute('orientation'))
                    if orie:
                        element.orientation = int(orie)
                    else:
                        element.orientation = 0
                elif i == 1:
                    element = Balisa()
                element.deviceNo = int(str(el.getAttribute('address')))
                element.zone = unicode(el.getAttribute('zone'))
                element.mapPosition = (int(el.getAttribute('mapX')),
                                       int(el.getAttribute('mapY')))
                element.description = el.childNodes[0].nodeValue
                lst[i].append(element)
        self.switchersLst, self.balisesLst = lst