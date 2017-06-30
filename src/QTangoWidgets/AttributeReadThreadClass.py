"""
Created on 14 aug 2014

@author: Filip
"""
# -*- coding:utf-8 -*-

from PyQt4 import QtGui, QtCore

import time
import sys
import threading
import PyTango as pt


# noinspection PyAttributeOutsideInit
class AttributeClass(QtCore.QObject):
    attrSignal = QtCore.pyqtSignal(pt.device_attribute.DeviceAttribute)
    attrInfoSignal = QtCore.pyqtSignal(pt.AttributeInfoEx)

    def __init__(self, name, device, interval, slot=None, getInfo=False):
        super(AttributeClass, self).__init__()
        self.name = name
        self.device = device
        self.interval = interval
        self.get_info_flag = getInfo
        self.pause_read_flag = False

        if slot is not None:
            self.attrSignal.connect(slot)

        self.last_read_time = time.time()
        self.attr = None
        self.attr_info = None
        self.read_thread = threading.Thread(name=self.name, target=self.attr_read)
        self.stop_thread_flag = False

        self.start_read()

    def attr_read(self):
        reply_ready = True
        while self.stop_thread_flag is False:
            if self.pause_read_flag is True:
                time.sleep(0.1)
            else:
                if self.get_info_flag is True:
                    self.get_info_flag = False
                    try:
                        self.attr_info = self.device.get_attribute_config(self.name)
                        self.attrInfoSignal.emit(self.attr_info)

                    except pt.DevFailed, e:
                        if e[0].reason == 'API_DeviceTimeOut':
                            print 'AttrInfo Timeout'
                        else:
                            print self.name, '  attrinfo error ', e[0].reason
                        self.attr_info = pt.AttributeInfoEx()
                        self.attrInfoSignal.emit(self.attr_info)
                    except Exception, e:
                        print self.name, ' recovering from attrInfo ', str(e)
                        self.attr_info = pt.AttributeInfoEx()
                        self.attrInfoSignal.emit(self.attr_info)

                t = time.time()

                if t-self.last_read_time > self.interval:
                    self.last_read_time = t
                    try:
                        reply_id = self.device.read_attribute_asynch(self.name)

                        reply_ready = False
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

                    while reply_ready is False and self.stop_thread_flag is False:
                        try:
                            self.attr = self.device.read_attribute_reply(reply_id)
                            reply_ready = True
                            self.attrSignal.emit(self.attr)
                            # Read only once if interval = None:
                            if self.interval is None:
                                self.stop_thread_flag = True
                                self.interval = 0.0
                        except pt.DevFailed, e:
                            if e[0].reason == 'API_AsynReplyNotArrived':
                                time.sleep(0.1)
                            else:
                                reply_ready = True
                                print 'Error reply ', self.name, str(e)
                                self.attr = pt.DeviceAttribute()
                                self.attr.quality = pt.AttrQuality.ATTR_INVALID
                                self.attr.value = None
                                self.attr.w_value = None
                                self.attrSignal.emit(self.attr)

                if self.interval is not None:
                    time.sleep(self.interval)
                else:
                    time.sleep(1)
        print self.name, ' waiting for final reply'
        final_timeout = 1.0  # Wait max 1 s
        final_start_time = time.time()
        final_timeout_flag = False
        while reply_ready is False and final_timeout_flag is False:
            try:
                self.attr = self.device.read_attribute_reply(reply_id)
                reply_ready = True
                self.attrSignal.emit(self.attr)
            except Exception, e:
                if e[0].reason == 'API_AsynReplyNotArrived':
                    time.sleep(0.1)
                else:
                    reply_ready = True
                    print 'Error reply ', self.name, str(e)
                    self.attr = pt.DeviceAttribute()
                    self.attr.quality = pt.AttrQuality.ATTR_INVALID
                    self.attr.value = None
                    self.attr.w_value = None
                    self.attrSignal.emit(self.attr)
            if time.time()-final_start_time > final_timeout:
                final_timeout_flag = True
        if final_timeout_flag is False:
            print self.name, '... Thread stopped'
        else:
            print self.name, '... Thread timed out'

    def attr_write(self, wvalue):
        self.device.write_attribute(self.name, wvalue)

    def stop_read(self):
        """
        Stop the tango attribute reading thread
        :return:
        """
        self.stop_thread_flag = True

    def stopRead(self):
        # For compatiblity
        self.stop_thread_flag = True

    def start_read(self):
        """
        Start the tango attribute reading thread. First stop the old thread if it was running.
        :return:
        """
        self.stop_read()
        if self.read_thread.is_alive() is True:
            self.read_thread.join(3.0)
        self.stop_thread_flag = False
        self.pause_read_flag = False
        self.read_thread.start()

    def pause_read(self):
        """
        Signal that the read thread should pause. The thread is still running, but tango
        calls are paused.
        :return:
        """
        self.pause_read_flag = True

    def unpause_read(self):
        """
        Signal that the read thread should unpause.
        :return:
        """
        self.pause_read_flag = False

    def init_retrieve_attribute_info(self):
        """
        Init retrieval of attribute info from the tango attribute object
        :return:
        """
        self.get_info_flag = True

    def get_attr_info(self):
        """
        Get the tango attribute info.
        :return: Tango attribute info AttributeInfoEx if retrieved, otherwise return False
        """
        if self.attr_info is not None:
            return self.attr_info
        else:
            return False
