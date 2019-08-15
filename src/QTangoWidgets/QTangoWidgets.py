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
import re
import decimal
import logging

logger = logging.getLogger("QTangoWidgets")
logger.setLevel(logging.INFO)
f = logging.Formatter("%(asctime)s - %(name)s.   %(funcName)s - %(levelname)s - %(message)s")
fh = logging.StreamHandler()
fh.setFormatter(f)
logger.addHandler(fh)

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
        self.primaryColor3 = '#bb6622'
        self.primaryColor4 = '#aa5533'
        self.primaryColor5 = '#882211'
        self.secondaryColor0 = '#66cbff'
        self.secondaryColor1 = '#3399ff'
        self.secondaryColor2 = '#99cdff'
        self.secondaryColor3 = '#3366cc'
        self.secondaryColor4 = '#000088'
        self.tertiaryColor0 = '#cc99cc'
        self.tertiaryColor1 = '#cc6699'
        self.tertiaryColor2 = '#cc6666'
        self.tertiaryColor3 = '#664466'
        self.tertiaryColor4 = '#9977aa'

        self.faultColor = '#ff0000'
        #		self.alarmColor2 = '#f7bd5a'
        self.alarmColor2 = '#ffffff'
        self.warnColor = '#a35918'
        self.alarmColor = '#ff0000'
        #		self.warnColor2 = '#cb99cc'
        self.warnColor2 = '#ffcc33'
        self.onColor = '#99dd66'
        self.offColor = '#ffffff'
        self.standbyColor = '#9c9cff'
        self.unknownColor = '#45616f'
        self.disableColor = '#ff00ff'
        self.movingColor = '#feff99'
        self.runningColor = '#feff99'

        self.validColor = self.secondaryColor0
        self.invalidColor = self.unknownColor
        self.changingColor = self.secondaryColor1

        self.legend_color_list = [self.secondaryColor0,
                                  self.primaryColor2,
                                  self.tertiaryColor1,
                                  self.secondaryColor3,
                                  self.primaryColor3,
                                  self.tertiaryColor4,
                                  self.primaryColor5,
                                  self.secondaryColor4,
                                  self.tertiaryColor3]


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

# Regular expression to find floats. Match groups are the whole string, the
# whole coefficient, the decimal part of the coefficient, and the exponent
# part.
_float_re = re.compile(r'(([+-]?\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?)')


def valid_float_string(string):
    match = _float_re.search(string)
    return match.groups()[0] == string if match else False


class FloatValidator(QtGui.QValidator):
    def validate(self, string, position):
        string = str(string)
        if valid_float_string(string):
            return self.Acceptable
        if string == "" or string[position - 1] in 'e.-+':
            return self.Intermediate
        return self.Invalid

    def fixup(self, text):
        match = _float_re.search(text)
        return match.groups()[0] if match else ""


def format_float(value):
    """Modified form of the 'g' format specifier."""
    string = "{0:.4g}".format(value).replace("e+", "e")
    string = re.sub("e(-?)0*(\d+)", r"e\1\2", string)
    return string


def to_precision(x, p):
    """
    returns a string representation of x formatted with a precision of p

    Based on the webkit javascript implementation taken from here:
    https://code.google.com/p/webkit-mirror/source/browse/JavaScriptCore/kjs/number_object.cpp
    """
    x = float(x)
    if x == 0.:
        return "0." + "0" * (p - 1)

    out = []

    if x < 0:
        out.append("-")
        x = -x

    e = int(np.log10(x))
    tens = 10 ** (e - p + 1)
    n = np.floor(x / tens)

    if n < 10 ** (p - 1):
        e -= 1
        tens = 10 ** (e - p + 1)
        n = np.floor(x / tens)

    if abs((n + 1.) * tens - x) <= abs(n * tens - x):
        n += 1

    if n >= 10 ** p:
        n /= 10.
        e += 1

    m = "%.*g" % (p, n)

    if e < -2 or e >= p:
        out.append(m[0])
        if p > 1:
            out.append(".")
            out.extend(m[1:p])
        out.append('e')
        if e > 0:
            out.append("+")
        out.append(str(e))
    elif e == (p - 1):
        out.append(m)
    elif e >= 0:
        out.append(m[:e + 1])
        if e + 1 < len(m):
            out.append(".")
            out.extend(m[e + 1:])
    else:
        out.append("0.")
        out.extend(["0"] * -(e + 1))
        out.append(m)

    return "".join(out)


class QTangoAttributeBase(QtGui.QWidget):
    def __init__(self, sizes=None, colors=None, parent=None):
        QtGui.QWidget.__init__(self, parent)
        if colors is None:
            self.attrColors = QTangoColors()
        else:
            self.attrColors = colors
        if sizes is None:
            self.sizes = QTangoSizes()
        else:
            self.sizes = sizes

        self.state = 'UNKNOWN'
        self.quality = 'UNKNOWN'
        self.currentAttrColor = self.attrColors.secondaryColor0
        self.currentAttrColor = self.attrColors.unknownColor

        self.attrInfo = None

    def setState(self, state, use_background_color=False):
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
        elif state_str == str(pt.DevState.RUNNING):
            color = self.attrColors.runningColor
            stateString = 'RUNNING'
        elif state_str == str(pt.AttrQuality.ATTR_WARNING):
            color = self.attrColors.warnColor
            stateString = 'WARNING'
        elif state_str == str(pt.AttrQuality.ATTR_CHANGING):
            color = self.attrColors.changingColor
            stateString = 'CHANGING'
        elif state_str == str(pt.AttrQuality.ATTR_ALARM):
            color = self.attrColors.alarmColor2
            stateString = 'ALARM'
        elif state_str == str(pt.AttrQuality.ATTR_INVALID):
            color = self.attrColors.invalidColor
            stateString = 'INVALID'
        elif state_str == str(pt.AttrQuality.ATTR_VALID):
            color = self.attrColors.validColor
            stateString = 'VALID'
        else:
            color = self.attrColors.unknownColor
            stateString = 'UNKNOWN'

        self.state = stateString
        self.currentAttrColor = color

        s = str(self.styleSheet())
        if s != '':
            if use_background_color is True:
                i0 = s.find('\nbackground-color')
            else:
                i0 = s.find('\ncolor')
            i1 = s[i0:].find(':')
            i2 = s[i0:].find(';')
            sNew = ''.join((s[0:i0 + i1 + 1], ' ', color, s[i0 + i2:]))
            self.setStyleSheet(sNew)

        self.update()

    def setQuality(self, quality, use_background_color=False):
        if type(quality) == pt.DeviceAttribute:
            logger.debug("Device attribute quality: {0}".format(quality.value))
            state_str = str(quality.value)
        else:
            state_str = str(quality)
            logger.debug("Quality string: {0}".format(quality))
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
            color = self.attrColors.warnColor2
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
            if use_background_color is True:
                i0 = s.find('\nbackground-color')
            else:
                i0 = s.find('\ncolor')
            i1 = s[i0:].find(':')
            i2 = s[i0:].find(';')
            sNew = ''.join((s[0:i0 + i1 + 1], ' ', color, s[i0 + i2:]))
            self.setStyleSheet(sNew)

        self.update()

    def setupLayout(self):
        pass

    def configureAttribute(self, attrInfo):
        self.attrInfo = attrInfo


# noinspection PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit
class QTangoTitleBar(QtGui.QWidget):
    def __init__(self, title='', sizes=None, colors=None, parent=None):
        QtGui.QWidget.__init__(self, parent)
        if title is None:
            self.title = ''
        else:
            self.title = title
        if sizes is None:
            self.sizes = QTangoSizes()
        else:
            self.sizes = sizes
        if colors is None:
            self.attrColors = QTangoColors()
        else:
            self.attrColors = colors

        self.setupLayout()

    def setupLayout(self):
        barHeight = self.sizes.barHeight
        self.startLabel = QtGui.QLabel('')
        s = ''.join(('QLabel {min-height: ', str(int(barHeight * 1.25)), 'px; \n',
                     'min-width: ', str(int(barHeight * 1.25 / 3)), 'px; \n',
                     'max-height: ', str(int(barHeight * 1.25)), 'px; \n',
                     'background-color: ', self.attrColors.primaryColor0, '; \n',
                     '}'))
        self.startLabel.setStyleSheet(s)

        self.startLabel.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)

        self.endLabel = QtGui.QLabel('')
        s = ''.join(('QLabel {min-height: ', str(int(barHeight * 1.25)), 'px; \n',
                     'min-width: ', str(int(barHeight * 1.25)), 'px; \n',
                     'max-height: ', str(int(barHeight * 1.25)), 'px; \n',
                     'background-color: ', self.attrColors.primaryColor0, '; \n',
                     '}'))
        self.endLabel.setStyleSheet(s)

        self.nameLabel = QtGui.QLabel('')
        s = ''.join(('QLabel {min-height: ', str(int(barHeight * 1.25)), 'px; \n',
                     'max-height: ', str(int(barHeight * 1.25)), 'px; \n',
                     'background-color: ', self.attrColors.backgroundColor, '; \n',
                     'color: ', self.attrColors.primaryColor0, '; \n',
                     '}'))
        self.nameLabel.setStyleSheet(s)

        self.nameLabel.setText(self.title.upper())
        font = self.nameLabel.font()
        font.setFamily(self.sizes.fontType)
        font.setStretch(self.sizes.fontStretch)
        font.setWeight(self.sizes.fontWeight)
        #		font.setFamily('TrebuchetMS')
        #		font.setStretch(QtGui.QFont.Condensed)
        #		font.setWeight(QtGui.QFont.Light)
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

    def setName(self, name):
        self.nameLabel.setText(name)


# noinspection PyAttributeOutsideInit,PyAttributeOutsideInit
class QTangoSideBar(QtGui.QWidget):
    def __init__(self, sizes=None, colors=None, parent=None):
        QtGui.QWidget.__init__(self, parent)
        if colors is None:
            self.attrColors = QTangoColors()
        else:
            self.attrColors = colors
        if sizes is None:
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

        if self.layout is not None:
            for i in reversed(range(self.layout.count())):
                self.layout.itemAt(i).widget().setParent(None)
        if self.layout is None:
            self.layout = QtGui.QVBoxLayout(self)
        self.layout.setMargin(0)
        self.layout.setSpacing(int(self.sizes.barHeight / 10))
        self.layout.addWidget(self.startLabel)
        for cmdButton in self.cmdButtons.itervalues():
            self.layout.addWidget(cmdButton)
        self.layout.addWidget(self.endLabel)

        self.update()

    def addCmdButton(self, title, slot=None):
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

        if slot is not None:
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


class QTangoContentWidget(QtGui.QWidget):
    def __init__(self, name, sizes=None, colors=None, parent=None):
        QtGui.QWidget.__init__(self, parent)
        if colors is None:
            self.attrColors = QTangoColors()
        else:
            self.attrColors = colors
        if sizes is None:
            self.sizes = QTangoSizes()
        else:
            self.sizes = sizes
        self.layout = None
        self.name = name
        self.setupLayout()

    def setupLayout(self):
        colors = self.attrColors
        colors.primaryColor0 = colors.secondaryColor0
        self.title_bar = QTangoTitleBar(self.name, sizes=self.sizes, colors=colors)
        # self.title_bar.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        self.side_bar = QTangoSideBar(colors=self.attrColors, sizes=self.sizes)
        self.layout = QtGui.QVBoxLayout()
        self.layout.setMargin(0)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)
        self.setMinimumHeight(self.sizes.readAttributeHeight * 1.2)
        self.layout_bar = QtGui.QHBoxLayout()
        self.layout_content = QtGui.QHBoxLayout()
        self.layout_content.setMargin(self.sizes.barHeight)
        self.layout_content.setSpacing(self.sizes.barHeight * 2)
        self.layout_content.setContentsMargins(self.sizes.barHeight * 1.25,
                                               self.sizes.barHeight * 1.25,
                                               self.sizes.barHeight,
                                               self.sizes.barHeight)
        self.layout.addWidget(self.title_bar)
        self.layout.addLayout(self.layout_bar)
        self.layout_bar.addWidget(self.side_bar)
        self.layout_bar.addLayout(self.layout_content)

    def addLayout(self, layout):
        self.layout_content.addLayout(layout)

    def addWidget(self, widget):
        self.layout_content.addWidget(widget)

    def addSpacerItem(self, spaceritem):
        self.layout_content.addSpacerItem(spaceritem)


class QTangoCommandButton(QtGui.QPushButton, QTangoAttributeBase):
    def __init__(self, title, slot=None, sizes=None, colors=None, parent=None):
        QTangoAttributeBase.__init__(self, sizes, colors, parent)
        QtGui.QPushButton.__init__(self, parent)
        self.name = title

        if slot is not None:
            self.clicked.connect(slot)

        self.setupLayout()

    # cmdButton = QtGui.QPushButton('CMD ')
    def setupLayout(self):
        buttonHeight = self.sizes.barHeight * 1.75
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
        font.setStretch(self.sizes.fontStretch)  # QtGui.QFont.Condensed)
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

        buttonHeight = self.sizes.barHeight * 1.75
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


# noinspection PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit
class QTangoCommandSelection(QTangoAttributeBase):
    def __init__(self, title, sizes=None, colors=None, parent=None):
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
            self.layout.setContentsMargins(0, 0, 0, 0)
            #			self.layout.setMargin(int(self.sizes.barHeight/5))
            self.layout.setMargin(0)
            #			self.layout.setSpacing(self.sizes.barHeight/3)
            self.layout.setSpacing(self.sizes.barWidth / 3)

            self.layout2 = QtGui.QVBoxLayout()
            self.layout2.setContentsMargins(0, 0, 0, 0)
            #			self.layout2.setMargin(int(self.sizes.barHeight/5))
            self.layout2.setMargin(0)

            self.layoutInfo = QtGui.QHBoxLayout()
            self.layoutInfo.setContentsMargins(0, 0, 0, 0)
            #			self.layoutInfo.setMargin(int(self.sizes.barHeight/10))
            self.layoutInfo.setMargin(0)
            self.layoutInfo.setSpacing(int(self.sizes.barWidth / 6))
            self.layoutInfo.addWidget(self.nameLabel)
            self.layoutInfo.addWidget(self.statusLabel)
            self.layoutButtons = QtGui.QHBoxLayout()
            self.layoutButtons.setContentsMargins(0, 0, 0, 0)
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

    def setStatus(self, status, state=None):
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
        if statusText is not None:
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
    def __init__(self, sizes=None, colors=None, parent=None):
        QTangoAttributeBase.__init__(self, sizes, colors, parent)
        QtGui.QLabel.__init__(self, parent)
        self.setupLayout()

    def setQuality(self, quality):
        QTangoAttributeBase.setQuality(self, quality, use_background_color=True)

    def setState(self, state):
        QTangoAttributeBase.setState(self, state, use_background_color=True)

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
    def __init__(self, sizes=None, colors=None, parent=None):
        QtGui.QLabel.__init__(self, parent)
        if colors is None:
            self.attrColors = QTangoColors()
        else:
            self.attrColors = colors
        if sizes is None:
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
        if boolState is False:
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
    def __init__(self, sizes=None, colors=None, parent=None):
        QTangoAttributeBase.__init__(self, sizes, colors, parent)
        QtGui.QLabel.__init__(self, parent)
        self.setupLayout()

    def setQuality(self, quality):
        QTangoAttributeBase.setQuality(self, quality, use_background_color=True)

    def setState(self, state):
        QTangoAttributeBase.setState(self, state, use_background_color=True)

    def setupLayout(self):
        st = ''.join(('QLabel {min-height: ', str(self.sizes.barHeight), 'px; \n',
                      'min-width: ', str(int(self.sizes.barWidth)), 'px; \n',
                      'max-width: ', str(int(self.sizes.barWidth)), 'px; \n',
                      'background-color: ', self.currentAttrColor, ';}'))
        self.setStyleSheet(st)


class QTangoAttributeNameLabel(QtGui.QLabel, QTangoAttributeBase):
    def __init__(self, sizes=None, colors=None, parent=None):
        QTangoAttributeBase.__init__(self, sizes, colors, parent)
        QtGui.QLabel.__init__(self, parent)
        self.name_text = ''
        self.currentAttrColor = self.attrColors.secondaryColor0
        self.setupLayout()

    def setupLayout(self):
        self.setText('')
        # s = ''.join(('QLabel { \n',
        #              'background-color: ', self.attrColors.backgroundColor, '; \n',
        #              #			'selection-background-color: ', self.attrColors.secondaryColor1, '; \n',
        #              #			'selection-color: ', self.attrColors.backgroundColor, '; \n',
        #              #			'border-width: ', str(int(self.sizes.barHeight/10)), 'px; \n',
        #              'border-width: ', str(int(1)), 'px; \n',
        #              'border-color: ', self.attrColors.backgroundColor, '; \n',
        #              'border-top-style: solid; \n',
        #              'border-bottom-style: solid; \n',
        #              'border-left-style: double; \n',
        #              'border-right-style: solid; \n',
        #              'border-radius: 0px; \n',
        #              'padding: 0px; \n',
        #              'margin: 0px; \n',
        #              'min-width: ', str(int(self.sizes.barHeight) * 1), 'px; \n',
        #              'max-width: ', str(int(self.sizes.barHeight) * 4), 'px; \n',
        #              'min-height: ', str(int(self.sizes.barHeight * 1.3)), 'px; \n',
        #              'max-height: ', str(int(self.sizes.barHeight * 1.3)), 'px; \n',
        #              'qproperty-readOnly: 1; \n',
        #              'color: ', self.attrColors.secondaryColor0, ';} \n'))
        s = ''.join(('QLabel {min-height: ', str(self.sizes.barHeight), 'px; \n',
                     'max-height: ', str(self.sizes.barHeight), 'px; \n',
                     # 					'min-width: ', str(int(readWidth)), 'px; \n',
                     # 					'max-width: ', str(int(readWidth)), 'px; \n',
                     'background-color: ', self.attrColors.backgroundColor, '; \n',
                     'color: ', self.currentAttrColor, ';}'))
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
        s = ''.join(('QLabel {min-height: ', str(self.sizes.barHeight), 'px; \n',
                     'max-height: ', str(self.sizes.barHeight), 'px; \n',
                     'background-color: ', self.attrColors.backgroundColor, '; \n',
                     'color: ', self.currentAttrColor, ';}'))
        self.setStyleSheet(s)
        #		QtGui.QLabel.setText(self, "".join(("<font color=", self.currentAttrColor, ">", self.name_text, "</font>")))

        self.update()


# def setText(self, s):
#		self.name_text = str(s)
#		QtGui.QLabel.setText(self, "".join(("<font color=", self.currentAttrColor, ">", self.name_text, "</font>")))


