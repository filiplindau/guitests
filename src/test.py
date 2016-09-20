'''
Created on 5 feb 2016

@author: laser
'''
import PyTango as pt
import numpy as np
from PyQt4 import QtGui, QtCore
import sys
from QTangoWidgets.AttributeReadThreadClass import AttributeClass
import pyqtgraph as pq
import time


motorName = pt.DeviceProxy('gunlaser/motors/zaber01')
spectrometerName = pt.DeviceProxy('gunlaser/devices/spectrometer_diag')


class TangoDeviceClient(QtGui.QWidget):
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self,parent)

        self.devices = {}
        self.motorName = motorName
        self.motorDev = pt.DeviceProxy(self.motorName)
        self.spectName = spectrometerName
        self.specDev = pt.DeviceProxy(self.spectName)

        self.specDev.command_inout('init')
        time.sleep(1)
        self.specDev.command_inout('on')
        time.sleep(1)


        self.pos = self.motorDev.read_attribute('position').value
        print self.pos

        print self.specDev.attribute_list_query()

        self.state = self.specDev.read_attribute('State').value
        print self.state

        self.Wavelengths = self.specDev.read_attribute('Wavelengths').value
        self.spectrum = self.specDev.read_attribute('Spectrum').value
        print self.spectrum

        self.plotWidget = pq.PlotWidget(useOpenGL=True)
        self.plot1 = self.plotWidget.plot()
        self.plot1.setPen((200, 25, 10))
        self.plot1.antialiasing = True
        self.plotWidget.setAntialiasing(True)
        self.plotWidget.showGrid(True, True)

        self.plot1.setData(x=self.Wavelengths)
        self.plot1.setData(y=self.spectrum)
        self.plot1.update()


        plotLayout = QtGui.QHBoxLayout()
        plotLayout.addWidget(self.plotWidget)

        self.layout = QtGui.QVBoxLayout(self)
        self.layout.addLayout(plotLayout)
        
        
        


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    myapp = TangoDeviceClient()
    myapp.show()
    sys.exit(app.exec_())