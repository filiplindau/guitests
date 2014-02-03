# -*- coding:utf-8 -*-
"""
Created on 2 dec 2013

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
		self.readThread = threading.Thread(name = self.name, target = self.attr_read)
		self.stopThread = False
		
		self.startRead() 
		
	def attr_read(self):
		replyReady = True
		while self.stopThread == False:
			t = time.time()
				
			if t-self.lastRead > self.interval:
				self.lastRead = t				
				try:
					id = self.device.read_attribute_asynch(self.name)
					
					replyReady = False
				except pt.DevFailed, e:
					if e[0].reason == 'API_DeviceTimeOut':
						print 'Timeout'
					else:
						print self.name, ' error ', e[0].reason
					self.attr = pt.DeviceAttribute()
					self.attr.quality = pt.AttrQuality.ATTR_INVALID
					self.attr.value = None
					self.attr.w_value = None
					self.attrSignal.emit(self.attr)
				except Exception, e:
					print self.name, ' recovering from ', str(e)				
					self.attr = pt.DeviceAttribute()
					self.attr.quality = pt.AttrQuality.ATTR_INVALID
					self.attr.value = None
					self.attrSignal.emit(self.attr)
					
				while replyReady == False and self.stopThread == False:
					try:
						self.attr = self.device.read_attribute_reply(id)
						replyReady = True
						self.attrSignal.emit(self.attr)
						# Read only once if interval = None:
						if self.interval == None:
							self.stopThread = True
							self.interval = 0.0
					except Exception, e:
						if e[0].reason == 'API_AsynReplyNotArrived':
#							print self.name, ' not replied'
							time.sleep(0.1)
						else:
							replyReady = True
							print 'Error reply ', self.name, str(e)
				
			if self.interval != None:
				time.sleep(self.interval)
			else:
				time.sleep(1)
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
		readComplete = False		
		while readComplete == False:
			try:
				self.devices['m0v']=pt.DeviceProxy('m4gun/motors/m0v')
				readComplete = True
			except Exception, e:
				print e
		readComplete = False		
		while readComplete == False:
			try:			
				self.devices['m0h']=pt.DeviceProxy('m4gun/motors/m0h')
				readComplete = True
			except Exception, e:
				print e

		splash.showMessage('Reading startup attributes', alignment = QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
		app.processEvents()

# 		readComplete = False		
# 		while readComplete == False:
# 			try:
# 				hInit = self.devices['m0h'].read_attribute('position')
# 				self.positionHWidget.setAttributeWriteValue(hInit.w_value)
# 				readComplete = True
# 			except Exception, e:
# 				print e
# 
# 		readComplete = False		
# 		while readComplete == False:
# 			try:
# 				vInit = self.devices['m0v'].read_attribute('position')
# 				self.positionVWidget.setAttributeWriteValue(vInit.w_value)
# 				readComplete = True
# 			except Exception, e:
# 				print e

		splash.showMessage('Initializing attributes', alignment = QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
		app.processEvents()

		self.guiLock = threading.Lock()				
		self.attributes = {}
		self.attributes['position_v'] = AttributeClass('position', self.devices['m0v'], 0.3)
		self.attributes['position_h'] = AttributeClass('position', self.devices['m0h'], 0.3)
		self.attributes['limit_v'] = AttributeClass('limit_switches', self.devices['m0v'], 0.3)
		self.attributes['limit_h'] = AttributeClass('limit_switches', self.devices['m0h'], 0.3)

# 		self.attributes['status_v'] = AttributeClass('status', self.devices['m0v'], 0.3)
# 		self.attributes['status_h'] = AttributeClass('status', self.devices['m0h'], 0.3)
		self.attributes['state_v'] = AttributeClass('state', self.devices['m0v'], 0.3)
		self.attributes['state_h'] = AttributeClass('state', self.devices['m0h'], 0.3)
		
		self.attributes['position_v'].attrSignal.connect(self.readPositionV)
		self.attributes['position_h'].attrSignal.connect(self.readPositionH)
		self.attributes['limit_h'].attrSignal.connect(self.readLimitH)
		self.attributes['limit_v'].attrSignal.connect(self.readLimitV)
 		self.attributes['state_v'].attrSignal.connect(self.readStateV)
 		self.attributes['state_h'].attrSignal.connect(self.readStateH)

		splash.showMessage('Setting up variables', alignment = QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
		app.processEvents()

# 		self.timer = QtCore.QTimer(self)
# 		self.timer.timeout.connect(self.checkDevices)
# 		self.timer.start(100)
		

		
	def checkDevices(self):
		for a in self.attributes.itervalues():
			pass
#			a.attr_read()
	
	def readStateH(self, data):
		self.hName.setState(data)
		data.value = ''
		self.onOffCommands.setStatus(data)

	def readStateV(self, data):
		self.vName.setState(data)

	def readStatusH(self, data):
		pass
#		self.onOffCommands.setStatus(data.value, data.quality)

	def readLimitH(self, data):
		# The limits attribute is a spectrum attribute.
		# Convert to two scalar attributes with the
		# value of each limit switch as value.
		vals = data.value
		if data.dim_x>1:
			data.value[0] = vals[0]
			self.limit0H.setAttributeValue(data)
			data.value[0] = vals[1]
			self.limit1H.setAttributeValue(data)
		else:
			# Something wrong, maybe not initialized
			self.limit0H.setAttributeValue(data)
			self.limit1H.setAttributeValue(data)
		

	def readLimitV(self, data):
		# The limits attribute is a spectrum attribute.
		# Convert to two scalar attributes with the
		# value of each limit switch as value.
		vals = data.value
		if data.dim_x>1:
			data.value[0] = vals[0]
			self.limit0V.setAttributeValue(data)
			data.value[0] = vals[1]
			self.limit1V.setAttributeValue(data)
		else:
			# Something wrong, maybe not initialized
			self.limit0V.setAttributeValue(data)
			self.limit1V.setAttributeValue(data)

	def readPositionH(self, data):
		self.positionHWidget.setAttributeValue(data)

	def readPositionV(self, data):
		self.positionVWidget.setAttributeValue(data)
		
	def writePositionH(self):
		w = self.positionHWidget.getWriteValue()
		self.attributes['position_h'].attr_write(w)

	def writePositionV(self):
		w = self.positionVWidget.getWriteValue()
		self.attributes['position_v'].attr_write(w)
			
	def stopMotors(self):
		self.devices['m0h'].command_inout('stop')
		self.devices['m0v'].command_inout('stop')

	def homeMotors(self):
		self.devices['m0h'].command_inout('home')
		self.devices['m0v'].command_inout('home')
				
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
		for a in self.attributes.itervalues():
			print 'Stopping', a.name
			a.stopRead()
			a.readThread.join()
		event.accept()
		
	def setupLayout(self):
		s='QWidget{background-color: #000000; }'
		self.setStyleSheet(s)
		
		w = 250
		
		self.frameSizes = qw.QTangoSizes()
		self.frameSizes.readAttributeWidth = w
		self.frameSizes.writeAttributeWidth = 299
		self.frameSizes.fontStretch= 80
		self.frameSizes.fontType = 'Segoe UI'
#		self.frameSizes.fontType = 'Trebuchet MS'
		self.attrSizes = qw.QTangoSizes()
		self.attrSizes.barHeight = 20
		self.attrSizes.barWidth = 60
		self.attrSizes.readAttributeWidth = w
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
		spacerItemV_bar = QtGui.QSpacerItem(self.attrSizes.barHeight, self.attrSizes.barHeight, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
		
		layoutData = QtGui.QHBoxLayout()
		layoutData.setMargin(self.attrSizes.barHeight/2)
		layoutData.setSpacing(self.attrSizes.barHeight/2)
		self.layoutAttributes = QtGui.QVBoxLayout()
		self.layoutAttributes.setMargin(0)
		self.layoutAttributes.setSpacing(self.attrSizes.barHeight/2)
		self.layoutAttributes.setContentsMargins(0, 0, 0, 0)
		
		self.title = qw.QTangoTitleBar('Mirror motors')
		self.sidebar = qw.QTangoSideBar(colors = self.colors, sizes = self.frameSizes)
#  		self.sidebar.addCmdButton('Init', self.initSpectrometer)
		self.bottombar = qw.QTangoHorizontalBar()
		self.hName = qw.QTangoDeviceNameStatus(colors = self.colors, sizes = self.frameSizes)
		self.hName.setAttributeName('Horizontal')
		self.vName = qw.QTangoDeviceNameStatus(colors = self.colors, sizes = self.frameSizes)
		self.vName.setAttributeName('Vertical')
				
		self.onOffCommands = qw.QTangoCommandSelection('Commands', colors = self.colors, sizes = self.attrSizes)
		self.onOffCommands.addCmdButton('Home', self.homeMotors)
		self.onOffCommands.addCmdButton('Stop', self.stopMotors)
		
		self.limit0V = qw.QTangoReadAttributeBoolean(colors = self.colors, sizes = self.attrSizes)
		self.limit0V.setAttributeName('Vertical limit 0')
		self.limit1V = qw.QTangoReadAttributeBoolean(colors = self.colors, sizes = self.attrSizes)
		self.limit1V.setAttributeName('Vertical limit 1')

		self.limit0H = qw.QTangoReadAttributeBoolean(colors = self.colors, sizes = self.attrSizes)
		self.limit0H.setAttributeName('Horizontal limit 0')
		self.limit1H = qw.QTangoReadAttributeBoolean(colors = self.colors, sizes = self.attrSizes)
		self.limit1H.setAttributeName('Horizontal limit 1')
		
		self.positionHWidget = qw.QTangoWriteAttributeSlider(colors = self.colors, sizes = self.attrSizes)
		self.positionHWidget.setAttributeName('Horizontal pos')
		self.positionHWidget.writeValueSpinbox.editingFinished.connect(self.writePositionH)
		self.positionHWidget.setAttributeWarningLimits([0, 6])
		self.positionHWidget.setSliderLimits(0, 6)
		
		self.positionVWidget = qw.QTangoWriteAttributeSlider(colors = self.colors, sizes = self.attrSizes)
		self.positionVWidget.setAttributeName('Vertical pos')
		self.positionVWidget.writeValueSpinbox.editingFinished.connect(self.writePositionV)
		self.positionVWidget.setAttributeWarningLimits([0, 6])
		self.positionVWidget.setSliderLimits(0, 6)
			
		layout2.addWidget(self.title)		
		layout2.addLayout(layoutData)
		layoutData.addLayout(self.layoutAttributes)
		layoutData.addSpacerItem(spacerItemH)
						
		self.layoutAttributes.addWidget(self.hName)
		self.layoutAttributes.addWidget(self.vName)
		self.layoutAttributes.addWidget(self.onOffCommands)
		self.layoutAttributes.addSpacerItem(spacerItemV)
		self.layoutAttributes.addWidget(self.limit0H)
		self.layoutAttributes.addWidget(self.limit1H)
		self.layoutAttributes.addWidget(self.positionHWidget)
		self.layoutAttributes.addSpacerItem(spacerItemV_bar)
		self.layoutAttributes.addWidget(self.limit0V)
		self.layoutAttributes.addWidget(self.limit1V)
		self.layoutAttributes.addWidget(self.positionVWidget)
		
		layout1.addWidget(self.sidebar)
		layout1.addLayout(layout2)
		layout0.addLayout(layout1)
		layout0.addWidget(self.bottombar)
		
		self.resize(300,400)
		
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