class QTangoStateLabel(QtGui.QLabel, QTangoAttributeBase):
    def __init__(self, sizes=None, colors=None, parent=None):
        QTangoAttributeBase.__init__(self, sizes, colors, parent)
        QtGui.QLabel.__init__(self, parent)
        self.currentAttrColor = self.attrColors.secondaryColor0
        self.setupLayout()

    def setupLayout(self):
        self.setText('')
        s = ''.join(('QLabel {min-height: ', str(self.sizes.barHeight), 'px; \n',
                     'max-height: ', str(self.sizes.barHeight), 'px; \n',
                     'background-color: ', self.attrColors.backgroundColor, '; \n',
                     'color: ', self.currentAttrColor, ';}'))
        self.setStyleSheet(s)

        font = self.font()
        font.setFamily(self.sizes.fontType)
        font.setStretch(self.sizes.fontStretch)
        font.setWeight(self.sizes.fontWeight)
        font.setPointSize(int(self.sizes.barHeight * 0.7))
        font.setStyleStrategy(QtGui.QFont.PreferAntialias)
        self.setFont(font)
        self.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)

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
        s = ''.join(('QLabel {min-height: ', str(self.sizes.barHeight), 'px; \n',
                     'max-height: ', str(self.sizes.barHeight), 'px; \n',
                     'background-color: ', self.attrColors.backgroundColor, '; \n',
                     'color: ', self.currentAttrColor, ';}'))
        self.setStyleSheet(s)
        self.update()

    def setState(self, state):
        QTangoAttributeBase.setState(self, state)
        self.setText(self.state)


class QTangoAttributeUnitLabel(QtGui.QLabel, QTangoAttributeBase):
    def __init__(self, sizes=None, colors=None, parent=None):
        QTangoAttributeBase.__init__(self, sizes, colors, parent)
        QtGui.QLabel.__init__(self, parent)
        self.unit_text = ''
        self.currentAttrColor = self.attrColors.secondaryColor0
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
                     'color: ', self.currentAttrColor, ';}'))
        self.setStyleSheet(s)

    def setText(self, unitText):
        if unitText == '':
            #			txt = '[a.u.]'
            txt = 'a.u.'
        else:
            #			txt=''.join(('[', unitText, ']'))
            txt = ''.join(('', unitText, ''))
        self.unit_text = txt
        #		QtGui.QLabel.setText(self, "".join(("<font color=", self.currentAttrColor, ">", self.unit_text, "</font>")))
        QtGui.QLabel.setText(self, txt)

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

        s = ''.join(('QLabel {min-height: ', str(self.sizes.barHeight), 'px; \n',
                     'max-height: ', str(self.sizes.barHeight), 'px; \n',
                     'background-color: ', self.attrColors.backgroundColor, '; \n',
                     'color: ', self.currentAttrColor, ';}'))
        self.setStyleSheet(s)
        #		QtGui.QLabel.setText(self, "".join(("<font color=", self.currentAttrColor, ">", self.unit_text, "</font>")))

        self.update()


# noinspection PyAttributeOutsideInit
class QTangoReadAttributeSpinBox(QtGui.QDoubleSpinBox, QTangoAttributeBase):
    def __init__(self, sizes=None, colors=None, parent=None):
        QTangoAttributeBase.__init__(self, sizes, colors, parent)
        QtGui.QDoubleSpinBox.__init__(self, parent)
        self.setupLayout()

    def setupLayout(self):
        self.setLocale(QtCore.QLocale(QtCore.QLocale.English))
        # 		s = ''.join(('QDoubleSpinBox { \n',
        #             'background-color: ', self.attrColors.backgroundColor, '; \n',
        #             'border-width: 0px; \n',
        #             'border-color: #339; \n',
        #             'border-style: solid; \n',
        #             'border-radius: 0; \n',
        #             'border: 0px; \n',
        #             'padding: 0px; \n',
        #             'margin: 0px; \n',
        #             'qproperty-buttonSymbols: NoButtons; \n',
        #             'min-width: ', str(int(self.sizes.barHeight)*2.5), 'px; \n',
        # 			'max-width: ', str(int(self.sizes.barHeight)*2.5), 'px; \n',
        #             'min-height: ', str(self.sizes.barHeight), 'px; \n',
        #             'max-height: ', str(self.sizes.barHeight), 'px; \n',
        #             'qproperty-readOnly: 1; \n',
        #             'color: ', self.attrColors.secondaryColor0, ';} \n'))
        s = ''.join(('QDoubleSpinBox { \n',
                     'background-color: ', self.attrColors.backgroundColor, '; \n',
                     'selection-background-color: ', self.attrColors.secondaryColor1, '; \n',
                     'selection-color: ', self.attrColors.backgroundColor, '; \n',
                     #			'border-width: ', str(int(self.sizes.barHeight/10)), 'px; \n',
                     'border-width: ', str(int(1)), 'px; \n',
                     'border-color: ', self.attrColors.backgroundColor, '; \n',
                     'border-top-style: solid; \n',
                     'border-bottom-style: solid; \n',
                     'border-left-style: double; \n',
                     'border-right-style: solid; \n',
                     'border-radius: 0px; \n',
                     'padding: 0px; \n',
                     'margin: 0px; \n',
                     'qproperty-buttonSymbols: NoButtons; \n',
                     #			'qproperty-buttonSymbols: UpDownArrows; \n',
                     #			'min-width: ', str(int(self.sizes.barHeight)*2.5), 'px; \n',
                     'min-width: ', str(int(self.sizes.barHeight) * 1), 'px; \n',
                     'max-width: ', str(int(self.sizes.barHeight) * 4), 'px; \n',
                     'min-height: ', str(int(self.sizes.barHeight * 1.3)), 'px; \n',
                     'max-height: ', str(int(self.sizes.barHeight * 1.3)), 'px; \n',
                     'qproperty-readOnly: 1; \n',
                     #			'color: ', self.attrColors.secondaryColor0,
                     #			'color: ', self.currentAttrColor,
                     ';} \n'))

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
        self.setMaximum(np.inf)
        self.setMinimum(-np.inf)

        self.validator = FloatValidator()

    def setValue(self, value):
        if type(value) == pt.DeviceAttribute:
            self.setQuality(value.quality)
            val = value.value
        else:
            val = value
        if val != None:
            QtGui.QDoubleSpinBox.setValue(self, val)
        else:
            QtGui.QDoubleSpinBox.setValue(self, 0.0)
        #		QtGui.QDoubleSpinBox.setValue(self,val)

    def validate(self, text, position):
        return self.validator.validate(text, position)

    def fixup(self, text):
        return self.validator.fixup(text)

    def valueFromText(self, text):
        return float(text)

    def textFromValue(self, value):
        return format_float(value)

    def stepBy(self, steps):
        text = self.cleanText()
        groups = _float_re.search(text).groups()
        decimal = float(groups[1])
        decimal += steps
        new_string = "{:g}".format(decimal) + (groups[3] if groups[3] else "")
        self.lineEdit().setText(new_string)


# noinspection PyAttributeOutsideInit
class QTangoReadAttributeLabel(QtGui.QLabel, QTangoAttributeBase):
    def __init__(self, sizes=None, colors=None, precision=4, parent=None):
        QTangoAttributeBase.__init__(self, sizes, colors, parent)
        QtGui.QLabel.__init__(self, parent)
        self.precision = 4
        self.currentAttrColor = self.attrColors.secondaryColor0
        self.setupLayout()

    def setupLayout(self):
        self.setLocale(QtCore.QLocale(QtCore.QLocale.English))
        s = ''.join(('QLabel { \n',
                     'background-color: ', self.attrColors.backgroundColor, '; \n',
                     'selection-background-color: ', self.attrColors.secondaryColor1, '; \n',
                     'selection-color: ', self.attrColors.backgroundColor, '; \n',
                     #			'border-width: ', str(int(self.sizes.barHeight/10)), 'px; \n',
                     'border-width: ', str(int(1)), 'px; \n',
                     'border-color: ', self.attrColors.backgroundColor, '; \n',
                     'border-top-style: solid; \n',
                     'border-bottom-style: solid; \n',
                     'border-left-style: double; \n',
                     'border-right-style: solid; \n',
                     'border-radius: 0px; \n',
                     'padding: 0px; \n',
                     'margin: 0px; \n',
                     'min-width: ', str(int(self.sizes.barHeight) * 1), 'px; \n',
                     'max-width: ', str(int(self.sizes.barHeight) * 4), 'px; \n',
                     'min-height: ', str(int(self.sizes.barHeight * 1.3)), 'px; \n',
                     'max-height: ', str(int(self.sizes.barHeight * 1.3)), 'px; \n',
                     'color: ', self.currentAttrColor, ';} \n'))

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

        self.validator = FloatValidator()

    def setValue(self, value):
        if type(value) == pt.DeviceAttribute:
            self.setQuality(value.quality)
            val = value.value

        else:
            val = value
        if val != None:
            #			QtGui.QLabel.setText(self, "".join(("<font color=", self.currentAttrColor, ">", self.textFromValue(val), "</font>")))
            QtGui.QLabel.setText(self, self.textFromValue(val))
        else:
            QtGui.QLabel.setText(self, "0.0")
        #		QtGui.QDoubleSpinBox.setValue(self,val)

    def validate(self, text, position):
        return self.validator.validate(text, position)

    def fixup(self, text):
        return self.validator.fixup(text)

    def valueFromText(self, text):
        return float(text)

    def textFromValue(self, value):
        return to_precision(value, self.precision)

    #		return format_float(value)

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

        s = ''.join(('QLabel { \n',
                     'background-color: ', self.attrColors.backgroundColor, '; \n',
                     'selection-background-color: ', self.attrColors.secondaryColor1, '; \n',
                     'selection-color: ', self.attrColors.backgroundColor, '; \n',
                     #			'border-width: ', str(int(self.sizes.barHeight/10)), 'px; \n',
                     'border-width: ', str(int(1)), 'px; \n',
                     'border-color: ', self.attrColors.backgroundColor, '; \n',
                     'border-top-style: solid; \n',
                     'border-bottom-style: solid; \n',
                     'border-left-style: double; \n',
                     'border-right-style: solid; \n',
                     'border-radius: 0px; \n',
                     'padding: 0px; \n',
                     'margin: 0px; \n',
                     'min-width: ', str(int(self.sizes.barHeight) * 1), 'px; \n',
                     'max-width: ', str(int(self.sizes.barHeight) * 4), 'px; \n',
                     'min-height: ', str(int(self.sizes.barHeight * 1.3)), 'px; \n',
                     'max-height: ', str(int(self.sizes.barHeight * 1.3)), 'px; \n',
                     'color: ', self.currentAttrColor, ';} \n'))
        self.setStyleSheet(s)

        self.update()


class QTangoComboBoxBase(QtGui.QComboBox, QTangoAttributeBase):
    def __init__(self, sizes=None, colors=None, parent=None):
        QTangoAttributeBase.__init__(self, sizes, colors, parent)
        QtGui.QComboBox.__init__(self, parent)
        self.setupLayout()

    def setupLayout(self):
        self.setLocale(QtCore.QLocale(QtCore.QLocale.English))
        s = ''.join(('QComboBox { \n',
                     'background-color: ', self.attrColors.secondaryColor0, '; \n',
                     'selection-background-color: ', self.attrColors.secondaryColor1, '; \n',
                     'selection-color: ', self.attrColors.backgroundColor, '; \n',
                     'border-width: ', str(int(1)), 'px; \n',
                     'border-color: ', self.attrColors.backgroundColor, '; \n',
                     'border-top-style: solid; \n',
                     'border-bottom-style: solid; \n',
                     'border-left-style: double; \n',
                     'border-right-style: solid; \n',
                     'border-radius: 0px; \n',
                     'padding: 1px 0px 1px 3px; \n',
                     'margin: 0px; \n',
                     # 			'min-width: ', str(int(self.sizes.barHeight)*1), 'px; \n',
                     # 			'max-width: ', str(int(self.sizes.barHeight)*4), 'px; \n',
                     'min-width: ', str(int(self.sizes.readAttributeWidth / 3)), 'px; \n',
                     'max-width: ', str(int(self.sizes.readAttributeWidth)), 'px; \n',
                     'min-height: ', str(int(self.sizes.barHeight * 1.3)), 'px; \n',
                     'max-height: ', str(int(self.sizes.barHeight * 1.3)), 'px; \n',
                     'color: ', self.attrColors.backgroundColor, ';} \n',

                     'QComboBox:on { \n',
                     'background-color: ', self.attrColors.secondaryColor0, '; \n',
                     'color: ', self.attrColors.backgroundColor, '; \n',
                     '} \n',

                     'QComboBox QAbstractItemView { \n',
                     'background-color: ', self.attrColors.backgroundColor, '; \n',
                     'color: ', self.attrColors.secondaryColor0, '; \n',
                     'border-color: ', self.attrColors.backgroundColor, '; \n',
                     'selection-background-color: ', self.attrColors.secondaryColor1, '; \n',
                     'selection-color: ', self.attrColors.backgroundColor, '; \n',
                     '} \n',

                     'QComboBox::drop-down { \n',
                     'background-color: ', self.attrColors.secondaryColor0, '; \n',
                     'color: ', self.attrColors.backgroundColor, '; \n',
                     '} \n',

                     'QComboBox::down-arrow { \n',
                     ## 			'background-color: ', self.attrColors.secondaryColor0, '; \n',
                     'image: url(blackarrowdown.png); \n',
                     '} \n'
                     ))

        font = self.font()
        font.setFamily(self.sizes.fontType)
        font.setStretch(self.sizes.fontStretch)
        font.setWeight(self.sizes.fontWeight)
        font.setPointSize(int(self.sizes.barHeight * 0.7))
        font.setStyleStrategy(QtGui.QFont.PreferAntialias)
        self.setFont(font)
        self.setStyleSheet(s)
        self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        itemDelegate = QtGui.QStyledItemDelegate()
        self.setItemDelegate(itemDelegate)

    #		self.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom)

    def setValue(self, value):
        if type(value) == pt.DeviceAttribute:
            self.setQuality(value.quality)
            val = value.value
        else:
            val = value
        if val is not None:
            ind = self.findText(val)
            self.setCurrentIndex(ind)
        else:
            self.setCurrentIndex(0)

    def setWidth(self, width):
        s = str(self.styleSheet())
        ind0 = s.find('min-width') + 11
        ind1 = s[ind0:].find('px') + ind0
        s2 = s[0:ind0] + str(width) + s[ind1:]
        self.setStyleSheet(s2)


