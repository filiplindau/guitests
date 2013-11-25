# -*- coding:utf-8 -*-
"""
Created on Feb 14, 2013

@author: Filip
"""
from PyQt4 import QtGui, QtCore, Qt
import numpy as np
import sys
import PyTango as pt
import pyqtgraph as pg
from collections import OrderedDict
import time

backgroundColor = '#000000'
primaryColor0 = '#ff9900'
primaryColor1 = '#ffcc66'
primaryColor2 = '#feff99'
secondaryColor0 = '#66cbff'
secondaryColor1 = '#3399ff'
secondaryColor2 = '#99cdff'

faultColor = '#ff0000'
alarmColor = '#f7bd5a'
onColor = '#99dd66'
offColor = '#ffffff'
standbyColor = '#9c9cff'
unknownColor = '#45616f'
disableColor = '#ff00ff'

class QTangoColors(object):
	def __init__(self):
		self.backgroundColor = '#000000'
		self.primaryColor0 = '#ff9900'
		self.primaryColor1 = '#ffcc66'
		self.primaryColor2 = '#feff99'
		self.secondaryColor0 = '#66cbff'
		self.secondaryColor1 = '#3399ff'
		self.secondaryColor2 = '#99cdff'
		
		self.faultColor = '#ff0000'
		self.alarmColor = '#f7bd5a'
		self.warnColor = '#a35918'
		self.onColor = '#99dd66'
		self.offColor = '#ffffff'
		self.standbyColor = '#9c9cff'
		self.unknownColor = '#45616f'
		self.disableColor = '#ff00ff'

class QTangoSizes(object):
	def __init__(self):
		self.barHeight = 30
		self.barWidth = 90
		self.readAttributeWidth = 200
		self.writeAttributeWidth = 280
		self.trendWidth = 100
		self.fontSize = 12
		self.fontType = 'Calibri'
		self.fontStretch = 75
		self.fontWeight = 50
		
barHeight = 30
barWidth = 90

class QTangoTitleBar(QtGui.QWidget):
	def __init__(self, title='', parent=None):
		QtGui.QWidget.__init__(self, parent)
		self.title = title
		self.setupLayout()
		
	def setupLayout(self):
		self.startLabel = QtGui.QLabel('')
		s = ''.join(('QLabel {min-height: ', str(int(barHeight * 1.25)), 'px; \n',
					'min-width: ', str(int(barHeight * 1.25 / 3)), 'px; \n',
					'max-height: ', str(int(barHeight * 1.25)), 'px; \n',
					'background-color: ', primaryColor0, '; \n',
					'}'))
		self.startLabel.setStyleSheet(s)
		
		self.endLabel = QtGui.QLabel('')
		s = ''.join(('QLabel {min-height: ', str(int(barHeight * 1.25)), 'px; \n',
					'min-width: ', str(int(barHeight * 1.25)), 'px; \n',
					'max-height: ', str(int(barHeight * 1.25)), 'px; \n',
					'background-color: ', primaryColor0, '; \n',
					'}'))
		self.endLabel.setStyleSheet(s)
		
		self.nameLabel = QtGui.QLabel('')
		s = ''.join(('QLabel {min-height: ', str(int(barHeight * 1.25)), 'px; \n',
					'max-height: ', str(int(barHeight * 1.25)), 'px; \n',
					'background-color: ', backgroundColor, '; \n',
					'color: ', primaryColor0, '; \n',
					'}'))
		self.nameLabel.setStyleSheet(s)
		
		self.nameLabel.setText(self.title.upper())
		font = self.nameLabel.font()
		font.setFamily('TrebuchetMS')
		font.setStretch(QtGui.QFont.Condensed)
		font.setWeight(QtGui.QFont.Light)
		font.setPointSize(int(barHeight * 1.15))
		font.setStyleStrategy(QtGui.QFont.PreferAntialias)
		self.nameLabel.setFont(font)
		self.nameLabel.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
		
		self.layout = QtGui.QHBoxLayout(self)
		self.layout.setSpacing(int(barHeight / 5))
		self.layout.setMargin(0)
		self.layout.addStretch()
		self.layout.addWidget(self.startLabel)
		self.layout.addWidget(self.nameLabel)
		self.layout.addWidget(self.endLabel)
		
#		self.setStyleSheet(s)

class QTangoSideBar(QtGui.QWidget):
	def __init__(self, sizes = None, colors = None, parent=None):
		QtGui.QWidget.__init__(self, parent)
		if colors == None:
			self.attrColors = QTangoColors()
		else:
			self.attrColors = colors
		if sizes == None:
			self.sizes = QTangoSizes()
		else:
			self.sizes = sizes
		self.cmdButtons = OrderedDict()
		self.layout = None
		self.setupLayout()		
		
	def setupLayout(self):
		self.startLabel = QtGui.QLabel('')
		s = ''.join(('QLabel {min-height: ', str(int(self.sizes.barHeight * 2)), 'px; \n',
					'min-width: ', str(int(self.sizes.barWidth)), 'px; \n',
					'max-width: ', str(int(self.sizes.barWidth)), 'px; \n',
					'max-height: ', str(int(self.sizes.barHeight * 2)), 'px; \n',
					'background-color: ', self.attrColors.primaryColor0, '; \n',
					'}'))
		self.startLabel.setStyleSheet(s)
		
		self.endLabel = QtGui.QLabel('')
		s = ''.join(('QLabel {min-height: ', str(int(self.sizes.barHeight * 2)), 'px; \n',
					'min-width: ', str(int(self.sizes.barWidth)), 'px; \n',
					'max-width: ', str(int(self.sizes.barWidth)), 'px; \n',
					'background-color: ', self.attrColors.primaryColor0, '; \n',
					'}'))
		self.endLabel.setStyleSheet(s)
		self.endLabel.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Expanding)
		
		if self.layout != None:
			for i in reversed(range(self.layout.count())): 
				self.layout.itemAt(i).widget().setParent(None)
		if self.layout == None:
			self.layout = QtGui.QVBoxLayout(self)
		self.layout.setMargin(0)
		self.layout.setSpacing(int(self.sizes.barHeight / 10))
		self.layout.addWidget(self.startLabel)
		for cmdButton in self.cmdButtons.itervalues():
			self.layout.addWidget(cmdButton)
		self.layout.addWidget(self.endLabel)
		
		self.update()
		
	def addCmdButton(self, title, slot = None):
		cmdButton = QtGui.QPushButton('CMD ')
		s = ''.join(('QPushButton {	background-color: ', self.attrColors.primaryColor0, '; \n',
					'color: ', self.attrColors.backgroundColor, '; \n',
					'min-height: ', str(int(self.sizes.barHeight * 1.25)), 'px; \n',
					'max-height: ', str(int(self.sizes.barHeight * 1.25)), 'px; \n',
					'min-width: ', str(int(self.sizes.barWidth)), 'px; \n',
					'max-width: ', str(int(self.sizes.barWidth)), 'px; \n',
					'padding-left: 5px; \n',
					'padding-right: 5px; \n',
					'border-width: 0px; \n',
					'border-style: solid; \n',
					'border-color: #339; \n',
					'border-radius: 0; \n',
					'border: 0px; \n',
					'text-align: right bottom;\n',
					'padding: 0px; \n',
					'margin: 0px; \n',
					'} \n',
					'QPushButton:hover{ background-color: ', self.attrColors.primaryColor1, ';} \n',
					'QPushButton:hover:pressed{ background-color: ', self.attrColors.primaryColor2, ';} \n'))
		cmdButton.setStyleSheet(s)
		
		cmdButton.setText(''.join((title, ' ')))
		font = cmdButton.font()
		font.setFamily(self.sizes.fontType)
		font.setStretch(self.sizes.fontStretch)
		font.setPointSize(int(self.sizes.barHeight * 0.5))	
		font.setStyleStrategy(QtGui.QFont.PreferAntialias)	
		cmdButton.setFont(font)
		
		if slot != None:
			cmdButton.clicked.connect(slot)
		
		self.cmdButtons[title] = cmdButton
		
		self.setupLayout()
		
class QTangoHorizontalBar(QtGui.QWidget):
	def __init__(self, parent=None):
		QtGui.QWidget.__init__(self, parent)
		self.startLabel = QtGui.QLabel('')
		s = ''.join(('QLabel {min-height: ', str(int(barHeight)), 'px; \n',
					'min-width: ', str(int(barWidth)), 'px; \n',
					'max-height: ', str(int(barHeight)), 'px; \n',
					'background-color: ', primaryColor0, '; \n',
					'}'))
		self.startLabel.setStyleSheet(s)
		
		self.endLabel = QtGui.QLabel('')
		s = ''.join(('QLabel {min-height: ', str(int(barHeight)), 'px; \n',
					'min-width: ', str(int(barWidth * 1.25)), 'px; \n',
					'max-height: ', str(int(barHeight)), 'px; \n',
					'background-color: ', primaryColor0, '; \n',
					'}'))
		self.endLabel.setStyleSheet(s)
		self.endLabel.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
		
		
		
		self.layout = QtGui.QHBoxLayout(self)
		self.layout.setSpacing(0)
		self.layout.setMargin(0)
		self.layout.addWidget(self.startLabel)
		self.layout.addWidget(self.endLabel)
		
