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
import copy

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
#		self.alarmColor = '#f7bd5a'
		self.warnColor = '#a35918'
		self.alarmColor = '#ff0000'
#		self.warnColor = '#cb99cc'
		self.onColor = '#99dd66'
		self.offColor = '#ffffff'
		self.standbyColor = '#9c9cff'
		self.unknownColor = '#45616f'
		self.disableColor = '#ff00ff'
		self.movingColor = '#feff99'

		self.validColor = self.secondaryColor0
		self.invalidColor = self.unknownColor
		self.changingColor = self.secondaryColor1

class QTangoSizes(object):
	def __init__(self):
		self.barHeight = 30
		self.barWidth = 20
		self.readAttributeWidth = 200
		self.readAttributeHeight = 200
		self.writeAttributeWidth = 280
		self.trendWidth = 100
		self.fontSize = 12
		self.fontType = 'Calibri'
		self.fontStretch = 75
		self.fontWeight = 50

barHeight = 30
barWidth = 90

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

		self.state = 'UNKNOWN'
		self.quality = 'UNKNOWN'
		self.currentAttrColor = self.attrColors.secondaryColor0
		self.currentAttrColor = self.attrColors.unknownColor

		self.attrInfo = None

	def setState(self, state):
		if type(state) == pt.DeviceAttribute:
			state_str = str(state.value)
		else:
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
		elif state_str == str(pt.DevState.MOVING):
			color = self.attrColors.movingColor
			stateString = 'MOVING'
		else:
			color = self.attrColors.unknownColor
			stateString = 'UNKNOWN'

		self.state = stateString
		self.currentAttrColor = color

		s = str(self.styleSheet())
		if s != '':
			i0 = s.find('\ncolor')
			i1 = s[i0:].find(':')
			i2 = s[i0:].find(';')
			sNew = ''.join((s[0:i0+i1+1],' ', color, s[i0+i2:]))
			self.setStyleSheet(sNew)

		self.update()

	def setQuality(self, quality):
		if type(quality) == pt.DeviceAttribute:
			state_str = str(quality.value)
		else:
			state_str = str(quality)
		if state_str == str(pt.AttrQuality.ATTR_VALID):
			color = self.attrColors.validColor
			stateString = 'VALID'
		elif state_str == str(pt.AttrQuality.ATTR_INVALID):
			color = self.attrColors.invalidColor
			stateString = 'INVALID'
		elif state_str == str(pt.AttrQuality.ATTR_ALARM):
			color = self.attrColors.alarmColor
			stateString = 'ALARM'
		elif state_str == str(pt.AttrQuality.ATTR_WARNING):
			color = self.attrColors.warnColor
			stateString = 'WARNING'
		elif state_str == str(pt.AttrQuality.ATTR_CHANGING):
			color = self.attrColors.changingColor
			stateString = 'CHANGING'
		else:
			color = self.attrColors.unknownColor
			stateString = 'UNKNOWN'

		self.quality = stateString
		self.currentAttrColor = color

#		print 'Quality: ', self.quality, self.currentAttrColor

		s = str(self.styleSheet())
		if s != '':
			i0 = s.find('\ncolor')
			i1 = s[i0:].find(':')
			i2 = s[i0:].find(';')
			sNew = ''.join((s[0:i0+i1+1],' ', color, s[i0+i2:]))
			self.setStyleSheet(sNew)


		self.update()

	def setupLayout(self):
		pass

	def configureAttribute(self, attrInfo):
		self.attrInfo = attrInfo


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

		self.startLabel.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)

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
#		self.layout.addStretch()
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

class QTangoCommandButton(QtGui.QPushButton, QTangoAttributeBase):
	def __init__(self, title, slot = None, sizes = None, colors = None, parent=None):
		QTangoAttributeBase.__init__(self, sizes, colors, parent)
		QtGui.QPushButton.__init__(self, parent)
		self.name = title

		if slot != None:
			self.clicked.connect(slot)

		self.setupLayout()

		#cmdButton = QtGui.QPushButton('CMD ')
	def setupLayout(self):
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
		self.setStyleSheet(s)

		self.setText(''.join((self.name, ' ')))
		font = self.font()
		font.setFamily(self.sizes.fontType)
		font.setStretch(self.sizes.fontStretch)#QtGui.QFont.Condensed)
