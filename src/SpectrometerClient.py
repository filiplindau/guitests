# -*- coding:utf-8 -*-
"""
Created on 19 nov 2013

@author: Filip
"""
from PyQt4 import QtGui, QtCore

import time 
import sys

class AttributeClass(object):
	def __init__(self, name, device, interval, callback = None):
		self.name = name
		self.device = device
		self.interval = interval
		self.callback = callback
		
		self.lastRead = time.time()
		self.attr = None
		
	def attr_read(self):
		t = time.time()
		if t-self.lastRead > self.interval:
			self.lastRead = t
			self.attr = self.device.read_attribute(self.name)
			if self.callback != None:
				self.callback(self.attr)
				
	def attr_write(self, wvalue):
		self.device.write_attribute(self.name, wvalue)

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
		self.devices['spectrometer']=pt.DeviceProxy('testfel/gunlaser/osc_spectrometer')

		splash.showMessage('Initializing attributes', alignment = QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
		app.processEvents()
		
		self.attributes = {}
		self.attributes['peakenergy'] = AttributeClass('peakenergy', self.devices['spectrometer'], 0.3, self.readPeakEnergy)
		self.attributes['peakwidth'] = AttributeClass('spectrumwidth', self.devices['spectrometer'], 0.3, self.readPeakWidth)
		self.attributes['spectrum'] = AttributeClass('spectrum', self.devices['spectrometer'], 0.3, self.readSpectrum)
		self.attributes['exposure'] = AttributeClass('exposuretime', self.devices['spectrometer'], 0.3, self.readExposure)
		self.attributes['spectrometerstate'] = AttributeClass('state', self.devices['spectrometer'], 0.3, self.readSpectrometerState)		
		self.attributes['spectrometerstatus'] = AttributeClass('status', self.devices['spectrometer'], 0.3, self.readSpectrometerStatus)

		splash.showMessage('Setting up variables', alignment = QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
		app.processEvents()

		timeVectorAttr = self.devices['spectrometer'].read_attribute('wavelengths')
		self.timeVector = timeVectorAttr.value

		expInit = self.devices['spectrometer'].read_attribute('exposuretime')
		self.exposureWidget.setAttributeWriteValue(expInit.w_value)
		
		self.timer = QtCore.QTimer(self)
		self.timer.timeout.connect(self.checkDevices)
		self.timer.start(100)
		
	def checkDevices(self):
		for a in self.attributes.itervalues():
			a.attr_read()
	
	def readSpectrometerState(self, data):
		self.spectrometerName.setState(data.value)

	def readSpectrometerStatus(self, data):
		pass
#		self.onOffCommands.setStatus(data.value, data.quality)

	def readPeakEnergy(self, data):
		self.peakEnergyWidget.setAttributeValue(data.value)
		
	def readPeakWidth(self, data):
		self.peakWidthWidget.setAttributeValue(data.value)

	def readExposure(self, data):
#		self.exposureWidget.setAttributeValue(data.value)
		self.exposureWidget.setAttributeValue(data)

	def writeExposure(self):
		w = self.exposureWidget.getWriteValue()
		self.attributes['exposure'].attr_write(w)
		
	def readSpectrum(self, data):
		if self.timeVector == None:
			self.oscSpectrumPlot.setSpectrum(0, data.value)
		else:
			self.oscSpectrumPlot.setSpectrum(xData = self.timeVector, yData = data.value)
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
			self.layoutAttributes.addWidget(attQObject)
			
	def closeEvent(self, event):
# 		for device in self.devices.itervalues():
# 			device.terminate()
		event.accept()
		
	def setupLayout(self):
		s='QWidget{background-color: #000000; }'
		self.setStyleSheet(s)
		
		self.frameSizes = qw.QTangoSizes()
		self.frameSizes.readAttributeWidth = 240
		self.frameSizes.writeAttributeWidth = 299
		self.frameSizes.fontStretch= 80
		self.frameSizes.fontType = 'Segoe UI'
#		self.frameSizes.fontType = 'Trebuchet MS'
		self.attrSizes = qw.QTangoSizes()
		self.attrSizes.barHeight = 20
		self.attrSizes.barWidth = 60
		self.attrSizes.readAttributeWidth = 240
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
		spacerItemV = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.MinimumExpanding)
		spacerItemH = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Minimum)
		
		layoutData = QtGui.QHBoxLayout()
		layoutData.setMargin(self.attrSizes.barHeight/2)
		layoutData.setSpacing(self.attrSizes.barHeight/2)
		self.layoutAttributes = QtGui.QVBoxLayout()
		self.layoutAttributes.setMargin(0)
		self.layoutAttributes.setSpacing(self.attrSizes.barHeight/2)
		self.layoutAttributes.setContentsMargins(0, 0, 0, 0)
		
		self.title = qw.QTangoTitleBar('Gunlaser spectrometer')
		self.sidebar = qw.QTangoSideBar(colors = self.colors, sizes = self.frameSizes)