class QTangoCommandButton(QtGui.QWidget):
	def __init__(self, title, slot = None, sizes = None, colors = None, parent=None):
		QtGui.QWidget.__init__(self, parent)
		
		cmdButton = QtGui.QPushButton('CMD ')
		s = ''.join(('QPushButton {	background-color: ', self.attrColors.primaryColor0, '; \n',
					'color: ', self.attrColors.backgroundColor, '; \n',
					'min-height: ', str(int(self.sizes.barHeight * 1.25)), 'px; \n',
					'max-height: ', str(int(self.sizes.barHeight * 1.25)), 'px; \n',
					'min-width: ', str(int(self.sizes.barWidth)), 'px; \n',
					'max-width: ', str(int(self.sizes.barWidth)), 'px; \n',
					'padding-left: 5px; \n',
					'padding-right: 5px; \n',
					'border-width: 0px; \n',
					'border-style: solid; \n',
					'border-color: #339; \n',
					'border-radius: 0; \n',
					'border: 0px; \n',
					'text-align: right bottom;\n',
					'padding: 0px; \n',
					'margin: 0px; \n',
					'} \n',
					'QPushButton:hover{ background-color: ', self.attrColors.primaryColor1, ';} \n',
					'QPushButton:hover:pressed{ background-color: ', self.attrColors.primaryColor2, ';} \n'))
		cmdButton.setStyleSheet(s)
		
		cmdButton.setText(''.join((title, ' ')))
		font = cmdButton.font()
		font.setFamily(self.sizes.fontType)
		font.setStretch(QtGui.QFont.Condensed)
		font.setPointSize(int(self.sizes.barHeight * 0.5))		
		cmdButton.setFont(font)
		
class QTangoCommandSelection(QtGui.QWidget):
	def __init__(self, title, sizes = None, colors = None, parent=None):
		QtGui.QWidget.__init__(self, parent)

		if colors == None:
			self.attrColors = QTangoColors()
		else:
			self.attrColors = colors
		if sizes == None:
			self.sizes = QTangoSizes()
		else:
			self.sizes = sizes
		self.cmdButtons = OrderedDict()
		self.title = title
		self.layout = None
		self.setupLayout()		
		
	def setupLayout(self):
		# Init layouts once
		if self.layout == None:

			self.startLabel = QTangoStartLabel(self.sizes, self.attrColors)
			self.endLabel = QTangoEndLabel(self.sizes, self.attrColors)
			self.nameLabel = QTangoAttributeNameLabel(self.sizes, self.attrColors)
			self.nameLabel.setText(self.title)
			self.statusLabel = QTangoAttributeNameLabel(self.sizes, self.attrColors)			
			self.statusLabel.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
			self.statusLabel.setText('')
	

			self.layout = QtGui.QHBoxLayout(self)
			self.layout.setContentsMargins(0,0,0,0)
			self.layout.setMargin(int(self.sizes.barHeight/10))
#			self.layout.setMargin(0)
			self.layout.setSpacing(self.sizes.barHeight/3)
			
			self.layout2 = QtGui.QVBoxLayout()
			self.layout2.setContentsMargins(0,0,0,0)
			self.layout2.setMargin(int(self.sizes.barHeight/10))
			self.layout2.setMargin(0)			
			
			self.layoutInfo = QtGui.QHBoxLayout()
			self.layoutInfo.setContentsMargins(0,0,0,0)
			self.layoutInfo.setMargin(int(self.sizes.barHeight/10))
			self.layoutInfo.setMargin(0)
			self.layoutInfo.setSpacing(int(self.sizes.barHeight / 3))
			self.layoutInfo.addWidget(self.nameLabel)		
			self.layoutInfo.addWidget(self.statusLabel)
			self.layoutButtons = QtGui.QHBoxLayout()
			self.layoutButtons.setContentsMargins(0,0,0,0)
			self.layoutButtons.setMargin(int(self.sizes.barHeight/10))
			self.layoutButtons.setMargin(0)
			self.layoutButtons.setSpacing(int(self.sizes.barHeight / 3))
			self.layout2.addLayout(self.layoutInfo)		
			self.layout2.addLayout(self.layoutButtons)
			
			self.layout.addWidget(self.startLabel)		
			self.layout.addLayout(self.layout2)		
			self.layout.addWidget(self.endLabel)
			
# 			self.setMaximumWidth(self.sizes.readAttributeWidth)
# 			self.setMinimumWidth(self.sizes.readAttributeWidth)
# 			self.setMaximumHeight(self.sizes.barHeight*2.2)
# 			self.setMinimumHeight(self.sizes.barHeight*2.2)
# 			self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
			


# Clear out old layout
		if self.cmdButtons.keys().__len__() > 0:
			for i in reversed(range(self.layoutButtons.count())): 
				self.layoutButtons.itemAt(i).widget().setParent(None)

# Add buttons	
		for cmdButton in self.cmdButtons.itervalues():
			self.layoutButtons.addWidget(cmdButton)		
#		self.layoutButtons.setSpacing(int(self.sizes.barHeight / 10))				
	
		self.setMaximumWidth(self.sizes.readAttributeWidth)
		self.setMinimumWidth(self.sizes.readAttributeWidth)
		self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)

		self.update()
		
	def setStatus(self, statusText, state = None):
		self.statusLabel.setText(statusText)	
		self.statusLabel.repaint()
		
#		self.update()	
		
	def addCmdButton(self, name, slot):
		cmdButton = QtGui.QPushButton('CMD ')
		buttonHeight = self.sizes.barHeight*1.75
		s = ''.join(('QPushButton {	background-color: ', self.attrColors.secondaryColor0, '; \n',
					'color: ', self.attrColors.backgroundColor, '; \n',
					'min-height: ', str(int(buttonHeight)), 'px; \n',
					'max-height: ', str(int(buttonHeight)), 'px; \n',
#					'min-width: ', str(int(self.sizes.barWidth)), 'px; \n',
#					'max-width: ', str(int(self.sizes.barWidth)), 'px; \n',
					'padding-left: 5px; \n',
					'padding-right: 5px; \n',
					'border-width: 0px; \n',
					'border-style: solid; \n',
					'border-color: #339; \n',
					'border-radius: 0; \n',
					'border: 0px; \n',
					'text-align: right bottom;\n',
					'padding: 0px; \n',
					'margin: 0px; \n',
					'} \n',
					'QPushButton:hover{ background-color: ', self.attrColors.secondaryColor1, ';} \n',
					'QPushButton:hover:pressed{ background-color: ', self.attrColors.secondaryColor2, ';} \n'))
		cmdButton.setStyleSheet(s)
		
		cmdButton.setText(''.join((name, ' ')))
		font = cmdButton.font()
		font.setFamily(self.sizes.fontType)
		font.setStretch(self.sizes.fontStretch)#QtGui.QFont.Condensed)
#		font.setPointSize(int(buttonHeight  * 0.4))	
		font.setPointSize(int(self.sizes.barHeight * 0.7))	
		font.setStyleStrategy(QtGui.QFont.PreferAntialias)	
		cmdButton.setFont(font)
		
		if slot != None:
			cmdButton.clicked.connect(slot)
		
		self.cmdButtons[name] = cmdButton	
		
		self.setupLayout()	
		
class QTangoAttributeBase(QtGui.QWidget):
	def __init__(self, sizes = None, colors = None, parent=None):
		QtGui.QWidget.__init__(self, parent)
		if colors == None:
			self.attrColors = QTangoColors()
		else:
			self.attrColors = colors
		if sizes == None:
			self.sizes = QTangoSizes()
		else:
			self.sizes = sizes		
		self.setupLayout()
		
class QTangoStartLabel(QtGui.QLabel):
	def __init__(self, sizes = None, colors = None, parent=None):
		QtGui.QLabel.__init__(self, parent)
		if colors == None:
			self.attrColors = QTangoColors()
		else:
			self.attrColors = colors
		if sizes == None:
			self.sizes = QTangoSizes()
		else:
			self.sizes = sizes				
		self.setText('')
		st = ''.join(('QLabel {min-height: ', str(self.sizes.barHeight), 'px; \n',
					'min-width: ', str(int(self.sizes.barHeight / 6)), 'px; \n',
					'max-width: ', str(int(self.sizes.barHeight / 6)), 'px; \n',
					'background-color: ', self.attrColors.secondaryColor0, ';}'))
		self.setStyleSheet(st)

class QTangoEndLabel(QtGui.QLabel):
	def __init__(self, sizes = None, colors = None, parent=None):
		QtGui.QLabel.__init__(self, parent)
		if colors == None:
			self.attrColors = QTangoColors()
		else:
			self.attrColors = colors
		if sizes == None:
			self.sizes = QTangoSizes()
		else:
			self.sizes = sizes				
		self.setText('')
		st = ''.join(('QLabel {min-height: ', str(self.sizes.barHeight), 'px; \n',
					'min-width: ', str(int(self.sizes.barHeight / 2)), 'px; \n',
					'max-width: ', str(int(self.sizes.barHeight / 2)), 'px; \n',
					'background-color: ', self.attrColors.secondaryColor0, ';}'))
		self.setStyleSheet(st)

