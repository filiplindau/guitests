'''
Created on 23 okt 2014

@author: Filip Lindau
'''
# -*- coding:utf-8 -*-
from PyQt4 import QtGui, QtCore

import time
import sys




class TangoDeviceClient(QtGui.QWidget):
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self,parent)
#        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.timeVector = None
        self.xData = None
        self.xDataTemp = None

        self.setupLayout()

        splash.showMessage('         Initializing devices', alignment = QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
        app.processEvents()

        t0=time.clock()
        self.devices = {}
        self.devices['waveplate']=pt.DeviceProxy('gunlaser/mp/waveplate')
        self.devices['redpitaya2']=pt.DeviceProxy('gunlaser/devices/redpitaya2')
        print time.clock()-t0, ' s'

        splash.showMessage('         Reading startup attributes', alignment = QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
        app.processEvents()


        self.guiLock = threading.Lock()
        self.attributes = {}
        self.attributes['position'] = AttributeClass('position', self.devices['waveplate'], 0.3)
        self.attributes['waveplateState'] = AttributeClass('state', self.devices['waveplate'], 0.3)
        self.attributes['energyir'] = AttributeClass('measurementdata2', self.devices['redpitaya2'], 0.3)

        self.devices['redpitaya2'].write_attribute('measurementstring2', '5.22e-3*(w2[40:90]-w2[500:600].mean()).sum()')

        self.attributes['position'].attrSignal.connect(self.readPosition)
        self.attributes['waveplateState'].attrSignal.connect(self.readWaveplateState)
        self.attributes['energyir'].attrSignal.connect(self.readEnergyIR)



        splash.showMessage('         Setting up variables', alignment = QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
        app.processEvents()

        self.positionOffset = 0.0

#         self.timer = QtCore.QTimer(self)
#         self.timer.timeout.connect(self.checkDevices)
#         self.timer.start(100)



    def checkDevices(self):
        for a in self.attributes.itervalues():
            pass
#            a.attr_read()

    def readPosition(self, data):
        self.positionWidget.setAttributeValue(data)

        data.value = 100*np.cos(2*data.value*np.pi/180.0)**3
        data.w_value = 100*np.cos(2*data.w_value*np.pi/180.0)**3
        self.energyWidget.setAttributeValue(data)

    def writePosition(self):
        print "in writePosition::"
        self.guiLock.acquire()
        energy = self.energyWidget.getWriteValue()
        print "energy: ", energy
        if energy > 100:
            energy = 100
        elif energy < 0:
            energy = 0
        w = np.arccos((energy/100.0)**0.33)*90/np.pi
        self.attributes['position'].attr_write(w)
        self.guiLock.release()

    def readWaveplateState(self, data):
        self.waveplateName.setState(data)
        data.value = ''
        self.waveplateWidget.setStatus(data)

    def readEnergyIR(self, data):
        data.value = 1000 * data.value
        self.energyIRWidget.setAttributeValue(data)


    def initWaveplate(self):
        self.devices['waveplate'].command_inout('init')

    def stopWaveplate(self):
        self.devices['waveplate'].command_inout('stop')

    def setMaxWaveplate(self):
        self.devices['waveplate'].command_inout('defineposition', 0)


    def setupAttributeLayout(self, attributeList = []):
        self.attributeQObjects = []
        for att in attributeList:
            attQObject = qw.QTangoReadAttributeDouble()
            attQObject.setAttributeName(att.name)
            self.attributeQObjects.append(attQObject)
            self.layoutAttributes.addWidget(attQObject)

    def closeEvent(self, event):
#         for device in self.devices.itervalues():
#             device.terminate()
        for a in self.attributes.itervalues():
            print 'Stopping', a.name
            a.stopRead()
        for a in self.attributes.itervalues():
            a.readThread.join()
        event.accept()

    def setupLayout(self):
        s='QWidget{background-color: #000000; }'
        self.setStyleSheet(s)

        self.frameSizes = qw.QTangoSizes()
        self.frameSizes.barHeight = 20
        self.frameSizes.barWidth = 18
        self.frameSizes.readAttributeWidth = 250
        self.frameSizes.writeAttributeWidth = 150
        self.frameSizes.fontStretch= 80
        self.frameSizes.fontType = 'Segoe UI'
#        self.frameSizes.fontType = 'Trebuchet MS'

        self.attrSizes = qw.QTangoSizes()
        self.attrSizes.barHeight = 22
        self.attrSizes.barWidth = 18
        self.attrSizes.readAttributeWidth = 250
        self.attrSizes.readAttributeHeight = 250
        self.attrSizes.writeAttributeWidth = 299
        self.attrSizes.fontStretch= 80
        self.attrSizes.fontType = 'Segoe UI'
#        self.attrSizes.fontType = 'Trebuchet MS'


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
        spacerItemV = QtGui.QSpacerItem(20, 5, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.MinimumExpanding)
        spacerItemBar = QtGui.QSpacerItem(self.frameSizes.barWidth, self.frameSizes.barHeight+8, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        spacerItemH = QtGui.QSpacerItem(20, 5, QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Minimum)

        layoutData = QtGui.QHBoxLayout()
        layoutData.setMargin(self.attrSizes.barHeight/2)
        layoutData.setSpacing(self.attrSizes.barHeight*2)
        self.layoutAttributes = QtGui.QVBoxLayout()
        self.layoutAttributes.setMargin(0)
        self.layoutAttributes.setSpacing(self.attrSizes.barHeight/2)
        self.layoutAttributes.setContentsMargins(0, 0, 0, 0)

#         self.layoutAttributes2 = QtGui.QVBoxLayout()
#         self.layoutAttributes2.setMargin(0)
#         self.layoutAttributes2.setSpacing(self.attrSizes.barHeight/2)
#         self.layoutAttributes2.setContentsMargins(0, 0, 0, 0)
#
#         self.layoutAttributes3 = QtGui.QVBoxLayout()
#         self.layoutAttributes3.setMargin(0)
#         self.layoutAttributes3.setSpacing(self.attrSizes.barHeight/2)
#         self.layoutAttributes3.setContentsMargins(0, 0, 0, 0)

        self.title = qw.QTangoTitleBar('Energy control')
        self.setWindowTitle('Energy control')
        self.sidebar = qw.QTangoSideBar(colors = self.colors, sizes = self.frameSizes)
        self.bottombar = qw.QTangoHorizontalBar()

        self.waveplateName = qw.QTangoDeviceNameStatus(colors = self.colors, sizes = self.frameSizes)
        self.waveplateName.setAttributeName('Waveplate')

        self.waveplateWidget = qw.QTangoCommandSelection('Waveplate', colors = self.colors, sizes = self.attrSizes)
        self.waveplateWidget.addCmdButton('Stop', self.stopWaveplate)
        self.waveplateWidget.addCmdButton('Set Max', self.setMaxWaveplate)


        self.attrSizes.readAttributeHeight = 250
        self.positionWidget = qw.QTangoReadAttributeSliderV(colors = self.colors, sizes = self.attrSizes)
        self.positionWidget.setAttributeName('Pos', 'deg')
        self.positionWidget.setAttributeWarningLimits([-10, 370])
        self.positionWidget.setSliderLimits(0, 50)

        self.energyWidget = qw.QTangoWriteAttributeSliderV(colors = self.colors, sizes = self.attrSizes)
        self.energyWidget.setAttributeName('Energy UV', '%')
        self.energyWidget.setSliderLimits(0, 100)
        self.energyWidget.setAttributeWarningLimits([-1, 110])
        self.energyWidget.writeValueLineEdit.editingFinished.connect(self.writePosition)

        self.energyIRWidget = qw.QTangoReadAttributeSliderV(colors = self.colors, sizes = self.attrSizes)
        self.energyIRWidget.setAttributeName('Energy IR', 'mJ')
        self.energyIRWidget.setAttributeWarningLimits([0, 15])
        self.energyIRWidget.setSliderLimits(0, 10)

        self.energyUVWidget = qw.QTangoReadAttributeSliderV(colors = self.colors, sizes = self.attrSizes)
        self.energyUVWidget.setAttributeName('Energy UV', 'uJ')
        self.energyUVWidget.setAttributeWarningLimits([0, 500])
        self.energyUVWidget.setSliderLimits(0, 200)


        layout2.addWidget(self.title)
        layout2.addLayout(layoutData)
        layoutData.addLayout(self.layoutAttributes)
#        layoutData.addSpacerItem(spacerItemH)
#        layoutData.addLayout(self.layoutAttributes2)
#        layoutData.addLayout(self.layoutAttributes3)

        self.layoutAttributes.addWidget(self.waveplateName)
        self.layoutAttributes.addWidget(self.waveplateWidget)
        self.layoutAttributes.addSpacerItem(spacerItemV)

        layoutSliders = QtGui.QHBoxLayout()
        layoutSliders.addWidget(self.energyWidget)
        layoutSliders.addWidget(self.positionWidget)
        layoutSliders.addWidget(self.energyIRWidget)
        layoutSliders.addWidget(self.energyUVWidget)
        self.layoutAttributes.addLayout(layoutSliders)
#        self.layoutAttributes2.addSpacerItem(spacerItemV)



        layout1.addWidget(self.sidebar)
        layout1.addLayout(layout2)
        layout0.addLayout(layout1)
#        layout0.addWidget(self.bottombar)

#        self.resize(500,800)
        self.setGeometry(200,100,300,500)

        self.update()

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    splash_pix = QtGui.QPixmap('splash_tangoloading.png')
    splash = QtGui.QSplashScreen(splash_pix, QtCore.Qt.WindowStaysOnTopHint)
    splash.setMask(splash_pix.mask())
    splash.show()
    splash.showMessage('         Importing modules', alignment = QtCore.Qt.AlignBottom | QtCore.Qt.AlignLeft, color = QtGui.QColor('#66cbff'))
    app.processEvents()

    import QTangoWidgets.QTangoWidgets as qw
    from QTangoWidgets.AttributeReadThreadClass import AttributeClass
    import pyqtgraph as pg
    import PyTango as pt
    import threading
    import numpy as np

    splash.showMessage('         Starting GUI', alignment = QtCore.Qt.AlignBottom | QtCore.Qt.AlignLeft, color = QtGui.QColor('#66cbff'))
    app.processEvents()
    myapp = TangoDeviceClient()
    myapp.show()
    splash.finish(myapp)
    sys.exit(app.exec_())