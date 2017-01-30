# -*- coding:utf-8 -*-
"""
Created on 17 okt 2013

@author: Filip
"""
from PyQt4 import QtGui, QtCore
import numpy as np
import time 
import sys
import QTangoWidgets.QTangoWidgets as qw
import pyqtgraph as pg
import PyTango as pt
import threading
import multiprocessing as mp 
import Queue
from SmallTrend import SmallTrend

class DeviceEvent:
	def __init__(self, eventType, data = None):
		self.eventType = eventType
		self.data = data
		
class ClientCommand:
	def __init__(self, command, data = None):
		self.command = command
		self.data = data
		
class DeviceAttribute:
	def __init__(self, name, value = None):
		self.name = name
		self.value = value
		self.w_value = None
		self.quality = 'ATTR_INVALID'
		self.timestamp = None

class DeviceConnectionProcess(mp.Process):
	class RegAttribute(object):
		def __init__(self, name, interval = 1):
			self.name = name
			self.interval = interval
			self.lastCheck = time.time()
			
	def __init__(self, deviceName, deviceEventQueue, clientCommandQueue):
		mp.Process.__init__(self)
		self.stateCheckPeriod = 1.0
		self.registeredAttributes = {}
		self.attributeTypes = [pt._PyTango.CmdArgType.DevState]
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
				self.deviceEventQueue.put(DeviceEvent('info',''.join((self.deviceName, ' terminating'))))
			elif cmd.command == 'getState':
				self.deviceEventQueue.put(DeviceEvent('state',self.state))
			elif cmd.command == 'registerAttribute':
				# Register new attribute for polling
				# cmd.data is tuple where first argument is name of the attribute,
				# second argument is the polling interval
				self.registeredAttributes[cmd.data[0]] = self.RegAttribute(cmd.data[0], cmd.data[1])
			elif cmd.command == 'unregisterAttribute':
				# Unregister attribute for polling
				# cmd.data is name of the attribute,
				try:
					self.registeredAttributes.pop(cmd.data)
				except KeyError:
					# Probably there was no attribute with that name registered
					self.deviceEventQueue.put(DeviceEvent('error','Attribute not registered'))
				
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
		lastStateCheck = time.time()		
		while self.state == 'connected':
			cmd = self.checkCommands()
			if cmd.command == 'getAttribute':
				try:
					attr = self.device.read_attribute(cmd.data)
					devAttr = DeviceAttribute(attr.name)
					devAttr.value = attr.value
					devAttr.w_value = attr.w_value
					devAttr.quality = attr.quality
					devAttr.timestamp = attr.time.totime()
					self.deviceEventQueue.put(DeviceEvent('attribute',devAttr))
				except Exception, e:
					self.deviceEventQueue.put(DeviceEvent('error',e))
			elif cmd.command == 'setAttribute':
				try:
					self.device.write_attribute(cmd.data.name, cmd.data.value)
				except Exception, e:
					self.deviceEventQueue.put(DeviceEvent('error',e))
					
			# Periodically check if the connection to the device server is alive and registered attributes
			checkTime = time.time()
			if checkTime - lastStateCheck > self.stateCheckPeriod:
				lastStateCheck = checkTime
				try:
					self.device.ping()
				except Exception, e:
					if e[0].reason == 'API_DeviceNotExported':
						self.state = 'proxy'
					if e[0].reason == 'API_DeviceNotDefined':
						self.state = 'disconnected'
			for regAttr in self.registeredAttributes.itervalues():
				if checkTime - regAttr.lastCheck > regAttr.interval:
					regAttr.lastCheck = checkTime
					try:
						attr = self.device.read_attribute(regAttr.name)
						devAttr = DeviceAttribute(attr.name)
						# Some data types can't be pickled. We need to 
						# transform them into a string that can be pickled
						if attr.type in self.attributeTypes:
							devAttr.value = str(attr.value)
							devAttr.w_value = str(attr.w_value)
						else:
							devAttr.value = attr.value
							devAttr.w_value = attr.w_value
						devAttr.quality = attr.quality
						devAttr.timestamp = attr.time.totime()
						self.deviceEventQueue.put(DeviceEvent('regAttribute',devAttr))
					except Exception, e:
						self.deviceEventQueue.put(DeviceEvent('error',e))
					
			time.sleep(0.05) 
	

