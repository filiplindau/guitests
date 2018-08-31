'''
Created on 11 feb 2015

@author: Filip Lindau
'''

# -*- coding:utf-8 -*-
from PyQt4 import QtGui, QtCore

import time
import sys


# noinspection PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit
class TangoDeviceClient(QtGui.QWidget):
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self,parent)
#        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.timeVector = None
        self.errorSampleTime = None
        self.xData = None
        self.xDataTemp = None

        self.setupLayout()

        splash.showMessage('         Initializing devices', alignment = QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
        app.processEvents()

        t0=time.clock()
        self.devices = {}
        self.devices['spectrometer']=pt.DeviceProxy('gunlaser/oscillator/spectrometer')
        self.devices['finesse']=pt.DeviceProxy('gunlaser/oscillator/finesse')
        self.devices['prism1']=pt.DeviceProxy('gunlaser/oscillator/prism1')
        self.devices['prism2']=pt.DeviceProxy('gunlaser/oscillator/prism2')
        self.devices['picomotor']=pt.DeviceProxy('gunlaser/devices/picomotor-0')
        self.devices['halcyon']=pt.DeviceProxy('gunlaser/oscillator/halcyon_raspberry')
        self.devices['redpitaya']=pt.DeviceProxy('gunlaser/devices/redpitaya1')
        print time.clock()-t0, ' s'

        splash.showMessage('         Reading startup attributes', alignment = QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
        app.processEvents()


        self.guiLock = threading.Lock()
        self.attributes = {}
        self.attributes['wavelengths'] = AttributeClass('wavelengthsROI', self.devices['spectrometer'], None)
        self.attributes['peakenergy'] = AttributeClass('peakenergy', self.devices['spectrometer'], 0.3)
        self.attributes['peakwidth'] = AttributeClass('peakwidth', self.devices['spectrometer'], 0.3)
        self.attributes['peakwavelength'] = AttributeClass('peakwavelength', self.devices['spectrometer'], 0.3)
        self.attributes['spectrum'] = AttributeClass('spectrumROI', self.devices['spectrometer'], 0.3)
        self.attributes['spectrometerState'] = AttributeClass('state', self.devices['spectrometer'], 0.3)

        self.attributes['peakenergy'].attrSignal.connect(self.readPeakEnergy)
        self.attributes['peakwidth'].attrSignal.connect(self.readPeakWidth)
        self.attributes['peakwavelength'].attrSignal.connect(self.readPeakWavelength)
        self.attributes['spectrum'].attrSignal.connect(self.readSpectrum)
        self.attributes['wavelengths'].attrSignal.connect(self.readWavelengths)
        self.attributes['spectrometerState'].attrSignal.connect(self.readSpectrometerState)

        self.attributes['pumpPower'] = AttributeClass('power', self.devices['finesse'], 0.3)
        self.attributes['pumpTemp'] = AttributeClass('lasertemperature', self.devices['finesse'], 0.3)
        self.attributes['pumpStatus'] = AttributeClass('status', self.devices['finesse'], 0.3)
        self.attributes['pumpState'] = AttributeClass('state', self.devices['finesse'], 0.3)
        self.attributes['pumpShutterState'] = AttributeClass('shutterstate', self.devices['finesse'], 0.3)
        self.attributes['pumpOperationState'] = AttributeClass('laseroperationstate', self.devices['finesse'], 0.3)

        self.attributes['pumpPower'].attrSignal.connect(self.readPumpPower)
        self.attributes['pumpTemp'].attrSignal.connect(self.readPumpTemp)
        self.attributes['pumpState'].attrSignal.connect(self.readPumpState)
        self.attributes['pumpShutterState'].attrSignal.connect(self.readPumpShutterState)
        self.attributes['pumpOperationState'].attrSignal.connect(self.readPumpOperationState)

        self.attributes['prism1Position'] = AttributeClass('position', self.devices['prism1'], 0.3)
        self.attributes['prism1Limit'] = AttributeClass('limit_switches', self.devices['prism1'], 0.3)
        self.attributes['prism1Position'].attrSignal.connect(self.readPrism1Position)
        self.attributes['prism1Limit'].attrSignal.connect(self.readPrism1Limit)
        self.attributes['prism2Position'] = AttributeClass('position', self.devices['prism2'], 0.3)
        self.attributes['prism2Limit'] = AttributeClass('limit_switches', self.devices['prism2'], 0.3)
        self.attributes['prism2Position'].attrSignal.connect(self.readPrism2Position)
        self.attributes['prism2Limit'].attrSignal.connect(self.readPrism2Limit)

        self.attributes['halcyonPiezoVoltage'] = AttributeClass('piezovoltage', self.devices['halcyon'], 0.3)
        self.attributes['halcyonPiezoVoltage'].attrSignal.connect(self.readPiezoVoltage)
        self.attributes['halcyonPicomotorPosition'] = AttributeClass('picomotorposition', self.devices['halcyon'], 0.3)
        self.attributes['halcyonPicomotorPosition'].attrSignal.connect(self.readPicomotorPosition)
        self.attributes['halcyonFollow'] = AttributeClass('picomotorfollow', self.devices['halcyon'], 0.5)
        self.attributes['halcyonFollow'].attrSignal.connect(self.readPicomotorFollow)
        self.attributes['halcyonModelocked'] = AttributeClass('modelocked', self.devices['halcyon'], 0.3)
        self.attributes['halcyonModelocked'].attrSignal.connect(self.readModelocked)
        self.attributes['halcyonJitter'] = AttributeClass('jitter', self.devices['halcyon'], 0.3)
        self.attributes['halcyonJitter'].attrSignal.connect(self.readJitter)
        self.attributes['halcyonErrorFrequency'] = AttributeClass('errorfrequency', self.devices['halcyon'], 0.3)
        self.attributes['halcyonErrorFrequency'].attrSignal.connect(self.readErrorFrequency)
        self.attributes['halcyonErrorTrace'] = AttributeClass('errortrace', self.devices['halcyon'], 0.3)
        self.attributes['halcyonErrorTrace'].attrSignal.connect(self.readErrorTrace)
        self.attributes['sampleTime'] = AttributeClass('sampletime', self.devices['halcyon'], None)
        self.attributes['sampleTime'].attrSignal.connect(self.readHalcyonSampleTime)

        self.attributes['oscPower'] = AttributeClass('measurementdata1', self.devices['redpitaya'], 0.3)
        self.attributes['oscPower'].attrSignal.connect(self.readRedpitayaPower)

        splash.showMessage('         Setting up variables', alignment = QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
        app.processEvents()

#         self.timer = QtCore.QTimer(self)
#         self.timer.timeout.connect(self.checkDevices)
#         self.timer.start(100)



    def checkDevices(self):
        for a in self.attributes.itervalues():
            pass
#            a.attr_read()

    def readPumpPower(self, data):
#        print 'readPump', data.value
        self.laserPowerWidget.setAttributeValue(data)

    def writePumpPower(self):
        self.guiLock.acquire()
        w = self.laserPowerWidget.getWriteValue()
        self.attributes['pumpPower'].attr_write(w)
        self.guiLock.release()

    def readPumpTemp(self, data):
#        print 'readTemp', data.value
        self.laserTempWidget.setAttributeValue(data)
#        self.laserTempWidget2.setAttributeValue(data)

    def readSpectrometerState(self, data):
        self.spectrometerName.setState(data)
        data.value = ''
        self.onOffCommands.setStatus(data)

    def readSpectrometerStatus(self, data):
        pass
#        self.onOffCommands.setStatus(data.value, data.quality)

    def readPumpState(self, data):
        self.finesseName.setState(data)

    def readPumpShutterState(self, data):
        self.shutter_widget.setStatus(data)

    def readPumpOperationState(self, data):
        self.laserOperationWidget.setStatus(data)

    def readPrism1Position(self, data):
        self.prism1PositionWidget.setAttributeValue(data)

    def writePrism1Position(self):
        self.guiLock.acquire()
        w = self.prism1PositionWidget.getWriteValue()
        self.attributes['prism1Position'].attr_write(w)
        self.guiLock.release()

    def readPrism1Limit(self, data):
        # The limits attribute is a spectrum attribute.
        # Convert to two scalar attributes with the
        # value of each limit switch as value.
        vals = data.value
        if data.dim_x>1:
            data.value[0] = vals[0]
            self.prism1LimitWidget.setAttributeValue(data)
        else:
            # Something wrong, maybe not initialized
            self.prism1LimitWidget.setAttributeValue(data)
#            self.limit1H.setAttributeValue(data)


    def readPrism2Position(self, data):
        self.prism2PositionWidget.setAttributeValue(data)

    def writePrism2Position(self):
        self.guiLock.acquire()
        w = self.prism2PositionWidget.getWriteValue()
        self.attributes['prism2Position'].attr_write(w)
        self.guiLock.release()

    def readPrism2Limit(self, data):
        # The limits attribute is a spectrum attribute.
        # Convert to two scalar attributes with the
        # value of each limit switch as value.
        vals = data.value
        if data.dim_x>1:
            data.value[0] = vals[0]
            self.prism2LimitWidget.setAttributeValue(data)
        else:
            # Something wrong, maybe not initialized
            self.prism2LimitWidget.setAttributeValue(data)
#            self.limit1H.setAttributeValue(data)

    def readRedpitayaPower(self, data):
#        data.value = (data.value*1.1889 + 13.5e-3) * 1000
        data.value = (data.value) * 1000
        self.peakEnergyWidget.setAttributeValue(data)

    def readPeakEnergy(self, data):
        data.value = data.value * 6.1
#        self.peakEnergyWidget.setAttributeValue(data)

    def readPeakWidth(self, data):
        self.peakWidthWidget.setAttributeValue(data)

    def readPeakWavelength(self, data):
        self.peakWavelengthWidget.setAttributeValue(data)

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
            self.oscSpectrumPlot.setSpectrum(xData = self.timeVector, yData = data)
            self.oscSpectrumPlot.update()

    def readPiezoVoltage(self, data):
        self.piezoVoltageWidget.setAttributeValue(data)

    def readJitter(self, data):
        if data.value != None:
            data.value = data.value*1e15
        self.jitterWidget.setAttributeValue(data)

    def readModelocked(self, data):
        self.modelockedWidget.setAttributeValue(data)

    def readPicomotorPosition(self, data):
        self.picomotorWidget.setAttributeValue(data)

    def writePicomotorPosition(self):
        with self.guiLock:
            w = self.picomotorWidget.getWriteValue()
            self.attributes['halcyonPicomotorPosition'].attr_write(w)

    def readPicomotorFollow(self, data):
        self.trackCommands.setStatus(data)

    def trackPicomotor(self):
        with self.guiLock:
            self.attributes['halcyonFollow'].attr_write(True)

    def stopPicomotor(self):
        with self.guiLock:
            self.attributes['halcyonFollow'].attr_write(False)

    def readErrorFrequency(self, data):
        self.errorFrequencyWidget.setAttributeValue(data)

    def readErrorTrace(self, data):
        if self.errorSampleTime == None:
            print 'No time vector'
        else:
            timeVector = np.linspace(0,data.value.shape[0]*self.errorSampleTime, data.value.shape[0])
            self.errorTrace.setSpectrum(xData = timeVector, yData = data)
            self.errorTrace.update()

    def readHalcyonSampleTime(self, data):
        try:
            print 'Sample time read: ', data.value
            self.errorSampleTime = data.value
        except:
            pass

    def initSpectrometer(self):
        self.devices['spectrometer'].command_inout('init')

    def onSpectrometer(self):
        self.devices['spectrometer'].command_inout('on')

    def offSpectrometer(self):
        self.devices['spectrometer'].command_inout('off')

    def stopSpectrometer(self):
        self.devices['spectrometer'].command_inout('stop')

    def onFinesse(self):
        self.devices['finesse'].command_inout('on')

    def offFinesse(self):
        self.devices['finesse'].command_inout('off')

    def openFinesseShutter(self):
        self.devices['finesse'].command_inout('open')

    def closeFinesseShutter(self):
        self.devices['finesse'].command_inout('close')


    def setupAttributeLayout(self, attributeList = []):
        self.attributeQObjects = []
        for att in attributeList:
            attQObject = qw.QTangoReadAttributeDouble()
            attQObject.setAttributeName(att.name)
            self.attributeQObjects.append(attQObject)
            self.layout_attributes.addWidget(attQObject)

    def closeEvent(self, event):
#         for device in self.devices.itervalues():
#             device.terminate()
        for a in self.attributes.itervalues():
            print 'Stopping', a.name
            a.stop_read()
        for a in self.attributes.itervalues():
            a.readThread.join()
        event.accept()

    def setupLayout(self):
        s='QWidget{background-color: #000000; }'
        self.setStyleSheet(s)

        self.frame_sizes = qw.QTangoSizes()
        self.frame_sizes.barHeight = 20
        self.frame_sizes.barWidth = 18
        self.frame_sizes.readAttributeWidth = 300
        self.frame_sizes.writeAttributeWidth = 150
        self.frame_sizes.fontStretch= 80
        self.frame_sizes.fontType = 'Segoe UI'
#        self.frame_sizes.fontType = 'Trebuchet MS'

        self.attr_sizes = qw.QTangoSizes()
        self.attr_sizes.barHeight = 22
        self.attr_sizes.barWidth = 23
        self.attr_sizes.readAttributeWidth = 320
        self.attr_sizes.readAttributeHeight = 250
        self.attr_sizes.writeAttributeWidth = 320
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

        self.layoutAttributes2 = QtGui.QVBoxLayout()
        self.layoutAttributes2.setMargin(0)
        self.layoutAttributes2.setSpacing(self.attr_sizes.barHeight/2)
        self.layoutAttributes2.setContentsMargins(0, 0, 0, 0)

        self.layoutAttributes3 = QtGui.QVBoxLayout()
        self.layoutAttributes3.setMargin(0)
        self.layoutAttributes3.setSpacing(self.attr_sizes.barHeight/2)
        self.layoutAttributes3.setContentsMargins(0, 0, 0, 0)

        self.title = qw.QTangoTitleBar('Oscillator control')
        self.setWindowTitle('Oscillator control')
        self.sidebar = qw.QTangoSideBar(colors = self.colors, sizes = self.frame_sizes)
        self.bottombar = qw.QTangoHorizontalBar()

#######################
# Finesse widgets
#
        self.finesseName = qw.QTangoDeviceNameStatus(colors = self.colors, sizes = self.frame_sizes)
        self.finesseName.setAttributeName('Finesse')

        self.shutter_widget = qw.QTangoCommandSelection('Shutter', colors = self.colors, sizes = self.attr_sizes)
        self.shutter_widget.addCmdButton('Open', self.openFinesseShutter)
        self.shutter_widget.addCmdButton('Close', self.closeFinesseShutter)

        self.laserOperationWidget = qw.QTangoCommandSelection('Laser', colors = self.colors, sizes = self.attr_sizes)
        self.laserOperationWidget.addCmdButton('Start', self.onFinesse)
        self.laserOperationWidget.addCmdButton('Stop', self.offFinesse)

        self.attr_sizes.readAttributeHeight = 250
        self.laserTempWidget = qw.QTangoReadAttributeSliderV(colors = self.colors, sizes = self.attr_sizes)
        self.laserTempWidget.setAttributeName('Temp', ''.join((unichr(0x00b0),'C')))
        self.laserTempWidget.setAttributeWarningLimits([25, 27])
        self.laserTempWidget.setSliderLimits(23, 28)

        self.laserPowerWidget = qw.QTangoWriteAttributeSliderV(colors = self.colors, sizes = self.attr_sizes)
        self.laserPowerWidget.setAttributeName('Pump pwr', 'W')
        self.laserPowerWidget.setSliderLimits(0, 6)
        self.laserPowerWidget.setAttributeWarningLimits([4, 5.5])
        self.laserPowerWidget.writeValueLineEdit.newValueSignal.connect(self.writePumpPower)

###########################
# Oscillator box widgets
#
        self.attr_sizes.readAttributeHeight = 250
        self.prism1PositionWidget = qw.QTangoWriteAttributeSlider4(colors = self.colors, sizes = self.attr_sizes)
        self.prism1PositionWidget.setAttributeName('Prism 1', 'steps')
        self.prism1PositionWidget.setSliderLimits(-500, 500)
        self.prism1PositionWidget.setAttributeWarningLimits((-500, 500))
        self.prism1PositionWidget.writeValueLineEdit.newValueSignal.connect(self.writePrism1Position)

        self.prism1LimitWidget = qw.QTangoReadAttributeBoolean(colors = self.colors, sizes = self.attr_sizes)
        self.prism1LimitWidget.setAttributeName('Prism1 limit')

        self.prism2PositionWidget = qw.QTangoWriteAttributeSlider4(colors = self.colors, sizes = self.attr_sizes)
        self.prism2PositionWidget.setAttributeName('Prism 2', 'steps')
        self.prism2PositionWidget.setSliderLimits(-500, 500)
        self.prism2PositionWidget.setAttributeWarningLimits((-500, 500))
        self.prism2PositionWidget.writeValueLineEdit.newValueSignal.connect(self.writePrism2Position)

        self.prism2LimitWidget = qw.QTangoReadAttributeBoolean(colors = self.colors, sizes = self.attr_sizes)
        self.prism2LimitWidget.setAttributeName('Prism2 limit')

######################
# Spectrometer widgets
#
        self.spectrometerName = qw.QTangoDeviceNameStatus(colors = self.colors, sizes = self.frame_sizes)
        self.spectrometerName.setAttributeName('Spectrometer')

        self.onOffCommands = qw.QTangoCommandSelection('Spectrometer commands', colors = self.colors, sizes = self.attr_sizes)
        self.onOffCommands.addCmdButton('Init', self.initSpectrometer)
        self.onOffCommands.addCmdButton('On', self.onSpectrometer)
        self.onOffCommands.addCmdButton('Off', self.offSpectrometer)
        self.onOffCommands.addCmdButton('Stop', self.stopSpectrometer)

        self.attr_sizes.readAttributeHeight = 200
        self.peakWidthWidget = qw.QTangoReadAttributeSliderV(colors = self.colors, sizes = self.attr_sizes)
        self.peakWidthWidget.setAttributeName(''.join((unichr(0x0394),unichr(0x03bb), ' FWHM')), 'nm')
        self.peakWidthWidget.setAttributeWarningLimits([35, 100])
        self.peakWidthWidget.setSliderLimits(0, 70)
        self.peakEnergyWidget = qw.QTangoReadAttributeSliderV(colors = self.colors, sizes = self.attr_sizes)
        self.peakEnergyWidget.setAttributeName('Osc pwr', 'mW')
        self.peakEnergyWidget.setAttributeWarningLimits([150, 800])
        self.peakEnergyWidget.setSliderLimits(50, 250)
        self.peakWavelengthWidget = qw.QTangoReadAttributeSliderV(colors = self.colors, sizes = self.attr_sizes)
        self.peakWavelengthWidget.setAttributeName(''.join((unichr(0x03bb),' peak')), 'nm')
        self.peakWavelengthWidget.setAttributeWarningLimits([780, 810])
        self.peakWavelengthWidget.setSliderLimits(760, 840)

        self.oscSpectrumPlot = qw.QTangoReadAttributeSpectrum(colors = self.colors, sizes = self.attr_sizes)
        self.oscSpectrumPlot.setAttributeName('Oscillator spectrum')
        self.oscSpectrumPlot.setXRange(700, 900)
        self.oscSpectrumPlot.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
#        self.oscSpectrumPlot.fixedSize(True)

#######################
# Halcyon attributes
#
        self.modelockedWidget = qw.QTangoReadAttributeBoolean(colors = self.colors, sizes = self.attr_sizes)
        self.modelockedWidget.setAttributeName('Modelocked')

        self.jitterWidget = qw.QTangoReadAttributeSliderV(colors = self.colors, sizes = self.attr_sizes)
        self.jitterWidget.setAttributeName('Jitter', 'fs')
        self.jitterWidget.setSliderLimits(0, 750)
        self.jitterWidget.setAttributeWarningLimits([-1, 500])

        self.errorFrequencyWidget = qw.QTangoReadAttributeSliderV(colors = self.colors, sizes = self.attr_sizes)
        self.errorFrequencyWidget.setAttributeName('f err', 'Hz')
        self.errorFrequencyWidget.setSliderLimits(-1, 10000)
        self.errorFrequencyWidget.setAttributeWarningLimits([-1, 100000])

        self.piezoVoltageWidget = qw.QTangoReadAttributeSliderV(colors = self.colors, sizes = self.attr_sizes)
        self.piezoVoltageWidget.setAttributeName('Piezo', '%')
        self.piezoVoltageWidget.setSliderLimits(0, 100)
        self.piezoVoltageWidget.setAttributeWarningLimits([30, 70])

        self.picomotorWidget = qw.QTangoWriteAttributeDouble(colors = self.colors, sizes = self.attr_sizes)
        self.picomotorWidget.setAttributeName('Picomotor', 'steps')
        self.picomotorWidget.writeValueLineEdit.returnPressed.connect(self.writePicomotorPosition)

        self.trackCommands = qw.QTangoCommandSelection('Track picomotor', colors = self.colors, sizes = self.attr_sizes)
        self.trackCommands.addCmdButton('Track', self.trackPicomotor)
        self.trackCommands.addCmdButton('Stop', self.stopPicomotor)

        self.errorTrace = qw.QTangoReadAttributeSpectrum(colors = self.colors, sizes = self.attr_sizes)
        self.errorTrace.setAttributeName('Error trace')
        self.errorTrace.fixedSize(fixed=True)
#        self.errorTrace.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Expanding)


############################
# Setting up layout
#
        layout2.addWidget(self.title)
        layout2.addLayout(layoutData)
        layoutData.addLayout(self.layout_attributes)
#        layoutData.addSpacerItem(spacerItemH)
        layoutData.addLayout(self.layoutAttributes2)
        layoutData.addLayout(self.layoutAttributes3)

        layoutSlidersFinesse = QtGui.QHBoxLayout()
        layoutSlidersFinesse.addWidget(self.laserPowerWidget)
        layoutSlidersFinesse.addWidget(self.laserTempWidget)

        self.layout_attributes.addWidget(self.finesseName)
        self.layout_attributes.addWidget(self.shutter_widget)
        self.layout_attributes.addWidget(self.laserOperationWidget)
        self.layout_attributes.addLayout(layoutSlidersFinesse)
        self.layout_attributes.addSpacerItem(spacerItemV)


        layoutSliders = QtGui.QHBoxLayout()
        layoutSliders.addSpacerItem(spacerItemBar)
        layoutSliders.addWidget(self.errorFrequencyWidget)
        layoutSliders.addWidget(self.piezoVoltageWidget)
        layoutSliders.addWidget(self.jitterWidget)
        self.layoutAttributes2.addWidget(self.modelockedWidget)
        self.layoutAttributes2.addLayout(layoutSliders)
        self.layoutAttributes2.addWidget(self.picomotorWidget)
        self.layoutAttributes2.addWidget(self.trackCommands)
        self.layoutAttributes2.addWidget(self.errorTrace)
#        self.layoutAttributes2.addSpacerItem(spacerItemV)

        self.layoutAttributes3.addWidget(self.spectrometerName)
        self.layoutAttributes3.addWidget(self.onOffCommands)
        layoutSpectrometerSliders = QtGui.QHBoxLayout()
        layoutSpectrometerSliders.addWidget(self.peakEnergyWidget)
        layoutSpectrometerSliders.addWidget(self.peakWidthWidget)
        layoutSpectrometerSliders.addWidget(self.peakWavelengthWidget)
        self.layoutAttributes3.addSpacerItem(spacerItemV)
        self.layoutAttributes3.addLayout(layoutSpectrometerSliders)
        self.layoutAttributes3.addWidget(self.prism1PositionWidget)
        self.layoutAttributes3.addWidget(self.prism2PositionWidget)
        layoutData.addWidget(self.oscSpectrumPlot)


        layout1.addWidget(self.sidebar)
        layout1.addLayout(layout2)
        layout0.addLayout(layout1)
#        layout0.addWidget(self.bottombar)

#        self.resize(500,800)
        self.setGeometry(100,100,1800,300)

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