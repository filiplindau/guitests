"""
Created on 03 Sep 2018

@author: Filip Lindau
"""

# -*- coding:utf-8 -*-
from PyQt4 import QtGui, QtCore

import time
import sys


# noinspection PyAttributeOutsideInit
class TangoDeviceClient(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        #        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.time_vector = None
        self.errorSampleTime = None
        self.xData = None
        self.xDataTemp = None

        self.setupLayout()

        splash.showMessage('         Initializing devices', alignment=QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
        app.processEvents()

        self.emission = [False, False]

        t0 = time.clock()
        self.devices = dict()
        self.devices['spectrometer'] = pt.DeviceProxy('gunlaser/oscillator/spectrometer')
        self.devices['finesse'] = pt.DeviceProxy('gunlaser/oscillator/finesse')
        self.devices['redpitaya0'] = pt.DeviceProxy('gunlaser/devices/redpitaya1')
        self.devices['patara'] = pt.DeviceProxy('gunlaser/devices/patara')
        self.devices['energy'] = pt.DeviceProxy('gunlaser/thg/energy')
        self.devices['redpitaya4'] = pt.DeviceProxy('gunlaser/devices/redpitaya4')
        self.devices['halcyon'] = pt.DeviceProxy('gunlaser/oscillator/halcyon_raspberry')
        self.devices['regenTemp'] = pt.DeviceProxy('gunlaser/regen/temperature')
        self.devices['mpTemp'] = pt.DeviceProxy('gunlaser/mp/temperature')
        self.devices['kmpc'] = pt.DeviceProxy('gunlaser/regen/kmpc')
        print time.clock() - t0, ' s'

        splash.showMessage('         Reading startup attributes',
                           alignment=QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
        app.processEvents()

        self.guiLock = threading.Lock()
        self.attributes = dict()
        self.attributes['finessePower'] = AttributeClass('power', self.devices['finesse'], 0.3)
        self.attributes['finesseTemperature'] = AttributeClass('lasertemperature', self.devices['finesse'], 0.3)
        self.attributes['finesseState'] = AttributeClass('state', self.devices['finesse'], 0.3)
        self.attributes['finesseShutterState'] = AttributeClass('shutterstate', self.devices['finesse'], 0.3)
        self.attributes['finesseOperationState'] = AttributeClass('laseroperationstate', self.devices['finesse'], 0.3)
        self.attributes['peakwidth'] = AttributeClass('peakwidth', self.devices['spectrometer'], 0.3)
        self.attributes['peakWavelength'] = AttributeClass('peakwavelength', self.devices['spectrometer'], 0.3)
        self.attributes['oscPower'] = AttributeClass('measurementdata1', self.devices['redpitaya0'], 0.3)
        self.attributes['wavelengths'] = AttributeClass('wavelengthsROI', self.devices['spectrometer'], None)
        self.attributes['spectrum'] = AttributeClass('spectrumROI', self.devices['spectrometer'], 0.3)
        self.attributes['halcyonState'] = AttributeClass('state', self.devices['halcyon'], 0.3)
        self.attributes['halcyonPiezoVoltage'] = AttributeClass('piezovoltage', self.devices['halcyon'], 0.3)
        self.attributes['halcyonErrorFrequency'] = AttributeClass('errorfrequency', self.devices['halcyon'], 0.3)
        self.attributes['halcyonJitter'] = AttributeClass('jitter', self.devices['halcyon'], 0.3)
        self.attributes['picomotorPosition'] = AttributeClass('picomotorposition', self.devices['halcyon'], 0.3)
        self.attributes['picomotorFollow'] = AttributeClass('picomotorfollow', self.devices['halcyon'], 0.3)
        self.attributes['halcyon_error_trace'] = AttributeClass('errortrace', self.devices['halcyon'], 0.3)
        self.attributes['halcyon_sampletime'] = AttributeClass('sampletime', self.devices['halcyon'], None)

        self.attributes['finessePower'].attrSignal.connect(self.read_finesse_power)
        self.attributes['finesseTemperature'].attrSignal.connect(self.read_finesse_temperature)
        self.attributes['finesseState'].attrSignal.connect(self.read_finesse_state)
        self.attributes['finesseShutterState'].attrSignal.connect(self.read_finesse_shutter_state)
        self.attributes['finesseOperationState'].attrSignal.connect(self.read_finesse_operation_state)
        self.attributes['peakwidth'].attrSignal.connect(self.read_peak_width)
        self.attributes['peakWavelength'].attrSignal.connect(self.read_peak_wavelength)
        self.attributes['oscPower'].attrSignal.connect(self.read_oscillator_power)
        self.attributes['spectrum'].attrSignal.connect(self.read_spectrum)
        self.attributes['wavelengths'].attrSignal.connect(self.read_wavelengths)
        self.attributes['halcyonState'].attrSignal.connect(self.read_halcyon_state)
        self.attributes['halcyonPiezoVoltage'].attrSignal.connect(self.read_piezo_voltage)
        self.attributes['halcyonErrorFrequency'].attrSignal.connect(self.read_error_frequency)
        self.attributes['halcyonJitter'].attrSignal.connect(self.read_jitter)
        self.attributes['picomotorPosition'].attrSignal.connect(self.read_picomotor)
        self.attributes['picomotorFollow'].attrSignal.connect(self.read_track_picomotor)
        self.attributes['halcyon_sampletime'].attrSignal.connect(self.read_halcyon_sampletime)
        self.attributes['halcyon_error_trace'].attrSignal.connect(self.read_error_trace)

        self.attributes['pataraState'] = AttributeClass('state', self.devices['patara'], 0.3)
        self.attributes['pataraShutterState'] = AttributeClass('shutter', self.devices['patara'], 0.3)
        self.attributes['pataraEmissionState'] = AttributeClass('emission', self.devices['patara'], 0.3)
        self.attributes['pataraPower'] = AttributeClass('measurementdata2', self.devices['redpitaya4'], 0.3)
        self.attributes['pataraCurrent'] = AttributeClass('current', self.devices['patara'], 1.0)
        self.attributes['regenCrystalTemp'] = AttributeClass('temperature', self.devices['regenTemp'], 0.3)
        self.attributes['mpCrystalTemp'] = AttributeClass('temperature', self.devices['mpTemp'], 1.0)
        self.attributes['kmpcState'] = AttributeClass('state', self.devices['kmpc'], 1.0)

        self.attributes['pataraState'].attrSignal.connect(self.read_patara_state)
        self.attributes['pataraShutterState'].attrSignal.connect(self.read_patara_shutter_state)
        self.attributes['pataraEmissionState'].attrSignal.connect(self.read_patara_emission_state)
        self.attributes['pataraPower'].attrSignal.connect(self.read_patara_power)
        self.attributes['pataraCurrent'].attrSignal.connect(self.read_patara_current)
        self.attributes['regenCrystalTemp'].attrSignal.connect(self.read_pegen_crystal_temp)
        self.attributes['mpCrystalTemp'].attrSignal.connect(self.read_mp_crystal_temp)
        self.attributes['kmpcState'].attrSignal.connect(self.read_kmpc_state)

        self.attributes['irEnergy'] = AttributeClass('ir_energy', self.devices['energy'], 0.3)
        self.attributes['irEnergy'].attrSignal.connect(self.read_ir_energy)
        self.attributes['uvEnergy'] = AttributeClass('uv_energy', self.devices['energy'], 0.3)
        self.attributes['uvEnergy'].attrSignal.connect(self.read_uv_energy)
        self.attributes['uvPercent'] = AttributeClass('uv_percent', self.devices['energy'], 1.0)
        self.attributes['uvPercent'].attrSignal.connect(self.read_uv_percent)
        self.attributes['irPercent'] = AttributeClass('ir_percent', self.devices['energy'], 1.0)
        self.attributes['irPercent'].attrSignal.connect(self.read_ir_percent)

    def read_finesse_state(self, data):
        self.finesse_name.setStatus(data)

    def read_finesse_shutter_state(self, data):
        if data.value == "open":
            data.value = "OPEN"
        else:
            data.value = "CLOSED"
        self.finesse_shutter_widget.setStatus(data)

    def read_finesse_operation_state(self, data):
        if data.value == "running":
            data.value = "ON"
            self.emission[0] = True
        else:
            self.emission[0] = False
        self.finesse_operation_widget.setStatus(data)

    def read_finesse_power(self, data):
        self.finesse_power_widget.setAttributeValue(data)

    def write_finesse_power(self):
        w = self.finesse_power_widget.getWriteValue()
        self.attributes['finesse_power'].attr_write(w)

    def read_finesse_temperature(self, data):
        self.finesse_temp_widget.setAttributeValue(data)

    def read_patara_state(self, data):
        self.patara_name.setStatus(data)

    def read_patara_shutter_state(self, data):
        if data.value is False:
            data.value = "CLOSED"
        else:
            data.value = "OPEN"
        self.patara_shutter_widget.setStatus(data)

    def read_patara_emission_state(self, data):
        if data.value is False:
            data.value = "OFF"
            self.emission[1] = False
        else:
            data.value = "ON"
            self.emission[1] = True
        self.patara_operation_widget.setStatus(data)

    def read_patara_power(self, data):
        data.value = data.value * 1e3
        self.patara_energy_widget.setAttributeValue(data)

    def read_patara_current(self, data):
        self.patara_current_widget.setAttributeValue(data)

    def write_patara_current(self):
        w = self.patara_current_widget.getWriteValue()
        self.attributes['pataraCurrent'].attr_write(w)

    def read_pegen_crystal_temp(self, data):
        self.regen_temp_widget.setAttributeValue(data)

    def read_mp_crystal_temp(self, data):
        self.mp_temp_widget.setAttributeValue(data)

    def read_kmpc_state(self, data):
        self.kmpc_widget.setStatus(data)

    def read_oscillator_power(self, data):
        data.value = data.value
        self.oscillator_power_widget.setAttributeValue(data)

    def read_peak_width(self, data):
        self.oscillator_peak_width_widget.setAttributeValue(data)

    def read_peak_wavelength(self, data):
        self.oscillator_peak_wavelength_widget.setAttributeValue(data)

    def read_wavelengths(self, data):
        try:
            print 'time vector read: ', data.value.shape[0]
        except:
            pass
        self.time_vector = data.value

    def read_spectrum(self, data):
        if self.time_vector is None:
            print 'No time vector'
        else:
            self.oscillator_spectrum_plot.setSpectrum(xData=self.time_vector, yData=data)
            self.oscillator_spectrum_plot.update()

    def read_halcyon_state(self, data):
        self.halcyon_name.setStatus(data)

    def read_piezo_voltage(self, data):
        self.piezo_voltage_widget.setAttributeValue(data)

    def read_error_frequency(self, data):
        self.error_frequency_widget.setAttributeValue(data)

    def read_jitter(self, data):
        try:
            data.value = data.value * 1e15
        except TypeError:
            data.value = 0.0
            data.quality = pt.AttrQuality.ATTR_INVALID
        self.jitter_widget.setAttributeValue(data)

    def read_picomotor(self, data):
        self.picomotor_widget.setAttributeValue(data)

    def write_picomotor(self):
        w = self.picomotor_widget.getWriteValue()
        self.attributes['picomotorPosition'].attr_write(w)

    def read_track_picomotor(self, data):
        self.picomotor_track_widget.setStatus(data)

    def track_picomotor_true(self):
        self.attributes['picomotorFollow'].attr_write(True)

    def track_picomotor_false(self):
        self.attributes['picomotorFollow'].attr_write(False)

    def read_ir_energy(self, data):
        data.value = data.value
        self.ir_energy_widget.setAttributeValue(data)

    def read_uv_energy(self, data):
        data.value = data.value
        self.uv_energy_widget.setAttributeValue(data)

    def read_uv_percent(self, data):
        data.value = data.value
        self.uv_percent_widget.setAttributeValue(data)

    def write_uv_percent(self):
        w = self.uv_percent_widget.getWriteValue()
        self.attributes['uvPercent'].attr_write(w)

    def read_ir_percent(self, data):
        data.value = data.value
        # self.uv_percent_widget.setAttributeValue(data)

    def read_error_trace(self, data):
        if self.error_sampletime is None:
            print 'No time vector'
        else:
            timevector = np.linspace(0, data.value.shape[0] * self.error_sampletime, data.value.shape[0])
            self.error_trace_widget.setSpectrum(xData=timevector, yData=data)
            self.error_trace_widget.update()

    def read_halcyon_sampletime(self, data):
        try:
            print 'Sample time read: ', data.value
            self.error_sampletime = data.value
        except:
            pass

    def closeEvent(self, event):
        for a in self.attributes.itervalues():
            print 'Stopping', a.name
            a.stop_read()
        for a in self.attributes.itervalues():
            a.readThread.join()
        event.accept()

    # Commands
    def start_finesse(self):
        self.devices['finesse'].command_inout('on')

    def stop_finesse(self):
        self.devices['finesse'].command_inout('off')

    def init_finesse(self):
        self.devices['finesse'].command_inout('init')

    def open_finesse_shutter(self):
        self.devices['finesse'].command_inout('open')

    def close_finesse_shutter(self):
        self.devices['finesse'].command_inout('close')

    def start_patara(self):
        self.devices['patara'].command_inout('start')

    def stop_patara(self):
        self.devices['patara'].command_inout('stop')

    def clear_patara(self):
        self.devices['patara'].command_inout('clear_fault')

    def init_patara(self):
        self.devices['patara'].command_inout('init')

    def open_patara_shutter(self):
        self.devices['patara'].command_inout('open')

    def close_patara_shutter(self):
        self.devices['patara'].command_inout('close')

    def on_kmpc(self):
        self.devices['kmpc'].command_inout('on')

    def off_kmpc(self):
        self.devices['kmpc'].command_inout('off')

    def init_halcyon(self):
        self.devices['halcyon'].command_inout('init')

    def setupLayout(self):
        s = 'QWidget{background-color: #000000; }'
        self.setStyleSheet(s)

        self.title_sizes = qw.QTangoSizes()
        self.title_sizes.barHeight = 30
        self.title_sizes.barWidth = 18
        self.title_sizes.readAttributeWidth = 400
        self.title_sizes.writeAttributeWidth = 150
        self.title_sizes.fontStretch = 80
        self.title_sizes.fontType = 'Arial'

        self.frame_sizes = qw.QTangoSizes()
        self.frame_sizes.barHeight = 40
        self.frame_sizes.barWidth = 35
        self.frame_sizes.readAttributeWidth = 400
        self.frame_sizes.writeAttributeWidth = 400
        self.frame_sizes.fontStretch = 80
        self.frame_sizes.fontType = 'Segoe UI'
        #        self.frame_sizes.fontType = 'Trebuchet MS'

        self.attr_sizes = qw.QTangoSizes()
        self.attr_sizes.barHeight = 22
        self.attr_sizes.barWidth = 22
        self.attr_sizes.readAttributeWidth = 300
        self.attr_sizes.readAttributeHeight = 300
        self.attr_sizes.writeAttributeWidth = 300
        self.attr_sizes.fontStretch = 80
        self.attr_sizes.fontWeight = 1
        self.attr_sizes.fontType = 'Arial'
        # self.attr_sizes.fontType = 'Segoe UI'

        cat_sizes = qw.QTangoSizes()
        cat_sizes.barHeight = 20
        cat_sizes.barWidth = 2
        cat_sizes.readAttributeWidth = 100
        cat_sizes.readAttributeHeight = 250
        cat_sizes.writeAttributeWidth = 299
        cat_sizes.fontStretch = 80
        cat_sizes.fontType = 'Arial'
        #        self.attr_sizes.fontType = 'Trebuchet MS'
        cat_colors = qw.QTangoColors()
        cat_colors.primaryColor0 = cat_colors.secondaryColor0

        self.colors = qw.QTangoColors()

        #######################
        # Title widgets
        #
        self.title = qw.QTangoTitleBar('Gunlaser control', self.title_sizes)
        self.setWindowTitle('Gunlaser control')
        self.sidebar = qw.QTangoSideBar(colors=self.colors, sizes=self.frame_sizes)
        self.bottombar = qw.QTangoHorizontalBar()

        #######################
        # Finesse widgets
        #
        self.finesse_name = qw.QTangoCommandSelection("Finesse", colors=self.colors, sizes=self.attr_sizes)
        self.finesse_name.addCmdButton('Init', self.init_finesse)

        self.finesse_shutter_widget = qw.QTangoCommandSelection('Shutter', colors=self.colors, sizes=self.attr_sizes)
        self.finesse_shutter_widget.addCmdButton('Open', self.open_finesse_shutter)
        self.finesse_shutter_widget.addCmdButton('Close', self.close_finesse_shutter)

        self.finesse_operation_widget = qw.QTangoCommandSelection('Operation', colors=self.colors,
                                                                  sizes=self.attr_sizes)
        self.finesse_operation_widget.addCmdButton('Start', self.start_finesse)
        self.finesse_operation_widget.addCmdButton('Stop', self.stop_finesse)

        self.finesse_power_widget = qw.QTangoWriteAttributeDouble(colors=self.colors, sizes=self.attr_sizes)
        self.finesse_power_widget.setAttributeName('Finesse power', 'W')
        self.finesse_power_widget.writeValueLineEdit.newValueSignal.connect(self.write_finesse_power)

        self.finesse_temp_widget = qw.QTangoReadAttributeDouble(colors=self.colors, sizes=self.attr_sizes)
        self.finesse_temp_widget.setAttributeName('Finesse temp', 'degC')

        ######################
        # Oscillator widgets
        #
        self.oscillator_power_widget = qw.QTangoReadAttributeDouble(colors=self.colors, sizes=self.attr_sizes)
        self.oscillator_power_widget.setAttributeName('Oscillator power', 'W')
        self.oscillator_power_widget.setPrefix('m')
        self.oscillator_peak_width_widget = qw.QTangoReadAttributeDouble(colors=self.colors, sizes=self.attr_sizes)
        self.oscillator_peak_width_widget.setAttributeName('Width FWHM', 'nm')
        self.oscillator_peak_wavelength_widget = qw.QTangoReadAttributeDouble(colors=self.colors, sizes=self.attr_sizes)
        self.oscillator_peak_wavelength_widget.setAttributeName('Peak', 'nm')
        self.oscillator_spectrum_plot = qw.QTangoReadAttributeSpectrum(colors=self.colors, sizes=self.attr_sizes)
        self.oscillator_spectrum_plot.setAttributeName('Oscillator spectrum')
        self.oscillator_spectrum_plot.setXRange(700, 900)
        self.oscillator_spectrum_plot.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)

        self.regen_temp_widget = qw.QTangoReadAttributeDouble(colors=self.colors, sizes=self.attr_sizes)
        self.regen_temp_widget.setAttributeName('Regen cryo temp', 'degC')

        ######################
        # Halcyon widgets
        self.halcyon_name = qw.QTangoCommandSelection('Halcyon', colors=self.colors, sizes=self.attr_sizes)
        self.halcyon_name.addCmdButton('Init', self.init_halcyon)

        self.picomotor_track_widget = qw.QTangoCommandSelection('Picomotor track', colors=self.colors, sizes=self.attr_sizes)
        self.picomotor_track_widget.addCmdButton('True', self.track_picomotor_true)
        self.picomotor_track_widget.addCmdButton('False', self.track_picomotor_false)

        self.picomotor_widget = qw.QTangoWriteAttributeDouble(colors=self.colors, sizes=self.attr_sizes)
        self.picomotor_widget.setAttributeName('Picomotor', 'steps')
        self.picomotor_widget.writeValueLineEdit.newValueSignal.connect(self.write_picomotor)

        self.error_frequency_widget = qw.QTangoReadAttributeDouble(colors=self.colors, sizes=self.attr_sizes)
        self.error_frequency_widget.setAttributeName('Error frequency', 'Hz')

        self.error_trace_widget = qw.QTangoReadAttributeSpectrum(colors=self.colors, sizes=self.attr_sizes)
        self.error_trace_widget.setAttributeName('Error trace')
        self.error_trace_widget.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        self.error_trace_widget.spectrum.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        self.error_trace_widget.setMaximumHeight(150)
        self.error_trace_widget.setMinimumHeight(150)

        self.jitter_widget = qw.QTangoReadAttributeDouble(colors=self.colors, sizes=self.attr_sizes)
        self.jitter_widget.setAttributeName('Jitter', 'fs')

        self.piezo_voltage_widget = qw.QTangoReadAttributeDouble(colors=self.colors, sizes=self.attr_sizes)
        self.piezo_voltage_widget.setAttributeName('Piezo', '%')

        ######################
        # Patara widgets
        #
        self.patara_name = qw.QTangoCommandSelection("Patara", colors=self.colors, sizes=self.attr_sizes)
        self.patara_name.addCmdButton("Init", self.init_patara)
        self.patara_name.addCmdButton("Clear", self.clear_patara)
        self.patara_shutter_widget = qw.QTangoCommandSelection('Shutter', colors=self.colors, sizes=self.attr_sizes)
        self.patara_shutter_widget.addCmdButton('Open', self.open_patara_shutter)
        self.patara_shutter_widget.addCmdButton('Close', self.close_patara_shutter)
        self.patara_operation_widget = qw.QTangoCommandSelection('Emission', colors=self.colors, sizes=self.attr_sizes)
        self.patara_operation_widget.addCmdButton('Start', self.start_patara)
        self.patara_operation_widget.addCmdButton('Stop', self.stop_patara)

        self.patara_energy_widget = qw.QTangoReadAttributeDouble(colors=self.colors, sizes=self.attr_sizes)
        self.patara_energy_widget.setAttributeName('Patara Energy', 'mJ')

        self.patara_current_widget = qw.QTangoWriteAttributeDouble(colors=self.colors, sizes=self.attr_sizes)
        self.patara_current_widget.setAttributeName('Patara current', 'A')
        self.patara_current_widget.writeValueLineEdit.newValueSignal.connect(self.write_patara_current)

        self.kmpc_widget = qw.QTangoCommandSelection("KMPC", colors=self.colors, sizes=self.attr_sizes)
        self.kmpc_widget.addCmdButton("On", self.on_kmpc)
        self.kmpc_widget.addCmdButton("Off", self.off_kmpc)

        ######################
        # Cryo widgets
        #
        self.regen_temp_widget = qw.QTangoReadAttributeDouble(colors=self.colors, sizes=self.attr_sizes)
        self.regen_temp_widget.setAttributeName('Regen crystal', 'degC')

        self.mp_temp_widget = qw.QTangoReadAttributeDouble(colors=self.colors, sizes=self.attr_sizes)
        self.mp_temp_widget.setAttributeName('MP crystal', 'degC')

        ######################
        # energy widgets
        #
        self.ir_energy_widget = qw.QTangoReadAttributeDouble(colors=self.colors, sizes=self.attr_sizes)
        self.ir_energy_widget.setAttributeName('IR energy', 'mJ')

        self.uv_energy_widget = qw.QTangoReadAttributeDouble(colors=self.colors, sizes=self.attr_sizes)
        self.uv_energy_widget.setAttributeName('UV energy', 'uJ')

        self.uv_percent_widget = qw.QTangoWriteAttributeDouble(colors=self.colors, sizes=self.attr_sizes)
        self.uv_percent_widget.setAttributeName('UV energy', '%')
        self.uv_percent_widget.writeValueLineEdit.newValueSignal.connect(self.write_uv_percent)

        #######################
        # Pump lasers title
        #
        self.layout_attributes_oscillator = QtGui.QVBoxLayout()
        self.layout_attributes_oscillator.setMargin(0)
        self.layout_attributes_oscillator.setSpacing(self.attr_sizes.barHeight / 2)
        self.layout_attributes_oscillator.addWidget(self.finesse_name)
        self.layout_attributes_oscillator.addWidget(self.finesse_operation_widget)
        self.layout_attributes_oscillator.addWidget(self.finesse_shutter_widget)
        self.layout_attributes_oscillator.addWidget(self.finesse_power_widget)
        self.layout_attributes_oscillator.addWidget(self.finesse_temp_widget)
        self.layout_attributes_oscillator.addSpacerItem(QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum,
                                                                          QtGui.QSizePolicy.Minimum))
        self.layout_attributes_oscillator.addWidget(self.oscillator_power_widget)
        self.layout_attributes_oscillator.addWidget(self.oscillator_peak_width_widget)
        self.layout_attributes_oscillator.addWidget(self.oscillator_peak_wavelength_widget)
        self.layout_attributes_oscillator.addWidget(self.oscillator_spectrum_plot)

        self.layout_attributes_halcyon = QtGui.QVBoxLayout()
        self.layout_attributes_halcyon.setMargin(0)
        self.layout_attributes_halcyon.setSpacing(self.attr_sizes.barHeight / 2)
        self.layout_attributes_halcyon.addWidget(self.halcyon_name)
        self.layout_attributes_halcyon.addWidget(self.picomotor_track_widget)
        self.layout_attributes_halcyon.addWidget(self.picomotor_widget)
        self.layout_attributes_halcyon.addWidget(self.error_frequency_widget)
        self.layout_attributes_halcyon.addWidget(self.jitter_widget)
        self.layout_attributes_halcyon.addWidget(self.piezo_voltage_widget)
        self.layout_attributes_halcyon.addWidget(self.error_trace_widget)
        self.layout_attributes_halcyon.addSpacerItem(QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum,
                                                                       QtGui.QSizePolicy.Expanding))
        self.layout_attributes_halcyon.addWidget(self.regen_temp_widget)
        self.layout_attributes_halcyon.addWidget(self.mp_temp_widget)

        self.layout_attributes_amp = QtGui.QVBoxLayout()
        self.layout_attributes_amp.setMargin(0)
        self.layout_attributes_amp.setSpacing(self.attr_sizes.barHeight / 2)
        self.layout_attributes_amp.addWidget(self.patara_name)
        self.layout_attributes_amp.addWidget(self.patara_operation_widget)
        self.layout_attributes_amp.addWidget(self.patara_shutter_widget)
        self.layout_attributes_amp.addWidget(self.patara_current_widget)
        self.layout_attributes_amp.addWidget(self.patara_energy_widget)
        self.layout_attributes_amp.addSpacerItem(QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum,
                                                                   QtGui.QSizePolicy.Minimum))
        self.layout_attributes_amp.addWidget(self.kmpc_widget)
        self.layout_attributes_amp.addSpacerItem(QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum,
                                                                   QtGui.QSizePolicy.Expanding))
        self.layout_attributes_amp.addWidget(self.ir_energy_widget)
        self.layout_attributes_amp.addWidget(self.uv_percent_widget)
        self.layout_attributes_amp.addWidget(self.uv_energy_widget)

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
        spacerItemV = QtGui.QSpacerItem(20, 5, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.MinimumExpanding)
        spacerItemBar = QtGui.QSpacerItem(self.frame_sizes.barWidth, self.frame_sizes.barHeight + 8,
                                          QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        spacerItemH = QtGui.QSpacerItem(20, 5, QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Minimum)

        layout_data = QtGui.QVBoxLayout()
        layout_data.setMargin(self.attr_sizes.barHeight / 2)
        layout_data.setSpacing(self.attr_sizes.barHeight * 1)
        layout_data.setContentsMargins(20, 0, 20, 20)

        layout_content = QtGui.QHBoxLayout()
        layout_content.setMargin(self.attr_sizes.barHeight / 2)
        layout_content.setSpacing(self.attr_sizes.barHeight * 2)
        layout_content.setContentsMargins(20, 0, 20, 20)
        layout_content.addLayout(self.layout_attributes_oscillator)
        layout_content.addSpacerItem(QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Expanding,
                                                       QtGui.QSizePolicy.Expanding))
        layout_content.addLayout(self.layout_attributes_halcyon)
        layout_content.addSpacerItem(QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum))
        layout_content.addLayout(self.layout_attributes_amp)
        layout_data.addLayout(layout_content)

        layout2.addWidget(self.title)
        layout2.addSpacerItem(QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum))
        layout2.addLayout(layout_data)

        layout_data.addSpacerItem(QtGui.QSpacerItem(20, 20, QtGui.QSizePolicy.Minimum,
                                                    QtGui.QSizePolicy.Expanding))

        layout1.addLayout(layout2)
        layout0.addLayout(layout1)
        # self.showFullScreen()
        self.setGeometry(100, 100, 1200, 900)

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