class QTangoAttributeNameLabel(QtGui.QLabel):
	def __init__(self, sizes = None, colors = None, parent=None):
		QtGui.QLabel.__init__(self, parent)
		if colors == None:
			self.attrColors = QTangoColors()
		else:
			self.attrColors = colors
		if sizes == None:
			self.sizes = QTangoSizes()
		else:
			self.sizes = sizes				
		self.setText('')
		s = ''.join(('QLabel {min-height: ', str(self.sizes.barHeight), 'px; \n',
					'max-height: ', str(self.sizes.barHeight), 'px; \n',
# 					'min-width: ', str(int(readWidth)), 'px; \n',
# 					'max-width: ', str(int(readWidth)), 'px; \n',
					'background-color: ', self.attrColors.backgroundColor, '; \n',
#					'background-color: ', self.attrColors.primaryColor0, '; \n',
					'color: ', self.attrColors.secondaryColor0, ';}'))
		self.setStyleSheet(s)
	
		font = self.font()
		font.setFamily(self.sizes.fontType)
		font.setStretch(self.sizes.fontStretch)
		font.setWeight(self.sizes.fontWeight)
		font.setPointSize(int(self.sizes.barHeight * 0.7))
		font.setStyleStrategy(QtGui.QFont.PreferAntialias)
#		font.setPointSize(int(self.sizes.fontSize))
		self.setFont(font)
		self.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
		self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)

class QTangoReadAttributeSpinBox(QtGui.QDoubleSpinBox):
	def __init__(self, sizes = None, colors = None, parent=None):
		QtGui.QDoubleSpinBox.__init__(self, parent)
		self.setLocale(QtCore.QLocale(QtCore.QLocale.English))
		if colors == None:
			self.attrColors = QTangoColors()
		else:
			self.attrColors = colors
		if sizes == None:
			self.sizes = QTangoSizes()
		else:
			self.sizes = sizes				
		s = ''.join(('QDoubleSpinBox { \n',
            'background-color: ', self.attrColors.backgroundColor, '; \n',
            'border-width: 0px; \n',
            'border-color: #339; \n',
            'border-style: solid; \n',
            'border-radius: 0; \n',
            'border: 0px; \n',
            'padding: 0px; \n',
            'margin: 0px; \n',
            'qproperty-buttonSymbols: NoButtons; \n',
            'min-width: ', str(int(self.sizes.barWidth)), 'px; \n',
			'max-width: ', str(int(self.sizes.barWidth)), 'px; \n',
            'min-height: ', str(self.sizes.barHeight), 'px; \n',
            'max-height: ', str(self.sizes.barHeight), 'px; \n',
            'qproperty-readOnly: 1; \n',
            'color: ', self.attrColors.secondaryColor0, ';} \n'))
		font = self.font()
		font.setFamily(self.sizes.fontType)
		font.setStretch(self.sizes.fontStretch)
		font.setWeight(self.sizes.fontWeight)
		font.setPointSize(int(self.sizes.barHeight * 0.7))
		font.setStyleStrategy(QtGui.QFont.PreferAntialias)
		self.setFont(font)
		self.setStyleSheet(s)
		self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
		self.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom)
		self.setMaximum(1e9)
		
class QTangoWriteAttributeSpinBox(QtGui.QDoubleSpinBox):
	def __init__(self, sizes = None, colors = None, parent=None):
		QtGui.QDoubleSpinBox.__init__(self, parent)
		self.setLocale(QtCore.QLocale(QtCore.QLocale.English))		
		self.lineEdit().cursorPositionChanged.connect(self.changeStep)
		self.valueChanged.connect(self.valueReady)
		self.editingFinished.connect(self.editReady)		
		self.storedCursorPos = 0
		if colors == None:
			self.attrColors = QTangoColors()
		else:
			self.attrColors = colors
		if sizes == None:
			self.sizes = QTangoSizes()
		else:
			self.sizes = sizes		
		s = ''.join(('QDoubleSpinBox { \n',
            'background-color: ', self.attrColors.backgroundColor, '; \n',
            'selection-background-color: ', self.attrColors.secondaryColor0, '; \n',
            'selection-color: ', self.attrColors.backgroundColor, '; \n',
            'border-width: 1px; \n',
            'border-color: ', self.attrColors.secondaryColor0, '; \n',
            'border-style: solid; \n',
            'border-radius: 0px; \n',
            'padding: 0px; \n',
            'margin: 0px; \n',
            'qproperty-buttonSymbols: NoButtons; \n',
            'min-width: ', str(self.sizes.barWidth), 'px; \n',
            'max-width: ', str(self.sizes.barWidth), 'px; \n',
            'min-height: ', str(int(self.sizes.barHeight-2)), 'px; \n',
            'max-height: ', str(int(self.sizes.barHeight-2)), 'px; \n',
            'qproperty-readOnly: 0; \n',
            'color: ', self.attrColors.secondaryColor0, ';} \n'))
		font = self.font()
		font.setFamily(self.sizes.fontType)
		font.setStretch(self.sizes.fontStretch)
		font.setWeight(self.sizes.fontWeight)
		font.setPointSize(int(self.sizes.barHeight * 0.7))
		font.setStyleStrategy(QtGui.QFont.PreferAntialias)
		self.setFont(font)
#		self.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Minimum)

		self.setStyleSheet(s)
		self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
		self.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)	
		self.setMaximum(1e9)	

	def valueReady(self, value):
		print 'Value ready::', value
		self.lineEdit().setCursorPosition(self.storedCursorPos)

	def editReady(self):
		print 'Edit ready::'
		self.lineEdit().setCursorPosition(self.storedCursorPos)

	def stepBy(self, steps):
		print 'Step ', steps
		self.setValue(self.value() + self.singleStep() * steps)
		
	def changeStep(self, old, new):
		print 'In changeStep::'
		txt = str(self.text())
		commaPos = txt.find('.')
		self.storedCursorPos = self.lineEdit().cursorPosition()
		pos = commaPos - self.storedCursorPos + 1
		print 'pos', pos
		print 'comma pos', commaPos
		print 'stored pos', self.storedCursorPos
		if pos + self.decimals() < 0:
			pos = -self.decimals()
		elif pos > 0:
			pos -= 1

		print txt, pos
		self.setSingleStep(10 ** pos)
		
	def setColors(self, attrColorName, backgroundColorName):
		backgroundColor = self.attrColors.__getattribute__(backgroundColorName)
		mainColor = self.attrColors.__getattribute__(attrColorName)
		s = ''.join(('QDoubleSpinBox { \n',
            'background-color: ', backgroundColor, '; \n',
            'selection-background-color: ', mainColor, '; \n',
            'selection-color: ', backgroundColor, '; \n',
            'border-width: 1px; \n',
            'border-color: ', mainColor, '; \n',
            'border-style: solid; \n',
            'border-radius: 0px; \n',
            'padding: 0px; \n',
            'margin: 0px; \n',
            'qproperty-buttonSymbols: NoButtons; \n',
            'min-width: ', str(self.sizes.barWidth), 'px; \n',
            'max-width: ', str(self.sizes.barWidth), 'px; \n',
            'min-height: ', str(int(self.sizes.barHeight-2)), 'px; \n',
            'max-height: ', str(int(self.sizes.barHeight-2)), 'px; \n',
            'qproperty-readOnly: 0; \n',
            'color: ', mainColor, ';} \n'))
		
		self.setStyleSheet(s)
				
class QTangoReadAttributeDouble(QtGui.QWidget):
	def __init__(self, sizes = None, colors = None, parent=None):
		QtGui.QWidget.__init__(self, parent)
		if colors == None:
			self.attrColors = QTangoColors()
		else:
			self.attrColors = colors
		if sizes == None:
			self.sizes = QTangoSizes()
		else:
			self.sizes = sizes		
		self.setupLayout()
		
	def setupLayout(self):
		readValueWidth = self.sizes.barWidth
		readWidth = self.sizes.readAttributeWidth-self.sizes.barHeight/6-self.sizes.barHeight/2-readValueWidth

		self.startLabel = QtGui.QLabel('')
		st = ''.join(('QLabel {min-height: ', str(self.sizes.barHeight), 'px; \n',
					'min-width: ', str(int(self.sizes.barHeight / 6)), 'px; \n',
					'max-width: ', str(int(self.sizes.barHeight / 6)), 'px; \n',
					'max-height: ', str(self.sizes.barHeight), 'px; \n',
					'background-color: ', self.attrColors.secondaryColor0, ';}'))
		self.startLabel.setStyleSheet(st)
		self.endLabel = QtGui.QLabel('')
		st = ''.join(('QLabel {min-height: ', str(self.sizes.barHeight), 'px; \n',
					'min-width: ', str(int(self.sizes.barHeight / 2)), 'px; \n',
					'max-width: ', str(int(self.sizes.barHeight / 2)), 'px; \n',
					'max-height: ', str(self.sizes.barHeight), 'px; \n',
					'background-color: ', self.attrColors.secondaryColor0, ';}'))
		self.endLabel.setStyleSheet(st)

		self.nameLabel = QtGui.QLabel('Test')
		s = ''.join(('QLabel {min-height: ', str(self.sizes.barHeight), 'px; \n',
					'max-height: ', str(self.sizes.barHeight), 'px; \n',
					'min-width: ', str(int(readWidth)), 'px; \n',
					'max-width: ', str(int(readWidth)), 'px; \n',
					'background-color: ', self.attrColors.backgroundColor, '; \n',
					'color: ', self.attrColors.secondaryColor0, ';}'))
		self.nameLabel.setStyleSheet(s)
	
		font = self.nameLabel.font()
		font.setFamily(self.sizes.fontType)
		font.setStretch(self.sizes.fontStretch)
		font.setWeight(self.sizes.fontWeight)
		font.setPointSize(int(self.sizes.barHeight * 0.7))
		font.setStyleStrategy(QtGui.QFont.PreferAntialias)
