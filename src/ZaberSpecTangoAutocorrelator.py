# -*- coding:utf-8 -*-
"""
Created on Feb 1, 2016

@author: m
"""

from PyQt4 import QtGui, QtCore

import time
import sys
sys.path.insert(0, '../../guitests/src/QTangoWidgets')

import pyqtgraph as pq
import PyTango as pt
import threading
import numpy as np
# import QTangoWidgets as qw
from AttributeReadThreadClass import AttributeClass


redpitayaName = 'b-v0-gunlaser-csdb-0:10000/gunlaser/devices/redpitaya2'
motorName = 'gunlaser/motors/zaber01'
spectrometerName = pt.DeviceProxy('gunlaser/devices/spectrometer_diag')

class TangoDeviceClient(QtGui.QWidget):
    def __init__(self, redpitayaName, specName, motorName, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.settings = QtCore.QSettings('Maxlab', 'RedpitayaTangoAutocorrelation')

#        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.timeVector = None
        self.xData = None
        self.xDataTemp = None

        self.redpitayaName = redpitayaName
        self.motorName = motorName
        self.spectrometerName = spectrometerName

        self.title = 'FROG'



        t0 = time.clock()
        print time.clock() - t0, ' s'

        self.guiLock = threading.Lock()
        self.positionOffset = 0.0

        print "Getting osc device"
        self.oscDev = pt.DeviceProxy('gunlaser/devices/redpitaya2')
        print '...connected'

        print "Getting spectrometer device"
        self.specDev = pt.DeviceProxy(self.spectrometerName)
        print '...connected'

        print 'Getting motor device...'
        self.motorDev = pt.DeviceProxy('gunlaser/motors/zaber01')
        print '...connected'


        self.wavelengthVector = self.specDev.read_attribute('Wavelengths')


        #=======================================================================
        # self.devices = {}
        # self.devices['redpitaya'] = pt.DeviceProxy(self.redpitayaName)
        # self.devices['motor'] = pt.DeviceProxy(self.motorName)
        # self.devices['spectrometer'] = pt.DeviceProxy(self.spectrometerName)
        #=======================================================================

        self.attributes = {}
        self.attributes['Wavelengths'] = AttributeClass('Wavelengths', self.specDev, None)
        self.attributes['spectrum1'] = AttributeClass('Spectrum', self.specDev, 0.05)
        self.attributes['position'] = AttributeClass('position', self.motorDev, 0.05)
        self.attributes['Speed'] = AttributeClass('Speed', self.motorDev, 0.05)
        self.specState['specState'] = AttributeClass('State', self.specDev, 0.05)


        self.setLocale(QtCore.QLocale(QtCore.QLocale.English))
        self.layout = QtGui.QVBoxLayout(self)
        self.gridLayout1 = QtGui.QGridLayout()
        self.gridLayout2 = QtGui.QGridLayout()
        self.gridLayout3 = QtGui.QGridLayout()
        self.gridLayout4 = QtGui.QGridLayout()


        self.startPosSpinbox = QtGui.QDoubleSpinBox()
        self.startPosSpinbox.setDecimals(3)
        self.startPosSpinbox.setMaximum(2000000)
        self.startPosSpinbox.setMinimum(-2000000)
        self.startPosSpinbox.setValue(46.8)
        self.stepSizeSpinbox = QtGui.QDoubleSpinBox()
        self.stepSizeSpinbox.setDecimals(3)
        self.stepSizeSpinbox.setMaximum(2000000)
        self.stepSizeSpinbox.setMinimum(-2000000)
        self.stepSizeSpinbox.setValue(0.05)
        self.currentPosSpinbox = QtGui.QDoubleSpinBox()
        self.currentPosSpinbox.setDecimals(3)
        self.currentPosSpinbox.setMaximum(2000000)
        self.currentPosSpinbox.setMinimum(-2000000)
        self.averageSpinbox = QtGui.QSpinBox()
        self.averageSpinbox.setMaximum(100)
        self.averageSpinbox.setValue(self.settings.value('averages', 5).toInt()[0])
        self.averageSpinbox.editingFinished.connect(self.setAverage)
        self.setPosSpinbox = QtGui.QDoubleSpinBox()
        self.setPosSpinbox.setDecimals(3)
        self.setPosSpinbox.setMaximum(2000000)
        self.setPosSpinbox.setMinimum(-2000000)
        self.setPosSpinbox.setValue(63.7)
        self.setPosSpinbox.setValue(self.settings.value('setPos', 63).toDouble()[0])
        self.setPosSpinbox.editingFinished.connect(self.writePosition)
        self.currentPosLabel = QtGui.QLabel()
        f = self.currentPosLabel.font()
        f.setPointSize(14)
        currentPosTextLabel = QtGui.QLabel('Current pos ')
        currentPosTextLabel.setFont(f)
        self.currentPosLabel.setFont(f)
        self.currentSpeedLabel = QtGui.QLabel()


        self.startButton = QtGui.QPushButton('Start')
        self.startButton.clicked.connect(self.startScan)
        self.stopButton = QtGui.QPushButton('Stop')
        self.stopButton.clicked.connect(self.stopScan)
        self.exportButton = QtGui.QPushButton('Export')
        self.exportButton.clicked.connect(self.exportScan)

        self.pos = self.motorDev.read_attribute('position').value
        self.currentPosSpinbox.setValue(self.pos)


        self.gridLayout1.addWidget(QtGui.QLabel("Start position"), 0, 0)
        self.gridLayout1.addWidget(self.startPosSpinbox, 0, 1)
        self.gridLayout1.addWidget(QtGui.QLabel("Step size"), 1, 0)
        self.gridLayout1.addWidget(self.stepSizeSpinbox, 1, 1)
        self.gridLayout1.addWidget(QtGui.QLabel("Averages"), 2, 0)
        self.gridLayout1.addWidget(self.averageSpinbox, 2, 1)
        self.gridLayout2.addWidget(QtGui.QLabel("Set position"), 0, 0)
        self.gridLayout2.addWidget(self.setPosSpinbox, 0, 1)
        self.gridLayout2.addWidget(QtGui.QLabel("Start scan"), 1, 0)
        self.gridLayout2.addWidget(self.startButton, 1, 1)
        self.gridLayout2.addWidget(QtGui.QLabel("Stop scan"), 2, 0)
        self.gridLayout2.addWidget(self.stopButton, 2, 1)
        self.gridLayout2.addWidget(QtGui.QLabel("Export scan"), 3, 0)
        self.gridLayout2.addWidget(self.exportButton, 3, 1)
        self.gridLayout3.addWidget(currentPosTextLabel, 0, 0)
        self.gridLayout3.addWidget(self.currentPosLabel, 0, 1)
        self.gridLayout3.addWidget(QtGui.QLabel("Current speed"), 1, 0)
        self.gridLayout3.addWidget(self.currentSpeedLabel, 1, 1)

        # spectrometer buttons
        self.specInitButton = QtGui.QPushButton('Init')
        self.specInitButton.clicked.connect(self.initSpectrometer)
        self.specOnButton = QtGui.QPushButton('On')
        self.specOnButton.clicked.connect(self.onSpectrometer)
        self.specOffButton = QtGui.QPushButton('Off')
        self.specOffButton.clicked.connect(self.offSpectrometer)
        self.specStopButton = QtGui.QPushButton('Stop')
        self.specStopButton.clicked.connect(self.stopSpectrometer)

        #self.specStopButton.clicked.connect(self.readSpectrometerState)


        self.SpectrometerStatusLabel = QtGui.QLabel()
        SpectrometerStatusTextLabel= QtGui.QLabel('Spec Status')
        self.specStatus = self.specDev.read_attribute('State').value
        #=======================================================================
        # self.SpectrometerStatusLabel.setValue(self.specStatus)
        #=======================================================================


        self.gridLayout4.addWidget(QtGui.QLabel("Init"), 1, 0)
        self.gridLayout4.addWidget(self.specInitButton, 1, 1)
        self.gridLayout4.addWidget(QtGui.QLabel("On"), 2, 0)
        self.gridLayout4.addWidget(self.specOnButton, 2, 1)
        #=======================================================================
        # self.gridLayout4.addWidget(QtGui.QLabel("Off"), 3, 0)
        # self.gridLayout4.addWidget(self.specOffButton, 3, 1)
        #=======================================================================
        self.gridLayout4.addWidget(QtGui.QLabel("Stop"), 3, 0)
        self.gridLayout4.addWidget(self.specStopButton, 3, 1)
        self.gridLayout4.addWidget(SpectrometerStatusTextLabel, 4, 0)
        self.gridLayout4.addWidget(self.SpectrometerStatusLabel, 4, 1)


        # plots
        self.plotWidget = pq.PlotWidget(useOpenGL=True)
        self.SpectrumPlot = self.plotWidget.plot()
        self.SpectrumPlot.setPen((200, 25, 10))
        self.SpectrumPlot.antialiasing = True
        self.plotWidget.setAntialiasing(True)
        self.plotWidget.showGrid(True, True)

        plotLayout = QtGui.QHBoxLayout()
        plotLayout.addWidget(self.plotWidget)

        #adding layouts        gridLay = QtGui.QHBoxLayout()
        gridLay = QtGui.QHBoxLayout()
        gridLay.addLayout(self.gridLayout1)
        gridLay.addSpacerItem(QtGui.QSpacerItem(30, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum))
        gridLay.addLayout(self.gridLayout2)
        gridLay.addSpacerItem(QtGui.QSpacerItem(30, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum))
        gridLay.addLayout(self.gridLayout3)
        gridLay.addSpacerItem(QtGui.QSpacerItem(30, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum))
        gridLay.addLayout(self.gridLayout4)
        gridLay.addSpacerItem(QtGui.QSpacerItem(30, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum))
        self.layout.addLayout(gridLay)
        self.layout.addLayout(plotLayout)


        self.waveform1 = np.zeros(4000)
        self.waveform2 = np.zeros(4000)
        self.trendData1 = np.zeros(600)
        self.trendData2 = np.zeros(600)
        self.scanData = np.array([])
        self.timeData = np.array([])
        self.posData = np.array([])
        self.avgSamples = 5
        self.currentSample = 0
        self.avgData = 0
        self.targetPos = 0.0
        self.measureUpdateTimes = np.array([time.time()])
        self.lock = threading.Lock()

        self.spectrum = np.array([])

        self.running = False
        self.scanning = False
        self.moving = False
        self.moveStart = False
        self.scanTimer = QtCore.QTimer()
        self.scanTimer.timeout.connect(self.scanUpdateAction)

        self.settings = QtCore.QSettings('Maxlab', 'RedpitayaTangoAutocorrelation')


        specLayout = QtGui.QHBoxLayout()


        self.resize(800,400)
        self.update()


    def readSpectrometerState(self, data):
        print 'reading spectrometer status'
        self.SpectrometerStatusLabel.setText('status here')
        self.spectrometerName.setState(data)
        self.onOffCommands.setStatus(data)

    def readPeakEnergy(self, data):
        self.attributes['PeakEnergy'] = data.value

    def readPeakWidth(self, data):
        self.attributes['PeakWidth'] = data.value

    def readExposure(self, data):
#        self.exposureWidget.setAttributeValue(data.value)
        self.attributes['Exposure'] = data.value

    def writeExposure(self):
        self.guiLock.acquire()
        w = self.exposureWidget.getWriteValue()
        self.attributes['exposure'].attr_write(w)
        self.guiLock.release()

    def readSpectrum(self, data):
        if self.timeVector == None:
            self.SpectrumPlot.setSpectrum(0, data.value)
        else:
            self.SpectrumPlot.setData(xData = self.WavelengthVector, yData = data)
        self.SpectrumPlot.update()

    #===========================================================================
    # def readSpectrum(self, data):
    #     if data.value.shape[0] != self.timeVector.shape[0]:
    #         self.attributes['Wavelengths'] = AttributeClass('Wavelengths', self.devices['spectrometer'], None)
    #         self.attributes['Wavelengths'].attrSignal.connect(self.readWavelengthvector)
    #     else:
    #         self.plot2.setData(y=data.value)
    #         self.spectrum = data.value
    #         self.plot2.update()
    #===========================================================================

    #===========================================================================
    # def readWaveform1(self, data):
    #     if data.value.shape[0] != self.timeVector.shape[0]:
    #         self.attributes['timevector'] = AttributeClass('timevector', self.devices['redpitaya'], None)
    #         self.attributes['timevector'].attrSignal.connect(self.readTimevector)
    #     else:
    #         self.plot2.setData(y=data.value)
    #         self.waveform1 = data.value
    #         self.measureData()
    #         self.plot2.update()
    #===========================================================================

    def initSpectrometer(self):
        print 'Spectrometer INIT'
        self.specDev.command_inout('init')

    def onSpectrometer(self):
        print 'Spectrometer ON'
        self.specDev.command_inout('on')

    def offSpectrometer(self):
        print 'Spectrometer OFF'
        self.specDev.command_inout('off')

    def stopSpectrometer(self):
        print 'Spectrometer STOP'
        self.specDev.command_inout('stop')

    #===========================================================================
    # def setupAttributeLayout(self, attributeList = []):
    #     self.attributeQObjects = []
    #     for att in attributeList:
    #         attQObject = qw.QTangoReadAttributeDouble()
    #         attQObject.setAttributeName(att.name)
    #         self.attributeQObjects.append(attQObject)
    #         self.layoutAttributes.addWidget(attQObject)
    #===========================================================================

    def readWavelengthvector(self,data):
        self.Wavelengthvector = data.value

    def readPosition(self, data):
        self.currentPosLabel.setText(QtCore.QString.number(data.value, 'f', 3))
        if np.abs(self.targetPos - data.value) < 0.01:
            self.moveStart = False
            self.moving = False

    def readSpeed(self, data):
        try:
            self.currentSpeedLabel.setText(QtCore.QString.number(data.value, 'f', 3))
            if self.moveStart == True:
                if data.value > 0.01:
                    self.moving = True
                    self.moveStart = False
            if self.moving == True:
                if np.abs(data.value) < 0.01:
                    self.moving = False
        except:
            pass

    def writePosition(self):
        w = self.setPosSpinbox.value()
        self.attributes['position'].attr_write(w)

    def setAverage(self):
        self.avgSamples = self.averageSpinbox.value()

    def startScan(self):
        self.scanData = np.array([])
        self.timeData = np.array([])
        self.scanning = True
        self.motorDev.write_attribute('position', self.startPosSpinbox.value())
        newPos = self.startPosSpinbox.value()
        self.pos = self.motorDev.read_attribute('position').value
        self.currentPosSpinbox.setValue(self.pos)
        print 'Moving from ', self.pos
        motorState = self.motorDev.state()
#        while self.pos != self.startPosSpinbox.value():
        while (np.abs(self.pos - newPos) > 0.005) or (motorState == pt.DevState.MOVING):
            time.sleep(0.25)
            self.pos = self.motorDev.read_attribute('position').value
            self.currentPosSpinbox.setValue(self.pos)
            motorState = self.motorDev.state()
            self.update()
        self.scanTimer.start(100 * self.avgSamples)


    def stopScan(self):
        print 'Stopping scan'
        self.running = False
        self.scanning = False
        self.scanTimer.stop()

    def exportScan(self):
        print 'Exporting scan data'
        data = np.vstack((self.posData, self.timeData, self.scanData)).transpose()
        filename = ''.join(('scandata_', time.strftime('%Y-%m-%d_%Hh%M'), '.txt'))
        np.savetxt(filename, data)

    def scanUpdateAction(self):
        self.scanTimer.stop()
        while self.running == True:
            time.sleep(0.1)
        newPos = self.targetPos + self.stepSizeSpinbox.value()
        print 'New pos: ', newPos
        self.attributes['position'].attr_write(newPos)
        self.targetPos = newPos
        self.running = True
        self.moveStart = True

    def measureScanData(self):
        self.avgData = self.trendData1[-self.avgSamples:].mean()
        self.scanData = np.hstack((self.scanData, self.avgData))
        pos = np.double(str(self.currentPosLabel.text()))
        newTime = (pos - self.startPosSpinbox.value()) * 2 * 1e-3 / 299792458.0
        self.timeData = np.hstack((self.timeData, newTime))
        self.posData = np.hstack((self.posData, pos * 1e-3))
        if self.timeUnitsRadio.isChecked() == True:
            self.plot5.setData(x=self.timeData * 1e12, y=self.scanData)
        else:
            self.plot5.setData(x=self.posData * 1e3, y=self.scanData)

    def measureData(self):
        if self.running == True and self.moving == False:
            data = self.devices['redpitaya'].read_attributes(['waveform1', 'waveform2'])
            self.waveform1 = data[0].value
            self.waveform2 = data[1].value
        goodInd = np.arange(self.signalStartIndex.value(), self.signalEndIndex.value() + 1, 1)
        bkgInd = np.arange(self.backgroundStartIndex.value(), self.backgroundEndIndex.value() + 1, 1)
        bkg = self.waveform1[bkgInd].mean()
        bkgPump = self.waveform2[bkgInd].mean()
        autoCorr = (self.waveform1[goodInd] - bkg).sum()
        pump = (self.waveform2[goodInd] - bkgPump).sum()
#        pump = 1.0
        if self.normalizePumpCheck.isChecked() == True:
            try:
                self.trendData1 = np.hstack((self.trendData1[1:], autoCorr / pump))
            except:
                pass
        else:
            self.trendData1 = np.hstack((self.trendData1[1:], autoCorr))
        self.plot3.setData(y=self.trendData1)

        # Evaluate the fps
        t = time.time()
        if self.measureUpdateTimes.shape[0] > 10:
            self.measureUpdateTimes = np.hstack((self.measureUpdateTimes[1:], t))
        else:
            self.measureUpdateTimes = np.hstack((self.measureUpdateTimes, t))
        fps = 1 / np.diff(self.measureUpdateTimes).mean()
        self.fpsLabel.setText(QtCore.QString.number(fps, 'f', 1))

        # If we are running a scan, update the scan data
        if self.running == True:
            if self.moving == False and self.moveStart == False:
                self.currentSample += 1
                if self.currentSample >= self.avgSamples:
                    self.running = False
                    self.measureScanData()
                    self.currentSample = 0
                    self.scanUpdateAction()

    def xAxisUnitsToggle(self):
        if self.timeUnitsRadio.isChecked() == True:
            self.plot5.setData(x=self.timeData * 1e12, y=self.scanData)
        else:
            self.plot5.setData(x=self.posData * 1e3, y=self.scanData)

#===============================================================================
#     def closeEvent(self, event):
#         for a in self.attributes.itervalues():
#             print 'Stopping', a.name
#             a.stopRead()
#         for a in self.attributes.itervalues():
#             a.readThread.join()
#
#         self.settings.setValue('startPos', self.startPosSpinbox.value())
#         self.settings.setValue('setPos', self.setPosSpinbox.value())
#         self.settings.setValue('averages', self.averageSpinbox.value())
#         self.settings.setValue('step', self.stepSizeSpinbox.value())
#         self.settings.setValue('startInd', self.signalStartIndex.value())
#         self.settings.setValue('endInd', self.signalEndIndex.value())
#         self.settings.setValue('bkgStartInd', self.backgroundStartIndex.value())
#         self.settings.setValue('bkgEndInd', self.backgroundEndIndex.value())
#         self.settings.setValue('xUnitTime', self.timeUnitsRadio.isChecked())
#         self.settings.sync()
#         event.accept()
#===============================================================================

    def setupLayout(self):
        self.setLocale(QtCore.QLocale(QtCore.QLocale.English))
        self.layout = QtGui.QVBoxLayout(self)
        self.gridLayout1 = QtGui.QGridLayout()
        self.gridLayout2 = QtGui.QGridLayout()
        self.gridLayout3 = QtGui.QGridLayout()
        self.gridLayout4 = QtGui.QGridLayout()
        self.gridLayout5 = QtGui.QGridLayout()

        self.fpsLabel = QtGui.QLabel()
        self.averageSpinbox = QtGui.QSpinBox()
        self.averageSpinbox.setMaximum(100)
        self.averageSpinbox.setValue(self.settings.value('averages', 5).toInt()[0])
        self.averageSpinbox.editingFinished.connect(self.setAverage)

        #=======================================================================
        # self.startPosSpinbox = QtGui.QDoubleSpinBox()
        # self.startPosSpinbox.setDecimals(3)
        # self.startPosSpinbox.setMaximum(2000000)
        # self.startPosSpinbox.setMinimum(-2000000)
        #=======================================================================
        self.startPosSpinbox.setValue(46.8)
        self.stepSizeSpinbox = QtGui.QDoubleSpinBox()
        self.stepSizeSpinbox.setDecimals(3)
        self.stepSizeSpinbox.setMaximum(2000000)
        self.stepSizeSpinbox.setMinimum(-2000000)
        self.stepSizeSpinbox.setValue(self.settings.value('step', 0.05).toDouble()[0])
        self.setPosSpinbox = QtGui.QDoubleSpinBox()
        self.setPosSpinbox.setDecimals(3)
        self.setPosSpinbox.setMaximum(2000000)
        self.setPosSpinbox.setMinimum(-2000000)
        self.setPosSpinbox.setValue(63.7)
        self.setPosSpinbox.setValue(self.settings.value('setPos', 63).toDouble()[0])
        self.setPosSpinbox.editingFinished.connect(self.writePosition)
        self.currentPosLabel = QtGui.QLabel()
        f = self.currentPosLabel.font()
        f.setPointSize(28)
        currentPosTextLabel = QtGui.QLabel('Current pos ')
        currentPosTextLabel.setFont(f)
        self.currentPosLabel.setFont(f)
        self.currentSpeedLabel = QtGui.QLabel()
#        self.currentSpeedLabel.setFont(f)

        self.signalStartIndex = QtGui.QSpinBox()
        self.signalStartIndex.setMinimum(0)
        self.signalStartIndex.setMaximum(16384)
        self.signalStartIndex.setValue(self.settings.value('startInd', 1050).toInt()[0])
        self.signalEndIndex = QtGui.QSpinBox()
        self.signalEndIndex.setMinimum(0)
        self.signalEndIndex.setMaximum(16384)
        self.signalEndIndex.setValue(self.settings.value('endInd', 1150).toInt()[0])
        self.backgroundStartIndex = QtGui.QSpinBox()
        self.backgroundStartIndex.setMinimum(0)
        self.backgroundStartIndex.setMaximum(16384)
        self.backgroundStartIndex.setValue(self.settings.value('bkgStartInd', 900).toInt()[0])
        self.backgroundEndIndex = QtGui.QSpinBox()
        self.backgroundEndIndex.setMinimum(0)
        self.backgroundEndIndex.setMaximum(16384)
        self.backgroundEndIndex.setValue(self.settings.value('bkgEndInd', 1000).toInt()[0])

        self.timeUnitsRadio = QtGui.QRadioButton('ps')
        self.posUnitsRadio = QtGui.QRadioButton('mm')
        if self.settings.value('xUnitTime', True).toBool() == True:
            self.timeUnitsRadio.setChecked(True)
        else:
            self.posUnitsRadio.setChecked(True)
        self.timeUnitsRadio.toggled.connect(self.xAxisUnitsToggle)


        self.startButton = QtGui.QPushButton('Start')
        self.startButton.clicked.connect(self.startScan)
        self.stopButton = QtGui.QPushButton('Stop')
        self.stopButton.clicked.connect(self.stopScan)
        self.exportButton = QtGui.QPushButton('Export')
        self.exportButton.clicked.connect(self.exportScan)


        self.gridLayout2.addWidget(self.startPosSpinbox, 2, 1)

        self.spectrometerInit = QtGui.QPushButton('Spec Init')
        self.spectrometerInit.clicked.connect(self.initSpectrometer)
        self.spectrometerOn = QtGui.QPushButton('Spec On')
        self.spectrometerOn.clicked.connect(self.onSpectrometer)
        self.spectrometerOff = QtGui.QPushButton('Spec Off')
        self.spectrometerOff.clicked.connect(self.offSpectrometer)
        self.spectrometerStop = QtGui.QPushButton('Spec Stop')
        self.spectrometerStop.clicked.connect(self.stopSpectrometer)


        #spectrum = self.devices['spectrometer'].read_attributes(['spectrum'])


        self.fpsLabel = QtGui.QLabel()

        #=======================================================================
        # self.peakWidthWidget = qw.QTangoReadAttributeSlider2(colors = self.colors, sizes = self.attrSizes)
        # self.peakWidthWidget.setAttributeName('Spectral width')
        # self.peakWidthWidget.setAttributeWarningLimits((20, 70))
        # self.peakWidthWidget.setSliderLimits(0, 100)
        # self.peakEnergyWidget = qw.QTangoReadAttributeSlider2(colors = self.colors, sizes = self.attrSizes)
        # self.peakEnergyWidget.setAttributeName('Laser energy')
        # self.peakEnergyWidget.setAttributeWarningLimits((0.5, 5))
        # self.peakEnergyWidget.setSliderLimits(0, 2)
        # self.exposureWidget = qw.QTangoWriteAttributeSlider(colors = self.colors, sizes = self.attrSizes)
        # self.exposureWidget.setAttributeName('Exposure time')
        # self.exposureWidget.setAttributeWarningLimits((10, 900))
        # self.exposureWidget.writeValueSpinbox.editingFinished.connect(self.writeExposure)
        # self.exposureWidget.setSliderLimits(0, 1000)
        #=======================================================================

        #=======================================================================
        # self.oscSpectrumPlot = qw.QTangoReadAttributeSpectrum(colors = self.colors, sizes = self.attrSizes)
        # self.oscSpectrumPlot.setAttributeName('Oscillator spectrum')
        # self.oscSpectrumPlot.setXRange(700, 900)
        # self.oscSpectrumPlot.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        #=======================================================================

        self.gridLayout1.addWidget(QtGui.QLabel("Start position"), 0, 0)
        self.gridLayout1.addWidget(self.startPosSpinbox, 0, 1)
        self.gridLayout1.addWidget(QtGui.QLabel("Step size"), 1, 0)
        self.gridLayout1.addWidget(self.stepSizeSpinbox, 1, 1)
        self.gridLayout1.addWidget(QtGui.QLabel("Averages"), 2, 0)
        self.gridLayout1.addWidget(self.averageSpinbox, 2, 1)
        self.gridLayout1.addWidget(QtGui.QLabel("Normalize"), 3, 0)
        self.gridLayout1.addWidget(self.normalizePumpCheck, 3, 1)
        self.gridLayout2.addWidget(QtGui.QLabel("Set position"), 0, 0)
        self.gridLayout2.addWidget(self.setPosSpinbox, 0, 1)
        self.gridLayout2.addWidget(QtGui.QLabel("Start scan"), 1, 0)
        self.gridLayout2.addWidget(self.startButton, 1, 1)
        self.gridLayout2.addWidget(QtGui.QLabel("Stop scan"), 2, 0)
        self.gridLayout2.addWidget(self.stopButton, 2, 1)
        self.gridLayout2.addWidget(QtGui.QLabel("Export scan"), 3, 0)
        self.gridLayout2.addWidget(self.exportButton, 3, 1)
        self.gridLayout3.addWidget(currentPosTextLabel, 0, 0)
        self.gridLayout3.addWidget(self.currentPosLabel, 0, 1)
        self.gridLayout3.addWidget(QtGui.QLabel("Current speed"), 1, 0)
        self.gridLayout3.addWidget(self.currentSpeedLabel, 1, 1)

        self.gridLayout4.addWidget(QtGui.QLabel("Signal start index"), 0, 0)
        self.gridLayout4.addWidget(self.signalStartIndex, 0, 1)
        self.gridLayout4.addWidget(QtGui.QLabel("Signal end index"), 1, 0)
        self.gridLayout4.addWidget(self.signalEndIndex, 1, 1)
        self.gridLayout4.addWidget(QtGui.QLabel("Background start index"), 2, 0)
        self.gridLayout4.addWidget(self.backgroundStartIndex, 2, 1)
        self.gridLayout4.addWidget(QtGui.QLabel("Background end index"), 3, 0)
        self.gridLayout4.addWidget(self.backgroundEndIndex, 3, 1)

        self.gridLayout5.addWidget(QtGui.QLabel("X-axis units"), 0, 0)
        self.gridLayout5.addWidget(self.timeUnitsRadio, 0, 1)
        self.gridLayout5.addWidget(self.posUnitsRadio, 1, 1)
        self.gridLayout5.addWidget(QtGui.QLabel("FPS"), 2, 0)
        self.gridLayout5.addWidget(self.fpsLabel, 2, 1)


        # plots
        self.plotWidget = pq.PlotWidget(useOpenGL=True)
        self.SpectrumPlot = self.plotWidget.plot()
        self.SpectrumPlot.setPen((200, 25, 10))
        self.SpectrumPlot.antialiasing = True
        self.plotWidget.setAntialiasing(True)
        self.plotWidget.showGrid(True, True)

        #=======================================================================
        # self.plotWidget2 = pq.PlotWidget(useOpenGL=True)
        # self.plot3 = self.plotWidget2.plot()
        # self.plot3.setPen((50, 99, 200))
        # self.plot4 = self.plotWidget2.plot()
        # self.plot4.setPen((10, 200, 25))
        # self.plot3.antialiasing = True
        # self.plotWidget2.setAntialiasing(True)
        # self.plotWidget2.showGrid(True, True)
        #=======================================================================

        #=======================================================================
        # self.plotWidget3 = pq.PlotWidget(useOpenGL=True)
        # self.plot5 = self.plotWidget3.plot()
        # self.plot5.setPen((10, 200, 70))
        # self.plotWidget3.setAntialiasing(True)
        # self.plotWidget3.showGrid(True, True)
        #=======================================================================

        plotLayout = QtGui.QHBoxLayout()
        plotLayout.addWidget(self.plotWidget)
        #=======================================================================
        # plotLayout.addWidget(self.plotWidget2)
        # plotLayout.addWidget(self.plotWidget3)
        #=======================================================================

        gridLay = QtGui.QHBoxLayout()
        gridLay.addLayout(self.gridLayout1)
        gridLay.addSpacerItem(QtGui.QSpacerItem(30, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum))
        gridLay.addLayout(self.gridLayout2)
        gridLay.addSpacerItem(QtGui.QSpacerItem(30, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum))
        gridLay.addLayout(self.gridLayout4)
        gridLay.addSpacerItem(QtGui.QSpacerItem(30, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum))
        gridLay.addLayout(self.gridLayout3)
        gridLay.addSpacerItem(QtGui.QSpacerItem(30, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum))
        gridLay.addLayout(self.gridLayout5)
        gridLay.addSpacerItem(QtGui.QSpacerItem(20, 20, QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Minimum))
        self.layout.addLayout(gridLay)
        self.layout.addLayout(plotLayout)

        self.update()

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    myapp = TangoDeviceClient(redpitayaName, spectrometerName, motorName)
    myapp.show()
    sys.exit(app.exec_())



