"""
Created on 29 Aug 2018

@author: Filip Lindau
"""

# -*- coding:utf-8 -*-
from PyQt4 import QtGui, QtCore

import time
import sys


# noinspection PyAttributeOutsideInit
class TangoDeviceClient(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        #        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.timeVector = None
        self.errorSampleTime = None
        self.xData = None
        self.xDataTemp = None

        self.setupLayout()

        splash.showMessage('         Initializing devices', alignment=QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
        app.processEvents()

        t0 = time.clock()
        self.devices = dict()
        self.devices['spectrometer'] = pt.DeviceProxy('gunlaser/oscillator/spectrometer')
        self.devices['finesse'] = pt.DeviceProxy('gunlaser/oscillator/finesse')
        self.devices['redpitaya0'] = pt.DeviceProxy('gunlaser/devices/redpitaya1')
        self.devices['patara'] = pt.DeviceProxy('gunlaser/devices/patara')
        self.devices['energy'] = pt.DeviceProxy('gunlaser/thg/energy')
        self.devices['redpitaya4'] = pt.DeviceProxy('gunlaser/devices/redpitaya4')
        self.devices['halcyon'] = pt.DeviceProxy('gunlaser/oscillator/halcyon_raspberry')
        self.devices['regenTemp'] = pt.DeviceProxy('gunlaser/regen/temperature')
        self.devices['mpTemp'] = pt.DeviceProxy('gunlaser/mp/temperature')
        print time.clock() - t0, ' s'

        splash.showMessage('         Reading startup attributes',
                           alignment=QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
        app.processEvents()

        self.guiLock = threading.Lock()
        self.attributes = dict()
        self.attributes['finessePower'] = AttributeClass('power', self.devices['finesse'], 0.3)
        self.attributes['finesseTemperature'] = AttributeClass('lasertemperature', self.devices['finesse'], 0.3)
        self.attributes['finesseState'] = AttributeClass('state', self.devices['finesse'], 0.3)
        self.attributes['finesseShutterState'] = AttributeClass('shutterstate', self.devices['finesse'], 0.3)
        self.attributes['finesseOperationState'] = AttributeClass('laseroperationstate', self.devices['finesse'], 0.3)
        self.attributes['peakwidth'] = AttributeClass('peakwidth', self.devices['spectrometer'], 0.3)
        self.attributes['oscPower'] = AttributeClass('measurementdata1', self.devices['redpitaya0'], 0.3)
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
        self.attributes['halcyonState'].attrSignal.connect(self.readHalcyonState)
        self.attributes['halcyonPiezoVoltage'].attrSignal.connect(self.readPiezoVoltage)
        self.attributes['halcyonErrorFrequency'].attrSignal.connect(self.readErrorFrequency)

        self.attributes['pataraState'] = AttributeClass('state', self.devices['patara'], 0.3)
        self.attributes['pataraShutterState'] = AttributeClass('shutter', self.devices['patara'], 0.3)
        self.attributes['pataraEmissionState'] = AttributeClass('emission', self.devices['patara'], 0.3)
        self.attributes['pataraPower'] = AttributeClass('measurementdata2', self.devices['redpitaya4'], 0.3)
        self.attributes['pataraCurrent'] = AttributeClass('current', self.devices['patara'], 0.3)
        self.attributes['regenCrystalTemp'] = AttributeClass('temperature', self.devices['regenTemp'], 0.3)
        self.attributes['mpCrystalTemp'] = AttributeClass('temperature', self.devices['mpTemp'], 0.3)

        self.attributes['pataraState'].attrSignal.connect(self.readPataraState)
        self.attributes['pataraShutterState'].attrSignal.connect(self.readPataraShutterState)
        self.attributes['pataraEmissionState'].attrSignal.connect(self.readRegenEmissionState)
        self.attributes['pataraPower'].attrSignal.connect(self.readPataraPower)
        self.attributes['pataraCurrent'].attrSignal.connect(self.readPataraCurrent)
        self.attributes['regenCrystalTemp'].attrSignal.connect(self.readRegenCrystalTemp)
        self.attributes['mpCrystalTemp'].attrSignal.connect(self.readMPCrystalTemp)

        self.attributes['irEnergy'] = AttributeClass('ir_energy', self.devices['energy'], 0.3)
        self.attributes['irEnergy'].attrSignal.connect(self.readIrEnergy)
        self.attributes['uvEnergy'] = AttributeClass('uv_energy', self.devices['energy'], 0.3)
        self.attributes['uvEnergy'].attrSignal.connect(self.readUvEnergy)
        self.attributes['uvPercent'] = AttributeClass('uv_percent', self.devices['energy'], 1.0)
        self.attributes['uvPercent'].attrSignal.connect(self.readUvPercent)
        self.attributes['irPercent'] = AttributeClass('ir_percent', self.devices['energy'], 1.0)
        self.attributes['irPercent'].attrSignal.connect(self.readIrPercent)

    def readFinesseState(self, data):
        self.finesseName.setState(data)

    def readFinesseShutterState(self, data):
        if data.value == "open":
            data.value = "OPEN"
        else:
            data.value = "CLOSED"
        self.shutter_widget.setStatus(data)

    def readFinesseOperationState(self, data):
        if data.value == "running":
            data.value = "ON"
        self.finesseOperationWidget.setStatus(data)

    def readFinessePower(self, data):
        self.finessePowerWidget.setAttributeValue(data)

    def readFinesseTemperature(self, data):
        self.finesseTempWidget.setAttributeValue(data)

    def readPataraState(self, data):
        self.pataraName.setState(data)

    def readPataraShutterState(self, data):
        if data.value is False:
            data.value = "CLOSED"
        else:
            data.value = "OPEN"
        self.pataraShutterWidget.setStatus(data)

    def readRegenEmissionState(self, data):
        if data.value is False:
            data.value = "OFF"
        else:
            data.value = "ON"
        self.pataraEmissionWidget.setStatus(data)

    def readPataraPower(self, data):
        data.value = data.value * 1e3
        self.pataraEnergyWidget.setAttributeValue(data)

    def readPataraCurrent(self, data):
        self.pataraCurrentWidget.setAttributeValue(data)

    def readRegenCrystalTemp(self, data):
        self.regenTempWidget.setAttributeValue(data)

    def readMPCrystalTemp(self, data):
        self.mpTempWidget.setAttributeValue(data)

    def readOscillatorPower(self, data):
        data.value = data.value * 1e3
        self.oscillatorPowerWidget.setAttributeValue(data)

    def readPeakWidth(self, data):
        self.peakWidthWidget.setAttributeValue(data)

    def readHalcyonState(self, data):
        self.halcyonName.setState(data)

    def readPiezoVoltage(self, data):
        self.piezoVoltageWidget.setAttributeValue(data)

    def readErrorFrequency(self, data):
        self.errorFrequencyWidget.setAttributeValue(data)

    def readIrEnergy(self, data):
        data.value = data.value
        self.irEnergyWidget.setAttributeValue(data)

    def readUvEnergy(self, data):
        data.value = data.value
        self.uvEnergyWidget.setAttributeValue(data)

    def readUvPercent(self, data):
        data.value = data.value
        self.uvEnergyWidget.setAttributeWarningLimits([0.01 * data.value * 200, 500])

    def readIrPercent(self, data):
        data.value = data.value
        self.irEnergyWidget.setAttributeWarningLimits([0.01 * data.value * 6.0, 20])

    def closeEvent(self, event):
        for a in self.attributes.itervalues():
            print 'Stopping', a.name
            a.stop_read()
        for a in self.attributes.itervalues():
            a.readThread.join()
        event.accept()

    def setupLayout(self):
        s = 'QWidget{background-color: #000000; }'
        self.setStyleSheet(s)

        self.title_sizes = qw.QTangoSizes()
        self.title_sizes.barHeight = 60
        self.title_sizes.barWidth = 18
        self.title_sizes.readAttributeWidth = 300
        self.title_sizes.writeAttributeWidth = 150
        self.title_sizes.fontStretch = 80
        self.title_sizes.fontType = 'Arial'

        self.frame_sizes = qw.QTangoSizes()
        self.frame_sizes.barHeight = 60
        self.frame_sizes.barWidth = 35
        self.frame_sizes.readAttributeWidth = 300
        self.frame_sizes.writeAttributeWidth = 150
        self.frame_sizes.fontStretch = 80
        self.frame_sizes.fontType = 'Arial'
        #        self.frame_sizes.fontType = 'Trebuchet MS'

        self.attr_sizes = qw.QTangoSizes()
        self.attr_sizes.barHeight = 30
        self.attr_sizes.barWidth = 35
        self.attr_sizes.readAttributeWidth = 300
        self.attr_sizes.readAttributeHeight = 250
        self.attr_sizes.writeAttributeWidth = 299
        self.attr_sizes.fontStretch = 80
        self.attr_sizes.fontType = 'Arial'
        #        self.attr_sizes.fontType = 'Trebuchet MS'

        self.colors = qw.QTangoColors()

        #######################
        # Title widgets
        #
        self.title = qw.QTangoTitleBar('Gunlaser overview', self.title_sizes)
        self.setWindowTitle('Gunlaser overview')
        self.sidebar = qw.QTangoSideBar(colors=self.colors, sizes=self.frame_sizes)
        self.bottombar = qw.QTangoHorizontalBar()

        #######################
        # Finesse widgets
        #
        self.finesseName = qw.QTangoDeviceNameStatus(colors=self.colors, sizes=self.frame_sizes)
        self.finesseName.setAttributeName('Finesse')

        self.shutter_widget = qw.QTangoCommandSelection('Shutter', colors=self.colors, sizes=self.attr_sizes)

        self.finesseOperationWidget = qw.QTangoCommandSelection('Laser', colors=self.colors, sizes=self.attr_sizes)

        self.attr_sizes.readAttributeHeight = 300

        self.finessePowerWidget = qw.QTangoReadAttributeSliderV(colors=self.colors, sizes=self.attr_sizes)
        self.finessePowerWidget.setAttributeName('Finesse power', 'W')
        self.finessePowerWidget.setSliderLimits(0, 7)
        self.finessePowerWidget.setAttributeWarningLimits([4, 5.5])

        self.finesseTempWidget = qw.QTangoReadAttributeSliderV(colors=self.colors, sizes=self.attr_sizes)
        self.finesseTempWidget.setAttributeName('Temp', ''.join((unichr(0x00b0), 'C')))
        self.finesseTempWidget.setAttributeWarningLimits([25, 27])
        self.finesseTempWidget.setSliderLimits(23, 28)

        ######################
        # Oscillator widgets
        #
        self.attr_sizes.readAttributeHeight = 300
        self.peakWidthWidget = qw.QTangoReadAttributeSliderV(colors=self.colors, sizes=self.attr_sizes)
        #        self.peakWidthWidget.setAttributeName(''.join((unichr(0x0394),unichr(0x03bb), ' FWHM')), 'nm')
        self.peakWidthWidget.setAttributeName('Osc width', 'nm')
        self.peakWidthWidget.setAttributeWarningLimits([35, 100])
        self.peakWidthWidget.setSliderLimits(0, 70)
        self.oscillatorPowerWidget = qw.QTangoReadAttributeSliderV(colors=self.colors, sizes=self.attr_sizes)
        self.oscillatorPowerWidget.setAttributeName('Oscillator', 'mW')
        self.oscillatorPowerWidget.setAttributeWarningLimits([150, 800])
        self.oscillatorPowerWidget.setSliderLimits(50, 250)

        ######################
        # Halcyon widgets
        self.halcyonName = qw.QTangoDeviceNameStatus(colors=self.colors, sizes=self.attr_sizes)
        self.halcyonName.setAttributeName('Halcyon')

        self.errorFrequencyWidget = qw.QTangoReadAttributeSliderV(colors=self.colors, sizes=self.attr_sizes)
        self.errorFrequencyWidget.setAttributeName('Error freq', 'kHz')
        self.errorFrequencyWidget.setSliderLimits(-1, 10000)
        self.errorFrequencyWidget.setAttributeWarningLimits([-1, 100000])

        self.piezoVoltageWidget = qw.QTangoReadAttributeSliderV(colors=self.colors, sizes=self.attr_sizes)
        self.piezoVoltageWidget.setAttributeName('Piezo', '%')
        self.piezoVoltageWidget.setSliderLimits(0, 100)
        self.piezoVoltageWidget.setAttributeWarningLimits([30, 70])

        ######################
        # Regen widgets
        #

        self.pataraName = qw.QTangoDeviceNameStatus(colors=self.colors, sizes=self.frame_sizes)
        self.pataraName.setAttributeName('Patara')
        self.pataraShutterWidget = qw.QTangoCommandSelection('Shutter', colors=self.colors, sizes=self.attr_sizes)
        self.pataraEmissionWidget = qw.QTangoCommandSelection('Emission', colors=self.colors, sizes=self.attr_sizes)

        self.attr_sizes.readAttributeHeight = 300

        self.pataraEnergyWidget = qw.QTangoReadAttributeSliderV(colors=self.colors, sizes=self.attr_sizes)
        self.pataraEnergyWidget.setAttributeName('Patara Energy', 'mJ')
        self.pataraEnergyWidget.setSliderLimits(0, 55)
        self.pataraEnergyWidget.setAttributeWarningLimits([30, 50])

        self.pataraCurrentWidget = qw.QTangoReadAttributeSliderV(colors=self.colors, sizes=self.attr_sizes)
        self.pataraCurrentWidget.setAttributeName('Current', '%')
        self.pataraCurrentWidget.setAttributeWarningLimits([22, 28.5])
        self.pataraCurrentWidget.setSliderLimits(10, 35)

        self.regenTempWidget = qw.QTangoReadAttributeSliderV(colors=self.colors, sizes=self.attr_sizes)
        self.regenTempWidget.setAttributeName('Regen crystal', 'degC')
        self.regenTempWidget.setAttributeWarningLimits([-280, -170])
        self.regenTempWidget.setSliderLimits(-270, 30)

        ######################
        # mp widgets
        #

        self.mpTempWidget = qw.QTangoReadAttributeSliderV(colors=self.colors, sizes=self.attr_sizes)
        self.mpTempWidget.setAttributeName('MP crystal', 'degC')
        self.mpTempWidget.setAttributeWarningLimits([-280, -170])
        self.mpTempWidget.setSliderLimits(-270, 30)

        ######################
        # energy widgets
        #
        self.attr_sizes.readAttributeHeight = 300

        self.irEnergyWidget = qw.QTangoReadAttributeSliderV(colors=self.colors, sizes=self.attr_sizes)
        self.irEnergyWidget.setAttributeName('IR energy', 'mJ')
        self.irEnergyWidget.setSliderLimits(0, 12)
        self.irEnergyWidget.setAttributeWarningLimits([8, 11])

        self.uvEnergyWidget = qw.QTangoReadAttributeSliderV(colors=self.colors, sizes=self.attr_sizes)
        self.uvEnergyWidget.setAttributeName('UV energy', 'uJ')
        self.uvEnergyWidget.setSliderLimits(0, 400)
        self.uvEnergyWidget.setAttributeWarningLimits([50, 400])

        ############################
        # Setting up layout
        #
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
        spacerItemBar = QtGui.QSpacerItem(self.frame_sizes.barWidth, self.frame_sizes.barHeight + 8,
                                          QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        spacerItemH = QtGui.QSpacerItem(20, 5, QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Minimum)

        layoutData = QtGui.QVBoxLayout()
        layoutData.setMargin(self.attr_sizes.barHeight / 2)
        layoutData.setSpacing(self.attr_sizes.barHeight * 2)

        self.layoutAttributesFinesse = QtGui.QVBoxLayout()
        self.layoutAttributesFinesse.setMargin(0)
        self.layoutAttributesFinesse.setSpacing(self.attr_sizes.barHeight / 2)
        self.layoutAttributesFinesse.setContentsMargins(0, 0, 0, 0)
        self.layoutAttributesFinesse.addWidget(self.finesseName)
        self.layoutAttributesFinesse.addWidget(self.shutter_widget)
        self.layoutAttributesFinesse.addWidget(self.finesseOperationWidget)
        self.layoutAttributesFinesse.addSpacerItem(QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum,
                                                                     QtGui.QSizePolicy.Minimum))

        self.layoutAttributesPatara = QtGui.QVBoxLayout()
        self.layoutAttributesPatara.setMargin(0)
        self.layoutAttributesPatara.setSpacing(self.attr_sizes.barHeight / 2)
        self.layoutAttributesPatara.setContentsMargins(0, 0, 0, 0)
        self.layoutAttributesPatara.addWidget(self.pataraName)
        self.layoutAttributesPatara.addWidget(self.pataraShutterWidget)
        self.layoutAttributesPatara.addWidget(self.pataraEmissionWidget)
        self.layoutAttributesPatara.addSpacerItem(QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum,
                                                                    QtGui.QSizePolicy.Minimum))

        self.layoutAttributesPumps = QtGui.QHBoxLayout()
        self.layoutAttributesPumps.setMargin(0)
        self.layoutAttributesPumps.setSpacing(self.attr_sizes.barHeight / 2)
        self.layoutAttributesPumps.setContentsMargins(0, 0, 0, 0)
        self.layoutAttributesPumps.addLayout(self.layoutAttributesFinesse)
        self.layoutAttributesPumps.addSpacerItem(QtGui.QSpacerItem(80, 40, QtGui.QSizePolicy.Minimum,
                                                                    QtGui.QSizePolicy.Minimum))
        self.layoutAttributesPumps.addLayout(self.layoutAttributesPatara)
        self.layoutAttributesPumps.addSpacerItem(QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding,
                                                                    QtGui.QSizePolicy.Minimum))


        self.layoutAttributesEnergies = QtGui.QHBoxLayout()
        self.layoutAttributesEnergies.setMargin(0)
        self.layoutAttributesEnergies.setSpacing(self.attr_sizes.barHeight / 2)
        self.layoutAttributesEnergies.setContentsMargins(0, 0, 0, 0)
        self.layoutAttributesEnergies.addWidget(self.finessePowerWidget)
        self.layoutAttributesEnergies.addSpacerItem(QtGui.QSpacerItem(250, 20, QtGui.QSizePolicy.Minimum,
                                                                    QtGui.QSizePolicy.Minimum))
        self.layoutAttributesEnergies.addWidget(self.pataraEnergyWidget)
        self.layoutAttributesEnergies.addSpacerItem(QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding,
                                                                    QtGui.QSizePolicy.Minimum))
        self.layoutAttributesEnergies.addWidget(self.oscillatorPowerWidget)
        self.layoutAttributesEnergies.addSpacerItem(QtGui.QSpacerItem(80, 20, QtGui.QSizePolicy.Minimum,
                                                                    QtGui.QSizePolicy.Minimum))
        self.layoutAttributesEnergies.addWidget(self.irEnergyWidget)
        self.layoutAttributesEnergies.addSpacerItem(QtGui.QSpacerItem(80, 20, QtGui.QSizePolicy.Minimum,
                                                                    QtGui.QSizePolicy.Minimum))
        self.layoutAttributesEnergies.addWidget(self.uvEnergyWidget)
        self.layoutAttributesEnergies.addSpacerItem(QtGui.QSpacerItem(80, 20, QtGui.QSizePolicy.Minimum,
                                                                    QtGui.QSizePolicy.Minimum))

        self.layoutAttributesMisc = QtGui.QHBoxLayout()
        self.layoutAttributesMisc.setMargin(0)
        self.layoutAttributesMisc.setSpacing(self.attr_sizes.barHeight / 2)
        self.layoutAttributesMisc.setContentsMargins(0, 0, 0, 0)
        self.layoutAttributesMisc.addWidget(self.peakWidthWidget)
        self.layoutAttributesMisc.addSpacerItem(QtGui.QSpacerItem(80, 20, QtGui.QSizePolicy.Minimum,
                                                                    QtGui.QSizePolicy.Minimum))
        self.layoutAttributesMisc.addWidget(self.errorFrequencyWidget)
        self.layoutAttributesMisc.addSpacerItem(QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding,
                                                                    QtGui.QSizePolicy.Minimum))
        self.layoutAttributesMisc.addWidget(self.regenTempWidget)
        self.layoutAttributesMisc.addSpacerItem(QtGui.QSpacerItem(80, 20, QtGui.QSizePolicy.Minimum,
                                                                    QtGui.QSizePolicy.Minimum))
        self.layoutAttributesMisc.addWidget(self.mpTempWidget)
        self.layoutAttributesMisc.addSpacerItem(QtGui.QSpacerItem(80, 20, QtGui.QSizePolicy.Minimum,
                                                                    QtGui.QSizePolicy.Minimum))

        layout2.addWidget(self.title)
        layout2.addSpacerItem(QtGui.QSpacerItem(20, 60, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum))
        layout2.addLayout(layoutData)
        layoutData.addLayout(self.layoutAttributesPumps)
        layoutData.addLayout(self.layoutAttributesEnergies)
        layoutData.addLayout(self.layoutAttributesMisc)
        layoutData.addSpacerItem(QtGui.QSpacerItem(20, 20, QtGui.QSizePolicy.Minimum,
                                                                    QtGui.QSizePolicy.Expanding))

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
    splash.showMessage('         Importing modules', alignment=QtCore.Qt.AlignBottom | QtCore.Qt.AlignLeft,
                       color=QtGui.QColor('#66cbff'))
    app.processEvents()

    import QTangoWidgets.QTangoWidgets as qw
    from QTangoWidgets.AttributeReadThreadClass import AttributeClass
    import pyqtgraph as pg
    import PyTango as pt
    import threading
    import numpy as np

    splash.showMessage('         Starting GUI', alignment=QtCore.Qt.AlignBottom | QtCore.Qt.AlignLeft,
                       color=QtGui.QColor('#66cbff'))
    app.processEvents()
    myapp = TangoDeviceClient()
    myapp.show()
    splash.finish(myapp)
    sys.exit(app.exec_())