#		font.setPointSize(int(self.sizes.fontSize))
		self.nameLabel.setFont(font)
		self.nameLabel.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
		self.nameLabel.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)

		self.valueSpinbox = QtGui.QDoubleSpinBox()
		s = ''.join(('QDoubleSpinBox { \n',
            'background-color: ', self.attrColors.backgroundColor, '; \n',
            'border-width: 0px; \n',
            'border-color: #339; \n',
            'border-style: solid; \n',
            'border-radius: 0; \n',
            'border: 0px; \n',
            'padding: 0px; \n',
            'margin: 0px; \n',
            'qproperty-buttonSymbols: NoButtons; \n',
            'min-width: ', str(int(readValueWidth)), 'px; \n',
			'max-width: ', str(int(readValueWidth)), 'px; \n',
            'min-height: ', str(self.sizes.barHeight), 'px; \n',
            'max-height: ', str(self.sizes.barHeight), 'px; \n',
            'qproperty-readOnly: 1; \n',
            'color: ', self.attrColors.secondaryColor0, ';} \n'))
		font = self.valueSpinbox.font()
		font.setFamily(self.sizes.fontType)
		font.setStretch(self.sizes.fontStretch)
		font.setWeight(self.sizes.fontWeight)
		font.setPointSize(int(self.sizes.barHeight * 0.7))
		font.setStyleStrategy(QtGui.QFont.PreferAntialias)
		self.valueSpinbox.setFont(font)
		self.valueSpinbox.setStyleSheet(s)
		self.valueSpinbox.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
		self.valueSpinbox.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

		spacerItem = QtGui.QSpacerItem(0, 0, QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Minimum)

		layout = QtGui.QHBoxLayout(self)
		layout.setContentsMargins(0,0,0,0)
		layout.setMargin(int(self.sizes.barHeight/10))
		
#		layout.addSpacerItem(spacerItem)		
		layout.addWidget(self.startLabel)
		layout.addWidget(self.nameLabel)
		layout.addWidget(self.valueSpinbox)
		layout.addWidget(self.endLabel)
		
		self.setMaximumWidth(self.sizes.readAttributeWidth)
		self.setMinimumWidth(self.sizes.readAttributeWidth)
		self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)

	def attributeName(self):
		return str(self.nameLabel.text())

	@QtCore.pyqtSignature('setAttributeName(QString)')

	def setAttributeName(self, aName):
		self.nameLabel.setText(aName)
		self.update()
		
	def setAttributeValue(self, value):
		self.valueSpinbox.setValue(value)
		self.update()


		
class QTangoHSliderBase(QtGui.QSlider):
	def __init__(self, sizes = None, colors = None, parent=None):
		QtGui.QSlider.__init__(self, parent)
		if colors == None:
			self.attrColors = QTangoColors()
		else:
			self.attrColors = colors
		if sizes == None:
			self.sizes = QTangoSizes()
		else:
			self.sizes = sizes
		self.setMaximum(100)
		self.setMinimum(0)
		self.attrMaximum = 1
		self.attrMinimum = 0		
		self.attrValue = 0.5
		self.attrWriteValue = None
		self.warnHigh = 0.9
		self.warnLow = 0.1
		
		self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
		self.setMaximumHeight(self.sizes.barHeight)
		self.setMinimumHeight(self.sizes.barHeight)		
		
	def paintEvent(self, e):
		qp = QtGui.QPainter()
		qp.begin(self)
		self.drawWidget(qp)
		qp.end()
		
	def drawWidget(self, qp):
		size = self.size()
		w = size.width()
		h = size.height()
		
		startH = h/6.0		# Position of horizontal line
		lineW = h/4.0		# Width of horizontal line
		arrowW = h/2.5		# Width of arrow
		writeW = h/8.0
		
		# Vertical position of scale text
		textVertPos = h-h/16.0
		textVertPos = h
		# Pixel coordinate of current value:		
		xVal = w*(self.attrValue-self.attrMinimum)/(self.attrMaximum-self.attrMinimum)

		# Setup font
		font = QtGui.QFont(self.sizes.fontType, self.sizes.barHeight*0.5, self.sizes.fontWeight)
		font.setStretch(self.sizes.fontStretch)
		
		# Strings to draw
		sVal = "{:.2f}".format((self.attrValue))
		sMin = "{:.2f}".format((self.attrMinimum))
		sMax = "{:.2f}".format((self.attrMaximum))
		sValWidth = QtGui.QFontMetricsF(font).width(sVal)
		sMinWidth = QtGui.QFontMetricsF(font).width(sMin)
		sMaxWidth = QtGui.QFontMetricsF(font).width(sMax)
		
		# Position to draw text of current value
		textPoint = QtCore.QPointF(xVal+lineW/2+h/5.0,textVertPos)
		if xVal < 0:
			textPoint.setX(h/3.0+h/16.0) 
		if xVal + sValWidth > w:
			textPoint.setX(w-sValWidth-h/3.0-h/16.0)
		if xVal < 0:
			# Draw left pointing arrow if the pixel position is < 0
			poly = QtGui.QPolygonF([QtCore.QPointF(0,(startH+lineW/2+h)/2), 
					QtCore.QPointF(h/3.0,h),
					QtCore.QPointF(h/3.0,startH+lineW/2)])
		elif xVal > w:
			# Draw right pointing arrow if the pixel position is > w
			poly = QtGui.QPolygonF([QtCore.QPointF(w,(startH+lineW/2+h)/2), 
					QtCore.QPointF(w-h/3.0,h),
					QtCore.QPointF(w-h/3.0,startH+lineW/2)])
		else:
			# Draw up pointing arrow otherwise
			poly = QtGui.QPolygonF([QtCore.QPointF(xVal,startH+lineW/2.0), 
					QtCore.QPointF(xVal-arrowW/2.0,h),
					QtCore.QPointF(xVal+arrowW/2.0,h)])
			
		colorAttr = QtGui.QColor(self.attrColors.secondaryColor0)
		colorWriteAttr = QtGui.QColor(self.attrColors.secondaryColor2)
		penAttr = QtGui.QPen(colorAttr)
		penAttr.setWidthF(lineW)
		brushAttr = QtGui.QBrush(colorAttr)
		qp.setFont(font)

		colorWarn = QtGui.QColor(self.attrColors.warnColor)
		penWarn = QtGui.QPen(colorWarn)
		penWarn.setWidthF(lineW)
		brushWarn = QtGui.QBrush(colorWarn)
		
		qp.setRenderHint(QtGui.QPainter.Antialiasing, False) # No antialiasing when drawing horizontal/vertical lines
		qp.setRenderHint(QtGui.QPainter.TextAntialiasing, True)
		qp.setRenderHint(QtGui.QPainter.SmoothPixmapTransform, True)
		# Draw warning line
		qp.setPen(penWarn)
		qp.setBrush(brushWarn)
		qp.drawLine(0, startH, w, startH)
		# Draw line
		qp.setPen(penAttr)
		qp.setBrush(brushAttr)
		qp.drawLine(w*(self.warnLow-self.attrMinimum)/(self.attrMaximum-self.attrMinimum),startH,
				w*(self.warnHigh-self.attrMinimum)/(self.attrMaximum-self.attrMinimum),startH)
		
		# Draw arrow
		qp.setRenderHint(QtGui.QPainter.Antialiasing, True)
		
		# Change color of arrow when in warning range
# 		if self.attrValue < self.warnLow or self.attrValue > self.warnHigh: 
# 			pen = penWarn
# 			brush = brushWarn
# 			qp.setBrush(brush)
# 		else:
# 			pen = penAttr
# 			brush = brushAttr
		pen = penAttr
		pen.setWidthF(0)
		qp.setPen(pen)
		qp.drawPolygon(poly)
		if self.attrWriteValue != None:
			pen.setWidthF(writeW)
			pen.setColor(colorWriteAttr)
			qp.setPen(pen)
			xValW = w*(self.attrWriteValue-self.attrMinimum)/(self.attrMaximum-self.attrMinimum)
			qp.drawLine(xValW, h, xValW, 0)
		# Draw texts
#		qp.drawText(textPoint, sVal)
		# Don't draw the limit texts if the value text is overlapping
		pen.setColor(colorAttr)
		qp.setPen(pen)
		if xVal - arrowW/2 > sMinWidth:
			qp.drawText(QtCore.QPointF(0, textVertPos), sMin)
		if textPoint.x() < w-sMaxWidth:
			qp.drawText(QtCore.QPointF(w-sMaxWidth, textVertPos), sMax)

	def setValue(self, value):
		self.attrValue = value
		self.update()
		
	def setWriteValue(self, value):
		self.attrWriteValue = value
		self.update()
		
	def setWarningLimits(self, warnLow, warnHigh):
		self.warnHigh = warnHigh
		self.warnLow = warnLow
		self.update()
	
	def setSliderLimits(self, min, max):
		self.attrMinimum = min
		self.attrMaximum = max
		self.update()
		
