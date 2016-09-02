'''
Created on 14 aug 2014

@author: Filip
'''
# -*- coding:utf-8 -*-

from PyQt4 import QtGui, QtCore

import time
import sys


class TangoDeviceClient(QtGui.QWidget):
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self,parent)
#        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

        self.devName = 'gunlaser/cameras/cam0'

        self.setupLayout()

        splash.showMessage('       Initializing devices', alignment = QtCore.Qt.AlignBottom | QtCore.Qt.AlignLeft, color = QtGui.QColor('#66cbff'))
        app.processEvents()

        t0=time.clock()
        self.devices = {}
        self.devices['camera']=pt.DeviceProxy(self.devName)
        print time.clock()-t0, ' s'

        splash.showMessage('       Reading startup attributes... LeeLaser', alignment = QtCore.Qt.AlignBottom | QtCore.Qt.AlignLeft, color = QtGui.QColor('#66cbff'))
        app.processEvents()


        self.attributes = {}

        self.attributes['shutter'] = AttributeClass('shutter', self.devices['camera'], 0.3)
        self.attributes['gain'] = AttributeClass('gain', self.devices['camera'], 0.3)
        self.attributes['image'] = AttributeClass('image', self.devices['camera'], 0.3)
        self.attributes['state'] = AttributeClass('state', self.devices['camera'], 0.3)

        self.attributes['shutter'].attrSignal.connect(self.readShutter)
        self.attributes['gain'].attrSignal.connect(self.readGain)
        self.attributes['image'].attrSignal.connect(self.readImage)
        self.attributes['state'].attrSignal.connect(self.readState)


        splash.showMessage('       Setting up variables', alignment = QtCore.Qt.AlignBottom | QtCore.Qt.AlignLeft, color = QtGui.QColor('#66cbff'))
        app.processEvents()

    def readShutter(self, data):
        self.shutterWidget.setAttributeValue(data)

    def writeShutter(self):
        w = self.shutterWidget.getWriteValue()
        self.attributes['shutter'].attr_write(w)

    def readGain(self, data):
        self.gainWidget.setAttributeValue(data)

    def writeGain(self):
        w = self.gainWidget.getWriteValue()
        self.attributes['gain'].attr_write(w)

    def readState(self, data):
        self.cameraName.setState(data)

    def readImage(self, data):
        self.imageWidget.setImage(data)

    def closeEvent(self, event):
#         for device in self.devices.itervalues():
#             device.terminate()
        for a in self.attributes.itervalues():
            print 'Stopping', a.name
            a.stopRead()
            a.readThread.join()
        print 'All stopped.'
        print 'Sending close event'
        super(TangoDeviceClient, self).closeEvent(event)
        print 'Exiting'
#        event.accept()

    def setupLayout(self):
        s='QWidget{background-color: #000000; }'
        self.setStyleSheet(s)

        self.frameSizes = qw.QTangoSizes()
        self.frameSizes.readAttributeWidth = 200
        self.frameSizes.writeAttributeWidth = 150
        self.frameSizes.barHeight = 30
        self.frameSizes.barWidth = 20
        self.frameSizes.fontStretch= 80
        self.frameSizes.fontType = 'Segoe UI'
#        self.frameSizes.fontType = 'Trebuchet MS'
        self.attrSizes = qw.QTangoSizes()
        self.attrSizes.barHeight = 20
        self.attrSizes.barWidth = 20
        self.attrSizes.readAttributeWidth = 300
        self.attrSizes.writeAttributeWidth = 300
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
        spacerItemV = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.MinimumExpanding)
        spacerItemH = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Minimum)

        layoutData = QtGui.QHBoxLayout()
        layoutData.setMargin(self.attrSizes.barHeight/2)
        layoutData.setSpacing(self.attrSizes.barHeight/2)
        self.layoutAttributes = QtGui.QVBoxLayout()
        self.layoutAttributes.setMargin(0)
        self.layoutAttributes.setSpacing(self.attrSizes.barHeight/2)
        self.layoutAttributes.setContentsMargins(0, 0, 0, 0)

        self.title = qw.QTangoTitleBar(self.devName)
        self.setWindowTitle(self.devName)
        self.title.startLabel.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
#        self.sidebar = qw.QTangoSideBar(colors = self.colors, sizes = self.frameSizes)
        self.bottombar = qw.QTangoHorizontalBar()

        self.cameraName = qw.QTangoDeviceNameStatus(colors = self.colors, sizes = self.frameSizes)
        self.cameraName.setAttributeName('Camera')


        self.shutterWidget = qw.QTangoWriteAttributeSlider(colors = self.colors, sizes = self.attrSizes)
        self.shutterWidget.setAttributeName('Shutter', 'ms')
        self.shutterWidget.setAttributeWarningLimits([0, 1000])
        self.shutterWidget.setSliderLimits(0, 40)
        self.shutterWidget.writeValueSpinbox.editingFinished.connect(self.writeShutter)

        self.gainWidget = qw.QTangoWriteAttributeSlider(colors = self.colors, sizes = self.attrSizes)
        self.gainWidget.setAttributeName('Gain', 'dB')
        self.gainWidget.setAttributeWarningLimits([0, 1000])
        self.gainWidget.setSliderLimits(0, 12)
        self.gainWidget.writeValueSpinbox.editingFinished.connect(self.writeGain)

        self.imageWidget = qw.QTangoReadAttributeImage()
        self.imageWidget.setAttributeName('Image')
        self.imageWidget.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)


        layout2.addWidget(self.title)
        layout2.addLayout(layoutData)
        layoutData.addLayout(self.layoutAttributes)
        layoutData.addWidget(self.imageWidget)
 #       layoutData.addSpacerItem(spacerItemH)

        self.layoutAttributes.addWidget(self.cameraName)
        self.layoutAttributes.addSpacerItem(spacerItemV)
        self.layoutAttributes.addWidget(self.gainWidget)
        self.layoutAttributes.addWidget(self.shutterWidget)

        layout0.addLayout(layout2)
        layout0.addWidget(self.bottombar)

        self.setGeometry(200,100,600,350)

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
    from QTangoWidgets.AttributeReadThreadClass import AttributeClass
    import pyqtgraph as pg
    import PyTango as pt
    import threading
    import numpy as np

    splash.showMessage('       Starting GUI', alignment = QtCore.Qt.AlignBottom | QtCore.Qt.AlignLeft, color = QtGui.QColor('#66cbff'))
    app.processEvents()
    myapp = TangoDeviceClient()
    myapp.show()
    splash.finish(myapp)
    sys.exit(app.exec_())
