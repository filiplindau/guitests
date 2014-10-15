'''
Created on 13 aug 2014

@author: Filip
'''
# -*- coding:utf-8 -*-

from PyQt4 import QtGui, QtCore

import time
import sys

class TangoDeviceClient(QtGui.QWidget):
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self,parent)

        self.timeStr = time.strftime('%H : %M : %S ')

        self.setupLayout()

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.updateTime)
        self.timer.start(1000)

    def updateTime(self):
        self.timeStr = time.strftime('%H : %M : %S ')
        self.timeWidget.statusLabel.setText(self.timeStr)
        self.dateWidget.statusLabel.setText(time.strftime('%Y-%m-%d'))


    def setupLayout(self):
        s='QWidget{background-color: #000000; }'
        self.setStyleSheet(s)

        self.frameSizes = qw.QTangoSizes()
        self.frameSizes.readAttributeWidth = 300
        self.frameSizes.writeAttributeWidth = 150
        self.frameSizes.fontStretch= 80
        self.frameSizes.fontType = 'Segoe UI'

        self.attrSizes = qw.QTangoSizes()
        self.attrSizes.barHeight = 20
        self.attrSizes.barWidth = 20
        self.attrSizes.readAttributeWidth = 400
        self.attrSizes.writeAttributeWidth = 299
        self.attrSizes.fontStretch= 80
        self.attrSizes.fontType = 'Segoe UI'

        self.clockSizes = qw.QTangoSizes()
        self.clockSizes.barHeight = 70
        self.clockSizes.barWidth = 20
        self.clockSizes.readAttributeWidth = 400
        self.clockSizes.writeAttributeWidth = 299
        self.clockSizes.fontStretch= 80
        self.clockSizes.fontType = 'Segoe UI'


        self.colors = qw.QTangoColors()

        layout0 = QtGui.QVBoxLayout(self)
        layout0.setMargin(0)
        layout0.setSpacing(0)
        layout0.setContentsMargins(9, 9, 9, 9)

        layout1 = QtGui.QHBoxLayout()
        layout1.setMargin(0)
        layout1.setSpacing(0)
        layout1.setContentsMargins(-1, 0, 0, 0)

        layout2 = QtGui.QVBoxLayout()
        layout2.setMargin(0)
        layout2.setSpacing(0)
        layout2.setContentsMargins(-1, 0, 0, 0)
        spacerItemV = QtGui.QSpacerItem(20, 2, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.MinimumExpanding)
        spacerItemH = QtGui.QSpacerItem(2, 2, QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Minimum)

        layoutData = QtGui.QHBoxLayout()
#        layoutData.setMargin(self.attrSizes.barHeight/2)
        layoutData.setMargin(0)
        layoutData.setSpacing(self.attrSizes.barHeight/2)
        layoutData.setContentsMargins(0, 15, 0, 0)

        self.layoutAttributes = QtGui.QVBoxLayout()
        self.layoutAttributes.setMargin(0)
        self.layoutAttributes.setSpacing(self.attrSizes.barHeight/2)
        self.layoutAttributes.setContentsMargins(0, 0, 0, 0)

        self.title = qw.QTangoTitleBar('TIME')
        self.setWindowTitle('Clock')
        self.title.startLabel.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)

        self.timeWidget = qw.QTangoCommandSelection('', colors = self.colors, sizes = self.clockSizes)
        self.timeWidget.startLabel.setQuality('ATTR_VALID')
        self.timeWidget.endLabel.setQuality('ATTR_VALID')
#        self.timeWidget.nameLabel.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.dateWidget = qw.QTangoCommandSelection('', colors = self.colors, sizes = self.attrSizes)
        self.dateWidget.startLabel.setQuality('ATTR_VALID')
        self.dateWidget.endLabel.setQuality('ATTR_VALID')

        self.layoutAttributes.addWidget(self.timeWidget)
        self.layoutAttributes.addWidget(self.dateWidget)
        self.layoutAttributes.addSpacerItem(spacerItemV)

        layout2.addWidget(self.title)
        layout2.addLayout(layoutData)
        layoutData.addLayout(self.layoutAttributes)
        layoutData.addSpacerItem(spacerItemH)

        layout0.addLayout(layout2)

#        self.resize(500,800)
        self.setGeometry(600,100,400,100)

        self.update()


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    splash_pix = QtGui.QPixmap('splash_tangoloading.png')
    splash = QtGui.QSplashScreen(splash_pix, QtCore.Qt.WindowStaysOnTopHint)
    splash.setMask(splash_pix.mask())
    splash.show()
    splash.showMessage('       Importing modules', alignment = QtCore.Qt.AlignBottom | QtCore.Qt.AlignLeft, color = QtGui.QColor('#66cbff'))
    app.processEvents()

    import QTangoWidgets.QTangoWidgets as qw
#     import pyqtgraph as pg
#     import PyTango as pt
#     import threading
#     import numpy as np

    splash.showMessage('       Starting GUI', alignment = QtCore.Qt.AlignBottom | QtCore.Qt.AlignLeft, color = QtGui.QColor('#66cbff'))
    app.processEvents()
    myapp = TangoDeviceClient()
    myapp.show()
    splash.finish(myapp)
    sys.exit(app.exec_())