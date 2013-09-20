# -*- coding:utf-8 -*-
"""
Created on Aug 26, 2013

@author: Filip
"""
import numpy as np
import PyTango as pt
import pyqtgraph as pq
from PyQt4 import QtGui, QtCore
import sys
import time

class SmallTrend(QtGui.QWidget):
	def __init__(self, parent = None):
		self.bkgColor = QtGui.QColor(0x000000)
		self.axisColor = QtGui.QColor(0xffcc66)
		self.crvColor = QtGui.QColor(0x99ccff)
		
		QtGui.QWidget.__init__(self,parent)
		
		self.maxDataSize = 20000
		self.xSpan = float(1800.0)
		self.ySpan = float(800.0)
 		self.axisOffset = 1
		self.xScale = (self.size().width() - self.axisOffset*2) / self.xSpan		
		self.yScale = (self.size().height() - self.axisOffset*2) / self.ySpan

		
		
		self.xData = np.zeros(self.maxDataSize)
		self.yData = np.zeros(self.maxDataSize)
		self.xData[0] = time.time()
		self.paintPath = QtGui.QPainterPath(QtCore.QPointF((self.xData[0]-self.xData[0])*self.xScale, self.yData[0]))
		self.dataPoly = QtGui.QPolygonF([QtCore.QPointF(self.width()-self.axisOffset,self.height()-self.axisOffset),
										QtCore.QPointF(self.width()-self.axisOffset,self.height()-self.axisOffset)])
		self.pointList = [QtCore.QPointF(self.width()-self.axisOffset-0*self.xScale, self.height()-self.axisOffset-0*self.yScale), 
						QtCore.QPointF(self.width()-self.axisOffset-0*self.xScale, self.height()-self.axisOffset-0*self.yScale)]
		self.xPos = 0
		self.xNum = 1	
			
		self.curvePen = QtGui.QPen(self.crvColor)
		self.curvePen.setWidthF(1.3)
		self.curvePen.setCosmetic(True)		
		crvFillColor = self.crvColor
		crvFillColor.setAlphaF(0.2)
		self.curveBrush = QtGui.QBrush(crvFillColor)
		self.curveBrush.setStyle = QtCore.Qt.SolidPattern
		self.axisPen = QtGui.QPen(self.axisColor)
		self.axisPen.setWidthF(1.0)
		self.axisBrush = QtGui.QBrush()
		self.axisBrush.setStyle = QtCore.Qt.NoBrush
		self.axisFont = QtGui.QFont('arial', 8)
		self.axisFontHeight = QtGui.QFontMetricsF(self.axisFont).height()
		
		self.setMinimumWidth(50)
		self.setMinimumHeight(20)
		self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
		p = self.palette()
		p.setColor(self.backgroundRole(), self.bkgColor)
		self.setPalette(p)
		self.setAutoFillBackground(True)

		self.axisRect = QtCore.QRectF(10.0, 10.0, self.size().width(), self.size().height())		
		self.viewRect = QtCore.QRectF(0,-0.01,self.xSpan,2*self.ySpan)
		
		
		
				
			
	def updateData(self, xNew, yNew):
#		print 'In updateData: '
		self.xPos += 1
		if self.xPos >= self.maxDataSize:
			self.xPos = 0
		self.xData[self.xPos]=xNew	
		self.yData[self.xPos]=yNew
		self.xNum += 1	
		if self.xNum > self.maxDataSize:
			self.xNum = self.maxDataSize

# 		self.pointList[-1] = QtCore.QPointF(self.width()-self.axisOffset-(xNew - self.xData[0])*self.xScale, self.height()-self.axisOffset-yNew*self.yScale)
#  		self.pointList.append(QtCore.QPointF(self.width()-self.axisOffset-(xNew - self.xData[0])*self.xScale, self.height()-self.axisOffset))
#  		self.dataPoly = QtGui.QPolygonF(self.pointList)

		self.pointList[-1] = QtCore.QPointF(xNew, yNew)
 		self.pointList.append(QtCore.QPointF(xNew, 0.0))

		self.pointList = [QtCore.QPointF(self.xData[0], 0)]
		self.pointList = [ QtCore.QPointF(x, self.yData[ind]) for ind, x in enumerate(self.xData[0:self.xPos])]
		self.pointList.append(QtCore.QPointF(self.xData[self.xPos], 0.0))
 		
 		self.dataPoly = QtGui.QPolygonF(self.pointList)
		
		self.update()


	def paintEvent(self, e):
#		print "In paintEvent:"

		transform = QtGui.QTransform()
#		transform = QtGui.QTransform.fromTranslate(self.width()-self.axisOffset, self.height()-self.axisOffset)
		transform.translate(self.width()-self.axisOffset, self.height()-self.axisOffset+1)
		transform.scale(self.xScale, -self.yScale)
		transform.translate(-self.xData[self.xPos], 0)
		
