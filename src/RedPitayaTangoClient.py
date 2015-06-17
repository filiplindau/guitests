# -*- coding:utf-8 -*-
"""
Created on 19 nov 2013

@author: Filip
"""
from PyQt4 import QtGui, QtCore

import time 
import sys


class AttributeClass(QtCore.QObject):
    import PyTango as pt
    attrSignal = QtCore.pyqtSignal(pt.device_attribute.DeviceAttribute)
    def __init__(self, name, device, interval):
        super(AttributeClass, self).__init__()
        self.name = name
        self.device = device
        self.interval = interval
        
        self.lastRead = time.time()
        self.attr = None
        self.readThread = threading.Thread(name=self.name, target=self.attr_read)
        self.stopThread = False
        
        self.startRead() 
        
    def attr_read(self):
        while self.stopThread == False:
            t = time.time()
            if t - self.lastRead > self.interval:
                self.lastRead = t                
                try:
                    self.attr = self.device.read_attribute(self.name)
                    self.attrSignal.emit(self.attr)
                except Exception, e:
                    print self.name, ' recovering from ', str(e)                
            time.sleep(self.interval)
        print self.name, ' stopped'
                
    def attr_write(self, wvalue):
        self.device.write_attribute(self.name, wvalue)
        
    def stopRead(self):
        self.stopThread = True
        
    def startRead(self):
        self.stopRead()
        self.stopThread = False
        self.readThread.start()

