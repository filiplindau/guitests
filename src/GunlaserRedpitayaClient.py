'''
Created on 23 okt 2014

@author: Filip Lindau
'''
# -*- coding:utf-8 -*-
from PyQt4 import QtGui, QtCore

import time
import sys




class TangoDeviceClient(QtGui.QWidget):
    def __init__(self, deviceName, parent = None):
        QtGui.QWidget.__init__(self,parent)
#        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.timeVector = None
        self.xData = None
        self.xDataTemp = None
        self.deviceName = deviceName

        self.setupLayout()

        splash.showMessage('         Initializing devices', alignment = QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
        app.processEvents()

        t0=time.clock()
        print time.clock()-t0, ' s'

        splash.showMessage('         Reading startup attributes', alignment = QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
        app.processEvents()


        self.guiLock = threading.Lock()

        self.changeDevice(self.deviceName)

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

    def changeDevice(self, devName):
        try:
            for a in self.attributes.itervalues():
                print 'Stopping', a.name
                a.stopRead()
            for a in self.attributes.itervalues():
                a.readThread.join()
        except:
            pass

        self.trigDelayWidget.writeValueInitialized = False
        self.trigLevelWidget.writeValueInitialized = False
        self.trigSourceWidget.writeValueInitialized = False
        self.trigModeWidget.writeValueInitialized = False
        self.recordLengthWidget.writeValueInitialized = False
        self.sampleRateWidget.writeValueInitialized = False

        self.deviceName = str(devName)
        self.title.setName(self.deviceName.upper())
        self.devices = {}
        self.devices['redpitaya']=pt.DeviceProxy(self.deviceName)

        self.attributes = {}
        self.attributes['timevector'] = AttributeClass('timevector', self.devices['redpitaya'], None)
        self.attributes['waveform1'] = AttributeClass('waveform1', self.devices['redpitaya'], 0.3)
        self.attributes['waveform2'] = AttributeClass('waveform2', self.devices['redpitaya'], 0.3)
        self.attributes['triggerlevel'] = AttributeClass('triggerlevel', self.devices['redpitaya'], 0.3)
        self.attributes['triggerdelay'] = AttributeClass('triggerdelay', self.devices['redpitaya'], 0.3)
        self.attributes['triggermode'] = AttributeClass('triggermode', self.devices['redpitaya'], 1.0)
        self.attributes['triggersource'] = AttributeClass('triggersource', self.devices['redpitaya'], 1.0)
        self.attributes['recordlength'] = AttributeClass('recordlength', self.devices['redpitaya'], 0.3)
        self.attributes['samplerate'] = AttributeClass('samplerate', self.devices['redpitaya'], 0.3)
        self.attributes['state'] = AttributeClass('state', self.devices['redpitaya'], 0.3)

        self.attributes['timevector'].attrSignal.connect(self.readTimevector)
        self.attributes['waveform1'].attrSignal.connect(self.readWaveform1)
        self.attributes['waveform2'].attrSignal.connect(self.readWaveform2)
        self.attributes['triggerlevel'].attrSignal.connect(self.readTrigLevel)
        self.attributes['triggerdelay'].attrSignal.connect(self.readTrigDelay)
        self.attributes['triggermode'].attrSignal.connect(self.readTrigMode)
        self.attributes['triggersource'].attrSignal.connect(self.readTrigSource)
        self.attributes['recordlength'].attrSignal.connect(self.readRecordLength)
        self.attributes['samplerate'].attrSignal.connect(self.readSampleRate)
        self.attributes['state'].attrSignal.connect(self.readState)


    def readTimevector(self, data):
        self.timeVector = data.value

    def readWaveform1(self, data):
        if data.value.shape[0] != self.timeVector.shape[0]:
            self.attributes['timevector'] = AttributeClass('timevector', self.devices['redpitaya'], None)
            self.attributes['timevector'].attrSignal.connect(self.readTimevector)
        else:
            self.waveformPlot.setSpectrum(xData = self.timeVector, yData = data, index=0)
            self.waveformPlot.update()

    def readWaveform2(self, data):
        if data.value.shape[0] != self.timeVector.shape[0]:
            self.attributes['timevector'] = AttributeClass('timevector', self.devices['redpitaya'], None)
            self.attributes['timevector'].attrSignal.connect(self.readTimevector)
        else:
            self.waveformPlot.setSpectrum(xData = self.timeVector, yData = data, index=1)
            self.waveformPlot.update()

    def initRedpitaya(self):
        self.devices['redpitaya'].command_inout('init')

    def startRedpitaya(self):
        self.devices['redpitaya'].command_inout('start')

    def stopRedpitaya(self):
        self.devices['redpitaya'].command_inout('stop')

    def readState(self, data):
        self.redpitayaCommands.setStatus(data)
        self.redpitayaName.setState(data)

    def writeTrigLevel(self):
        with self.guiLock:
            w = self.trigLevelWidget.getWriteValue()
            self.attributes['triggerlevel'].attr_write(w)

    def readTrigLevel(self, data):
        self.trigLevelWidget.setAttributeValue(data)

    def readTrigDelay(self, data):
        self.trigDelayWidget.setAttributeValue(data)

    def readTrigMode(self, data):
        self.trigModeWidget.setAttributeValue(data)

    def readTrigSource(self, data):
        self.trigSourceWidget.setAttributeValue(data)

    def readRecordLength(self, data):
        self.recordLengthWidget.setAttributeValue(data)

    def readSampleRate(self, data):
#        print str(data.value)
        self.sampleRateWidget.setAttributeValue(data)

    def writeTrigDelay(self):
        with self.guiLock:
            w = self.trigDelayWidget.getWriteValue()
            self.attributes['triggerdelay'].attr_write(w)

    def writeRecordLength(self):
        with self.guiLock:
            w = self.recordLengthWidget.getWriteValue()
            self.attributes['recordlength'].attr_write(w)

    def writeSampleRate(self):
        with self.guiLock:
            w = self.sampleRateWidget.getWriteValue()
            self.attributes['samplerate'].attr_write(w)

    def writeTrigMode(self, text):
        with self.guiLock:
            self.attributes['triggermode'].attr_write(str(text))
            print text

    def writeTrigSource(self, text):
        with self.guiLock:
            self.attributes['triggersource'].attr_write(str(text))
            print text

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
        self.frameSizes.barWidth = 20
        self.frameSizes.readAttributeWidth = 320
        self.frameSizes.writeAttributeWidth = 150
        self.frameSizes.fontStretch= 80
        self.frameSizes.fontType = 'Segoe UI'
#        self.frameSizes.fontType = 'Trebuchet MS'

        self.attrSizes = qw.QTangoSizes()
        self.attrSizes.barHeight = 20
        self.attrSizes.barWidth = 20
        self.attrSizes.readAttributeWidth = 320
        self.attrSizes.readAttributeHeight = 320
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
        spacerItemBar = QtGui.QSpacerItem(self.frameSizes.barWidth, self.frameSizes.barHeight + 8, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        spacerItemH = QtGui.QSpacerItem(20, 5, QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Minimum)

        layoutData = QtGui.QHBoxLayout()
        layoutData.setMargin(self.attrSizes.barHeight / 2)
        layoutData.setSpacing(self.attrSizes.barHeight * 2)
        self.layoutAttributes = QtGui.QVBoxLayout()
        self.layoutAttributes.setMargin(0)
        self.layoutAttributes.setSpacing(self.attrSizes.barHeight / 2)
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

        self.title = qw.QTangoTitleBar(self.deviceName)
        self.setWindowTitle('RedPitaya')
        self.sidebar = qw.QTangoSideBar(colors=self.colors, sizes=self.frameSizes)
        self.bottombar = qw.QTangoHorizontalBar()

        self.redpitayaDevices = qw.QTangoWriteAttributeComboBox(colors=self.colors, sizes=self.attrSizes)
        s = str(self.redpitayaDevices.writeValueComboBox.styleSheet())

        self.redpitayaDevices.setAttributeName('Device list')
        db = pt.Database()
        devNameList = db.get_device_exported_for_class('redpitayads').value_string
        for devName in devNameList:
            self.redpitayaDevices.addItem(devName)
        self.redpitayaDevices.writeValueComboBox.blockSignals(True)
        ind = self.redpitayaDevices.writeValueComboBox.findText(self.deviceName)
        self.redpitayaDevices.writeValueComboBox.setCurrentIndex(ind)
        self.redpitayaDevices.writeValueComboBox.blockSignals(False)

        self.redpitayaDevices.writeValueComboBox.setWidth(self.attrSizes.barHeight*10)
        self.redpitayaDevices.setActivatedMethod(self.changeDevice)
        self.redpitayaDevices.startLabel.setQuality(pt.AttrQuality.ATTR_VALID)
        self.redpitayaDevices.endLabel.setQuality(pt.AttrQuality.ATTR_VALID)

        self.redpitayaName = qw.QTangoDeviceNameStatus(colors = self.colors, sizes = self.frameSizes)
        self.redpitayaName.setAttributeName('Redpitaya')
        self.redpitayaCommands = qw.QTangoCommandSelection('Commands', colors = self.colors, sizes = self.attrSizes)
        self.redpitayaCommands.addCmdButton('Init', self.initRedpitaya)
        self.redpitayaCommands.addCmdButton('Start', self.startRedpitaya)
        self.redpitayaCommands.addCmdButton('Stop', self.stopRedpitaya)

        self.trigLevelWidget = qw.QTangoWriteAttributeDouble(colors = self.colors, sizes = self.attrSizes)
        self.trigLevelWidget.setAttributeName('Trigger level', 'V')
        self.trigLevelWidget.writeValueLineEdit.returnPressed.connect(self.writeTrigLevel)

        self.trigDelayWidget = qw.QTangoWriteAttributeDouble(colors = self.colors, sizes = self.attrSizes)
        self.trigDelayWidget.setAttributeName('Trigger delay', 'us')
        self.trigDelayWidget.writeValueLineEdit.returnPressed.connect(self.writeTrigDelay)

        self.trigModeWidget = qw.QTangoWriteAttributeComboBox(colors = self.colors, sizes = self.attrSizes)
        self.trigModeWidget.setAttributeName('Trigger mode')
        self.trigModeWidget.addItem('NORMAL')
        self.trigModeWidget.addItem('AUTO')
        self.trigModeWidget.setActivatedMethod(self.writeTrigMode)

        self.trigSourceWidget = qw.QTangoWriteAttributeComboBox(colors = self.colors, sizes = self.attrSizes)
        self.trigSourceWidget.setAttributeName('Trigger source')
        self.trigSourceWidget.addItem('CHANNEL1')
        self.trigSourceWidget.addItem('CHANNEL2')
        self.trigSourceWidget.addItem('EXTERNAL')
        self.trigSourceWidget.setActivatedMethod(self.writeTrigSource)

        self.recordLengthWidget = qw.QTangoWriteAttributeDouble(colors = self.colors, sizes = self.attrSizes)
        self.recordLengthWidget.setAttributeName('Record length', 'samples')
        self.recordLengthWidget.writeValueLineEdit.returnPressed.connect(self.writeRecordLength)

        self.sampleRateWidget = qw.QTangoWriteAttributeDouble(colors = self.colors, sizes = self.attrSizes)
        self.sampleRateWidget.setAttributeName('Sample rate', 'samples')
        self.sampleRateWidget.writeValueLineEdit.returnPressed.connect(self.writeSampleRate)

        self.waveformPlot = qw.QTangoReadAttributeSpectrum(colors = self.colors, sizes = self.attrSizes)
        self.waveformPlot.setAttributeName('Waveform')
        self.waveformPlot.spectrum.addPlot(self.colors.secondaryColor1)
        self.waveformPlot.spectrum.setCurveName(0, 'Waveform 1')
        self.waveformPlot.spectrum.setCurveName(1, 'Waveform 2')
        self.waveformPlot.spectrum.showLegend(True)
#        self.waveformPlot.setXRange(700, 900)
        self.waveformPlot.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

        self.attrSizes.readAttributeHeight = 250



        layout2.addWidget(self.title)
        layout2.addLayout(layoutData)
        layoutData.addLayout(self.layoutAttributes)
#        layoutData.addSpacerItem(spacerItemH)
#        layoutData.addLayout(self.layoutAttributes2)
#        layoutData.addLayout(self.layoutAttributes3)

        self.layoutAttributes.addWidget(self.redpitayaDevices)
        self.layoutAttributes.addWidget(self.redpitayaName)
        self.layoutAttributes.addWidget(self.redpitayaCommands)
        self.layoutAttributes.addWidget(self.recordLengthWidget)
        self.layoutAttributes.addWidget(self.sampleRateWidget)
        self.layoutAttributes.addWidget(self.trigLevelWidget)
        self.layoutAttributes.addWidget(self.trigDelayWidget)
        self.layoutAttributes.addWidget(self.trigModeWidget)
        self.layoutAttributes.addWidget(self.trigSourceWidget)
        layoutData.addWidget(self.waveformPlot)

        self.layoutAttributes.addSpacerItem(spacerItemV)



        layout1.addWidget(self.sidebar)
        layout1.addLayout(layout2)
        layout0.addLayout(layout1)
#        layout0.addWidget(self.bottombar)

#        self.resize(500,800)
        self.setGeometry(200,100,800,400)

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
    myapp = TangoDeviceClient('gunlaser/devices/redpitaya0')
    myapp.show()
    splash.finish(myapp)
    sys.exit(app.exec_())