# 		print '0,0 -> ', transform.map(0,0)
# 		print '50,0 -> ', transform.map(self.xData[0],0)
# 		print '0,1.5 -> ', transform.map(0,1.5)

 		right = self.width()-self.axisOffset
 		bottom = self.height()-self.axisOffset
 		painter = QtGui.QPainter()
 		painter.begin(self)
  		painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
  		painter.setTransform(transform)  	
  		painter.setPen(self.curvePen)
  		painter.setBrush(self.curveBrush)
  		painter.drawPolygon(self.dataPoly)
  		painter.setRenderHint(QtGui.QPainter.TextAntialiasing, True)
  		painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform, True)
  		painter.setWorldMatrixEnabled(False)
  		painter.setPen(self.axisPen)
  		painter.setBrush(self.axisBrush)
  		painter.setFont(self.axisFont)
  		painter.drawText(self.axisOffset+2, bottom-1, str(self.xSpan))
  		s = str(self.ySpan)
  		painter.drawText(right-QtGui.QFontMetricsF(self.axisFont).width(s)-2, self.axisOffset+self.axisFontHeight-4, s)
  		painter.setRenderHint(QtGui.QPainter.Antialiasing, False)
  		painter.drawRect(self.axisOffset, self.axisOffset, right - self.axisOffset, bottom - self.axisOffset)
 		painter.end()
		
	
	def resizeEvent(self, e):
		self.xScale = (self.size().width() - self.axisOffset*2-2) / self.xSpan		
		self.yScale = (self.size().height() - self.axisOffset*2-2) / self.ySpan
		print self.curvePen.isCosmetic()
		print 'In resizeEvent: scale ', self.xScale, self.yScale
		print 'Extents: ', self.size().width(), self.size().height() 
		
		self.generatePointList()
					
		self.dataPoly = QtGui.QPolygonF(self.pointList)
		
	def generatePointList(self):
		if self.xNum < 2:
			self.pointList = [QtCore.QPointF(self.width()-self.axisOffset-0*self.xScale, self.height()-self.axisOffset-0*self.yScale), 
						QtCore.QPointF(self.width()-self.axisOffset-0*self.xScale, self.height()-self.axisOffset-0*self.yScale)]
			self.pointList = [QtCore.QPointF(0.0, 0.0),	QtCore.QPointF(0.0, 0.0)]
		else:
	 		hOff = self.width()-self.axisOffset
	 		vOff = self.height()-self.axisOffset
			
			self.pointList = [QtCore.QPointF(self.width()-self.axisOffset-0*self.xScale, self.height()-self.axisOffset-0*self.yScale)]
			self.pointList = [ QtCore.QPointF(hOff-(x - self.xData[0])*self.xScale, vOff-self.yData[ind]*self.yScale) for ind, x in enumerate(self.xData[0:self.xPos])]
			self.pointList.append(QtCore.QPointF(self.width()-self.axisOffset-(self.xData[self.xPos] - self.xData[0])*self.xScale, self.height()-self.axisOffset))
		
			self.pointList = [QtCore.QPointF(0, 0)]
			self.pointList = [ QtCore.QPointF(x, self.yData[ind]) for ind, x in enumerate(self.xData[0:self.xPos])]
			self.pointList.append(QtCore.QPointF(self.xData[self.xPos], 0.0))

		
class TrendTest(QtGui.QWidget):
	def __init__(self, parent = None):
		QtGui.QWidget.__init__(self, parent)

		self.deviceName = 'testfel/gunlaser/osc_spectrometer'
	
		self.device = pt.DeviceProxy(self.deviceName)
		
		layout = QtGui.QVBoxLayout(self)
		layout2 = QtGui.QHBoxLayout(self)
		self.trendWidget = SmallTrend()
		label = QtGui.QLabel(''.join(('Trending ', self.deviceName)))
		self.labelData = QtGui.QLabel('')

		layout.addWidget(label)
		layout2.addWidget(self.trendWidget)
		layout2.addWidget(self.labelData)
		layout.addLayout(layout2)

		s = '''QWidget { background-color : #000000;
			color : #66ccff; }
			QLabel { background-color : #000000;
			color : #66ccff; }
		'''
		self.setStyleSheet(s)
		
		self.timer = QtCore.QTimer()
		QtCore.QObject.connect(self.timer, QtCore.SIGNAL("timeout()"), self.updateData)
		self.timer.start(500)
		
	def updateData(self):
		attr = self.device.read_attribute('PeakEnergy')
		t = attr.value
		self.labelData.setText(str(int(t)))
		self.trendWidget.updateData(time.time(), t)
		

if __name__ == '__main__':
	app = QtGui.QApplication(sys.argv)
	myapp = TrendTest()
	myapp.show()
	sys.exit(app.exec_())	
