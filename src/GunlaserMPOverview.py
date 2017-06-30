'''
Created on 12 aug 2014

@author: Filip
'''
# -*- coding:utf-8 -*-

from PyQt4 import QtGui, QtCore

import time
import sys


# noinspection PyAttributeOutsideInit
class AttributeClass(QtCore.QObject):
    import PyTango as pt
    attrSignal = QtCore.pyqtSignal(pt.device_attribute.DeviceAttribute)
    attrInfoSignal = QtCore.pyqtSignal(pt.AttributeInfoEx)
    def __init__(self, name, device, interval, getInfo = False):
        super(AttributeClass, self).__init__()
        self.name = name
        self.device = device
        self.interval = interval
        self.getInfoFlag = getInfo

        self.lastRead = time.time()
        self.attr = None
        self.readThread = threading.Thread(name = self.name, target = self.attr_read)
        self.stopThread = False

        self.startRead()

    def attr_read(self):
        replyReady = True
        while self.stopThread == False:
            if self.getInfoFlag ==True:
                self.getInfoFlag = False
                try:
                    self.attrInfo = self.device.get_attribute_config(self.name)
                    self.attrInfoSignal.emit(self.attrInfo)

                except pt.DevFailed, e:
                    if e[0].reason == 'API_DeviceTimeOut':
                        print 'AttrInfo Timeout'
                    else:
                        print self.name, '  attrinfo error ', e[0].reason
                    self.attrInfo = pt.AttributeInfoEx()
                    self.attrInfoSignal.emit(self.attrInfo)
                except Exception, e:
                    print self.name, ' recovering from attrInfo ', str(e)
                    self.attrInfo = pt.AttributeInfoEx()
                    self.attrInfoSignal.emit(self.attrInfo)

            t = time.time()

            if t-self.lastRead > self.interval:
                self.lastRead = t
                try:
                    id = self.device.read_attribute_asynch(self.name)

                    replyReady = False
                except pt.DevFailed, e:
                    if e[0].reason == 'API_DeviceTimeOut':
                        print 'Timeout'
                    else:
                        print self.name, ' error ', e[0].reason
                    self.attr = pt.DeviceAttribute()
                    self.attr.quality = pt.AttrQuality.ATTR_INVALID
                    self.attr.value = None
                    self.attr.w_value = None
                    self.attrSignal.emit(self.attr)
                except Exception, e:
                    print self.name, ' recovering from ', str(e)
                    self.attr = pt.DeviceAttribute()
                    self.attr.quality = pt.AttrQuality.ATTR_INVALID
                    self.attr.value = None
                    self.attrSignal.emit(self.attr)

                while replyReady == False and self.stopThread == False:
                    try:
                        self.attr = self.device.read_attribute_reply(id)
                        replyReady = True
                        self.attrSignal.emit(self.attr)
                        # Read only once if interval = None:
                        if self.interval == None:
                            self.stopThread = True
                            self.interval = 0.0
                    except Exception, e:
                        if e[0].reason == 'API_AsynReplyNotArrived':
#                            print self.name, ' not replied'
                            time.sleep(0.1)
                        else:
                            replyReady = True
                            print 'Error reply ', self.name, str(e)
                            self.attr = pt.DeviceAttribute()
                            self.attr.quality = pt.AttrQuality.ATTR_INVALID
                            self.attr.value = None
                            self.attr.w_value = None
                            self.attrSignal.emit(self.attr)

            if self.interval != None:
                time.sleep(self.interval)
            else:
                time.sleep(1)
        print self.name, ' stopped'

    def attr_write(self, wvalue):
        self.device.write_attribute(self.name, wvalue)

    def stopRead(self):
        self.stopThread = True

    def startRead(self):
        self.stopRead()
        self.stopThread = False
        self.readThread.start()

    def getInfo(self):
        self.getInfoFlag = True


