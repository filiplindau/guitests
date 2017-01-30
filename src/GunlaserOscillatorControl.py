'''
Created on 8 aug 2014

@author: Filip
'''
# -*- coding:utf-8 -*-
from PyQt4 import QtGui, QtCore

import time
import sys


# noinspection PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit
class TangoDeviceClient(QtGui.QWidget):
	def __init__(self, parent = None):
		QtGui.QWidget.__init__(self,parent)
#		self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
		self.timeVector = None
		self.xData = None
		self.xDataTemp = None

		self.setupLayout()

		splash.showMessage('	     Initializing devices', alignment = QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
		app.processEvents()

		t0=time.clock()
		self.devices = {}
		self.devices['spectrometer']=pt.DeviceProxy('gunlaser/oscillator/spectrometer')
		self.devices['finesse']=pt.DeviceProxy('gunlaser/oscillator/finesse')
		self.devices['prism1']=pt.DeviceProxy('gunlaser/oscillator/prism1')
		self.devices['prism2']=pt.DeviceProxy('gunlaser/oscillator/prism2')
		print time.clock()-t0, ' s'

		splash.showMessage('	     Reading startup attributes', alignment = QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
		app.processEvents()


		self.guiLock = threading.Lock()
		self.attributes = {}
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

		splash.showMessage('	     Setting up variables', alignment = QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
		app.processEvents()

#		 self.timer = QtCore.QTimer(self)
#		 self.timer.timeout.connect(self.checkDevices)
#		 self.timer.start(100)



	def checkDevices(self):
		for a in self.attributes.itervalues():
			pass
#			a.attr_read()

	def readPumpPower(self, data):
#		print 'readPump', data.value
		self.laserPowerWidget.setAttributeValue(data)

	def writePumpPower(self):
		self.guiLock.acquire()
		w = self.laserPowerWidget.getWriteValue()
		self.attributes['pumpPower'].attr_write(w)
		self.guiLock.release()

	def readPumpTemp(self, data):
#		print 'readTemp', data.value
		self.laserTempWidget.setAttributeValue(data)
#		self.laserTempWidget2.setAttributeValue(data)

	def readSpectrometerState(self, data):
		self.spectrometerName.setState(data)
		data.value = ''
		self.onOffCommands.setStatus(data)

	def readSpectrometerStatus(self, data):
		pass
#		self.onOffCommands.setStatus(data.value, data.quality)

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
#			self.limit1H.setAttributeValue(data)


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
#			self.limit1H.setAttributeValue(data)

	def readPeakEnergy(self, data):
		self.peakEnergyWidget.setAttributeValue(data)

	def readPeakWidth(self, data):
		self.peakWidthWidget.setAttributeValue(data)

	def readExposure(self, data):
#		self.exposureWidget.setAttributeValue(data.value)
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
#		 for device in self.devices.itervalues():
#			 device.terminate()
		for a in self.attributes.itervalues():
			print 'Stopping', a.name
			a.stopRead()
		for a in self.attributes.itervalues():			
			a.readThread.join()
		event.accept()

	def setupLayout(self):
		s='QWidget{background-color: #000000; }'
		self.setStyleSheet(s)

		self.frame_sizes = qw.QTangoSizes()
		self.frame_sizes.barHeight = 30
		self.frame_sizes.barWidth = 20
		self.frame_sizes.readAttributeWidth = 300
		self.frame_sizes.writeAttributeWidth = 150
		self.frame_sizes.fontStretch= 80
		self.frame_sizes.fontType = 'Segoe UI'
#		self.frame_sizes.fontType = 'Trebuchet MS'
		self.attr_sizes = qw.QTangoSizes()
		self.attr_sizes.barHeight = 20
		self.attr_sizes.barWidth = 20
		self.attr_sizes.readAttributeWidth = 300
		self.attr_sizes.writeAttributeWidth = 299
		self.attr_sizes.fontStretch= 80
		self.attr_sizes.fontType = 'Segoe UI'
#		self.attr_sizes.fontType = 'Trebuchet MS'


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

		self.layoutAttributes2 = QtGui.QVBoxLayout()
		self.layoutAttributes2.setMargin(0)
		self.layoutAttributes2.setSpacing(self.attr_sizes.barHeight/2)
		self.layoutAttributes2.setContentsMargins(0, 0, 0, 0)

		self.title = qw.QTangoTitleBar('Oscillator control')
		self.setWindowTitle('Oscillator control')
		self.sidebar = qw.QTangoSideBar(colors = self.colors, sizes = self.frame_sizes)
		self.bottombar = qw.QTangoHorizontalBar()

		self.finesseName = qw.QTangoDeviceNameStatus(colors = self.colors, sizes = self.frame_sizes)
		self.finesseName.setAttributeName('Finesse')

		self.shutter_widget = qw.QTangoCommandSelection('Shutter', colors = self.colors, sizes = self.attr_sizes)
		self.shutter_widget.addCmdButton('Open', self.openFinesseShutter)
		self.shutter_widget.addCmdButton('Close', self.closeFinesseShutter)

		self.laserOperationWidget = qw.QTangoCommandSelection('Laser', colors = self.colors, sizes = self.attr_sizes)
		self.laserOperationWidget.addCmdButton('Start', self.onFinesse)
		self.laserOperationWidget.addCmdButton('Stop', self.offFinesse)


		self.laserTempWidget = qw.QTangoReadAttributeSlider4(colors = self.colors, sizes = self.attr_sizes)
		self.laserTempWidget.setAttributeName('Pump temperature', ''.join((unichr(0x00b0),'C')))
		self.laserTempWidget.setAttributeWarningLimits([25, 27])
		self.laserTempWidget.setSliderLimits(23, 28)

# 		self.laserTempWidget2 = qw.QTangoReadAttributeTrend(colors = self.colors, sizes = self.attr_sizes)
# 		self.laserTempWidget2.setAttributeName('Pump temperature')
# 		self.laserTempWidget2.setAttributeWarningLimits([25, 27])
# 		self.laserTempWidget2.setTrendLimits(23, 28)
# 		self.laserTempWidget2.valueTrend.setYRange(23.0,28.0, padding=0.05)


		self.laserPowerWidget = qw.QTangoWriteAttributeSlider4(colors = self.colors, sizes = self.attr_sizes)
		self.laserPowerWidget.setAttributeName('Pump power', 'W')
		self.laserPowerWidget.setSliderLimits(0, 6)
		self.laserPowerWidget.setAttributeWarningLimits([4, 5.5])
#		self.laserPowerWidget.setAttributeWriteValue(5)
		self.laserPowerWidget.writeValueSpinbox.editingFinished.connect(self.writePumpPower)

		self.prism1PositionWidget = qw.QTangoWriteAttributeSlider4(colors = self.colors, sizes = self.attr_sizes)
		self.prism1PositionWidget.setAttributeName('Prism 1', 'steps')
		self.prism1PositionWidget.setSliderLimits(-500, 500)
		self.prism1PositionWidget.setAttributeWarningLimits((-500, 500))
		self.prism1PositionWidget.writeValueSpinbox.editingFinished.connect(self.writePrism1Position)

		self.prism1LimitWidget = qw.QTangoReadAttributeBoolean(colors = self.colors, sizes = self.attr_sizes)
		self.prism1LimitWidget.setAttributeName('Prism1 limit')

		self.prism2PositionWidget = qw.QTangoWriteAttributeSlider4(colors = self.colors, sizes = self.attr_sizes)
		self.prism2PositionWidget.setAttributeName('Prism 2', 'steps')
		self.prism2PositionWidget.setSliderLimits(-500, 500)
		self.prism2PositionWidget.setAttributeWarningLimits((-500, 500))
		self.prism2PositionWidget.writeValueSpinbox.editingFinished.connect(self.writePrism2Position)

		self.prism2LimitWidget = qw.QTangoReadAttributeBoolean(colors = self.colors, sizes = self.attr_sizes)
		self.prism2LimitWidget.setAttributeName('Prism2 limit')

		self.spectrometerName = qw.QTangoDeviceNameStatus(colors = self.colors, sizes = self.frame_sizes)
		self.spectrometerName.setAttributeName('Spectrometer')

		self.onOffCommands = qw.QTangoCommandSelection('Spectrometer commands', colors = self.colors, sizes = self.attr_sizes)
		self.onOffCommands.addCmdButton('Init', self.initSpectrometer)
		self.onOffCommands.addCmdButton('On', self.onSpectrometer)
		self.onOffCommands.addCmdButton('Off', self.offSpectrometer)
		self.onOffCommands.addCmdButton('Stop', self.stopSpectrometer)
		self.peakWidthWidget = qw.QTangoReadAttributeSlider4(colors = self.colors, sizes = self.attr_sizes)
		self.peakWidthWidget.setAttributeName('Spectral width', 'nm')
		self.peakWidthWidget.setAttributeWarningLimits([35, 100])
		self.peakWidthWidget.setSliderLimits(0, 70)
		self.peakEnergyWidget = qw.QTangoReadAttributeSlider4(colors = self.colors, sizes = self.attr_sizes)
		self.peakEnergyWidget.setAttributeName('Laser energy', 'a.u.')
		self.peakEnergyWidget.setAttributeWarningLimits([0.1, 10])
		self.peakEnergyWidget.setSliderLimits(0, 0.3)

		self.oscSpectrumPlot = qw.QTangoReadAttributeSpectrum(colors = self.colors, sizes = self.attr_sizes)
		self.oscSpectrumPlot.setAttributeName('Oscillator spectrum')
		self.oscSpectrumPlot.setXRange(700, 900)
		self.oscSpectrumPlot.fixedSize(True)


		layout2.addWidget(self.title)
		layout2.addLayout(layoutData)
		layoutData.addLayout(self.layout_attributes)
		layoutData.addSpacerItem(spacerItemH)
		layoutData.addLayout(self.layoutAttributes2)

		self.layout_attributes.addWidget(self.finesseName)
		self.layout_attributes.addWidget(self.spectrometerName)
		self.layout_attributes.addSpacerItem(spacerItemV)
		self.layout_attributes.addWidget(self.shutter_widget)
		self.layout_attributes.addWidget(self.laserOperationWidget)
		self.layout_attributes.addWidget(self.laserPowerWidget)
		self.layout_attributes.addWidget(self.laserTempWidget)
#		self.layout_attributes.addWidget(self.laserTempWidget2)
#		self.layout_attributes.addWidget(self.laserTempTrend)

		self.layout_attributes.addSpacerItem(spacerItemV)
		self.layout_attributes.addWidget(self.prism1PositionWidget)
		self.layout_attributes.addWidget(self.prism1LimitWidget)
		self.layout_attributes.addWidget(self.prism2PositionWidget)
		self.layout_attributes.addWidget(self.prism2LimitWidget)

		self.layoutAttributes2.addSpacerItem(spacerItemV)
		self.layoutAttributes2.addWidget(self.onOffCommands)
		self.layoutAttributes2.addWidget(self.peakWidthWidget)
		self.layoutAttributes2.addWidget(self.peakEnergyWidget)
		self.layoutAttributes2.addWidget(self.oscSpectrumPlot)


		layout1.addWidget(self.sidebar)
		layout1.addLayout(layout2)
		layout0.addLayout(layout1)
		layout0.addWidget(self.bottombar)

#		self.resize(500,800)
		self.setGeometry(200,100,500,800)

		self.update()

if __name__ == '__main__':
	app = QtGui.QApplication(sys.argv)

	splash_pix = QtGui.QPixmap('splash_tangoloading.png')
	splash = QtGui.QSplashScreen(splash_pix, QtCore.Qt.WindowStaysOnTopHint)
	splash.setMask(splash_pix.mask())
	splash.show()
	splash.showMessage('	     Importing modules', alignment = QtCore.Qt.AlignBottom | QtCore.Qt.AlignLeft, color = QtGui.QColor('#66cbff'))
	app.processEvents()

	import QTangoWidgets.QTangoWidgets as qw
	from QTangoWidgets.AttributeReadThreadClass import AttributeClass
	import pyqtgraph as pg
	import PyTango as pt
	import threading
	import numpy as np

	splash.showMessage('	     Starting GUI', alignment = QtCore.Qt.AlignBottom | QtCore.Qt.AlignLeft, color = QtGui.QColor('#66cbff'))
	app.processEvents()
	myapp = TangoDeviceClient()
	myapp.show()
	splash.finish(myapp)
	sys.exit(app.exec_())