class DeviceProcessHandler:
	def __init__(self, name):
		self.name = name
		self.state = 'disconnected'
		self.eventQueue = mp.Queue(100)
		self.commandQueue = mp.Queue(100)
		self.process = DeviceConnectionProcess(self.name, self.eventQueue, self.commandQueue)
		
		self.attributeSlots = {}
		
	def addAttributeSlot(self, attributeName, slot, timeInterval):
		cmd = ClientCommand('registerAttribute',(attributeName, timeInterval))
		print cmd.command, cmd.data
		self.commandQueue.put(cmd)
		self.attributeSlots[str.lower(attributeName)] = slot
		
	def handleEvent(self):
		while self.eventQueue.empty() == False:
			ev = self.eventQueue.get(block = False)
			if ev.eventType == 'regAttribute':
				try:
					self.attributeSlots[str.lower(ev.data.name)](ev.data)
					return ev
				except KeyError:
					return ev
			elif ev.eventType == 'attribute':
				return ev
			elif ev.eventType == 'state':
				self.state = ev.data
				return ev
			else:
				print ev.eventType, ev.data
				return ev
		
	def sendCommand(self, cmd):
		self.commandQueue.put(cmd)
				
	def terminate(self):
		self.commandQueue.put(ClientCommand(command = 'terminate'))
		while self.eventQueue.empty() == False:
			ev = self.eventQueue.get(block = False)
		
	def startProcess(self):
		self.process.start()


# noinspection PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit
class TangoDeviceClientTest(QtGui.QWidget):
	def __init__(self, parent = None):
		QtGui.QWidget.__init__(self,parent)
#		self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
		self.timeVector = None
		self.xData = None
		
		self.devices = {}
		self.devices['finesse']=DeviceProcessHandler('testfel/seedlaser/finesse')
		self.devices['spectrometer']=DeviceProcessHandler('testfel/seedlaser/spectrometer_osc')
		self.devices['leelaser']=DeviceProcessHandler('testfel/seedlaser/leelaser_mp')
		
		self.setupLayout()
		
		self.timer = QtCore.QTimer(self)
		self.timer.timeout.connect(self.checkDevices)
		self.timer.start(100)
		
		for device in self.devices.itervalues():
			device.startProcess()
		
		
	def checkDevices(self):
		for device in self.devices:
			devEvent=self.devices[device].handleEvent()
			if devEvent != None:
				if devEvent.eventType == 'state':
					if device == 'finesse':
						if self.devices[device].state != 'connected':
							self.laserPowerWidget.setDisabled(True)
							self.laserTempWidget.setDisabled(True)
							self.finesseName.setDisabled(True)
							self.finesseName.setState(pt.DevState.UNKNOWN)
						else:
							self.devices['finesse'].addAttributeSlot('laserTemperature', self.readLaserTemperature, 1)
							self.devices['finesse'].addAttributeSlot('Power', self.readLaserPower, 0.5)
							self.devices['finesse'].addAttributeSlot('State', self.readFinesseState, 0.5)
							
							self.laserPowerWidget.setDisabled(False)
							self.laserTempWidget.setDisabled(False)
							self.finesseName.setDisabled(False)
					elif device == 'spectrometer':
						if self.devices[device].state != 'connected':
							self.spectrometerName.setDisabled(True)
							self.spectrometerName.setState(pt.DevState.UNKNOWN)
						else:
							self.devices['spectrometer'].addAttributeSlot('PeakEnergy', self.readPeakEnergy, 0.3)
							self.devices['spectrometer'].addAttributeSlot('Spectrum', self.readSpectrum, 0.3)
							self.devices['spectrometer'].addAttributeSlot('State', self.readSpectrometerState, 0.5)
							
							self.devices['spectrometer'].sendCommand(ClientCommand('getAttribute','Wavelengths'))
							self.spectrometerName.setDisabled(False)
					elif device == 'leelaser':
						if self.devices[device].state != 'connected':
							self.leelaserName.setDisabled(True)
							self.leelaserName.setState(pt.DevState.UNKNOWN)
						else:
							self.devices['leelaser'].addAttributeSlot('State', self.readLeelaserState, 0.5)

							self.leelaserName.setDisabled(False)

				elif devEvent.eventType == 'attribute':
					if device == 'spectrometer':
						self.timeVector = devEvent.data.value
				elif devEvent.eventType == 'error':
					print device, ' error ', str(devEvent.data)
					
	
	def readLaserTemperature(self, data):
		self.laserTempWidget.setAttributeValue(data.value)

	def readLaserPower(self, data):
		self.laserPowerWidget.setAttributeValue(data.value)
		
	def readFinesseState(self, data):
		self.finesseName.setState(data.value)

	def readSpectrometerState(self, data):
		self.spectrometerName.setState(data.value)

	def readLeelaserState(self, data):
		self.leelaserName.setState(data.value)

	def readPeakEnergy(self, data):
		self.peakEnergyWidget.setAttributeValue(data.value)