# noinspection PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit
class TangoDeviceClient(QtGui.QWidget):
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self,parent)
#        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.timeVector = None
        self.xData = None
        self.xDataTemp = None

        self.setupLayout()

        splash.showMessage('       Initializing devices', alignment = QtCore.Qt.AlignBottom | QtCore.Qt.AlignLeft, color = QtGui.QColor('#66cbff'))
        app.processEvents()

        t0=time.clock()
        self.devices = {}
        self.devices['leelaser']=pt.DeviceProxy('gunlaser/mp/leelaser')
        self.devices['ionpump']=pt.DeviceProxy('gunlaser/mp/ionpump')
        self.devices['temperature']=pt.DeviceProxy('gunlaser/mp/temperature')
        self.devices['spectrometer']=pt.DeviceProxy('gunlaser/mp/spectrometer')
        print time.clock()-t0, ' s'

        splash.showMessage('       Reading startup attributes... LeeLaser', alignment = QtCore.Qt.AlignBottom | QtCore.Qt.AlignLeft, color = QtGui.QColor('#66cbff'))
        app.processEvents()



        self.guiLock = threading.Lock()
        self.attributes = {}
# LeeLaser
        self.attributes['leelasercurrent'] = AttributeClass('current', self.devices['leelaser'], 0.3)
        self.attributes['leelaserpercentcurrent'] = AttributeClass('percentcurrent', self.devices['leelaser'], 0.3)
        self.attributes['leelaserstatus'] = AttributeClass('status', self.devices['leelaser'], 0.3)
        self.attributes['leelaserstate'] = AttributeClass('state', self.devices['leelaser'], 0.3)
        self.attributes['leelasershutterstate'] = AttributeClass('shutterstate', self.devices['leelaser'], 0.3)

        self.attributes['leelasercurrent'].attrSignal.connect(self.readLeeLaserCurrent)
        self.attributes['leelaserpercentcurrent'].attrSignal.connect(self.readLeeLaserPercentCurrent)
        self.attributes['leelasershutterstate'].attrSignal.connect(self.readLeeLaserShutterState)
        self.attributes['leelaserstate'].attrSignal.connect(self.readLeeLaserState)

        splash.showMessage('       Reading startup attributes... KMPC', alignment = QtCore.Qt.AlignBottom | QtCore.Qt.AlignLeft, color = QtGui.QColor('#66cbff'))
        app.processEvents()


# Ionpump
        self.attributes['ionpumppressure'] = AttributeClass('pressure', self.devices['ionpump'], 0.3)

        self.attributes['ionpumppressure'].attrSignal.connect(self.readIonpumpPressure)

# Temperature
        self.attributes['crystaltemperature'] = AttributeClass('temperature', self.devices['temperature'], 0.3)

        self.attributes['crystaltemperature'].attrSignal.connect(self.readCrystalTemperature)

# Spectrometer
        self.attributes['wavelengths'] = AttributeClass('wavelengths', self.devices['spectrometer'], None)
        self.attributes['peakenergy'] = AttributeClass('peakenergy', self.devices['spectrometer'], 0.3)
        self.attributes['peakwidth'] = AttributeClass('spectrumwidth', self.devices['spectrometer'], 0.3)
        self.attributes['spectrum'] = AttributeClass('spectrum', self.devices['spectrometer'], 0.3)

        self.attributes['peakenergy'].attrSignal.connect(self.readPeakEnergy)
        self.attributes['peakwidth'].attrSignal.connect(self.readPeakWidth)
        self.attributes['spectrum'].attrSignal.connect(self.readSpectrum)
        self.attributes['wavelengths'].attrSignal.connect(self.readWavelengths)



        splash.showMessage('       Setting up variables', alignment = QtCore.Qt.AlignBottom | QtCore.Qt.AlignLeft, color = QtGui.QColor('#66cbff'))
        app.processEvents()

#         self.timer = QtCore.QTimer(self)
#         self.timer.timeout.connect(self.checkDevices)
#         self.timer.start(100)



    def checkDevices(self):
        for a in self.attributes.itervalues():
            pass
#            a.attr_read()

    def readLeeLaserCurrent(self, data):
        self.leeLaserCurrentWidget.setAttributeValue(data)

    def readLeeLaserPercentCurrent(self, data):
        self.leeLaserPercentCurrentWidget.setAttributeValue(data)

    def readLeeLaserState(self, data):
        self.leeLaserName.setState(data)

    def readLeeLaserShutterState(self, data):
        self.leeLaserShutterWidget.setStatus(data)

    def readKmpcVoltage(self, data):
        self.kmpcVoltageWidget.setAttributeValue(data)

    def configureKmpcVoltage(self, attrInfo):
