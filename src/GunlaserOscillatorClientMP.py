# -*- coding:utf-8 -*-
"""
Created on 24 okt 2013

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
				self.deviceEventQueue.close()
				self.deviceEventQueue.join_thread()
				break
			else:
				stateHandler = self.stateHandlerDict[self.state]
				stateHandler()
		
	def checkCommands(self):
		try:
			cmd = self.clientCommandQueue.get(block=False)
			self.deviceEventQueue.put(DeviceEvent('info',''.join((cmd.command, ' ', str(cmd.data)))))
			if cmd.command == 'terminate':
				self.state = 'terminate'
				self.deviceEventQueue.put(DeviceEvent('info',''.join((self.deviceName, ' terminating'))))
				while self.clientCommandQueue.empty() == False:
					self.clientCommandQueue.get(block=False)
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
					self.deviceEventQueue.put(DeviceEvent('error',str(e)))
			elif cmd.command == 'setAttribute':
				# First element in data is the attribute name, second is the new value
				try:
					self.device.write_attribute(cmd.data[0], cmd.data[1])
				except Exception, e:
					self.deviceEventQueue.put(DeviceEvent('error',str(e)))
			elif cmd.command == 'tangoCommand':
				try:
					self.device.command_inout(cmd.data)
				except Exception, e:
					self.deviceEventQueue.put(DeviceEvent('error',str(e)))
					
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
						self.deviceEventQueue.put(DeviceEvent('error',str(e)))
					
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
#			print ev.eventType, ev.data
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
				print self.state
				return ev
			else:
				print ev.eventType, ev.data
				return ev
		
	def sendCommand(self, cmd):
		self.commandQueue.put(cmd)
				
	def terminate(self):
		print self.name, ' terminating'
		self.commandQueue.put(ClientCommand(command = 'terminate'))
		self.process.terminate()
# 		time.sleep(0.5)
# 		while self.eventQueue.empty() == False:
# 			ev = self.eventQueue.get(block = False)
# 			print self.name, ':', ev.eventType, ev.data
# 		self.process.join(0.25)
# 		if self.process.is_alive() == True:
# 			print self.name, ': Force terminate'
# 			self.process.terminate()
		
	def startProcess(self):
		self.process.start()

class TangoDeviceClientTest(QtGui.QWidget):
	def __init__(self, parent = None):
		QtGui.QWidget.__init__(self,parent)
#		self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
		self.timeVector = None
		self.xData = None
		self.xDataTemp = None
		
		self.devices = {}
		self.devices['finesse']=DeviceProcessHandler('testfel/gunlaser/finesse')
		self.devices['spectrometer']=DeviceProcessHandler('testfel/gunlaser/osc_spectrometer')
		
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
							self.devices['finesse'].addAttributeSlot('ShutterState', self.readShutterState, 0.5)
							self.devices['finesse'].addAttributeSlot('LaserOperationState', self.readLaserOperationState, 0.5)
							
							self.laserPowerWidget.setDisabled(False)
							self.laserTempWidget.setDisabled(False)
							self.finesseName.setDisabled(False)
					elif device == 'spectrometer':
						if self.devices[device].state != 'connected':
							self.spectrometerName.setDisabled(True)
							self.spectrometerName.setState(pt.DevState.UNKNOWN)
						else:
							self.devices['spectrometer'].addAttributeSlot('PeakEnergy', self.readPeakEnergy, 0.3)
							self.devices['spectrometer'].addAttributeSlot('SpectrumWidth', self.readPeakWidth, 0.3)
							self.devices['spectrometer'].addAttributeSlot('Spectrum', self.readSpectrum, 0.3)
							self.devices['spectrometer'].addAttributeSlot('State', self.readSpectrometerState, 0.5)
							
							self.devices['spectrometer'].sendCommand(ClientCommand('getAttribute','Wavelengths'))
							self.spectrometerName.setDisabled(False)

				elif devEvent.eventType == 'attribute':
					if device == 'spectrometer':
						self.timeVector = devEvent.data.value
				elif devEvent.eventType == 'error':
					print device, ' error ', str(devEvent.data)
					
	
	def readLaserTemperature(self, data):
		self.laserTempWidget.setAttributeValue(data.value)
# 		if self.xDataTemp == None:
# 			self.xDataTemp = np.array([time.time()])
# 			yData = np.array([data.value])
# 		else:
# 			self.xDataTemp = np.append(self.xDataTemp, time.time())
# 			yData = np.append(self.laserTempTrendCurve.yData, data.value)
# 			if yData.shape[0] > 100000:
# 				yData = yData[-90000:]
# 				self.xDataTemp = self.xDataTemp[-90000:]
# 		self.laserTempTrendCurve.setData(self.xDataTemp-self.xDataTemp[-1], yData, antialias = True)
		self.laserTempWidget2.setAttributeValue(data.value)


	def readLaserPower(self, data):
		self.laserPowerWidget.setAttributeValue(data.value)
		
	def writeLaserPower(self):
		power = self.laserPowerWidget.writeValueSpinbox.value()
		data = ['Power', power]
#		self.devices['finesse'].sendCommand(ClientCommand('setAttribute', data))
		print 'Power: ', power
		
	def readFinesseState(self, data):
		self.finesseName.setState(data.value)

	def readShutterState(self, data):
		self.shutterWidget.setStatus(data.value)

	def readLaserOperationState(self, data):
		self.laserOperationWidget.setStatus(data.value)


	def readSpectrometerState(self, data):
		self.spectrometerName.setState(data.value)


	def readPeakEnergy(self, data):
		self.peakEnergyWidget.setAttributeValue(data.value)
#		self.laserEnergyTrend.updateData(time.time(), data.value)
#		oldData = self.laserEnergyTrendCurve.getData()
# 		if self.xData == None:
# 			self.xData = np.array([time.time()])
# 			yData = np.array([data.value])
# 		else:
# 			self.xData = np.append(self.xData, time.time())
# 			yData = np.append(self.laserEnergyTrendCurve.yData, data.value)
# 			if yData.shape[0] > 100000:
# 				yData = yData[-90000:]
# 				self.xData = self.xData[-90000:]
# 		self.laserEnergyTrendCurve.setData(self.xData-self.xData[-1], yData, antialias = True)
		
	def readPeakWidth(self, data):
		self.peakWidthWidget.setAttributeValue(data.value)
		
	def readSpectrum(self, data):
# 		if self.timeVector == None:
# 			self.oscSpectrumCurve.setData(data.value)
# 		else:
# 			self.oscSpectrumCurve.setData(y = data.value, x = self.timeVector, antialias = True)
# 		self.oscSpectrumPlot.update()
		pass
		
	def onFinesse(self):
		self.devices['finesse'].sendCommand(ClientCommand('tangoCommand','On'))
		
	def offFinesse(self):
		self.devices['finesse'].sendCommand(ClientCommand('tangoCommand','Off'))
		
	def openFinesseShutter(self):
		self.devices['finesse'].sendCommand(ClientCommand('tangoCommand','Open'))

	def closeFinesseShutter(self):
		self.devices['finesse'].sendCommand(ClientCommand('tangoCommand','Close'))

	def testOpenShutter(self):
		print 'Open shutter!'

	def testCloseShutter(self):
		print 'Close shutter!'


	def setupAttributeLayout(self, attributeList = []):
		self.attributeQObjects = []
		for att in attributeList:
			attQObject = qw.QTangoReadAttributeDouble()
			attQObject.setAttributeName(att.name)
			self.attributeQObjects.append(attQObject)
			self.layoutAttributes.addWidget(attQObject)
			
	def closeEvent(self, event):
		for device in self.devices.itervalues():
			device.terminate()
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
		layoutData.setMargin(3)
		layoutData.setSpacing(0)
		self.layoutAttributes = QtGui.QVBoxLayout()
		self.layoutAttributes.setMargin(0)
		self.layoutAttributes.setSpacing(self.attrSizes.barHeight/2)
		self.layoutAttributes.setContentsMargins(0, 0, 0, 0)
		
		self.title = qw.QTangoTitleBar('Gunlaser oscillator')
		self.sidebar = qw.QTangoSideBar(colors = self.colors, sizes = self.frameSizes)
# 		self.sidebar.addCmdButton('On', self.onFinesse)
# 		self.sidebar.addCmdButton('Off', self.offFinesse)
# 		self.sidebar.addCmdButton('Open', self.openFinesseShutter)
# 		self.sidebar.addCmdButton('Close', self.closeFinesseShutter)
		self.bottombar = qw.QTangoHorizontalBar()
		self.finesseName = qw.QTangoDeviceNameStatus(colors = self.colors, sizes = self.frameSizes)
		self.finesseName.setAttributeName('Finesse')
		self.spectrometerName = qw.QTangoDeviceNameStatus(colors = self.colors, sizes = self.frameSizes)
		self.spectrometerName.setAttributeName('Spectrometer')
				
		self.shutterWidget = qw.QTangoCommandSelection('Shutter', colors = self.colors, sizes = self.attrSizes)
		self.shutterWidget.addCmdButton('Open', self.openFinesseShutter)
		self.shutterWidget.addCmdButton('Close', self.closeFinesseShutter)

		self.laserOperationWidget = qw.QTangoCommandSelection('Laser', colors = self.colors, sizes = self.attrSizes)
		self.laserOperationWidget.addCmdButton('Start', self.onFinesse)
		self.laserOperationWidget.addCmdButton('Stop', self.offFinesse)

		
# 		self.laserTempWidget = qw.QTangoReadAttributeDouble(colors = self.colors, sizes = self.attrSizes)
# 		self.laserTempWidget.setAttributeName('Laser temperature')
		self.laserTempWidget = qw.QTangoReadAttributeSlider(colors = self.colors, sizes = self.attrSizes)
		self.laserTempWidget.setAttributeName('Laser temperature')
		self.laserTempWidget.setAttributeWarningLimits(25, 26)
		self.laserTempWidget.setSliderLimits(23, 27)

		self.laserTempWidget2 = qw.QTangoReadAttributeTrend(colors = self.colors, sizes = self.attrSizes)
		self.laserTempWidget2.setAttributeName('Laser temperature')
		self.laserTempWidget2.setAttributeWarningLimits(25, 26)
		self.laserTempWidget2.setTrendLimits(23, 27)


#		self.laserPowerWidget = qw.QTangoWriteAttributeDouble(colors = self.colors, sizes = self.attrSizes)
		self.laserPowerWidget = qw.QTangoWriteAttributeSlider(colors = self.colors, sizes = self.attrSizes)
		self.laserPowerWidget.setAttributeName('Laser power')
		self.laserPowerWidget.setSliderLimits(0, 6)
		self.laserPowerWidget.setAttributeWarningLimits(4, 5.5)
		self.laserPowerWidget.setAttributeWriteValue(5)
		self.peakWidthWidget = qw.QTangoReadAttributeSlider(colors = self.colors, sizes = self.attrSizes)
		self.peakWidthWidget.setAttributeName('Peak width')
		self.peakWidthWidget.setAttributeWarningLimits(7, 20)
		self.peakWidthWidget.setSliderLimits(0, 15)
		self.peakEnergyWidget = qw.QTangoReadAttributeSlider(colors = self.colors, sizes = self.attrSizes)
		self.peakEnergyWidget.setAttributeName('Peak energy')
		self.peakEnergyWidget.setAttributeWarningLimits(0.02, 1)
		self.peakEnergyWidget.setSliderLimits(0, 0.04)
		

# 		self.laserTempTrend = pg.PlotWidget(name = 'oscTempTrend')
# 		self.laserTempTrend.setXRange(-600, 0)
# 		self.laserTempTrend.setMaximumHeight(90)
# 		self.laserTempTrend.setMaximumWidth(300)
# 		self.laserTempTrendCurve = self.laserTempTrend.plot()
# 		self.laserTempTrendCurve.setPen('#66cbff', width = 1.5)
# 		
# 		self.laserEnergyTrend = pg.PlotWidget(name = 'oscEnergyTrend')
# 		self.laserEnergyTrend.setXRange(-600, 0)
# 		self.laserEnergyTrend.setMaximumHeight(90)
# 		self.laserEnergyTrend.setMaximumWidth(300)
# 		self.laserEnergyTrendCurve = self.laserEnergyTrend.plot()
# 		self.laserEnergyTrendCurve.setPen('#66cbff', width = 1.5)

# 		self.oscSpectrumPlot = pg.PlotWidget(name = 'oscSpectrum')
# 		self.oscSpectrumPlot.setXRange(760, 820)
# 		self.oscSpectrumCurve = self.oscSpectrumPlot.plot()
# 		self.oscSpectrumCurve.setPen('#66cbff', width = 1.5)
				
		self.laserPowerWidget.writeValueSpinbox.editingFinished.connect(self.writeLaserPower)
		
		layout2.addWidget(self.title)		
		layout2.addLayout(layoutData)
		layoutData.addLayout(self.layoutAttributes)
#		layoutData.addWidget(self.oscSpectrumPlot)
#		layoutData.addSpacerItem(spacerItemH)
						
		self.layoutAttributes.addWidget(self.finesseName)
		self.layoutAttributes.addWidget(self.spectrometerName)
		self.layoutAttributes.addSpacerItem(spacerItemV)
		self.layoutAttributes.addWidget(self.shutterWidget)
		self.layoutAttributes.addWidget(self.laserOperationWidget)		
		self.layoutAttributes.addWidget(self.laserTempWidget)
		self.layoutAttributes.addWidget(self.laserTempWidget2)
#		self.layoutAttributes.addWidget(self.laserTempTrend)
		self.layoutAttributes.addWidget(self.laserPowerWidget)
		self.layoutAttributes.addWidget(self.peakWidthWidget)
		self.layoutAttributes.addWidget(self.peakEnergyWidget)
#		self.layoutAttributes.addWidget(self.laserEnergyTrend)
		
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