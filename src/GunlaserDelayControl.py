'''
Created on 19 dec 2014

@author: Filip Lindau
'''
# -*- coding:utf-8 -*-
from PyQt4 import QtGui, QtCore

import time
import sys




class TangoDeviceClient(QtGui.QWidget):
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self,parent)
#        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.delayDict = {'A': None, 'B': None, 'C': None, 'D': None, 'E': None, 'F': None, 'G': None, 'H': None}
        self.linkDict = {'A': None, 'B': None, 'C': None, 'D': None, 'E': None, 'F': None, 'G': None, 'H': None}
        self.prescalerDict = {'AB': None, 'CD': None, 'EF': None, 'GH': None}

        self.setupLayout()

        splash.showMessage('         Initializing devices', alignment = QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
        app.processEvents()

        t0=time.clock()
        self.devices = {}
        self.devices['dg645']=pt.DeviceProxy('gunlaser/devices/delaygenerator')
        print time.clock()-t0, ' s'

        splash.showMessage('         Reading startup attributes', alignment = QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
        app.processEvents()


        self.guiLock = threading.Lock()
        self.attributes = {}
        self.attributes['dgState'] = AttributeClass('state', self.devices['dg645'], 0.3)
        self.attributes['dgState'].attrSignal.connect(self.readDGState)
        for name in self.delayDict.keys():
            self.attributes[''.join((name, 'Delay'))] = AttributeClass(''.join((name, 'Delay')), self.devices['dg645'], 0.5)
            self.attributes[''.join((name, 'Delay'))].attrSignal.connect(self.readDelay)
            self.attributes[''.join((name, 'DelayLink'))] = AttributeClass(''.join((name, 'DelayLink')), self.devices['dg645'], 0.5)
            self.attributes[''.join((name, 'DelayLink'))].attrSignal.connect(self.readLink)
        for name in self.prescalerDict.keys():
            self.attributes[''.join((name, 'PrescaleFactor'))] = AttributeClass(''.join((name, 'PrescaleFactor')), self.devices['dg645'], 0.5)
            self.attributes[''.join((name, 'PrescaleFactor'))].attrSignal.connect(self.readPrescaleFactor)

        splash.showMessage('         Setting up variables', alignment = QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
        app.processEvents()


    def readDelay(self, data):
        self.positionWidget.setAttributeValue(data)

        data.value = 100*np.cos(2*data.value*np.pi/180.0)**4
        data.w_value = 100*np.cos(2*data.w_value*np.pi/180.0)**4
        self.energyWidget.setAttributeValue(data)

    def writeDelay(self):
        print "in writeDelay::"
        with self.guiLock:
            energy = self.energyWidget.getWriteValue()
            print "energy: ", energy
            if energy > 100:
                energy = 100
            elif energy < 0:
                energy = 0
            w = np.arccos((energy/100.0)**0.25)*90/np.pi
            self.attributes['position'].attr_write(w)

    def readDGState(self, data):
        self.waveplateName.setState(data)
        data.value = ''
        self.waveplateWidget.setStatus(data)



    def setupAttributeLayout(self, attributeList = []):
        self.attributeQObjects = []
        for att in attributeList:
            attQObject = qw.QTangoReadAttributeDouble()
            attQObject.setAttributeName(att.name)
            self.attributeQObjects.append(attQObject)
            self.layoutAttributes.addWidget(attQObject)

    def closeEvent(self, event):
#         for device in self.devices.itervalues():
#             device.terminate()
        for a in self.attributes.itervalues():
            print 'Stopping', a.name
            a.stopRead()
        for a in self.attributes.itervalues():
            a.readThread.join()
        event.accept()

    def setupLayout(self):
        s='QWidget{background-color: #000000; }'
        self.setStyleSheet(s)

        self.frameSizes = qw.QTangoSizes()
        self.frameSizes.barHeight = 20
        self.frameSizes.barWidth = 18
        self.frameSizes.readAttributeWidth = 250
        self.frameSizes.writeAttributeWidth = 150
        self.frameSizes.fontStretch= 80
        self.frameSizes.fontType = 'Segoe UI'
#        self.frameSizes.fontType = 'Trebuchet MS'

        self.attrSizes = qw.QTangoSizes()
        self.attrSizes.barHeight = 22
        self.attrSizes.barWidth = 18
        self.attrSizes.readAttributeWidth = 250
        self.attrSizes.readAttributeHeight = 250
        self.attrSizes.writeAttributeWidth = 299
        self.attrSizes.fontStretch= 80
        self.attrSizes.fontType = 'Segoe UI'
#        self.attrSizes.fontType = 'Trebuchet MS'


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
        spacerItemV = QtGui.QSpacerItem(20, 5, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.MinimumExpanding)
        spacerItemBar = QtGui.QSpacerItem(self.frameSizes.barWidth, self.frameSizes.barHeight+8, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        spacerItemH = QtGui.QSpacerItem(20, 5, QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Minimum)

        layoutData = QtGui.QHBoxLayout()
        layoutData.setMargin(self.attrSizes.barHeight/2)
        layoutData.setSpacing(self.attrSizes.barHeight*2)
        self.layoutAttributes = QtGui.QVBoxLayout()
        self.layoutAttributes.setMargin(0)
        self.layoutAttributes.setSpacing(self.attrSizes.barHeight/2)
        self.layoutAttributes.setContentsMargins(0, 0, 0, 0)

#         self.layoutAttributes2 = QtGui.QVBoxLayout()
#         self.layoutAttributes2.setMargin(0)
#         self.layoutAttributes2.setSpacing(self.attrSizes.barHeight/2)
#         self.layoutAttributes2.setContentsMargins(0, 0, 0, 0)
#
#         self.layoutAttributes3 = QtGui.QVBoxLayout()
#         self.layoutAttributes3.setMargin(0)
#         self.layoutAttributes3.setSpacing(self.attrSizes.barHeight/2)
#         self.layoutAttributes3.setContentsMargins(0, 0, 0, 0)

        self.title = qw.QTangoTitleBar('Delay control')
        self.setWindowTitle('Delay control')
        self.sidebar = qw.QTangoSideBar(colors = self.colors, sizes = self.frameSizes)
        self.bottombar = qw.QTangoHorizontalBar()

        self.dgName = qw.QTangoDeviceNameStatus(colors = self.colors, sizes = self.frameSizes)
        self.dgName.setAttributeName('Delay generator')

        self.attrSizes.readAttributeHeight = 250
        self.positionWidget = qw.QTangoReadAttributeSliderV(colors = self.colors, sizes = self.attrSizes)
        self.positionWidget.setAttributeName('Pos', 'deg')
        self.positionWidget.setAttributeWarningLimits([-10, 370])
        self.positionWidget.setSliderLimits(0, 50)

        self.energyWidget = qw.QTangoWriteAttributeSliderV(colors = self.colors, sizes = self.attrSizes)
        self.energyWidget.setAttributeName('Energy', '%')
        self.energyWidget.setSliderLimits(0, 100)
        self.energyWidget.setAttributeWarningLimits([-1, 110])
        self.energyWidget.writeValueLineEdit.editingFinished.connect(self.writePosition)



        layout2.addWidget(self.title)
        layout2.addLayout(layoutData)
        layoutData.addLayout(self.layoutAttributes)
#        layoutData.addSpacerItem(spacerItemH)
#        layoutData.addLayout(self.layoutAttributes2)
#        layoutData.addLayout(self.layoutAttributes3)

        self.layoutAttributes.addWidget(self.waveplateName)
        self.layoutAttributes.addSpacerItem(spacerItemV)

        layoutSliders = QtGui.QHBoxLayout()
        layoutSliders.addWidget(self.energyWidget)
        layoutSliders.addWidget(self.positionWidget)
        self.layoutAttributes.addLayout(layoutSliders)
#        self.layoutAttributes2.addSpacerItem(spacerItemV)



        layout1.addWidget(self.sidebar)
        layout1.addLayout(layout2)
        layout0.addLayout(layout1)
#        layout0.addWidget(self.bottombar)

#        self.resize(500,800)
        self.setGeometry(200,100,300,500)

        self.update()

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    splash_pix = QtGui.QPixmap('splash_tangoloading.png')
    splash = QtGui.QSplashScreen(splash_pix, QtCore.Qt.WindowStaysOnTopHint)
    splash.setMask(splash_pix.mask())
    splash.show()
    splash.showMessage('         Importing modules', alignment = QtCore.Qt.AlignBottom | QtCore.Qt.AlignLeft, color = QtGui.QColor('#66cbff'))
    app.processEvents()

    import QTangoWidgets.QTangoWidgets as qw
    from QTangoWidgets.AttributeReadThreadClass import AttributeClass
    import pyqtgraph as pg
    import PyTango as pt
    import threading
    import numpy as np

    splash.showMessage('         Starting GUI', alignment = QtCore.Qt.AlignBottom | QtCore.Qt.AlignLeft, color = QtGui.QColor('#66cbff'))
    app.processEvents()
    myapp = TangoDeviceClient()
    myapp.show()
    splash.finish(myapp)
    sys.exit(app.exec_())