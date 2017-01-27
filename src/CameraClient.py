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

        self.devName = 'gunlaser/cameras/spectrometer_camera'

        self.setupLayout()

        splash.showMessage('       Initializing devices', alignment = QtCore.Qt.AlignBottom | QtCore.Qt.AlignLeft, color = QtGui.QColor('#66cbff'))
        app.processEvents()

        t0=time.clock()
        self.devices = {}
        try:
            self.devices['camera']=pt.DeviceProxy(self.devName)
        except pt.DevFailed, e:
            print "Error starting camera", str(e)
        print time.clock()-t0, ' s'

        splash.showMessage('       Reading startup attributes... ', alignment = QtCore.Qt.AlignBottom | QtCore.Qt.AlignLeft, color = QtGui.QColor('#66cbff'))
        app.processEvents()


        self.attributes = {}

        self.attributes['shutter'] = AttributeClass('shutter', self.devices['camera'], 0.3)
        self.attributes['gain'] = AttributeClass('gain', self.devices['camera'], 0.3)
        self.attributes['image'] = AttributeClass('image', self.devices['camera'], 0.1)
        self.attributes['state'] = AttributeClass('state', self.devices['camera'], 0.3)

        self.attributes['shutter'].attrSignal.connect(self.readShutter)
        self.attributes['gain'].attrSignal.connect(self.readGain)
        self.attributes['image'].attrSignal.connect(self.readImage)
        self.attributes['state'].attrSignal.connect(self.readState)


        splash.showMessage('       Setting up variables', alignment = QtCore.Qt.AlignBottom | QtCore.Qt.AlignLeft, color = QtGui.QColor('#66cbff'))
        app.processEvents()

    def readShutter(self, data):
        self.shutter_widget.setAttributeValue(data)

    def writeShutter(self):
        w = self.shutter_widget.getWriteValue()
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

        self.frame_sizes = qw.QTangoSizes()
        self.frame_sizes.readAttributeWidth = 200
        self.frame_sizes.writeAttributeWidth = 150
        self.frame_sizes.barHeight = 30
        self.frame_sizes.barWidth = 20
        self.frame_sizes.fontStretch= 80
        self.frame_sizes.fontType = 'Segoe UI'
#        self.frame_sizes.fontType = 'Trebuchet MS'
        self.attr_sizes = qw.QTangoSizes()
        self.attr_sizes.barHeight = 20
        self.attr_sizes.barWidth = 20
        self.attr_sizes.readAttributeWidth = 200
        self.attr_sizes.writeAttributeWidth = 299
        self.attr_sizes.fontStretch= 80
        self.attr_sizes.fontType = 'Segoe UI'
#        self.attr_sizes.fontType = 'Trebuchet MS'


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
        layoutData.setMargin(self.attr_sizes.barHeight/2)
        layoutData.setSpacing(self.attr_sizes.barHeight/2)
        self.layout_attributes = QtGui.QVBoxLayout()
        self.layout_attributes.setMargin(0)
        self.layout_attributes.setSpacing(self.attr_sizes.barHeight/2)
        self.layout_attributes.setContentsMargins(0, 0, 0, 0)

        self.title = qw.QTangoTitleBar(self.devName)
        self.setWindowTitle(self.devName)
        self.title.startLabel.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
#        self.sidebar = qw.QTangoSideBar(colors = self.colors, sizes = self.frame_sizes)
        self.bottombar = qw.QTangoHorizontalBar()

        self.cameraName = qw.QTangoDeviceNameStatus(colors = self.colors, sizes = self.frame_sizes)
        self.cameraName.setAttributeName('Camera')


        self.shutter_widget = qw.QTangoWriteAttributeSlider(colors = self.colors, sizes = self.attr_sizes)
        self.shutter_widget.setAttributeName('Shutter', 'ms')
        self.shutter_widget.setAttributeWarningLimits([0, 1000])
        self.shutter_widget.setSliderLimits(0, 40)
        self.shutter_widget.writeValueSpinbox.editingFinished.connect(self.writeShutter)

        self.gainWidget = qw.QTangoWriteAttributeSlider(colors = self.colors, sizes = self.attr_sizes)
        self.gainWidget.setAttributeName('Gain', 'dB')
        self.gainWidget.setAttributeWarningLimits([0, 1000])
        self.gainWidget.setSliderLimits(0, 12)
        self.gainWidget.writeValueSpinbox.editingFinished.connect(self.writeGain)

        self.imageWidget = qw.QTangoReadAttributeImage()
        self.imageWidget.setAttributeName('Image')
        self.imageWidget.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)


        layout2.addWidget(self.title)
        layout2.addLayout(layoutData)
        layoutData.addLayout(self.layout_attributes)
        layoutData.addWidget(self.imageWidget)
 #       layoutData.addSpacerItem(spacerItemH)

        self.layout_attributes.addWidget(self.cameraName)
        self.layout_attributes.addSpacerItem(spacerItemV)
        self.layout_attributes.addWidget(self.gainWidget)
        self.layout_attributes.addWidget(self.shutter_widget)

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