#  		self.sidebar.addCmdButton('Init', self.initSpectrometer)
#  		self.sidebar.addCmdButton('On', self.onSpectrometer)
#  		self.sidebar.addCmdButton('Off', self.offSpectrometer)
#  		self.sidebar.addCmdButton('Stop', self.stopSpectrometer)
		self.bottombar = qw.QTangoHorizontalBar()
		self.spectrometerName = qw.QTangoDeviceNameStatus(colors = self.colors, sizes = self.frameSizes)
		self.spectrometerName.setAttributeName('Spectrometer')
				
		self.onOffCommands = qw.QTangoCommandSelection('Commands', colors = self.colors, sizes = self.attrSizes)
		self.onOffCommands.addCmdButton('Init', self.initSpectrometer)
		self.onOffCommands.addCmdButton('On', self.onSpectrometer)
		self.onOffCommands.addCmdButton('Off', self.offSpectrometer)
		self.onOffCommands.addCmdButton('Stop', self.stopSpectrometer)
		self.peakWidthWidget = qw.QTangoReadAttributeSlider(colors = self.colors, sizes = self.attrSizes)
		self.peakWidthWidget.setAttributeName('Spectral width')
		self.peakWidthWidget.setAttributeWarningLimits(7, 20)
		self.peakWidthWidget.setSliderLimits(0, 15)
		self.peakEnergyWidget = qw.QTangoReadAttributeSlider(colors = self.colors, sizes = self.attrSizes)
		self.peakEnergyWidget.setAttributeName('Laser energy')
		self.peakEnergyWidget.setAttributeWarningLimits(0.02, 1)
		self.peakEnergyWidget.setSliderLimits(0, 0.04)
		self.exposureWidget = qw.QTangoWriteAttributeSlider(colors = self.colors, sizes = self.attrSizes)
		self.exposureWidget.setAttributeName('Exposure time')
		self.exposureWidget.setAttributeWarningLimits(10, 900)
		self.exposureWidget.writeValueSpinbox.editingFinished.connect(self.writeExposure)
		self.exposureWidget.setSliderLimits(0, 1000)
		
		self.oscSpectrumPlot = qw.QTangoReadAttributeSpectrum(colors = self.colors, sizes = self.attrSizes)
		self.oscSpectrumPlot.setAttributeName('Oscillator spectrum')
		self.oscSpectrumPlot.setXRange(760, 820)
		self.oscSpectrumPlot.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
				
		layout2.addWidget(self.title)		
		layout2.addLayout(layoutData)
		layoutData.addLayout(self.layoutAttributes)
		layoutData.addWidget(self.oscSpectrumPlot)
						
		self.layoutAttributes.addWidget(self.spectrometerName)
		self.layoutAttributes.addWidget(self.onOffCommands)
		self.layoutAttributes.addSpacerItem(spacerItemV)
		self.layoutAttributes.addWidget(self.peakWidthWidget)
		self.layoutAttributes.addWidget(self.peakEnergyWidget)
		self.layoutAttributes.addWidget(self.exposureWidget)
		
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