class QTangoTrendBase(pg.PlotWidget):
	def __init__(self, sizes = None, colors = None, parent=None):
		pg.PlotWidget.__init__(self, useOpenGL = True)
		if colors == None:
			self.attrColors = QTangoColors()
		else:
			self.attrColors = colors
		if sizes == None:
			self.sizes = QTangoSizes()
		else:
			self.sizes = sizes		

		self.valuesSize = 100000

		self.setupLayout()
		self.setupData()
		
		
	def setupLayout(self):
		self.setXRange(-600, 0)
		self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
#		self.setMaximumWidth(self.sizes.readAttributeWidth-self.sizes.barHeight/6-self.sizes.barHeight/2)
		pi=self.getPlotItem()
		axLeft = pi.getAxis('left')
		axLeft.setPen(self.attrColors.secondaryColor0)
		pi.hideAxis('left')
#		axLeft.setWidth(1)
		axBottom = pi.getAxis('bottom')
		axBottom.setPen(self.attrColors.secondaryColor0)
#		axBottom.setHeight(1)

		axRight = pi.getAxis('right')
		axRight.setPen(self.attrColors.secondaryColor0)
# 		axRight.setWidth(0)
# 		axRight.setTicks([])
# 		axRight.showLabel(False)
 		pi.showAxis('right')

		colorWarn = QtGui.QColor(self.attrColors.warnColor)
#		colorWarn = QtGui.QColor('#339922')
		colorWarn.setAlphaF(0.75)
		colorGood = QtGui.QColor(self.attrColors.secondaryColor0)
		colorGood.setAlphaF(0.33)
		brushWarn = QtGui.QBrush(colorWarn, style = QtCore.Qt.SolidPattern)
		brushGood = QtGui.QBrush(colorGood, style = QtCore.Qt.SolidPattern)
		penLines = QtGui.QPen(QtGui.QColor('#55555500'))
		
		self.warningRegionUpper = pg.LinearRegionItem(values=[24, 100], orientation = pg.LinearRegionItem.Horizontal, 
													brush = brushWarn, movable = False)
		self.warningRegionUpper.lines[0].setPen(penLines)
		self.warningRegionUpper.lines[1].setPen(penLines)
		self.warningRegionLower = pg.LinearRegionItem(values=[-100, 26], orientation = pg.LinearRegionItem.Horizontal, 
													brush = brushWarn, movable = False)
		self.warningRegionLower.lines[0].setPen(penLines)
		self.warningRegionLower.lines[1].setPen(penLines)
		self.goodRegion = pg.LinearRegionItem(values=[24, 26], orientation = pg.LinearRegionItem.Horizontal, 
													brush = brushGood, movable = False)
		self.goodRegion.lines[0].setPen(penLines)
		self.goodRegion.lines[1].setPen(penLines)
		self.addItem(self.warningRegionUpper)	
		self.addItem(self.warningRegionLower)
		self.addItem(self.goodRegion)
		self.valueTrendCurve = self.plot()
		self.valueTrendCurve.setPen(self.attrColors.secondaryColor0, width = 2.0)
		
	def setupData(self):
		self.xValues = np.linspace(-10000, 0, self.valuesSize)
		self.yValues = np.sin(self.xValues*10*np.pi/600)+1
		self.currentDataIndex = 0
		self.valueTrendCurve.setData(self.xValues, self.yValues, antialias = True)
		
	def setWarningLimits(self, warnLow, warnHigh):
		self.warningRegionUpper.setRegion([warnHigh, 1e6])
		self.warningRegionLower.setRegion([-1e6, warnLow])
		self.goodRegion.setRegion([warnLow, warnHigh])
		
		
	def addPoint(self, xNew, yNew):
		if self.currentDataIndex+1 > self.valuesSize:
			self.xData[0:self.valuesSize*0.75]=self.xData[self.valuesSize-self.valuesSize*0.75, self.valuesSize]
			self.yData[0:self.valuesSize*0.75]=self.yData[self.valuesSize-self.valuesSize*0.75, self.valuesSize]
			self.currentDataIndex = self.valuesSize*0.75
		elif self.currentDataIndex == 0:
			self.xValues[0] = xNew
			self.yValues[0] = yNew
		self.currentDataIndex+=1
		self.xValues[self.currentDataIndex] = xNew
		self.yValues[self.currentDataIndex] = yNew
		self.valueTrendCurve.setData(self.xValues[0:self.currentDataIndex]-xNew, self.yValues[0:self.currentDataIndex], antialias = True)

class QTangoSpectrumBase(pg.PlotWidget):
	def __init__(self, sizes = None, colors = None, parent=None):
		pg.PlotWidget.__init__(self, useOpenGL = True)
		if colors == None:
			self.attrColors = QTangoColors()
		else:
			self.attrColors = colors
		if sizes == None:
			self.sizes = QTangoSizes()
		else:
			self.sizes = sizes		

		self.setupLayout()
		
	def setupLayout(self):
		self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
		pi=self.getPlotItem()
		axLeft = pi.getAxis('left')
		axLeft.setPen(self.attrColors.secondaryColor0)
		axBottom = pi.getAxis('bottom')
		axBottom.setPen(self.attrColors.secondaryColor0)

		self.spectrumCurve = self.plot()
		self.spectrumCurve.setPen(self.attrColors.secondaryColor0, width = 2.0)
		
	def setSpectrum(self, xData, yData):
		self.spectrumCurve.setData(y = yData, x = xData, antialias = True)
		self.update()
		

class QTangoReadAttributeSlider(QtGui.QWidget):
	def __init__(self, sizes = None, colors = None, parent=None):
		QtGui.QWidget.__init__(self, parent)
		if colors == None:
			self.attrColors = QTangoColors()
		else:
			self.attrColors = colors
		if sizes == None:
			self.sizes = QTangoSizes()
		else:
			self.sizes = sizes		
		self.setupLayout()
		
	def setupLayout(self):
		readValueWidth = self.sizes.barWidth
		readWidth = self.sizes.readAttributeWidth-self.sizes.barHeight/6-self.sizes.barHeight/2
		
		self.startLabel = QTangoStartLabel(self.sizes, self.attrColors)
		self.endLabel = QTangoEndLabel(self.sizes, self.attrColors)
		self.nameLabel = QTangoAttributeNameLabel(self.sizes, self.attrColors)
		self.valueSpinbox = QTangoReadAttributeSpinBox(self.sizes, self.attrColors)
		self.valueSlider = QTangoHSliderBase(self.sizes, self.attrColors)


		self.layout = QtGui.QHBoxLayout(self)
		self.layout.setContentsMargins(0,0,0,0)
		self.layout.setMargin(int(self.sizes.barHeight/10))
		self.layout.setSpacing(self.sizes.barHeight/3)
		
		self.layoutGrid = QtGui.QGridLayout()
		self.layoutGrid.setContentsMargins(0, 0, 0, 0)
		self.layoutGrid.setMargin(int(self.sizes.barHeight/10))
		self.layoutGrid.setMargin(0)
		self.layoutGrid.addWidget(self.nameLabel, 0, 0, )
		self.layoutGrid.addWidget(self.valueSlider, 1, 0)
		self.layoutGrid.addWidget(self.valueSpinbox, 0, 1)		
		self.layoutGrid.setHorizontalSpacing(self.sizes.barHeight/4)
		self.layoutGrid.setVerticalSpacing(0)

		self.layout.addWidget(self.startLabel)		
		self.layout.addLayout(self.layoutGrid)		
		self.layout.addWidget(self.endLabel)
		
		self.setMaximumWidth(self.sizes.readAttributeWidth)
		self.setMinimumWidth(self.sizes.readAttributeWidth)
		self.setMaximumHeight(self.sizes.barHeight*2.2)
		self.setMinimumHeight(self.sizes.barHeight*2.2)
		self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)

	def attributeName(self):
		return str(self.nameLabel.text())

	@QtCore.pyqtSignature('setAttributeName(QString)')

	def setAttributeName(self, aName):
		self.nameLabel.setText(aName)
		self.update()
		
	def setAttributeValue(self, value):
		self.valueSpinbox.setValue(value)
		self.valueSlider.setValue(value)
		self.update()
		
	def setAttributeWarningLimits(self, warnLow, warnHigh):
		self.valueSlider.setWarningLimits(warnLow, warnHigh)
		
	def setSliderLimits(self, min, max):
		self.valueSlider.setSliderLimits(min, max)

class QTangoReadAttributeTrend(QtGui.QWidget):
	def __init__(self, sizes = None, colors = None, parent=None):
		QtGui.QWidget.__init__(self, parent)
		if colors == None:
			self.attrColors = QTangoColors()
		else:
			self.attrColors = colors
		if sizes == None:
			self.sizes = QTangoSizes()
		else:
			self.sizes = sizes		
		self.setupLayout()
		
	def setupLayout(self):
		readValueWidth = self.sizes.barWidth
		readWidth = self.sizes.readAttributeWidth-self.sizes.barHeight/6-self.sizes.barHeight/2

		self.startLabel = QTangoStartLabel(self.sizes, self.attrColors)
		self.endLabel = QTangoEndLabel(self.sizes, self.attrColors)
		self.nameLabel = QTangoAttributeNameLabel(self.sizes, self.attrColors)
		self.valueSpinbox = QTangoReadAttributeSpinBox(self.sizes, self.attrColors)
		self.valueSlider = QTangoHSliderBase(self.sizes, self.attrColors)
		self.valueTrend = QTangoTrendBase(self.sizes, self.attrColors)
		
		self.layout = QtGui.QHBoxLayout(self)
		self.layout.setContentsMargins(0,0,0,0)
		self.layout.setMargin(int(self.sizes.barHeight/10))