# noinspection PyAttributeOutsideInit
class QTangoWriteAttributeLineEdit(QtGui.QLineEdit, QTangoAttributeBase):
    """ A line edit for input of values to a tango attribute. Will emit a signal newValueSignal
    when enter is pressed.
    """
    newValueSignal = QtCore.pyqtSignal()

    def __init__(self, sizes=None, colors=None, parent=None):
        QTangoAttributeBase.__init__(self, sizes, colors, parent)
        QtGui.QLineEdit.__init__(self, parent)

        self.storedCursorPos = 0
        self.lastKey = QtCore.Qt.Key_0

        self.dataValue = 1.0
        self.dataFormat = "{0:.4g}"

        self.setupLayout()

    def setupLayout(self):
        # 		s = ''.join(('QLineEdit { \n',
        #             'background-color: ', self.attrColors.backgroundColor, '; \n',
        #             'selection-background-color: ', self.attrColors.secondaryColor0, '; \n',
        #             'selection-color: ', self.attrColors.backgroundColor, '; \n',
        #             'border-width: 1px; \n',
        #             'border-color: ', self.attrColors.secondaryColor0, '; \n',
        #             'border-style: solid; \n',
        #             'border-radius: 0px; \n',
        #             'padding: 0px; \n',
        #             'margin: 0px; \n',
        #             'min-width: ', str(self.sizes.barWidth), 'px; \n',
        #             'max-width: ', str(self.sizes.barWidth), 'px; \n',
        #             'min-height: ', str(int(self.sizes.barHeight-2)), 'px; \n',
        #             'max-height: ', str(int(self.sizes.barHeight-2)), 'px; \n',
        #             'qproperty-readOnly: 0; \n',
        #             'color: ', self.attrColors.secondaryColor0, ';} \n'))
        # 		font = self.font()
        # 		font.setFamily(self.sizes.fontType)
        # 		font.setStretch(self.sizes.fontStretch)
        # 		font.setWeight(self.sizes.fontWeight)
        # 		font.setPointSize(int(self.sizes.barHeight * 0.7))
        # 		font.setStyleStrategy(QtGui.QFont.PreferAntialias)
        # 		self.setFont(font)
        #
        # 		self.setStyleSheet(s)
        # 		self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        # 		self.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        ###############
        s = ''.join(('QLineEdit { \n',
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
                     #            'qproperty-buttonSymbols: UpDownArrows; \n',
                     #            'min-width: ', str(int(self.sizes.barHeight)*2.5), 'px; \n',
                     'min-width: ', str(int(self.sizes.barHeight) * 1), 'px; \n',
                     'max-width: ', str(int(self.sizes.barHeight) * 4), 'px; \n',
                     'min-height: ', str(int(self.sizes.barHeight * 1.3)), 'px; \n',
                     'max-height: ', str(int(self.sizes.barHeight * 1.3)), 'px; \n',
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
        self.setSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Minimum)
        self.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        self.validatorObject = QtGui.QDoubleValidator()
        self.validatorObject.setNotation(QtGui.QDoubleValidator.ScientificNotation)

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
                     'min-height: ', str(int(self.sizes.barHeight - 2)), 'px; \n',
                     'max-height: ', str(int(self.sizes.barHeight - 2)), 'px; \n',
                     'qproperty-readOnly: 0; \n',
                     'color: ', mainColor, ';} \n'))

        self.setStyleSheet(s)

    def value(self):
        if self.validatorObject.validate(self.text(), 0)[0] == QtGui.QValidator.Acceptable:
            return np.double(self.text())
        else:
            return self.dataValue

    def setValue(self, value):
        self.dataValue = value
        try:
            sVal = self.dataFormat.format((value))
        except ValueError:
            sVal = str(value)
        self.setText(sVal)

    def keyPressEvent(self, event):
        # Record keypress to check if it was return in changeStep
        if type(event) == QtGui.QKeyEvent:
            self.lastKey = event.key()
            if event.key() == QtCore.Qt.Key_Up or event.key() == QtCore.Qt.Key_Down:
                txt = str(self.text()).lower()
                if self.validatorObject.validate(self.text(), 0)[0] == QtGui.QValidator.Acceptable:
                    self.dataValue = np.double(self.text())

                commaPos = txt.find('.')
                expPos = txt.find('e')
                if commaPos < 0:
                    # Compensate if there is no comma
                    if expPos < 0:
                        # No exponent
                        commaPos = txt.__len__()
                    else:
                        commaPos = expPos
                cursorPos = self.cursorPosition()
                cursorDecimalPos = commaPos - cursorPos
                logger.debug("\n decimal pos: {0}\n comma pos: {1}\n cursor pos: {2}\n"
                             " exp pos: {3}\n old data value: {4}".format(cursorDecimalPos, commaPos, cursorPos,
                                                                          expPos, self.dataValue))

                # Compensate for the length of the comma character if we are to left of the comma
                if cursorDecimalPos < 0:
                    logger.debug('New decimal pos: {0}'.format(cursorDecimalPos))
                    newDecimalPos = cursorDecimalPos + 1
                else:
                    newDecimalPos = cursorDecimalPos

                if cursorPos <= expPos or expPos < 0:
                    # We are adjusting decimal value
                    # 				print txt, pos
                    # Find exponent value:
                    if expPos > 0:
                        expValue = float(txt[expPos + 1:])
                    else:
                        expValue = 0
                    if event.key() == QtCore.Qt.Key_Up:
                        stepDir = 1
                    else:
                        stepDir = -1
                    self.dataValue += stepDir * 10 ** (expValue + newDecimalPos)
                    logger.debug('New decimal pos: {0}'.format(newDecimalPos))
                    logger.debug("Step: {0}".format(stepDir * 10 ** newDecimalPos))
                    logger.debug('New decimal dataValue: {0}'.format(self.dataValue))

                    txt = self.dataFormat.format(self.dataValue)
                    newCommaPos = txt.find('.')
                    if newCommaPos < 0:
                        # There is no comma (integer)
                        newCommaPos = txt.__len__()
                        txt += '.'
                    if cursorDecimalPos < 0:
                        newCursorPos = newCommaPos - cursorDecimalPos
                    else:
                        newCursorPos = newCommaPos - cursorDecimalPos
                    logger.debug("newCursorPosition: {0}".format(newCursorPos))
                    # Check if the new number was truncated due to trailing zeros being removed
                    if newCursorPos > txt.__len__() - 1:
                        logger.debug("Adding {0} zeros".format(newCursorPos - txt.__len__()))
                        txt += '0' * (newCursorPos - txt.__len__())
                    self.clear()
                    self.insert(txt)
                    self.setCursorPosition(newCursorPos)

                else:
                    # We are adjusting exponent value
                    cursorExpPos = txt.__len__() - cursorPos
                    logger.debug("Adjusting exponent: cursorExpPos {0}".format(cursorExpPos))
                    if event.key() == QtCore.Qt.Key_Up:
                        self.dataValue *= 10 ** (cursorExpPos + 1)
                    else:
                        self.dataValue /= 10 ** (cursorExpPos + 1)

                    logger.debug('New decimal dataValue: {0}'.format(self.dataValue))
                    txt = self.dataFormat.format(self.dataValue)
                    self.clear()
                    self.insert(txt)

            elif event.key() in [QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return]:
                logger.debug('Enter!')
                if self.validatorObject.validate(self.text(), 0)[0] == QtGui.QValidator.Acceptable:
                    self.dataValue = np.double(self.text())
                self.newValueSignal.emit()
                # This fires an editingFinished event
                super(QTangoWriteAttributeLineEdit, self).keyPressEvent(event)

            elif event.key() in [QtCore.Qt.Key_Right]:
                # This is to add another zero if we press right while at the right edge of the field
                cursorPos = self.cursorPosition()
                txt = str(self.text()).lower()
                if self.validatorObject.validate(self.text(), 0)[0] == QtGui.QValidator.Acceptable:
                    self.dataValue = np.double(self.text())
                logger.debug("cursorPos: {0}".format(cursorPos))
                logger.debug("txt.__len__: {0}".format(txt.__len__()))
                if cursorPos == txt.__len__():
                    # We are at the right edge so add a zero if it is a decimal number
                    commaPos = txt.find('.')
                    expPos = txt.find('e')
                    if expPos < 0:
                        # There is no exponent, so ok to add zero
                        if commaPos < 0:
                            # Compensate if there is no comma
                            txt += '.'
                            commaPos = txt.__len__()
                        txt += '0'
                        self.clear()
                        self.insert(txt)
                else:
                    # We were not at the right edge, so process normally
                    super(QTangoWriteAttributeLineEdit, self).keyPressEvent(event)

            else:
                super(QTangoWriteAttributeLineEdit, self).keyPressEvent(event)


class QTangoWriteAttributeSpinBox(QtGui.QDoubleSpinBox):
    def __init__(self, sizes=None, colors=None, parent=None):
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
                     'border-width: ', str(int(self.sizes.barHeight / 10)), 'px; \n',
                     'border-color: ', self.attrColors.secondaryColor0, '; \n',
                     'border-top-style: none; \n',
                     'border-bottom-style: none; \n',
                     'border-left-style: double; \n',
                     'border-right-style: solid; \n',
                     'border-radius: 0px; \n',
                     'padding: 0px; \n',
                     'margin: 0px; \n',
                     'qproperty-buttonSymbols: NoButtons; \n',
                     'min-width: ', str(int(self.sizes.barHeight) * 2.5), 'px; \n',
                     'max-width: ', str(int(self.sizes.barHeight) * 2.5), 'px; \n',
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
        logger.debug('Value ready:: {0}'.format(value))
        self.lineEdit().setCursorPosition(self.storedCursorPos)

    def editReady(self):
        logger.debug('Cursor pos set to {0}'.format(self.storedCursorPos))
        self.lineEdit().setCursorPosition(self.storedCursorPos)

    def stepBy(self, steps):
        logger.debug('Step {0}, value: {1}, text: {2}'.format(steps, self.value(), self.valueFromText(self.text())))
        txt = self.text()
        currentValue = self.valueFromText(txt)
        commaPos = str(txt).find('.')
        self.storedCursorPos = self.lineEdit().cursorPosition()
        pos = commaPos - self.storedCursorPos + 1
        if pos + self.decimals() < 0:
            pos = -self.decimals()
        elif pos > 0:
            pos -= 1
        self.setValue(currentValue + 10 ** pos * steps)

    def changeStep(self, old, new):
        logger.debug('In changeStep::')

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
                     'min-height: ', str(int(self.sizes.barHeight - 2)), 'px; \n',
                     'max-height: ', str(int(self.sizes.barHeight - 2)), 'px; \n',
                     'qproperty-readOnly: 0; \n',
                     'color: ', mainColor, ';} \n'))

        self.setStyleSheet(s)


class QTangoWriteAttributeSpinBox2(QtGui.QDoubleSpinBox):
    def __init__(self, sizes=None, colors=None, parent=None):
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
        if colors is None:
            self.attrColors = QTangoColors()
        else:
            self.attrColors = colors
        if sizes is None:
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
                     'min-width: ', str(int(self.sizes.barHeight) * 1), 'px; \n',
                     'max-width: ', str(int(self.sizes.barHeight) * 4), 'px; \n',
                     'min-height: ', str(int(self.sizes.barHeight * 1.2)), 'px; \n',
                     'max-height: ', str(int(self.sizes.barHeight * 1.2)), 'px; \n',
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
        logger.debug('Value ready::{0}'.format(value))
        self.lineEdit().setCursorPosition(self.storedCursorPos)

    def editReady(self):
        logger.debug('Edit ready::')
        logger.debug('Cursor pos set to {0}'.format(self.storedCursorPos))
        self.lineEdit().setCursorPosition(self.storedCursorPos)

    def stepBy(self, steps):
        logger.debug('stepBy::Step {0}, value {1}, text {2}'.format(steps, self.value(),
                                                                    self.valueFromText(self.text())))
        txt = self.text()
        currentValue = self.valueFromText(txt)
        commaPos = str(txt).find('.')
        self.storedCursorPos = self.lineEdit().cursorPosition()
        #		self.lineEdit().setCursorPosition(self.storedCursorPos)
        pos = commaPos - self.storedCursorPos + 1
        logger.debug('stepBy::comma pos {0}'.format(commaPos))
        logger.debug('stepBy::stored pos {0}'.format(self.storedCursorPos))
        logger.debug('stepBy::cursor pos {0}'.format(self.lineEdit().cursorPosition()))
        if pos + self.decimals() < 0:
            pos = -self.decimals()
        elif pos > 0:
            pos -= 1
        self.setValue(currentValue + 10 ** pos * steps)

    def changeStep(self, old, new):
        # Check if the last key was return, then the cursor
        # shouldn't change
        if self.lastKey != QtCore.Qt.Key_Return:
            #		if self.lastKey == QtCore.Qt.Key_Up:
            txt = str(self.text())
            commaPos = txt.find('.')
            #			self.storedCursorPos = self.lineEdit().cursorPosition()
            pos = commaPos - self.storedCursorPos + 1
            logger.debug('pos {0}, comma pos {1}, stored pos {2}'.format(pos, commaPos, self.storedCursorPos))
            if pos + self.decimals() < 0:
                pos = -self.decimals()
            elif pos > 0:
                pos -= 1

        #			self.setSingleStep(10 ** pos)

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
                     'min-height: ', str(int(self.sizes.barHeight - 2)), 'px; \n',
                     'max-height: ', str(int(self.sizes.barHeight - 2)), 'px; \n',
                     'qproperty-readOnly: 0; \n',
                     'color: ', mainColor, ';} \n'))

        self.setStyleSheet(s)


# noinspection PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit
class QTangoReadAttributeDouble(QtGui.QWidget):
    def __init__(self, sizes=None, colors=None, parent=None):
        QtGui.QWidget.__init__(self, parent)
        if colors is None:
            self.attrColors = QTangoColors()
        else:
            self.attrColors = colors
        if sizes is None:
            self.sizes = QTangoSizes()
        else:
            self.sizes = sizes
        self.unit = None
        self.prefixDict = {'k': 1e-3, 'M': 1e-6, 'G': 1e-9, 'T': 1e-12, 'P': 1e-15,
                           'm': 1e3, 'u': 1e6, 'n': 1e9, 'p': 1e12, 'f': 1e15, 'c': 1e2}
        self.prefix = None
        self.prefixFactor = 1.0
        self.setupLayout()

    def setupLayout(self):
        self.startLabel = QTangoStartLabel(self.sizes, self.attrColors)
        self.endLabel = QTangoEndLabel(self.sizes, self.attrColors)
        self.nameLabel = QTangoAttributeNameLabel(self.sizes, self.attrColors)
        self.nameLabel.setSizePolicy(Qt.QSizePolicy.Expanding, Qt.QSizePolicy.Minimum)
        self.unitLabel = QTangoAttributeUnitLabel(self.sizes, self.attrColors)
        self.valueSpinbox = QTangoReadAttributeLabel(self.sizes, self.attrColors)
        self.unitLabel.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)

        layout = QtGui.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setMargin(int(self.sizes.barHeight / 10))

        layout.addWidget(self.startLabel)
        layout.addWidget(self.nameLabel)
        layout.addWidget(self.valueSpinbox)
        layout.addWidget(self.unitLabel)
        layout.addWidget(self.endLabel)

        self.setMaximumWidth(self.sizes.readAttributeWidth)
        self.setMinimumWidth(self.sizes.readAttributeWidth)
        self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)

    def attributeName(self):
        return str(self.nameLabel.text())

    @QtCore.pyqtSignature('setAttributeName(QString)')
    def setAttributeName(self, aName, aUnit=None):
        self.nameLabel.setText(aName)
        if aUnit is not None:
            self.setUnit(aUnit)
        self.update()

    def setAttributeValue(self, value):
        if type(value) == pt.DeviceAttribute:
            self.startLabel.setQuality(value.quality)
            self.endLabel.setQuality(value.quality)
            self.unitLabel.setQuality(value.quality)
            self.valueSpinbox.setQuality(value.quality)
            self.nameLabel.setQuality(value.quality)
            val = value.value
        else:
            val = value

        self.valueSpinbox.setValue(val * self.prefixFactor)
        self.update()

    def setUnit(self, unit):
        self.unit = unit
        if self.unit is not None:
            unitStr = self.unit
            if self.prefix is not None:
                unitStr = ''.join((self.prefix, unitStr))

            self.unitLabel.setText(unitStr)

    def setPrefix(self, prefix):
        try:
            self.prefixFactor = self.prefixDict[prefix]
            self.prefix = prefix
            self.setUnit(self.unit)
        except KeyError:
            self.prefix = None
            self.prefixFactor = 1.0


# noinspection PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit
class QTangoHSliderBase(QtGui.QSlider, QTangoAttributeBase):
    def __init__(self, sizes=None, colors=None, parent=None):
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

        startH = h / 6.0  # Position of horizontal line
        lineW = h / 4.0  # Width of horizontal line
        arrowW = h / 2.5  # Width of arrow
        writeW = h / 8.0

        # Vertical position of scale text
        textVertPos = h - h / 16.0
        textVertPos = h
        # Pixel coordinate of current value:
        xVal = w * (self.attrValue - self.attrMinimum) / (self.attrMaximum - self.attrMinimum)

        # Setup font
        font = QtGui.QFont(self.sizes.fontType, self.sizes.barHeight * 0.5, self.sizes.fontWeight)
        font.setStretch(self.sizes.fontStretch)

        # Strings to draw
        sVal = "{:.2f}".format((self.attrValue))
        sMin = "{:.2f}".format((self.attrMinimum))
        sMax = "{:.2f}".format((self.attrMaximum))
        sValWidth = QtGui.QFontMetricsF(font).width(sVal)
        sMinWidth = QtGui.QFontMetricsF(font).width(sMin)
        sMaxWidth = QtGui.QFontMetricsF(font).width(sMax)

        # Position to draw text of current value
        textPoint = QtCore.QPointF(xVal + lineW / 2 + h / 5.0, textVertPos)
        if xVal < 0:
            textPoint.setX(h / 3.0 + h / 16.0)
        if xVal + sValWidth > w:
            textPoint.setX(w - sValWidth - h / 3.0 - h / 16.0)
        if xVal < 0:
            # Draw left pointing arrow if the pixel position is < 0
            poly = QtGui.QPolygonF([QtCore.QPointF(0, (startH + lineW / 2 + h) / 2),
                                    QtCore.QPointF(h / 3.0, h),
                                    QtCore.QPointF(h / 3.0, startH + lineW / 2)])
        elif xVal > w:
            # Draw right pointing arrow if the pixel position is > w
            poly = QtGui.QPolygonF([QtCore.QPointF(w, (startH + lineW / 2 + h) / 2),
                                    QtCore.QPointF(w - h / 3.0, h),
                                    QtCore.QPointF(w - h / 3.0, startH + lineW / 2)])
        else:
            # Draw up pointing arrow otherwise
            poly = QtGui.QPolygonF([QtCore.QPointF(xVal, startH + lineW / 2.0),
                                    QtCore.QPointF(xVal - arrowW / 2.0, h),
                                    QtCore.QPointF(xVal + arrowW / 2.0, h)])

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

        qp.setRenderHint(QtGui.QPainter.Antialiasing, False)  # No antialiasing when drawing horizontal/vertical lines
        qp.setRenderHint(QtGui.QPainter.TextAntialiasing, True)
        qp.setRenderHint(QtGui.QPainter.SmoothPixmapTransform, True)
        # Draw warning line
        qp.setPen(penWarn)
        qp.setBrush(brushWarn)
        qp.drawLine(0, startH, w, startH)
        # Draw line
        qp.setPen(penAttr)
        qp.setBrush(brushAttr)
        qp.drawLine(w * (self.warnLow - self.attrMinimum) / (self.attrMaximum - self.attrMinimum), startH,
                    w * (self.warnHigh - self.attrMinimum) / (self.attrMaximum - self.attrMinimum), startH)

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
            xValW = w * (self.attrWriteValue - self.attrMinimum) / (self.attrMaximum - self.attrMinimum)
            qp.drawLine(xValW, h, xValW, 0)
        # Draw texts
        #		qp.drawText(textPoint, sVal)
        # Don't draw the limit texts if the value text is overlapping
        pen.setColor(colorAttr)
        qp.setPen(pen)
        if xVal - arrowW / 2 > sMinWidth:
            qp.drawText(QtCore.QPointF(0, textVertPos), sMin)
        if textPoint.x() < w - sMaxWidth:
            qp.drawText(QtCore.QPointF(w - sMaxWidth, textVertPos), sMax)

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
        if type(limits) == pt.AttributeInfoListEx:
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


