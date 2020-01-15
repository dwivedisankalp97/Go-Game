import PyQt5
from PyQt5 import QtWidgets
from PyQt5.QtCore import *

# from board_components.mydesign import Ui_GO_OBSERVER
# importing our generated file
from PyQt5.QtWidgets import QApplication, QTableWidgetItem
from board_components.mydesign import Ui_GO_OBSERVER
from board_components.definitions import POINT_REGEX,BOARD_SIZE_X,BOARD_SIZE_Y
import re
import sys


class mywindow(QtWidgets.QMainWindow):


    def __init__(self):
        super(mywindow, self).__init__()
        self.closed=False
        self.ui = Ui_GO_OBSERVER()

        self.ui.setupUi(self)
        
    def update_Status(self,msg):
        self.ui.label_3.setText(msg)
        self.ui.label_3.adjustSize()
        QApplication.processEvents()

    def update_mode(self,msg):
        self.ui.label_13.setText(msg)
        self.ui.label_13.adjustSize()
        QApplication.processEvents()

    def update_winner(self,msg):
        msg=str(msg)
        self.ui.label_11.setText(msg)
        self.ui.label_11.adjustSize()
        QApplication.processEvents()



    def reset_table(self):
        for row in range(0,BOARD_SIZE_X) :
            for col in range(0,BOARD_SIZE_Y) :
                self.ui.tableWidget.setItem(row,col, QTableWidgetItem())
        QApplication.processEvents()

    def set_table(self,tab):
        # print("table")
        for row in range(0,BOARD_SIZE_X) :
            for col in range(0,BOARD_SIZE_Y) :
                item=QTableWidgetItem(tab[row][col])
                item.setTextAlignment(Qt.AlignCenter)
                # item.setTextCo()
                # if tab[row][col]=="W":
                #     item.setBackground(Qt.white)
                # elif tab[row][col]=="B":
                #     item.setBackground(Qt.black)
                # else:
                #     item.setBackground(Qt.red)

                # p = item.palette()
                # p.setColor(item.backgroundRole(), Qt.red)
                # item.setPalette(p)
                self.ui.tableWidget.setItem(row, col, item)

                # self.ui.tableWidget.setItem(row,col, QTableWidgetItem())
        QApplication.processEvents()

    def update_move(self,point):
        self.ui.label_7.setText(point)
        self.ui.label_7.adjustSize()
        QApplication.processEvents()

    def update_curr_players(self, msg):
        self.ui.label_17.setText(msg)
        self.ui.label_17.adjustSize()
        QApplication.processEvents()

    def update_player(self, msg):
        self.ui.label_5.setText (msg)
        self.ui.label_5.adjustSize()
        QApplication.processEvents()

    def update_total_player(self, msg):
        fin=""
        for i in range(0,len(msg)):
            fin=fin+" "+msg[i][0]
        self.ui.label_10.setText(fin)
        self.ui.label_10.adjustSize()
        QApplication.processEvents()

    def update_ranks(self, msg):
        msg=str(msg)
        self.ui.label_8.setText(msg)
        self.ui.label_8.adjustSize()
        QApplication.processEvents()

    def closeEvent(self,event):
        self.closed=True

