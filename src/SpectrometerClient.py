# -*- coding:utf-8 -*-
"""
Created on 19 nov 2013

@author: Filip
"""
from PyQt4 import QtGui, QtCore

import time
import sys


# noinspection PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit
class TangoDeviceClient(QtGui.QWidget):
	def __init__(self, parent = None):
		QtGui.QWidget.__init__(self,parent)
#		self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
		self.timeVector = None
		self.xData = None
		self.xDataTemp = None

		self.setupLayout()

		splash.showMessage('Initializing devices', alignment = QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
		app.processEvents()

		self.devices = {}
		self.devices['spectrometer']=pt.DeviceProxy('gunlaser/devices/spectrometer_diag')

		splash.showMessage('Reading startup attributes', alignment = QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
		app.processEvents()

		timeVectorAttr = self.devices['spectrometer'].read_attribute('wavelengths')
		self.timeVector = timeVectorAttr.value

		expInit = self.devices['spectrometer'].read_attribute('exposuretime')
		self.exposureWidget.setAttributeWriteValue(expInit.w_value)

		splash.showMessage('Initializing attributes', alignment = QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
		app.processEvents()

		self.guiLock = threading.Lock()
		self.attributes = {}
		self.attributes['peakenergy'] = AttributeClass('peakenergy', self.devices['spectrometer'], 0.3)
		self.attributes['peakwidth'] = AttributeClass('peakwidth', self.devices['spectrometer'], 0.3)
		self.attributes['spectrum'] = AttributeClass('spectrum', self.devices['spectrometer'], 0.3)
		self.attributes['exposure'] = AttributeClass('exposuretime', self.devices['spectrometer'], 0.3)
 		self.attributes['spectrometerstate'] = AttributeClass('state', self.devices['spectrometer'], 0.3, self.readSpectrometerState)
# 		self.attributes['spectrometerstatus'] = AttributeClass('status', self.devices['spectrometer'], 0.3)

 		self.attributes['peakenergy'].attrSignal.connect(self.readPeakEnergy)
 		self.attributes['peakwidth'].attrSignal.connect(self.readPeakWidth)
 		self.attributes['spectrum'].attrSignal.connect(self.readSpectrum)
 		self.attributes['exposure'].attrSignal.connect(self.readExposure)
 		self.attributes['spectrometerstate'].attrSignal.connect(self.readSpectrometerState)

		splash.showMessage('Setting up variables', alignment = QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
		app.processEvents()

# 		self.timer = QtCore.QTimer(self)
# 		self.timer.timeout.connect(self.checkDevices)
# 		self.timer.start(100)



	def checkDevices(self):
		for a in self.attributes.itervalues():
			pass
#			a.attr_read()

	def readSpectrometerState(self, data):
		self.spectrometerName.setState(data)
		self.onOffCommands.setStatus(data)

	def readSpectrometerStatus(self, data):
		pass
#		self.onOffCommands.setStatus(data.value, data.quality)

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

	def readSpectrum(self, data):
		if self.timeVector == None:
			self.oscSpectrumPlot.setSpectrum(0, data.value)
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

	def setupAttributeLayout(self, attributeList = []):
		self.attributeQObjects = []
		for att in attributeList:
			attQObject = qw.QTangoReadAttributeDouble()
			attQObject.setAttributeName(att.name)
			self.attributeQObjects.append(attQObject)
			self.layout_attributes.addWidget(attQObject)

	def closeEvent(self, event):
# 		for device in self.devices.itervalues():
# 			device.terminate()
		for a in self.attributes.itervalues():
			print 'Stopping', a.name
			a.stop_read()
			a.readThread.join()
		event.accept()

	def setupLayout(self):
		s='QWidget{background-color: #000000; }'
		self.setStyleSheet(s)

		self.frame_sizes = qw.QTangoSizes()
		self.frame_sizes.barHeight = 30
		self.frame_sizes.barWidth = 20
		self.frame_sizes.readAttributeWidth = 240
		self.frame_sizes.writeAttributeWidth = 299
		self.frame_sizes.fontStretch= 80
		self.frame_sizes.fontType = 'Segoe UI'
#		self.frame_sizes.fontType = 'Trebuchet MS'
		self.attr_sizes = qw.QTangoSizes()
		self.attr_sizes.barHeight = 20
		self.attr_sizes.barWidth = 20
		self.attr_sizes.readAttributeWidth = 240
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

		self.title = qw.QTangoTitleBar('Gunlaser spectrometer')
		self.sidebar = qw.QTangoSideBar(colors = self.colors, sizes = self.frame_sizes)
#  		self.sidebar.addCmdButton('Init', self.initSpectrometer)
#  		self.sidebar.addCmdButton('On', self.onSpectrometer)
#  		self.sidebar.addCmdButton('Off', self.offSpectrometer)
#  		self.sidebar.addCmdButton('Stop', self.stopSpectrometer)
		self.bottombar = qw.QTangoHorizontalBar()
		self.spectrometerName = qw.QTangoDeviceNameStatus(colors = self.colors, sizes = self.frame_sizes)
		self.spectrometerName.setAttributeName('Spectrometer')

		self.onOffCommands = qw.QTangoCommandSelection('Commands', colors = self.colors, sizes = self.attr_sizes)
		self.onOffCommands.addCmdButton('Init', self.initSpectrometer)
		self.onOffCommands.addCmdButton('On', self.onSpectrometer)
		self.onOffCommands.addCmdButton('Off', self.offSpectrometer)
		self.onOffCommands.addCmdButton('Stop', self.stopSpectrometer)
		self.peakWidthWidget = qw.QTangoReadAttributeSlider2(colors = self.colors, sizes = self.attr_sizes)
		self.peakWidthWidget.setAttributeName('Spectral width')
		self.peakWidthWidget.setAttributeWarningLimits((20, 70))
		self.peakWidthWidget.setSliderLimits(0, 100)
		self.peakEnergyWidget = qw.QTangoReadAttributeSlider2(colors = self.colors, sizes = self.attr_sizes)
		self.peakEnergyWidget.setAttributeName('Laser energy')
		self.peakEnergyWidget.setAttributeWarningLimits((0.5, 5))
		self.peakEnergyWidget.setSliderLimits(0, 2)
		self.exposureWidget = qw.QTangoWriteAttributeSlider(colors = self.colors, sizes = self.attr_sizes)
		self.exposureWidget.setAttributeName('Exposure time')
		self.exposureWidget.setAttributeWarningLimits((10, 900))
		self.exposureWidget.writeValueSpinbox.editingFinished.connect(self.writeExposure)
		self.exposureWidget.setSliderLimits(0, 1000)

		self.oscSpectrumPlot = qw.QTangoReadAttributeSpectrum(colors = self.colors, sizes = self.attr_sizes)
		self.oscSpectrumPlot.setAttributeName('Oscillator spectrum')
		self.oscSpectrumPlot.setXRange(700, 900)
		self.oscSpectrumPlot.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

		layout2.addWidget(self.title)
		layout2.addLayout(layoutData)
		layoutData.addLayout(self.layout_attributes)
		layoutData.addWidget(self.oscSpectrumPlot)

		self.layout_attributes.addWidget(self.spectrometerName)
		self.layout_attributes.addWidget(self.onOffCommands)
		self.layout_attributes.addSpacerItem(spacerItemV)
		self.layout_attributes.addWidget(self.peakWidthWidget)
		self.layout_attributes.addWidget(self.peakEnergyWidget)
		self.layout_attributes.addWidget(self.exposureWidget)

		layout1.addWidget(self.sidebar)
		layout1.addLayout(layout2)
		layout0.addLayout(layout1)
		layout0.addWidget(self.bottombar)

		self.resize(800,400)

		self.update()

if __name__ == '__main__':
	app = QtGui.QApplication(sys.argv)

	splash_pix = QtGui.QPixmap('splash_loading.png')
	splash = QtGui.QSplashScreen(splash_pix, QtCore.Qt.WindowStaysOnTopHint)
	splash.setMask(splash_pix.mask())
	splash.show()
	splash.showMessage('Importing modules', alignment = QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
	app.processEvents()

	import QTangoWidgets.QTangoWidgets as qw
	from QTangoWidgets.AttributeReadThreadClass import AttributeClass
	import pyqtgraph as pg
	import PyTango as pt
	import threading
	import numpy as np

	splash.showMessage('Starting GUI', alignment = QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
	app.processEvents()
	myapp = TangoDeviceClient()
	myapp.show()
	splash.finish(myapp)
	sys.exit(app.exec_())