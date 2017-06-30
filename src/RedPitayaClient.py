# -*- coding:utf-8 -*-
"""
Created on 29 jan 2014

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
							self.attr = pt.DeviceAttribute()
							self.attr.quality = pt.AttrQuality.ATTR_INVALID
							self.attr.value = None
							self.attr.w_value = None
							self.attrSignal.emit(self.attr)
							
				
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


# noinspection PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit
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
		self.devices['delaystage']=pt.DeviceProxy('testfel/gunlaser/delaystage')

		splash.showMessage('Reading startup attributes', alignment = QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
		app.processEvents()


		self.guiLock = threading.Lock()	
		self.delaystageLock = threading.Lock()			
		self.attributes = {}
		self.attributes['position'] = AttributeClass('position', self.devices['delaystage'], 0.3)
		self.attributes['limits'] = AttributeClass('limit_switches', self.devices['delaystage'], 0.3)
		self.attributes['state'] = AttributeClass('state', self.devices['delaystage'], 0.3)
		
		self.attributes['position'].attrSignal.connect(self.readPosition)
		self.attributes['limits'].attrSignal.connect(self.readLimits)
		self.attributes['state'].attrSignal.connect(self.readState)

		splash.showMessage('Setting up variables', alignment = QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
		app.processEvents()

			
	def readPosition(self, data):
		self.positionWidget.setAttributeValue(data)
		
	def writePosition(self):
		self.guiLock.acquire()
		w = self.positionWidget.getWriteValue()
		self.attributes['position'].attr_write(w)
		self.guiLock.release()
		
	def readLimits(self, data):
		# The limits attribute is a spectrum attribute.
		# Convert to two scalar attributes with the
		# value of each limit switch as value.
		vals = data.value
		if data.dim_x>1:
			data.value[0] = vals[0]
			self.limit0Widget.setAttributeValue(data)
			data.value[0] = vals[1]
			self.limit1Widget.setAttributeValue(data)
		else:
			# Something wrong, maybe not initialized
			self.limit0Widget.setAttributeValue(data)
			self.limit1Widget.setAttributeValue(data)
		
	
	def readState(self, data):
		self.delayName.setState(data)
		data.value = ''
		self.stopCommands.setStatus(data)
		
	def homeMotor(self):
		self.devices['delaystage'].command_inout('home')

	def stopMotor(self):
		self.devices['delaystage'].command_inout('stop')

		
	def setupAttributeLayout(self, attributeList = []):
		self.attributeQObjects = []
		for att in attributeList:
			attQObject = qw.QTangoReadAttributeDouble()
			attQObject.setAttributeName(att.name)
			self.attributeQObjects.append(attQObject)
			self.layout_attributes.addWidget(attQObject)
			
	def closeEvent(self, event):
		for a in self.attributes.itervalues():
			print 'Stopping', a.name
			a.stop_read()
			a.readThread.join()
		event.accept()
		
	def setupLayout(self):
		s='QWidget{background-color: #000000; }'
		self.setStyleSheet(s)
		
		self.frame_sizes = qw.QTangoSizes()
		self.frame_sizes.readAttributeWidth = 300
		self.frame_sizes.writeAttributeWidth = 150
		self.frame_sizes.fontStretch= 80
		self.frame_sizes.fontType = 'Segoe UI'
#		self.frame_sizes.fontType = 'Trebuchet MS'
		self.attr_sizes = qw.QTangoSizes()
		self.attr_sizes.barHeight = 20
		self.attr_sizes.barWidth = 60
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
		
		self.title = qw.QTangoTitleBar('Delaystage')
		self.sidebar = qw.QTangoSideBar(colors = self.colors, sizes = self.frame_sizes)
		self.bottombar = qw.QTangoHorizontalBar()
		
		self.delayName = qw.QTangoDeviceNameStatus(colors = self.colors, sizes = self.frame_sizes)
		self.delayName.setAttributeName('Delaystage')
		self.stopCommands = qw.QTangoCommandSelection('Commands', colors = self.colors, sizes = self.attr_sizes)
		self.stopCommands.addCmdButton('Home', self.homeMotor)
		self.stopCommands.addCmdButton('Stop', self.stopMotor)
				
		self.positionWidget = qw.QTangoWriteAttributeSlider(colors = self.colors, sizes = self.attr_sizes)
#		self.positionWidget.setAttributeName('Position', unichr(176))
		self.positionWidget.setAttributeName('Position', 'deg')
		self.positionWidget.setAttributeWarningLimits([0, 720])
		self.positionWidget.setSliderLimits(0, 720)
		self.positionWidget.writeValueSpinbox.editingFinished.connect(self.writePosition)

		self.limit0Widget = qw.QTangoReadAttributeBoolean(colors = self.colors, sizes = self.attr_sizes)
		self.limit0Widget.setAttributeName('Limit 0')
		self.limit1Widget = qw.QTangoReadAttributeBoolean(colors = self.colors, sizes = self.attr_sizes)
		self.limit1Widget.setAttributeName('Limit 1')
		
				
		layout2.addWidget(self.title)		
		layout2.addLayout(layoutData)
		layoutData.addLayout(self.layout_attributes)
		layoutData.addSpacerItem(spacerItemH)
						
		self.layout_attributes.addWidget(self.delayName)
		self.layout_attributes.addWidget(self.stopCommands)
		self.layout_attributes.addSpacerItem(spacerItemV)
		self.layout_attributes.addWidget(self.limit0Widget)
		self.layout_attributes.addWidget(self.limit1Widget)
		self.layout_attributes.addWidget(self.positionWidget)
		
		
		layout1.addWidget(self.sidebar)
		layout1.addLayout(layout2)
		layout0.addLayout(layout1)
		layout0.addWidget(self.bottombar)
		
#		self.resize(500,800)
		self.setGeometry(200,100,400,300)
		
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