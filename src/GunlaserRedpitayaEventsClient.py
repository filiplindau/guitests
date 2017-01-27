'''
Created on 23 okt 2014

@author: Filip Lindau
'''
# -*- coding:utf-8 -*-
from PyQt4 import QtGui, QtCore

import time
import sys
import PyTango as pt

class TangoDeviceData(object):
    def __init__(self, deviceProxy = None, eventList = None):
        self.device = deviceProxy
        self.eventList = eventList

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

        self.lastRead = time.time()
        self.fps = [0,0,0,0,0]
        self.changeDevice(self.deviceName)

        splash.showMessage('         Setting up variables', alignment = QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
        app.processEvents()

        self.positionOffset = 0.0

        


    def checkDevices(self):
        for a in self.attributes.itervalues():
            pass
#            a.attr_read()

    def changeDevice(self, devName=None):
        try:
            for a in self.attributes.itervalues():
                print 'Stopping', a.name
                a.unsubscribe_event()
        except:
            pass

        self.trigDelayWidget.writeValueInitialized = False
        self.trigLevelWidget.writeValueInitialized = False
        self.trigSourceWidget.writeValueInitialized = False
        self.trigModeWidget.writeValueInitialized = False
        self.recordLengthWidget.writeValueInitialized = False
        self.sampleRateWidget.writeValueInitialized = False

        if devName != None:
            self.deviceName = str(devName)
        else:
            self.deviceName = str(self.redpitayaDevices.writeValueComboBox.itemText(0))
            
        self.title.setName(self.deviceName.upper())
        self.devices = {}
        self.devices['redpitaya']=pt.DeviceProxy(self.deviceName)

        self.attributes = {}
        self.attributes['timevector'] = AttributeClass('timevector', self.devices['redpitaya'], None, slot=self.readTimevector, eventType=None)
        
        self.attributes['waveform1'] = AttributeClass('waveform1', self.devices['redpitaya'], 0.02, slot=self.readWaveform1, eventType=pt.EventType.CHANGE_EVENT, rateLimit=True)
        self.attributes['waveform2'] = AttributeClass('waveform2', self.devices['redpitaya'], 0.02, slot=self.readWaveform2, eventType=pt.EventType.CHANGE_EVENT, rateLimit=True)
        self.attributes['triggerlevel'] = AttributeClass('triggerlevel', self.devices['redpitaya'], 0.05, slot=self.readTrigLevel, eventType=pt.EventType.CHANGE_EVENT)
        self.attributes['triggerdelay'] = AttributeClass('triggerdelay', self.devices['redpitaya'], 0.05, slot=self.readTrigDelay, eventType=pt.EventType.CHANGE_EVENT)
        self.attributes['triggermode'] = AttributeClass('triggermode', self.devices['redpitaya'], 0.05, slot=self.readTrigMode, eventType=pt.EventType.CHANGE_EVENT)
        self.attributes['triggersource'] = AttributeClass('triggersource', self.devices['redpitaya'], 0.05, slot=self.readTrigSource, eventType=pt.EventType.CHANGE_EVENT)
        self.attributes['recordlength'] = AttributeClass('recordlength', self.devices['redpitaya'], 0.05, slot=self.readRecordLength, eventType=pt.EventType.CHANGE_EVENT)
        self.attributes['samplerate'] = AttributeClass('samplerate', self.devices['redpitaya'], 0.05, slot=self.readSampleRate, eventType=pt.EventType.CHANGE_EVENT)
        self.attributes['state'] = AttributeClass('state', self.devices['redpitaya'], 0.05, slot=self.readState, eventType=pt.EventType.CHANGE_EVENT)

        
        
#         self.attributes['waveform1'].attrSignal.connect(self.readWaveform1)
#         self.attributes['waveform2'].attrSignal.connect(self.readWaveform2)
#         self.attributes['triggerlevel'].attrSignal.connect(self.readTrigLevel)
#         self.attributes['triggerdelay'].attrSignal.connect(self.readTrigDelay)
#         self.attributes['triggermode'].attrSignal.connect(self.readTrigMode)
#         self.attributes['triggersource'].attrSignal.connect(self.readTrigSource)
#         self.attributes['recordlength'].attrSignal.connect(self.readRecordLength)
#         self.attributes['samplerate'].attrSignal.connect(self.readSampleRate)
#         self.attributes['state'].attrSignal.connect(self.readState)
        
        
        


    def readTimevector(self, data):
        self.timeVector = data.value

    def readWaveform1(self, data):
        try:
            with self.attributes['waveform1'].attrLock:
                if self.timeVector != None:
                    if data.value.shape[0] != self.timeVector.shape[0]:
                        self.attributes['timevector'] = AttributeClass('timevector', self.devices['redpitaya'], None, slot=self.readTimevector, eventType=None)
                    else:
                        self.waveformPlot.setSpectrum(xData = self.timeVector, yData = data, index=0)
                        self.waveformPlot.update()
        except KeyError:
            print 'keyerror'
            pass
            

    def readWaveform2(self, data):
        try:
            with self.attributes['waveform2'].attrLock:
                if self.timeVector != None:
                    if data.value.shape[0] != self.timeVector.shape[0]:
                        self.attributes['timevector'] = AttributeClass('timevector', self.devices['redpitaya'], None, slot=self.readTimevector, eventType=None)
                    else:
                        self.waveformPlot.setSpectrum(xData = self.timeVector, yData = data, index=1)
                        self.waveformPlot.update()
        except KeyError:
            pass

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
        
    def triggerLevelEvent(self, event):
        data = event.attr_value
        self.trigLevelSignal.emit(data)
        
    def readTrigDelay(self, data):
        self.trigDelayWidget.setAttributeValue(data)

    def readTrigMode(self, data):
        self.trigModeWidget.setAttributeValue(data)

    def readTrigSource(self, data):
        self.trigSourceWidget.setAttributeValue(data)

    def readRecordLength(self, data):
        self.recordLengthWidget.setAttributeValue(data)

    def readSampleRate(self, data):
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
            self.layout_attributes.addWidget(attQObject)

    def closeEvent(self, event):
        try:
            for a in self.attributes.itervalues():
                print 'Stopping', a.name
                a.unsubscribe_event()
        except:
            pass
            
        event.accept()

    def enumerateDevices(self):
        db = pt.Database()
        self.devNameList = db.get_device_exported_for_class('redpitayaeventsds').value_string


    def setupLayout(self):
        s='QWidget{background-color: #000000; }'
        self.setStyleSheet(s)

        self.frame_sizes = qw.QTangoSizes()
        self.frame_sizes.barHeight = 20
        self.frame_sizes.barWidth = 20
        self.frame_sizes.readAttributeWidth = 320
        self.frame_sizes.writeAttributeWidth = 150
        self.frame_sizes.fontStretch= 80
        self.frame_sizes.fontType = 'Segoe UI'
#        self.frame_sizes.fontType = 'Trebuchet MS'

        self.attr_sizes = qw.QTangoSizes()
        self.attr_sizes.barHeight = 20
        self.attr_sizes.barWidth = 20
        self.attr_sizes.readAttributeWidth = 320
        self.attr_sizes.readAttributeHeight = 320
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
        spacerItemV = QtGui.QSpacerItem(20, 5, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.MinimumExpanding)
        spacerItemBar = QtGui.QSpacerItem(self.frame_sizes.barWidth, self.frame_sizes.barHeight+8, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        spacerItemH = QtGui.QSpacerItem(20, 5, QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Minimum)

        layoutData = QtGui.QHBoxLayout()
        layoutData.setMargin(self.attr_sizes.barHeight/2)
        layoutData.setSpacing(self.attr_sizes.barHeight*2)
        self.layout_attributes = QtGui.QVBoxLayout()
        self.layout_attributes.setMargin(0)
        self.layout_attributes.setSpacing(self.attr_sizes.barHeight/2)
        self.layout_attributes.setContentsMargins(0, 0, 0, 0)

#         self.layoutAttributes2 = QtGui.QVBoxLayout()
#         self.layoutAttributes2.setMargin(0)
#         self.layoutAttributes2.setSpacing(self.attr_sizes.barHeight/2)
#         self.layoutAttributes2.setContentsMargins(0, 0, 0, 0)
#
#         self.layoutAttributes3 = QtGui.QVBoxLayout()
#         self.layoutAttributes3.setMargin(0)
#         self.layoutAttributes3.setSpacing(self.attr_sizes.barHeight/2)
#         self.layoutAttributes3.setContentsMargins(0, 0, 0, 0)

        self.title = qw.QTangoTitleBar(self.deviceName)
        self.setWindowTitle('RedPitaya')
        self.sidebar = qw.QTangoSideBar(colors = self.colors, sizes = self.frame_sizes)
        self.bottombar = qw.QTangoHorizontalBar()


        self.redpitayaDevices = qw.QTangoWriteAttributeComboBox(colors = self.colors, sizes = self.attr_sizes)
        s=str(self.redpitayaDevices.writeValueComboBox.styleSheet())

        self.redpitayaDevices.setAttributeName('Device list')
        db = pt.Database()
        devNameList = db.get_device_exported_for_class('redpitayaeventsds').value_string
        for devName in devNameList:
            self.redpitayaDevices.addItem(devName)

        self.redpitayaDevices.writeValueComboBox.setWidth(self.attr_sizes.barHeight*10)
        self.redpitayaDevices.setActivatedMethod(self.changeDevice)
        self.redpitayaDevices.startLabel.setQuality(pt.AttrQuality.ATTR_VALID)
        self.redpitayaDevices.endLabel.setQuality(pt.AttrQuality.ATTR_VALID)


        self.redpitayaName = qw.QTangoDeviceNameStatus(colors = self.colors, sizes = self.frame_sizes)
        self.redpitayaName.setAttributeName('Redpitaya')
        self.redpitayaCommands = qw.QTangoCommandSelection('Commands', colors = self.colors, sizes = self.attr_sizes)
        self.redpitayaCommands.addCmdButton('Init', self.initRedpitaya)
        self.redpitayaCommands.addCmdButton('Start', self.startRedpitaya)
        self.redpitayaCommands.addCmdButton('Stop', self.stopRedpitaya)

        self.trigLevelWidget = qw.QTangoWriteAttributeDouble(colors = self.colors, sizes = self.attr_sizes)
        self.trigLevelWidget.setAttributeName('Trigger level', 'V')
        self.trigLevelWidget.writeValueLineEdit.returnPressed.connect(self.writeTrigLevel)

        self.trigDelayWidget = qw.QTangoWriteAttributeDouble(colors = self.colors, sizes = self.attr_sizes)
        self.trigDelayWidget.setAttributeName('Trigger delay', 'us')
        self.trigDelayWidget.writeValueLineEdit.returnPressed.connect(self.writeTrigDelay)

        self.trigModeWidget = qw.QTangoWriteAttributeComboBox(colors = self.colors, sizes = self.attr_sizes)
        self.trigModeWidget.setAttributeName('Trigger mode')
        self.trigModeWidget.addItem('NORMAL')
        self.trigModeWidget.addItem('AUTO')
        self.trigModeWidget.setActivatedMethod(self.writeTrigMode)

        self.trigSourceWidget = qw.QTangoWriteAttributeComboBox(colors = self.colors, sizes = self.attr_sizes)
        self.trigSourceWidget.setAttributeName('Trigger source')
        self.trigSourceWidget.addItem('CHANNEL1')
        self.trigSourceWidget.addItem('CHANNEL2')
        self.trigSourceWidget.addItem('EXTERNAL')
        self.trigSourceWidget.setActivatedMethod(self.writeTrigSource)

        self.recordLengthWidget = qw.QTangoWriteAttributeDouble(colors = self.colors, sizes = self.attr_sizes)
        self.recordLengthWidget.setAttributeName('Record length', 'samples')
        self.recordLengthWidget.writeValueLineEdit.returnPressed.connect(self.writeRecordLength)

        self.sampleRateWidget = qw.QTangoWriteAttributeDouble(colors = self.colors, sizes = self.attr_sizes)
        self.sampleRateWidget.setAttributeName('Sample rate', 'samples')
        self.sampleRateWidget.writeValueLineEdit.returnPressed.connect(self.writeSampleRate)

        self.waveformPlot = qw.QTangoReadAttributeSpectrum(colors = self.colors, sizes = self.attr_sizes)
        self.waveformPlot.setAttributeName('Waveform')
        self.waveformPlot.spectrum.addPlot(self.colors.secondaryColor1)
#        self.waveformPlot.setXRange(700, 900)
        self.waveformPlot.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

        self.attr_sizes.readAttributeHeight = 250



        layout2.addWidget(self.title)
        layout2.addLayout(layoutData)
        layoutData.addLayout(self.layout_attributes)
#        layoutData.addSpacerItem(spacerItemH)
#        layoutData.addLayout(self.layoutAttributes2)
#        layoutData.addLayout(self.layoutAttributes3)

        self.layout_attributes.addWidget(self.redpitayaDevices)
        self.layout_attributes.addWidget(self.redpitayaName)
        self.layout_attributes.addWidget(self.redpitayaCommands)
        self.layout_attributes.addWidget(self.recordLengthWidget)
        self.layout_attributes.addWidget(self.sampleRateWidget)
        self.layout_attributes.addWidget(self.trigLevelWidget)
        self.layout_attributes.addWidget(self.trigDelayWidget)
        self.layout_attributes.addWidget(self.trigModeWidget)
        self.layout_attributes.addWidget(self.trigSourceWidget)
        layoutData.addWidget(self.waveformPlot)

        self.layout_attributes.addSpacerItem(spacerItemV)



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
#    from QTangoWidgets.AttributeReadThreadClass import AttributeClass
    from QTangoWidgets.AttributeReadClass import AttributeClass
    import pyqtgraph as pg    
    import threading
    import numpy as np

    splash.showMessage('         Starting GUI', alignment = QtCore.Qt.AlignBottom | QtCore.Qt.AlignLeft, color = QtGui.QColor('#66cbff'))
    app.processEvents()
    myapp = TangoDeviceClient(None)
    myapp.show()
    splash.finish(myapp)
    sys.exit(app.exec_())