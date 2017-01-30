'''
Created on 15 sep 2016

@author: laser
'''


from PyQt4 import QtGui, QtCore
import PyTango as pt
from QTangoWidgets.AttributeReadThreadClass import AttributeClass
import sys
import pyqtgraph as pq
import numpy as np


# noinspection PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit
class TangoDeviceClient(QtGui.QWidget):
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self)
        self.cameraName = pt.DeviceProxy('gunlaser/thg/camera')
        self.cameraDevice = pt.DeviceProxy(self.cameraName)
        self.image = self.cameraName.read_attribute('Image').value
        
        print self.image[0:10,0]

        self.myLayout()


    def myLayout(self):
        #=======================================================================
        self.layout = QtGui.QVBoxLayout(self) #the whole window, main layout
        self.inputLayout = QtGui.QHBoxLayout()
        self.plotLayout = QtGui.QHBoxLayout()
        # self.gridLayout1 = QtGui.QGridLayout()
        self.layout.addLayout(self.inputLayout)
        self.layout.addLayout(self.plotLayout)
        #=======================================================================

        self.button = QtGui.QPushButton('button')
        self.inputLayout.addWidget(self.button)

        win = pq.GraphicsLayoutWidget()
        self.plotLayout.addWidget(win)
#        win.show()  ## show widget alone in its own window
#        win.setWindowTitle('pyqtgraph example: ImageItem')
        view = win.addViewBox()

        view.setAspectLocked(True)

        img = pq.ImageItem(border='w')
        view.addItem(img)
        img.setImage(self.image)
        
        view.setRange(QtCore.QRectF(0, 0, 600, 600))


 
if __name__ == '__main__':
    
    app = QtGui.QApplication([])
    myapp = TangoDeviceClient()
    myapp.show()
    sys.exit(app.exec_())