# noinspection PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit
class QTangoHSliderBase2(QtGui.QSlider, QTangoAttributeBase):
    def __init__(self, sizes=None, colors=None, parent=None):
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
        self.setMaximumHeight(self.sizes.barHeight * 1.0)
        self.setMinimumHeight(self.sizes.barHeight * 1.0)

    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawWidget(qp)
        qp.end()

    def drawWidget(self, qp):
        size = self.size()
        w = size.width()
        h = size.height()

        startH = h / 2.0  # Position of horizontal line
        startH = h / 6.0  # Position of horizontal line
        lineW = h / 4.0  # Width of horizontal line
        arrowW = h / 2.5  # Width of arrow
        writeW = h / 8.0

        # Vertical position of scale text
        textVertPos = h - h / 16.0
        textVertPos = self.sizes.barHeight * 0.5 - h / 16.0
        textVertPos = h
        textVertPos = startH + self.sizes.barHeight * 0.5 + lineW / 2 + 1

        # Pixel coordinate of current value:
        xVal = w * (self.attrValue - self.attrMinimum) / (self.attrMaximum - self.attrMinimum)

        # Setup font
        font = QtGui.QFont('Calibri', self.sizes.barHeight * 0.5, self.sizes.fontWeight)
        #		font.setStretch(self.sizes.fontStretch)

        # Strings to draw
        sVal = "{:.2f}".format((self.attrValue))
        sMin = "{:.2f}".format((self.attrMinimum))
        sMax = "{:.2f}".format((self.attrMaximum))
        sValWidth = QtGui.QFontMetricsF(font).width(sVal)
        sMinWidth = QtGui.QFontMetricsF(font).width(sMin)
        sMaxWidth = QtGui.QFontMetricsF(font).width(sMax)

        # Position to draw text of current value
        textPoint = QtCore.QPointF(xVal + lineW / 2 + h / 5.0, textVertPos)
        if xVal < 0:
            textPoint.setX(h / 3.0 + h / 16.0)
        if xVal + sValWidth > w:
            textPoint.setX(w - sValWidth - h / 3.0 - h / 16.0)
        if xVal < 0:
            # Draw left pointing arrow if the pixel position is < 0
            poly = QtGui.QPolygonF([QtCore.QPointF(0, (startH + lineW / 2 + h) / 2),
                                    QtCore.QPointF(h / 3.0, h),
                                    QtCore.QPointF(h / 3.0, startH + lineW / 2)])
        elif xVal > w:
            # Draw right pointing arrow if the pixel position is > w
            poly = QtGui.QPolygonF([QtCore.QPointF(w, (startH + lineW / 2 + h) / 2),
                                    QtCore.QPointF(w - h / 3.0, h),
                                    QtCore.QPointF(w - h / 3.0, startH + lineW / 2)])
        else:
            # Draw up pointing arrow otherwise
            poly = QtGui.QPolygonF([QtCore.QPointF(xVal, startH + lineW / 2.0),
                                    QtCore.QPointF(xVal - arrowW / 2.0, h),
                                    QtCore.QPointF(xVal + arrowW / 2.0, h)])

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
            xValW = w * (self.attrWriteValue - self.attrMinimum) / (self.attrMaximum - self.attrMinimum)

            polyW = QtGui.QPolygonF([QtCore.QPointF(xValW, startH - lineW / 2.0),
                                     QtCore.QPointF(xValW - arrowW / 2.0, 0),
                                     QtCore.QPointF(xValW + arrowW / 2.0, 0)])
            polyW = QtGui.QPolygonF([QtCore.QPointF(xValW - arrowW / 2.0 - 4, h),
                                     QtCore.QPointF(xValW - 4, startH + lineW / 2.0 - 1),
                                     QtCore.QPointF(xValW + 4, startH + lineW / 2.0 - 1),
                                     QtCore.QPointF(xValW + arrowW / 2.0 + 4, h)])

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
        if xVal - arrowW / 2 > sMinWidth:
            qp.drawText(QtCore.QPointF(2, textVertPos), sMin)
        if textPoint.x() < w - sMaxWidth:
            qp.drawText(QtCore.QPointF(w - sMaxWidth - 2, textVertPos), sMax)

        qp.setRenderHint(QtGui.QPainter.Antialiasing, False)  # No antialiasing when drawing horizontal/vertical lines
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
        qp.drawLine(
            QtCore.QPointF(w * (self.warnLow - self.attrMinimum) / (self.attrMaximum - self.attrMinimum), startH),
            QtCore.QPointF(w * (self.warnHigh - self.attrMinimum) / (self.attrMaximum - self.attrMinimum), startH))
        # Draw start and end point lines
        penAttr.setWidthF(1)
        if self.warnLow > self.attrMinimum:
            penAttr.setColor(colorWarn)
        qp.setPen(penAttr)
        qp.drawLine(0, startH, 0, startH + lineW * 2)
        if self.warnHigh > self.attrMaximum:
            penAttr.setColor(colorLine)
            qp.setPen(penAttr)
        qp.drawLine(w - 1, startH, w - 1, startH + lineW * 2)

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
        if type(limits) == pt.AttributeInfoListEx:
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


# noinspection PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit
class QTangoHSliderBaseCompact(QtGui.QSlider, QTangoAttributeBase):
    def __init__(self, sizes=None, colors=None, parent=None):
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
        self.setMaximumHeight(self.sizes.barHeight * 0.3)
        self.setMinimumHeight(self.sizes.barHeight * 0.3)

    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawWidget(qp)
        qp.end()

    def drawWidget(self, qp):
        size = self.size()
        w = size.width()
        h = size.height()

        startH = h / 2.0  # Position of horizontal line
        #		startH = h/6.0		# Position of horizontal line
        lineW = h * 0.6  # Width of horizontal line
        arrowW = h * 0.5  # Width of indicator

        # Pixel coordinate of current value:
        xVal = w * (self.attrValue - self.attrMinimum) / (self.attrMaximum - self.attrMinimum)

        colorAttr = QtGui.QColor(self.attrColors.secondaryColor0)
        colorLine = QtGui.QColor(self.attrColors.secondaryColor0)
        penAttr = QtGui.QPen(colorLine)
        penAttr.setWidthF(lineW)
        brushAttr = QtGui.QBrush(colorLine)

        colorWarn = QtGui.QColor(self.attrColors.warnColor)
        penWarn = QtGui.QPen(colorWarn)
        brushWarn = QtGui.QBrush(colorWarn)

        qp.setRenderHint(QtGui.QPainter.Antialiasing, False)  # No antialiasing when drawing horizontal/vertical lines

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
        qp.drawLine(
            QtCore.QPointF(w * (self.warnLow - self.attrMinimum) / (self.attrMaximum - self.attrMinimum), int(startH)),
            QtCore.QPointF(w * (self.warnHigh - self.attrMinimum) / (self.attrMaximum - self.attrMinimum), int(startH)))
        # Draw indicator
        penInd = QtGui.QPen(QtCore.Qt.black)
        penInd.setWidthF(3 * arrowW)
        brushInd = QtGui.QBrush(QtCore.Qt.white)
        qp.setPen(penInd)
        qp.setBrush(brushInd)
        qp.drawLine(QtCore.QPointF(xVal, startH - lineW / 2.0 - 1), QtCore.QPointF(xVal, startH + lineW / 2.0 + 1))
        penInd.setWidthF(arrowW)
        penInd.setColor(QtCore.Qt.white)
        qp.setPen(penInd)
        qp.setBrush(brushInd)
        qp.drawLine(QtCore.QPointF(xVal, startH - lineW / 2.0 - 1), QtCore.QPointF(xVal, startH + lineW / 2.0 + 1))

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
        if type(limits) == pt.AttributeInfoListEx:
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


# noinspection PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit
class QTangoVSliderBase2(QtGui.QSlider, QTangoAttributeBase):
    def __init__(self, sizes=None, colors=None, parent=None):
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
        self.setMaximumWidth(self.sizes.barWidth * 4.2 - 2)
        self.setMinimumWidth(self.sizes.barWidth * 4.2 - 2)

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
        font = QtGui.QFont(self.sizes.fontType, self.sizes.barHeight * 0.75, self.sizes.fontWeight)
        font.setStretch(self.sizes.fontStretch)
        font.setStyleStrategy(QtGui.QFont.PreferAntialias)

        # Strings to draw
        sVal = ''.join(("{0:.4g}".format(self.attrValue), " ", self.unit))
        sMin = "{0:.4g}".format(self.attrMinimum)
        sMax = "{0:.4g}".format(self.attrMaximum)

        # Width of value text:
        sValWidth = QtGui.QFontMetricsF(font).width(sVal)
        # Height of the text:
        sValHeight = QtGui.QFontMetricsF(font).height()
        # Width of the min scale text:
        sMinWidth = QtGui.QFontMetricsF(font).width(sMin)
        # Width of the max scale text:
        sMaxWidth = QtGui.QFontMetricsF(font).width(sMax)

        startX = w / 2.0  # Position of vertical line
        startX = 0.0  # Position of vertical line
        lineW = w / 8.0  # Width of vertical line
        #		lineW = 5.0
        arrowW = w / 2.5  # Width of arrow
        arrowW = sValHeight / 2.0
        writeW = w / 8.0
        writeW = 6.0

        # Vertical position of scale text
        textVertPos = h - h / 16.0
        textVertPos = self.sizes.barHeight * 0.5 - h / 16.0
        textVertPos = h
        textVertPos = startX + self.sizes.barHeight * 0.5 + lineW / 2 + 1

        # Pixel coordinate of current value:
        yVal = h - h * (self.attrValue - self.attrMinimum) / (self.attrMaximum - self.attrMinimum)

        # Position to draw text of current value
        textPoint = QtCore.QPointF(startX + lineW / 2 + arrowW, yVal + sValHeight * 0.3)
        # Check if text is outside the bounds of the slider
        if yVal - arrowW < 0:
            textPoint.setY(0.8 * sValHeight)
        if yVal + arrowW > h:
            textPoint.setY(h - sValHeight * 0.2)

        if self.quality == "ALARM":
            colorAttr = QtGui.QColor(self.attrColors.alarmColor)
            colorWriteAttr = QtGui.QColor(self.attrColors.alarmColor)
            colorLine = QtGui.QColor(self.attrColors.alarmColor2)
            pen = QtGui.QPen(colorLine)
            penAttr = QtGui.QPen(colorAttr)
            penAttr.setWidthF(lineW)
            brushAttr = QtGui.QBrush(colorAttr, QtCore.Qt.NoBrush)
            qp.setFont(font)

            colorWarn = QtGui.QColor(self.attrColors.alarmColor)
            penWarn = QtGui.QPen(colorWarn)
            brushWarn = QtGui.QBrush(colorWarn, QtCore.Qt.NoBrush)

        elif self.quality == "WARNING":
            colorAttr = QtGui.QColor(self.attrColors.warnColor2)
            colorWriteAttr = QtGui.QColor(self.attrColors.secondaryColor2)
            colorLine = QtGui.QColor(self.attrColors.secondaryColor0)
            pen = QtGui.QPen(colorLine)
            penAttr = QtGui.QPen(colorAttr)
            penAttr.setWidthF(lineW)
            brushAttr = QtGui.QBrush(colorAttr, QtCore.Qt.NoBrush)
            qp.setFont(font)

            colorWarn = QtGui.QColor(self.attrColors.warnColor)
            penWarn = QtGui.QPen(colorWarn)
            brushWarn = QtGui.QBrush(colorWarn)

        elif self.quality == "UNKNOWN":
            colorAttr = QtGui.QColor(self.attrColors.unknownColor)
            colorWriteAttr = QtGui.QColor(self.attrColors.unknownColor)
            colorLine = QtGui.QColor(self.attrColors.unknownColor)
            pen = QtGui.QPen(colorLine)
            penAttr = QtGui.QPen(colorAttr)
            penAttr.setWidthF(lineW)
            brushAttr = QtGui.QBrush(colorAttr, QtCore.Qt.NoBrush)
            qp.setFont(font)

            colorWarn = QtGui.QColor(self.attrColors.unknownColor)
            penWarn = QtGui.QPen(colorWarn)
            brushWarn = QtGui.QBrush(colorWarn)

        elif self.quality == "INVALID":
            colorAttr = QtGui.QColor(self.attrColors.unknownColor)
            colorWriteAttr = QtGui.QColor(self.attrColors.unknownColor)
            colorLine = QtGui.QColor(self.attrColors.unknownColor)
            pen = QtGui.QPen(colorLine)
            penAttr = QtGui.QPen(colorAttr)
            penAttr.setWidthF(lineW)
            brushAttr = QtGui.QBrush(colorAttr, QtCore.Qt.NoBrush)
            qp.setFont(font)

            colorWarn = QtGui.QColor(self.attrColors.unknownColor)
            penWarn = QtGui.QPen(colorWarn)
            brushWarn = QtGui.QBrush(colorWarn)

        else:
            colorAttr = QtGui.QColor(self.attrColors.secondaryColor0)
            colorWriteAttr = QtGui.QColor(self.attrColors.secondaryColor2)
            colorLine = QtGui.QColor(self.attrColors.secondaryColor0)
            pen = QtGui.QPen(colorLine)
            penAttr = QtGui.QPen(colorLine)
            penAttr.setWidthF(lineW)
            brushAttr = QtGui.QBrush(colorLine, QtCore.Qt.NoBrush)
            qp.setFont(font)

            colorWarn = QtGui.QColor(self.attrColors.warnColor)
            penWarn = QtGui.QPen(colorWarn)
            brushWarn = QtGui.QBrush(colorWarn)

        # Draw anti-aliased
        qp.setRenderHint(QtGui.QPainter.Antialiasing, True)
        qp.setRenderHint(QtGui.QPainter.TextAntialiasing, True)

        penAttr.setWidthF(1.5)
        #		brushAttr = QtGui.QBrush(colorLine, QtCore.Qt.NoBrush)
        qp.setPen(penAttr)
        qp.setBrush(brushAttr)

        # Check if the arrow is outside the bounds of the slider
        if yVal < 0:
            # Draw up pointing arrow if the pixel position is < 0
            arrowPoly = QtGui.QPolygonF([QtCore.QPointF(startX + lineW / 2 + arrowW / 2.0, arrowW / 4.0),
                                         QtCore.QPointF(startX + lineW / 2.0, 0.0),
                                         QtCore.QPointF(startX + lineW / 2.0 + arrowW, 2 * arrowW),
                                         QtCore.QPointF(w - 1.0, 2 * arrowW)])
            qp.drawPolyline(arrowPoly)
        elif yVal - arrowW < 0:
            # Intermediate position, draw modified arrow
            arrowPoly = QtGui.QPolygonF([QtCore.QPointF(startX + lineW / 2.0, yVal),
                                         QtCore.QPointF(startX + lineW / 2.0 + arrowW, 2 * arrowW),
                                         QtCore.QPointF(w - 1.0, 2 * arrowW),
                                         QtCore.QPointF(w - 1.0, 0.0),
                                         QtCore.QPointF(startX + lineW / 2.0 + arrowW, 0.0)])
            qp.drawPolygon(arrowPoly)
        elif yVal > h:
            # Draw down pointing arrow if the pixel position is > h
            arrowPoly = QtGui.QPolygonF([QtCore.QPointF(startX + lineW / 2 + arrowW / 2.0, h - arrowW / 4.0),
                                         QtCore.QPointF(startX + lineW / 2.0, h),
                                         QtCore.QPointF(startX + lineW / 2.0 + arrowW, h - 2 * arrowW),
                                         QtCore.QPointF(w - 1.0, h - 2 * arrowW)])
            qp.drawPolyline(arrowPoly)
        elif yVal + arrowW > h:
            # Intermediate position, draw modified arrow
            arrowPoly = QtGui.QPolygonF([QtCore.QPointF(startX + lineW / 2.0, yVal),
                                         QtCore.QPointF(startX + lineW / 2.0 + arrowW, h),
                                         QtCore.QPointF(w - 1.0, h),
                                         QtCore.QPointF(w - 1.0, h - 2 * arrowW),
                                         QtCore.QPointF(startX + lineW / 2.0 + arrowW, h - 2 * arrowW)])
            qp.drawPolygon(arrowPoly)
        else:
            # Draw left pointing arrow otherwise
            arrowPoly = QtGui.QPolygonF([QtCore.QPointF(startX + lineW / 2.0, yVal),
                                         QtCore.QPointF(startX + lineW / 2.0 + arrowW, yVal + arrowW),
                                         QtCore.QPointF(w - 1.0, yVal + arrowW),
                                         QtCore.QPointF(w - 1.0, yVal - arrowW),
                                         QtCore.QPointF(startX + lineW / 2.0 + arrowW, yVal - arrowW)])
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
        if self.attrWriteValue is not None:
            pen.setWidthF(2.5)
            pen.setColor(colorWriteAttr)
            qp.setPen(pen)
            writeYVal = h - h * (self.attrWriteValue - self.attrMinimum) / (self.attrMaximum - self.attrMinimum)

            polyW = QtGui.QPolygonF([QtCore.QPointF(startX + lineW / 2.0 + arrowW, writeYVal + arrowW + writeW),
                                     QtCore.QPointF(startX + lineW / 2.0, writeYVal + writeW),
                                     QtCore.QPointF(startX + lineW / 2.0, writeYVal - writeW),
                                     QtCore.QPointF(startX + lineW / 2.0 + arrowW, writeYVal - arrowW - writeW)])

            qp.drawPolyline(polyW)

        #
        # Draw texts
        #

        # Draw value text
        pen.setColor(colorAttr)
        qp.setPen(pen)
        qp.drawText(textPoint, sVal)

        # Draw slider scale texts
        # Don't draw the limit texts if the value text is overlapping
        font.setPointSizeF(self.sizes.barHeight * 0.5)

        qp.setRenderHint(QtGui.QPainter.TextAntialiasing, True)
        qp.setFont(font)
        pen.setColor(colorLine)
        qp.setPen(pen)
        if yVal + arrowW / 2 < h - sValHeight:
            qp.drawText(QtCore.QPointF(startX + lineW, h - sValHeight * 0.2), sMin)
        if yVal - arrowW / 2 > sValHeight:
            qp.drawText(QtCore.QPointF(startX + lineW, sValHeight * 0.6), sMax)

        qp.setRenderHint(QtGui.QPainter.Antialiasing, False)  # No antialiasing when drawing horizontal/vertical lines
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
        qp.drawLine(
            QtCore.QPointF(startX, h - h * (self.warnLow - self.attrMinimum) / (self.attrMaximum - self.attrMinimum)),
            QtCore.QPointF(startX, h - h * (self.warnHigh - self.attrMinimum) / (self.attrMaximum - self.attrMinimum)))
        # Draw start and end point lines
        penAttr.setWidthF(1)
        if self.warnLow > self.attrMinimum:
            penAttr.setColor(colorWarn)
        qp.setPen(penAttr)
        qp.drawLine(startX, h - 1, startX + lineW * 2, h - 1)
        if self.warnHigh > self.attrMaximum:
            penAttr.setColor(colorLine)
            qp.setPen(penAttr)
        qp.drawLine(startX, 0, startX + lineW * 2, 0)

    def setValue(self, value):
        if type(value) == pt.DeviceAttribute:
            logger.debug("QTangoVSliderBase2 quality {0}".format(value.quality))
            self.setQuality(value.quality)
            if value.value is not None:
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
        if type(limits) == pt.AttributeInfoListEx:
            warnHigh = limits[0].alarms.max_warning
            warnLow = limits[0].alarms.min_warning
        else:
            warnLow = limits[0]
            warnHigh = limits[1]
        self.warnHigh = warnHigh
        self.warnLow = warnLow
        self.update()

    def setSliderLimits(self, min_limit, max_limit):
        self.attrMinimum = min_limit
        self.attrMaximum = max_limit
        self.update()

    def setUnit(self, aUnit):
        self.unit = aUnit
        self.update()


