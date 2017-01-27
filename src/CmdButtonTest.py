# -*- coding:utf-8 -*-
"""
Created on 8 nov 2013

@author: Filip
"""
from PyQt4 import QtGui, QtCore
import numpy as np
import time 
import sys
import QTangoWidgets.QTangoWidgets as qw

class ButtonTest(QtGui.QWidget):
	def __init__(self, parent = None):
		QtGui.QWidget.__init__(self,parent)
		
		self.value = 0.5
		self.lastTime = time.clock()
		
		self.setupLayout()
		
	def buttonFunction(self):
		print 'Button press'
		self.buttonWidget.setStatus('Grr')
		self.buttonWidget.cmdButtons['Change'].setText('Apa ')
		self.buttonWidget.statusLabel.update()
		self.buttonWidget.layoutInfo.update()
		self.update()
		
	def timerFunction(self):
		
		newValue = (np.sin(time.clock()-self.lastTime)+1)/2+np.random.rand()*0.1
		self.sliderWidget.setAttributeValue(newValue)
	
	def setupLayout(self):
		s='QWidget{background-color: #000000; }'
		self.setStyleSheet(s)
		
		self.attr_sizes = qw.QTangoSizes()
		self.attr_sizes.barHeight = 18
		self.attr_sizes.barWidth = 42
		self.attr_sizes.readAttributeWidth = 240
		self.attr_sizes.writeAttributeWidth = 299
		self.attr_sizes.fontStretch= 80
		self.attr_sizes.fontType = 'Segoe UI'
		
		
		self.buttonWidget = qw.QTangoCommandSelection('Test', sizes = self.attr_sizes)
		self.buttonWidget.addCmdButton('Change', self.buttonFunction)
		self.buttonWidget.addCmdButton('B2', self.buttonFunction)
		
#		self.sliderWidget = qw.QTangoHSliderBase()
		self.sliderWidget = qw.QTangoReadAttributeSlider(sizes = self.attr_sizes)
		self.sliderWidget.setAttributeWarningLimits(0.25, 0.9)
		self.sliderWidget.setSliderLimits(0.2, 0.8)
		self.sliderWidget.setAttributeValue(0.9)
		self.sliderWidget.setAttributeName('Temperature')
#		self.sliderWidget.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
				
		self.layout = QtGui.QVBoxLayout(self)
		self.layout.addWidget(self.buttonWidget)
		self.layout.addWidget(self.sliderWidget)
		
		self.timer = QtCore.QTimer()
		self.timer.timeout.connect(self.timerFunction)
		self.timer.setInterval(300)
		self.timer.start()
		
		self.update()


if __name__ == '__main__':
	app = QtGui.QApplication(sys.argv)
	myapp = ButtonTest()
	myapp.show()
	sys.exit(app.exec_())	