#		self.layout.setMargin(0)
		self.layout.setSpacing(self.sizes.barHeight/3)
		
		self.layoutGrid = QtGui.QGridLayout()
		self.layoutGrid.setContentsMargins(0, 0, 0, 0)
		self.layoutGrid.setMargin(0)
		self.layoutGrid.addWidget(self.nameLabel, 0, 0)
		self.layoutGrid.addWidget(self.valueSpinbox, 0, 1)		
		self.layoutGrid.addWidget(self.valueTrend, 1, 0, 1, 2)
		self.layoutGrid.setHorizontalSpacing(self.sizes.barHeight/4)
		self.layoutGrid.setVerticalSpacing(0)

		self.layout.addWidget(self.startLabel)
		self.layout.addLayout(self.layoutGrid)		
		self.layout.addWidget(self.endLabel)
		
		self.setMaximumWidth(self.sizes.readAttributeWidth)
		self.setMinimumWidth(self.sizes.readAttributeWidth)
		self.setMaximumHeight(self.sizes.barHeight*4)
		self.setMinimumHeight(self.sizes.barHeight*4)
		self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)		

	def attributeName(self):
		return str(self.nameLabel.text())

	@QtCore.pyqtSignature('setAttributeName(QString)')

	def setAttributeName(self, aName):
		self.nameLabel.setText(aName)
		self.update()
		
	def setAttributeValue(self, value):
		t = time.time()
		self.valueSpinbox.setValue(value)
		self.valueTrend.addPoint(t, value)
		self.update()
		
	def setAttributeWarningLimits(self, warnLow, warnHigh):
		self.valueTrend.setWarningLimits(warnLow, warnHigh)
		
	def setTrendLimits(self, low, high):
		self.valueTrend.setYRange(low, high)
		
class QTangoReadAttributeSpectrum(QtGui.QWidget):
	def __init__(self, sizes = None, colors = None, parent=None):
		QtGui.QWidget.__init__(self, parent)
		if colors == None:
			self.attrColors = QTangoColors()
		else:
			self.attrColors = colors
		if sizes == None:
			self.sizes = QTangoSizes()
		else:
			self.sizes = sizes		
		self.setupLayout()
		
	def setupLayout(self):
		readValueWidth = self.sizes.barWidth
		readWidth = self.sizes.readAttributeWidth-self.sizes.barHeight/6-self.sizes.barHeight/2

		self.startLabel = QTangoStartLabel(self.sizes, self.attrColors)
		self.endLabel = QTangoEndLabel(self.sizes, self.attrColors)
		self.nameLabel = QTangoAttributeNameLabel(self.sizes, self.attrColors)
		self.spectrum = QTangoSpectrumBase(self.sizes, self.attrColors)
		
		self.layout = QtGui.QHBoxLayout(self)
		self.layout.setContentsMargins(0,0,0,0)
		self.layout.setMargin(int(self.sizes.barHeight/10))
#		self.layout.setMargin(0)
		self.layout.setSpacing(self.sizes.barHeight/3)
		
		self.layoutGrid = QtGui.QGridLayout()
		self.layoutGrid.setContentsMargins(0, 0, 0, 0)
		self.layoutGrid.setMargin(0)
		self.layoutGrid.addWidget(self.nameLabel, 0, 0)
		self.layoutGrid.addWidget(self.spectrum, 1, 0, 1, 2)
		self.layoutGrid.setHorizontalSpacing(self.sizes.barHeight/4)
		self.layoutGrid.setVerticalSpacing(0)

		self.layout.addWidget(self.startLabel)
		self.layout.addLayout(self.layoutGrid)		
		self.layout.addWidget(self.endLabel)
		
#		self.setMaximumWidth(self.sizes.readAttributeWidth)
		self.setMinimumWidth(self.sizes.readAttributeWidth)
#		self.setMaximumHeight(self.sizes.barHeight*6)
		self.setMinimumHeight(self.sizes.barHeight*6)
		self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)		

	def attributeName(self):
		return str(self.nameLabel.text())

	@QtCore.pyqtSignature('setAttributeName(QString)')

	def setAttributeName(self, aName):
		self.nameLabel.setText(aName)
		self.update()
		
	def setSpectrum(self, xData, yData):
		self.spectrum.setSpectrum(xData, yData)
				
	def setXRange(self, low, high):
		self.spectrum.setXRange(low, high)
		
class QTangoWriteAttributeSlider(QtGui.QWidget):
	def __init__(self, sizes = None, colors = None, parent=None):
		QtGui.QWidget.__init__(self, parent)
		if colors == None:
			self.attrColors = QTangoColors()
		else:
			self.attrColors = colors
		if sizes == None:
			self.sizes = QTangoSizes()
		else:
			self.sizes = sizes		
		self.setupLayout()
		
	def setupLayout(self):
		readValueWidth = self.sizes.barWidth
		readWidth = self.sizes.readAttributeWidth-self.sizes.barHeight/6-self.sizes.barHeight/2		

		self.startLabel = QTangoStartLabel(self.sizes, self.attrColors)
		self.endLabel = QTangoEndLabel(self.sizes, self.attrColors)
		self.nameLabel = QTangoAttributeNameLabel(self.sizes, self.attrColors)
		self.valueSpinbox = QTangoReadAttributeSpinBox(self.sizes, self.attrColors)
		self.valueSlider = QTangoHSliderBase(self.sizes, self.attrColors)
		self.writeValueSpinbox = QTangoWriteAttributeSpinBox(self.sizes, self.attrColors)
		self.writeValueSpinbox.editingFinished.connect(self.editingFinished)		

		self.layout = QtGui.QHBoxLayout(self)
		self.layout.setContentsMargins(0,0,0,0)
		self.layout.setMargin(int(self.sizes.barHeight/10))
		self.layout.setSpacing(self.sizes.barHeight/3)		

		self.layoutGrid = QtGui.QGridLayout()
		self.layoutGrid.setContentsMargins(0, 0, 0, 0)
		self.layoutGrid.setMargin(int(self.sizes.barHeight/10))
		self.layoutGrid.setMargin(0)
		self.layoutGrid.setHorizontalSpacing(self.sizes.barHeight/4)
		self.layoutGrid.setVerticalSpacing(0)		
		self.layoutGrid.addWidget(self.nameLabel, 0, 0, )
		self.layoutGrid.addWidget(self.valueSlider, 1, 0)
		self.layoutGrid.addWidget(self.valueSpinbox, 0, 1)
		self.layoutGrid.addWidget(self.writeValueSpinbox, 1, 1)

		self.layout.addWidget(self.startLabel)		
		self.layout.addLayout(self.layoutGrid)		
		self.layout.addWidget(self.endLabel)
		
		self.setMaximumWidth(self.sizes.readAttributeWidth)
		self.setMinimumWidth(self.sizes.readAttributeWidth)
		self.setMaximumHeight(self.sizes.barHeight*2.2)
		#self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
		self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)

	def attributeName(self):
		return str(self.nameLabel.text())

	@QtCore.pyqtSignature('setAttributeName(QString)')

	def setAttributeName(self, aName):
		self.nameLabel.setText(aName)
		self.update()
		
	def setAttributeValue(self, data):
		if type(data) == pt._PyTango.DeviceAttribute:
			self.valueSpinbox.setValue(data.value)
			self.valueSlider.setValue(data.value)
			if data.w_value != self.writeValueSpinbox.value():
				self.writeValueSpinbox.setColors('primaryColor0', 'secondaryColor1')
			else:
				self.writeValueSpinbox.setColors('secondaryColor0', 'backgroundColor')
		else:
			self.valueSpinbox.setValue(data)
			self.valueSlider.setValue(data)
		self.update()
		
	def setAttributeWriteValue(self, value):
		self.writeValueSpinbox.setValue(value)
		self.valueSlider.setWriteValue(value)
		self.update()
		
	def setAttributeWarningLimits(self, warnLow, warnHigh):
		self.valueSlider.setWarningLimits(warnLow, warnHigh)
		
	def setSliderLimits(self, min, max):
		self.valueSlider.setSliderLimits(min, max)
		
	def editingFinished(self):
		self.valueSlider.setWriteValue(self.writeValueSpinbox.value())
		self.update()
		print 'updating slider to ', self.writeValueSpinbox.value()

	def getWriteValue(self):
		return self.writeValueSpinbox.value()

