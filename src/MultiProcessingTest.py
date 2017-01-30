# -*- coding:utf-8 -*-
"""
Created on Mar 25, 2013

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
import Queue

class DeviceEvent:
	def __init__(self, eventType, data = None):
		self.eventType = eventType
		self.data = data
		
class ClientCommand:
	def __init__(self, command, data = None):
		self.command = command
		self.data = data

class DeviceConnectionProcess(mp.Process):
	def __init__(self, deviceName, deviceEventQueue, clientCommandQueue):
		mp.Process.__init__(self)
		self.stateCheckPeriod = 1.0
		self.deviceName = deviceName
		self.device = None
		self.deviceEventQueue = deviceEventQueue
		self.clientCommandQueue = clientCommandQueue
		
		self.stateHandlerDict = {'disconnected': self.disconnectedState,
								'proxy': self.proxyState,
								'connected': self.connectedState,}
		
		self.state = 'disconnected'
	
	def run(self):
		self.deviceEventQueue.put(DeviceEvent('info',''.join(('Starting process ',self.deviceName))))
		while 1:
			if self.state == 'terminate':
				self.deviceEventQueue.put(DeviceEvent('state','terminate'))
				break
			else:
				stateHandler = self.stateHandlerDict[self.state]
				stateHandler()
		
	def checkCommands(self):
		try:
			cmd = self.clientCommandQueue.get(block=False)
			if cmd.command == 'terminate':
				self.state = 'terminate'
			elif cmd.command == 'getState':
				self.deviceEventQueue.put(DeviceEvent('state',self.state))
			return cmd
		except Queue.Empty:
			return ClientCommand('')
		
	def disconnectedState(self):
		self.deviceEventQueue.put(DeviceEvent('state','disconnected'))
		while self.state == 'disconnected':
			cmd = self.checkCommands()
			try:
				self.device = pt.DeviceProxy(self.deviceName)
				self.state = 'proxy'
				break
			except Exception, e:
				self.state = 'disconnected'
			time.sleep(0.5)
	
	def proxyState(self):
		self.deviceEventQueue.put(DeviceEvent('state','disconnected'))
		while self.state == 'proxy':
			cmd = self.checkCommands()
			try:
				self.device.ping()
				self.state = 'connected'
				break
			except Exception, e:
				if e[0].reason == 'API_DeviceNotExported':
					self.state = 'proxy'
				if e[0].reason == 'API_DeviceNotDefined':
					self.state = 'disconnected'
					break
			time.sleep(0.5)
				
	def connectedState(self):
		self.deviceEventQueue.put(DeviceEvent('state','connected'))
		lastStateCheck = time.clock()		
		while self.state == 'connected':
			cmd = self.checkCommands()
			if cmd.command == 'getAttribute':
				try:
					attr = self.device.read_attribute(cmd.data)
					self.deviceEventQueue.put(DeviceEvent('attribute',attr))
				except Exception, e:
					self.deviceEventQueue.put(DeviceEvent('error',e))
			elif cmd.command == 'setAttribute':
				try:
					self.device.write_attribute(cmd.data.name, cmd.data.value)
				except Exception, e:
					self.deviceEventQueue.put(DeviceEvent('error',e))
			tmpStateCheckTime = time.clock()
			if tmpStateCheckTime - lastStateCheck > self.stateCheckPeriod:
				try:
					self.device.ping()
				except Exception, e:
					if e[0].reason == 'API_DeviceNotExported':
						self.state = 'proxy'
					if e[0].reason == 'API_DeviceNotDefined':
						self.state = 'disconnected'
			time.sleep(0.05) 
	

class DeviceProcessHandler:
	def __init__(self, name):
		self.name = name
		self.eventQueue = mp.Queue(100)
		self.commandQueue = mp.Queue(100)
		self.process = DeviceConnectionProcess(self.name, self.eventQueue, self.commandQueue)
		
		self.attributeSlots = {}
		
	def addAttributeSlot(self, attributeName, slot):
		self.attributeSlots[attributeName] = slot
		
	def handleEvent(self):
		try:
			ev = self.eventQueue.get(block = False)
			if ev.eventType == 'attribute':
				try:
					self.attributeSlots[ev.data.name](ev.data)
					return None
				except KeyError:
					return ev
			else:
				return ev
		except Queue.Empty:
			return None
		
	def sendCommand(self, cmd):
		self.commandQueue.put(ClientCommand(command = cmd))
				
	def terminate(self):
		self.commandQueue.put(ClientCommand(command = 'terminate'))
		
	def startProcess(self):
		self.process.start()


# noinspection PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit
class TangoDeviceClientTest(QtGui.QWidget):
	def __init__(self, parent = None):
		QtGui.QWidget.__init__(self,parent)
#		self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
		self.devices = []
		self.devices.append(DeviceProcessHandler('testfel/beamline/m1h'))
		self.devices.append(DeviceProcessHandler('testfel/beamline/m1v'))
		self.devices.append(DeviceProcessHandler('testfel/beamline/m2h'))
		self.devices.append(DeviceProcessHandler('testfel/beamline/m2v'))
		
		self.setupLayout()
		
		
		self.timer = QtCore.QTimer(self)
		self.timer.timeout.connect(self.checkDevices)
		self.timer.start(100)
		
		for device in self.devices:
			device.startProcess()
		
		
	def checkDevices(self):
		for device in self.devices:
			devEvent=device.handleEvent()
			if devEvent != None:
				if devEvent.eventType == 'state':
					if devEvent.data == 'connected':
						self.deviceStatus.setStatus(pt.DevState.ON,'Device connected')
					else:
						self.deviceStatus.setStatus(pt.DevState.UNKNOWN,'Device disconnected')

		
		
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
			
	def closeEvent(self, event):
		for device in self.devices:
			device.terminate()
		event.accept()
		
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
		
		self.title = qw.QTangoTitleBar('Thorlabs motors')
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
	myapp = TangoDeviceClientTest()
	myapp.show()
	sys.exit(app.exec_())	