#        self.kmpcVoltageWidget.configureAttribute(attrInfo)
        pass

    def readIonpumpPressure(self, data):
        self.ionpumpPressureWidget.setAttributeValue(data)

    def readCrystalTemperature(self, data):
        self.temperatureWidget.setAttributeValue(data)

    def readPeakEnergy(self, data):
        self.peakEnergyWidget.setAttributeValue(data)

    def readPeakWidth(self, data):
        self.peakWidthWidget.setAttributeValue(data)

    def readWavelengths(self, data):
        try:
            print 'time vector read: ', data.value.shape[0]
        except:
            pass
        self.timeVector = data.value

    def readSpectrum(self, data):
        if self.timeVector == None:
            print 'No time vector'
        else:
            self.oscSpectrumPlot.setSpectrum(xData = self.timeVector, yData = data)
            self.oscSpectrumPlot.update()


    def setupAttributeLayout(self, attributeList = []):
        self.attributeQObjects = []
        for att in attributeList:
            attQObject = qw.QTangoReadAttributeDouble()
            attQObject.setAttributeName(att.name)
            self.attributeQObjects.append(attQObject)
            self.layout_attributes.addWidget(attQObject)

    def closeEvent(self, event):
#         for device in self.devices.itervalues():
#             device.terminate()
        for a in self.attributes.itervalues():
            print 'Stopping', a.name
            a.stop_read()
            a.readThread.join()
        print 'All stopped.'
        print 'Sending close event'
        super(TangoDeviceClient, self).closeEvent(event)
        print 'Exiting'
#        event.accept()

    def setupLayout(self):
        s='QWidget{background-color: #000000; }'
        self.setStyleSheet(s)

        self.frame_sizes = qw.QTangoSizes()
        self.frame_sizes.readAttributeWidth = 300
        self.frame_sizes.writeAttributeWidth = 150
        self.frame_sizes.barHeight = 30
        self.frame_sizes.barWidth = 20
        self.frame_sizes.fontStretch= 80
        self.frame_sizes.fontType = 'Segoe UI'
#        self.frame_sizes.fontType = 'Trebuchet MS'
        self.attr_sizes = qw.QTangoSizes()
        self.attr_sizes.barHeight = 20
        self.attr_sizes.barWidth = 20
        self.attr_sizes.readAttributeWidth = 300
        self.attr_sizes.writeAttributeWidth = 299
        self.attr_sizes.fontStretch= 80
        self.attr_sizes.fontType = 'Segoe UI'
#        self.attr_sizes.fontType = 'Trebuchet MS'


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
        layoutData.setMargin(self.attr_sizes.barHeight/2)
        layoutData.setSpacing(self.attr_sizes.barHeight/2)
        self.layout_attributes = QtGui.QVBoxLayout()
        self.layout_attributes.setMargin(0)
        self.layout_attributes.setSpacing(self.attr_sizes.barHeight/2)
        self.layout_attributes.setContentsMargins(0, 0, 0, 0)

        self.title = qw.QTangoTitleBar('Multipass')
        self.setWindowTitle('Multipass')
        self.title.startLabel.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
