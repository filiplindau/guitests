'''
Created on 28 sep 2016

@author: laser
'''

import PyTango as pt
import time
import pyqtgraph as pq
from PyQt4 import QtGui, QtCore
import sys



class TangoDeviceClient(QtGui.QWidget):
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)
        self.adName = pt.DeviceProxy('gunlaser/devices/ad5370dac')
        self.adDevice = pt.DeviceProxy(self.adName)

        self.myLayout()

        #self.adName.write_attribute('channel0',1)
        time.sleep(0.)
        #voltages = self.adName.read_attribute('channel0')


        #print voltages.value
    
    def setVoltages(self):
        print 'reading voltage'
        for i in range(0,1):
            print self.voltageSliders[i].value

    def myLayout(self):
        self.layout = QtGui.QVBoxLayout(self) #the whole window, main layout
        self.gridLayout1 = QtGui.QGridLayout()
        self.layout.addLayout(self.gridLayout1)

#===============================================================================
#         self.ch0slider = QtGui.QSlider()
#         self.gridLayout1.addWidget(self.ch0slider,0,0)
#         #self.gridLayout1.addWidget(QtGui.QLabel(str(0),0,1))
#
#         self.ch1slider = QtGui.QSlider()
#         self.gridLayout1.addWidget(self.ch0slider,0,1)
#===============================================================================
        self.voltageSliders = []
        for i in range(0,1):
            slider = QtGui.QSlider()
            slider.setTickPosition(QtGui.QSlider.TicksLeft)
            slider.setTickInterval(1)
            slider.setMaximum(10)
            slider.setMinimum(0)
            slider.valueChanged.connect(self.setVoltages)
            self.voltageSliders.append(slider)
            self.gridLayout1.addWidget(slider,0,i)
            self.gridLayout1.addWidget(QtGui.QLabel(str(i)), 1,i)
            
        

        print len(self.voltageSliders)

        #=======================================================================
        # for i in range(0,40):
        #     self.gridLayout1.addWidget(QtGui.QSlider(),0,i)
        #     self.gridLayout1.addWidget(QtGui.QLabel(str(i)), 1,i)
        #     self.voltageSliders.valueChanged.connect(self.setVoltages)
        #=======================================================================



if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    myapp = TangoDeviceClient()
    myapp.show()
    sys.exit(app.exec_())