#		font.setPointSize(int(buttonHeight  * 0.4))
		font.setPointSize(int(self.sizes.barHeight * 0.7))
		font.setStyleStrategy(QtGui.QFont.PreferAntialias)
		self.setFont(font)

	def setQuality(self, quality):
		if type(quality) == pt.DeviceAttribute:
			state_str = str(quality.value)
		else:
			state_str = str(quality)
		if state_str == str(pt.AttrQuality.ATTR_VALID):
			color = self.attrColors.validColor
			stateString = 'VALID'
		elif state_str == str(pt.AttrQuality.ATTR_INVALID):
			color = self.attrColors.invalidColor
			stateString = 'INVALID'
		elif state_str == str(pt.AttrQuality.ATTR_ALARM):
			color = self.attrColors.alarmColor
			stateString = 'ALARM'
		elif state_str == str(pt.AttrQuality.ATTR_WARNING):
			color = self.attrColors.warnColor
			stateString = 'WARNING'
		elif state_str == str(pt.AttrQuality.ATTR_CHANGING):
			color = self.attrColors.changingColor
			stateString = 'CHANGING'
		else:
			color = self.attrColors.unknownColor
			stateString = 'UNKNOWN'

		self.quality = stateString
		self.currentAttrColor = color

		buttonHeight = self.sizes.barHeight*1.75
		s = ''.join(('QPushButton {	background-color: ', self.currentAttrColor, '; \n',
					'color: ', self.attrColors.backgroundColor, '; \n',
					'min-height: ', str(int(buttonHeight)), 'px; \n',
					'max-height: ', str(int(buttonHeight)), 'px; \n',
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
		self.setStyleSheet(s)
		self.update()

class QTangoCommandSelection(QTangoAttributeBase):
	def __init__(self, title, sizes = None, colors = None, parent=None):
		QTangoAttributeBase.__init__(self, sizes, colors, parent)
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
			self.nameLabel.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
			self.nameLabel.setMinimumWidth(0)
			self.statusLabel = QTangoAttributeNameLabel(self.sizes, self.attrColors)
			self.statusLabel.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
			self.statusLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
			self.statusLabel.setText('')


			self.layout = QtGui.QHBoxLayout(self)
			self.layout.setContentsMargins(0,0,0,0)
#			self.layout.setMargin(int(self.sizes.barHeight/5))
			self.layout.setMargin(0)
#			self.layout.setSpacing(self.sizes.barHeight/3)
			self.layout.setSpacing(self.sizes.barWidth/3)

			self.layout2 = QtGui.QVBoxLayout()
			self.layout2.setContentsMargins(0,0,0,0)
#			self.layout2.setMargin(int(self.sizes.barHeight/5))
			self.layout2.setMargin(0)

			self.layoutInfo = QtGui.QHBoxLayout()
			self.layoutInfo.setContentsMargins(0,0,0,0)
#			self.layoutInfo.setMargin(int(self.sizes.barHeight/10))
			self.layoutInfo.setMargin(0)
			self.layoutInfo.setSpacing(int(self.sizes.barWidth / 6))
			self.layoutInfo.addWidget(self.nameLabel)
			self.layoutInfo.addWidget(self.statusLabel)
			self.layoutButtons = QtGui.QHBoxLayout()
			self.layoutButtons.setContentsMargins(0,0,0,0)
#			self.layoutButtons.setMargin(int(self.sizes.barHeight/10))
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

	def setStatus(self, status, state = None):
		if type(status) == pt.DeviceAttribute:
			self.startLabel.setQuality(status.quality)
			self.endLabel.setQuality(status.quality)
			self.nameLabel.setQuality(status.quality)
			self.statusLabel.setQuality(status.quality)
			for cmdButton in self.cmdButtons.itervalues():
				cmdButton.setQuality(status.quality)
			statusText = str(status.value)
		else:
			statusText = status
		if statusText != None:
			self.statusLabel.setText(statusText)
		else:
			self.statusLabel.setText('--')
		self.statusLabel.repaint()

#		self.update()

	def addCmdButton(self, name, slot):
# 		cmdButton = QtGui.QPushButton('CMD ')
# 		buttonHeight = self.sizes.barHeight*1.75
# 		s = ''.join(('QPushButton {	background-color: ', self.attrColors.secondaryColor0, '; \n',
# 					'color: ', self.attrColors.backgroundColor, '; \n',
# 					'min-height: ', str(int(buttonHeight)), 'px; \n',
# 					'max-height: ', str(int(buttonHeight)), 'px; \n',
# #					'min-width: ', str(int(self.sizes.barWidth)), 'px; \n',
# #					'max-width: ', str(int(self.sizes.barWidth)), 'px; \n',
# 					'padding-left: 5px; \n',
# 					'padding-right: 5px; \n',
# 					'border-width: 0px; \n',
# 					'border-style: solid; \n',
# 					'border-color: #339; \n',
# 					'border-radius: 0; \n',
# 					'border: 0px; \n',
# 					'text-align: right bottom;\n',
# 					'padding: 0px; \n',
# 					'margin: 0px; \n',
# 					'} \n',
# 					'QPushButton:hover{ background-color: ', self.attrColors.secondaryColor1, ';} \n',
# 					'QPushButton:hover:pressed{ background-color: ', self.attrColors.secondaryColor2, ';} \n'))
# 		cmdButton.setStyleSheet(s)
#
# 		cmdButton.setText(''.join((name, ' ')))
# 		font = cmdButton.font()
# 		font.setFamily(self.sizes.fontType)
# 		font.setStretch(self.sizes.fontStretch)#QtGui.QFont.Condensed)
# #		font.setPointSize(int(buttonHeight  * 0.4))
# 		font.setPointSize(int(self.sizes.barHeight * 0.7))
# 		font.setStyleStrategy(QtGui.QFont.PreferAntialias)
# 		cmdButton.setFont(font)
		cmdButton = QTangoCommandButton(name, slot, self.sizes, self.attrColors)

# 		if slot != None:
# 			cmdButton.clicked.connect(slot)

		self.cmdButtons[name] = cmdButton

		self.setupLayout()


class QTangoStartLabel(QtGui.QLabel, QTangoAttributeBase):
	def __init__(self, sizes = None, colors = None, parent=None):
		QTangoAttributeBase.__init__(self, sizes, colors, parent)
		QtGui.QLabel.__init__(self, parent)
		self.setupLayout()

	def setQuality(self, quality):
		state_str = str(quality)
		if state_str == str(pt.AttrQuality.ATTR_VALID):
			color = self.attrColors.validColor
			stateString = 'VALID'
		elif state_str == str(pt.AttrQuality.ATTR_INVALID):
			color = self.attrColors.invalidColor
			stateString = 'INVALID'
		elif state_str == str(pt.AttrQuality.ATTR_ALARM):
			color = self.attrColors.alarmColor
			stateString = 'ALARM'
		elif state_str == str(pt.AttrQuality.ATTR_WARNING):
			color = self.attrColors.warnColor
			stateString = 'WARNING'
		elif state_str == str(pt.AttrQuality.ATTR_CHANGING):
			color = self.attrColors.changingColor
			stateString = 'CHANGING'
		else:
			color = self.attrColors.unknownColor
			stateString = 'UNKNOWN'

		self.quality = stateString
		self.currentAttrColor = color

		s = str(self.styleSheet())
		if s != '':
			i0 = s.find('\nbackground-color')
			i1 = s[i0:].find(':')
			i2 = s[i0:].find(';')
			sNew = ''.join((s[0:i0+i1+1],' ', color, s[i0+i2:]))
			self.setStyleSheet(sNew)

		self.update()

	def setState(self, state):
		if type(state) == pt.DeviceAttribute:
			state_str = str(state.value)
		else:
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
		elif state_str == str(pt.DevState.MOVING):
			color = self.attrColors.movingColor
			stateString = 'MOVING'
		else:
			color = self.attrColors.unknownColor
			stateString = 'UNKNOWN'

		self.state = stateString
		self.currentAttrColor = color

		s = str(self.styleSheet())
		if s != '':
			i0 = s.find('\nbackground-color')
			i1 = s[i0:].find(':')
			i2 = s[i0:].find(';')
			sNew = ''.join((s[0:i0+i1+1],' ', color, s[i0+i2:]))
			self.setStyleSheet(sNew)

		self.update()


	def setupLayout(self):
		self.setText('')
		st = ''.join(('QLabel {min-height: ', str(self.sizes.barHeight), 'px; \n',
 					'min-width: ', str(int(self.sizes.barWidth / 3)), 'px; \n',
 					'max-width: ', str(int(self.sizes.barWidth / 3)), 'px; \n',
#					'min-width: 1 px; \n',
#					'max-width: 1 px; \n',
					'background-color: ', self.currentAttrColor, ';}'))
		self.setStyleSheet(st)

class QTangoBooleanLabel(QtGui.QLabel):
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
		st = ''.join(('QLabel {min-height: ', str(self.sizes.barHeight / 2), 'px; \n',
					'max-height: ', str(int(self.sizes.barHeight / 2)), 'px; \n',
					'min-width: ', str(int(self.sizes.barHeight / 2)), 'px; \n',
					'max-width: ', str(int(self.sizes.barHeight / 2)), 'px; \n',
					'border-width: 1px; \n',
					'border-color: ', self.attrColors.secondaryColor0, '; \n',
					'border-style: solid; \n',
					'border-radius: 0px; \n',
					'padding: 0px; \n',
					'margin: 0px; \n',
					'background-color: ', self.attrColors.backgroundColor, ';}'))
		self.setStyleSheet(st)

	def setBooleanState(self, boolState):
		if boolState == False:
			st = ''.join(('QLabel {min-height: ', str(self.sizes.barHeight / 2), 'px; \n',
						'max-height: ', str(int(self.sizes.barHeight / 2)), 'px; \n',
						'min-width: ', str(int(self.sizes.barHeight / 2)), 'px; \n',
						'max-width: ', str(int(self.sizes.barHeight / 2)), 'px; \n',
						'border-width: 1px; \n',
						'border-color: ', self.attrColors.secondaryColor0, '; \n',
						'border-style: solid; \n',
						'border-radius: 0px; \n',
						'padding: 0px; \n',
						'margin: 0px; \n',
						'background-color: ', self.attrColors.backgroundColor, ';}'))
		else:
			st = ''.join(('QLabel {min-height: ', str(self.sizes.barHeight / 2), 'px; \n',
						'max-height: ', str(int(self.sizes.barHeight / 2)), 'px; \n',
						'min-width: ', str(int(self.sizes.barHeight / 2)), 'px; \n',
						'max-width: ', str(int(self.sizes.barHeight / 2)), 'px; \n',
						'border-width: 1px; \n',
						'border-color: ', self.attrColors.secondaryColor0, '; \n',
						'border-style: solid; \n',
						'border-radius: 0px; \n',
						'padding: 0px; \n',
						'margin: 0px; \n',
						'background-color: ', self.attrColors.secondaryColor0, ';}'))
		self.setStyleSheet(st)

class QTangoEndLabel(QtGui.QLabel, QTangoAttributeBase):
	def __init__(self, sizes = None, colors = None, parent=None):
		QTangoAttributeBase.__init__(self, sizes, colors, parent)
		QtGui.QLabel.__init__(self, parent)
		self.setupLayout()

	def setQuality(self, quality):
		state_str = str(quality)
		if state_str == str(pt.AttrQuality.ATTR_VALID):
			color = self.attrColors.validColor
			stateString = 'VALID'
		elif state_str == str(pt.AttrQuality.ATTR_INVALID):
			color = self.attrColors.invalidColor
			stateString = 'INVALID'
		elif state_str == str(pt.AttrQuality.ATTR_ALARM):
			color = self.attrColors.alarmColor
			stateString = 'ALARM'
		elif state_str == str(pt.AttrQuality.ATTR_WARNING):
			color = self.attrColors.warnColor
			stateString = 'WARNING'
		elif state_str == str(pt.AttrQuality.ATTR_CHANGING):
			color = self.attrColors.changingColor
			stateString = 'CHANGING'
		else:
			color = self.attrColors.unknownColor
			stateString = 'UNKNOWN'

		self.quality = stateString
		self.currentAttrColor = color

		s = str(self.styleSheet())
		if s != '':
			i0 = s.find('\nbackground-color')
			i1 = s[i0:].find(':')
			i2 = s[i0:].find(';')
			sNew = ''.join((s[0:i0+i1+1],' ', color, s[i0+i2:]))
			self.setStyleSheet(sNew)

		self.update()

	def setState(self, state):
		if type(state) == pt.DeviceAttribute:
			state_str = str(state.value)
		else:
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
		elif state_str == str(pt.DevState.MOVING):
			color = self.attrColors.movingColor
			stateString = 'MOVING'
		else:
			color = self.attrColors.unknownColor
			stateString = 'UNKNOWN'

		self.state = stateString
		self.currentAttrColor = color

		s = str(self.styleSheet())
		if s != '':
			i0 = s.find('\nbackground-color')
			i1 = s[i0:].find(':')
			i2 = s[i0:].find(';')
			sNew = ''.join((s[0:i0+i1+1],' ', color, s[i0+i2:]))
			self.setStyleSheet(sNew)

		self.update()


	def setupLayout(self):
		st = ''.join(('QLabel {min-height: ', str(self.sizes.barHeight), 'px; \n',
 					'min-width: ', str(int(self.sizes.barWidth)), 'px; \n',
 					'max-width: ', str(int(self.sizes.barWidth)), 'px; \n',
					'background-color: ', self.currentAttrColor, ';}'))
		self.setStyleSheet(st)


class QTangoAttributeNameLabel(QtGui.QLabel, QTangoAttributeBase):
	def __init__(self, sizes = None, colors = None, parent=None):
		QTangoAttributeBase.__init__(self, sizes, colors, parent)
		QtGui.QLabel.__init__(self, parent)
		self.setupLayout()

	def setupLayout(self):
		self.setText('')
		s = ''.join(('QLabel {min-height: ', str(self.sizes.barHeight), 'px; \n',
					'max-height: ', str(self.sizes.barHeight), 'px; \n',
# 					'min-width: ', str(int(readWidth)), 'px; \n',
# 					'max-width: ', str(int(readWidth)), 'px; \n',
					'background-color: ', self.attrColors.backgroundColor, '; \n',
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
		self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)

class QTangoAttributeUnitLabel(QtGui.QLabel, QTangoAttributeBase):
	def __init__(self, sizes = None, colors = None, parent=None):
		QTangoAttributeBase.__init__(self, sizes, colors, parent)
		QtGui.QLabel.__init__(self, parent)
		self.setupLayout()

	def setupLayout(self):
		self.setText('')

		font = self.font()
		font.setFamily(self.sizes.fontType)
		font.setStretch(self.sizes.fontStretch)
		font.setWeight(self.sizes.fontWeight)
		font.setPointSize(int(self.sizes.barHeight * 0.7))
		font.setStyleStrategy(QtGui.QFont.PreferAntialias)
		self.setFont(font)
		self.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom)
		self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)

		unitWidth = QtGui.QFontMetricsF(font).width('mmmm')
		s = ''.join(('QLabel {min-height: ', str(self.sizes.barHeight), 'px; \n',
					'max-height: ', str(self.sizes.barHeight), 'px; \n',
# 					'min-width: ', str(int(unitWidth)), 'px; \n',
# 					'max-width: ', str(int(unitWidth)), 'px; \n',
					'background-color: ', self.attrColors.backgroundColor, '; \n',
					'color: ', self.attrColors.secondaryColor0, ';}'))
		self.setStyleSheet(s)

	def setText(self, unitText):
		if unitText == '':
			txt = '[a.u.]'
		else:
			txt=''.join(('[', unitText, ']'))
		QtGui.QLabel.setText(self, txt)

class QTangoReadAttributeSpinBox(QtGui.QDoubleSpinBox, QTangoAttributeBase):
	def __init__(self, sizes = None, colors = None, parent=None):
		QTangoAttributeBase.__init__(self, sizes, colors, parent)
		QtGui.QDoubleSpinBox.__init__(self, parent)
		self.setupLayout()

	def setupLayout(self):
		self.setLocale(QtCore.QLocale(QtCore.QLocale.English))
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
            'min-width: ', str(int(self.sizes.barHeight)*2.5), 'px; \n',
			'max-width: ', str(int(self.sizes.barHeight)*2.5), 'px; \n',
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
		self.setMinimum(-1e9)

	def setValue(self, value):
		if type(value) == pt.DeviceAttribute:
			self.setQuality(value.quality)
			val = value.value
		else:
			val = value
 		if val != None:
 			QtGui.QDoubleSpinBox.setValue(self,val)
 		else:
 			QtGui.QDoubleSpinBox.setValue(self,0.0)
#		QtGui.QDoubleSpinBox.setValue(self,val)

class QTangoWriteAttributeLineEdit(QtGui.QLineEdit, QTangoAttributeBase):
	def __init__(self, sizes = None, colors = None, parent=None):
		QTangoAttributeBase.__init__(self, sizes, colors, parent)
		QtGui.QLineEdit.__init__(self, parent)

		self.storedCursorPos = 0
		self.lastKey = QtCore.Qt.Key_0

		self.dataValue = 1.0

		self.setupLayout()

	def setupLayout(self):
		s = ''.join(('QLineEdit { \n',
            'background-color: ', self.attrColors.backgroundColor, '; \n',
            'selection-background-color: ', self.attrColors.secondaryColor0, '; \n',
            'selection-color: ', self.attrColors.backgroundColor, '; \n',
            'border-width: 1px; \n',
            'border-color: ', self.attrColors.secondaryColor0, '; \n',
            'border-style: solid; \n',
            'border-radius: 0px; \n',
            'padding: 0px; \n',
            'margin: 0px; \n',
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

		self.setStyleSheet(s)
		self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
		self.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)


	def setColors(self, attrColorName, backgroundColorName):
		backgroundColor = self.attrColors.__getattribute__(backgroundColorName)
		mainColor = self.attrColors.__getattribute__(attrColorName)
		s = ''.join(('QLineEdit { \n',
            'background-color: ', backgroundColor, '; \n',
            'selection-background-color: ', mainColor, '; \n',
            'selection-color: ', backgroundColor, '; \n',
            'border-width: 1px; \n',
            'border-color: ', mainColor, '; \n',
            'border-style: solid; \n',
            'border-radius: 0px; \n',
            'padding: 0px; \n',
            'margin: 0px; \n',
            'min-width: ', str(self.sizes.barWidth), 'px; \n',
            'max-width: ', str(self.sizes.barWidth), 'px; \n',
            'min-height: ', str(int(self.sizes.barHeight-2)), 'px; \n',
            'max-height: ', str(int(self.sizes.barHeight-2)), 'px; \n',
            'qproperty-readOnly: 0; \n',
            'color: ', mainColor, ';} \n'))

		self.setStyleSheet(s)

	def value(self):
		return self.dataValue

	def setValue(self, value):
		self.dataValue = value
		self.setText(str(value))

	def keyPressEvent(self, event):
		# Record keypress to check if it was return in changeStep
		if type(event) == QtGui.QKeyEvent:
			self.lastKey = event.key()
			if event.key() == QtCore.Qt.Key_Up or event.key() == QtCore.Qt.Key_Down:
				print 'Upp!'
				txt = str(self.text())
				commaPos = txt.find('.')
				cursorPos = self.cursorPosition()
				pos = commaPos - cursorPos
				print 'pos', pos
				print 'comma pos', commaPos
				print 'cursor pos', cursorPos


				if pos + commaPos - 1 < 0:
					pos = -(commaPos - 1)
				elif pos > 0:
					pos -= 1
#
# 				print txt, pos
				if event.key() == QtCore.Qt.Key_Up:
					stepDir = 1
				else:
					stepDir = -1
				self.dataValue += stepDir * 10**pos

				self.clear()
				self.insert(str(self.dataValue))
# 				self.setText(str(self.dataValue))
# 				self.setCursorPosition(cursorPos)

			else:
				super(QTangoWriteAttributeLineEdit, self).keyPressEvent(event)


class QTangoWriteAttributeSpinBox(QtGui.QDoubleSpinBox):
	def __init__(self, sizes = None, colors = None, parent=None):
		QtGui.QDoubleSpinBox.__init__(self, parent)
		self.setLocale(QtCore.QLocale(QtCore.QLocale.English))

# 		Setting up event handling:
		self.lineEdit().cursorPositionChanged.connect(self.changeStep)
		self.lineEdit().editingFinished.connect(self.editReady)
		self.lineEdit().returnPressed.connect(self.editReady)
		self.setKeyboardTracking(False)
		self.valueChanged.connect(self.valueReady)
		self.editingFinished.connect(self.editReady)

		self.storedCursorPos = 0
		self.lastKey = QtCore.Qt.Key_0
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
            'border-width: ', str(int(self.sizes.barHeight/10)), 'px; \n',
            'border-color: ', self.attrColors.secondaryColor0, '; \n',
            'border-top-style: none; \n',
			'border-bottom-style: none; \n',
			'border-left-style: double; \n',
			'border-right-style: solid; \n',
            'border-radius: 0px; \n',
            'padding: 0px; \n',
            'margin: 0px; \n',
            'qproperty-buttonSymbols: NoButtons; \n',
            'min-width: ', str(int(self.sizes.barHeight)*2.5), 'px; \n',
            'max-width: ', str(int(self.sizes.barHeight)*2.5), 'px; \n',
            'min-height: ', str(int(self.sizes.barHeight)), 'px; \n',
            'max-height: ', str(int(self.sizes.barHeight)), 'px; \n',
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
#		self.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
		self.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom)
		self.setMaximum(1e9)
		self.setMinimum(-1e9)

	def valueReady(self, value):
		print 'Value ready::', value
		self.lineEdit().setCursorPosition(self.storedCursorPos)

	def editReady(self):
		print 'Edit ready::'
		print 'Cursor pos set to ', self.storedCursorPos
		self.lineEdit().setCursorPosition(self.storedCursorPos)

	def stepBy(self, steps):
		print 'Step ', steps
		print 'Value: ', self.value()
		print 'Text: ', self.valueFromText(self.text())
		txt = self.text()
		currentValue = self.valueFromText(txt)
		commaPos = str(txt).find('.')
		self.storedCursorPos = self.lineEdit().cursorPosition()
		pos = commaPos - self.storedCursorPos + 1
		if pos + self.decimals() < 0:
			pos = -self.decimals()
		elif pos > 0:
			pos -= 1
		self.setValue(currentValue + 10**pos * steps)

	def changeStep(self, old, new):
		print 'In changeStep::'
		# Check if the last key was return, then the cursor
		# shouldn't change
#		if self.lastKey != QtCore.Qt.Key_Return:
#		if self.lastKey == QtCore.Qt.Key_Up:
# 			txt = str(self.text())
# 			commaPos = txt.find('.')
# 			self.storedCursorPos = self.lineEdit().cursorPosition()
# 			pos = commaPos - self.storedCursorPos + 1
# 			print 'pos', pos
# 			print 'comma pos', commaPos
# 			print 'stored pos', self.storedCursorPos
# 			if pos + self.decimals() < 0:
# 				pos = -self.decimals()
# 			elif pos > 0:
# 				pos -= 1
#
# 			print txt, pos
# 			self.setSingleStep(10 ** pos)

	def keyPressEvent(self, event):
		# Record keypress to check if it was return in changeStep
		if type(event) == QtGui.QKeyEvent:
			self.lastKey = event.key()
		super(QTangoWriteAttributeSpinBox, self).keyPressEvent(event)

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

class QTangoWriteAttributeSpinBox2(QtGui.QDoubleSpinBox):
	def __init__(self, sizes = None, colors = None, parent=None):
		QtGui.QDoubleSpinBox.__init__(self, parent)
		self.setLocale(QtCore.QLocale(QtCore.QLocale.English))

# 		Setting up event handling:
		self.lineEdit().cursorPositionChanged.connect(self.changeStep)
		self.lineEdit().editingFinished.connect(self.editReady)
		self.lineEdit().returnPressed.connect(self.editReady)
		self.setKeyboardTracking(False)
		self.valueChanged.connect(self.valueReady)
		self.editingFinished.connect(self.editReady)

		self.storedCursorPos = 0
		self.lastKey = QtCore.Qt.Key_0
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
            'selection-background-color: ', self.attrColors.secondaryColor1, '; \n',
            'selection-color: ', self.attrColors.backgroundColor, '; \n',
#            'border-width: ', str(int(self.sizes.barHeight/10)), 'px; \n',
			'border-width: ', str(int(1)), 'px; \n',
            'border-color: ', self.attrColors.secondaryColor0, '; \n',
            'border-top-style: solid; \n',
			'border-bottom-style: solid; \n',
			'border-left-style: double; \n',
			'border-right-style: solid; \n',
            'border-radius: 0px; \n',
            'padding: 0px; \n',
            'margin: 0px; \n',
            'qproperty-buttonSymbols: UpDownArrows; \n',
#            'min-width: ', str(int(self.sizes.barHeight)*2.5), 'px; \n',
            'min-width: ', str(int(self.sizes.barHeight)*1), 'px; \n',
            'max-width: ', str(int(self.sizes.barHeight)*4), 'px; \n',
            'min-height: ', str(int(self.sizes.barHeight*1.2)), 'px; \n',
            'max-height: ', str(int(self.sizes.barHeight*1.2)), 'px; \n',
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
		self.setSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Minimum)
		self.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
