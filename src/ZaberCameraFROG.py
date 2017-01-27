'''
Created on 22 feb 2016

@author: laser
'''

# -*- coding:utf-8 -*-
"""
Created on Feb 1, 2016

@author: m
"""

from PyQt4 import QtGui, QtCore

import time
import sys
sys.path.insert(0, '../../guitests/src/QTangoWidgets')

import pyqtgraph as pq
import PyTango as pt
import threading
import numpy as np
# import QTangoWidgets as qw
from AttributeReadThreadClass import AttributeClass


motorName = 'gunlaser/motors/zaber01'
cameraName = pt.DeviceProxy('gunlaser/cameras/cam0')

class TangoDeviceClient(QtGui.QWidget):
    def __init__(self, cameraName, motorName, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.settings = QtCore.QSettings('Maxlab', 'RedpitayaTangoAutocorrelation')

#        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.timeVector = None
        self.xData = None
        self.xDataTemp = None

        self.cameraName = cameraName
        self.motorName = motorName


        self.title = 'FROG'


        t0 = time.clock()
        print time.clock() - t0, ' s'

        self.guiLock = threading.Lock()
        self.positionOffset = 0.0


        print 'Getting motor device...'
        self.motorDev = pt.DeviceProxy(motorName)
        print '...connected'

        print 'Getting camera device...'
        self.cameraDev = pt.DeviceProxy(self.cameraName)
        print '...connected'



        #=======================================================================
        # self.devices = {}
        # self.devices['redpitaya'] = pt.DeviceProxy(self.redpitayaName)
        # self.devices['motor'] = pt.DeviceProxy(self.motorName)
        # self.devices['spectrometer'] = pt.DeviceProxy(self.spectrometerName)
        #=======================================================================

        self.attributes = {}
        self.attributes['Position'] = AttributeClass('Position', self.motorDev, 0.05)
        self.attributes['Speed'] = AttributeClass('Speed', self.motorDev, 0.05)
        self.attributes['Shutter'] = AttributeClass('Shutter', self.cameraDev, 0.3)
        self.attributes['Gain'] = AttributeClass('Gain', self.cameraDev, 0.3)
        self.attributes['Image'] = AttributeClass('Image', self.cameraDev, 1.0)
        self.attributes['State'] = AttributeClass('State', self.cameraDev, 0.3)


        self.attributes['Shutter'].attrSignal.connect(self.readExposure)
        self.attributes['Gain'].attrSignal.connect(self.readGain)
        self.attributes['Image'].attrSignal.connect(self.readImage)
        # self.attributes['state'].attrSignal.connect(self.readState)
        self.attributes['Position'].attrSignal.connect(self.readPosition)
        self.attributes['Speed'].attrSignal.connect(self.readSpeed)


        self.setLocale(QtCore.QLocale(QtCore.QLocale.English))
        self.layout = QtGui.QVBoxLayout(self)
        self.gridLayout1 = QtGui.QGridLayout()
        self.gridLayout2 = QtGui.QGridLayout()
        self.gridLayout3 = QtGui.QGridLayout()
        self.gridLayout4 = QtGui.QGridLayout()


        self.startPosSpinbox = QtGui.QDoubleSpinBox()
        self.startPosSpinbox.setDecimals(3)
        self.startPosSpinbox.setMaximum(2000000)
        self.startPosSpinbox.setMinimum(-2000000)
        self.startPosSpinbox.setValue(46.8)
        self.stepSizeSpinbox = QtGui.QDoubleSpinBox()
        self.stepSizeSpinbox.setDecimals(3)
        self.stepSizeSpinbox.setMaximum(2000000)
        self.stepSizeSpinbox.setMinimum(-2000000)
        self.stepSizeSpinbox.setValue(0.05)
        self.currentPosSpinbox = QtGui.QDoubleSpinBox()
        self.currentPosSpinbox.setDecimals(3)
        self.currentPosSpinbox.setMaximum(2000000)
        self.currentPosSpinbox.setMinimum(-2000000)
        self.averageSpinbox = QtGui.QSpinBox()
        self.averageSpinbox.setMaximum(100)
        self.averageSpinbox.setValue(self.settings.value('averages', 5).toInt()[0])
        self.averageSpinbox.editingFinished.connect(self.setAverage)
        self.setPosSpinbox = QtGui.QDoubleSpinBox()
        self.setPosSpinbox.setDecimals(3)
        self.setPosSpinbox.setMaximum(2000000)
        self.setPosSpinbox.setMinimum(-2000000)
        self.setPosSpinbox.setValue(63.7)
        self.setPosSpinbox.setValue(self.settings.value('setPos', 63).toDouble()[0])
        self.setPosSpinbox.editingFinished.connect(self.writePosition)
        self.currentPosLabel = QtGui.QLabel()
        f = self.currentPosLabel.font()
        f.setPointSize(14)
        currentPosTextLabel = QtGui.QLabel('Current pos ')
        currentPosTextLabel.setFont(f)
        self.currentPosLabel.setFont(f)
        self.currentSpeedLabel = QtGui.QLabel()


        self.startButton = QtGui.QPushButton('Start')
        self.startButton.clicked.connect(self.startScan)
        self.stopButton = QtGui.QPushButton('Stop')
        self.stopButton.clicked.connect(self.stopScan)
        self.exportButton = QtGui.QPushButton('Export')
        self.exportButton.clicked.connect(self.exportScan)

        self.pos = self.motorDev.read_attribute('position').value
        self.currentPosSpinbox.setValue(self.pos)


#        self.startButton.clicked.connect(self.)

        self.gridLayout1.addWidget(QtGui.QLabel("Start position"), 0, 0)
        self.gridLayout1.addWidget(self.startPosSpinbox, 0, 1)
        self.gridLayout1.addWidget(QtGui.QLabel("Step size"), 1, 0)
        self.gridLayout1.addWidget(self.stepSizeSpinbox, 1, 1)
        self.gridLayout1.addWidget(QtGui.QLabel("Averages"), 2, 0)
        self.gridLayout1.addWidget(self.averageSpinbox, 2, 1)
        self.gridLayout2.addWidget(QtGui.QLabel("Set position"), 0, 0)
        self.gridLayout2.addWidget(self.setPosSpinbox, 0, 1)
        self.gridLayout2.addWidget(QtGui.QLabel("Start scan"), 1, 0)
        self.gridLayout2.addWidget(self.startButton, 1, 1)
        self.gridLayout2.addWidget(QtGui.QLabel("Stop scan"), 2, 0)
        self.gridLayout2.addWidget(self.stopButton, 2, 1)
        self.gridLayout2.addWidget(QtGui.QLabel("Export scan"), 3, 0)
        self.gridLayout2.addWidget(self.exportButton, 3, 1)
        self.gridLayout3.addWidget(currentPosTextLabel, 0, 0)
        self.gridLayout3.addWidget(self.currentPosLabel, 0, 1)
        self.gridLayout3.addWidget(QtGui.QLabel("Current speed"), 1, 0)
        self.gridLayout3.addWidget(self.currentSpeedLabel, 1, 1)

        #=======================================================================
        # #camera slider controls
        # self.shutterSlider = QtGui.QSlider()
        # self.shutterSlider.setMaximum(500)
        # self.shutterSlider.setMaximum(0)
        # self.shutterSlider.setOrientation(QtCore.Qt.Horizontal)
        # self.gainSlider = QtGui.QSlider()
        # self.gainSlider.setOrientation(QtCore.Qt.Horizontal)
        # self.gridLayout4.addWidget(QtGui.QLabel("Shutter"), 0, 0)
        # self.gridLayout4.addWidget(self.shutterSlider, 0, 1)
        # self.gridLayout4.addWidget(QtGui.QLabel("Gain"), 1, 0)
        # self.gridLayout4.addWidget(self.gainSlider, 1, 1)
        #=======================================================================

        #camera controls
        self.shutterSpinbox = QtGui.QDoubleSpinBox()
        self.shutterSpinbox.setDecimals(3)
        self.shutterSpinbox.setMaximum(100)
        self.shutterSpinbox.setMinimum(0)
        #self.shutterSpinbox.setValue(10)
        self.shutterSpinbox.editingFinished.connect(self.writeExposure)

        self.gainSpinbox = QtGui.QDoubleSpinBox()
        self.gainSpinbox.setDecimals(3)
        self.gainSpinbox.setMaximum(200)
        self.gainSpinbox.setMinimum(0)
        self.gainSpinbox.setValue(10)
        self.shutterSpinbox.editingFinished.connect(self.writeGain)

        self.shutterSpinboxLabel = QtGui.QLabel()
        self.gainSpinboxLabel = QtGui.QLabel()

        self.gridLayout4.addWidget(QtGui.QLabel("Shutter"), 0, 0)
        self.gridLayout4.addWidget(self.shutterSpinbox, 0, 1)
        self.gridLayout4.addWidget(QtGui.QLabel("Current shutter"), 1, 0)
        self.gridLayout4.addWidget(self.shutterSpinboxLabel, 1, 1)
        self.gridLayout4.addWidget(QtGui.QLabel("Gain"), 2, 0)
        self.gridLayout4.addWidget(self.gainSpinbox, 2, 1)
        self.gridLayout4.addWidget(QtGui.QLabel("Current gain"), 3, 0)
        self.gridLayout4.addWidget(self.gainSpinboxLabel, 3, 1)


        self.plotWidget = pq.PlotWidget(useOpenGL=True)
        self.plot1 = self.plotWidget.plot()
        self.plot1.update()

        #self.plot1.setData(np.ones(10


        self.gv = pq.GraphicsView()
        self.vb = pq.ViewBox(lockAspect = 1.0, invertY = True)
        self.gv.setCentralItem(self.vb)
        self.image = pq.ImageItem()
        self.vb.addItem(self.image)

 #       self.gw = pq.GraphicsWindow(size=(1000,800), border=True)



        #ROI
        self.roi = pq.RectROI([20, 10], [30, 50], pen=(0,9), sideScalers = False)
        #rois.append(pq.MultiRectROI([[20, 90], [50, 60], [60, 90]], width=5, pen=(2,9)))
        self.roi.addScaleHandle([0.5, 0.], [0.5, 0.5])
        #self.roi.addScaleHandle([1,1],[0,0])
        self.roi.addScaleHandle([0,0],[0,0])
        self.vb.addItem(self.roi)

        hh = self.roi.getHandles()
        hh = [self.roi.mapToItem(self.image, h.pos()) for h in hh]
        print hh

        print self.roi.pos()
        print self.roi.size()

        self.roi.sigRegionChanged.connect(self.updateRoi)


        #self.roi.sigRegionChangeFinished.connect(self.updateRoiPlot)
        #self.updateRoiPlot(self)


#===============================================================================
#         for roi in rois:
#             roi.sigRegionChanged.connect(self.update)
#             self.vb.addItem(roi)
#
#         self.update(rois[-1])
#===============================================================================

        imageLayout = QtGui.QHBoxLayout()
        imageLayout.addWidget(self.gv)
        imageLayout.addWidget(self.plotWidget)

#        self.layout = QtGui.QVBoxLayout(self)

#===============================================================================
#         # plots
#         self.plotWidget = pq.PlotWidget(useOpenGL=True)
#         self.SpectrumPlot = self.plotWidget.plot()
#         self.SpectrumPlot.setPen((200, 25, 10))
#         self.SpectrumPlot.antialiasing = True
#         self.plotWidget.setAntialiasing(True)
#         self.plotWidget.showGrid(True, True)
#
#         plotLayout = QtGui.QHBoxLayout()
#         plotLayout.addWidget(self.plotWidget)
#===============================================================================

        #adding layouts        gridLay = QtGui.QHBoxLayout()
        gridLay = QtGui.QHBoxLayout()
        gridLay.addLayout(self.gridLayout1)
        gridLay.addSpacerItem(QtGui.QSpacerItem(30, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum))
        gridLay.addLayout(self.gridLayout2)
        gridLay.addSpacerItem(QtGui.QSpacerItem(30, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum))
        gridLay.addLayout(self.gridLayout3)
        gridLay.addSpacerItem(QtGui.QSpacerItem(30, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum))
        gridLay.addLayout(self.gridLayout4)
        gridLay.addSpacerItem(QtGui.QSpacerItem(30, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum))
        self.layout.addLayout(gridLay)
        self.layout.addLayout(imageLayout)


        self.trendData1 = np.zeros(600)
        self.trendData2 = np.zeros(600)
        self.scanData = np.array([])
        self.timeData = np.array([])
        self.posData = np.array([])
        self.avgSamples = 5
        self.currentSample = 0
        self.avgData = 0
        self.targetPos = 0.0
        self.measureUpdateTimes = np.array([time.time()])
        self.lock = threading.Lock()

        self.spectrum = np.array([])

        self.running = False
        self.scanning = False
        self.moving = False
        self.moveStart = False
        self.scanTimer = QtCore.QTimer()
        self.scanTimer.timeout.connect(self.scanUpdateAction)

        self.settings = QtCore.QSettings('Maxlab', 'RedpitayaTangoAutocorrelation')


#        specLayout = QtGui.QHBoxLayout()


        self.resize(800,400)
        self.update()

        #=======================================================================
        #print dir(self.roi)
        # print self.roi.viewPos()
        # print self.roi.viewRect()
        # print self.roi.x()
        # print self.roi.y()
        # print self.roi.sigRegionChanged()
        #=======================================================================


    def updateRoi(self):
        hh = self.roi.getHandles()
        hh = [self.roi.mapToItem(self.image, h.pos()) for h in hh]
         # ...after getting the handles' positions from the updated ROI
        ht = [np.array([h.x(), h.y(), 0.]) for h in hh]

        # The new ROI position is the position of that handle
        new_position = QtCore.QPointF(float(hh[2][0]), float(ht[2][1]))

        # Its new size is defined by the handles as well
        new_size = QtCore.QSizeF(float(np.linalg.norm(ht[2] - ht[1])), float(np.linalg.norm(ht[1] - ht[0])))
        # Set them
        self.roi.setPos(new_position, update=False, finish=False)
        self.roi.setSize(new_size, update=False, finish=False)



    #===========================================================================
    # def updateRoiPlot(self, roi, data=None):
    #     if data is None:
    #         data = roi.getArrayRegion(self.image, img=self.image)
    #         print 'updating roi'
    #     if data is not None:
    #         pass
    #         #self.plot1.setData(data.mean(axis=1))
    #===========================================================================

    def readExposure(self, data):
        self.shutterSpinboxLabel.setText(QtCore.QString.number(data.value, 'f', 3))
        #self.attributes['Shutter'] = data.value
        #print data.value

    def writeExposure(self):
        w = self.shutterSpinbox.value()
        self.attributes['Shutter'].attr_write(w)
        print w

    def readGain(self, data):
        self.gainSpinboxLabel.setText(QtCore.QString.number(data.value, 'f', 3))

    def writeGain(self):
        w = self.gainSpinbox.value()
        self.attributes['Gain'].attr_write(w)

    def readState(self, data):
        self.cameraName.setState(data)

    def readImage(self, data):
        #print data.value[0:10]
#         self.image.setImage(np.transpose(data), autoLevels = False, lut = self.lut, autoDownSample = True)
        self.image.setImage(np.transpose(data.value)[0:300,0:300])

    #===========================================================================
    # def readROIdata(self, data):
    #     self.image.
    #===========================================================================

    def readPosition(self, data):
        self.currentPosLabel.setText(QtCore.QString.number(data.value, 'f', 3))
        if np.abs(self.targetPos - data.value) < 0.01:
            self.moveStart = False
            self.moving = False

    def readSpeed(self, data):
        try:
            self.currentSpeedLabel.setText(QtCore.QString.number(data.value, 'f', 3))
            if self.moveStart == True:
                if data.value > 0.01:
                    self.moving = True
                    self.moveStart = False
            if self.moving == True:
                if np.abs(data.value) < 0.01:
                    self.moving = False
        except:
            pass

    def writePosition(self):
        w = self.setPosSpinbox.value()
        self.attributes['Position'].attr_write(w)

    def setAverage(self):
        self.avgSamples = self.averageSpinbox.value()

    def startScan(self):
        self.scanData = np.array([])
        self.timeData = np.array([])
        self.scanning = True
        self.motorDev.write_attribute('Position', self.startPosSpinbox.value())
        newPos = self.startPosSpinbox.value()
        self.pos = self.motorDev.read_attribute('Position').value
        self.currentPosSpinbox.setValue(self.pos)
        print 'Moving from ', self.pos
        motorState = self.motorDev.state()
#        while self.pos != self.startPosSpinbox.value():
        while (np.abs(self.pos - newPos) > 0.005) or (motorState == pt.DevState.MOVING):
            time.sleep(0.25)
            self.pos = self.motorDev.read_attribute('Position').value
            self.currentPosSpinbox.setValue(self.pos)
            motorState = self.motorDev.state()
            self.update()
        self.scanTimer.start(100 * self.avgSamples)


    def stopScan(self):
        print 'Stopping scan'
        self.running = False
        self.scanning = False
        self.scanTimer.stop()

    def exportScan(self):
        print 'Exporting scan data'
        data = np.vstack((self.posData, self.timeData, self.scanData)).transpose()
        filename = ''.join(('scandata_', time.strftime('%Y-%m-%d_%Hh%M'), '.txt'))
        np.savetxt(filename, data)

    def scanUpdateAction(self):
        self.scanTimer.stop()
        while self.running == True:
            time.sleep(0.1)
        newPos = self.targetPos + self.stepSizeSpinbox.value()
        print 'New pos: ', newPos
        self.attributes['position'].attr_write(newPos)
        self.targetPos = newPos
        self.running = True
        self.moveStart = True

    def measureScanData(self):
        self.avgData = self.trendData1[-self.avgSamples:].mean()
        self.scanData = np.hstack((self.scanData, self.avgData))
        pos = np.double(str(self.currentPosLabel.text()))
        newTime = (pos - self.startPosSpinbox.value()) * 2 * 1e-3 / 299792458.0
        self.timeData = np.hstack((self.timeData, newTime))
        self.posData = np.hstack((self.posData, pos * 1e-3))
        if self.timeUnitsRadio.isChecked() == True:
            self.plot5.setData(x=self.timeData * 1e12, y=self.scanData)
        else:
            self.plot5.setData(x=self.posData * 1e3, y=self.scanData)

    def measureData(self):
        if self.running == True and self.moving == False:
            data = self.devices['redpitaya'].read_attributes(['waveform1', 'waveform2'])
            self.waveform1 = data[0].value
            self.waveform2 = data[1].value
        goodInd = np.arange(self.signalStartIndex.value(), self.signalEndIndex.value() + 1, 1)
        bkgInd = np.arange(self.backgroundStartIndex.value(), self.backgroundEndIndex.value() + 1, 1)
        bkg = self.waveform1[bkgInd].mean()
        bkgPump = self.waveform2[bkgInd].mean()
        autoCorr = (self.waveform1[goodInd] - bkg).sum()
        pump = (self.waveform2[goodInd] - bkgPump).sum()
#        pump = 1.0
        if self.normalizePumpCheck.isChecked() == True:
            try:
                self.trendData1 = np.hstack((self.trendData1[1:], autoCorr / pump))
            except:
                pass
        else:
            self.trendData1 = np.hstack((self.trendData1[1:], autoCorr))
        self.plot3.setData(y=self.trendData1)

        # Evaluate the fps
        t = time.time()
        if self.measureUpdateTimes.shape[0] > 10:
            self.measureUpdateTimes = np.hstack((self.measureUpdateTimes[1:], t))
        else:
            self.measureUpdateTimes = np.hstack((self.measureUpdateTimes, t))
        fps = 1 / np.diff(self.measureUpdateTimes).mean()
        self.fpsLabel.setText(QtCore.QString.number(fps, 'f', 1))

        # If we are running a scan, update the scan data
        if self.running == True:
            if self.moving == False and self.moveStart == False:
                self.currentSample += 1
                if self.currentSample >= self.avgSamples:
                    self.running = False
                    self.measureScanData()
                    self.currentSample = 0
                    self.scanUpdateAction()

    def xAxisUnitsToggle(self):
        if self.timeUnitsRadio.isChecked() == True:
            self.plot5.setData(x=self.timeData * 1e12, y=self.scanData)
        else:
            self.plot5.setData(x=self.posData * 1e3, y=self.scanData)

#===============================================================================
#     def closeEvent(self, event):
#         for a in self.attributes.itervalues():
#             print 'Stopping', a.name
#             a.stopRead()
#         for a in self.attributes.itervalues():
#             a.readThread.join()
#
#         self.settings.setValue('startPos', self.startPosSpinbox.value())
#         self.settings.setValue('setPos', self.setPosSpinbox.value())
#         self.settings.setValue('averages', self.averageSpinbox.value())
#         self.settings.setValue('step', self.stepSizeSpinbox.value())
#         self.settings.setValue('startInd', self.signalStartIndex.value())
#         self.settings.setValue('endInd', self.signalEndIndex.value())
#         self.settings.setValue('bkgStartInd', self.backgroundStartIndex.value())
#         self.settings.setValue('bkgEndInd', self.backgroundEndIndex.value())
#         self.settings.setValue('xUnitTime', self.timeUnitsRadio.isChecked())
#         self.settings.sync()
#         event.accept()
#===============================================================================

    #===========================================================================
    # def setupLayout(self):
    #
    #     self.update()
    #===========================================================================

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    myapp = TangoDeviceClient(cameraName , motorName)
    myapp.show()
    sys.exit(app.exec_())



