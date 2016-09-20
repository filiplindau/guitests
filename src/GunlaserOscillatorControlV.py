'''
Created on 8 aug 2014

@author: Filip
'''
# -*- coding:utf-8 -*-
from PyQt4 import QtGui, QtCore

import time
import sys




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
		self.shutterWidget.setStatus(data)

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
		data.value = data.value * 6.1
		self.peakEnergyWidget.setAttributeValue(data)

	def readPeakWidth(self, data):
		self.peakWidthWidget.setAttributeValue(data)

	def readPeakWavelength(self, data):
		self.peakWavelengthWidget.setAttributeValue(data)

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
			self.layoutAttributes.addWidget(attQObject)

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

		self.frameSizes = qw.QTangoSizes()
		self.frameSizes.barHeight = 20
		self.frameSizes.barWidth = 18
		self.frameSizes.readAttributeWidth = 250
		self.frameSizes.writeAttributeWidth = 150
		self.frameSizes.fontStretch= 80
		self.frameSizes.fontType = 'Segoe UI'
#		self.frameSizes.fontType = 'Trebuchet MS'

		self.attrSizes = qw.QTangoSizes()
		self.attrSizes.barHeight = 22
		self.attrSizes.barWidth = 18
		self.attrSizes.readAttributeWidth = 250
		self.attrSizes.readAttributeHeight = 250
		self.attrSizes.writeAttributeWidth = 299
		self.attrSizes.fontStretch= 80
		self.attrSizes.fontType = 'Segoe UI'
#		self.attrSizes.fontType = 'Trebuchet MS'


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

		self.title = qw.QTangoTitleBar('Oscillator control')
		self.setWindowTitle('Oscillator control')
		self.sidebar = qw.QTangoSideBar(colors = self.colors, sizes = self.frameSizes)
		self.bottombar = qw.QTangoHorizontalBar()

		self.finesseName = qw.QTangoDeviceNameStatus(colors = self.colors, sizes = self.frameSizes)
		self.finesseName.setAttributeName('Finesse')

		self.shutterWidget = qw.QTangoCommandSelection('Shutter', colors = self.colors, sizes = self.attrSizes)
		self.shutterWidget.addCmdButton('Open', self.openFinesseShutter)
		self.shutterWidget.addCmdButton('Close', self.closeFinesseShutter)

		self.laserOperationWidget = qw.QTangoCommandSelection('Laser', colors = self.colors, sizes = self.attrSizes)
		self.laserOperationWidget.addCmdButton('Start', self.onFinesse)
		self.laserOperationWidget.addCmdButton('Stop', self.offFinesse)

		self.attrSizes.readAttributeHeight = 250
		self.laserTempWidget = qw.QTangoReadAttributeSliderV(colors = self.colors, sizes = self.attrSizes)
		self.laserTempWidget.setAttributeName('Temp', ''.join((unichr(0x00b0),'C')))
		self.laserTempWidget.setAttributeWarningLimits([25, 27])
		self.laserTempWidget.setSliderLimits(23, 28)

		self.laserPowerWidget = qw.QTangoWriteAttributeSliderV(colors = self.colors, sizes = self.attrSizes)
		self.laserPowerWidget.setAttributeName('Pump pwr', 'W')
		self.laserPowerWidget.setSliderLimits(0, 6)
		self.laserPowerWidget.setAttributeWarningLimits([4, 5.5])
		self.laserPowerWidget.writeValueLineEdit.editingFinished.connect(self.writePumpPower)

		self.attrSizes.readAttributeHeight = 250
		self.prism1PositionWidget = qw.QTangoWriteAttributeSliderV(colors = self.colors, sizes = self.attrSizes)
		self.prism1PositionWidget.setAttributeName('Prism 1', 'steps')
		self.prism1PositionWidget.setSliderLimits(-500, 500)
		self.prism1PositionWidget.setAttributeWarningLimits((-500, 500))
		self.prism1PositionWidget.writeValueLineEdit.editingFinished.connect(self.writePrism1Position)

		self.prism1LimitWidget = qw.QTangoReadAttributeBoolean(colors = self.colors, sizes = self.attrSizes)
		self.prism1LimitWidget.setAttributeName('Prism1 limit')

		self.prism2PositionWidget = qw.QTangoWriteAttributeSliderV(colors = self.colors, sizes = self.attrSizes)
		self.prism2PositionWidget.setAttributeName('Prism 2', 'steps')
		self.prism2PositionWidget.setSliderLimits(-500, 500)
		self.prism2PositionWidget.setAttributeWarningLimits((-500, 500))
		self.prism2PositionWidget.writeValueLineEdit.editingFinished.connect(self.writePrism2Position)

		self.prism2LimitWidget = qw.QTangoReadAttributeBoolean(colors = self.colors, sizes = self.attrSizes)
		self.prism2LimitWidget.setAttributeName('Prism2 limit')

		self.spectrometerName = qw.QTangoDeviceNameStatus(colors = self.colors, sizes = self.frameSizes)
		self.spectrometerName.setAttributeName('Spectrometer')

		self.onOffCommands = qw.QTangoCommandSelection('Spectrometer commands', colors = self.colors, sizes = self.attrSizes)
		self.onOffCommands.addCmdButton('Init', self.initSpectrometer)
		self.onOffCommands.addCmdButton('On', self.onSpectrometer)
		self.onOffCommands.addCmdButton('Off', self.offSpectrometer)
		self.onOffCommands.addCmdButton('Stop', self.stopSpectrometer)

		self.attrSizes.readAttributeHeight = 200
		self.peakWidthWidget = qw.QTangoReadAttributeSliderV(colors = self.colors, sizes = self.attrSizes)
		self.peakWidthWidget.setAttributeName(''.join((unichr(0x0394),unichr(0x03bb), ' FWHM')), 'nm')
		self.peakWidthWidget.setAttributeWarningLimits([35, 100])
		self.peakWidthWidget.setSliderLimits(0, 70)
		self.peakEnergyWidget = qw.QTangoReadAttributeSliderV(colors = self.colors, sizes = self.attrSizes)
		self.peakEnergyWidget.setAttributeName('Osc pwr', 'mW')
		self.peakEnergyWidget.setAttributeWarningLimits([350, 800])
		self.peakEnergyWidget.setSliderLimits(100, 450)
		self.peakWavelengthWidget = qw.QTangoReadAttributeSliderV(colors = self.colors, sizes = self.attrSizes)
		self.peakWavelengthWidget.setAttributeName(''.join((unichr(0x03bb),' peak')), 'nm')
		self.peakWavelengthWidget.setAttributeWarningLimits([780, 810])
		self.peakWavelengthWidget.setSliderLimits(760, 840)

		self.oscSpectrumPlot = qw.QTangoReadAttributeSpectrum(colors = self.colors, sizes = self.attrSizes)
		self.oscSpectrumPlot.setAttributeName('Oscillator spectrum')
		self.oscSpectrumPlot.setXRange(700, 900)
		self.oscSpectrumPlot.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