class TangoDeviceClient(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
#        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.timeVector = None
        self.xData = None
        self.xDataTemp = None

        self.setupLayout()

        splash.showMessage('Initializing devices', alignment=QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
        app.processEvents()
        
        self.devices = {}
        self.devices['oscilloscope'] = pt.DeviceProxy('testfel/gunlaser/redpitaya1')

        splash.showMessage('Reading startup attributes', alignment=QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
        app.processEvents()

        timeVectorAttr = self.devices['oscilloscope'].read_attribute('timevector')
        self.timeVector = timeVectorAttr.value

        trigInit = self.devices['oscilloscope'].read_attribute('triggerlevel')
        self.triggerLevelWidget.setAttributeWriteValue(trigInit.value)
        self.triggerLevelLine.setValue(trigInit.value)
        self.triggerDrag = False

        splash.showMessage('Initializing attributes', alignment=QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
        app.processEvents()

        self.guiLock = threading.Lock()                
        self.attributes = {}
        self.attributes['waveform1'] = AttributeClass('waveform1', self.devices['oscilloscope'], 0.1)
        self.attributes['waveform2'] = AttributeClass('waveform2', self.devices['oscilloscope'], 0.1)
        self.attributes['triggerlevel'] = AttributeClass('triggerlevel', self.devices['oscilloscope'], 0.3)
        self.attributes['triggerdelay'] = AttributeClass('triggerdelay', self.devices['oscilloscope'], 0.3)
        self.attributes['recordlength'] = AttributeClass('recordlength', self.devices['oscilloscope'], 0.3)
        self.attributes['samplerate'] = AttributeClass('samplerate', self.devices['oscilloscope'], 0.3)
        self.attributes['status'] = AttributeClass('status', self.devices['oscilloscope'], 0.3)
        self.attributes['state'] = AttributeClass('state', self.devices['oscilloscope'], 0.3)

        self.attributes['waveform1'].attrSignal.connect(self.readWaveform1)
        self.attributes['waveform2'].attrSignal.connect(self.readWaveform2)
        self.attributes['triggerlevel'].attrSignal.connect(self.readTriggerLevel)
        self.attributes['triggerdelay'].attrSignal.connect(self.readTriggerDelay)
        self.attributes['recordlength'].attrSignal.connect(self.readRecordLength)
        self.attributes['samplerate'].attrSignal.connect(self.readSampleRate)
        self.attributes['status'].attrSignal.connect(self.readStatus)
        self.attributes['state'].attrSignal.connect(self.readState)
                  
        splash.showMessage('Setting up variables', alignment=QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
        app.processEvents()


        
    def checkDevices(self):
        for a in self.attributes.itervalues():
            pass
#            a.attr_read()
    
    def readState(self, data):
        self.oscilloscopeName.setState(data.value)
        data.value = ''
        self.onOffCommands.setStatus(data)

    def readStatus(self, data):
        pass
#        self.onOffCommands.setStatus(data.value, data.quality)

    def readTriggerDelay(self, data):
        data.value = data.value * 1e6
        self.triggerDelayWidget.setAttributeValue(data)

    def writeTriggerDelay(self):
        self.guiLock.acquire()
        w = self.triggerDelayWidget.getWriteValue()
        self.attributes['triggerdelay'].attr_write(w * 1e-6)
        self.guiLock.release()

    def readRecordLength(self, data):
        self.recordLengthWidget.setAttributeValue(data)

    def writeRecordLength(self):
        self.guiLock.acquire()
        w = self.recordLengthWidget.getWriteValue()
        self.attributes['recordlength'].attr_write(w)
        self.guiLock.release()
        self.getTimevector()

    def readSampleRate(self, data):
        self.sampleRateWidget.setAttributeValue(data)

    def writeSampleRate(self):
        print 'write sample rate'
        self.guiLock.acquire()
        w = self.sampleRateWidget.getWriteValue()
        self.attributes['samplerate'].attr_write(w)
        self.guiLock.release()
        self.getTimevector()

    def readTriggerLevel(self, data):
        self.triggerLevelWidget.setAttributeValue(data)
        if self.triggerDrag == False:
            self.triggerLevelLine.setPos(data.value)

    def writeTriggerLevel(self):
        self.guiLock.acquire()
        w = self.triggerLevelWidget.getWriteValue()
        self.attributes['triggerlevel'].attr_write(w)
        self.guiLock.release()
        
    def triggerPosChanged(self):
        print 'Trig at ', self.triggerLevelLine.value()
        self.triggerDrag = True
        w = self.triggerLevelLine.value()
        self.triggerLevelWidget.setAttributeWriteValue(w)

    def triggerPosFinished(self):
        print 'FINSISHED DRAGGING'
        self.triggerDrag = False
        self.guiLock.acquire()
        w = self.triggerLevelWidget.getWriteValue()
        self.attributes['triggerlevel'].attr_write(w)
        self.guiLock.release()
        
    def readWaveform1(self, data):
        if self.timeVector == None:
            self.oscilloscopePlot1.setSpectrum(0, data.value)
        elif self.timeVector.shape[0] != data.value.shape[0]:
            self.getTimevector()
        else:
            self.oscilloscopePlot1.setSpectrum(xData=self.timeVector, yData=data)
#        self.oscilloscopePlot1.update()
        
    def readWaveform2(self, data):
        if self.timeVector == None:
            self.waveform2Plot.setData(data.value)
        elif self.timeVector.shape[0] != data.value.shape[0]:
            self.getTimevector()
        else:
            self.waveform2Plot.setData(x=self.timeVector, y=data.value, antialias=True)
#        self.oscilloscopePlot1.update()        
        
    def getTimevector(self):
        timeVectorAttr = self.devices['oscilloscope'].read_attribute('timevector')
        self.timeVector = timeVectorAttr.value        
        
    def initOscilloscope(self):
        self.devices['oscilloscope'].command_inout('init')

    def startOscilloscope(self):
        self.devices['oscilloscope'].command_inout('start')

    def stopOscilloscope(self):
        self.devices['oscilloscope'].command_inout('stop')
        
    def setupAttributeLayout(self, attributeList=[]):
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
            a.readThread.join()
        event.accept()
        
    def setupLayout(self):
        s = 'QWidget{background-color: #000000; }'
        self.setStyleSheet(s)
        
        self.frameSizes = qw.QTangoSizes()
        self.frameSizes.readAttributeWidth = 240
        self.frameSizes.writeAttributeWidth = 299
        self.frameSizes.fontStretch = 80
        self.frameSizes.fontType = 'Segoe UI'
#        self.frameSizes.fontType = 'Trebuchet MS'
        self.attrSizes = qw.QTangoSizes()
        self.attrSizes.barHeight = 20
        self.attrSizes.barWidth = 60
        self.attrSizes.readAttributeWidth = 300
#        self.attrSizes.writeAttributeWidth = 299
        self.attrSizes.fontStretch = 80
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
        layoutData.setMargin(self.attrSizes.barHeight / 2)
        layoutData.setSpacing(self.attrSizes.barHeight / 2)
        self.layoutAttributes = QtGui.QVBoxLayout()
        self.layoutAttributes.setMargin(0)
        self.layoutAttributes.setSpacing(self.attrSizes.barHeight / 2)
        self.layoutAttributes.setContentsMargins(0, 0, 0, 0)
        
        self.title = qw.QTangoTitleBar('Gunlaser oscilloscope')
        self.sidebar = qw.QTangoSideBar(colors=self.colors, sizes=self.frameSizes)
#          self.sidebar.addCmdButton('Init', self.initOscilloscope)
#          self.sidebar.addCmdButton('On', self.onOscilloscope)
#          self.sidebar.addCmdButton('Off', self.offOscilloscope)
#          self.sidebar.addCmdButton('Stop', self.stopOscilloscope)
        self.bottombar = qw.QTangoHorizontalBar()
        self.oscilloscopeName = qw.QTangoDeviceNameStatus(colors=self.colors, sizes=self.frameSizes)
        self.oscilloscopeName.setAttributeName('Oscilloscope')
                
        self.onOffCommands = qw.QTangoCommandSelection('Commands', colors=self.colors, sizes=self.attrSizes)
        self.onOffCommands.addCmdButton('Init', self.initOscilloscope)
        self.onOffCommands.addCmdButton('Start', self.startOscilloscope)
        self.onOffCommands.addCmdButton('Stop', self.stopOscilloscope)
        self.triggerLevelWidget = qw.QTangoWriteAttributeSlider(colors=self.colors, sizes=self.attrSizes)
        self.triggerLevelWidget.setAttributeName('Trigger level', 'V')
        self.triggerLevelWidget.setAttributeWarningLimits([-10, 10])
        self.triggerLevelWidget.writeValueSpinbox.editingFinished.connect(self.writeTriggerLevel)
        self.triggerLevelWidget.setSliderLimits(-2, 2)
        self.triggerLevelWidget.setAttributeValueLimits([-2, 2])
        self.triggerDelayWidget = qw.QTangoWriteAttributeSlider(colors=self.colors, sizes=self.attrSizes)
        self.triggerDelayWidget.setAttributeName('Trigger delay', 'us')
        self.triggerDelayWidget.setAttributeWarningLimits([-1000, 1000])
        self.triggerDelayWidget.writeValueSpinbox.editingFinished.connect(self.writeTriggerDelay)
        self.triggerDelayWidget.setSliderLimits(-200, 200)
        self.recordLengthWidget = qw.QTangoWriteAttributeSlider(colors=self.colors, sizes=self.attrSizes)
        self.recordLengthWidget.setAttributeName('Record length', 'samples')
        self.recordLengthWidget.setAttributeWarningLimits([0, 16000])
        self.recordLengthWidget.writeValueSpinbox.editingFinished.connect(self.writeRecordLength)
        self.recordLengthWidget.setSliderLimits(0, 12000)
        self.sampleRateWidget = qw.QTangoWriteAttributeSlider(colors=self.colors, sizes=self.attrSizes)
        self.sampleRateWidget.setAttributeName('Samplerate', 'sps')
        self.sampleRateWidget.setAttributeWarningLimits([0, 1.25e8])
        self.sampleRateWidget.writeValueSpinbox.editingFinished.connect(self.writeSampleRate)
        self.sampleRateWidget.setSliderLimits(0, 1.25e8)

        self.oscilloscopePlot1 = qw.QTangoReadAttributeSpectrum(colors=self.colors, sizes=self.attrSizes)
        self.oscilloscopePlot1.setAttributeName('Waveforms')
        self.oscilloscopePlot1.setXRange(0, 1e-5)
        self.oscilloscopePlot1.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

        self.oscilloscopePlot1.spectrum.spectrumCurve.setPen(self.colors.secondaryColor2, width=1.5)
        self.waveform2Plot = self.oscilloscopePlot1.spectrum.plot(np.zeros(1000))
        self.waveform2Plot.setPen(self.colors.secondaryColor1, width=1.5)
        
        self.triggerLevelLine = pg.InfiniteLine(pos=0, angle=0, movable=True)
        self.triggerLevelLine.setPen(self.colors.primaryColor1)
        self.oscilloscopePlot1.spectrum.addItem(self.triggerLevelLine)
        self.triggerLevelLine.sigDragged.connect(self.triggerPosChanged)
        self.triggerLevelLine.sigPositionChangeFinished.connect(self.triggerPosFinished)
                
        layout2.addWidget(self.title)        
        layout2.addLayout(layoutData)
        layoutData.addLayout(self.layoutAttributes)
        layoutData.addWidget(self.oscilloscopePlot1)
                        
        self.layoutAttributes.addWidget(self.oscilloscopeName)
        self.layoutAttributes.addWidget(self.onOffCommands)
        self.layoutAttributes.addSpacerItem(spacerItemV)
        self.layoutAttributes.addWidget(self.triggerLevelWidget)
        self.layoutAttributes.addWidget(self.triggerDelayWidget)
        self.layoutAttributes.addWidget(self.recordLengthWidget)
        self.layoutAttributes.addWidget(self.sampleRateWidget)
        
        layout1.addWidget(self.sidebar)
        layout1.addLayout(layout2)
        layout0.addLayout(layout1)
        layout0.addWidget(self.bottombar)
        
        self.resize(800, 400)
        
        self.update()
        
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    
    splash_pix = QtGui.QPixmap('splash_loading.png')
    splash = QtGui.QSplashScreen(splash_pix, QtCore.Qt.WindowStaysOnTopHint)
    splash.setMask(splash_pix.mask())
    splash.show()
    splash.showMessage('Importing modules', alignment=QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
    app.processEvents()

    import QTangoWidgets.QTangoWidgets as qw
    import pyqtgraph as pg
    import PyTango as pt
    import threading
    import numpy as np

    splash.showMessage('Starting GUI', alignment=QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
    app.processEvents()
    myapp = TangoDeviceClient()
    myapp.show()
    splash.finish(myapp)
    sys.exit(app.exec_())    