#		self.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom)
		self.setMaximum(1e9)
		self.setMinimum(-1e9)

	def valueReady(self, value):
		print 'Value ready::', value
		self.lineEdit().setCursorPosition(self.storedCursorPos)

	def editReady(self):
		print 'Edit ready::'
		print 'Cursor pos set to ', self.storedCursorPos
		self.lineEdit().setCursorPosition(self.storedCursorPos)

	def stepBy(self, steps):
		print "In stepBy::"
		print 'stepBy::Step ', steps
		print 'stepBy::Value: ', self.value()
		print 'stepBy::Text: ', self.valueFromText(self.text())
		txt = self.text()
		currentValue = self.valueFromText(txt)
		commaPos = str(txt).find('.')
		self.storedCursorPos = self.lineEdit().cursorPosition()
#		self.lineEdit().setCursorPosition(self.storedCursorPos)
		pos = commaPos - self.storedCursorPos + 1
		print 'stepBy::comma pos', commaPos
		print 'stepBy::stored pos', self.storedCursorPos
		print 'stepBy::cursor pos', self.lineEdit().cursorPosition()
		if pos + self.decimals() < 0:
			pos = -self.decimals()
		elif pos > 0:
			pos -= 1
		self.setValue(currentValue + 10**pos * steps)

	def changeStep(self, old, new):
		print 'In changeStep::'
		# Check if the last key was return, then the cursor
		# shouldn't change
		if self.lastKey != QtCore.Qt.Key_Return:
#		if self.lastKey == QtCore.Qt.Key_Up:
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

	def keyPressEvent(self, event):
		# Record keypress to check if it was return in changeStep
		if type(event) == QtGui.QKeyEvent:
			self.lastKey = event.key()
		super(QTangoWriteAttributeSpinBox2, self).keyPressEvent(event)

	def setColors(self, attrColorName, backgroundColorName):
		mainColor = self.attrColors.__getattribute__(backgroundColorName)
		backgroundColor = self.attrColors.__getattribute__(attrColorName)
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
		if type(value) == pt.DeviceAttribute:
			self.startLabel.setQuality(value.quality)
			self.endLabel.setQuality(value.quality)
			val = value.value
		else:
			val = value

		self.valueSpinbox.setValue(val)
		self.update()



class QTangoHSliderBase(QtGui.QSlider, QTangoAttributeBase):
	def __init__(self, sizes = None, colors = None, parent=None):
		QTangoAttributeBase.__init__(self, sizes, colors, parent)
		QtGui.QSlider.__init__(self, parent)
		self.setupLayout()

	def setupLayout(self):
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
		colorLine = QtGui.QColor(self.attrColors.secondaryColor0)
		penAttr = QtGui.QPen(colorLine)
		penAttr.setWidthF(lineW)
		brushAttr = QtGui.QBrush(colorLine)
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
		pen.setColor(colorAttr)
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
		if type(value) == pt.DeviceAttribute:
			self.setQuality(value.quality)
			if value.value != None:
				val = 0.0
			else:
				val = value.value
		else:
			val = value
		self.attrValue = val
		self.update()

	def setWriteValue(self, value):
		self.attrWriteValue = value
		self.update()

	def setWarningLimits(self, limits):
		if type(limits)==pt.AttributeInfoListEx:
			warnHigh = limits[0].alarms.max_warning
			warnLow = limits[0].alarms.min_warning
		else:
			warnLow = limits[0]
			warnHigh = limits[1]
		self.warnHigh = warnHigh
		self.warnLow = warnLow
		self.update()

	def setSliderLimits(self, min, max):
		self.attrMinimum = min
		self.attrMaximum = max
		self.update()

class QTangoHSliderBase2(QtGui.QSlider, QTangoAttributeBase):
	def __init__(self, sizes = None, colors = None, parent=None):
		QTangoAttributeBase.__init__(self, sizes, colors, parent)
		QtGui.QSlider.__init__(self, parent)
		self.setupLayout()

	def setupLayout(self):
		self.setMaximum(100)
		self.setMinimum(0)
		self.attrMaximum = 1
		self.attrMinimum = 0
		self.attrValue = 0.5
		self.attrWriteValue = None
		self.warnHigh = 0.9
		self.warnLow = 0.1

		self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
		self.setMaximumHeight(self.sizes.barHeight*1.0)
		self.setMinimumHeight(self.sizes.barHeight*1.0)

	def paintEvent(self, e):
		qp = QtGui.QPainter()
		qp.begin(self)
		self.drawWidget(qp)
		qp.end()

	def drawWidget(self, qp):
		size = self.size()
		w = size.width()
		h = size.height()

		startH = h/2.0		# Position of horizontal line
		startH = h/6.0		# Position of horizontal line
		lineW = h/4.0		# Width of horizontal line
		arrowW = h/2.5		# Width of arrow
		writeW = h/8.0

		# Vertical position of scale text
		textVertPos = h-h/16.0
		textVertPos = self.sizes.barHeight*0.5-h/16.0
		textVertPos = h
		textVertPos = startH+self.sizes.barHeight*0.5+lineW/2+1

		# Pixel coordinate of current value:
		xVal = w*(self.attrValue-self.attrMinimum)/(self.attrMaximum-self.attrMinimum)

		# Setup font
		font = QtGui.QFont('Calibri', self.sizes.barHeight*0.5, self.sizes.fontWeight)
#		font.setStretch(self.sizes.fontStretch)

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
		colorLine = QtGui.QColor(self.attrColors.secondaryColor0)
		penAttr = QtGui.QPen(colorLine)
		penAttr.setWidthF(lineW)
		brushAttr = QtGui.QBrush(colorLine)
		qp.setFont(font)

		colorWarn = QtGui.QColor(self.attrColors.warnColor)
		penWarn = QtGui.QPen(colorWarn)
		brushWarn = QtGui.QBrush(colorWarn)

		# Draw write value arrow
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
		pen.setColor(colorAttr)
		pen.setWidthF(0)
		qp.setPen(pen)
		qp.setBrush(brushAttr)
		qp.drawPolygon(poly)
		if self.attrWriteValue != None:
#			pen.setWidthF(writeW)
			pen.setWidthF(2)
			pen.setColor(colorWriteAttr)
			qp.setPen(pen)
			xValW = w*(self.attrWriteValue-self.attrMinimum)/(self.attrMaximum-self.attrMinimum)

			polyW = QtGui.QPolygonF([QtCore.QPointF(xValW,startH-lineW/2.0),
					QtCore.QPointF(xValW-arrowW/2.0,0),
					QtCore.QPointF(xValW+arrowW/2.0,0)])
			polyW = QtGui.QPolygonF([QtCore.QPointF(xValW-arrowW/2.0-4,h),
					QtCore.QPointF(xValW-4,startH+lineW/2.0-1),
					QtCore.QPointF(xValW+4,startH+lineW/2.0-1),
					QtCore.QPointF(xValW+arrowW/2.0+4,h)])


			qp.drawPolyline(polyW)

		pen.setColor(colorAttr)
		pen.setWidthF(2)
		qp.setPen(pen)
		qp.drawPolygon(poly)

		# Draw texts
#		qp.drawText(textPoint, sVal)
		# Don't draw the limit texts if the value text is overlapping
		pen.setColor(colorAttr)
		qp.setPen(pen)
		if xVal - arrowW/2 > sMinWidth:
			qp.drawText(QtCore.QPointF(2, textVertPos), sMin)
		if textPoint.x() < w-sMaxWidth:
			qp.drawText(QtCore.QPointF(w-sMaxWidth-2, textVertPos), sMax)

		qp.setRenderHint(QtGui.QPainter.Antialiasing, False) # No antialiasing when drawing horizontal/vertical lines
		qp.setRenderHint(QtGui.QPainter.TextAntialiasing, True)
		qp.setRenderHint(QtGui.QPainter.SmoothPixmapTransform, True)

		# Draw warning line
		penWarn.setWidthF(lineW)
		qp.setPen(penWarn)
		qp.setBrush(brushWarn)
		qp.drawLine(0, startH, w, startH)
		# Draw line
		penAttr = QtGui.QPen(colorLine)
		penAttr.setWidthF(lineW)
		brushAttr = QtGui.QBrush(colorLine)
		qp.setPen(penAttr)
		qp.setBrush(brushAttr)
		qp.drawLine(QtCore.QPointF(w*(self.warnLow-self.attrMinimum)/(self.attrMaximum-self.attrMinimum),startH),
				QtCore.QPointF(w*(self.warnHigh-self.attrMinimum)/(self.attrMaximum-self.attrMinimum),startH))
		# Draw start and end point lines
		penAttr.setWidthF(1)
		if self.warnLow > self.attrMinimum:
			penAttr.setColor(colorWarn)
		qp.setPen(penAttr)
		qp.drawLine(0, startH, 0, startH+lineW*2)
		if self.warnHigh > self.attrMaximum:
			penAttr.setColor(colorLine)
			qp.setPen(penAttr)
		qp.drawLine(w-1, startH, w-1, startH+lineW*2)

	def setValue(self, value):
		if type(value) == pt.DeviceAttribute:
			self.setQuality(value.quality)
			if value.value != None:
				val = value.value
			else:
				val = 0.0
		else:
			val = value
		self.attrValue = val
		self.update()

	def setWriteValue(self, value):
		self.attrWriteValue = value
		self.update()

	def setWarningLimits(self, limits):
		if type(limits)==pt.AttributeInfoListEx:
			warnHigh = limits[0].alarms.max_warning
			warnLow = limits[0].alarms.min_warning
		else:
			warnLow = limits[0]
			warnHigh = limits[1]
		self.warnHigh = warnHigh
		self.warnLow = warnLow
		self.update()

	def setSliderLimits(self, min, max):
		self.attrMinimum = min
		self.attrMaximum = max
		self.update()

