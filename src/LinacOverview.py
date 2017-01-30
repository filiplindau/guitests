"""
Created on 23 jan 2017

@author: Filip Lindau
"""
from PyQt4 import QtGui, QtCore

import time
import sys


# noinspection PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit
class TangoDeviceClient(QtGui.QWidget):
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self,parent)
#        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.timeVector = None
        self.errorSampleTime = None
        self.xData = None
        self.xDataTemp = None

        self.setupLayout()

        splash.showMessage('         Initializing devices', alignment = QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
        app.processEvents()

        t0=time.clock()
        self.database_name = "g-v-csdb-0:10000/"
        self.devices = {}
        self.devices['shutter']=pt.DeviceProxy(''.join((self.database_name,
                                                        'i-b080603/pss/plc-01')))
        self.devices['timing_selector']=pt.DeviceProxy(''.join((self.database_name,
                                                        'g/tim/sel')))
        self.devices['energy_filter']=pt.DeviceProxy(''.join((self.database_name,
                                                        'i-k00/mag/pspc-01')))
        self.devices['r3_current']=pt.DeviceProxy(''.join((self.database_name,
                                                        'R3-319S2/DIA/DCCT-01')))
        self.devices['r1_current']=pt.DeviceProxy(''.join((self.database_name,
                                                        'R1-101S/DIA/DCCT-01')))
        self.devices['ms1_charge']=pt.DeviceProxy(''.join((self.database_name,
                                                        'I-MS1/DIA/BPL-02')))
        self.devices['ex3_charge']=pt.DeviceProxy(''.join((self.database_name,
                                                        'I-EX3/DIA/BPL-01')))
        self.devices['sp02_charge']=pt.DeviceProxy(''.join((self.database_name,
                                                        'I-SP02/DIA/BPL-02')))
        self.devices['virtual_cathode']=pt.DeviceProxy(''.join((self.database_name,
                                                        'lima/liveviewer/i-gs00-dia-caml-01')))
        self.devices['virtual_cathode'].command_inout_asynch('start')

        print time.clock()-t0, ' s'

        splash.showMessage('         Reading startup attributes', alignment = QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
        app.processEvents()


        self.guiLock = threading.Lock()
        self.attributes = {}
        self.attributes['shutter'] = AttributeClass('FBS_I_B080008_PSS_LS01__Out_Open', self.devices['shutter'], 0.3)
        self.attributes['shutter'].attrSignal.connect(self.read_shutter_state)
        self.attributes['injection'] = AttributeClass('Injection', self.devices['timing_selector'], 1.0)
        self.attributes['injection'].attrSignal.connect(self.read_timing_selector)
        self.attributes['gun'] = AttributeClass('current', self.devices['energy_filter'], 1.0)
        self.attributes['gun'].attrSignal.connect(self.read_energy_filter)
        self.attributes['r3_current'] = AttributeClass('InstantaneousCurrent', self.devices['r3_current'], 1.0)
        self.attributes['r3_current'].attrSignal.connect(self.read_r3_current)
        self.attributes['r1_current'] = AttributeClass('InstantaneousCurrent', self.devices['r1_current'], 1.0)
        self.attributes['r1_current'].attrSignal.connect(self.read_r1_current)
        self.attributes['ms1_charge'] = AttributeClass('Sum', self.devices['ms1_charge'], 1.0)
        self.attributes['ms1_charge'].attrSignal.connect(self.read_ms1_charge)
        self.attributes['ex3_charge'] = AttributeClass('Sum', self.devices['ex3_charge'], 1.0)
        self.attributes['ex3_charge'].attrSignal.connect(self.read_ex3_charge)
        self.attributes['sp02_charge'] = AttributeClass('Sum', self.devices['sp02_charge'], 1.0)
        self.attributes['sp02_charge'].attrSignal.connect(self.read_sp02_charge)
        self.attributes['virtual_cathode'] = AttributeClass('Image', self.devices['virtual_cathode'], 5.0)
        self.attributes['virtual_cathode'].attrSignal.connect(self.read_virtual_cathode)

    def read_shutter_state(self, data):
        if data.value is True:
            data.value = 'Open'
            if data.quality == pt.AttrQuality.ATTR_VALID:
                data.quality = pt.AttrQuality.ATTR_VALID
        else:
            data.value = 'Closed'
            if data.quality == pt.AttrQuality.ATTR_VALID:
                data.quality = pt.AttrQuality.ATTR_WARNING
        self.shutter_widget.setStatus(data)

    def read_timing_selector(self, data):
        if data.value == 'SPF':
            if data.quality == pt.AttrQuality.ATTR_VALID:
                data.quality = pt.AttrQuality.ATTR_VALID
        else:
            if data.quality == pt.AttrQuality.ATTR_VALID:
                data.quality = pt.AttrQuality.ATTR_WARNING
        self.timing_widget.setStatus(data)
        
    def read_energy_filter(self, data):
        if data.value > 0.05:
            if data.quality == pt.AttrQuality.ATTR_VALID:
                data.quality = pt.AttrQuality.ATTR_WARNING
            data.value = 'Thermionic'
        else:
            if data.quality == pt.AttrQuality.ATTR_VALID:
                data.quality = pt.AttrQuality.ATTR_VALID
            data.value = 'Photocathode'
        self.gun_widget.setStatus(data)

    def read_r1_current(self, data):
        self.rings_trend_widget.addPoint(data, 1)

    def read_r3_current(self, data):
        self.rings_trend_widget.addPoint(data, 0)

    def read_ms1_charge(self, data):
        self.linac_charge_trend_widget.addPoint(data, 0)

    def read_ex3_charge(self, data):
        self.linac_charge_trend_widget.addPoint(data, 1)

    def read_sp02_charge(self, data):
        self.linac_charge_trend_widget.addPoint(data, 2)

    def read_virtual_cathode(self, data):
        self.virtual_cathode_widget.setImage(data, True)

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

        self.title_sizes = qw.QTangoSizes()
        self.title_sizes.barHeight = 30
        self.title_sizes.barWidth = 20
        self.title_sizes.readAttributeWidth = 300
        self.title_sizes.writeAttributeWidth = 150
        self.title_sizes.fontStretch= 80
#        self.title_sizes.fontType = 'Trebuchet MS'
        self.title_sizes.fontType = 'Arial'

        self.frame_sizes = qw.QTangoSizes()
        self.frame_sizes.barHeight = 30
        self.frame_sizes.barWidth = 20
        self.frame_sizes.readAttributeWidth = 300
        self.frame_sizes.writeAttributeWidth = 150
        self.frame_sizes.fontStretch= 80
        self.frame_sizes.fontType = 'Arial'
#        self.frame_sizes.fontType = 'Trebuchet MS'

        self.attr_sizes = qw.QTangoSizes()
        self.attr_sizes.barHeight = 25
        self.attr_sizes.barWidth = 20
        self.attr_sizes.readAttributeWidth = 300
        self.attr_sizes.readAttributeHeight = 250
        self.attr_sizes.writeAttributeWidth = 299
        self.attr_sizes.fontStretch= 80
        self.attr_sizes.fontType = 'Arial'
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
        spacer_item_v = QtGui.QSpacerItem(20, 5, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.MinimumExpanding)
        spacer_item_bar = QtGui.QSpacerItem(self.frame_sizes.barWidth, self.frame_sizes.barHeight+8, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        spacer_item_h = QtGui.QSpacerItem(20, 5, QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Minimum)

        layout_data = QtGui.QHBoxLayout()
        layout_data.setMargin(self.attr_sizes.barHeight/2)
        layout_data.setSpacing(self.attr_sizes.barHeight*2)
        self.layout_attributes = QtGui.QVBoxLayout()
        self.layout_attributes.setMargin(0)
        self.layout_attributes.setSpacing(self.attr_sizes.barHeight/2)
        self.layout_attributes.setContentsMargins(0, 0, 0, 0)
        layout_attributes2 = QtGui.QVBoxLayout()
        layout_attributes2.setMargin(0)
        layout_attributes2.setSpacing(self.attr_sizes.barHeight / 2)
        layout_attributes2.setContentsMargins(0, 0, 0, 0)
        layout_attributes_top = QtGui.QHBoxLayout()
        layout_attributes_top.setMargin(0)
        layout_attributes_top.setSpacing(self.attr_sizes.barHeight / 2)
        layout_attributes_top.setContentsMargins(0, 0, 0, 0)

        self.title = qw.QTangoTitleBar('Linac', self.title_sizes)
        self.setWindowTitle('Linac overview')
        self.sidebar = qw.QTangoSideBar(colors = self.colors, sizes = self.frame_sizes)
        self.bottombar = qw.QTangoHorizontalBar()

        # Attributes
        self.shutter_widget = qw.QTangoCommandSelection('Shutter', colors = self.colors, sizes = self.attr_sizes)
        self.timing_widget = qw.QTangoCommandSelection('Target', colors = self.colors, sizes = self.attr_sizes)
        self.gun_widget = qw.QTangoCommandSelection('Gun', colors = self.colors, sizes = self.attr_sizes)

        # Trends
#        self.rings_trend_widget = qw.QTangoTrendBase(colors = self.colors, sizes = self.attr_sizes)
        self.rings_trend_widget = qw.QTangoReadAttributeTrend(name='R3', colors = self.colors, sizes = self.attr_sizes)
        self.rings_trend_widget.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.rings_trend_widget.valueTrend.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.rings_trend_widget.setMaximumHeight(800)
        self.rings_trend_widget.setMaximumWidth(2500)
        self.rings_trend_widget.setAttributeName('Ring current', 'A')
        self.rings_trend_widget.setPrefix('m')
        self.rings_trend_widget.setDuration(3600.0)
        self.rings_trend_widget.addCurve(name='R1')
        self.rings_trend_widget.showLegend(True)

        self.linac_charge_trend_widget = qw.QTangoReadAttributeTrend(name='MS1', colors = self.colors, sizes = self.attr_sizes)
        self.linac_charge_trend_widget.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.linac_charge_trend_widget.valueTrend.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.linac_charge_trend_widget.setMaximumHeight(800)
        self.linac_charge_trend_widget.setMaximumWidth(1500)
        self.linac_charge_trend_widget.setAttributeName('Linac charge', 'pC')
        self.linac_charge_trend_widget.setDuration(3600.0)
        self.linac_charge_trend_widget.showLegend(True)
        self.linac_charge_trend_widget.addCurve(name="EX3")
        self.linac_charge_trend_widget.addCurve(name="SP02")
        self.linac_charge_trend_widget.showLegend(False)
        self.linac_charge_trend_widget.showLegend(True)

        self.virtual_cathode_widget = qw.QTangoReadAttributeImage()
        self.virtual_cathode_widget.setAttributeName('Virtual cathode')
        self.virtual_cathode_widget.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        self.virtual_cathode_widget.setMaximumHeight(self.attr_sizes.readAttributeHeight)
        self.virtual_cathode_widget.setMaximumWidth(self.attr_sizes.readAttributeWidth)



############################
# Setting up layout
#
        layout_attributes2.addWidget(self.shutter_widget)
        layout_attributes2.addWidget(self.gun_widget)
        layout_attributes2.addWidget(self.timing_widget)
        layout_attributes2.addSpacerItem(spacer_item_v)
        layout_attributes_top.addLayout(layout_attributes2)
        layout_attributes_top.addSpacerItem(spacer_item_h)
        layout_attributes_top.addWidget(self.virtual_cathode_widget)
        self.layout_attributes.addLayout(layout_attributes_top)
        self.layout_attributes.addWidget(self.linac_charge_trend_widget)
        self.layout_attributes.addWidget(self.rings_trend_widget)        


        layout2.addWidget(self.title)
        layout2.addSpacerItem(QtGui.QSpacerItem(20, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum))
        layout2.addLayout(layout_data)
        layout2.addWidget(self.bottombar)
        layout1.addLayout(layout2)
        layout0.addLayout(layout1)
        layout_data.addLayout(self.layout_attributes)
#        layout_data.addSpacerItem(spacer_item_h)

        self.setGeometry(200,100,350,600)

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