class QTangoWriteAttributeDouble(QtGui.QWidget):
	def __init__(self, sizes = None, colors = None, parent=None):
		QtGui.QWidget.__init__(self, parent)
		self.attrColors = QTangoColors()
		if colors == None:
			self.attrColors = QTangoColors()
		else:
			self.attrColors = colors
		if sizes == None:
			self.sizes = QTangoSizes()
		else:
			self.sizes = sizes		
		self.setupLayout()
		
	def setupLayout(self):
		readValueWidth = self.sizes.barWidth
		readWidth = self.sizes.readAttributeWidth-int(self.sizes.barHeight/6)-readValueWidth
		print 'writeAttr readwidth:', readWidth
		writeValueWidth = self.sizes.writeAttributeWidth-self.sizes.readAttributeWidth-int(self.sizes.barHeight/6)-int(self.sizes.barHeight/2)
		
		self.startLabel = QtGui.QLabel('')
		st = ''.join(('QLabel {min-height: ', str(self.sizes.barHeight), 'px; \n',
					'min-width: ', str(int(self.sizes.barHeight / 6)), 'px; \n',
					'max-width: ', str(int(self.sizes.barHeight / 6)), 'px; \n',
					'max-height: ', str(self.sizes.barHeight), 'px; \n',
					'background-color: ', self.attrColors.secondaryColor0, ';}'))
		self.startLabel.setStyleSheet(st)
		self.middleLabel = QtGui.QLabel('')
		st = ''.join(('QLabel {min-height: ', str(self.sizes.barHeight), 'px; \n',
					'min-width: ', str(int(self.sizes.barHeight / 6)), 'px; \n',
					'max-width: ', str(int(self.sizes.barHeight / 6)), 'px; \n',
					'max-height: ', str(self.sizes.barHeight), 'px; \n',
					'background-color: ', self.attrColors.secondaryColor0, ';}'))
		self.middleLabel.setStyleSheet(st)
		self.endLabel = QtGui.QLabel('')
		st = ''.join(('QLabel {min-height: ', str(self.sizes.barHeight), 'px; \n',
					'min-width: ', str(int(self.sizes.barHeight / 2)), 'px; \n',
					'max-width: ', str(int(self.sizes.barHeight / 2)), 'px; \n',
					'max-height: ', str(self.sizes.barHeight), 'px; \n',
					'background-color: ', self.attrColors.secondaryColor0, ';}'))
		self.endLabel.setStyleSheet(st)

		self.nameLabel = QtGui.QLabel('Test')
		s = ''.join(('QLabel {min-height: ', str(self.sizes.barHeight), 'px; \n',
					'max-height: ', str(self.sizes.barHeight), 'px; \n',
					'min-width: ', str(readWidth), 'px; \n',
					'max-width: ', str(readWidth), 'px; \n',
					'background-color: ', self.attrColors.backgroundColor, '; \n',
					'color: ', self.attrColors.secondaryColor0, ';}'))
		self.nameLabel.setStyleSheet(s)
	
		font = self.nameLabel.font()
		font.setFamily(self.sizes.fontType)
		font.setStretch(self.sizes.fontStretch)
		font.setWeight(self.sizes.fontWeight)
		font.setPointSize(int(self.sizes.barHeight * 0.7))
		font.setStyleStrategy(QtGui.QFont.PreferAntialias)
#		font.setPointSize(int(self.sizes.fontSize))
		self.nameLabel.setFont(font)
		self.nameLabel.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
		self.nameLabel.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)

		self.readValueSpinbox = QtGui.QDoubleSpinBox()
		s = ''.join(('QDoubleSpinBox { \n',
            'background-color: ', self.attrColors.backgroundColor, '; \n',
            'border-width: 0px; \n',
            'border-color: #339; \n',
            'border-style: solid; \n',
            'border-radius: 0; \n',
            'border: 0px; \n',
            'padding: 0px; \n',
            'margin: 0px; \n',
            'qproperty-buttonSymbols: NoButtons; \n',
            'min-width: ', str(int(readValueWidth)), 'px; \n',
			'max-width: ', str(int(readValueWidth)), 'px; \n',
            'min-height: ', str(self.sizes.barHeight), 'px; \n',
            'max-height: ', str(self.sizes.barHeight), 'px; \n',
            'qproperty-readOnly: 1; \n',
            'color: ', self.attrColors.secondaryColor0, ';} \n'))
		font = self.readValueSpinbox.font()
		font.setFamily(self.sizes.fontType)
		font.setStretch(self.sizes.fontStretch)
		font.setWeight(self.sizes.fontWeight)
		font.setPointSize(int(self.sizes.barHeight * 0.7))
		font.setStyleStrategy(QtGui.QFont.PreferAntialias)
		self.readValueSpinbox.setFont(font)
		self.readValueSpinbox.setStyleSheet(s)
		self.readValueSpinbox.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
		self.readValueSpinbox.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

		self.writeValueSpinbox = QtGui.QDoubleSpinBox()
		s = ''.join(('QDoubleSpinBox { \n',
            'background-color: ', self.attrColors.backgroundColor, '; \n',
            'border-width: 0px; \n',
            'border-color: #339; \n',
            'border-style: solid; \n',
            'border-radius: 0; \n',
            'border: 0px; \n',
            'padding: 0px; \n',
            'margin: 0px; \n',
            'qproperty-buttonSymbols: NoButtons; \n',
            'min-width: ', str(self.sizes.barWidth), 'px; \n',
            'min-height: ', str(self.sizes.barHeight), 'px; \n',
            'max-height: ', str(self.sizes.barHeight), 'px; \n',
            'qproperty-readOnly: 0; \n',
            'color: ', self.attrColors.secondaryColor0, ';} \n'))
		font = self.writeValueSpinbox.font()
		font.setFamily(self.sizes.fontType)
		font.setStretch(self.sizes.fontStretch)
		font.setWeight(self.sizes.fontWeight)
		font.setPointSize(int(self.sizes.barHeight * 0.7))
		font.setStyleStrategy(QtGui.QFont.PreferAntialias)
		self.writeValueSpinbox.setFont(font)
		self.writeValueSpinbox.setStyleSheet(s)
		self.writeValueSpinbox.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Minimum)
		self.writeValueSpinbox.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)


		spacerItem = QtGui.QSpacerItem(0, 0, QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Minimum)

		layout = QtGui.QHBoxLayout(self)
		layout.setContentsMargins(0,0,0,0)
		layout.setMargin(int(self.sizes.barHeight/10))
		
#		layout.addSpacerItem(spacerItem)		
		layout.addWidget(self.startLabel)
		layout.addWidget(self.nameLabel)
		layout.addWidget(self.readValueSpinbox)
		layout.addWidget(self.middleLabel)
		layout.addWidget(self.writeValueSpinbox)
		layout.addWidget(self.endLabel)
		
		self.setMaximumWidth(self.sizes.writeAttributeWidth)
		self.setMinimumWidth(self.sizes.writeAttributeWidth)
		self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
		

	def attributeName(self):
		return str(self.nameLabel.text())

	@QtCore.pyqtSignature('setAttributeName(QString)')

	def setAttributeName(self, aName):
		self.nameLabel.setText(aName)
		self.update()
		
	def setAttributeValue(self, value):
		self.readValueSpinbox.setValue(value)
		self.update()

	def getWriteValue(self):
		return self.writeValueSpinbox.value()
	
		
class QTangoDeviceStatus(QtGui.QWidget):
	def __init__(self, parent=None):
		QtGui.QWidget.__init__(self, parent)
		self.startLabel = QtGui.QLabel('')
		st = ''.join(('QLabel {min-height: ', str(barHeight * 3), 'px; \n',
					'min-width: ', str(int(barHeight / 6)), 'px; \n',
					'max-width: ', str(int(barHeight / 6)), 'px; \n',
					'max-height: ', str(barHeight * 3), 'px; \n',
					'background-color: ', secondaryColor0, ';}'))
		self.startLabel.setStyleSheet(st)
		self.endLabel = QtGui.QLabel('')
		st = ''.join(('QLabel {min-height: ', str(barHeight * 3), 'px; \n',
					'min-width: ', str(int(barHeight / 2)), 'px; \n',
					'max-width: ', str(int(barHeight / 2)), 'px; \n',
					'max-height: ', str(barHeight * 3), 'px; \n',
					'background-color: ', secondaryColor0, ';}'))
		self.endLabel.setStyleSheet(st)

		self.nameLabel = QtGui.QLabel('Status:')
		s = ''.join(('QLabel {min-height: ', str(barHeight), 'px; \n',
					'max-height: ', str(barHeight), 'px; \n',
					'background-color: ', backgroundColor, '; \n',
					'color: ', secondaryColor0, ';}'))
		self.nameLabel.setStyleSheet(s)
		font = self.nameLabel.font()
		font.setFamily('TrebuchetMS')
		font.setStretch(QtGui.QFont.Condensed)
		font.setPointSize(int(barHeight * 0.7))
		font.setStyleStrategy(QtGui.QFont.PreferAntialias)
		self.nameLabel.setFont(font)
		self.nameLabel.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

		self.stateLabel = QtGui.QLabel('')
		s = ''.join(('QLabel {min-height: ', str(barHeight), 'px; \n',
					'max-height: ', str(barHeight), 'px; \n',
					'background-color: ', backgroundColor, '; \n',
					'color: ', secondaryColor0, ';}'))
		self.stateLabel.setStyleSheet(s)
		font = self.stateLabel.font()
		font.setFamily('TrebuchetMS')
		font.setStretch(QtGui.QFont.Condensed)
		font.setPointSize(int(barHeight * 0.7))
		self.stateLabel.setFont(font)
		self.stateLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTop)

		self.statusLabel = QtGui.QLabel('')
		s = ''.join(('QLabel {min-height: ', str(barHeight*2), 'px; \n',
					'max-height: ', str(barHeight*2), 'px; \n',
					'background-color: ', backgroundColor, '; \n',
					'color: ', secondaryColor0, ';}'))
		self.statusLabel.setStyleSheet(s)			
	
		font = self.statusLabel.font()
		font.setFamily('TrebuchetMS')
		font.setStretch(QtGui.QFont.Condensed)
		font.setPointSize(int(barHeight * 0.4))
		self.statusLabel.setFont(font)
		self.statusLabel.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)

		spacerItem = QtGui.QSpacerItem(0, 0, QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Minimum)
				
		layout = QtGui.QHBoxLayout(self)
		layout.setContentsMargins(0, 0, 0, 0)
		layout.setMargin(int(barHeight/10))
		layoutTop = QtGui.QHBoxLayout()
		layoutTop.setContentsMargins(0, 0, 0, 0)
		layoutTop.setMargin(int(barHeight/10))
		layout2 = QtGui.QVBoxLayout()
		layout2.setMargin(0)
		layout2.setSpacing(0)
		layout2.setContentsMargins(0, 0, 0, 3)