class QTangoHSliderBaseCompact(QtGui.QSlider, QTangoAttributeBase):
	def __init__(self, sizes = None, colors = None, parent=None):
		QTangoAttributeBase.__init__(self, sizes, colors, parent)
		QtGui.QSlider.__init__(self, parent)
		self.setupLayout()

	def setupLayout(self):
		self.setMaximum(100)
		self.setMinimum(0)
		self.attrMaximum = 1
		self.attrMinimum = 0
		self.attrValue = 0.5
		self.attrWriteValue = None
		self.warnHigh = 0.9
		self.warnLow = 0.1

		self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
		self.setMaximumHeight(self.sizes.barHeight*0.3)
		self.setMinimumHeight(self.sizes.barHeight*0.3)

	def paintEvent(self, e):
		qp = QtGui.QPainter()
		qp.begin(self)
		self.drawWidget(qp)
		qp.end()

	def drawWidget(self, qp):
		size = self.size()
		w = size.width()
		h = size.height()

		startH = h/2.0		# Position of horizontal line
#		startH = h/6.0		# Position of horizontal line
		lineW = h*0.6		# Width of horizontal line
		arrowW = h*0.5		# Width of indicator


		# Pixel coordinate of current value:
		xVal = w*(self.attrValue-self.attrMinimum)/(self.attrMaximum-self.attrMinimum)


		colorAttr = QtGui.QColor(self.attrColors.secondaryColor0)
		colorLine = QtGui.QColor(self.attrColors.secondaryColor0)
		penAttr = QtGui.QPen(colorLine)
		penAttr.setWidthF(lineW)
		brushAttr = QtGui.QBrush(colorLine)

		colorWarn = QtGui.QColor(self.attrColors.warnColor)
		penWarn = QtGui.QPen(colorWarn)
		brushWarn = QtGui.QBrush(colorWarn)

		qp.setRenderHint(QtGui.QPainter.Antialiasing, False) # No antialiasing when drawing horizontal/vertical lines

		# Draw warning line
		penWarn.setWidthF(lineW)
		qp.setPen(penWarn)
		qp.setBrush(brushWarn)
		qp.drawLine(0, int(startH), w, int(startH))
		# Draw line
		penAttr = QtGui.QPen(colorLine)
		penAttr.setWidthF(lineW)
		brushAttr = QtGui.QBrush(colorLine)
		qp.setPen(penAttr)
		qp.setBrush(brushAttr)
		qp.drawLine(QtCore.QPointF(w*(self.warnLow-self.attrMinimum)/(self.attrMaximum-self.attrMinimum),int(startH)),
				QtCore.QPointF(w*(self.warnHigh-self.attrMinimum)/(self.attrMaximum-self.attrMinimum),int(startH)))
		# Draw indicator
		penInd = QtGui.QPen(QtCore.Qt.white)
		penInd.setWidthF(arrowW)
		brushInd = QtGui.QBrush(QtCore.Qt.white)
		qp.setPen(penInd)
		qp.setBrush(brushInd)
		qp.drawLine(QtCore.QPointF(xVal, startH-lineW/2.0-1), QtCore.QPointF(xVal, startH+lineW/2.0+1))

	def setValue(self, value):
		if type(value) == pt.DeviceAttribute:
			self.setQuality(value.quality)
			if value.value != None:
				val = value.value
			else:
				val = 0.0
		else:
			val = value
		self.attrValue = val
		self.update()

	def setWriteValue(self, value):
		self.attrWriteValue = value
		self.update()

	def setWarningLimits(self, limits):
		if type(limits)==pt.AttributeInfoListEx:
			warnHigh = limits[0].alarms.max_warning
			warnLow = limits[0].alarms.min_warning
		else:
			warnLow = limits[0]
			warnHigh = limits[1]
		self.warnHigh = warnHigh
		self.warnLow = warnLow
		self.update()

	def setSliderLimits(self, min, max):
		self.attrMinimum = min
		self.attrMaximum = max
		self.update()

class QTangoVSliderBase2(QtGui.QSlider, QTangoAttributeBase):
	def __init__(self, sizes = None, colors = None, parent=None):
		QTangoAttributeBase.__init__(self, sizes, colors, parent)
		QtGui.QSlider.__init__(self, parent)
		self.unit = ""
		self.setupLayout()

	def setupLayout(self):
		self.setMaximum(100)
		self.setMinimum(0)
		self.attrMaximum = 1
		self.attrMinimum = 0
		self.attrValue = 0.5
		self.attrWriteValue = None
		self.warnHigh = 0.9
		self.warnLow = 0.1

		self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
		self.setMaximumWidth(self.sizes.barWidth*4.0-2)
		self.setMinimumWidth(self.sizes.barWidth*4.0-2)

	def paintEvent(self, e):
		qp = QtGui.QPainter()
		qp.begin(self)
		self.drawWidget(qp)
		qp.end()

	def drawWidget(self, qp):
		size = self.size()
		w = size.width()
		h = size.height()

		# Setup font
#		font = QtGui.QFont('Calibri', self.sizes.barHeight*0.75, self.sizes.fontWeight)
		font = QtGui.QFont(self.sizes.fontType, self.sizes.barHeight*0.75, self.sizes.fontWeight)
		font.setStretch(self.sizes.fontStretch)
		font.setStyleStrategy(QtGui.QFont.PreferAntialias)
#		font.setStretch(self.sizes.fontStretch)

		# Strings to draw
		sVal = "{:.4g}".format((self.attrValue))
		sMin = "{:.4g}".format((self.attrMinimum))
		sMax = "{:.4g}".format((self.attrMaximum))
		sValWidth = QtGui.QFontMetricsF(font).width(sVal)
		sValHeight = QtGui.QFontMetricsF(font).height()
		sMinWidth = QtGui.QFontMetricsF(font).width(sMin)
		sMaxWidth = QtGui.QFontMetricsF(font).width(sMax)


		startX = w/2.0		# Position of vertical line
		startX = 0.0		# Position of vertical line
		lineW = w/8.0		# Width of vertical line
#		lineW = 5.0
		arrowW = w/2.5		# Width of arrow
		arrowW = sValHeight/2.0
		writeW = w/8.0
		writeW = 6.0

		# Vertical position of scale text
		textVertPos = h-h/16.0
		textVertPos = self.sizes.barHeight*0.5-h/16.0
		textVertPos = h
		textVertPos = startX+self.sizes.barHeight*0.5+lineW/2+1


		# Pixel coordinate of current value:
		yVal = h-h*(self.attrValue-self.attrMinimum)/(self.attrMaximum-self.attrMinimum)

		# Position to draw text of current value
		textPoint = QtCore.QPointF(startX+lineW/2+arrowW, yVal+sValHeight*0.3)
		# Check if text is outside the bounds of the slider
		if yVal - sValHeight < 0:
			textPoint.setY(sValHeight)
		if yVal + sValHeight > h:
			textPoint.setY(h-sValHeight*0.2)


		colorAttr = QtGui.QColor(self.attrColors.secondaryColor0)
		colorWriteAttr = QtGui.QColor(self.attrColors.secondaryColor2)
		colorLine = QtGui.QColor(self.attrColors.secondaryColor0)
		pen = QtGui.QPen(colorLine)
		penAttr = QtGui.QPen(colorLine)
		penAttr.setWidthF(lineW)
		brushAttr = QtGui.QBrush(colorLine)
		qp.setFont(font)

		colorWarn = QtGui.QColor(self.attrColors.warnColor)
		penWarn = QtGui.QPen(colorWarn)
		brushWarn = QtGui.QBrush(colorWarn)

		# Draw anti-aliased
		qp.setRenderHint(QtGui.QPainter.Antialiasing, True)
		qp.setRenderHint(QtGui.QPainter.TextAntialiasing, True)

		pen.setWidthF(1.5)
		brushAttr = QtGui.QBrush(colorLine, QtCore.Qt.NoBrush)
		qp.setPen(pen)
		qp.setBrush(brushAttr)

		#Check if the arrow is outside the bounds of the slider
		if yVal < 0:
			# Draw up pointing arrow if the pixel position is < 0
			arrowPoly = QtGui.QPolygonF([QtCore.QPointF(startX+lineW/2+arrowW/2.0, arrowW/4.0),
					QtCore.QPointF(startX+lineW/2.0, 0.0),
					QtCore.QPointF(startX+lineW/2.0+arrowW, 2*arrowW),
					QtCore.QPointF(w-1.0, 2*arrowW)])
			qp.drawPolyline(arrowPoly)
		elif yVal - arrowW < 0:
			arrowPoly = QtGui.QPolygonF([QtCore.QPointF(startX+lineW/2.0, yVal),
					QtCore.QPointF(startX+lineW/2.0+arrowW, 2*arrowW),
					QtCore.QPointF(w-1.0, 2*arrowW),
					QtCore.QPointF(w-1.0, 0.0),
					QtCore.QPointF(startX+lineW/2.0+arrowW, 0.0)])
			qp.drawPolygon(arrowPoly)
		elif yVal > h:
			# Draw down pointing arrow if the pixel position is > h
			arrowPoly = QtGui.QPolygonF([QtCore.QPointF(startX+lineW/2+arrowW/2.0, h-arrowW/4.0),
					QtCore.QPointF(startX+lineW/2.0, h),
					QtCore.QPointF(startX+lineW/2.0+arrowW, h-2*arrowW),
					QtCore.QPointF(w-1.0, h-2*arrowW)])
			qp.drawPolyline(arrowPoly)
		elif yVal + arrowW > h:
			arrowPoly = QtGui.QPolygonF([QtCore.QPointF(startX+lineW/2.0, yVal),
					QtCore.QPointF(startX+lineW/2.0+arrowW, h),
					QtCore.QPointF(w-1.0, h),
					QtCore.QPointF(w-1.0, h-2*arrowW),
					QtCore.QPointF(startX+lineW/2.0+arrowW, h-2*arrowW)])
			qp.drawPolygon(arrowPoly)
		else:
			# Draw left pointing arrow otherwise
			arrowPoly = QtGui.QPolygonF([QtCore.QPointF(startX+lineW/2.0, yVal),
					QtCore.QPointF(startX+lineW/2.0+arrowW, yVal+arrowW),
					QtCore.QPointF(w-1.0, yVal+arrowW),
					QtCore.QPointF(w-1.0, yVal-arrowW),
					QtCore.QPointF(startX+lineW/2.0+arrowW, yVal-arrowW)])
			qp.drawPolygon(arrowPoly)


		# Change color of arrow when in warning range
# 		if self.attrValue < self.warnLow or self.attrValue > self.warnHigh:
# 			pen = penWarn
# 			brush = brushWarn
# 			qp.setBrush(brush)
# 		else:
# 			pen = penAttr
# 			brush = brushAttr


		# Write value arrow
		if self.attrWriteValue != None:
#			pen.setWidthF(writeW)
			pen.setWidthF(2.5)
			pen.setColor(colorWriteAttr)
			qp.setPen(pen)
			writeYVal = h-h*(self.attrWriteValue-self.attrMinimum)/(self.attrMaximum-self.attrMinimum)

			polyW = QtGui.QPolygonF([QtCore.QPointF(startX+lineW/2.0+arrowW, writeYVal+arrowW+writeW),
					QtCore.QPointF(startX+lineW/2.0, writeYVal+writeW),
					QtCore.QPointF(startX+lineW/2.0, writeYVal-writeW),
					QtCore.QPointF(startX+lineW/2.0+arrowW, writeYVal-arrowW-writeW)])


			qp.drawPolyline(polyW)

		#
		# Draw texts
		#

		# Draw value text
		pen.setColor(colorLine)
		qp.setPen(pen)
		qp.drawText(textPoint, sVal)

		# Draw slider scale texts
		# Don't draw the limit texts if the value text is overlapping
		font.setPointSizeF(self.sizes.barHeight*0.5)

		qp.setRenderHint(QtGui.QPainter.TextAntialiasing, True)
		qp.setFont(font)
		if yVal + arrowW/2 < h-sValHeight:
			qp.drawText(QtCore.QPointF(startX+lineW, h-sValHeight*0.2), sMin)
		if yVal - arrowW/2 > sValHeight:
			qp.drawText(QtCore.QPointF(startX+lineW, sValHeight*0.6), sMax)

		qp.setRenderHint(QtGui.QPainter.Antialiasing, False) # No antialiasing when drawing horizontal/vertical lines
		qp.setRenderHint(QtGui.QPainter.TextAntialiasing, True)
		qp.setRenderHint(QtGui.QPainter.SmoothPixmapTransform, True)

		# Draw warning line
		penWarn.setWidthF(lineW)
		qp.setPen(penWarn)
		qp.setBrush(brushWarn)
		qp.drawLine(startX, 0, startX, h)
		# Draw line
		penAttr = QtGui.QPen(colorLine)
		penAttr.setWidthF(lineW)
		brushAttr = QtGui.QBrush(colorLine)
		qp.setPen(penAttr)
		qp.setBrush(brushAttr)
		qp.drawLine(QtCore.QPointF(startX, h-h*(self.warnLow-self.attrMinimum)/(self.attrMaximum-self.attrMinimum)),
				QtCore.QPointF(startX, h-h*(self.warnHigh-self.attrMinimum)/(self.attrMaximum-self.attrMinimum)))
		# Draw start and end point lines
		penAttr.setWidthF(1)
		if self.warnLow > self.attrMinimum:
			penAttr.setColor(colorWarn)
		qp.setPen(penAttr)
		qp.drawLine(startX, h-1, startX+lineW*2, h-1)
		if self.warnHigh > self.attrMaximum:
			penAttr.setColor(colorLine)
			qp.setPen(penAttr)
		qp.drawLine(startX, 0, startX+lineW*2, 0)

	def setValue(self, value):
		if type(value) == pt.DeviceAttribute:
			self.setQuality(value.quality)
			if value.value != None:
				val = value.value
			else:
				val = 0.0
		else:
			val = value
		self.attrValue = val
		self.update()

	def setWriteValue(self, value):
		self.attrWriteValue = value
		self.update()

	def setWarningLimits(self, limits):
		if type(limits)==pt.AttributeInfoListEx:
			warnHigh = limits[0].alarms.max_warning
			warnLow = limits[0].alarms.min_warning
		else:
			warnLow = limits[0]
			warnHigh = limits[1]
		self.warnHigh = warnHigh
		self.warnLow = warnLow
		self.update()

	def setSliderLimits(self, min, max):
		self.attrMinimum = min
		self.attrMaximum = max
		self.update()

	def setUnit(self, aUnit):
		self.unit = aUnit
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

	def setWarningLimits(self, limits):
		if type(limits)==pt.AttributeInfoListEx:
			warnHigh = limits[0].alarms.max_warning
			warnLow = limits[0].alarms.min_warning
		else:
			warnLow = limits[0]
			warnHigh = limits[1]
		self.warningRegionUpper.setRegion([warnHigh, 1e6])
		self.warningRegionLower.setRegion([-1e6, warnLow])
		self.goodRegion.setRegion([warnLow, warnHigh])


	def addPoint(self, xNew, yNew):
		if self.currentDataIndex+1 > self.valuesSize:
			self.currentDataIndex = int(self.valuesSize*0.75)
			self.xValues[0:self.currentDataIndex]=self.xValues[self.valuesSize-self.currentDataIndex:self.valuesSize]
			self.yValues[0:self.currentDataIndex]=self.yValues[self.valuesSize-self.currentDataIndex:self.valuesSize]

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
		pi.hideAxis('left')
		pi.showAxis('right', True)
		axLeft = pi.getAxis('right')
		axLeft.setPen(self.attrColors.secondaryColor0)
		axBottom = pi.getAxis('bottom')
		axBottom.setPen(self.attrColors.secondaryColor0)

		self.spectrumCurve = self.plot()
		self.spectrumCurve.setPen(self.attrColors.secondaryColor0, width = 2.0)

	def setSpectrum(self, xData, yData):
		self.spectrumCurve.setData(y = yData, x = xData, antialias = False)
		self.update()

class QTangoImageWithHistBase(pg.ImageView):
	def __init__(self, sizes = None, colors = None, parent=None):
		if colors == None:
			self.attrColors = QTangoColors()
		else:
			self.attrColors = colors
		if sizes == None:
			self.sizes = QTangoSizes()
		else:
			self.sizes = sizes

# 		pi = pg.PlotItem()
# 		pi.getAxis('left').setPen(self.attrColors.secondaryColor0)
# 		pi.getAxis('bottom').setPen(self.attrColors.secondaryColor0)

#		pg.ImageView.__init__(self, view = pi)
		pg.ImageView.__init__(self)

		self.setupLayout()

	def setupLayout(self):
		self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
# 		pi=self.getPlotItem()
# 		pi.hideAxis('left')
# 		pi.showAxis('right', True)
# 		axLeft = pi.getAxis('right')
# 		axLeft.setPen(self.attrColors.secondaryColor0)
# 		axBottom = pi.getAxis('bottom')
# 		axBottom.setPen(self.attrColors.secondaryColor0)

#		self.imageItem = pg.ImageItem()

# 	def setImage(self, xData, yData):
# 		self.spectrumCurve.setData(y = yData, x = xData, antialias = True)
# 		self.update()

class QTangoImageBase(pg.GraphicsView):
	def __init__(self, sizes = None, colors = None, parent=None):
		if colors == None:
			self.attrColors = QTangoColors()
		else:
			self.attrColors = colors
		if sizes == None:
			self.sizes = QTangoSizes()
		else:
			self.sizes = sizes

		pg.GraphicsView.__init__(self)

		self.vb = pg.ViewBox(lockAspect = 1.0, invertY = True)
		self.setCentralItem(self.vb)
		self.image = pg.ImageItem()
		self.vb.addItem(self.image)

		gradEditor = pg.GradientEditorItem()
# 		for t in list(gradEditor.ticks.keys()):
# 			gradEditor.removeTick(t, finish = False)
# 		gradEditor.addTick(0.0, QtGui.QColor(0, 0, 0), movable = False, finish = False)
# 		gradEditor.addTick(0.3333, QtGui.QColor(0, 80, 255), movable = False, finish = False)
# 		gradEditor.addTick(0.6667, QtGui.QColor(102, 203, 255), movable = False, finish = False)
# 		gradEditor.addTick(1.0, QtGui.QColor(255, 255, 255), movable = False, finish = False)
		gradEditor.loadPreset('flame')
		self.lut = gradEditor.getLookupTable(256)

		self.setupLayout()

	def setupLayout(self):

		self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)


	def setImage(self, data):
		if data is not None:
			self.image.setImage(np.transpose(data), autoLevels = False, lut = self.lut, autoDownSample = True)
			self.update()

class QTangoReadAttributeSlider(QTangoAttributeBase):
	def __init__(self, sizes = None, colors = None, parent=None):
		QTangoAttributeBase.__init__(self, sizes, colors, parent)
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
#		self.layout.setMargin(int(self.sizes.barHeight/10))
		self.layout.setMargin(0)
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
		if type(value) == pt.DeviceAttribute:
			self.startLabel.setQuality(value.quality)
			self.endLabel.setQuality(value.quality)
			if value.value != None:
				val = value.value
				self.valueSpinbox.setValue(val)
				self.valueSlider.setValue(val)

		else:
			val = value
			self.valueSpinbox.setValue(val)
			self.valueSlider.setValue(val)
		self.update()

	def setAttributeWarningLimits(self, limits):
		self.valueSlider.setWarningLimits(limits)

	def setSliderLimits(self, min, max):
		self.valueSlider.setSliderLimits(min, max)

class QTangoReadAttributeSlider2(QTangoAttributeBase):
	def __init__(self, sizes = None, colors = None, parent=None):
		QTangoAttributeBase.__init__(self, sizes, colors, parent)
		self.setupLayout()

	def setupLayout(self):
		self.startLabel = QTangoStartLabel(self.sizes, self.attrColors)
		self.endLabel = QTangoEndLabel(self.sizes, self.attrColors)
		self.nameLabel = QTangoAttributeNameLabel(self.sizes, self.attrColors)
		self.unitLabel = QTangoAttributeUnitLabel(self.sizes, self.attrColors)
		self.valueSpinbox = QTangoReadAttributeSpinBox(self.sizes, self.attrColors)
		self.valueSlider = QTangoHSliderBase2(self.sizes, self.attrColors)
		self.writeLabel = QTangoStartLabel(self.sizes, self.attrColors)
		self.writeLabel.currentAttrColor = self.attrColors.backgroundColor
		self.writeLabel.setupLayout()

		self.layout = QtGui.QHBoxLayout(self)
		self.layout.setContentsMargins(0,0,0,0)
		self.layout.setMargin(int(self.sizes.barHeight/10))
		self.layout.setMargin(0)
		self.layout.setSpacing(self.sizes.barWidth/3)

		self.layoutGrid = QtGui.QGridLayout()
		self.layoutGrid.setContentsMargins(0, 0, 0, 0)
#		self.layoutGrid.setMargin(int(self.sizes.barHeight/10))
		self.layoutGrid.setMargin(0)
		self.layoutGrid.addWidget(self.nameLabel, 0, 0)
		self.layoutGrid.addWidget(self.unitLabel, 0, 1)
		self.layoutGrid.addWidget(self.valueSlider, 1, 0, 1, 2)
		self.layoutGrid.addWidget(self.valueSpinbox, 0, 3)
		self.layoutGrid.addWidget(self.writeLabel, 1, 2)

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

	def setAttributeName(self, aName, aUnit = None):
		self.nameLabel.setText(aName)
		if aUnit != None:
			self.unitLabel.setText(aUnit)
		self.update()

	def setAttributeValue(self, value):
		if type(value) == pt.DeviceAttribute:
			self.startLabel.setQuality(value.quality)
			self.endLabel.setQuality(value.quality)
			self.nameLabel.setQuality(value.quality)
			if value.value != None:
				val = value.value
				self.valueSpinbox.setValue(val)
				self.valueSlider.setValue(val)
		else:
			val = value
			self.valueSpinbox.setValue(val)
			self.valueSlider.setValue(val)
		self.update()

	def setAttributeWarningLimits(self, limits):
		self.valueSlider.setWarningLimits(limits)

	def setSliderLimits(self, min, max):
		self.valueSlider.setSliderLimits(min, max)

	def configureAttribute(self, attrInfo):
		QTangoAttributeBase.configureAttribute(self, attrInfo)
		try:
			min_warning = float(self.attrInfo.alarms.min_warning)
		except:
			min_warning = -np.inf
		try:
			max_warning = float(self.attrInfo.alarms.max_warning)
		except:
			max_warning = np.inf
		self.setAttributeWarningLimits((min_warning, max_warning))
		self.unitLabel.setText(self.attrInfo.unit)

class QTangoReadAttributeSlider3(QTangoReadAttributeSlider2):
	def __init__(self, sizes = None, colors = None, parent=None):
		QTangoReadAttributeSlider2.__init__(self, sizes, colors, parent)

	def setupLayout(self):
#		QTangoReadAttributeSlider2.setupLayout(self)
		self.startLabel = QTangoStartLabel(self.sizes, self.attrColors)
		self.endLabel = QTangoEndLabel(self.sizes, self.attrColors)
		self.nameLabel = QTangoAttributeNameLabel(self.sizes, self.attrColors)
		self.unitLabel = QTangoAttributeUnitLabel(self.sizes, self.attrColors)
		self.valueSpinbox = QTangoReadAttributeSpinBox(self.sizes, self.attrColors)
		self.valueSlider = QTangoHSliderBase2(self.sizes, self.attrColors)
		self.writeLabel = QTangoStartLabel(self.sizes, self.attrColors)
		self.writeLabel.currentAttrColor = self.attrColors.backgroundColor
		self.writeLabel.setupLayout()

		self.layout = QtGui.QHBoxLayout(self)
		self.layout.setContentsMargins(0,0,0,0)
		self.layout.setMargin(int(self.sizes.barHeight/10))
		self.layout.setSpacing(self.sizes.barHeight/3)

		self.layoutGrid = QtGui.QGridLayout()
		self.layoutGrid.setContentsMargins(0, 0, 0, 0)
		self.layoutGrid.setMargin(int(self.sizes.barHeight/10))
		self.layoutGrid.setMargin(0)
		self.layoutGrid.addWidget(self.nameLabel, 0, 0)
		self.layoutGrid.addWidget(self.unitLabel, 0, 1)
		self.layoutGrid.addWidget(self.valueSlider, 1, 0, 1, 2)