# noinspection PyAttributeOutsideInit,PyAttributeOutsideInit
class QTangoTrendBase(pg.PlotWidget):
    def __init__(self, name=None, sizes=None, colors=None, chronological=True, parent=None):
        pg.PlotWidget.__init__(self, useOpenGL=True)
        if colors is None:
            self.attrColors = QTangoColors()
        else:
            self.attrColors = colors
        if sizes is None:
            self.sizes = QTangoSizes()
        else:
            self.sizes = sizes

        self.valuesSize = 200000
        self.duration = 600.0
        self.xValues = []
        self.yValues = []

        self.legend = None
        self.curve_focus = 0
        self.curve_name_list = []

        self.chronological = chronological

        self.setupLayout(name)
        self.setupData()

    def setupLayout(self, name=None):
        self.setXRange(-self.duration, 0)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        #		self.setMaximumWidth(self.sizes.readAttributeWidth-self.sizes.barHeight/6-self.sizes.barHeight/2)
        pi = self.getPlotItem()
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
        # brushWarn = QtGui.QBrush(colorWarn, style=QtCore.Qt.SolidPattern)
        # brushGood = QtGui.QBrush(colorGood, style=QtCore.Qt.SolidPattern)
        # penLines = QtGui.QPen(QtGui.QColor('#55555500'))

        # high_lim = 1e9

        # 		self.warningRegionUpper = pg.LinearRegionItem(values=[high_lim, high_lim], orientation = pg.LinearRegionItem.Horizontal,
        # 													brush = brushWarn, movable = False)
        # 		self.warningRegionUpper.lines[0].setPen(penLines)
        # 		self.warningRegionUpper.lines[1].setPen(penLines)
        # 		self.warningRegionLower = pg.LinearRegionItem(values=[-high_lim, -high_lim], orientation = pg.LinearRegionItem.Horizontal,
        # 													brush = brushWarn, movable = False)
        # 		self.warningRegionLower.lines[0].setPen(penLines)
        # 		self.warningRegionLower.lines[1].setPen(penLines)
        # 		self.goodRegion = pg.LinearRegionItem(values=[-high_lim, high_lim], orientation = pg.LinearRegionItem.Horizontal,
        # 													brush = brushGood, movable = False)
        # 		self.goodRegion.lines[0].setPen(penLines)
        # 		self.goodRegion.lines[1].setPen(penLines)
        # 		self.addItem(self.warningRegionUpper)
        # 		self.addItem(self.warningRegionLower)
        # 		self.addItem(self.goodRegion)
        self.valueTrendCurves = []
        self.currentDataIndex = []

        self.trendMenu = QtGui.QMenu()
        self.trendMenu.setTitle("Trend options")
        duration_action = QtGui.QWidgetAction(self)
        duration_widget = QtGui.QWidget()
        duration_layout = QtGui.QHBoxLayout()
        duration_label = QtGui.QLabel("Duration / s")
        duration_spinbox = QtGui.QDoubleSpinBox()
        duration_spinbox.setMaximum(3e7)
        duration_spinbox.setValue(self.duration)
        duration_spinbox.setMinimumWidth(40)
        duration_spinbox.editingFinished.connect(self.setDurationContext)

        duration_layout.addWidget(duration_label)
        duration_layout.addWidget(duration_spinbox)
        duration_widget.setLayout(duration_layout)
        duration_action.setDefaultWidget(duration_widget)
        self.trendMenu.addAction(duration_action)
        pi.ctrlMenu = [self.trendMenu, pi.ctrlMenu]

        self.addCurve(name)

    def setupData(self, curve=0):
        """ Pre-allocate data arrays
        """
        if len(self.xValues) > curve + 1:
            # Curve already exists
            #			self.xValues[curve] = np.linspace(-self.duration, 0, self.valuesSize)
            self.xValues[curve] = -np.ones(self.valuesSize) * np.inf
            self.yValues[curve] = np.zeros(self.valuesSize)
            self.currentDataIndex[curve] = 0
            self.valueTrendCurves[curve].setData(self.xValues[curve], self.yValues[curve], antialias=True)
        else:
            # Need to create new arrays
            self.xValues.append(-np.ones(self.valuesSize) * np.inf)
            self.yValues.append(np.zeros(self.valuesSize))
            self.currentDataIndex.append(0)
            if len(self.valueTrendCurves) < curve + 1:
                self.addCurve()
            #			self.valueTrendCurves[curve].setData(self.xValues[curve], self.yValues[curve], antialias = True)

    def setWarningLimits(self, limits):
        if type(limits) == pt.AttributeInfoListEx:
            warnHigh = limits[0].alarms.max_warning
            warnLow = limits[0].alarms.min_warning
        else:
            warnLow = limits[0]
            warnHigh = limits[1]
        self.warningRegionUpper.setRegion([warnHigh, 1e6])
        self.warningRegionLower.setRegion([-1e6, warnLow])
        self.goodRegion.setRegion([warnLow, warnHigh])

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
        self.setWarningLimits((min_warning, max_warning))
        self.setUnit(self.attrInfo.unit)

    def setDuration(self, duration):
        """ Set the duration of the trend graph in x axis units
        (e.g. samples, seconds...)
        """
        self.duration = duration
        self.setXRange(-self.duration, 0)

    def setDurationContext(self):
        """ Set the duration of the trend graph in x axis units
        (e.g. samples, seconds...) from the context menu
        """
        w = self.sender()
        duration = w.value()
        self.duration = duration
        self.setXRange(-self.duration, 0)

    def addCurve(self, name=None):
        curve_index = len(self.valueTrendCurves)
        if name is not None:
            new_curve = self.plot(name=name)
            self.curve_name_list.append(name)
        else:
            new_curve = self.plot(name=str(curve_index))
            self.curve_name_list.append(str(curve_index))
        curve_color = self.attrColors.legend_color_list[curve_index % len(self.attrColors.legend_color_list)]
        new_curve.setPen(curve_color, width=2.0)
        new_curve.curve.setClickable(True)
        self.valueTrendCurves.append(new_curve)

        self.setupData(len(self.valueTrendCurves) - 1)

        new_curve.sigClicked.connect(self.setCurveFocus)

    #		self.autoRange(items=self.valueTrendCurves)
    #		vb = self.plotItem.getViewBox()
    #		vb.autoRange(items=self.valueTrendCurves)

    def setCurveFocus(self, curve):
        name = curve.opts.get('name', None)

    def showLegend(self, show_legend=True):
        if show_legend is True:
            if self.legend is None:
                self.legend = self.addLegend(offset=(5, 5))
                for it in self.valueTrendCurves:
                    self.legend.addItem(it, it.opts.get('name', None))
        else:
            if self.legend is not None:
                self.legend.scene().removeItem(self.legend)
                self.legend = None

    def setCurveName(self, curve, name):
        self.valueTrendCurves[curve].opts['name'] = name

    def addPoint(self, data, curve=0):
        if type(data) == pt.DeviceAttribute:
            xNew = data.time.totime()
            yNew = data.value
        else:
            xNew = data[0]
            yNew = data[1]
        # Check xNew against last x to see if it is increasing.
        # Sometimes there is a bug with wrong time values that are very much lower
        # than the old value (probably 0)
        if self.currentDataIndex[curve] == 0:
            xOld = 0.0
        else:
            xOld = self.xValues[curve][self.currentDataIndex[curve]]
        if (self.chronological is False) or (xNew > xOld):
            # Rescaling if the number of sample is too high
            if self.currentDataIndex[curve] + 1 >= self.valuesSize:
                self.currentDataIndex[curve] = int(self.valuesSize * 0.75)
                self.xValues[curve][0:self.currentDataIndex[curve]] = self.xValues[curve][
                                                                      self.valuesSize - self.currentDataIndex[
                                                                          curve]:self.valuesSize]
                self.yValues[curve][0:self.currentDataIndex[curve]] = self.yValues[curve][
                                                                      self.valuesSize - self.currentDataIndex[
                                                                          curve]:self.valuesSize]
            elif self.currentDataIndex[curve] == 0:
                self.xValues[curve][0] = xNew
                self.yValues[curve][0] = yNew
            self.currentDataIndex[curve] += 1
            self.xValues[curve][self.currentDataIndex[curve]] = xNew
            start_index = np.argmax((self.xValues[curve] - xNew) > -self.duration)
            self.yValues[curve][self.currentDataIndex[curve]] = yNew
            self.valueTrendCurves[curve].setData(self.xValues[curve][start_index:self.currentDataIndex[curve]] - xNew,
                                                 self.yValues[curve][start_index:self.currentDataIndex[curve]],
                                                 antialias=True)
            self.update()


# noinspection PyAttributeOutsideInit,PyAttributeOutsideInit
class QTangoSpectrumBase(pg.PlotWidget, QTangoAttributeBase):
    def __init__(self, sizes=None, colors=None, parent=None):
        pg.PlotWidget.__init__(self, useOpenGL=True)
        if colors is None:
            self.attrColors = QTangoColors()
        else:
            self.attrColors = colors
        if sizes is None:
            self.sizes = QTangoSizes()
        else:
            self.sizes = sizes

        self.legend = None
        self.spectrumCurves = list()
        self.spectrumNames = list()
        self.spectrumColors = list()
        self.vb2 = None
        self.setupLayout()

    def setupLayout(self):
        self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        pi = self.getPlotItem()
        pi.hideAxis('left')
        pi.showAxis('right', True)
        pi.showGrid(True, True, 0.2)
        axLeft = pi.getAxis('right')
        axLeft.setPen(self.attrColors.secondaryColor0)
        axBottom = pi.getAxis('bottom')
        axBottom.setPen(self.attrColors.secondaryColor0)

        self.spectrumCurves = [self.plot()]
        self.spectrumNames = ['']
        self.spectrumColors = [self.attrColors.secondaryColor0]
        self.spectrumCurves[0].setPen(self.attrColors.secondaryColor0, width=2.0)
        #		self.spectrumCurve.setDownsampling(True, True, 'subsample')

        self.useOpenGL(True)
        self.setAntialiasing(True)
        br = pg.mkBrush(self.attrColors.backgroundColor)
        #		self.setBackground(self.attrColors.backgroundColor)
        self.setBackgroundBrush(br)

    def setSpectrum(self, xData, yData, index=0):
        if self.quality in ["UNKNOWN", "INVALID"]:
            pi = self.getPlotItem()
            axRight = pi.getAxis('right')
            axRight.setPen(self.attrColors.unknownColor)
            axBottom = pi.getAxis('bottom')
            axBottom.setPen(self.attrColors.unknownColor)
            if self.vb2 is not None:
                axLeft = pi.getAxis('left')
                axLeft.setPen(self.attrColors.unknownColor)
            for ind, cur in enumerate(self.spectrumCurves):
                cur.setPen(self.attrColors.unknownColor, width=2.0)
        else:
            pi = self.getPlotItem()
            axRight = pi.getAxis('right')
            axRight.setPen(self.attrColors.secondaryColor0)
            axBottom = pi.getAxis('bottom')
            axBottom.setPen(self.attrColors.secondaryColor0)
            if self.vb2 is not None:
                axLeft = pi.getAxis('left')
                axLeft.setPen(self.attrColors.secondaryColor0)
            for ind, cur in enumerate(self.spectrumCurves):
                cur.setPen(self.spectrumColors[ind], width=2.0)
            self.spectrumCurves[index].setData(y=yData, x=xData, antialias=False)
        self.update()
        if self.vb2 is not None:
            self.vb2.setGeometry(self.getViewBox().sceneBoundingRect())
            self.vb2.linkedViewChanged(self.getViewBox(), self.vb2.XAxis)

    def showLegend(self, state):
        pi = self.getPlotItem()
        if state is True:
            if self.legend is None:
                self.legend = pi.addLegend()
                for ind, cur in enumerate(self.spectrumCurves):
                    self.legend.addItem(cur, self.spectrumNames[ind])
        else:
            if self.legend is not None:
                self.legend.scene().removeItem(self.legend)
                self.legend = None

    def setCurveName(self, index, name):
        self.spectrumNames[index] = name
        if self.legend is not None:
            self.legend.removeItem(name)
            self.legend.addItem(self.spectrumCurves[index], self.spectrumNames[index])

    def addPlot(self, color, name='', axis="right"):
        if axis == "right":
            p = self.plot()
        else:
            if self.vb2 is None:
                self.setupDualAxis()
            p = pg.PlotCurveItem()
            self.vb2.addItem(p)
        p.setPen(color, width=2.0)
        self.spectrumCurves.append(p)
        self.spectrumNames.append(name)
        self.spectrumColors.append(color)

    def setupDualAxis(self):
        self.vb2 = pg.ViewBox()
        self.scene().addItem(self.vb2)
        self.getAxis('left').linkToView(self.vb2)
        self.vb2.setXLink(self)
        pi = self.getPlotItem()
        pi.showAxis('left', True)


class QTangoImageWithHistBase(pg.ImageView):
    def __init__(self, sizes=None, colors=None, parent=None):
        if colors is None:
            self.attrColors = QTangoColors()
        else:
            self.attrColors = colors
        if sizes is None:
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


# pi=self.getPlotItem()
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
    def __init__(self, sizes=None, colors=None, parent=None):
        if colors is None:
            self.attrColors = QTangoColors()
        else:
            self.attrColors = colors
        if sizes is None:
            self.sizes = QTangoSizes()
        else:
            self.sizes = sizes

        pg.GraphicsView.__init__(self)

        self.vb = pg.ViewBox(lockAspect=1.0, invertY=True)
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

    def setImage(self, image, auto_levels=False):
        if image is not None:
            if type(image) == pt.DeviceAttribute:
                data = image.value
                if image.quality == pt.AttrQuality.ATTR_VALID:
                    gradEditor = pg.GradientEditorItem()
                    gradEditor.loadPreset('flame')
                    self.lut = gradEditor.getLookupTable(256)
                else:
                    gradEditor = pg.GradientEditorItem()
                    gradEditor.loadPreset('gray')
                    self.lut = gradEditor.getLookupTable(8)
            else:
                data = image
            self.image.setImage(np.transpose(data), autoLevels=auto_levels, lut=self.lut, autoDownSample=True)
            self.update()


# noinspection PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit
class QTangoReadAttributeSlider(QTangoAttributeBase):
    def __init__(self, sizes=None, colors=None, parent=None):
        QTangoAttributeBase.__init__(self, sizes, colors, parent)
        self.setupLayout()

    def setupLayout(self):
        readValueWidth = self.sizes.barWidth
        readWidth = self.sizes.readAttributeWidth - self.sizes.barHeight / 6 - self.sizes.barHeight / 2

        self.startLabel = QTangoStartLabel(self.sizes, self.attrColors)
        self.endLabel = QTangoEndLabel(self.sizes, self.attrColors)
        self.nameLabel = QTangoAttributeNameLabel(self.sizes, self.attrColors)
        self.valueSpinbox = QTangoReadAttributeSpinBox(self.sizes, self.attrColors)
        self.valueSlider = QTangoHSliderBase(self.sizes, self.attrColors)

        self.layout = QtGui.QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        #		self.layout.setMargin(int(self.sizes.barHeight/10))
        self.layout.setMargin(0)
        self.layout.setSpacing(self.sizes.barHeight / 3)

        self.layoutGrid = QtGui.QGridLayout()
        self.layoutGrid.setContentsMargins(0, 0, 0, 0)
        self.layoutGrid.setMargin(int(self.sizes.barHeight / 10))
        self.layoutGrid.setMargin(0)
        self.layoutGrid.addWidget(self.nameLabel, 0, 0, )
        self.layoutGrid.addWidget(self.valueSlider, 1, 0)
        self.layoutGrid.addWidget(self.valueSpinbox, 0, 1)
        self.layoutGrid.setHorizontalSpacing(self.sizes.barHeight / 4)
        self.layoutGrid.setVerticalSpacing(0)

        self.layout.addWidget(self.startLabel)
        self.layout.addLayout(self.layoutGrid)
        self.layout.addWidget(self.endLabel)

        self.setMaximumWidth(self.sizes.readAttributeWidth)
        self.setMinimumWidth(self.sizes.readAttributeWidth)
        self.setMaximumHeight(self.sizes.barHeight * 2.2)
        self.setMinimumHeight(self.sizes.barHeight * 2.2)
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
            if value.value is not None:
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

    def setSliderLimits(self, min_limit, max_limit):
        self.valueSlider.setSliderLimits(min_limit, max_limit)


# noinspection PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit
class QTangoReadAttributeSlider2(QTangoAttributeBase):
    def __init__(self, sizes=None, colors=None, parent=None):
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
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setMargin(int(self.sizes.barHeight / 10))
        self.layout.setMargin(0)
        self.layout.setSpacing(self.sizes.barWidth / 3)

        self.layoutGrid = QtGui.QGridLayout()
        self.layoutGrid.setContentsMargins(0, 0, 0, 0)
        #		self.layoutGrid.setMargin(int(self.sizes.barHeight/10))
        self.layoutGrid.setMargin(0)
        self.layoutGrid.addWidget(self.nameLabel, 0, 0)
        self.layoutGrid.addWidget(self.unitLabel, 0, 1)
        self.layoutGrid.addWidget(self.valueSlider, 1, 0, 1, 2)
        self.layoutGrid.addWidget(self.valueSpinbox, 0, 3)
        self.layoutGrid.addWidget(self.writeLabel, 1, 2)

        self.layoutGrid.setHorizontalSpacing(self.sizes.barHeight / 4)
        self.layoutGrid.setVerticalSpacing(0)

        self.layout.addWidget(self.startLabel)
        self.layout.addLayout(self.layoutGrid)
        self.layout.addWidget(self.endLabel)

        self.setMaximumWidth(self.sizes.readAttributeWidth)
        self.setMinimumWidth(self.sizes.readAttributeWidth)
        self.setMaximumHeight(self.sizes.barHeight * 2.2)
        self.setMinimumHeight(self.sizes.barHeight * 2.2)
        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)

    def attributeName(self):
        return str(self.nameLabel.text())

    @QtCore.pyqtSignature('setAttributeName(QString)')
    def setAttributeName(self, aName, aUnit=None):
        self.nameLabel.setText(aName)
        if aUnit is not None:
            self.unitLabel.setText(aUnit)
        self.update()

    def setAttributeValue(self, value):
        if type(value) == pt.DeviceAttribute:
            self.startLabel.setQuality(value.quality)
            self.endLabel.setQuality(value.quality)
            self.nameLabel.setQuality(value.quality)
            if value.value is not None:
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

    def setSliderLimits(self, min_limit, max_limit):
        self.valueSlider.setSliderLimits(min_limit, max_limit)

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


# noinspection PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit
class QTangoReadAttributeSlider3(QTangoReadAttributeSlider2):
    def __init__(self, sizes=None, colors=None, parent=None):
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
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setMargin(int(self.sizes.barHeight / 10))
        self.layout.setSpacing(self.sizes.barHeight / 3)

        self.layoutGrid = QtGui.QGridLayout()
        self.layoutGrid.setContentsMargins(0, 0, 0, 0)
        self.layoutGrid.setMargin(int(self.sizes.barHeight / 10))
        self.layoutGrid.setMargin(0)
        self.layoutGrid.addWidget(self.nameLabel, 0, 0)
        self.layoutGrid.addWidget(self.unitLabel, 0, 1)
        self.layoutGrid.addWidget(self.valueSlider, 1, 0, 1, 2)
        # 		self.layoutGrid.addWidget(self.valueSpinbox, 0, 3)
        # 		self.layoutGrid.addWidget(self.writeLabel, 1, 2)

        self.layoutGrid.setHorizontalSpacing(self.sizes.barHeight / 4)
        self.layoutGrid.setVerticalSpacing(0)

        self.layout.addWidget(self.startLabel)
        self.layout.addLayout(self.layoutGrid)
        self.layout.addWidget(self.endLabel)

        self.setMaximumWidth(self.sizes.readAttributeWidth)
        self.setMinimumWidth(self.sizes.readAttributeWidth)
        self.setMaximumHeight(self.sizes.barHeight * 2.2)
        self.setMinimumHeight(self.sizes.barHeight * 2.2)
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
            if value.value is not None:
                val = value.value
                self.valueLabel.setText(str(val))
                self.valueSlider.setValue(val)
        else:
            val = value
            self.valueLabel.setText(str(val))
            self.valueSlider.setValue(val)
        self.update()