#        self.sidebar = qw.QTangoSideBar(colors = self.colors, sizes = self.frame_sizes)
        self.bottombar = qw.QTangoHorizontalBar()

        self.leeLaserName = qw.QTangoDeviceNameStatus(colors = self.colors, sizes = self.frame_sizes)
        self.leeLaserName.setAttributeName('LeeLaser')

        self.leeLaserShutterWidget = qw.QTangoCommandSelection('Shutter', colors = self.colors, sizes = self.attr_sizes)

        self.leeLaserCurrentWidget = qw.QTangoReadAttributeSlider2(colors = self.colors, sizes = self.attr_sizes)
        self.leeLaserCurrentWidget.setAttributeName('LeeLaser current', 'A')
        self.leeLaserCurrentWidget.setAttributeWarningLimits([25, 27])
        self.leeLaserCurrentWidget.setSliderLimits(6, 30)

        self.leeLaserPercentCurrentWidget = qw.QTangoReadAttributeSlider2(colors = self.colors, sizes = self.attr_sizes)
        self.leeLaserPercentCurrentWidget.setAttributeName('LeeLaser percent current', '%')
        self.leeLaserPercentCurrentWidget.setAttributeWarningLimits([70, 73])
        self.leeLaserPercentCurrentWidget.setSliderLimits(30, 100)

        self.ionpumpPressureWidget = qw.QTangoReadAttributeSlider2(colors = self.colors, sizes = self.attr_sizes)
        self.ionpumpPressureWidget.setAttributeName('Crystal pressure', 'mBar')
        self.ionpumpPressureWidget.setAttributeWarningLimits([0, 5e-7])
        self.ionpumpPressureWidget.setSliderLimits(0, 1e-7)

        self.temperatureWidget = qw.QTangoReadAttributeSlider2(colors = self.colors, sizes = self.attr_sizes)
        self.temperatureWidget.setAttributeName('Crystal temp', 'degC')
        self.temperatureWidget.setAttributeWarningLimits([-280, -170])
        self.temperatureWidget.setSliderLimits(-270, 30)

        self.peakWidthWidget = qw.QTangoReadAttributeSlider2(colors = self.colors, sizes = self.attr_sizes)
        self.peakWidthWidget.setAttributeName('Spectral width', 'nm')
        self.peakWidthWidget.setAttributeWarningLimits([30, 100])
        self.peakWidthWidget.setSliderLimits(0, 70)
        self.peakEnergyWidget = qw.QTangoReadAttributeSlider2(colors = self.colors, sizes = self.attr_sizes)
        self.peakEnergyWidget.setAttributeName('Laser energy', 'a.u.')
        self.peakEnergyWidget.setAttributeWarningLimits([10, 30])
        self.peakEnergyWidget.setSliderLimits(0, 20)

        self.oscSpectrumPlot = qw.QTangoReadAttributeSpectrum(colors = self.colors, sizes = self.attr_sizes)
        self.oscSpectrumPlot.setAttributeName('Compressed spectrum')
        self.oscSpectrumPlot.setXRange(700, 900)
        self.oscSpectrumPlot.fixedSize(True)


        layout2.addWidget(self.title)
        layout2.addLayout(layoutData)
        layoutData.addLayout(self.layout_attributes)
        layoutData.addSpacerItem(spacerItemH)

        self.layout_attributes.addWidget(self.leeLaserName)
#        self.layout_attributes.addWidget(self.spectrometerName)
        self.layout_attributes.addSpacerItem(spacerItemV)
        self.layout_attributes.addWidget(self.leeLaserShutterWidget)
        self.layout_attributes.addWidget(self.leeLaserCurrentWidget)
        self.layout_attributes.addWidget(self.leeLaserPercentCurrentWidget)

        self.layout_attributes.addSpacerItem(spacerItemV)
        self.layout_attributes.addWidget(self.ionpumpPressureWidget)
        self.layout_attributes.addWidget(self.temperatureWidget)

        self.layout_attributes.addSpacerItem(spacerItemV)
        self.layout_attributes.addWidget(self.peakWidthWidget)
        self.layout_attributes.addWidget(self.peakEnergyWidget)
        self.layout_attributes.addWidget(self.oscSpectrumPlot)


#        layout1.addWidget(self.sidebar)
#        layout1.addLayout(layout2)
        layout0.addLayout(layout2)
        layout0.addWidget(self.bottombar)

#        self.resize(500,800)
        self.setGeometry(200,100,300,800)

        self.update()


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    splash_pix = QtGui.QPixmap('splash_tangoloading.png')
    splash = QtGui.QSplashScreen(splash_pix, QtCore.Qt.WindowStaysOnTopHint)
    splash.setMask(splash_pix.mask())
    splash.show()
    splash.showMessage('       Importing modules', alignment = QtCore.Qt.AlignBottom | QtCore.Qt.AlignLeft, color = QtGui.QColor('#66cbff'))
    app.processEvents()

    import QTangoWidgets.QTangoWidgets as qw
    import pyqtgraph as pg
    import PyTango as pt
    import threading
    import numpy as np

    splash.showMessage('       Starting GUI', alignment = QtCore.Qt.AlignBottom | QtCore.Qt.AlignLeft, color = QtGui.QColor('#66cbff'))
    app.processEvents()
    myapp = TangoDeviceClient()
    myapp.show()
    splash.finish(myapp)
    sys.exit(app.exec_())