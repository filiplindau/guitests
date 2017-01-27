'''
Created on 19 aug 2014

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
        self.timeVector = None
        self.xData = None
        self.xDataTemp = None

        self.setupLayout()

        splash.showMessage('         Initializing devices', alignment = QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
        app.processEvents()

        t0=time.clock()
        self.devices = {}
        self.devices['leelaser']=pt.DeviceProxy('gunlaser/mp/leelaser')
        self.devices['ionpump']=pt.DeviceProxy('gunlaser/mp/ionpump')
        self.devices['temperature']=pt.DeviceProxy('gunlaser/mp/temperature')
        self.devices['spectrometer']=pt.DeviceProxy('gunlaser/mp/spectrometer')
        print time.clock()-t0, ' s'

        splash.showMessage('         Reading startup attributes', alignment = QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
        app.processEvents()


        self.guiLock = threading.Lock()
        self.attributes = {}
        self.attributes['leelasercurrent'] = AttributeClass('current', self.devices['leelaser'], 0.3)
        self.attributes['leelaserpercentcurrent'] = AttributeClass('percentcurrent', self.devices['leelaser'], 0.3)
        self.attributes['leelaserstatus'] = AttributeClass('status', self.devices['leelaser'], 0.3)
        self.attributes['leelaserstate'] = AttributeClass('state', self.devices['leelaser'], 0.3)
        self.attributes['leelasershutterstate'] = AttributeClass('shutterstate', self.devices['leelaser'], 0.3)
        self.attributes['leelaseroperationstate'] = AttributeClass('laserstate', self.devices['leelaser'], 0.3)

        self.attributes['leelasercurrent'].attrSignal.connect(self.readLeeLaserCurrent)
        self.attributes['leelaserpercentcurrent'].attrSignal.connect(self.readLeeLaserPercentCurrent)
        self.attributes['leelasershutterstate'].attrSignal.connect(self.readLeeLaserShutterState)
        self.attributes['leelaserstate'].attrSignal.connect(self.readLeeLaserState)
        self.attributes['leelaseroperationstate'].attrSignal.connect(self.readLeeLaserOperationState)


# Ionpump
        self.attributes['ionpumppressure'] = AttributeClass('pressure', self.devices['ionpump'], 0.3)

        self.attributes['ionpumppressure'].attrSignal.connect(self.readIonpumpPressure)

# Temperature
        self.attributes['crystaltemperature'] = AttributeClass('temperature', self.devices['temperature'], 0.3)

        self.attributes['crystaltemperature'].attrSignal.connect(self.readCrystalTemperature)

# Spectrometer
        self.attributes['wavelengths'] = AttributeClass('wavelengths', self.devices['spectrometer'], None)
        self.attributes['peakenergy'] = AttributeClass('peakenergy', self.devices['spectrometer'], 0.3)
        self.attributes['peakwidth'] = AttributeClass('peakwidth', self.devices['spectrometer'], 0.3)
        self.attributes['spectrum'] = AttributeClass('spectrum', self.devices['spectrometer'], 0.3)
        self.attributes['spectrometerState'] = AttributeClass('state', self.devices['spectrometer'], 0.3)

        self.attributes['peakenergy'].attrSignal.connect(self.readPeakEnergy)
        self.attributes['peakwidth'].attrSignal.connect(self.readPeakWidth)
        self.attributes['spectrum'].attrSignal.connect(self.readSpectrum)
        self.attributes['wavelengths'].attrSignal.connect(self.readWavelengths)
        self.attributes['spectrometerState'].attrSignal.connect(self.readSpectrometerState)

        splash.showMessage('         Setting up variables', alignment = QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
        app.processEvents()

#         self.timer = QtCore.QTimer(self)
#         self.timer.timeout.connect(self.checkDevices)
#         self.timer.start(100)



    def checkDevices(self):
        for a in self.attributes.itervalues():
            pass
#            a.attr_read()

    def readLeeLaserCurrent(self, data):
        self.leeLaserCurrentWidget.setAttributeValue(data)

    def readLeeLaserPercentCurrent(self, data):
        self.leeLaserPercentCurrentWidget.setAttributeValue(data)

    def writeLeeLaserPercentCurrent(self):
        self.guiLock.acquire()
        w = self.leeLaserPercentCurrentWidget.getWriteValue()
        self.attributes['leelaserpercentcurrent'].attr_write(w)
        self.guiLock.release()

    def readLeeLaserState(self, data):
        self.leeLaserName.setState(data)

    def readLeeLaserShutterState(self, data):
        self.leeLaserShutterWidget.setStatus(data)

    def readLeeLaserOperationState(self, data):
        self.leeLaserOperationStateWidget.setStatus(data)

    def readIonpumpPressure(self, data):
        self.ionpumpPressureWidget.setAttributeValue(data)

    def readCrystalTemperature(self, data):
        self.temperatureWidget.setAttributeValue(data)

    def readSpectrometerState(self, data):
        self.spectrometerName.setState(data)
        data.value = ''
        self.onOffCommands.setStatus(data)

    def readPeakEnergy(self, data):
        self.peakEnergyWidget.setAttributeValue(data)

    def readPeakWidth(self, data):
        self.peakWidthWidget.setAttributeValue(data)

    def readExposure(self, data):
#        self.exposureWidget.setAttributeValue(data.value)
        self.exposureWidget.setAttributeValue(data)

    def writeExposure(self):
        self.guiLock.acquire()
        w = self.exposureWidget.getWriteValue()
        self.attributes['exposure'].attr_write(w)
        self.guiLock.release()

    def readWavelengths(self, data):
        try:
            print 'time vector read: ', data.value.shape[0]
        except:
            pass
        self.timeVector = data.value

    def readSpectrum(self, data):
        if self.timeVector == None:
            print 'No time vector'
        else:
            self.spectrometerPlot.setSpectrum(xData = self.timeVector, yData = data)
            self.spectrometerPlot.update()

    def initSpectrometer(self):
        self.devices['spectrometer'].command_inout('init')

    def onSpectrometer(self):
        self.devices['spectrometer'].command_inout('on')

    def offSpectrometer(self):
        self.devices['spectrometer'].command_inout('off')

    def stopSpectrometer(self):
        self.devices['spectrometer'].command_inout('stop')

    def setupAttributeLayout(self, attributeList = []):
        self.attributeQObjects = []
        for att in attributeList:
            attQObject = qw.QTangoReadAttributeDouble()
            attQObject.setAttributeName(att.name)
            self.attributeQObjects.append(attQObject)
            self.layout_attributes.addWidget(attQObject)

    def startLeeLaser(self):
        self.devices['leelaser'].command_inout('startlaser')

    def stopLeeLaser(self):
        self.devices['leelaser'].command_inout('off')

    def clearFaultLeeLaser(self):
        self.devices['leelaser'].command_inout('clearfault')

    def openLeeLaserShutter(self):
        self.devices['leelaser'].command_inout('open')

    def closeLeeLaserShutter(self):
        self.devices['leelaser'].command_inout('close')

    def closeEvent(self, event):
#         for device in self.devices.itervalues():
#             device.terminate()
        for a in self.attributes.itervalues():
            print 'Stopping', a.name
            a.stopRead()
            a.readThread.join()
        event.accept()

    def setupLayout(self):
        s='QWidget{background-color: #000000; }'
        self.setStyleSheet(s)

        self.frame_sizes = qw.QTangoSizes()
        self.frame_sizes.barHeight = 30
        self.frame_sizes.barWidth = 20
        self.frame_sizes.readAttributeWidth = 350
        self.frame_sizes.writeAttributeWidth = 150
        self.frame_sizes.fontStretch= 80
        self.frame_sizes.fontType = 'Segoe UI'
#        self.frame_sizes.fontType = 'Trebuchet MS'
        self.attr_sizes = qw.QTangoSizes()
        self.attr_sizes.barHeight = 20
        self.attr_sizes.barWidth = 20
        self.attr_sizes.readAttributeWidth = 350
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

        self.title = qw.QTangoTitleBar('MP control')
        self.setWindowTitle('MP control')
        self.sidebar = qw.QTangoSideBar(colors = self.colors, sizes = self.frame_sizes)
        self.bottombar = qw.QTangoHorizontalBar()

        self.leeLaserName = qw.QTangoDeviceNameStatus(colors = self.colors, sizes = self.frame_sizes)
        self.leeLaserName.setAttributeName('LeeLaser')
        self.leeLaserOperationStateWidget = qw.QTangoCommandSelection('Laser operation', colors = self.colors, sizes = self.attr_sizes)
        self.leeLaserOperationStateWidget.addCmdButton('Stop', self.stopLeeLaser)
        self.leeLaserOperationStateWidget.addCmdButton('Start', self.startLeeLaser)
        self.leeLaserOperationStateWidget.addCmdButton('Clear fault', self.clearFaultLeeLaser)

        self.leeLaserShutterWidget = qw.QTangoCommandSelection('Shutter', colors = self.colors, sizes = self.attr_sizes)
        self.leeLaserShutterWidget.addCmdButton('Close', self.closeLeeLaserShutter)
        self.leeLaserShutterWidget.addCmdButton('Open', self.openLeeLaserShutter)

        self.leeLaserCurrentWidget = qw.QTangoReadAttributeSlider2(colors = self.colors, sizes = self.attr_sizes)
        self.leeLaserCurrentWidget.setAttributeName('LeeLaser current', 'A')
        self.leeLaserCurrentWidget.setAttributeWarningLimits([8, 23])
        self.leeLaserCurrentWidget.setSliderLimits(6, 30)

        self.leeLaserPercentCurrentWidget = qw.QTangoWriteAttributeSlider(colors = self.colors, sizes = self.attr_sizes)
        self.leeLaserPercentCurrentWidget.setAttributeName('LeeLaser percent current', '%')
        self.leeLaserPercentCurrentWidget.setAttributeWarningLimits([40, 84])
        self.leeLaserPercentCurrentWidget.setSliderLimits(36, 100)
        self.leeLaserPercentCurrentWidget.writeValueSpinbox.editingFinished.connect(self.writeLeeLaserPercentCurrent)

        self.ionpumpPressureWidget = qw.QTangoReadAttributeSlider2(colors = self.colors, sizes = self.attr_sizes)
        self.ionpumpPressureWidget.setAttributeName('Crystal pressure', 'mBar')
        self.ionpumpPressureWidget.setAttributeWarningLimits([0, 5e-7])
        self.ionpumpPressureWidget.setSliderLimits(0, 1e-7)

        self.temperatureWidget = qw.QTangoReadAttributeSlider2(colors = self.colors, sizes = self.attr_sizes)
        self.temperatureWidget.setAttributeName('Crystal temp', 'degC')
        self.temperatureWidget.setAttributeWarningLimits([-280, -170])
        self.temperatureWidget.setSliderLimits(-270, 30)

        self.spectrometerName = qw.QTangoDeviceNameStatus(colors = self.colors, sizes = self.frame_sizes)
        self.spectrometerName.setAttributeName('Spectrometer')

        self.onOffCommands = qw.QTangoCommandSelection('Spectrometer commands', colors = self.colors, sizes = self.attr_sizes)
        self.onOffCommands.addCmdButton('Init', self.initSpectrometer)
        self.onOffCommands.addCmdButton('On', self.onSpectrometer)
        self.onOffCommands.addCmdButton('Off', self.offSpectrometer)
        self.onOffCommands.addCmdButton('Stop', self.stopSpectrometer)
        self.peakWidthWidget = qw.QTangoReadAttributeSlider2(colors = self.colors, sizes = self.attr_sizes)
        self.peakWidthWidget.setAttributeName('Spectral width', 'nm')
        self.peakWidthWidget.setAttributeWarningLimits([35, 100])
        self.peakWidthWidget.setSliderLimits(0, 70)
        self.peakEnergyWidget = qw.QTangoReadAttributeSlider2(colors = self.colors, sizes = self.attr_sizes)
        self.peakEnergyWidget.setAttributeName('Laser energy', 'a.u.')
        self.peakEnergyWidget.setAttributeWarningLimits([0.5, 5])
        self.peakEnergyWidget.setSliderLimits(0, 2)

        self.spectrometerPlot = qw.QTangoReadAttributeSpectrum(colors = self.colors, sizes = self.attr_sizes)
        self.spectrometerPlot.setAttributeName('Compressed spectrum')
        self.spectrometerPlot.setXRange(700, 900)
        self.spectrometerPlot.fixedSize(True)


        layout2.addWidget(self.title)
        layout2.addLayout(layoutData)
        layoutData.addLayout(self.layout_attributes)
#        layoutData.addWidget(self.crystalImageWidget)
        layoutData.addSpacerItem(spacerItemH)

        self.layout_attributes.addWidget(self.leeLaserName)
        self.layout_attributes.addWidget(self.spectrometerName)

        self.layout_attributes.addSpacerItem(spacerItemV)
        self.layout_attributes.addWidget(self.leeLaserOperationStateWidget)
        self.layout_attributes.addWidget(self.leeLaserShutterWidget)
        self.layout_attributes.addWidget(self.leeLaserCurrentWidget)
        self.layout_attributes.addWidget(self.leeLaserPercentCurrentWidget)

        self.layout_attributes.addSpacerItem(spacerItemV)
        self.layout_attributes.addWidget(self.ionpumpPressureWidget)
        self.layout_attributes.addWidget(self.temperatureWidget)

        self.layout_attributes.addSpacerItem(spacerItemV)
        self.layout_attributes.addWidget(self.onOffCommands)
        self.layout_attributes.addWidget(self.peakWidthWidget)
        self.layout_attributes.addWidget(self.peakEnergyWidget)
        self.layout_attributes.addWidget(self.spectrometerPlot)



        layout1.addWidget(self.sidebar)
        layout1.addLayout(layout2)
        layout0.addLayout(layout1)
        layout0.addWidget(self.bottombar)

#        self.resize(500,800)
        self.setGeometry(200,100,450,900)

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