# noinspection PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit
class QTangoReadAttributeSlider4(QTangoReadAttributeSlider2):
    def __init__(self, sizes=None, colors=None, parent=None):
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
            sNew = ''.join((s[0:i0 + i1 + 1], ' ', str(self.sizes.readAttributeWidth), s[i0 + i2:]))
            self.valueSpinbox.setStyleSheet(sNew)
        self.valueSpinbox.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Minimum)

        self.valueSlider = QTangoHSliderBase2(self.sizes, self.attrColors)
        self.writeLabel = QTangoStartLabel(self.sizes, self.attrColors)
        self.writeLabel.currentAttrColor = self.attrColors.backgroundColor
        self.writeLabel.setupLayout()

        self.vSpacer = QtGui.QSpacerItem(20, self.sizes.barHeight, QtGui.QSizePolicy.Minimum,
                                         QtGui.QSizePolicy.MinimumExpanding)

        self.layout = QtGui.QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setMargin(int(self.sizes.barHeight / 10))
        self.layout.setSpacing(self.sizes.barHeight / 3)

        self.layoutGrid = QtGui.QGridLayout()
        self.layoutGrid.setContentsMargins(0, 0, 0, 0)
        self.layoutGrid.setMargin(int(self.sizes.barHeight / 10))
        self.layoutGrid.setMargin(0)
        self.layoutGrid.addWidget(self.nameLabel, 0, 0, 1, 2)
        #		self.layoutGrid.addWidget(self.unitLabel, 0, 1)
        self.layoutGrid.addWidget(self.valueSpinbox, 1, 1)
        self.layoutGrid.addItem(self.vSpacer, 2, 0)
        self.layoutGrid.addWidget(self.valueSlider, 2, 0, 1, 2)
        # 		self.layoutGrid.addWidget(self.writeLabel, 1, 2)

        self.layoutGrid.setHorizontalSpacing(self.sizes.barHeight / 4)
        self.layoutGrid.setVerticalSpacing(self.sizes.barHeight / 10)

        self.layout.addWidget(self.startLabel)
        self.layout.addLayout(self.layoutGrid)
        self.layout.addWidget(self.endLabel)

        self.setMaximumWidth(self.sizes.readAttributeWidth)
        self.setMinimumWidth(self.sizes.readAttributeWidth)
        self.setMaximumHeight(self.sizes.barHeight * 4)
        self.setMinimumHeight(self.sizes.barHeight * 4)
        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)

    def configureAttribute(self, attrInfo):
        QTangoReadAttributeSlider2.configureAttribute(self, attrInfo)
        self.valueSpinbox.setSuffix(''.join((' ', self.attrInfo.unit)))

    def setAttributeName(self, aName, aUnit=None):
        self.nameLabel.setText(aName)
        if aUnit is not None:
            self.valueSpinbox.setSuffix(QtCore.QString.fromUtf8(''.join((' ', aUnit))))
        self.update()


# noinspection PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit
class QTangoReadAttributeSliderCompact(QTangoAttributeBase):
    def __init__(self, sizes=None, colors=None, parent=None):
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
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setMargin(int(self.sizes.barHeight / 10))
        self.layout.setMargin(0)
        self.layout.setSpacing(self.sizes.barWidth / 3)

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
        self.setMaximumHeight(self.sizes.barHeight * 1.6)
        self.setMinimumHeight(self.sizes.barHeight * 1.6)
        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)

    def attributeName(self):
        return str(self.nameLabel.text())

    @QtCore.pyqtSignature('setAttributeName(QString)')
    def setAttributeName(self, aName, aUnit=None):
        self.nameLabel.setText(aName)
        if aUnit is not None:
            self.unitLabel.setText(aUnit)
            self.valueSpinbox.setSuffix(''.join((' ', aUnit)))
        self.update()

    def setAttributeValue(self, value):
        if type(value) == pt.DeviceAttribute:
            self.startLabel.setQuality(value.quality)
            self.endLabel.setQuality(value.quality)
            self.nameLabel.setQuality(value.quality)
            if value.value is not None:
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

    def setSliderLimits(self, min_limit, max_limit):
        self.valueSlider.setSliderLimits(min_limit, max_limit)

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


# noinspection PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit
class QTangoReadAttributeSliderV(QTangoReadAttributeSlider2):
    def __init__(self, sizes=None, colors=None, parent=None):
        QTangoAttributeBase.__init__(self, sizes, colors, parent)
        self.unit = None
        self.prefixDict = {'k': 1e3, 'M': 1e6, 'G': 1e9, 'T': 1e12, 'P': 1e15,
                           'm': 1e-3, 'u': 1e-6, 'n': 1e-9, 'p': 1e-12, 'f': 1e-15, 'c': 1e-2}
        self.prefix = None
        self.prefixFactor = 1.0
        self.setupLayout()

    def setupLayout(self):
        self.nameLabel = QTangoAttributeNameLabel(self.sizes, self.attrColors)
        sizesValue = copy.copy(self.sizes)
        sizesValue.barHeight *= 1.25

        self.valueSlider = QTangoVSliderBase2(self.sizes, self.attrColors)
        self.writeLabel = QTangoStartLabel(self.sizes, self.attrColors)
        self.writeLabel.currentAttrColor = self.attrColors.backgroundColor
        self.writeLabel.setupLayout()

        self.unitLabel = QTangoAttributeNameLabel(self.sizes, self.attrColors)

        self.vSpacer = QtGui.QSpacerItem(20, self.sizes.barHeight, QtGui.QSizePolicy.Minimum,
                                         QtGui.QSizePolicy.MinimumExpanding)

        self.layout = QtGui.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setMargin(int(self.sizes.barHeight / 10))
        self.layout.setSpacing(self.sizes.barHeight / 10)

        self.layout.addWidget(self.valueSlider)
        self.layout.addWidget(self.nameLabel)
        self.layout.addWidget(self.unitLabel)

        self.setMaximumWidth(self.sizes.barWidth * 4.3)
        self.setMinimumWidth(self.sizes.barWidth * 4.3)
        self.setMaximumHeight(self.sizes.readAttributeHeight)
        self.setMinimumHeight(self.sizes.readAttributeHeight)
        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)

    def attributeName(self):
        return str(self.nameLabel.text())

    @QtCore.pyqtSignature('setAttributeName(QString)')
    def setAttributeName(self, aName, aUnit=None):
        self.nameLabel.setText(aName)
        if aUnit is not None:
            self.valueSlider.setUnit(aUnit)
            self.setUnit(aUnit)
        self.update()

    def setAttributeValue(self, value):
        if type(value) == pt.DeviceAttribute:
            logger.debug("QTangoReadAttributeSliderV quality {0}".format(value.quality))
            # if value.value is not None:
            self.valueSlider.setValue(value)
            self.nameLabel.setQuality(value.quality)
            self.unitLabel.setQuality(value.quality)
        else:
            val = value
            self.valueSlider.setValue(val)
        self.update()

    def setUnit(self, unit):
        self.unit = unit
        if self.unit is not None:
            unitStr = self.unit
            if self.prefix is not None:
                unitStr = ''.join((self.prefix, unitStr))

            self.unitLabel.setText(unitStr)

    def setPrefix(self, prefix):
        try:
            self.prefixFactor = self.prefixDict[prefix]
            self.prefix = prefix
            self.setUnit(self.unit)
        except KeyError:
            self.prefix = None
            self.prefixFactor = 1.0

    def setAttributeWarningLimits(self, limits):
        self.valueSlider.setWarningLimits(limits)

    def setSliderLimits(self, min_limit, max_limit):
        self.valueSlider.setSliderLimits(min_limit, max_limit)

    def setSliderRangeAnchor(self, anchor, range, anchorPos=0.75):
        """Set the slider total range. The anchor value is set at
        realtive position anchorPos (0-1)
        """
        valMin = anchor - range * anchorPos
        valMax = anchor + range * (1 - anchorPos)
        self.valueSlider.setSliderLimits(valMin, valMax)

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
        self.setUnit(self.attrInfo.unit)


# noinspection PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit
class QTangoReadAttributeBoolean(QTangoAttributeBase):
    def __init__(self, sizes=None, colors=None, parent=None):
        QTangoAttributeBase.__init__(self, sizes, colors, parent)
        self.setupLayout()

    def setupLayout(self):
        readValueWidth = self.sizes.barWidth
        readWidth = self.sizes.readAttributeWidth - self.sizes.barHeight / 6 - self.sizes.barHeight / 2

        self.startLabel = QTangoStartLabel(self.sizes, self.attrColors)
        self.endLabel = QTangoEndLabel(self.sizes, self.attrColors)
        self.nameLabel = QTangoAttributeNameLabel(self.sizes, self.attrColors)
        self.valueBoolean = QTangoBooleanLabel(self.sizes, self.attrColors)

        self.layout = QtGui.QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        #		self.layout.setMargin(int(self.sizes.barHeight/10))
        self.layout.setMargin(0)
        self.layout.setSpacing(self.sizes.barWidth / 3)

        self.layoutGrid = QtGui.QGridLayout()
        self.layoutGrid.setContentsMargins(0, 0, 0, 0)
        #		self.layoutGrid.setMargin(int(self.sizes.barHeight/10))
        self.layoutGrid.setMargin(0)
        self.layoutGrid.addWidget(self.nameLabel, 0, 0, )
        self.layoutGrid.addWidget(self.valueBoolean, 0, 1)
        self.layoutGrid.setHorizontalSpacing(self.sizes.barWidth / 4)
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
            if value.dim_x > 1:
                val = value.value[0]
            else:
                val = value.value
        else:
            val = value

        self.valueBoolean.setBooleanState(val)
        self.update()


# noinspection PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit
class QTangoReadAttributeTrend(QtGui.QWidget):
    def __init__(self, name=None, sizes=None, colors=None, parent=None):
        QtGui.QWidget.__init__(self, parent)
        if colors is None:
            self.attrColors = QTangoColors()
        else:
            self.attrColors = colors
        if sizes is None:
            self.sizes = QTangoSizes()
        else:
            self.sizes = sizes
        self.unit = None
        self.prefixDict = {'k': 1e3, 'M': 1e6, 'G': 1e9, 'T': 1e12, 'P': 1e15,
                           'm': 1e-3, 'u': 1e-6, 'n': 1e-9, 'p': 1e-12, 'f': 1e-15, 'c': 1e-2}
        self.prefix = None
        self.prefixFactor = 1.0

        self.curve_focus = 0
        self.setupLayout(name)

    def setupLayout(self, name=None):
        readValueWidth = self.sizes.barWidth
        readWidth = self.sizes.readAttributeWidth - self.sizes.barHeight / 6 - self.sizes.barHeight / 2

        self.startLabel = QTangoStartLabel(self.sizes, self.attrColors)
        self.endLabel = QTangoEndLabel(self.sizes, self.attrColors)
        self.nameLabel = QTangoAttributeNameLabel(self.sizes, self.attrColors)
        self.unitLabel = QTangoAttributeNameLabel(self.sizes, self.attrColors)
        self.curveNameLabel = QTangoAttributeNameLabel(self.sizes, self.attrColors)
        if name is not None:
            self.curveNameLabel.setText(name)
        else:
            self.curveNameLabel.setText(''.join(('curve 0')))
        self.valueSpinbox = QTangoReadAttributeLabel(self.sizes, self.attrColors)
        self.nameLabel.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        #		self.valueSpinbox.setMinimumWidth(50)
        self.valueSlider = QTangoVSliderBase2(self.sizes, self.attrColors)

        self.valueTrend = QTangoTrendBase(name=name, sizes=self.sizes, colors=self.attrColors)
        self.valueTrend.valueTrendCurves[-1].sigClicked.connect(self.setCurveFocus)

        self.layout = QtGui.QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setMargin(int(self.sizes.barHeight/10))
        # self.layout.setMargin(0)
        self.layout.setSpacing(self.sizes.barWidth / 3)

        layout2 = QtGui.QVBoxLayout()
        layout3 = QtGui.QHBoxLayout()
        layout2.addLayout(layout3)
        layout2.addWidget(self.valueTrend)
        layout3.addWidget(self.nameLabel)
        layout3.addWidget(self.curveNameLabel)
        layout3.addWidget(self.valueSpinbox)
        layout3.addWidget(self.unitLabel)

        self.layout.addWidget(self.startLabel)
        self.layout.addLayout(layout2)
        self.layout.addWidget(self.endLabel)

        self.setMaximumWidth(self.sizes.readAttributeWidth)
        self.setMinimumWidth(self.sizes.readAttributeWidth)
        self.setMaximumHeight(self.sizes.barHeight * 4)
        self.setMinimumHeight(self.sizes.barHeight * 4)
        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)

    def attributeName(self):
        return str(self.nameLabel.text())

    @QtCore.pyqtSignature('setAttributeName(QString)')
    def setAttributeName(self, aName, aUnit=None):
        self.nameLabel.setText(aName)
        if aUnit is not None:
            self.valueSlider.setUnit(aUnit)
            self.setUnit(aUnit)
        self.update()

    def setAttributeValue(self, value, curve=0):
        if type(value) == pt.DeviceAttribute:
            if value.value is not None:
                if curve == 0:
                    self.valueSlider.setValue(value)
                    self.valueSpinbox.setValue(value)
                self.valueTrend.addPoint(value, curve)
                self.nameLabel.setQuality(value.quality)
                self.unitLabel.setQuality(value.quality)
        else:
            t = time.time()
            self.valueTrend.addPoint([t, value], curve)
            if curve == 0:
                self.valueSlider.setValue(value)
                self.valueSpinbox.setValue(value)

        self.update()

    def addPoint(self, value, curve=0):
        if type(value) == pt.DeviceAttribute:
            if value.value is not None:
                value.value /= self.prefixFactor
                self.valueSlider.setValue(value)
                self.valueTrend.addPoint(value, curve)
                self.nameLabel.setQuality(value.quality)
                self.curveNameLabel.setQuality(value.quality)
                self.unitLabel.setQuality(value.quality)
                self.startLabel.setQuality(value.quality)
                self.endLabel.setQuality(value.quality)
                self.unitLabel.setQuality(value.quality)
                self.valueSpinbox.setQuality(value.quality)
        else:
            value /= self.prefixFactor
            self.valueSlider.setValue(value)
            t = time.time()
            self.valueTrend.addPoint([t, value], curve)
        if curve == self.curve_focus:
            self.valueSlider.setValue(value)
            self.valueSpinbox.setValue(value)
        self.update()

    def setUnit(self, unit):
        self.unit = unit
        if self.unit is not None:
            unitStr = self.unit
            if self.prefix is not None:
                unitStr = ''.join((self.prefix, unitStr))

            self.unitLabel.setText(unitStr)

    def setPrefix(self, prefix):
        try:
            self.prefixFactor = self.prefixDict[prefix]
            self.prefix = prefix
            self.setUnit(self.unit)
        except KeyError:
            self.prefix = None
            self.prefixFactor = 1.0

    def setAttributeWarningLimits(self, limits):
        self.valueSlider.setWarningLimits(limits)
        self.valueTrend.setWarningLimits(limits)

    def setSliderLimits(self, min, max):
        self.valueSlider.setSliderLimits(min, max)

    def setSliderRangeAnchor(self, anchor, range, anchorPos=0.75):
        '''Set the slider total range. The anchor value is set at
        realtive position anchorPos (0-1)
        '''
        valMin = anchor - range * anchorPos
        valMax = anchor + range * (1 - anchorPos)
        self.valueSlider.setSliderLimits(valMin, valMax)

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
        self.setUnit(self.attrInfo.unit)

    def setTrendLimits(self, low, high):
        self.valueTrend.setYRange(low, high, padding=0.05)

    def addCurve(self, name=None):
        self.valueTrend.addCurve(name)
        self.valueTrend.valueTrendCurves[-1].sigClicked.connect(self.setCurveFocus)

    def setCurveFocus(self, curve):
        name = curve.opts.get('name', None)
        if name is not None:
            self.curve_focus = self.valueTrend.curve_name_list.index(name)
            self.curveNameLabel.setText(name)

    def setCurveName(self, curve, name):
        self.valueTrend.setCurveName(curve, name)

    def showLegend(self, show_legend=True):
        self.valueTrend.showLegend(show_legend)

    def setDuration(self, duration):
        self.valueTrend.setDuration(duration)


# noinspection PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit
class QTangoReadAttributeSpectrum(QTangoAttributeBase):
    def __init__(self, sizes=None, colors=None, parent=None):
        QTangoAttributeBase.__init__(self, sizes, colors, parent)
        self.setupLayout()

    def setupLayout(self):
        readValueWidth = self.sizes.barWidth
        readWidth = self.sizes.readAttributeWidth - self.sizes.barHeight / 6 - self.sizes.barHeight / 2

        self.startLabel = QTangoStartLabel(self.sizes, self.attrColors)
        self.endLabel = QTangoEndLabel(self.sizes, self.attrColors)
        self.nameLabel = QTangoAttributeNameLabel(self.sizes, self.attrColors)
        self.spectrum = QTangoSpectrumBase(self.sizes, self.attrColors)
        # 		self.spectrum.useOpenGL(True)
        # 		self.spectrum.setBackground(None)
        # 		self.spectrum.setAntialiasing(True)

        self.layout = QtGui.QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setMargin(int(self.sizes.barWidth / 10))
        #		self.layout.setMargin(0)
        self.layout.setSpacing(self.sizes.barWidth / 3)

        self.layoutGrid = QtGui.QGridLayout()
        self.layoutGrid.setContentsMargins(0, 0, 0, 0)
        self.layoutGrid.setMargin(0)
        self.layoutGrid.addWidget(self.nameLabel, 0, 0)
        self.layoutGrid.addWidget(self.spectrum, 1, 0, 1, 2)
        self.layoutGrid.setHorizontalSpacing(self.sizes.barWidth / 4)
        self.layoutGrid.setVerticalSpacing(0)

        self.layout.addWidget(self.startLabel)
        self.layout.addLayout(self.layoutGrid)
        self.layout.addWidget(self.endLabel)

        self.setMinimumWidth(self.sizes.readAttributeWidth)
        self.setMinimumHeight(self.sizes.barHeight * 6)
        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)

    def attributeName(self):
        return str(self.nameLabel.text())

    @QtCore.pyqtSignature('setAttributeName(QString)')
    def setAttributeName(self, aName):
        self.nameLabel.setText(aName)
        self.update()

    def setSpectrum(self, xData, yData, index=0):
        if type(xData) == pt.DeviceAttribute:
            xData = xData.value
        if type(yData) == pt.DeviceAttribute:
            self.startLabel.setQuality(yData.quality)
            self.endLabel.setQuality(yData.quality)
            self.nameLabel.setQuality(yData.quality)
            self.spectrum.setQuality(yData.quality)
            yData = yData.value
        self.spectrum.setSpectrum(xData, yData, index)

    def setXRange(self, low, high):
        self.spectrum.setXRange(low, high)

    def fixedSize(self, fixed=True):
        if fixed is True:
            self.spectrum.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
            self.setMaximumWidth(self.sizes.readAttributeWidth)
        else:
            self.spectrum.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)


