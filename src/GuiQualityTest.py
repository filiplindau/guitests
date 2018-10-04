"""
Created on 04 Oct 2018

@author: Filip Lindau
"""

# -*- coding:utf-8 -*-
from PyQt4 import QtGui, QtCore

import time
import sys
import logging

logger = logging.getLogger("GuiTest")
logger.setLevel(logging.DEBUG)
# while len(logger.handlers):
#     logger.removeHandler(logger.handlers[0])
f = logging.Formatter("%(asctime)s - %(name)s.   %(funcName)s - %(levelname)s - %(message)s")
fh = logging.StreamHandler()
fh.setFormatter(f)
logger.addHandler(fh)


# noinspection PyAttributeOutsideInit
class TangoDeviceClient(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        #        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

        self.setupLayout()

        splash.showMessage('         Initializing devices', alignment=QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
        app.processEvents()

        t0 = time.clock()
        self.devices = dict()
        self.devices['test'] = pt.DeviceProxy('sys/tg_test/1')

        splash.showMessage('         Reading startup attributes',
                           alignment=QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
        app.processEvents()

        self.guiLock = threading.Lock()
        self.attributes = dict()
        self.attributes['double_scalar'] = AttributeClass('double_scalar', self.devices['test'], 0.3)
        self.attributes['no_value'] = AttributeClass('no_value', self.devices['test'], 0.3)
        self.attributes['double_spectrum'] = AttributeClass('double_spectrum_ro', self.devices['test'], 0.3)

        self.attributes['double_scalar'].attrSignal.connect(self.read_double_scalar)
        self.attributes['no_value'].attrSignal.connect(self.read_no_value)
        self.attributes['double_spectrum'].attrSignal.connect(self.read_spectrum)

    def read_double_scalar(self, data):
        self.double_widget.setAttributeValue(data)

    def read_no_value(self, data):
        logger.info("NO VALUE data: {0}".format(data))
        self.no_value_widget.setAttributeValue(data)

    def read_spectrum(self, data):
        try:
            xdata = np.arange(len(data.value))
        except TypeError:
            xdata = 0
        self.spectrum_widget.setSpectrum(xdata, data)

    def closeEvent(self, event):
        for a in self.attributes.itervalues():
            print 'Stopping', a.name
            a.stop_read()
        for a in self.attributes.itervalues():
            a.readThread.join()
        event.accept()

    def setupLayout(self):
        s = 'QWidget{background-color: #000000; }'
        self.setStyleSheet(s)

        self.title_sizes = qw.QTangoSizes()
        self.title_sizes.barHeight = 40
        self.title_sizes.barWidth = 18
        self.title_sizes.readAttributeWidth = 300
        self.title_sizes.writeAttributeWidth = 150
        self.title_sizes.fontStretch = 80
        self.title_sizes.fontType = 'Arial'

        self.frame_sizes = qw.QTangoSizes()
        self.frame_sizes.barHeight = 40
        self.frame_sizes.barWidth = 35
        self.frame_sizes.readAttributeWidth = 300
        self.frame_sizes.writeAttributeWidth = 150
        self.frame_sizes.fontStretch = 80
        self.frame_sizes.fontType = 'Arial'
        #        self.frame_sizes.fontType = 'Trebuchet MS'

        self.attr_sizes = qw.QTangoSizes()
        self.attr_sizes.barHeight = 30
        self.attr_sizes.barWidth = 35
        self.attr_sizes.readAttributeWidth = 300
        self.attr_sizes.readAttributeHeight = 250
        self.attr_sizes.writeAttributeWidth = 299
        self.attr_sizes.fontStretch = 80
        self.attr_sizes.fontType = 'Arial'
        #        self.attr_sizes.fontType = 'Trebuchet MS'

        self.colors = qw.QTangoColors()

        #######################
        # Title widgets
        #
        self.title = qw.QTangoTitleBar('Test quality', self.title_sizes)
        self.setWindowTitle('Test quality')
        self.sidebar = qw.QTangoSideBar(colors=self.colors, sizes=self.frame_sizes)
        self.bottombar = qw.QTangoHorizontalBar()

        #######################
        # Test widgets
        #
        self.attr_sizes.readAttributeHeight = 300

        self.double_widget = qw.QTangoReadAttributeSliderV(colors=self.colors, sizes=self.attr_sizes)
        self.double_widget.setAttributeName('Double scalar', 'a.u.')
        self.double_widget.setSliderLimits(0, 100)
        self.double_widget.setAttributeWarningLimits([10, 90])

        self.no_value_widget = qw.QTangoReadAttributeSliderV(colors=self.colors, sizes=self.attr_sizes)
        self.no_value_widget.setAttributeName('No value', 'a.u.')
        self.no_value_widget.setSliderLimits(0, 100)
        self.no_value_widget.setAttributeWarningLimits([10, 90])

        self.spectrum_widget = qw.QTangoReadAttributeSpectrum(colors=self.colors, sizes=self.attr_sizes)
        self.spectrum_widget.setAttributeName('Spectrum')
        # self.spectrum_widget.setXRange(700, 900)
        self.spectrum_widget.setMinimumWidth(600)
        self.spectrum_widget.setMaximumWidth(600)
        self.spectrum_widget.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)



        ############################
        # Setting up layout
        #
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

        layoutData = QtGui.QVBoxLayout()
        layoutData.setMargin(self.attr_sizes.barHeight / 2)
        layoutData.setSpacing(self.attr_sizes.barHeight * 2)

        self.layoutAttributesTest = QtGui.QHBoxLayout()
        self.layoutAttributesTest.setMargin(0)
        self.layoutAttributesTest.setSpacing(self.attr_sizes.barHeight / 2)
        self.layoutAttributesTest.setContentsMargins(0, 0, 0, 0)
        self.layoutAttributesTest.addWidget(self.double_widget)
        self.layoutAttributesTest.addWidget(self.no_value_widget)
        self.layoutAttributesTest.addWidget(self.spectrum_widget)
        self.layoutAttributesTest.addSpacerItem(QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Expanding,
                                                                  QtGui.QSizePolicy.Minimum))

        layout2.addWidget(self.title)
        layout2.addSpacerItem(QtGui.QSpacerItem(20, 60, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum))
        layout2.addLayout(layoutData)
        layoutData.addLayout(self.layoutAttributesTest)
        layoutData.addSpacerItem(QtGui.QSpacerItem(20, 20, QtGui.QSizePolicy.Minimum,
                                                                    QtGui.QSizePolicy.Expanding))

        layout1.addLayout(layout2)
        layout0.addLayout(layout1)
        layout0.addWidget(self.bottombar)

        self.resize(500,800)
        self.setGeometry(200, 100, 800, 600)
#        self.showFullScreen()

        self.update()


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    splash_pix = QtGui.QPixmap('splash_tangoloading.png')
    splash = QtGui.QSplashScreen(splash_pix, QtCore.Qt.WindowStaysOnTopHint)
    splash.setMask(splash_pix.mask())
    splash.show()
    splash.showMessage('         Importing modules', alignment=QtCore.Qt.AlignBottom | QtCore.Qt.AlignLeft,
                       color=QtGui.QColor('#66cbff'))
    app.processEvents()

    import QTangoWidgets.QTangoWidgets as qw
    from QTangoWidgets.AttributeReadThreadClass import AttributeClass
    import pyqtgraph as pg
    import PyTango as pt
    import threading
    import numpy as np

    splash.showMessage('         Starting GUI', alignment=QtCore.Qt.AlignBottom | QtCore.Qt.AlignLeft,
                       color=QtGui.QColor('#66cbff'))
    app.processEvents()
    myapp = TangoDeviceClient()
    myapp.show()
    splash.finish(myapp)
    sys.exit(app.exec_())
