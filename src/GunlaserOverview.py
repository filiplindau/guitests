'''
Created on 8 Sep 2015

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
        self.devices['redpitaya0']=pt.DeviceProxy('gunlaser/devices/redpitaya0')
        self.devices['regenLee']=pt.DeviceProxy('gunlaser/regen/leelaser')
        self.devices['redpitaya1']=pt.DeviceProxy('gunlaser/devices/redpitaya1')
        self.devices['mpLee']=pt.DeviceProxy('gunlaser/mp/leelaser')
        self.devices['redpitaya4']=pt.DeviceProxy('gunlaser/devices/redpitaya4')
        self.devices['halcyon']=pt.DeviceProxy('gunlaser/oscillator/halcyon')
        self.devices['regenTemp']=pt.DeviceProxy('gunlaser/regen/temperature')
        self.devices['mpTemp']=pt.DeviceProxy('gunlaser/mp/temperature')
        print time.clock()-t0, ' s'

        splash.showMessage('         Reading startup attributes', alignment = QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
        app.processEvents()


        self.guiLock = threading.Lock()
        self.attributes = {}
        self.attributes['finessePower'] = AttributeClass('power', self.devices['finesse'], 0.3)
        self.attributes['finesseTemperature'] = AttributeClass('lasertemperature', self.devices['finesse'], 0.3)
        self.attributes['finesseState'] = AttributeClass('state', self.devices['finesse'], 0.3)
        self.attributes['finesseShutterState'] = AttributeClass('shutterstate', self.devices['finesse'], 0.3)
        self.attributes['finesseOperationState'] = AttributeClass('laseroperationstate', self.devices['finesse'], 0.3)
        self.attributes['peakwidth'] = AttributeClass('peakwidth', self.devices['spectrometer'], 0.3)
        self.attributes['oscPower'] = AttributeClass('measurementdata1', self.devices['redpitaya0'], 0.3)
        self.attributes['wavelengths'] = AttributeClass('wavelengthsROI', self.devices['spectrometer'], None)
        self.attributes['spectrum'] = AttributeClass('spectrumROI', self.devices['spectrometer'], 0.3)
        self.attributes['halcyonState'] = AttributeClass('state', self.devices['halcyon'], 0.3)
        self.attributes['halcyonPiezoVoltage'] = AttributeClass('piezovoltage', self.devices['halcyon'], 0.3)
        self.attributes['halcyonErrorFrequency'] = AttributeClass('errorfrequency', self.devices['halcyon'], 0.3)
        
        self.attributes['finessePower'].attrSignal.connect(self.readFinessePower)
        self.attributes['finesseTemperature'].attrSignal.connect(self.readFinesseTemperature)
        self.attributes['finesseState'].attrSignal.connect(self.readFinesseState)
        self.attributes['finesseShutterState'].attrSignal.connect(self.readFinesseShutterState)
        self.attributes['finesseOperationState'].attrSignal.connect(self.readFinesseOperationState)
        self.attributes['peakwidth'].attrSignal.connect(self.readPeakWidth)
        self.attributes['oscPower'].attrSignal.connect(self.readOscillatorPower)
        self.attributes['spectrum'].attrSignal.connect(self.readSpectrum)
        self.attributes['wavelengths'].attrSignal.connect(self.readWavelengths)
        self.attributes['halcyonState'].attrSignal.connect(self.readHalcyonState)
        self.attributes['halcyonPiezoVoltage'].attrSignal.connect(self.readPiezoVoltage)
        self.attributes['halcyonErrorFrequency'].attrSignal.connect(self.readErrorFrequency)
        
        self.attributes['regenState'] = AttributeClass('state', self.devices['regenLee'], 0.3)
        self.attributes['regenShutterState'] = AttributeClass('shutterstate', self.devices['regenLee'], 0.3)
        self.attributes['regenOperationState'] = AttributeClass('laserstate', self.devices['regenLee'], 0.3)
        self.attributes['regenLeePower'] = AttributeClass('measurementdata1', self.devices['redpitaya4'], 0.3)
        self.attributes['regenLeePercentcurrent'] = AttributeClass('percentcurrent', self.devices['regenLee'], 0.3)
        self.attributes['regenCrystalTemp'] = AttributeClass('temperature', self.devices['regenTemp'], 0.3)
        self.attributes['mpState'] = AttributeClass('state', self.devices['mpLee'], 0.3)
        self.attributes['mpShutterState'] = AttributeClass('shutterstate', self.devices['mpLee'], 0.3)
        self.attributes['mpOperationState'] = AttributeClass('laserstate', self.devices['mpLee'], 0.3)
        self.attributes['mpLeePower'] = AttributeClass('measurementdata2', self.devices['redpitaya4'], 0.3)
        self.attributes['mpLeePercentcurrent'] = AttributeClass('percentcurrent', self.devices['mpLee'], 0.3)
        self.attributes['mpCrystalTemp'] = AttributeClass('temperature', self.devices['mpTemp'], 0.3)

        self.attributes['regenState'].attrSignal.connect(self.readRegenState)
        self.attributes['regenShutterState'].attrSignal.connect(self.readRegenShutterState)
        self.attributes['regenOperationState'].attrSignal.connect(self.readRegenOperationState)
        self.attributes['regenLeePower'].attrSignal.connect(self.readRegenLeePower)
        self.attributes['regenLeePercentcurrent'].attrSignal.connect(self.readRegenLeePercentCurrent)
        self.attributes['regenCrystalTemp'].attrSignal.connect(self.readRegenCrystalTemp)
        self.attributes['mpState'].attrSignal.connect(self.readMPState)
        self.attributes['mpShutterState'].attrSignal.connect(self.readMPShutterState)
        self.attributes['mpOperationState'].attrSignal.connect(self.readMPOperationState)
        self.attributes['mpLeePower'].attrSignal.connect(self.readMPLeePower)
        self.attributes['mpLeePercentcurrent'].attrSignal.connect(self.readMPLeePercentCurrent)
        self.attributes['mpCrystalTemp'].attrSignal.connect(self.readMPCrystalTemp)
        
    def readFinesseState(self, data):
        self.finesseName.setState(data)

    def readFinesseShutterState(self, data):
        self.shutterWidget.setStatus(data)

    def readFinesseOperationState(self, data):
        self.laserOperationWidget.setStatus(data)

    def readFinessePower(self, data):
#        print 'readPump', data.value
        self.laserPowerWidget.setAttributeValue(data)

    def readFinesseTemperature(self, data):
        self.finesseTempWidget.setAttributeValue(data)

    def readRegenState(self, data):
        self.regenLeeName.setState(data)

    def readRegenShutterState(self, data):
        self.regenShutterWidget.setStatus(data)

    def readRegenOperationState(self, data):
        self.regenOperationWidget.setStatus(data)

    def readRegenLeePower(self, data):
        data.value = data.value*1e3
        self.regenLeePowerWidget.setAttributeValue(data)

    def readRegenLeePercentCurrent(self, data):
        self.regenLeePercentCurrentWidget.setAttributeValue(data)

    def readRegenCrystalTemp(self, data):
        self.regenTempWidget.setAttributeValue(data)
        
    def readMPState(self, data):
        self.mpLeeName.setState(data)

    def readMPShutterState(self, data):
        self.mpShutterWidget.setStatus(data)

    def readMPOperationState(self, data):
        self.mpOperationWidget.setStatus(data)

    def readMPLeePower(self, data):
        data.value = data.value*1e3
        self.mpLeePowerWidget.setAttributeValue(data)

    def readMPLeePercentCurrent(self, data):
        self.mpLeePercentCurrentWidget.setAttributeValue(data)

    def readMPCrystalTemp(self, data):
        self.mpTempWidget.setAttributeValue(data)
        
    def readOscillatorPower(self, data):
        data.value = data.value*1e3
        self.peakEnergyWidget.setAttributeValue(data)


    def readPeakWidth(self, data):
        self.peakWidthWidget.setAttributeValue(data)

    def readHalcyonState(self, data):
        self.halcyonName.setState(data)

    def readPiezoVoltage(self, data):
        self.piezoVoltageWidget.setAttributeValue(data)

    def readErrorFrequency(self, data):
        self.errorFrequencyWidget.setAttributeValue(data)

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

        self.titleSizes = qw.QTangoSizes()
        self.titleSizes.barHeight = 60
        self.titleSizes.barWidth = 18
        self.titleSizes.readAttributeWidth = 300
        self.titleSizes.writeAttributeWidth = 150
        self.titleSizes.fontStretch= 80
        self.titleSizes.fontType = 'Arial'
        
        self.frameSizes = qw.QTangoSizes()
        self.frameSizes.barHeight = 60
        self.frameSizes.barWidth = 35
        self.frameSizes.readAttributeWidth = 300
        self.frameSizes.writeAttributeWidth = 150
        self.frameSizes.fontStretch= 80
        self.frameSizes.fontType = 'Arial'
#        self.frameSizes.fontType = 'Trebuchet MS'

        self.attrSizes = qw.QTangoSizes()
        self.attrSizes.barHeight = 30
        self.attrSizes.barWidth = 35
        self.attrSizes.readAttributeWidth = 300
        self.attrSizes.readAttributeHeight = 250
        self.attrSizes.writeAttributeWidth = 299
        self.attrSizes.fontStretch= 80
        self.attrSizes.fontType = 'Arial'
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
        self.layoutAttributesOsc = QtGui.QVBoxLayout()
        self.layoutAttributesOsc.setMargin(0)
        self.layoutAttributesOsc.setSpacing(self.attrSizes.barHeight/2)
        self.layoutAttributesOsc.setContentsMargins(0, 0, 0, 0)

        self.layoutAttributesRegen = QtGui.QVBoxLayout()
        self.layoutAttributesRegen.setMargin(0)
        self.layoutAttributesRegen.setSpacing(self.attrSizes.barHeight/2)
        self.layoutAttributesRegen.setContentsMargins(0, 0, 0, 0)

        self.layoutAttributesMP = QtGui.QVBoxLayout()
        self.layoutAttributesMP.setMargin(0)
        self.layoutAttributesMP.setSpacing(self.attrSizes.barHeight/2)
        self.layoutAttributesMP.setContentsMargins(0, 0, 0, 0)

        self.title = qw.QTangoTitleBar('Gunlaser overview', self.titleSizes)
        self.setWindowTitle('Gunlaser overview')
        self.sidebar = qw.QTangoSideBar(colors = self.colors, sizes = self.frameSizes)
        self.bottombar = qw.QTangoHorizontalBar()

#######################
# Finesse widgets
#
        self.finesseName = qw.QTangoDeviceNameStatus(colors = self.colors, sizes = self.frameSizes)
        self.finesseName.setAttributeName('Finesse')

        self.shutterWidget = qw.QTangoCommandSelection('Shutter', colors = self.colors, sizes = self.attrSizes)

        self.laserOperationWidget = qw.QTangoCommandSelection('Laser', colors = self.colors, sizes = self.attrSizes)

        self.attrSizes.readAttributeHeight = 300

        self.laserPowerWidget = qw.QTangoReadAttributeSliderV(colors = self.colors, sizes = self.attrSizes)
        self.laserPowerWidget.setAttributeName('Finesse', 'W')
        self.laserPowerWidget.setSliderLimits(0, 7)
        self.laserPowerWidget.setAttributeWarningLimits([4, 5.5])

        self.finesseTempWidget = qw.QTangoReadAttributeSliderV(colors = self.colors, sizes = self.attrSizes)
        self.finesseTempWidget.setAttributeName('Temp', ''.join((unichr(0x00b0),'C')))
        self.finesseTempWidget.setAttributeWarningLimits([25, 27])
        self.finesseTempWidget.setSliderLimits(23, 28)


######################
# Spectrometer widgets
#

        self.attrSizes.readAttributeHeight = 300
        self.peakWidthWidget = qw.QTangoReadAttributeSliderV(colors = self.colors, sizes = self.attrSizes)
#        self.peakWidthWidget.setAttributeName(''.join((unichr(0x0394),unichr(0x03bb), ' FWHM')), 'nm')
        self.peakWidthWidget.setAttributeName('Width', 'nm')
        self.peakWidthWidget.setAttributeWarningLimits([35, 100])
        self.peakWidthWidget.setSliderLimits(0, 70)
        self.peakEnergyWidget = qw.QTangoReadAttributeSliderV(colors = self.colors, sizes = self.attrSizes)
        self.peakEnergyWidget.setAttributeName('Oscillator', 'mW')
        self.peakEnergyWidget.setAttributeWarningLimits([150, 800])
        self.peakEnergyWidget.setSliderLimits(50, 250)
        self.oscSpectrumPlot = qw.QTangoReadAttributeSpectrum(colors = self.colors, sizes = self.attrSizes)
        self.oscSpectrumPlot.setAttributeName('Oscillator spectrum')
        self.oscSpectrumPlot.setXRange(700, 900)
        self.oscSpectrumPlot.setMinimumWidth(600)
        self.oscSpectrumPlot.setMaximumWidth(600)
        self.oscSpectrumPlot.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)

######################
# Halcyon widgets
        self.halcyonName = qw.QTangoDeviceNameStatus(colors = self.colors, sizes = self.attrSizes)
        self.halcyonName.setAttributeName('Halcyon')

        self.errorFrequencyWidget = qw.QTangoReadAttributeSliderV(colors = self.colors, sizes = self.attrSizes)
        self.errorFrequencyWidget.setAttributeName('f err', 'kHz')
        self.errorFrequencyWidget.setSliderLimits(-1, 10000)
        self.errorFrequencyWidget.setAttributeWarningLimits([-1, 100000])

        self.piezoVoltageWidget = qw.QTangoReadAttributeSliderV(colors = self.colors, sizes = self.attrSizes)
        self.piezoVoltageWidget.setAttributeName('Piezo', '%')
        self.piezoVoltageWidget.setSliderLimits(0, 100)
        self.piezoVoltageWidget.setAttributeWarningLimits([30, 70])


######################
# Regen widgets
#

        self.regenLeeName = qw.QTangoDeviceNameStatus(colors = self.colors, sizes = self.frameSizes)
        self.regenLeeName.setAttributeName('Regen')
        self.regenShutterWidget = qw.QTangoCommandSelection('Shutter', colors = self.colors, sizes = self.attrSizes)
        self.regenOperationWidget = qw.QTangoCommandSelection('Laser', colors = self.colors, sizes = self.attrSizes)

        self.attrSizes.readAttributeHeight = 300

        self.regenLeePowerWidget = qw.QTangoReadAttributeSliderV(colors = self.colors, sizes = self.attrSizes)
        self.regenLeePowerWidget.setAttributeName('Energy', 'mJ')
        self.regenLeePowerWidget.setSliderLimits(0, 30)
        self.regenLeePowerWidget.setAttributeWarningLimits([10, 20])

        self.regenLeePercentCurrentWidget = qw.QTangoReadAttributeSliderV(colors = self.colors, sizes = self.attrSizes)
        self.regenLeePercentCurrentWidget.setAttributeName('Current', '%')
        self.regenLeePercentCurrentWidget.setAttributeWarningLimits([40, 74])
        self.regenLeePercentCurrentWidget.setSliderLimits(36, 90)

        self.regenTempWidget = qw.QTangoReadAttributeSliderV(colors = self.colors, sizes = self.attrSizes)
        self.regenTempWidget.setAttributeName('Crystal temp', 'degC')
        self.regenTempWidget.setAttributeWarningLimits([-280, -170])
        self.regenTempWidget.setSliderLimits(-270, 30)

######################
# mp widgets
#

        self.mpLeeName = qw.QTangoDeviceNameStatus(colors = self.colors, sizes = self.frameSizes)
        self.mpLeeName.setAttributeName('MP')
        self.mpShutterWidget = qw.QTangoCommandSelection('Shutter', colors = self.colors, sizes = self.attrSizes)
        self.mpOperationWidget = qw.QTangoCommandSelection('Laser', colors = self.colors, sizes = self.attrSizes)

        self.attrSizes.readAttributeHeight = 300

        self.mpLeePowerWidget = qw.QTangoReadAttributeSliderV(colors = self.colors, sizes = self.attrSizes)
        self.mpLeePowerWidget.setAttributeName('Energy', 'mJ')
        self.mpLeePowerWidget.setSliderLimits(0, 30)
        self.mpLeePowerWidget.setAttributeWarningLimits([10, 25])

        self.mpLeePercentCurrentWidget = qw.QTangoReadAttributeSliderV(colors = self.colors, sizes = self.attrSizes)
        self.mpLeePercentCurrentWidget.setAttributeName('Current', '%')
        self.mpLeePercentCurrentWidget.setAttributeWarningLimits([50, 86])
        self.mpLeePercentCurrentWidget.setSliderLimits(36, 90)

        self.mpTempWidget = qw.QTangoReadAttributeSliderV(colors = self.colors, sizes = self.attrSizes)
        self.mpTempWidget.setAttributeName('Crystal temp', 'degC')
        self.mpTempWidget.setAttributeWarningLimits([-280, -170])
        self.mpTempWidget.setSliderLimits(-270, 30)

############################
# Setting up layout
#
        layout2.addWidget(self.title)
        layout2.addSpacerItem(QtGui.QSpacerItem(20, 60, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum))
        layout2.addLayout(layoutData)
        layoutData.addLayout(self.layoutAttributesOsc)
#        layoutData.addSpacerItem(spacerItemH)
        layoutData.addLayout(self.layoutAttributesRegen)
        layoutData.addLayout(self.layoutAttributesMP)

        layoutSlidersOsc = QtGui.QHBoxLayout()
        layoutSlidersOsc.addWidget(self.laserPowerWidget)
        layoutSlidersOsc.addWidget(self.finesseTempWidget)
        layoutSlidersOsc.addWidget(self.peakEnergyWidget)
        layoutSlidersOsc.addWidget(self.peakWidthWidget)
        
        layoutSpectrumOsc = QtGui.QHBoxLayout()
        layoutSpectrumOsc.addWidget(self.oscSpectrumPlot)

        self.layoutAttributesOsc.addWidget(self.finesseName)
        self.layoutAttributesOsc.addWidget(self.shutterWidget)
        self.layoutAttributesOsc.addWidget(self.laserOperationWidget)
        self.layoutAttributesOsc.addSpacerItem(QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum))
        self.layoutAttributesOsc.addLayout(layoutSlidersOsc)
        self.layoutAttributesOsc.addSpacerItem(spacerItemV)
        self.layoutAttributesOsc.addLayout(layoutSpectrumOsc)

        layoutSlidersRegen = QtGui.QHBoxLayout()
        layoutSlidersRegen.addWidget(self.regenLeePercentCurrentWidget)
        layoutSlidersRegen.addWidget(self.regenLeePowerWidget)
        layoutSlidersRegen.addWidget(self.regenTempWidget)
        
        layoutHalcyonData = QtGui.QHBoxLayout()
        layoutHalcyonData.addWidget(self.piezoVoltageWidget)
        layoutHalcyonData.addWidget(self.errorFrequencyWidget)

        self.layoutAttributesRegen.addWidget(self.regenLeeName)
        self.layoutAttributesRegen.addWidget(self.regenShutterWidget)
        self.layoutAttributesRegen.addWidget(self.regenOperationWidget)
        self.layoutAttributesRegen.addSpacerItem(QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum))
        self.layoutAttributesRegen.addLayout(layoutSlidersRegen)
        self.layoutAttributesRegen.addSpacerItem(spacerItemV)
        self.layoutAttributesRegen.addWidget(self.halcyonName)
        self.layoutAttributesRegen.addLayout(layoutHalcyonData)

        layoutSlidersMP = QtGui.QHBoxLayout()
        layoutSlidersMP.addWidget(self.mpLeePercentCurrentWidget)
        layoutSlidersMP.addWidget(self.mpLeePowerWidget)
        layoutSlidersMP.addWidget(self.mpTempWidget)

        self.layoutAttributesMP.addWidget(self.mpLeeName)
        self.layoutAttributesMP.addWidget(self.mpShutterWidget)
        self.layoutAttributesMP.addWidget(self.mpOperationWidget)
        self.layoutAttributesMP.addSpacerItem(QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum))
        self.layoutAttributesMP.addLayout(layoutSlidersMP)
        self.layoutAttributesMP.addSpacerItem(spacerItemV)


#        layout1.addWidget(self.sidebar)
        layout1.addLayout(layout2)
        layout0.addLayout(layout1)
#        layout0.addWidget(self.bottombar)

#        self.resize(500,800)
#        self.setGeometry(200,100,1600,300)
        self.showFullScreen()

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