# noinspection PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit
class QTangoReadAttributeImage(QTangoAttributeBase):
    def __init__(self, sizes=None, colors=None, parent=None):
        QTangoAttributeBase.__init__(self, sizes, colors, parent)
        self.setupLayout()

    def setupLayout(self):
        self.startLabel = QTangoStartLabel(self.sizes, self.attrColors)
        self.endLabel = QTangoEndLabel(self.sizes, self.attrColors)
        self.nameLabel = QTangoAttributeNameLabel(self.sizes, self.attrColors)
        self.imageWidget = QTangoImageBase(self.sizes, self.attrColors)

        self.layout = QtGui.QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setMargin(int(self.sizes.barWidth / 10))
        #		self.layout.setMargin(0)
        self.layout.setSpacing(self.sizes.barWidth / 3)

        self.layoutGrid = QtGui.QGridLayout()
        self.layoutGrid.setContentsMargins(0, 0, 0, 0)
        self.layoutGrid.setMargin(0)
        self.layoutGrid.addWidget(self.nameLabel, 0, 0)
        self.layoutGrid.addWidget(self.imageWidget, 1, 0, 1, 2)
        self.layoutGrid.setHorizontalSpacing(self.sizes.barWidth / 4)
        self.layoutGrid.setVerticalSpacing(0)

        self.layout.addWidget(self.startLabel)
        self.layout.addLayout(self.layoutGrid)
        self.layout.addWidget(self.endLabel)

        self.setMinimumWidth(self.sizes.readAttributeWidth)
        self.setMinimumHeight(self.sizes.barHeight * 6)
        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)

    def attributeName(self):
        return str(self.nameLabel.text())

    @QtCore.pyqtSignature('setAttributeName(QString)')
    def setAttributeName(self, aName):
        self.nameLabel.setText(aName)
        self.update()

    def setImage(self, image, auto_levels=False):
        if type(image) == pt.DeviceAttribute:
            im = image.value
            self.startLabel.setQuality(image.quality)
            self.endLabel.setQuality(image.quality)
            self.nameLabel.setQuality(image.quality)
        self.imageWidget.setImage(im, auto_levels)

    def fixedSize(self, fixed=True):
        if fixed is True:
            self.imageWidget.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
            self.setMaximumWidth(self.sizes.readAttributeWidth)
        else:
            self.imageWidget.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)


# noinspection PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit
class QTangoReadAttributeImageWithHist(QTangoAttributeBase):
    def __init__(self, sizes=None, colors=None, parent=None):
        QTangoAttributeBase.__init__(self, sizes, colors, parent)
        self.setupLayout()

    def setupLayout(self):
        self.startLabel = QTangoStartLabel(self.sizes, self.attrColors)
        self.endLabel = QTangoEndLabel(self.sizes, self.attrColors)
        self.nameLabel = QTangoAttributeNameLabel(self.sizes, self.attrColors)
        self.imageWidget = QTangoImageWithHistBase(self.sizes, self.attrColors)

        self.layout = QtGui.QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setMargin(int(self.sizes.barWidth / 10))
        #		self.layout.setMargin(0)
        self.layout.setSpacing(self.sizes.barWidth / 3)

        self.layoutGrid = QtGui.QGridLayout()
        self.layoutGrid.setContentsMargins(0, 0, 0, 0)
        self.layoutGrid.setMargin(0)
        self.layoutGrid.addWidget(self.nameLabel, 0, 0)
        self.layoutGrid.addWidget(self.imageWidget, 1, 0, 1, 2)
        self.layoutGrid.setHorizontalSpacing(self.sizes.barWidth / 4)
        self.layoutGrid.setVerticalSpacing(0)

        self.layout.addWidget(self.startLabel)
        self.layout.addLayout(self.layoutGrid)
        self.layout.addWidget(self.endLabel)

        self.setMinimumWidth(self.sizes.readAttributeWidth)
        self.setMinimumHeight(self.sizes.barHeight * 6)
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
        self.imageWidget.setImage(im, autoRange=False, autoLevels=False)


# noinspection PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit
class QTangoWriteAttributeSlider(QTangoAttributeBase):
    def __init__(self, sizes=None, colors=None, parent=None):
        QTangoAttributeBase.__init__(self, sizes, colors, parent)
        self.setupLayout()

        self.writeValueInitialized = False

    def setupLayout(self):
        readValueWidth = self.sizes.barWidth
        readWidth = self.sizes.readAttributeWidth - self.sizes.barHeight / 6 - self.sizes.barHeight / 2

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
        self.layout.setContentsMargins(0, 0, 0, 0)
        #		self.layout.setMargin(int(self.sizes.barHeight/10))
        self.layout.setMargin(0)
        self.layout.setSpacing(self.sizes.barWidth / 3)

        self.layoutGrid = QtGui.QGridLayout()
        self.layoutGrid.setContentsMargins(0, 0, 0, 0)
        self.layoutGrid.setMargin(int(self.sizes.barWidth / 10))
        self.layoutGrid.setMargin(0)
        self.layoutGrid.setHorizontalSpacing(self.sizes.barWidth / 4)
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
        self.setMaximumHeight(self.sizes.barHeight * 2.2)
        self.setMaximumHeight(self.sizes.barHeight * 2.7)
        # self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)

    def attributeName(self):
        return str(self.nameLabel.text())

    @QtCore.pyqtSignature('setAttributeName(QString)')
    def setAttributeName(self, aName, aUnit=None):
        self.nameLabel.setText(aName)
        if aUnit is not None:
            self.unitLabel.setText(aUnit)
        self.update()

    def setAttributeValue(self, data):

        if type(data) == pt.DeviceAttribute:
            self.startLabel.setQuality(data.quality)
            self.endLabel.setQuality(data.quality)
            if data.value is not None:
                self.valueSpinbox.setValue(data.value)
                self.valueSlider.setValue(data.value)
                if self.writeValueInitialized is False:
                    logger.debug('Initializing write value')
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

    def setSliderLimits(self, min_limit, max_limit):
        self.valueSlider.setSliderLimits(min_limit, max_limit)

    def editingFinished(self):
        self.valueSlider.setWriteValue(self.writeValueSpinbox.value())
        self.update()
        logger.debug('updating slider to {0}'.format(self.writeValueSpinbox.value()))

    def getWriteValue(self):
        return self.writeValueSpinbox.value()


# noinspection PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit
class QTangoWriteAttributeSlider4(QTangoWriteAttributeSlider):
    def __init__(self, sizes=None, colors=None, parent=None):
        QTangoWriteAttributeSlider.__init__(self, sizes, colors, parent)

    def setupLayout(self):
        self.startLabel = QTangoStartLabel(self.sizes, self.attrColors)
        self.endLabel = QTangoEndLabel(self.sizes, self.attrColors)
        self.nameLabel = QTangoAttributeNameLabel(self.sizes, self.attrColors)
        self.unitLabel = QTangoAttributeUnitLabel(self.sizes, self.attrColors)
        sizesValue = copy.copy(self.sizes)
        sizesValue.barHeight *= 1.0
        self.valueSpinbox = QTangoReadAttributeSpinBox(sizesValue, self.attrColors)
        s = str(self.valueSpinbox.styleSheet())
        if s != '':
            i0 = s.find('\nmax-width')
            i1 = s[i0:].find(':')
            i2 = s[i0:].find(';')
            sNew = ''.join((s[0:i0 + i1 + 1], ' ', str(self.sizes.readAttributeWidth), s[i0 + i2:]))
            self.valueSpinbox.setStyleSheet(sNew)
        self.valueSpinbox.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Minimum)

        self.valueSlider = QTangoHSliderBase2(self.sizes, self.attrColors)
        # 		self.writeValueSpinbox = QTangoWriteAttributeSpinBox2(sizesValue, self.attrColors)
        # 		self.writeValueSpinbox.editingFinished.connect(self.editingFinished)
        self.writeValueLineEdit = QTangoWriteAttributeLineEdit(self.sizes, self.attrColors)
        self.writeValueLineEdit.editingFinished.connect(self.editingFinished)
        self.writeValueLineEdit.setLayoutDirection(QtCore.Qt.RightToLeft)

        self.writeLabel = QTangoStartLabel(self.sizes, self.attrColors)
        self.writeLabel.currentAttrColor = self.attrColors.backgroundColor
        self.writeLabel.setupLayout()
        # 		s = str(self.writeValueSpinbox.styleSheet())
        # 		if s != '':
        # 			i0 = s.find('\nmax-width')
        # 			i1 = s[i0:].find(':')
        # 			i2 = s[i0:].find(';')
        # 			sNew = ''.join((s[0:i0+i1+1],' ', str(self.sizes.readAttributeWidth), s[i0+i2:]))
        # 			self.writeValueSpinbox.setStyleSheet(sNew)
        # 		self.writeValueSpinbox.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Minimum)

        self.vSpacer = QtGui.QSpacerItem(20, self.sizes.barHeight, QtGui.QSizePolicy.Minimum,
                                         QtGui.QSizePolicy.MinimumExpanding)

        self.layout = QtGui.QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setMargin(int(self.sizes.barHeight / 10))
        self.layout.setSpacing(self.sizes.barHeight / 3)

        # 		self.layoutGrid = QtGui.QVBoxLayout()
        # 		self.layoutGrid.setContentsMargins(0, 0, 0, 0)
        # 		self.layoutGrid.setMargin(int(self.sizes.barHeight/10))
        # #		self.layoutGrid.setMargin(0)
        # 		self.layoutGrid.addWidget(self.nameLabel)
        # #		self.layoutGrid.addWidget(self.unitLabel, 0, 1)
        # 		layoutSpinboxes = QtGui.QHBoxLayout()
        # #		layoutSpinboxes.addWidget(self.writeValueSpinbox)
        # 		layoutSpinboxes.addWidget(self.writeValueLineEdit)
        # 		layoutSpinboxes.addWidget(self.valueSpinbox)
        # 		self.layoutGrid.addLayout(layoutSpinboxes)
        # 		self.layoutGrid.addItem(self.vSpacer)
        # 		self.layoutGrid.addWidget(self.valueSlider)
        # 		self.layoutGrid.addWidget(self.writeLabel, 1, 2)

        #		self.layoutGrid.setHorizontalSpacing(self.sizes.barHeight/4)
        #		self.layoutGrid.setSpacing(self.sizes.barHeight/10)

        # 		self.layoutGrid = QtGui.QGridLayout()
        # 		self.layoutGrid.setContentsMargins(0, 0, 0, 0)
        # 		self.layoutGrid.setMargin(int(self.sizes.barHeight/10))
        # #		self.layoutGrid.setVerticalSpacing(self.sizes.barHeight/4)
        # 		self.layoutGrid.addWidget(self.nameLabel,0,0)
        # 		self.layoutGrid.addWidget(self.valueSpinbox,0,2)
        # 		self.layoutGrid.addWidget(self.writeLabel,1,1)
        # 		self.layoutGrid.addWidget(self.writeValueLineEdit,1,2)
        # #		self.layoutGrid.addWidget(self.valueSlider,2,0,1,3)
        # 		self.layoutGrid.addWidget(self.valueSlider,2,0)

        layoutV = QtGui.QVBoxLayout()
        layoutH1 = QtGui.QHBoxLayout()
        layoutH1.addWidget(self.nameLabel)
        layoutH1.addWidget(self.valueSpinbox)
        layoutH2 = QtGui.QHBoxLayout()
        spacerItemH = QtGui.QSpacerItem(5, 5, QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Minimum)
        layoutH2.addSpacerItem(spacerItemH)
        layoutH2.addWidget(self.writeLabel)
        layoutH2.addWidget(self.writeValueLineEdit)
        layoutV.addLayout(layoutH1)
        layoutV.addLayout(layoutH2)
        layoutV.addWidget(self.valueSlider)

        self.layout.addWidget(self.startLabel)
        #		self.layout.addLayout(self.layoutGrid)
        self.layout.addLayout(layoutV)
        self.layout.addWidget(self.endLabel)

        self.setMaximumWidth(self.sizes.readAttributeWidth)
        self.setMinimumWidth(self.sizes.readAttributeWidth)
        self.setMaximumHeight(self.sizes.barHeight * 4)
        self.setMinimumHeight(self.sizes.barHeight * 4)
        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)

    def configureAttribute(self, attrInfo):
        QTangoReadAttributeSlider2.configureAttribute(self, attrInfo)
        self.valueSpinbox.setSuffix(''.join((' ', self.attrInfo.unit)))

    def setAttributeName(self, aName, aUnit=None):
        self.nameLabel.setText(aName)
        if aUnit is not None:
            self.valueSpinbox.setSuffix(QtCore.QString.fromUtf8(''.join((' ', aUnit))))
        self.update()

    def setAttributeValue(self, data):
        if type(data) == pt.DeviceAttribute:
            self.startLabel.setQuality(data.quality)
            self.endLabel.setQuality(data.quality)
            if data.value is not None:
                self.valueSlider.setValue(data.value)
                self.valueSpinbox.setValue(data.value)
                if self.writeValueInitialized is False:
                    logger.debug("Initializing write value")
                    self.writeValueInitialized = True
                    self.setAttributeWriteValue(data.w_value)

                if data.w_value != self.writeValueLineEdit.value():
                    if self.writeLabel.currentAttrColor != self.attrColors.secondaryColor0:
                        self.writeLabel.currentAttrColor = self.attrColors.secondaryColor0
                        self.writeLabel.setupLayout()
                else:
                    if self.writeLabel.currentAttrColor != self.attrColors.backgroundColor:
                        self.writeLabel.currentAttrColor = self.attrColors.backgroundColor
                        self.writeLabel.setupLayout()
        else:
            self.valueSlider.setValue(data)
            self.valueSpinbox.setValue(data)
        self.update()

    def setAttributeWriteValue(self, value):
        self.writeValueLineEdit.setValue(value)
        self.valueSlider.setWriteValue(value)
        self.update()

    def setSliderLimits(self, min_limit, max_limit):
        self.valueSlider.setSliderLimits(min_limit, max_limit)

    def editingFinished(self):
        if self.writeValueLineEdit.validatorObject.validate(self.writeValueLineEdit.text(), 0)[
            0] == QtGui.QValidator.Acceptable:
            self.valueSlider.setWriteValue(np.double(self.writeValueLineEdit.text()))
        self.update()
        logger.debug('updating slider to {0}'.format(self.writeValueLineEdit.text()))

    def getWriteValue(self):
        return self.writeValueLineEdit.value()


# noinspection PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit
class QTangoWriteAttributeSliderV(QTangoWriteAttributeSlider):
    def __init__(self, sizes=None, colors=None, parent=None):
        QTangoWriteAttributeSlider.__init__(self, sizes, colors, parent)
        self.unit = None
        self.wheel_step = 0.1
        self.wheel_update = False

    def setupLayout(self):
        self.nameLabel = QTangoAttributeNameLabel(self.sizes, self.attrColors)
        sizesValue = copy.copy(self.sizes)
        sizesValue.barHeight *= 1.25

        self.valueSlider = QTangoVSliderBase2(self.sizes, self.attrColors)
        self.writeLabel = QTangoStartLabel(self.sizes, self.attrColors)
        self.writeLabel.currentAttrColor = self.attrColors.backgroundColor
        self.writeLabel.setupLayout()
        # 		self.writeValueSpinbox = QTangoWriteAttributeSpinBox2(self.sizes, self.attrColors)
        # 		self.writeValueSpinbox.editingFinished.connect(self.editingFinished)
        # 		self.writeValueSpinbox.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.writeValueLineEdit = QTangoWriteAttributeLineEdit(self.sizes, self.attrColors)
        self.writeValueLineEdit.editingFinished.connect(self.editingFinished)
        self.writeValueLineEdit.setLayoutDirection(QtCore.Qt.RightToLeft)

        self.vSpacer = QtGui.QSpacerItem(20, self.sizes.barHeight, QtGui.QSizePolicy.Minimum,
                                         QtGui.QSizePolicy.MinimumExpanding)

        self.layout = QtGui.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setMargin(int(self.sizes.barHeight / 10))
        self.layout.setSpacing(self.sizes.barHeight / 6.0)

        layout2 = QtGui.QHBoxLayout()
        layout2.setContentsMargins(0, 0, 0, 0)
        layout2.setMargin(int(self.sizes.barHeight / 10))
        layout2.setSpacing(self.sizes.barHeight / 6.0)
        layout2.addWidget(self.writeLabel)
        layout2.addWidget(self.writeValueLineEdit)

        self.layout.addWidget(self.valueSlider)
        self.layout.addLayout(layout2)
        #		self.layout.addWidget(self.writeValueLineEdit)
        self.layout.addWidget(self.nameLabel)

        self.setMaximumWidth(self.sizes.barWidth * 4)
        self.setMinimumWidth(self.sizes.barWidth * 4)
        self.setMaximumHeight(self.sizes.readAttributeHeight)
        self.setMinimumHeight(self.sizes.readAttributeHeight)
        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)

    def attributeName(self):
        return str(self.nameLabel.text())

    @QtCore.pyqtSignature('setAttributeName(QString)')
    def setAttributeName(self, aName, aUnit=None):
        self.nameLabel.setText(aName)
        if aUnit is not None:
            self.valueSlider.setUnit(aUnit)
            self.unit = aUnit
        self.update()

    def setAttributeValue(self, data):
        if type(data) == pt.DeviceAttribute:
            if data.value is not None:
                #				self.valueSlider.setValue(data.value)
                self.valueSlider.setValue(data)
                if self.writeValueInitialized is False:
                    logger.debug('Initializing write value')
                    self.writeValueInitialized = True
                    self.setAttributeWriteValue(data.w_value)

                if np.abs((data.w_value - self.writeValueLineEdit.value()) / data.w_value) > 0.0001:
                    if self.writeLabel.currentAttrColor != self.attrColors.secondaryColor0:
                        self.writeLabel.currentAttrColor = self.attrColors.secondaryColor0
                        self.writeLabel.setupLayout()
                else:
                    if self.writeLabel.currentAttrColor != self.attrColors.backgroundColor:
                        self.writeLabel.currentAttrColor = self.attrColors.backgroundColor
                        self.writeLabel.setupLayout()
        else:
            self.valueSlider.setValue(data)
            self.unitLabel.setQuality(data.quality)
            self.valueSpinbox.setQuality(data.quality)
            self.nameLabel.setQuality(data.quality)
        self.update()

    def setAttributeWriteValue(self, value):
        self.writeValueLineEdit.setValue(value)
        self.valueSlider.setWriteValue(value)
        self.update()

    def setAttributeWarningLimits(self, limits):
        self.valueSlider.setWarningLimits(limits)

    def setSliderLimits(self, min_limit, max_limit):
        self.valueSlider.setSliderLimits(min_limit, max_limit)

    def editingFinished(self):
        if self.writeValueLineEdit.validatorObject.validate(self.writeValueLineEdit.text(), 0)[
            0] == QtGui.QValidator.Acceptable:
            self.valueSlider.setWriteValue(np.double(self.writeValueLineEdit.text()))
        self.update()
        logger.debug('updating slider to {0}'.format(self.writeValueLineEdit.text()))

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

    def getWriteValue(self):
        return self.writeValueLineEdit.value()

    def wheelEvent(self, event):
        logger.debug("Wheel event delta: {0}".format(event.delta()))
        self.setAttributeWriteValue(self.getWriteValue() + self.wheel_step * event.delta() / 120.0)
        if self.wheel_update:
            self.writeValueLineEdit.newValueSignal.emit()