# 		self.layoutGrid.addWidget(self.valueSpinbox, 0, 3)
# 		self.layoutGrid.addWidget(self.writeLabel, 1, 2)

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
# 		self.layoutGrid.removeWidget(self.valueSpinbox)
# 		self.valueSpinbox = None
# 		self.layoutGrid.removeWidget(self.writeLabel)
		self.valueLabel = QTangoAttributeNameLabel(self.sizes, self.attrColors)
		self.layoutGrid.addWidget(self.valueLabel, 0, 3)

	def setAttributeValue(self, value):
		if type(value) == pt.DeviceAttribute:
			self.startLabel.setQuality(value.quality)
			self.endLabel.setQuality(value.quality)
			if value.value != None:
				val = value.value
				self.valueLabel.setText(str(val))
				self.valueSlider.setValue(val)
		else:
			val = value
			self.valueLabel.setText(str(val))
			self.valueSlider.setValue(val)
		self.update()

class QTangoReadAttributeSlider4(QTangoReadAttributeSlider2):
	def __init__(self, sizes = None, colors = None, parent=None):
		QTangoReadAttributeSlider2.__init__(self, sizes, colors, parent)

	def setupLayout(self):
		self.startLabel = QTangoStartLabel(self.sizes, self.attrColors)
		self.endLabel = QTangoEndLabel(self.sizes, self.attrColors)
		self.nameLabel = QTangoAttributeNameLabel(self.sizes, self.attrColors)
		self.unitLabel = QTangoAttributeUnitLabel(self.sizes, self.attrColors)
		sizesValue = copy.copy(self.sizes)
		sizesValue.barHeight *= 1.25
		self.valueSpinbox = QTangoReadAttributeSpinBox(sizesValue, self.attrColors)
		s = str(self.valueSpinbox.styleSheet())
		if s != '':
			i0 = s.find('\nmax-width')
			i1 = s[i0:].find(':')
			i2 = s[i0:].find(';')
			sNew = ''.join((s[0:i0+i1+1],' ', str(self.sizes.readAttributeWidth), s[i0+i2:]))
			self.valueSpinbox.setStyleSheet(sNew)
		self.valueSpinbox.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Minimum)

		self.valueSlider = QTangoHSliderBase2(self.sizes, self.attrColors)
		self.writeLabel = QTangoStartLabel(self.sizes, self.attrColors)
		self.writeLabel.currentAttrColor = self.attrColors.backgroundColor
		self.writeLabel.setupLayout()

		self.vSpacer = QtGui.QSpacerItem(20, self.sizes.barHeight, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.MinimumExpanding)

		self.layout = QtGui.QHBoxLayout(self)
		self.layout.setContentsMargins(0,0,0,0)
		self.layout.setMargin(int(self.sizes.barHeight/10))
		self.layout.setSpacing(self.sizes.barHeight/3)

		self.layoutGrid = QtGui.QGridLayout()
		self.layoutGrid.setContentsMargins(0, 0, 0, 0)
		self.layoutGrid.setMargin(int(self.sizes.barHeight/10))
		self.layoutGrid.setMargin(0)
		self.layoutGrid.addWidget(self.nameLabel, 0, 0, 1, 2)
#		self.layoutGrid.addWidget(self.unitLabel, 0, 1)
 		self.layoutGrid.addWidget(self.valueSpinbox, 1, 1)
 		self.layoutGrid.addItem(self.vSpacer, 2, 0)
		self.layoutGrid.addWidget(self.valueSlider, 2, 0, 1, 2)
# 		self.layoutGrid.addWidget(self.writeLabel, 1, 2)

		self.layoutGrid.setHorizontalSpacing(self.sizes.barHeight/4)
		self.layoutGrid.setVerticalSpacing(self.sizes.barHeight/10)

		self.layout.addWidget(self.startLabel)
		self.layout.addLayout(self.layoutGrid)
		self.layout.addWidget(self.endLabel)

		self.setMaximumWidth(self.sizes.readAttributeWidth)
		self.setMinimumWidth(self.sizes.readAttributeWidth)
		self.setMaximumHeight(self.sizes.barHeight*4)
		self.setMinimumHeight(self.sizes.barHeight*4)
		self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)

	def configureAttribute(self, attrInfo):
		QTangoReadAttributeSlider2.configureAttribute(self, attrInfo)
		self.valueSpinbox.setSuffix(''.join((' ', self.attrInfo.unit)))

	def setAttributeName(self, aName, aUnit = None):
		self.nameLabel.setText(aName)
		if aUnit != None:
			self.valueSpinbox.setSuffix(QtCore.QString.fromUtf8(''.join((' ', aUnit))))
		self.update()

class QTangoReadAttributeSliderCompact(QTangoAttributeBase):
	def __init__(self, sizes = None, colors = None, parent=None):
		QTangoAttributeBase.__init__(self, sizes, colors, parent)
		self.setupLayout()

	def setupLayout(self):
		self.startLabel = QTangoStartLabel(self.sizes, self.attrColors)
		self.endLabel = QTangoEndLabel(self.sizes, self.attrColors)
		self.nameLabel = QTangoAttributeNameLabel(self.sizes, self.attrColors)
		self.unitLabel = QTangoAttributeUnitLabel(self.sizes, self.attrColors)
		self.valueSpinbox = QTangoReadAttributeSpinBox(self.sizes, self.attrColors)
		self.valueSpinbox.setAlignment(QtCore.Qt.AlignRight)
		self.valueSlider = QTangoHSliderBaseCompact(self.sizes, self.attrColors)

		self.layout = QtGui.QHBoxLayout(self)
		self.layout.setContentsMargins(0,0,0,0)
		self.layout.setMargin(int(self.sizes.barHeight/10))
		self.layout.setMargin(0)
		self.layout.setSpacing(self.sizes.barWidth/3)

		self.layoutAttr = QtGui.QVBoxLayout()
#		self.layoutGrid.setContentsMargins(0, 0, 0, 0)
#		self.layoutGrid.setMargin(int(self.sizes.barHeight/10))
		self.layoutAttr.setMargin(0)
		self.layoutAttr.setSpacing(0)
		self.layoutAttr.setContentsMargins(0, 0, 0, 0)
		self.layoutData = QtGui.QHBoxLayout()
		self.layoutData.setMargin(0)
		self.layoutData.setContentsMargins(0, 0, 0, 0)
		self.layoutData.addWidget(self.nameLabel)
		self.layoutData.addWidget(self.valueSpinbox)
#		self.layoutData.addWidget(self.unitLabel)
		self.layoutAttr.addLayout(self.layoutData)
		self.layoutAttr.addWidget(self.valueSlider)

		self.layout.addWidget(self.startLabel)
		self.layout.addLayout(self.layoutAttr)
		self.layout.addWidget(self.endLabel)

		self.setMaximumWidth(self.sizes.readAttributeWidth)
		self.setMinimumWidth(self.sizes.readAttributeWidth)
		self.setMaximumHeight(self.sizes.barHeight*1.6)
		self.setMinimumHeight(self.sizes.barHeight*1.6)
		self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)

	def attributeName(self):
		return str(self.nameLabel.text())

	@QtCore.pyqtSignature('setAttributeName(QString)')

	def setAttributeName(self, aName, aUnit = None):
		self.nameLabel.setText(aName)
		if aUnit != None:
			self.unitLabel.setText(aUnit)
			self.valueSpinbox.setSuffix(''.join((' ', aUnit)))
		self.update()

	def setAttributeValue(self, value):
		if type(value) == pt.DeviceAttribute:
			self.startLabel.setQuality(value.quality)
			self.endLabel.setQuality(value.quality)
			self.nameLabel.setQuality(value.quality)
			if value.value != None:
				val = value.value
				self.valueSpinbox.setValue(val)
				self.valueSlider.setValue(val)
		else:
			val = value
			self.valueSpinbox.setValue(val)
			self.valueSlider.setValue(val)
		self.update()

	def setAttributeWarningLimits(self, limits):
		self.valueSlider.setWarningLimits(limits)

	def setSliderLimits(self, min, max):
		self.valueSlider.setSliderLimits(min, max)

	def configureAttribute(self, attrInfo):
		QTangoAttributeBase.configureAttribute(self, attrInfo)
		try:
			min_warning = float(self.attrInfo.alarms.min_warning)
		except:
			min_warning = -np.inf
		try:
			max_warning = float(self.attrInfo.alarms.max_warning)
		except:
			max_warning = np.inf
		self.setAttributeWarningLimits((min_warning, max_warning))
		self.unitLabel.setText(self.attrInfo.unit)
		self.valueSpinbox.setSuffix(''.join((' ', self.attrInfo.unit)))

class QTangoReadAttributeSliderV(QTangoReadAttributeSlider2):
	def __init__(self, sizes = None, colors = None, parent=None):
		QTangoAttributeBase.__init__(self, sizes, colors, parent)
		self.unit = None
		self.setupLayout()

	def setupLayout(self):
		self.nameLabel = QTangoAttributeNameLabel(self.sizes, self.attrColors)
		sizesValue = copy.copy(self.sizes)
		sizesValue.barHeight *= 1.25

		self.valueSlider = QTangoVSliderBase2(self.sizes, self.attrColors)
		self.writeLabel = QTangoStartLabel(self.sizes, self.attrColors)
		self.writeLabel.currentAttrColor = self.attrColors.backgroundColor
		self.writeLabel.setupLayout()

		self.vSpacer = QtGui.QSpacerItem(20, self.sizes.barHeight, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.MinimumExpanding)

		self.layout = QtGui.QVBoxLayout(self)
		self.layout.setContentsMargins(0,0,0,0)
		self.layout.setMargin(int(self.sizes.barHeight/10))
		self.layout.setSpacing(self.sizes.barHeight/10)

		self.layout.addWidget(self.valueSlider)
		self.layout.addWidget(self.nameLabel)

		self.setMaximumWidth(self.sizes.barWidth*4)
		self.setMinimumWidth(self.sizes.barWidth*4)
		self.setMaximumHeight(self.sizes.readAttributeHeight)
		self.setMinimumHeight(self.sizes.readAttributeHeight)
		self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)

	def attributeName(self):
		return str(self.nameLabel.text())

	@QtCore.pyqtSignature('setAttributeName(QString)')

	def setAttributeName(self, aName, aUnit = None):
		self.nameLabel.setText(aName)
		if aUnit != None:
			self.valueSlider.setUnit(aUnit)
			self.unit = aUnit
		self.update()

	def setAttributeValue(self, value):
		if type(value) == pt.DeviceAttribute:
			if value.value != None:
				val = value.value
				self.valueSlider.setValue(val)
				self.nameLabel.setQuality(value.quality)
		else:
			val = value
			self.valueSlider.setValue(val)
		self.update()

	def setAttributeWarningLimits(self, limits):
		self.valueSlider.setWarningLimits(limits)

	def setSliderLimits(self, min, max):
		self.valueSlider.setSliderLimits(min, max)

	def configureAttribute(self, attrInfo):
		QTangoAttributeBase.configureAttribute(self, attrInfo)
		try:
			min_warning = float(self.attrInfo.alarms.min_warning)
		except:
			min_warning = -np.inf
		try:
			max_warning = float(self.attrInfo.alarms.max_warning)
		except:
			max_warning = np.inf
		self.setAttributeWarningLimits((min_warning, max_warning))
		self.valueSlider.setUnit(self.attrInfo.unit)
		self.unit = self.attrInfo.unit


class QTangoReadAttributeBoolean(QTangoAttributeBase):
	def __init__(self, sizes = None, colors = None, parent=None):
		QTangoAttributeBase.__init__(self, sizes, colors, parent)
		self.setupLayout()

	def setupLayout(self):
		readValueWidth = self.sizes.barWidth
		readWidth = self.sizes.readAttributeWidth-self.sizes.barHeight/6-self.sizes.barHeight/2

		self.startLabel = QTangoStartLabel(self.sizes, self.attrColors)
		self.endLabel = QTangoEndLabel(self.sizes, self.attrColors)
		self.nameLabel = QTangoAttributeNameLabel(self.sizes, self.attrColors)
		self.valueBoolean = QTangoBooleanLabel(self.sizes, self.attrColors)


		self.layout = QtGui.QHBoxLayout(self)
		self.layout.setContentsMargins(0,0,0,0)
