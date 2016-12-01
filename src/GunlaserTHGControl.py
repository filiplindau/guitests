'''
Created on 30 Aug 2016

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
        self.timeVector = None
        self.xData = None
        self.xDataTemp = None

        self.setupLayout()

        splash.showMessage('         Initializing devices', alignment = QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
        app.processEvents()

        t0=time.clock()
        self.devices = {}
        self.devices['waveplate']=pt.DeviceProxy('gunlaser/mp/waveplate')
        self.devices['camera']=pt.DeviceProxy('gunlaser/thg/camera')
        self.devices['redpitaya']=pt.DeviceProxy('gunlaser/devices/redpitaya3')
        self.devices['mirror_x']=pt.DeviceProxy('gunlaser/thg/mirror_x')
        self.devices['mirror_y']=pt.DeviceProxy('gunlaser/thg/mirror_y')
        print time.clock()-t0, ' s'

        splash.showMessage('         Reading startup attributes', alignment = QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
        app.processEvents()


        self.guiLock = threading.Lock()
        self.attributes = {}
        self.attributes['wp_position'] = AttributeClass('position', self.devices['waveplate'], 0.3)
        self.attributes['waveplateState'] = AttributeClass('state', self.devices['waveplate'], 0.3)
        self.attributes['wp_position'].attrSignal.connect(self.readWPPosition)
        self.attributes['waveplateState'].attrSignal.connect(self.readWaveplateState)

        self.attributes['x_position'] = AttributeClass('position', self.devices['mirror_x'], 0.3)
        self.attributes['x_position'].attrSignal.connect(self.readXPosition)
        self.attributes['y_position'] = AttributeClass('position', self.devices['mirror_y'], 0.3)
        self.attributes['y_position'].attrSignal.connect(self.readYPosition)

        self.attributes['image'] = AttributeClass('image', self.devices['camera'], 0.3)
        self.attributes['cameraState'] = AttributeClass('state', self.devices['camera'], 0.3)
        self.attributes['image'].attrSignal.connect(self.readImage)
        self.attributes['cameraState'].attrSignal.connect(self.readCameraState)

        self.attributes['energy'] = AttributeClass('measurementdata1', self.devices['redpitaya'], 0.3)
        self.attributes['energy'].attrSignal.connect(self.readEnergy)

        self.devices['camera'].command_inout('start')


        splash.showMessage('         Setting up variables', alignment = QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
        app.processEvents()

        self.positionOffset = 0.0

#         self.timer = QtCore.QTimer(self)
#         self.timer.timeout.connect(self.checkDevices)
#         self.timer.start(100)



    def checkDevices(self):
        for a in self.attributes.itervalues():
            pass
#            a.attr_read()

    def readWPPosition(self, data):
        self.positionWidget.setAttributeValue(data)

#        data.value = 100*np.cos(2*data.value*np.pi/180.0)**4
#        data.w_value = 100*np.cos(2*data.w_value*np.pi/180.0)**4
        data.value = 100*np.cos(2*data.value*np.pi/180.0)**3
        data.w_value = 100*np.cos(2*data.w_value*np.pi/180.0)**3
        self.energyWidget.setAttributeValue(data)

    def writePosition(self):
        print "in writePosition::"
        self.guiLock.acquire()
        energy = self.energyWidget.getWriteValue()
        print "energy: ", energy
        if energy > 100:
            energy = 100
        elif energy < 0:
            energy = 0
#        w = np.arccos((energy/100.0)**0.25)*90/np.pi
        w = np.arccos((energy/100.0)**0.33)*90/np.pi
        self.attributes['wp_position'].attr_write(w)
        self.guiLock.release()

    def readWaveplateState(self, data):
        self.waveplateName.setState(data)
        data.value = ''
        self.waveplateWidget.setStatus(data)

    def readEnergy(self, data):
        self.photodiodeEnergyWidget.setAttributeValue(data)

    def readXPosition(self, data):
        self.positionXWidget.setAttributeValue(data)

    def writeXPosition(self):
        self.guiLock.acquire()
        w = self.positionXWidget.getWriteValue()
        self.attributes['x_position'].attr_write(w)
        self.guiLock.release()

    def readYPosition(self, data):
        self.positionYWidget.setAttributeValue(data)

    def writeYPosition(self):
        self.guiLock.acquire()
        w = self.positionYWidget.getWriteValue()
        self.attributes['y_position'].attr_write(w)
        self.guiLock.release()

    def readImage(self, data):
        self.cameraWidget.setImage(data)

    def readCameraState(self, data):
        self.cameraName.setState(data)
        data.value = ''

    def initWaveplate(self):
        self.devices['waveplate'].command_inout('init')

    def stopWaveplate(self):
        self.devices['waveplate'].command_inout('stop')

    def setMaxWaveplate(self):
        self.devices['waveplate'].command_inout('defineposition', 0)


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
        self.attrSizes.barWidth = 25
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

        self.layoutAttributes2 = QtGui.QVBoxLayout()
        self.layoutAttributes2.setMargin(0)
        self.layoutAttributes2.setSpacing(self.attrSizes.barHeight/2)
        self.layoutAttributes2.setContentsMargins(0, 0, 0, 0)

        self.layoutAttributes3 = QtGui.QVBoxLayout()
        self.layoutAttributes3.setMargin(0)
        self.layoutAttributes3.setSpacing(self.attrSizes.barHeight/2)
        self.layoutAttributes3.setContentsMargins(0, 0, 0, 0)

        self.title = qw.QTangoTitleBar('THG control')
        self.setWindowTitle('THG control')
        self.sidebar = qw.QTangoSideBar(colors = self.colors, sizes = self.frameSizes)
        self.bottombar = qw.QTangoHorizontalBar()

        self.waveplateName = qw.QTangoDeviceNameStatus(colors = self.colors, sizes = self.frameSizes)
        self.waveplateName.setAttributeName('Waveplate')

        self.cameraName = qw.QTangoDeviceNameStatus(colors = self.colors, sizes = self.frameSizes)
        self.cameraName.setAttributeName('Camera')

        self.waveplateWidget = qw.QTangoCommandSelection('Waveplate', colors = self.colors, sizes = self.attrSizes)
        self.waveplateWidget.addCmdButton('Stop', self.stopWaveplate)
        self.waveplateWidget.addCmdButton('Set Max', self.setMaxWaveplate)


        self.attrSizes.readAttributeHeight = 250
        self.positionWidget = qw.QTangoReadAttributeSliderV(colors = self.colors, sizes = self.attrSizes)
        self.positionWidget.setAttributeName('Pos', 'deg')
        self.positionWidget.setAttributeWarningLimits([-10, 370])
        self.positionWidget.setSliderLimits(0, 50)

        self.energyWidget = qw.QTangoWriteAttributeSliderV(colors = self.colors, sizes = self.attrSizes)
        self.energyWidget.setAttributeName('Energy', '%')
        self.energyWidget.setSliderLimits(0, 100)
        self.energyWidget.setAttributeWarningLimits([-1, 110])
        self.energyWidget.writeValueLineEdit.newValueSignal.connect(self.writePosition)

        self.photodiodeEnergyWidget = qw.QTangoReadAttributeSliderV(colors = self.colors, sizes = self.attrSizes)
        self.photodiodeEnergyWidget.setAttributeName('Energy', 'uJ')
        self.photodiodeEnergyWidget.setAttributeWarningLimits([-10, 1000])
        self.photodiodeEnergyWidget.setSliderLimits(0, 800)

        self.positionXWidget = qw.QTangoWriteAttributeSliderV(colors = self.colors, sizes = self.attrSizes)
        self.positionXWidget.setAttributeName('x pos', 'mm')
        self.positionXWidget.setSliderLimits(-10, 25)
        self.positionXWidget.setAttributeWarningLimits([-11, 110])
        self.positionXWidget.writeValueLineEdit.newValueSignal.connect(self.writeXPosition)

        self.positionYWidget = qw.QTangoWriteAttributeSliderV(colors = self.colors, sizes = self.attrSizes)
        self.positionYWidget.setAttributeName('y pos', 'mm')
        self.positionYWidget.setSliderLimits(-10, 25)
        self.positionYWidget.setAttributeWarningLimits([-11, 110])
        self.positionYWidget.writeValueLineEdit.newValueSignal.connect(self.writeYPosition)

        self.cameraWidget = qw.QTangoReadAttributeImage()
        self.cameraWidget.setAttributeName('Image')
        self.cameraWidget.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

        layout2.addWidget(self.title)
        layout2.addLayout(layoutData)
        layoutData.addLayout(self.layoutAttributes)
#        layoutData.addSpacerItem(spacerItemH)
        layoutData.addLayout(self.layoutAttributes2)
        layoutData.addLayout(self.layoutAttributes3)

        self.layoutAttributes.addWidget(self.waveplateName)
        self.layoutAttributes.addWidget(self.waveplateWidget)
        self.layoutAttributes.addSpacerItem(spacerItemV)

        layoutSliders = QtGui.QHBoxLayout()
        layoutSliders.addWidget(self.energyWidget)
        layoutSliders.addWidget(self.positionWidget)
        layoutSliders.addWidget(self.photodiodeEnergyWidget)
        self.layoutAttributes.addLayout(layoutSliders)
#        self.layoutAttributes2.addSpacerItem(spacerItemV)

        layoutSliders2 = QtGui.QHBoxLayout()
        layoutSliders2.addWidget(self.positionXWidget)
        layoutSliders2.addWidget(self.positionYWidget)
        self.layoutAttributes2.addSpacerItem(spacerItemV)
        self.layoutAttributes2.addLayout(layoutSliders2)

        self.layoutAttributes3.addWidget(self.cameraName)
        self.layoutAttributes3.addWidget(self.cameraWidget)

        layout1.addWidget(self.sidebar)
        layout1.addLayout(layout2)
        layout0.addLayout(layout1)
#        layout0.addWidget(self.bottombar)

#        self.resize(500,800)
        self.setGeometry(200,100,1000,400)

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