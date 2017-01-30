# -*- coding:utf-8 -*-
"""
Created on Feb 13, 2013

@author: Filip
"""
from PyQt4 import QtGui, QtCore
import numpy as np
import time 
import sys
import QTangoWidgets.QTangoWidgets as qw
import PyTango as pt
import threading
import multiprocessing as mp 

class LabelFontTest(QtGui.QWidget):
	def __init__(self, parent = None):
		QtGui.QWidget.__init__(self,parent)

		s='QWidget{background-color: #000000; }'
		self.setStyleSheet(s)
		
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
		layoutData.setMargin(3)
		layoutData.setSpacing(0)
		layoutAttributes = QtGui.QVBoxLayout()
		layoutAttributes.setMargin(0)
		layoutAttributes.setSpacing(0)
		layoutAttributes.setContentsMargins(0, 0, 0, 0)
		
		self.title = qw.QTangoTitleBar('GUNLASER')
		self.sidebar = qw.QTangoSideBar('Test')
		self.bottombar = qw.QTangoHorizontalBar()
		self.attributes = [qw.QTangoReadAttributeDouble(), qw.QTangoReadAttributeDouble(), qw.QTangoReadAttributeDouble()]
		self.attributes[0].setAttributeName('Temperature')
		self.attributes[1].setAttributeName('Power')
		self.attributes[2].setAttributeName('Current')
		self.deviceStatus = qw.QTangoDeviceStatus()
		layout2.addWidget(self.title)
		layout2.addSpacerItem(spacerItemV)
		layout2.addLayout(layoutData)
		layoutData.addLayout(layoutAttributes)
		layoutData.addSpacerItem(spacerItemH)
		layoutAttributes.addWidget(self.deviceStatus)
		self.deviceStatus.setStatus(pt.DevState.ON,'System ok. \nLaser on, shutter open\nTemp ok')
		for aw in self.attributes:
			layoutAttributes.addWidget(aw)
		layout1.addWidget(self.sidebar)
		layout1.addLayout(layout2)
		layout0.addLayout(layout1)
		layout0.addWidget(self.bottombar)

class TangoWorker(QtCore.QObject):
	def __init__(self, parent = None):
		QtCore.QObject.__init__(self,parent)
		
	def getAttributeList(self, device):
		print 'Time in getAttributeList:'
		t0=time.clock()
		attList = device.get_attribute_list()
		print time.clock()-t0
		
		return attList


# noinspection PyAttributeOutsideInit
class DeviceConnectionThread(QtCore.QThread):
	deviceReadySignal = QtCore.pyqtSignal(object)
	attributeListReadySignal = QtCore.pyqtSignal(object)
		
	def __init__(self, parent = None, deviceName = ''):
		QtCore.QThread.__init__(self,parent)
		self.stopThread = False
#		self.receiver = parent
		self.deviceName = deviceName
		self.device = None
		self.attributeList = []		
		
		
	def run(self):
		print 'DevCon run'
		print self.deviceName
		self.device = pt.DeviceProxy(self.deviceName)
		self.worker = TangoWorker(parent = None)
		self.deviceReadySignal.emit(self.device)
		t0=time.clock()
		attList = self.worker.getAttributeList(self.device)
		print time.clock()-t0
		print attList
		for attName in attList:
			self.attributeList.append(self.device.get_attribute_config(attName))
		print 'Attributes ready'
		time.sleep(2)
		self.attributeListReadySignal.emit(self.attributeList)
		print 'Signal emitted'
	
class TangoPyWorker():
	def __init__(self, parent = None):
		pass
		
	def getAttributeList(self, device):
		print 'Time in getAttributeList:'
		t0=time.clock()
		attList = device.get_attribute_list()
		print time.clock()-t0
		
		return attList
		
class DeviceConnectionPyThread(threading.Thread):
	def __init__(self, parent = None, deviceName = ''):
		threading.Thread.__init__(self)
		self.stopThread = False
#		self.receiver = parent
		self.deviceName = deviceName
		self.device = None
		self.attributeList = []		
		
		
	def run(self):
		print 'DevCon run'
		print self.deviceName
		self.device = pt.DeviceProxy(self.deviceName)
#		self.worker = TangoPyWorker(parent = None)
		t0=time.clock()
#		attList = self.worker.getAttributeList(self.device)
		print time.clock()-t0
#		print attList
#		for attName in attList:
#			self.attributeList.append(self.device.get_attribute_config(attName))
		print 'Attributes ready'
		time.sleep(2)
#		self.attributeListReadySignal.emit(self.attributeList)
		print 'Signal emitted'


# noinspection PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit
class TangoDeviceClientTest(QtGui.QWidget):
	def __init__(self, parent = None):
		QtGui.QWidget.__init__(self,parent)
#		self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
		self.deviceName = 'testfel/gunlaser/finesse'
		self.setupLayout()
		
#		self.connectDeviceThread = DeviceConnectionThread(None, self.deviceName)
#		self.connectDeviceThread.deviceReadySignal.connect(self.deviceConnected)
#		self.connectDeviceThread.attributeListReadySignal.connect(self.setupAttributeLayout)
#		self.connectDeviceThread.start()
		
		self.connectDeviceThread = DeviceConnectionPyThread(None, 'testfel/gunlaser/finesse')
		self.connectDeviceThread.start()
		
	def startThread(self):
		self.connectDeviceThread.start()
		
		
	def deviceConnected(self, device=None):
#		self.device = device
		self.deviceStatus.setStatus(pt.DevState.ON,'Device connected')

	def setupAttributeLayout(self, attributeList = []):
		self.attributeQObjects = []
		for att in attributeList:
			attQObject = qw.QTangoReadAttributeDouble()
			attQObject.setAttributeName(att.name)
			self.attributeQObjects.append(attQObject)
			self.layout_attributes.addWidget(attQObject)
			
			
		
	def setupLayout(self):
		s='QWidget{background-color: #000000; }'
		self.setStyleSheet(s)
		
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
		layoutData.setMargin(3)
		layoutData.setSpacing(0)
		self.layout_attributes = QtGui.QVBoxLayout()
		self.layout_attributes.setMargin(0)
		self.layout_attributes.setSpacing(0)
		self.layout_attributes.setContentsMargins(0, 0, 0, 0)
		
		self.title = qw.QTangoTitleBar(self.deviceName.upper())
		self.sidebar = qw.QTangoSideBar('Test')
		self.bottombar = qw.QTangoHorizontalBar()
		self.deviceStatus = qw.QTangoDeviceStatus()
		layout2.addWidget(self.title)
		layout2.addSpacerItem(spacerItemV)
		layout2.addLayout(layoutData)
		layoutData.addLayout(self.layout_attributes)
		layoutData.addSpacerItem(spacerItemH)
		self.layout_attributes.addWidget(self.deviceStatus)
		self.deviceStatus.setStatus(pt.DevState.DISABLE,'Connecting to device')
		layout1.addWidget(self.sidebar)
		layout1.addLayout(layout2)
		layout0.addLayout(layout1)
		layout0.addWidget(self.bottombar)
		
		self.update()
		


if __name__ == '__main__':
	app = QtGui.QApplication(sys.argv)
#	myapp = LabelFontTest()
	myapp = TangoDeviceClientTest()
	myapp.show()
	sys.exit(app.exec_())	
