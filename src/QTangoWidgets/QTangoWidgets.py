# -*- coding:utf-8 -*-
"""
Created on Feb 14, 2013

@author: Filip
"""
from PyQt4 import QtGui, QtCore, Qt
import numpy as np
import sys
import PyTango as pt
from collections import OrderedDict

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

class QTangoColors():
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
		self.onColor = '#99dd66'
		self.offColor = '#ffffff'
		self.standbyColor = '#9c9cff'
		self.unknownColor = '#45616f'
		self.disableColor = '#ff00ff'

class QTangoSizes():
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
		
		self.nameLabel.setText(self.title)
		font = self.nameLabel.font()
		font.setFamily('TrebuchetMS')
		font.setStretch(QtGui.QFont.Condensed)
		font.setPointSize(int(barHeight * 1.15))
		font.setStyleStrategy(QtGui.QFont.PreferAntialias)
		self.nameLabel.setFont(font)
		
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

			self.startLabel = QtGui.QLabel('')
			st = ''.join(('QLabel {min-height: ', str(self.sizes.barHeight), 'px; \n',
						'min-width: ', str(int(self.sizes.barHeight / 6)), 'px; \n',
						'max-width: ', str(int(self.sizes.barHeight / 6)), 'px; \n',
	#					'max-height: ', str(self.sizes.barHeight), 'px; \n',
						'background-color: ', self.attrColors.secondaryColor0, ';}'))
			self.startLabel.setStyleSheet(st)
			self.endLabel = QtGui.QLabel('')
			st = ''.join(('QLabel {min-height: ', str(self.sizes.barHeight), 'px; \n',
						'min-width: ', str(int(self.sizes.barHeight / 2)), 'px; \n',
						'max-width: ', str(int(self.sizes.barHeight / 2)), 'px; \n',
	#					'max-height: ', str(self.sizes.barHeight), 'px; \n',
						'background-color: ', self.attrColors.secondaryColor0, ';}'))
			self.endLabel.setStyleSheet(st)
	
			self.nameLabel = QtGui.QLabel(self.title)
			s = ''.join(('QLabel {min-height: ', str(self.sizes.barHeight), 'px; \n',
						'max-height: ', str(self.sizes.barHeight), 'px; \n',
						'background-color: ', self.attrColors.backgroundColor, '; \n',
						'color: ', self.attrColors.secondaryColor0, ';}'))
			self.nameLabel.setStyleSheet(s)
		
			font = self.nameLabel.font()
			font.setFamily(self.sizes.fontType)
			font.setStretch(self.sizes.fontStretch)
			font.setPointSize(int(self.sizes.barHeight * 0.75))
			font.setStyleStrategy(QtGui.QFont.PreferAntialias)
			self.nameLabel.setFont(font)
			self.nameLabel.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)		
			self.nameLabel.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)		
	
			self.statusLabel = QtGui.QLabel('Status')
			s = ''.join(('QLabel {min-height: ', str(self.sizes.barHeight), 'px; \n',
						'max-height: ', str(self.sizes.barHeight), 'px; \n',
						'background-color: ', self.attrColors.backgroundColor, '; \n',
						'color: ', self.attrColors.secondaryColor0, ';}'))
			self.statusLabel.setStyleSheet(s)
		
			font = self.statusLabel.font()
			font.setFamily(self.sizes.fontType)
			font.setStretch(self.sizes.fontStretch)
			font.setPointSize(int(self.sizes.barHeight * 0.75))
			font.setStyleStrategy(QtGui.QFont.PreferAntialias)
			self.statusLabel.setFont(font)
			self.statusLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
			self.statusLabel.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)		
	
			self.layout = QtGui.QHBoxLayout(self)
			self.layout.setContentsMargins(0,0,0,0)
			self.layout.setMargin(int(self.sizes.barHeight/10))
			
			self.layout2 = QtGui.QVBoxLayout()
			self.layout2.setContentsMargins(0,0,0,0)
			self.layout2.setMargin(int(self.sizes.barHeight/10))			
			
			self.layoutInfo = QtGui.QHBoxLayout()
			self.layoutInfo.setContentsMargins(0,0,0,0)
			self.layoutInfo.setMargin(int(self.sizes.barHeight/10))
			self.layoutInfo.setMargin(0)
			self.layoutInfo.setSpacing(int(self.sizes.barHeight / 2))
			self.layoutInfo.addWidget(self.nameLabel)		
			self.layoutInfo.addWidget(self.statusLabel)
			self.layoutButtons = QtGui.QHBoxLayout()
			self.layoutButtons.setContentsMargins(0,0,0,0)
			self.layoutButtons.setMargin(int(self.sizes.barHeight/10))
			self.layoutButtons.setMargin(0)
			self.layoutButtons.setSpacing(int(self.sizes.barHeight / 2))
			self.layout2.addLayout(self.layoutInfo)		
			self.layout2.addLayout(self.layoutButtons)
			
			self.layout.addWidget(self.startLabel)		
			self.layout.addLayout(self.layout2)		
			self.layout.addWidget(self.endLabel)


# Clear out old layout
		if self.cmdButtons.keys().__len__() > 0:
			for i in reversed(range(self.layoutButtons.count())): 
				self.layoutButtons.itemAt(i).widget().setParent(None)

# Add buttons	
		for cmdButton in self.cmdButtons.itervalues():
			self.layoutButtons.addWidget(cmdButton)		
#		self.layoutButtons.setSpacing(int(self.sizes.barHeight / 10))
		
		
		self.update()
		
		self.setMaximumWidth(self.sizes.readAttributeWidth)
		self.setMinimumWidth(self.sizes.readAttributeWidth)
		self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
		
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
		font.setPointSize(int(buttonHeight  * 0.4))	
		font.setStyleStrategy(QtGui.QFont.PreferAntialias)	
		cmdButton.setFont(font)
		
		if slot != None:
			cmdButton.clicked.connect(slot)
		
		self.cmdButtons[name] = cmdButton	
		
		self.setupLayout()	
		

		
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

		self.valueSlider = QtGui.QSlider()

		self.layout = QtGui.QHBoxLayout(self)
		self.layout.setContentsMargins(0,0,0,0)
		self.layout.setMargin(int(self.sizes.barHeight/10))
		
		self.layout2 = QtGui.QVBoxLayout()
		self.layout2.setContentsMargins(0,0,0,0)
		self.layout2.setMargin(int(self.sizes.barHeight/10))			
		
		self.layoutInfo = QtGui.QHBoxLayout()
		self.layoutInfo.setContentsMargins(0,0,0,0)
		self.layoutInfo.setMargin(int(self.sizes.barHeight/10))
		self.layoutInfo.setMargin(0)
		self.layoutInfo.setSpacing(int(self.sizes.barHeight / 2))
		self.layoutInfo.addWidget(self.nameLabel)		
		self.layout2.addLayout(self.layoutInfo)		
		self.layout2.addWidget(self.valueSlider)
		self.layout.addWidget(self.startLabel)		
		self.layout.addLayout(self.layout2)		
		self.layout.addWidget(self.endLabel)
		
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
		font.setPointSize(int(self.sizes.barHeight * 0.75))
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