#		self.laserEnergyTrend.updateData(time.time(), data.value)
#		oldData = self.laserEnergyTrendCurve.getData()
		if self.xData == None:
			self.xData = np.array([time.time()])
			yData = np.array([data.value])
		else:
			self.xData = np.append(self.xData, time.time())
			yData = np.append(self.laserEnergyTrendCurve.yData, data.value)
			if yData.shape[0] > 100000:
				yData = yData[-90000:]
				self.xData = self.xData[-90000:]
		self.laserEnergyTrendCurve.setData(self.xData-self.xData[-1], yData, antialias = True)
		
	def readSpectrum(self, data):
		if self.timeVector == None:
			self.oscSpectrumCurve.setData(data.value)
		else:
			self.oscSpectrumCurve.setData(y = data.value, x = self.timeVector, antialias = True)
		self.oscSpectrumPlot.update()

	def setupAttributeLayout(self, attributeList = []):
		self.attributeQObjects = []
		for att in attributeList:
			attQObject = qw.QTangoReadAttributeDouble()
			attQObject.setAttributeName(att.name)
			self.attributeQObjects.append(attQObject)
			self.layout_attributes.addWidget(attQObject)
			
	def closeEvent(self, event):
		for device in self.devices.itervalues():
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
		
		self.title = qw.QTangoTitleBar('Oscillator')
		self.sidebar = qw.QTangoSideBar()
		self.bottombar = qw.QTangoHorizontalBar()
		self.finesseName = qw.QTangoDeviceNameStatus()
		self.finesseName.setAttributeName('Finesse')
		self.spectrometerName = qw.QTangoDeviceNameStatus()
		self.spectrometerName.setAttributeName('Spectrometer')
		self.leelaserName = qw.QTangoDeviceNameStatus()
		self.leelaserName.setAttributeName('MP LeeLaser')
		self.laserTempWidget = qw.QTangoReadAttributeDouble()
		self.laserTempWidget.setAttributeName('Laser temperature')
		self.laserPowerWidget = qw.QTangoReadAttributeDouble()
		self.laserPowerWidget.setAttributeName('Laser power')
		self.peakEnergyWidget = qw.QTangoReadAttributeDouble()
		self.peakEnergyWidget.setAttributeName('Peak energy')
# 		self.laserEnergyTrend = SmallTrend()
# 		self.laserEnergyTrend.ySpan = 0.6
# 		self.laserEnergyTrend.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.MinimumExpanding)
		
		self.laserEnergyTrend = pg.PlotWidget(name = 'oscEnergyTrend')
		self.laserEnergyTrend.setXRange(-600, 0)
		self.laserEnergyTrend.setMaximumHeight(90)
		self.laserEnergyTrend.setMaximumWidth(300)
		self.laserEnergyTrendCurve = self.laserEnergyTrend.plot()
		self.laserEnergyTrendCurve.setPen('#66cbff')

		self.oscSpectrumPlot = pg.PlotWidget(name = 'oscSpectrum')
		self.oscSpectrumPlot.setXRange(700, 900)
		self.oscSpectrumCurve = self.oscSpectrumPlot.plot()
		self.oscSpectrumCurve.setPen('#66cbff')
		
		layout2.addWidget(self.title)		
		layout2.addLayout(layoutData)
		layoutData.addLayout(self.layout_attributes)
		layoutData.addWidget(self.oscSpectrumPlot)
#		layoutData.addSpacerItem(spacerItemH)
						
		self.layout_attributes.addWidget(self.finesseName)
		self.layout_attributes.addWidget(self.leelaserName)
		self.layout_attributes.addWidget(self.spectrometerName)
		self.layout_attributes.addSpacerItem(spacerItemV)		
		self.layout_attributes.addWidget(self.laserTempWidget)
		self.layout_attributes.addWidget(self.laserPowerWidget)
		self.layout_attributes.addWidget(self.peakEnergyWidget)
		self.layout_attributes.addWidget(self.laserEnergyTrend)
		
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