#		self.oscSpectrumPlot.fixedSize(True)


		layout2.addWidget(self.title)
		layout2.addLayout(layoutData)
		layoutData.addLayout(self.layoutAttributes)
#		layoutData.addSpacerItem(spacerItemH)
		layoutData.addLayout(self.layoutAttributes2)
		layoutData.addLayout(self.layoutAttributes3)

		self.layoutAttributes.addWidget(self.finesseName)
		self.layoutAttributes.addWidget(self.shutterWidget)
		self.layoutAttributes.addWidget(self.laserOperationWidget)
		self.layoutAttributes.addSpacerItem(spacerItemV)

		layoutSliders = QtGui.QHBoxLayout()
		layoutSliders.addWidget(self.laserPowerWidget)
		layoutSliders.addWidget(self.laserTempWidget)
		layoutSliders.addSpacerItem(spacerItemBar)
		layoutSliders.addWidget(self.prism1PositionWidget)
#		self.layoutAttributes2.addWidget(self.prism1LimitWidget)
#		self.layoutAttributes2.addSpacerItem(spacerItemBar)
		layoutSliders.addWidget(self.prism2PositionWidget)
#		self.layoutAttributes2.addWidget(self.prism2LimitWidget)
		self.layoutAttributes2.addLayout(layoutSliders)
		self.layoutAttributes2.addSpacerItem(spacerItemV)

		self.layoutAttributes3.addWidget(self.spectrometerName)
		self.layoutAttributes3.addWidget(self.onOffCommands)
		layoutSpectrometerSliders = QtGui.QHBoxLayout()
		layoutSpectrometerSliders.addWidget(self.peakEnergyWidget)
		layoutSpectrometerSliders.addWidget(self.peakWidthWidget)
		layoutSpectrometerSliders.addWidget(self.peakWavelengthWidget)
		self.layoutAttributes3.addSpacerItem(spacerItemV)
		self.layoutAttributes3.addLayout(layoutSpectrometerSliders)
		layoutData.addWidget(self.oscSpectrumPlot)


		layout1.addWidget(self.sidebar)
		layout1.addLayout(layout2)
		layout0.addLayout(layout1)
#		layout0.addWidget(self.bottombar)

#		self.resize(500,800)
		self.setGeometry(200,100,800,300)

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