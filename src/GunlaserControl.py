'''
Created on 30 Nov 2016

@author: Filip Lindau
'''
from PyQt4 import QtGui, QtCore

import time
import sys


# noinspection PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit
class TangoDeviceClient(QtGui.QWidget):
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self,parent)
#        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.timevector = None
        self.error_sampletime = None

        self.setupLayout()

        splash.showMessage('         Initializing devices', alignment = QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
        app.processEvents()

        t0=time.clock()
        self.devices = {}
        self.devices['finesse']=pt.DeviceProxy('gunlaser/oscillator/finesse')
        self.devices['mp_lee']=pt.DeviceProxy('gunlaser/mp/leelaser')
        self.devices['mp_temp']=pt.DeviceProxy('gunlaser/mp/temperature')
        self.devices['regen_lee']=pt.DeviceProxy('gunlaser/regen/leelaser')
        self.devices['regen_temp']=pt.DeviceProxy('gunlaser/regen/temperature')
        self.devices['mp_temp']=pt.DeviceProxy('gunlaser/mp/temperature')
        self.devices['spectrometer']=pt.DeviceProxy('gunlaser/oscillator/spectrometer')
        self.devices['halcyon']=pt.DeviceProxy('gunlaser/oscillator/halcyon_raspberry')
        self.devices['redpitaya_osc']=pt.DeviceProxy('gunlaser/devices/redpitaya0')
        self.devices['redpitaya_thg']=pt.DeviceProxy('gunlaser/devices/redpitaya3')
        print time.clock()-t0, ' s'

        splash.showMessage('         Reading startup attributes', alignment = QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
        app.processEvents()


        self.guiLock = threading.Lock()
        self.attributes = {}
        # Finesse
        self.attributes['finesse_power'] = AttributeClass('power', self.devices['finesse'], 0.3)
        self.attributes['finesse_temp'] = AttributeClass('lasertemperature', self.devices['finesse'], 0.3)
        self.attributes['finesse_state'] = AttributeClass('state', self.devices['finesse'], 0.3)
        self.attributes['finesse_shutter'] = AttributeClass('shutterstate', self.devices['finesse'], 0.3)
        self.attributes['finesse_operation'] = AttributeClass('laseroperationstate', self.devices['finesse'], 0.3)
        
        self.attributes['finesse_power'].attrSignal.connect(self.read_finesse_power)
        self.attributes['finesse_temp'].attrSignal.connect(self.read_finesse_temp)
        self.attributes['finesse_state'].attrSignal.connect(self.read_finesse_state)
        self.attributes['finesse_shutter'].attrSignal.connect(self.read_finesse_shutter)
        self.attributes['finesse_operation'].attrSignal.connect(self.read_finesse_operation)
        
        # Oscillator
        self.attributes['oscillator_power'] = AttributeClass('measurementdata1', self.devices['redpitaya_osc'], 0.3)
        self.attributes['oscillator_power'].attrSignal.connect(self.read_oscillator_power)
        
        self.attributes['wavelengths'] = AttributeClass('wavelengthsROI', self.devices['spectrometer'], None)
        self.attributes['peakwidth'] = AttributeClass('peakwidth', self.devices['spectrometer'], 0.3)
        self.attributes['spectrum'] = AttributeClass('spectrumROI', self.devices['spectrometer'], 0.3)
        self.attributes['peakwidth'].attrSignal.connect(self.read_peak_width)
        self.attributes['spectrum'].attrSignal.connect(self.read_spectrum)
        self.attributes['wavelengths'].attrSignal.connect(self.read_wavelengths)

        # Halcyon
        self.attributes['halcyon_error_trace'] = AttributeClass('errortrace', self.devices['halcyon'], 0.3)
        self.attributes['halcyon_error_trace'].attrSignal.connect(self.read_error_trace)
        self.attributes['halcyon_error_frequency'] = AttributeClass('errorfrequency', self.devices['halcyon'], 0.3)
        self.attributes['halcyon_error_frequency'].attrSignal.connect(self.read_error_frequency)
        self.attributes['halcyon_sampletime'] = AttributeClass('sampletime', self.devices['halcyon'], None)
        self.attributes['halcyon_sampletime'].attrSignal.connect(self.read_halcyon_sampletime)

        # Regen Lee
        self.attributes['regen_lee_current'] = AttributeClass('percentcurrent', self.devices['regen_lee'], 0.3)
        self.attributes['regen_lee_state'] = AttributeClass('state', self.devices['regen_lee'], 0.3)
        self.attributes['regen_lee_shutter'] = AttributeClass('shutterstate', self.devices['regen_lee'], 0.3)
        self.attributes['regen_lee_operation'] = AttributeClass('laserstate', self.devices['regen_lee'], 0.3)

        self.attributes['regen_lee_current'].attrSignal.connect(self.read_regen_lee_percentcurrent)
        self.attributes['regen_lee_shutter'].attrSignal.connect(self.read_regen_lee_shutter)
        self.attributes['regen_lee_state'].attrSignal.connect(self.read_regen_lee_state)
        self.attributes['regen_lee_operation'].attrSignal.connect(self.read_regen_lee_operation)

        self.attributes['regen_temperature'] = AttributeClass('temperature', self.devices['regen_temp'], 0.5)
        self.attributes['regen_temperature'].attrSignal.connect(self.read_regen_temperature)
        
        # MP Lee
        self.attributes['mp_lee_current'] = AttributeClass('percentcurrent', self.devices['mp_lee'], 0.3)
        self.attributes['mp_lee_state'] = AttributeClass('state', self.devices['mp_lee'], 0.3)
        self.attributes['mp_lee_shutter'] = AttributeClass('shutterstate', self.devices['mp_lee'], 0.3)
        self.attributes['mp_lee_operation'] = AttributeClass('laserstate', self.devices['mp_lee'], 0.3)

        self.attributes['mp_lee_current'].attrSignal.connect(self.read_mp_lee_percentcurrent)        
        self.attributes['mp_lee_shutter'].attrSignal.connect(self.read_mp_lee_shutter)
        self.attributes['mp_lee_state'].attrSignal.connect(self.read_mp_lee_state)
        self.attributes['mp_lee_operation'].attrSignal.connect(self.read_mp_lee_operation)

        self.attributes['mp_temperature'] = AttributeClass('temperature', self.devices['mp_temp'], 0.5)
        self.attributes['mp_temperature'].attrSignal.connect(self.read_mp_temperature)


        splash.showMessage('         Setting up variables', alignment = QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
        app.processEvents()

# Attribute reads
    def read_finesse_power(self, data):
        self.finesse_power_widget.setAttributeValue(data)

    def read_finesse_temp(self, data):
        self.finesse_temp_widget.setAttributeValue(data)

    def read_finesse_state(self, data):
        self.finesse_name.setState(data)

    def read_finesse_shutter(self, data):
        self.finesse_shutter_widget.setStatus(data)

    def read_finesse_operation(self, data):
        self.finesse_operation_widget.setStatus(data)

    def read_oscillator_power(self, data):
        self.oscillator_power_widget.setAttributeValue(data)

    def read_wavelengths(self, data):
        try:
            print 'time vector read: ', data.value.shape[0]
        except:
            pass
        self.timevector = data.value

    def read_spectrum(self, data):
        if self.timevector is None:
            print 'No time vector'
        else:
            self.oscillator_spectrum_plot.setSpectrum(xData = self.timevector, yData = data)
            self.oscillator_spectrum_plot.update()
            
    def read_peak_width(self, data):
        self.oscillator_peak_width_widget.setAttributeValue(data)

    def read_error_frequency(self, data):
        self.error_frequency_widget.setAttributeValue(data)
        
    def read_error_trace(self, data):
        if self.error_sampletime is None:
            print 'No time vector'
        else:
            timevector = np.linspace(0,data.value.shape[0]*self.error_sampletime, data.value.shape[0])
            self.error_trace_widget.setSpectrum(xData = timevector, yData = data)
            self.error_trace_widget.update()
    
    def read_halcyon_sampletime(self, data):
        try:
            print 'Sample time read: ', data.value
            self.error_sampletime = data.value
        except:
            pass

    def read_regen_lee_state(self, data):
        self.regen_lee_name.setState(data)

    def read_regen_lee_shutter(self, data):
        self.regen_shutter_widget.setStatus(data)

    def read_regen_lee_operation(self, data):
        self.regen_operation_widget.setStatus(data)
        
    def read_regen_lee_percentcurrent(self, data):
        self.regen_current_widget.setAttributeValue(data)
        
    def write_regen_lee_percentcurrent(self):
        w = self.regen_current_widget.getWriteValue()
        self.attributes['regen_lee_current'].attr_write(w)
        
    def read_regen_temperature(self, data):
        self.regen_temp_widget.setAttributeValue(data)

    def read_mp_lee_state(self, data):
        self.mp_lee_name.setState(data)

    def read_mp_lee_shutter(self, data):
        self.mp_shutter_widget.setStatus(data)

    def read_mp_lee_operation(self, data):
        self.mp_operation_widget.setStatus(data)
        
    def read_mp_lee_percentcurrent(self, data):
        self.mp_current_widget.setAttributeValue(data)
        
    def write_mp_lee_percentcurrent(self):
        w = self.mp_current_widget.getWriteValue()
        self.attributes['mp_lee_current'].attr_write(w)
        
    def read_mp_temperature(self, data):
        self.mp_temp_widget.setAttributeValue(data)        

# Commands    
    def start_finesse(self):
        self.devices['finesse'].command_inout('on')

    def stop_finesse(self):
        self.devices['finesse'].command_inout('off')

    def open_finesse_shutter(self):
        self.devices['finesse'].command_inout('open')

    def close_finesse_shutter(self):
        self.devices['finesse'].command_inout('close')
        
    def start_regen(self):
        self.devices['regen_lee'].command_inout('startlaser')

    def stop_regen(self):
        self.devices['regen_lee'].command_inout('off')

    def clear_regen(self):
        self.devices['regen_lee'].command_inout('clearfault')

    def open_regen_shutter(self):
        self.devices['regen_lee'].command_inout('open')

    def close_regen_shutter(self):
        self.devices['regen_lee'].command_inout('close')
        
    def start_mp(self):
        self.devices['mp_lee'].command_inout('startlaser')

    def stop_mp(self):
        self.devices['mp_lee'].command_inout('off')

    def clear_mp(self):
        self.devices['mp_lee'].command_inout('clearfault')

    def open_mp_shutter(self):
        self.devices['mp_lee'].command_inout('open')

    def close_mp_shutter(self):
        self.devices['mp_lee'].command_inout('close')

################
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
        for a in self.attributes.itervalues():
            a.readThread.join()
        event.accept()

    def setupLayout(self):
        s='QWidget{background-color: #000000; }'
        self.setStyleSheet(s)

        self.frame_sizes = qw.QTangoSizes()
        self.frame_sizes.barHeight = 20
        self.frame_sizes.barWidth = 18
        self.frame_sizes.readAttributeWidth = 280
        self.frame_sizes.writeAttributeWidth = 150
        self.frame_sizes.fontStretch= 80
        self.frame_sizes.fontType = 'Segoe UI'
#        self.frame_sizes.fontType = 'Trebuchet MS'

        self.attr_sizes = qw.QTangoSizes()
        self.attr_sizes.barHeight = 22
        self.attr_sizes.barWidth = 25
        self.attr_sizes.readAttributeWidth = 280
        self.attr_sizes.readAttributeHeight = 250
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
        spacerItemV = QtGui.QSpacerItem(20, 5, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.MinimumExpanding)
        spacerItemBar = QtGui.QSpacerItem(self.frame_sizes.barWidth, self.frame_sizes.barHeight+8, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        spacerItemH = QtGui.QSpacerItem(20, 5, QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Minimum)
        spacerItemSmall = QtGui.QSpacerItem(20, 15, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)

        layoutData = QtGui.QHBoxLayout()
        layoutData.setMargin(self.attr_sizes.barHeight/2)
        layoutData.setSpacing(self.attr_sizes.barHeight*2)
        self.layout_attributes = QtGui.QVBoxLayout()
        self.layout_attributes.setMargin(0)
        self.layout_attributes.setSpacing(self.attr_sizes.barHeight/2)
        self.layout_attributes.setContentsMargins(0, 0, 0, 0)

        self.layoutAttributes2 = QtGui.QVBoxLayout()
        self.layoutAttributes2.setMargin(0)
        self.layoutAttributes2.setSpacing(self.attr_sizes.barHeight/2)
        self.layoutAttributes2.setContentsMargins(0, 0, 0, 0)

        self.layoutAttributes3 = QtGui.QVBoxLayout()
        self.layoutAttributes3.setMargin(0)
        self.layoutAttributes3.setSpacing(self.attr_sizes.barHeight/2)
        self.layoutAttributes3.setContentsMargins(0, 0, 0, 0)

        self.title = qw.QTangoTitleBar('Gunlaser Control')
        self.setWindowTitle('Gunlaser control')
        self.sidebar = qw.QTangoSideBar(colors = self.colors, sizes = self.frame_sizes)
        self.bottombar = qw.QTangoHorizontalBar()

        self.finesse_name = qw.QTangoDeviceNameStatus(colors = self.colors, sizes = self.frame_sizes)
        self.finesse_name.setAttributeName('Finesse')

        self.finesse_shutter_widget = qw.QTangoCommandSelection('Shutter', colors = self.colors, sizes = self.attr_sizes)
        self.finesse_shutter_widget.addCmdButton('Open', self.open_finesse_shutter)
        self.finesse_shutter_widget.addCmdButton('Close', self.close_finesse_shutter)

        self.finesse_operation_widget = qw.QTangoCommandSelection('Operation', colors = self.colors, sizes = self.attr_sizes)
        self.finesse_operation_widget.addCmdButton('Start', self.start_finesse)
        self.finesse_operation_widget.addCmdButton('Stop', self.stop_finesse)

        self.finesse_power_widget = qw.QTangoReadAttributeDouble(colors = self.colors, sizes = self.attr_sizes)
        self.finesse_power_widget.setAttributeName('Finesse power', 'W')

        self.finesse_temp_widget = qw.QTangoReadAttributeDouble(colors = self.colors, sizes = self.attr_sizes)
        self.finesse_temp_widget.setAttributeName('Finesse temp', 'degC')

        self.oscillator_power_widget = qw.QTangoReadAttributeDouble(colors = self.colors, sizes = self.attr_sizes)
        self.oscillator_power_widget.setAttributeName('Oscillator power', 'W')
        self.oscillator_power_widget.setPrefix('m')
        self.oscillator_peak_width_widget = qw.QTangoReadAttributeDouble(colors = self.colors, sizes = self.attr_sizes)
        self.oscillator_peak_width_widget.setAttributeName('Width FWHM', 'nm')
        self.oscillator_spectrum_plot = qw.QTangoReadAttributeSpectrum(colors = self.colors, sizes = self.attr_sizes)
        self.oscillator_spectrum_plot.setAttributeName('Oscillator spectrum')
        self.oscillator_spectrum_plot.setXRange(700, 900)
        self.oscillator_spectrum_plot.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

        self.error_frequency_widget = qw.QTangoReadAttributeDouble(colors = self.colors, sizes = self.attr_sizes)
        self.error_frequency_widget.setAttributeName('Error frequency', 'Hz')
        self.error_trace_widget = qw.QTangoReadAttributeSpectrum(colors = self.colors, sizes = self.attr_sizes)
        self.error_trace_widget.setAttributeName('Error trace')
#        self.error_trace_widget.fixedSize(fixed=True)
        self.error_trace_widget.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        self.error_trace_widget.spectrum.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        self.error_trace_widget.setMaximumHeight(150)
        self.error_trace_widget.setMinimumHeight(150)

        self.regen_lee_name = qw.QTangoDeviceNameStatus(colors = self.colors, sizes = self.frame_sizes)
        self.regen_lee_name.setAttributeName('Regen LeeLaser')
        self.regen_operation_widget = qw.QTangoCommandSelection('Operation', colors = self.colors, sizes = self.attr_sizes)
        self.regen_operation_widget.addCmdButton('Start', self.start_regen)
        self.regen_operation_widget.addCmdButton('Stop', self.stop_regen)
        self.regen_operation_widget.addCmdButton('Clear', self.clear_regen)
        self.regen_shutter_widget = qw.QTangoCommandSelection('Shutter', colors = self.colors, sizes = self.attr_sizes)
        self.regen_shutter_widget.addCmdButton('Open', self.open_regen_shutter)
        self.regen_shutter_widget.addCmdButton('Close', self.close_regen_shutter)
        self.regen_current_widget = qw.QTangoWriteAttributeDouble(colors = self.colors, sizes = self.attr_sizes)
        self.regen_current_widget.setAttributeName('Regen current', '%')
        self.regen_current_widget.writeValueLineEdit.newValueSignal.connect(self.write_regen_lee_percentcurrent)
        self.regen_temp_widget = qw.QTangoReadAttributeDouble(colors = self.colors, sizes = self.attr_sizes)
        self.regen_temp_widget.setAttributeName('Regen cryo temp', 'degC')

        self.mp_lee_name = qw.QTangoDeviceNameStatus(colors = self.colors, sizes = self.frame_sizes)
        self.mp_lee_name.setAttributeName('MP LeeLaser')
        self.mp_operation_widget = qw.QTangoCommandSelection('Operation', colors = self.colors, sizes = self.attr_sizes)
        self.mp_operation_widget.addCmdButton('Start', self.start_mp)
        self.mp_operation_widget.addCmdButton('Stop', self.stop_mp)
        self.mp_operation_widget.addCmdButton('Clear', self.clear_mp)
        self.mp_shutter_widget = qw.QTangoCommandSelection('Shutter', colors = self.colors, sizes = self.attr_sizes)
        self.mp_shutter_widget.addCmdButton('Open', self.open_mp_shutter)
        self.mp_shutter_widget.addCmdButton('Close', self.close_mp_shutter)
        self.mp_current_widget = qw.QTangoWriteAttributeDouble(colors = self.colors, sizes = self.attr_sizes)
        self.mp_current_widget.setAttributeName('MP current', '%')
        self.mp_current_widget.writeValueLineEdit.newValueSignal.connect(self.write_mp_lee_percentcurrent)
        self.mp_temp_widget = qw.QTangoReadAttributeDouble(colors = self.colors, sizes = self.attr_sizes)
        self.mp_temp_widget.setAttributeName('MP cryo temp', 'degC')

        layout2.addWidget(self.title)
        layout2.addLayout(layoutData)
        layoutData.addLayout(self.layout_attributes)
#        layoutData.addSpacerItem(spacerItemH)
        layoutData.addLayout(self.layoutAttributes2)
        layoutData.addLayout(self.layoutAttributes3)

        self.layout_attributes.addWidget(self.finesse_name)
        self.layout_attributes.addWidget(self.finesse_operation_widget)
        self.layout_attributes.addWidget(self.finesse_shutter_widget)
        self.layout_attributes.addSpacerItem(spacerItemBar)
        self.layout_attributes.addWidget(self.regen_lee_name)
        self.layout_attributes.addWidget(self.regen_operation_widget)
        self.layout_attributes.addWidget(self.regen_shutter_widget)
        self.layout_attributes.addSpacerItem(spacerItemBar)
        self.layout_attributes.addWidget(self.mp_lee_name)
        self.layout_attributes.addWidget(self.mp_operation_widget)
        self.layout_attributes.addWidget(self.mp_shutter_widget)
        self.layout_attributes.addSpacerItem(spacerItemV)

        self.layoutAttributes2.addWidget(self.finesse_power_widget)
        self.layoutAttributes2.addWidget(self.finesse_temp_widget)
        self.layoutAttributes2.addWidget(self.oscillator_power_widget)
        self.layoutAttributes2.addWidget(self.oscillator_peak_width_widget)
        self.layoutAttributes2.addWidget(self.error_frequency_widget)
        self.layoutAttributes2.addSpacerItem(spacerItemBar)
        self.layoutAttributes2.addWidget(self.regen_current_widget)
        self.layoutAttributes2.addWidget(self.regen_temp_widget)
        self.layoutAttributes2.addSpacerItem(spacerItemBar)
        self.layoutAttributes2.addWidget(self.mp_current_widget)
        self.layoutAttributes2.addWidget(self.mp_temp_widget)
        self.layoutAttributes2.addSpacerItem(spacerItemV)
        
        self.layoutAttributes3.addWidget(self.oscillator_spectrum_plot)
        self.layoutAttributes3.addWidget(self.error_trace_widget)
        self.layoutAttributes3.addSpacerItem(spacerItemV)
        

        
        layout1.addWidget(self.sidebar)
        layout1.addLayout(layout2)
        layout0.addLayout(layout1)
#        layout0.addWidget(self.bottombar)

#        self.resize(500,800)
        self.setGeometry(200,100,1200,600)

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