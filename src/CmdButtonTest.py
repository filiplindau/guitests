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
		
		self.setupLayout()
		
	def buttonFunction(self):
		print 'Button press'
		self.buttonWidget.setStatus('Grr')
		self.buttonWidget.cmdButtons['Change'].setText('Apa ')
		self.buttonWidget.statusLabel.update()
		self.buttonWidget.layoutInfo.update()
		self.update()
	
	def setupLayout(self):
		s='QWidget{background-color: #000000; }'
		self.setStyleSheet(s)
		
		self.buttonWidget = qw.QTangoCommandSelection('Test')
		self.buttonWidget.addCmdButton('Change', self.buttonFunction)
		self.buttonWidget.addCmdButton('B2', self.buttonFunction)
				
		self.layout = QtGui.QVBoxLayout(self)
		self.layout.addWidget(self.buttonWidget)
		
		self.update()


if __name__ == '__main__':
	app = QtGui.QApplication(sys.argv)
	myapp = ButtonTest()
	myapp.show()
	sys.exit(app.exec_())	