# noinspection PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit
class QTangoWriteAttributeDouble(QtGui.QWidget):
    def __init__(self, sizes=None, colors=None, precision=4, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.attrColors = QTangoColors()
        if colors is None:
            self.attrColors = QTangoColors()
        else:
            self.attrColors = colors
        if sizes is None:
            self.sizes = QTangoSizes()
        else:
            self.sizes = sizes

        self.writeValueInitialized = False
        self.unit = None
        self.precision = precision
        self.prefix = None

        self.setupLayout()

    def setupLayout(self):
        readValueWidth = self.sizes.barWidth
        readWidth = self.sizes.readAttributeWidth - int(self.sizes.barHeight / 6) - readValueWidth
        logger.debug('writeAttr readwidth: {0}'.format(readWidth))
        writeValueWidth = self.sizes.writeAttributeWidth - self.sizes.readAttributeWidth - int(
            self.sizes.barHeight / 6) - int(self.sizes.barHeight / 2)

        self.startLabel = QTangoStartLabel(self.sizes, self.attrColors)
        self.endLabel = QTangoEndLabel(self.sizes, self.attrColors)
        self.nameLabel = QTangoAttributeNameLabel(self.sizes, self.attrColors)
        self.nameLabel.setSizePolicy(Qt.QSizePolicy.Expanding, Qt.QSizePolicy.Minimum)
        self.unitLabel = QTangoAttributeUnitLabel(self.sizes, self.attrColors)
        #		self.valueSpinbox = QTangoReadAttributeSpinBox(self.sizes, self.attrColors)
        self.valueSpinbox = QTangoReadAttributeLabel(self.sizes, self.attrColors)
        #		self.writeValueSpinbox = QTangoWriteAttributeSpinBox(self.sizes, self.attrColors)
        self.writeValueLineEdit = QTangoWriteAttributeLineEdit(self.sizes, self.attrColors)
        #		self.writeValueLineEdit.editingFinished.connect(self.editingFinished)
        self.writeValueLineEdit.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.writeLabel = QTangoStartLabel(self.sizes, self.attrColors)
        self.writeLabel.currentAttrColor = self.attrColors.backgroundColor
        self.writeLabel.setupLayout()

        # 		self.startLabel = QtGui.QLabel('')
        # 		st = ''.join(('QLabel {min-height: ', str(self.sizes.barHeight), 'px; \n',
        # 					'min-width: ', str(int(self.sizes.barHeight / 6)), 'px; \n',
        # 					'max-width: ', str(int(self.sizes.barHeight / 6)), 'px; \n',
        # 					'max-height: ', str(self.sizes.barHeight), 'px; \n',
        # 					'background-color: ', self.attrColors.secondaryColor0, ';}'))
        # 		self.startLabel.setStyleSheet(st)
        # 		self.middleLabel = QtGui.QLabel('')
        # 		st = ''.join(('QLabel {min-height: ', str(self.sizes.barHeight), 'px; \n',
        # 					'min-width: ', str(int(self.sizes.barHeight / 6)), 'px; \n',
        # 					'max-width: ', str(int(self.sizes.barHeight / 6)), 'px; \n',
        # 					'max-height: ', str(self.sizes.barHeight), 'px; \n',
        # 					'background-color: ', self.attrColors.secondaryColor0, ';}'))
        # 		self.middleLabel.setStyleSheet(st)
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
        # 					'min-width: ', str(readWidth), 'px; \n',
        # 					'max-width: ', str(readWidth), 'px; \n',
        # 					'background-color: ', self.attrColors.backgroundColor, '; \n',
        # 					'color: ', self.attrColors.secondaryColor0, ';}'))
        # 		self.nameLabel.setStyleSheet(s)
        #
        # 		font = self.nameLabel.font()
        # 		font.setFamily(self.sizes.fontType)
        # 		font.setStretch(self.sizes.fontStretch)
        # 		font.setWeight(self.sizes.fontWeight)
        # 		font.setPointSize(int(self.sizes.barHeight * 0.7))
        # 		font.setStyleStrategy(QtGui.QFont.PreferAntialias)
        # #		font.setPointSize(int(self.sizes.fontSize))
        # 		self.nameLabel.setFont(font)
        # 		self.nameLabel.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        # 		self.nameLabel.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        #
        # 		self.readValueSpinbox = QtGui.QDoubleSpinBox()
        # 		s = ''.join(('QDoubleSpinBox { \n',
        #             'background-color: ', self.attrColors.backgroundColor, '; \n',
        #             'border-width: 0px; \n',
        #             'border-color: #339; \n',
        #             'border-style: solid; \n',
        #             'border-radius: 0; \n',
        #             'border: 0px; \n',
        #             'padding: 0px; \n',
        #             'margin: 0px; \n',
        #             'qproperty-buttonSymbols: NoButtons; \n',
        #             'min-width: ', str(int(readValueWidth)), 'px; \n',
        # 			'max-width: ', str(int(readValueWidth)), 'px; \n',
        #             'min-height: ', str(self.sizes.barHeight), 'px; \n',
        #             'max-height: ', str(self.sizes.barHeight), 'px; \n',
        #             'qproperty-readOnly: 1; \n',
        #             'color: ', self.attrColors.secondaryColor0, ';} \n'))
        # 		font = self.readValueSpinbox.font()
        # 		font.setFamily(self.sizes.fontType)
        # 		font.setStretch(self.sizes.fontStretch)
        # 		font.setWeight(self.sizes.fontWeight)
        # 		font.setPointSize(int(self.sizes.barHeight * 0.7))
        # 		font.setStyleStrategy(QtGui.QFont.PreferAntialias)
        # 		self.readValueSpinbox.setFont(font)
        # 		self.readValueSpinbox.setStyleSheet(s)
        # 		self.readValueSpinbox.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        # 		self.readValueSpinbox.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        #
        # 		self.writeValueSpinbox = QtGui.QDoubleSpinBox()
        # 		s = ''.join(('QDoubleSpinBox { \n',
        #             'background-color: ', self.attrColors.backgroundColor, '; \n',
        #             'border-width: 0px; \n',
        #             'border-color: #339; \n',
        #             'border-style: solid; \n',
        #             'border-radius: 0; \n',
        #             'border: 0px; \n',
        #             'padding: 0px; \n',
        #             'margin: 0px; \n',
        #             'qproperty-buttonSymbols: NoButtons; \n',
        #             'min-width: ', str(self.sizes.barWidth), 'px; \n',
        #             'min-height: ', str(self.sizes.barHeight), 'px; \n',
        #             'max-height: ', str(self.sizes.barHeight), 'px; \n',
        #             'qproperty-readOnly: 0; \n',
        #             'color: ', self.attrColors.secondaryColor0, ';} \n'))
        # 		font = self.writeValueSpinbox.font()
        # 		font.setFamily(self.sizes.fontType)
        # 		font.setStretch(self.sizes.fontStretch)
        # 		font.setWeight(self.sizes.fontWeight)
        # 		font.setPointSize(int(self.sizes.barHeight * 0.7))
        # 		font.setStyleStrategy(QtGui.QFont.PreferAntialias)
        # 		self.writeValueSpinbox.setFont(font)
        # 		self.writeValueSpinbox.setStyleSheet(s)
        # 		self.writeValueSpinbox.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Minimum)
        # 		self.writeValueSpinbox.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)


        spacerItem = QtGui.QSpacerItem(0, 0, QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Minimum)

        layout = QtGui.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setMargin(int(self.sizes.barHeight / 10))

        layoutGrid = QtGui.QGridLayout()
        layoutGrid.setContentsMargins(0, 0, 0, 0)
        layoutGrid.setMargin(int(self.sizes.barHeight / 10))
        layoutGrid.addWidget(self.nameLabel, 0, 0)
        layoutGrid.addWidget(self.valueSpinbox, 0, 2)
        layoutGrid.addWidget(self.unitLabel, 0, 3)
        layoutGrid.addWidget(self.writeLabel, 1, 1)
        layoutGrid.addWidget(self.writeValueLineEdit, 1, 2)

        #		layout.addSpacerItem(spacerItem)
        layout.addWidget(self.startLabel)
        layout.addLayout(layoutGrid)
        #		layout.addWidget(self.nameLabel)
        # 		layout.addWidget(self.writeValueLineEdit)
        # 		layout.addWidget(self.writeLabel)
        # 		layout.addWidget(self.valueSpinbox)
        layout.addWidget(self.endLabel)

        self.setMaximumWidth(self.sizes.readAttributeWidth)
        self.setMinimumWidth(self.sizes.readAttributeWidth)
        self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)

    def attributeName(self):
        return str(self.nameLabel.text())

    @QtCore.pyqtSignature('setAttributeName(QString)')
    def setAttributeName(self, aName, aUnit=None):
        self.nameLabel.setText(aName)
        if aUnit is not None:
            self.setUnit(aUnit)
        self.update()

    def setUnit(self, unit):
        self.unit = unit
        if self.unit is not None:
            unitStr = self.unit
            if self.prefix is not None:
                unitStr = ''.join((self.prefix, unitStr))
            self.unitLabel.setText(unitStr)

    def setAttributeValue(self, value):
        if type(value) == pt.DeviceAttribute:
            if value.value is not None:
                if self.writeValueInitialized is False:
                    logger.debug('Initializing write value')
                    self.writeValueInitialized = True
                    self.setAttributeWriteValue(value.w_value)

                if value.w_value != self.writeValueLineEdit.value():
                    if self.writeLabel.currentAttrColor != self.attrColors.secondaryColor0:
                        self.writeLabel.currentAttrColor = self.attrColors.secondaryColor0
                        self.writeLabel.setupLayout()
                else:
                    if self.writeLabel.currentAttrColor != self.attrColors.backgroundColor:
                        self.writeLabel.currentAttrColor = self.attrColors.backgroundColor
                        self.writeLabel.setupLayout()
            self.startLabel.setQuality(value.quality)
            self.endLabel.setQuality(value.quality)
            self.unitLabel.setQuality(value.quality)
            self.valueSpinbox.setQuality(value.quality)
            self.nameLabel.setQuality(value.quality)

            val = value.value
        else:
            val = value

        self.valueSpinbox.setValue(val)
        self.update()

    def setAttributeWriteValue(self, value):
        self.writeValueLineEdit.setValue(value)
        self.update()

    def getWriteValue(self):
        return self.writeValueLineEdit.value()


# noinspection PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit
class QTangoWriteAttributeComboBox(QtGui.QWidget):
    def __init__(self, sizes=None, colors=None, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.attrColors = QTangoColors()
        if colors is None:
            self.attrColors = QTangoColors()
        else:
            self.attrColors = colors
        if sizes is None:
            self.sizes = QTangoSizes()
        else:
            self.sizes = sizes

        self.writeValueInitialized = False
        self.unit = None

        self.setupLayout()

    def setupLayout(self):
        readValueWidth = self.sizes.barWidth
        readWidth = self.sizes.readAttributeWidth - int(self.sizes.barHeight / 6) - readValueWidth

        self.startLabel = QTangoStartLabel(self.sizes, self.attrColors)
        self.endLabel = QTangoEndLabel(self.sizes, self.attrColors)
        self.nameLabel = QTangoAttributeNameLabel(self.sizes, self.attrColors)
        self.writeValueComboBox = QTangoComboBoxBase(self.sizes, self.attrColors)

        spacerItem = QtGui.QSpacerItem(0, 0, QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Minimum)

        layout = QtGui.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setMargin(int(self.sizes.barHeight / 10))

        layoutGrid = QtGui.QHBoxLayout()
        layoutGrid.setContentsMargins(0, 0, 0, 0)
        layoutGrid.setMargin(int(self.sizes.barHeight / 10))
        layoutGrid.addWidget(self.nameLabel)
        layoutGrid.addWidget(self.writeValueComboBox)

        #		layout.addSpacerItem(spacerItem)
        layout.addWidget(self.startLabel)
        layout.addLayout(layoutGrid)
        layout.addWidget(self.endLabel)

        self.setMaximumWidth(self.sizes.readAttributeWidth)
        self.setMinimumWidth(self.sizes.readAttributeWidth)
        self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)

        self.writeValueComboBox.activated[str].connect(self.onActivated)

    def attributeName(self):
        return str(self.nameLabel.text())

    @QtCore.pyqtSignature('setAttributeName(QString)')
    def setAttributeName(self, aName, aUnit=None):
        self.nameLabel.setText(aName)
        if aUnit is not None:
            self.unit = aUnit
        self.update()

    def setAttributeValue(self, value):
        if type(value) == pt.DeviceAttribute:
            if value.value is not None:
                if self.writeValueInitialized is False:
                    logger.debug('Initializing write value')
                    self.writeValueInitialized = True
                    self.setAttributeWriteValue(value.w_value)

            self.startLabel.setQuality(value.quality)
            self.endLabel.setQuality(value.quality)
        self.update()

    def setAttributeWriteValue(self, value):
        self.writeValueComboBox.setValue(value)
        self.update()

    def getWriteValue(self):
        return self.writeValueComboBox.value()

    def addItem(self, itemText):
        self.writeValueComboBox.addItem(itemText)

    def setActivatedMethod(self, method):
        self.writeValueComboBox.activated[str].connect(method)

    def onActivated(self, text):
        print text


class QTangoDeviceStatus(QTangoAttributeBase):
    def __init__(self, sizes=None, colors=None, parent=None):
        QTangoAttributeBase.__init__(self, sizes, colors, parent)

        self.startLabel = QTangoStartLabel(self.sizes, self.attrColors)
        self.startLabel.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Expanding)
        self.endLabel = QTangoEndLabel(self.sizes, self.attrColors)
        self.endLabel.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.nameLabel = QTangoAttributeNameLabel(self.sizes, self.attrColors)
        self.nameLabel.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        self.nameLabel.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        self.nameLabel.setText("Status")
        self.stateLabel = QTangoStateLabel(self.sizes, self.attrColors)
        self.stateLabel.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        self.stateLabel.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        self.statusLabel = QTangoAttributeNameLabel(self.sizes, self.attrColors)
        self.statusLabel.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        self.statusLabel.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.statusLabel.setWordWrap(True)

        s = ''.join(('QLabel {min-height: ', str(self.sizes.barHeight), 'px; \n',
                     'background-color: ', self.attrColors.backgroundColor, '; \n',
                     'color: ', self.currentAttrColor, ';}'))
        self.statusLabel.setStyleSheet(s)
        font = self.font()
        font.setPointSize(int(self.sizes.barHeight * 0.3))
        font.setStyleStrategy(QtGui.QFont.PreferAntialias)
        self.statusLabel.setFont(font)

        spacerItem = QtGui.QSpacerItem(0, 0, QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.MinimumExpanding)

        layout = QtGui.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layoutTop = QtGui.QHBoxLayout()
        layoutTop.setContentsMargins(0, 0, 0, 0)
        layout2 = QtGui.QVBoxLayout()
        layout2.setMargin(0)
        layout2.setSpacing(0)
        layout2.setContentsMargins(0, 0, 0, 3)

        layout.addWidget(self.startLabel)
        layout.addLayout(layout2)
        layout2.addLayout(layoutTop)
        layoutTop.addWidget(self.nameLabel)
        layoutTop.addWidget(self.stateLabel)
        layout2.addSpacerItem(spacerItem)
        layout2.addWidget(self.statusLabel)
        layout.addWidget(self.endLabel)

        self.setMaximumWidth(self.sizes.readAttributeWidth)
        self.setMinimumWidth(self.sizes.readAttributeWidth)
        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)

    def statusText(self):
        return str(self.statusLabel.text())

    @QtCore.pyqtSignature('setAttributeName(QString)')
    def setStatusText(self, aName):
        self.statusLabel.setText(aName)
        self.update()

    def setState(self, state):
        self.endLabel.setState(state)
        self.startLabel.setState(state)
        self.nameLabel.setState(state)
        self.stateLabel.setState(state)
        self.statusLabel.setState(state)

    def setStatus(self, state, status):
        self.setState(state)
        self.statusLabel.setText(status)
        self.update()


# noinspection PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit
class QTangoDeviceNameStatus(QTangoAttributeBase):
    def __init__(self, sizes=None, colors=None, parent=None):
        QTangoAttributeBase.__init__(self, sizes, colors, parent)
        self.setupLayout()

    def setupLayout(self):
        readValueWidth = self.sizes.barWidth
        readWidth = self.sizes.readAttributeWidth - self.sizes.barHeight / 6 - self.sizes.barHeight / 2

        self.startLabel = QTangoStartLabel(self.sizes, self.attrColors)
        self.startLabel.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        self.endLabel = QTangoEndLabel(self.sizes, self.attrColors)
        self.endLabel.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        self.nameLabel = QTangoAttributeNameLabel(self.sizes, self.attrColors)
        self.nameLabel.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        self.nameLabel.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)

        layout = QtGui.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
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