#		self.layout.setMargin(int(self.sizes.barHeight/10))
		self.layout.setMargin(0)
		self.layout.setSpacing(self.sizes.barWidth/3)

		self.layoutGrid = QtGui.QGridLayout()
		self.layoutGrid.setContentsMargins(0, 0, 0, 0)
#		self.layoutGrid.setMargin(int(self.sizes.barHeight/10))
		self.layoutGrid.setMargin(0)
		self.layoutGrid.addWidget(self.nameLabel, 0, 0, )
		self.layoutGrid.addWidget(self.valueBoolean, 0, 1)
		self.layoutGrid.setHorizontalSpacing(self.sizes.barWidth/4)
		self.layoutGrid.setVerticalSpacing(0)

		self.layout.addWidget(self.startLabel)
		self.layout.addLayout(self.layoutGrid)
		self.layout.addWidget(self.endLabel)

		self.setMaximumWidth(self.sizes.readAttributeWidth)
		self.setMinimumWidth(self.sizes.readAttributeWidth)
		self.setMaximumHeight(self.sizes.barHeight)
		self.setMinimumHeight(self.sizes.barHeight)
		self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)

	def attributeName(self):
		return str(self.nameLabel.text())

	@QtCore.pyqtSignature('setAttributeName(QString)')

	def setAttributeName(self, aName):
		self.nameLabel.setText(aName)
		self.update()

	def setAttributeValue(self, value):
		if type(value) == pt.DeviceAttribute:
			self.startLabel.setQuality(value.quality)
			self.endLabel.setQuality(value.quality)
			if value.dim_x>1:
				val = value.value[0]
			else:
				val = value.value
		else:
			val = value

		self.valueBoolean.setBooleanState(val)
		self.update()



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
#		self.layout.setMargin(int(self.sizes.barHeight/10))
		self.layout.setMargin(0)
		self.layout.setSpacing(self.sizes.barWidth/3)

		self.layoutGrid = QtGui.QGridLayout()
		self.layoutGrid.setContentsMargins(0, 0, 0, 0)
		self.layoutGrid.setMargin(0)
		self.layoutGrid.addWidget(self.nameLabel, 0, 0)
		self.layoutGrid.addWidget(self.valueSpinbox, 0, 1)
		self.layoutGrid.addWidget(self.valueTrend, 1, 0, 1, 2)
		self.layoutGrid.setHorizontalSpacing(self.sizes.barWidth/4)
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
		if type(value) == pt.DeviceAttribute:
			self.startLabel.setQuality(value.quality)
			self.endLabel.setQuality(value.quality)
			val = value.value
		else:
			val = value

		t = time.time()
		self.valueSpinbox.setValue(val)
		self.valueTrend.addPoint(t, val)
		self.update()

	def setAttributeWarningLimits(self, limits):
		self.valueTrend.setWarningLimits(limits)

	def setTrendLimits(self, low, high):
		self.valueTrend.setYRange(low, high, padding = 0.05)

class QTangoReadAttributeSpectrum(QTangoAttributeBase):
	def __init__(self, sizes = None, colors = None, parent=None):
		QTangoAttributeBase.__init__(self, sizes, colors, parent)
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
		self.layout.setMargin(int(self.sizes.barWidth/10))
#		self.layout.setMargin(0)
		self.layout.setSpacing(self.sizes.barWidth/3)

		self.layoutGrid = QtGui.QGridLayout()
		self.layoutGrid.setContentsMargins(0, 0, 0, 0)
		self.layoutGrid.setMargin(0)
		self.layoutGrid.addWidget(self.nameLabel, 0, 0)
		self.layoutGrid.addWidget(self.spectrum, 1, 0, 1, 2)
		self.layoutGrid.setHorizontalSpacing(self.sizes.barWidth/4)
		self.layoutGrid.setVerticalSpacing(0)

		self.layout.addWidget(self.startLabel)
		self.layout.addLayout(self.layoutGrid)
		self.layout.addWidget(self.endLabel)

		self.setMinimumWidth(self.sizes.readAttributeWidth)
		self.setMinimumHeight(self.sizes.barHeight*6)
		self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)

	def attributeName(self):
		return str(self.nameLabel.text())

	@QtCore.pyqtSignature('setAttributeName(QString)')

	def setAttributeName(self, aName):
		self.nameLabel.setText(aName)
		self.update()

	def setSpectrum(self, xData, yData):
		if type(xData) == pt.DeviceAttribute:
			xData = xData.value
		if type(yData) == pt.DeviceAttribute:
			self.startLabel.setQuality(yData.quality)
			self.endLabel.setQuality(yData.quality)
			self.nameLabel.setQuality(yData.quality)
			yData = yData.value
		self.spectrum.setSpectrum(xData, yData)

	def setXRange(self, low, high):
		self.spectrum.setXRange(low, high)

	def fixedSize(self, fixed = True):
		if fixed == True:
			self.spectrum.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
			self.setMaximumWidth(self.sizes.readAttributeWidth)
		else:
			self.spectrum.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

class QTangoReadAttributeImage(QTangoAttributeBase):
	def __init__(self, sizes = None, colors = None, parent=None):
		QTangoAttributeBase.__init__(self, sizes, colors, parent)
		self.setupLayout()

	def setupLayout(self):
		self.startLabel = QTangoStartLabel(self.sizes, self.attrColors)
		self.endLabel = QTangoEndLabel(self.sizes, self.attrColors)
		self.nameLabel = QTangoAttributeNameLabel(self.sizes, self.attrColors)
		self.imageWidget = QTangoImageBase(self.sizes, self.attrColors)

		self.layout = QtGui.QHBoxLayout(self)
		self.layout.setContentsMargins(0,0,0,0)
		self.layout.setMargin(int(self.sizes.barWidth/10))
#		self.layout.setMargin(0)
		self.layout.setSpacing(self.sizes.barWidth/3)

		self.layoutGrid = QtGui.QGridLayout()
		self.layoutGrid.setContentsMargins(0, 0, 0, 0)
		self.layoutGrid.setMargin(0)
		self.layoutGrid.addWidget(self.nameLabel, 0, 0)
		self.layoutGrid.addWidget(self.imageWidget, 1, 0, 1, 2)
		self.layoutGrid.setHorizontalSpacing(self.sizes.barWidth/4)
		self.layoutGrid.setVerticalSpacing(0)

		self.layout.addWidget(self.startLabel)
		self.layout.addLayout(self.layoutGrid)
		self.layout.addWidget(self.endLabel)

		self.setMinimumWidth(self.sizes.readAttributeWidth)
		self.setMinimumHeight(self.sizes.barHeight*6)
		self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)

	def attributeName(self):
		return str(self.nameLabel.text())

	@QtCore.pyqtSignature('setAttributeName(QString)')

	def setAttributeName(self, aName):
		self.nameLabel.setText(aName)
		self.update()

	def setImage(self, image):
		if type(image) == pt.DeviceAttribute:
			im = image.value
			self.startLabel.setQuality(image.quality)
			self.endLabel.setQuality(image.quality)
			self.nameLabel.setQuality(image.quality)
		self.imageWidget.setImage(im)

	def fixedSize(self, fixed = True):
		if fixed == True:
			self.imageWidget.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
			self.setMaximumWidth(self.sizes.readAttributeWidth)
		else:
			self.imageWidget.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)



class QTangoReadAttributeImageWithHist(QTangoAttributeBase):
	def __init__(self, sizes = None, colors = None, parent=None):
		QTangoAttributeBase.__init__(self, sizes, colors, parent)
		self.setupLayout()

	def setupLayout(self):
		self.startLabel = QTangoStartLabel(self.sizes, self.attrColors)
		self.endLabel = QTangoEndLabel(self.sizes, self.attrColors)
		self.nameLabel = QTangoAttributeNameLabel(self.sizes, self.attrColors)
		self.imageWidget = QTangoImageWithHistBase(self.sizes, self.attrColors)

		self.layout = QtGui.QHBoxLayout(self)
		self.layout.setContentsMargins(0,0,0,0)
		self.layout.setMargin(int(self.sizes.barWidth/10))
#		self.layout.setMargin(0)
		self.layout.setSpacing(self.sizes.barWidth/3)

		self.layoutGrid = QtGui.QGridLayout()
		self.layoutGrid.setContentsMargins(0, 0, 0, 0)
		self.layoutGrid.setMargin(0)
		self.layoutGrid.addWidget(self.nameLabel, 0, 0)
		self.layoutGrid.addWidget(self.imageWidget, 1, 0, 1, 2)
		self.layoutGrid.setHorizontalSpacing(self.sizes.barWidth/4)
		self.layoutGrid.setVerticalSpacing(0)

		self.layout.addWidget(self.startLabel)
		self.layout.addLayout(self.layoutGrid)
		self.layout.addWidget(self.endLabel)

		self.setMinimumWidth(self.sizes.readAttributeWidth)
		self.setMinimumHeight(self.sizes.barHeight*6)
		self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)

	def attributeName(self):
		return str(self.nameLabel.text())

	@QtCore.pyqtSignature('setAttributeName(QString)')

	def setAttributeName(self, aName):
		self.nameLabel.setText(aName)
		self.update()

	def setImage(self, image):
		if type(image) == pt.DeviceAttribute:
			im = image.value
			self.startLabel.setQuality(image.quality)
			self.endLabel.setQuality(image.quality)
		self.imageWidget.setImage(im, autoRange = False, autoLevels = False)



class QTangoWriteAttributeSlider(QTangoAttributeBase):
	def __init__(self, sizes = None, colors = None, parent=None):
		QTangoAttributeBase.__init__(self, sizes, colors, parent)
		self.setupLayout()

		self.writeValueInitialized = False

	def setupLayout(self):
		readValueWidth = self.sizes.barWidth
		readWidth = self.sizes.readAttributeWidth-self.sizes.barHeight/6-self.sizes.barHeight/2

		self.startLabel = QTangoStartLabel(self.sizes, self.attrColors)
		self.endLabel = QTangoEndLabel(self.sizes, self.attrColors)
		self.nameLabel = QTangoAttributeNameLabel(self.sizes, self.attrColors)
		self.unitLabel = QTangoAttributeUnitLabel(self.sizes, self.attrColors)
		self.valueSpinbox = QTangoReadAttributeSpinBox(self.sizes, self.attrColors)
		self.valueSlider = QTangoHSliderBase2(self.sizes, self.attrColors)
		self.writeValueSpinbox = QTangoWriteAttributeSpinBox(self.sizes, self.attrColors)
		self.writeValueSpinbox.editingFinished.connect(self.editingFinished)
		self.writeLabel = QTangoStartLabel(self.sizes, self.attrColors)
		self.writeLabel.currentAttrColor = self.attrColors.backgroundColor
		self.writeLabel.setupLayout()

		self.layout = QtGui.QHBoxLayout(self)
		self.layout.setContentsMargins(0,0,0,0)
#		self.layout.setMargin(int(self.sizes.barHeight/10))
		self.layout.setMargin(0)
		self.layout.setSpacing(self.sizes.barWidth/3)

		self.layoutGrid = QtGui.QGridLayout()
		self.layoutGrid.setContentsMargins(0, 0, 0, 0)
		self.layoutGrid.setMargin(int(self.sizes.barWidth/10))
		self.layoutGrid.setMargin(0)
		self.layoutGrid.setHorizontalSpacing(self.sizes.barWidth/4)
		self.layoutGrid.setVerticalSpacing(0)
		self.layoutGrid.addWidget(self.nameLabel, 0, 0)
		self.layoutGrid.addWidget(self.unitLabel, 0, 1)
		self.layoutGrid.addWidget(self.valueSlider, 1, 0, 1, 2)
		self.layoutGrid.addWidget(self.valueSpinbox, 0, 3)
		self.layoutGrid.addWidget(self.writeLabel, 1, 2)
		self.layoutGrid.addWidget(self.writeValueSpinbox, 1, 3)

		self.layout.addWidget(self.startLabel)
		self.layout.addLayout(self.layoutGrid)
		self.layout.addWidget(self.endLabel)

		self.setMaximumWidth(self.sizes.readAttributeWidth)
		self.setMinimumWidth(self.sizes.readAttributeWidth)
		self.setMaximumHeight(self.sizes.barHeight*2.2)
		self.setMaximumHeight(self.sizes.barHeight*2.7)
		#self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
		self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)

	def attributeName(self):
		return str(self.nameLabel.text())

	@QtCore.pyqtSignature('setAttributeName(QString)')

	def setAttributeName(self, aName, aUnit = None):
		self.nameLabel.setText(aName)
		if aUnit != None:
			self.unitLabel.setText(aUnit)
		self.update()

	def setAttributeValue(self, data):

		if type(data) == pt.DeviceAttribute:
			self.startLabel.setQuality(data.quality)
			self.endLabel.setQuality(data.quality)
			if data.value != None:
				self.valueSpinbox.setValue(data.value)
				self.valueSlider.setValue(data.value)
				if self.writeValueInitialized == False:
					print 'Initializing write value'
					self.writeValueInitialized = True
					self.setAttributeWriteValue(data.w_value)

				if data.w_value != self.writeValueSpinbox.value():
					if self.writeLabel.currentAttrColor != self.attrColors.secondaryColor0:
						self.writeLabel.currentAttrColor = self.attrColors.secondaryColor0
						self.writeLabel.setupLayout()
				else:
					if self.writeLabel.currentAttrColor != self.attrColors.backgroundColor:
						self.writeLabel.currentAttrColor = self.attrColors.backgroundColor
						self.writeLabel.setupLayout()
		else:
			self.valueSpinbox.setValue(data)
			self.valueSlider.setValue(data)
		self.update()

	def setAttributeWriteValue(self, value):
		self.writeValueSpinbox.setValue(value)
		self.valueSlider.setWriteValue(value)
		self.update()

	def setAttributeWarningLimits(self, limits):
		self.valueSlider.setWarningLimits(limits)

	def setSliderLimits(self, min, max):
		self.valueSlider.setSliderLimits(min, max)

	def editingFinished(self):
		self.valueSlider.setWriteValue(self.writeValueSpinbox.value())
		self.update()
		print 'updating slider to ', self.writeValueSpinbox.value()

	def getWriteValue(self):
		return self.writeValueSpinbox.value()