#		layout.addSpacerItem(spacerItem)		
		layout.addWidget(self.startLabel)
		layout.addLayout(layout2)
		layout2.addLayout(layoutTop)
		layoutTop.addWidget(self.nameLabel)
		layoutTop.addWidget(self.stateLabel)
		layout2.addWidget(self.statusLabel)
		layout.addWidget(self.endLabel)

	def statusText(self):
		return str(self.statusLabel.text())

	@QtCore.pyqtSignature('setAttributeName(QString)')

	def setStatusText(self, aName):
		self.statusLabel.setText(aName)
		self.update()
		
	def setStatus(self,state,status):
		if state == pt.DevState.OFF:
			color = offColor
			stateString = 'OFF'
		elif state == pt.DevState.ON:
			color = onColor
			stateString = 'ON'
		elif state == pt.DevState.FAULT:
			color = faultColor
			stateString = 'FAULT'
		elif state == pt.DevState.ALARM:
			color = alarmColor
			stateString = 'ALARM'
		elif state == pt.DevState.STANDBY:
			color = standbyColor
			stateString = 'STANDBY'
		elif state == pt.DevState.UNKNOWN:
			color = unknownColor
			stateString = 'UNKNOWN'
		elif state == pt.DevState.DISABLE:
			color = disableColor
			stateString = 'DISABLE'
		s = ''.join(('QLabel {min-height: ', str(barHeight * 3), 'px; \n',
					'min-width: ', str(int(barHeight / 6)), 'px; \n',
					'max-width: ', str(int(barHeight / 6)), 'px; \n',
					'max-height: ', str(barHeight * 3), 'px; \n',
					'background-color: ', color, ';}'))
		self.startLabel.setStyleSheet(s)
		s = ''.join(('QLabel {min-height: ', str(barHeight * 3), 'px; \n',
					'min-width: ', str(int(barHeight / 2)), 'px; \n',
					'max-width: ', str(int(barHeight / 2)), 'px; \n',
					'max-height: ', str(barHeight * 3), 'px; \n',
					'background-color: ', color, ';}'))
		self.endLabel.setStyleSheet(s)
		s = ''.join(('QLabel {min-height: ', str(barHeight), 'px; \n',
					'max-height: ', str(barHeight), 'px; \n',
					'background-color: ', backgroundColor, '; \n',
					'color: ', color, ';}'))
		self.nameLabel.setStyleSheet(s)
		self.stateLabel.setStyleSheet(s)
		s = ''.join(('QLabel {min-height: ', str(barHeight*2), 'px; \n',
					'max-height: ', str(barHeight*2), 'px; \n',
					'background-color: ', backgroundColor, '; \n',
					'color: ', color, ';}'))
		self.statusLabel.setStyleSheet(s)			
		
		self.stateLabel.setText(stateString)
		self.statusLabel.setText(status)
		
		self.update()

class QTangoDeviceNameStatus(QtGui.QWidget):
	def __init__(self, sizes = None, colors = None, parent=None):
		QtGui.QWidget.__init__(self, parent)
		
		self.attrColors = QTangoColors()
		if colors == None:
			self.attrColors = QTangoColors()
		else:
			self.attrColors = colors
		if sizes == None:
			self.sizes = QTangoSizes()
		else:
			self.sizes = sizes		
		self.setupLayout()		
		
	def setupLayout(self):
		self.startLabel = QtGui.QLabel('')
		st = ''.join(('QLabel {min-height: ', str(self.sizes.barHeight), 'px; \n',
					'min-width: ', str(int(self.sizes.barHeight / 6)), 'px; \n',
					'max-width: ', str(int(self.sizes.barHeight / 6)), 'px; \n',
					'max-height: ', str(self.sizes.barHeight), 'px; \n',
					'background-color: ', self.attrColors.secondaryColor0, ';}'))
		self.startLabel.setStyleSheet(st)
		self.endLabel = QtGui.QLabel('')
		st = ''.join(('QLabel {min-height: ', str(self.sizes.barHeight), 'px; \n',
					'min-width: ', str(int(self.sizes.barHeight / 2)), 'px; \n',
					'max-width: ', str(int(self.sizes.barHeight / 2)), 'px; \n',
					'max-height: ', str(self.sizes.barHeight), 'px; \n',
					'background-color: ', self.attrColors.secondaryColor0, ';}'))
		self.endLabel.setStyleSheet(st)

		self.nameLabel = QtGui.QLabel('Test')
		s = ''.join(('QLabel {min-height: ', str(self.sizes.barHeight), 'px; \n',
					'max-height: ', str(self.sizes.barHeight), 'px; \n',
					'background-color: ', self.attrColors.backgroundColor, '; \n',
					'color: ', self.attrColors.secondaryColor0, ';}'))
		self.nameLabel.setStyleSheet(s)
	
		font = self.nameLabel.font()
		font.setFamily(self.sizes.fontType)
		font.setStretch(self.sizes.fontStretch)
		font.setPointSize(int(self.sizes.barHeight * 0.7))
		font.setStyleStrategy(QtGui.QFont.PreferAntialias)
		self.nameLabel.setFont(font)
		self.nameLabel.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)		


		layout = QtGui.QHBoxLayout(self)
		layout.setContentsMargins(0,0,0,0)
		layout.setMargin(int(self.sizes.barHeight/10))
		
#		layout.addSpacerItem(spacerItem)		
		layout.addWidget(self.startLabel)
		layout.addWidget(self.nameLabel)
		layout.addWidget(self.endLabel)
		
		self.setMaximumWidth(self.sizes.readAttributeWidth)
		self.setMinimumWidth(self.sizes.readAttributeWidth)
		self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)		
		
	def attributeName(self):
		return str(self.nameLabel.text())

	@QtCore.pyqtSignature('setAttributeName(QString)')

	def setAttributeName(self, aName):
		self.nameLabel.setText(aName)
		self.update()
				
	def setState(self, state):
		state_str = str(state)
		if state_str == str(pt.DevState.OFF):
			color = self.attrColors.offColor
			stateString = 'OFF'
		elif state_str == str(pt.DevState.ON):
			color = self.attrColors.onColor
			stateString = 'ON'
		elif state_str == str(pt.DevState.FAULT):
			color = self.attrColors.faultColor
			stateString = 'FAULT'
		elif state_str == str(pt.DevState.ALARM):
			color = self.attrColors.alarmColor
			stateString = 'ALARM'
		elif state_str == str(pt.DevState.STANDBY):
			color = self.attrColors.standbyColor
			stateString = 'STANDBY'
		elif state_str == str(pt.DevState.UNKNOWN):
			color = self.attrColors.unknownColor
			stateString = 'UNKNOWN'
		elif state_str == str(pt.DevState.DISABLE):
			color = self.attrColors.disableColor
			stateString = 'DISABLE'
		else:
			color = self.attrColors.unknownColor
			stateString = 'UNKNOWN'
		s = ''.join(('QLabel {min-height: ', str(self.sizes.barHeight), 'px; \n',
					'min-width: ', str(int(self.sizes.barHeight / 6)), 'px; \n',
					'max-width: ', str(int(self.sizes.barHeight / 6)), 'px; \n',
					'max-height: ', str(self.sizes.barHeight), 'px; \n',
					'background-color: ', color, ';}'))
		self.startLabel.setStyleSheet(s)
		s = ''.join(('QLabel {min-height: ', str(self.sizes.barHeight), 'px; \n',
					'min-width: ', str(int(self.sizes.barHeight / 2)), 'px; \n',
					'max-width: ', str(int(self.sizes.barHeight / 2)), 'px; \n',
					'max-height: ', str(self.sizes.barHeight), 'px; \n',
					'background-color: ', color, ';}'))
		self.endLabel.setStyleSheet(s)
		s = ''.join(('QLabel {min-height: ', str(self.sizes.barHeight), 'px; \n',
					'max-height: ', str(self.sizes.barHeight), 'px; \n',
					'background-color: ', self.attrColors.backgroundColor, '; \n',
					'color: ', color, ';}'))
		self.nameLabel.setStyleSheet(s)
		
		self.update()