class QTangoWriteAttributeSlider4(QTangoWriteAttributeSlider):
	def __init__(self, sizes = None, colors = None, parent=None):
		QTangoWriteAttributeSlider.__init__(self, sizes, colors, parent)

	def setupLayout(self):
		self.startLabel = QTangoStartLabel(self.sizes, self.attrColors)
		self.endLabel = QTangoEndLabel(self.sizes, self.attrColors)
		self.nameLabel = QTangoAttributeNameLabel(self.sizes, self.attrColors)
		self.unitLabel = QTangoAttributeUnitLabel(self.sizes, self.attrColors)
		sizesValue = copy.copy(self.sizes)
		sizesValue.barHeight *= 1.25
		self.valueSpinbox = QTangoReadAttributeSpinBox(sizesValue, self.attrColors)
		s = str(self.valueSpinbox.styleSheet())
		if s != '':
			i0 = s.find('\nmax-width')
			i1 = s[i0:].find(':')
			i2 = s[i0:].find(';')
			sNew = ''.join((s[0:i0+i1+1],' ', str(self.sizes.readAttributeWidth), s[i0+i2:]))
			self.valueSpinbox.setStyleSheet(sNew)
		self.valueSpinbox.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Minimum)

		self.valueSlider = QTangoHSliderBase2(self.sizes, self.attrColors)
		self.writeValueSpinbox = QTangoWriteAttributeSpinBox2(sizesValue, self.attrColors)
		self.writeValueSpinbox.editingFinished.connect(self.editingFinished)
		self.writeLabel = QTangoStartLabel(self.sizes, self.attrColors)
		self.writeLabel.currentAttrColor = self.attrColors.backgroundColor
		self.writeLabel.setupLayout()
		s = str(self.writeValueSpinbox.styleSheet())
		if s != '':
			i0 = s.find('\nmax-width')
			i1 = s[i0:].find(':')
			i2 = s[i0:].find(';')
			sNew = ''.join((s[0:i0+i1+1],' ', str(self.sizes.readAttributeWidth), s[i0+i2:]))
			self.writeValueSpinbox.setStyleSheet(sNew)
		self.writeValueSpinbox.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Minimum)

		self.vSpacer = QtGui.QSpacerItem(20, self.sizes.barHeight, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.MinimumExpanding)

		self.layout = QtGui.QHBoxLayout(self)
		self.layout.setContentsMargins(0,0,0,0)
		self.layout.setMargin(int(self.sizes.barHeight/10))
		self.layout.setSpacing(self.sizes.barHeight/3)

		self.layoutGrid = QtGui.QVBoxLayout()
		self.layoutGrid.setContentsMargins(0, 0, 0, 0)
		self.layoutGrid.setMargin(int(self.sizes.barHeight/10))
#		self.layoutGrid.setMargin(0)
		self.layoutGrid.addWidget(self.nameLabel)
#		self.layoutGrid.addWidget(self.unitLabel, 0, 1)
		layoutSpinboxes = QtGui.QHBoxLayout()
		layoutSpinboxes.addWidget(self.writeValueSpinbox)
 		layoutSpinboxes.addWidget(self.valueSpinbox)
 		self.layoutGrid.addLayout(layoutSpinboxes)
 		self.layoutGrid.addItem(self.vSpacer)
		self.layoutGrid.addWidget(self.valueSlider)
# 		self.layoutGrid.addWidget(self.writeLabel, 1, 2)

#		self.layoutGrid.setHorizontalSpacing(self.sizes.barHeight/4)
		self.layoutGrid.setSpacing(self.sizes.barHeight/10)

		self.layout.addWidget(self.startLabel)
		self.layout.addLayout(self.layoutGrid)
		self.layout.addWidget(self.endLabel)

		self.setMaximumWidth(self.sizes.readAttributeWidth)
		self.setMinimumWidth(self.sizes.readAttributeWidth)
		self.setMaximumHeight(self.sizes.barHeight*4)
		self.setMinimumHeight(self.sizes.barHeight*4)
		self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)

	def configureAttribute(self, attrInfo):
		QTangoReadAttributeSlider2.configureAttribute(self, attrInfo)
		self.valueSpinbox.setSuffix(''.join((' ', self.attrInfo.unit)))

	def setAttributeName(self, aName, aUnit = None):
		self.nameLabel.setText(aName)
		if aUnit != None:
			self.valueSpinbox.setSuffix(QtCore.QString.fromUtf8(''.join((' ', aUnit))))
		self.update()

class QTangoWriteAttributeSliderV(QTangoWriteAttributeSlider):
	def __init__(self, sizes = None, colors = None, parent=None):
		QTangoWriteAttributeSlider.__init__(self, sizes, colors, parent)
		self.unit = None

	def setupLayout(self):
		self.nameLabel = QTangoAttributeNameLabel(self.sizes, self.attrColors)
		sizesValue = copy.copy(self.sizes)
		sizesValue.barHeight *= 1.25

		self.valueSlider = QTangoVSliderBase2(self.sizes, self.attrColors)
		self.writeLabel = QTangoStartLabel(self.sizes, self.attrColors)
		self.writeLabel.currentAttrColor = self.attrColors.backgroundColor
		self.writeLabel.setupLayout()
		self.writeValueSpinbox = QTangoWriteAttributeSpinBox2(self.sizes, self.attrColors)
		self.writeValueSpinbox.editingFinished.connect(self.editingFinished)
		self.writeValueSpinbox.setLayoutDirection(QtCore.Qt.RightToLeft)

		self.vSpacer = QtGui.QSpacerItem(20, self.sizes.barHeight, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.MinimumExpanding)

		self.layout = QtGui.QVBoxLayout(self)
		self.layout.setContentsMargins(0,0,0,0)
		self.layout.setMargin(int(self.sizes.barHeight/10))
		self.layout.setSpacing(self.sizes.barHeight/6.0)

		self.layout.addWidget(self.valueSlider)
		self.layout.addWidget(self.writeValueSpinbox)
		self.layout.addWidget(self.nameLabel)

		self.setMaximumWidth(self.sizes.barWidth*4)
		self.setMinimumWidth(self.sizes.barWidth*4)
		self.setMaximumHeight(self.sizes.readAttributeHeight)
		self.setMinimumHeight(self.sizes.readAttributeHeight)
		self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)

	def attributeName(self):
		return str(self.nameLabel.text())

	@QtCore.pyqtSignature('setAttributeName(QString)')

	def setAttributeName(self, aName, aUnit = None):
		self.nameLabel.setText(aName)
		if aUnit != None:
			self.valueSlider.setUnit(aUnit)
			self.unit = aUnit
		self.update()

	def setAttributeValue(self, data):
		if type(data) == pt.DeviceAttribute:
			if data.value != None:
				self.valueSlider.setValue(data.value)
				if self.writeValueInitialized == False:
					print 'Initializing write value'
					self.writeValueInitialized = True
					self.setAttributeWriteValue(data.w_value)

				if data.w_value != self.writeValueSpinbox.value():
					if self.writeLabel.currentAttrColor != self.attrColors.secondaryColor0:
						self.writeLabel.currentAttrColor = self.attrColors.secondaryColor0
						self.writeLabel.setupLayout()
				else:
					if self.writeLabel.currentAttrColor != self.attrColors.backgroundColor:
						self.writeLabel.currentAttrColor = self.attrColors.backgroundColor
						self.writeLabel.setupLayout()
		else:
			self.valueSlider.setValue(data)
		self.update()


	def setAttributeWarningLimits(self, limits):
		self.valueSlider.setWarningLimits(limits)

	def setSliderLimits(self, min, max):
		self.valueSlider.setSliderLimits(min, max)

	def configureAttribute(self, attrInfo):
		QTangoAttributeBase.configureAttribute(self, attrInfo)
		try:
			min_warning = float(self.attrInfo.alarms.min_warning)
		except:
			min_warning = -np.inf
		try:
			max_warning = float(self.attrInfo.alarms.max_warning)
		except:
			max_warning = np.inf
		self.setAttributeWarningLimits((min_warning, max_warning))
		self.valueSlider.setUnit(self.attrInfo.unit)
		self.unit = self.attrInfo.unit

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
		if type(value) == pt.DeviceAttribute:
			self.startLabel.setQuality(value.quality)
			self.endLabel.setQuality(value.quality)
			val = value.value
		else:
			val = value

		self.readValueSpinbox.setValue(val)
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

class QTangoDeviceNameStatus(QTangoAttributeBase):
	def __init__(self, sizes = None, colors = None, parent=None):
		QTangoAttributeBase.__init__(self, sizes, colors, parent)
		self.setupLayout()

	def setupLayout(self):
		readValueWidth = self.sizes.barWidth
		readWidth = self.sizes.readAttributeWidth-self.sizes.barHeight/6-self.sizes.barHeight/2

		self.startLabel = QTangoStartLabel(self.sizes, self.attrColors)
		self.endLabel = QTangoEndLabel(self.sizes, self.attrColors)
		self.nameLabel = QTangoAttributeNameLabel(self.sizes, self.attrColors)

# 	def setupLayout(self):
# 		self.startLabel = QtGui.QLabel('')
# 		st = ''.join(('QLabel {min-height: ', str(self.sizes.barHeight), 'px; \n',
# 					'min-width: ', str(int(self.sizes.barHeight / 6)), 'px; \n',
# 					'max-width: ', str(int(self.sizes.barHeight / 6)), 'px; \n',
# 					'max-height: ', str(self.sizes.barHeight), 'px; \n',
# 					'background-color: ', self.attrColors.secondaryColor0, ';}'))
# 		self.startLabel.setStyleSheet(st)
# 		self.endLabel = QtGui.QLabel('')
# 		st = ''.join(('QLabel {min-height: ', str(self.sizes.barHeight), 'px; \n',
# 					'min-width: ', str(int(self.sizes.barHeight / 2)), 'px; \n',
# 					'max-width: ', str(int(self.sizes.barHeight / 2)), 'px; \n',
# 					'max-height: ', str(self.sizes.barHeight), 'px; \n',
# 					'background-color: ', self.attrColors.secondaryColor0, ';}'))
# 		self.endLabel.setStyleSheet(st)
#
# 		self.nameLabel = QtGui.QLabel('Test')
# 		s = ''.join(('QLabel {min-height: ', str(self.sizes.barHeight), 'px; \n',
# 					'max-height: ', str(self.sizes.barHeight), 'px; \n',
# 					'background-color: ', self.attrColors.backgroundColor, '; \n',
# 					'color: ', self.attrColors.secondaryColor0, ';}'))
# 		self.nameLabel.setStyleSheet(s)
#
# 		font = self.nameLabel.font()
# 		font.setFamily(self.sizes.fontType)
# 		font.setStretch(self.sizes.fontStretch)
# 		font.setPointSize(int(self.sizes.barHeight * 0.7))
# 		font.setStyleStrategy(QtGui.QFont.PreferAntialias)
# 		self.nameLabel.setFont(font)
# 		self.nameLabel.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
#
#
		layout = QtGui.QHBoxLayout(self)
		layout.setContentsMargins(0,0,0,0)
#		layout.setMargin(int(self.sizes.barHeight/10))
		layout.setMargin(0)
#
# #		layout.addSpacerItem(spacerItem)
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
		self.endLabel.setState(state)
		self.startLabel.setState(state)
		self.nameLabel.setState(state)


