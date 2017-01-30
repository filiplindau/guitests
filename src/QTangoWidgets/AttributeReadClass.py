'''
Created on 27 mar 2015

@author: Filip Lindau
'''
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
    def __init__(self, name, device, minInterval=0.0, slot=None, eventType = pt.EventType.CHANGE_EVENT, getInfo = False, rateLimit = False):
        super(AttributeClass, self).__init__()
        self.name = name
        self.device = device
        self.interval = minInterval
        self.getInfoFlag = getInfo

        if slot != None:
            self.attrSignal.connect(slot)

        self.lastRead = 0
        self.eventType = eventType
        self.eventId = None
        self.attr = None
        self.attrLock = threading.Lock()
        self.signalPending = False
        self.rateLimit = rateLimit

        if eventType == None:
            self.readThread = threading.Thread(name = self.name, target = self.attr_read)
            self.stopThread = False
            self.startRead()
        else:
            self.subscribe_event()

    def subscribe_event(self):
        self.eventId = self.device.subscribe_event(self.name, self.eventType, self.attr_read_event, stateless = True)

    def unsubscribe_event(self):
        if self.eventId != None:
            self.device.unsubscribe_event(self.eventId)

    def attr_read_event(self, event):
        if event.err == False:
            t = time.time()
            if (t-self.lastRead) > self.interval:
                if self.rateLimit == True:
                    with self.attrLock:
                        self.attrSignal.emit(event.attr_value)
                else:
                    self.attrSignal.emit(event.attr_value)
                self.lastRead = t



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
                        print 'signal emitted', self.attr.value.shape
                        # Read only once if interval = None:
                        if self.interval == None:
                            self.stopThread = True
                            self.interval = 0.0
                    except pt.DevFailed, e:
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
        print self.name, ' waiting for final reply'
        finalTimeout = 1.0  # Wait max 1 s
        finalStartTime = time.time()
        finalTimeoutFlag = False
        while replyReady == False and finalTimeoutFlag == False:
            try:
                self.attr = self.device.read_attribute_reply(id)
                replyReady = True
                self.attrSignal.emit(self.attr)
            except pt.DevFailed, e:
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
            if time.time()-finalStartTime > finalTimeout:
                finalTimeoutFlag = True
        if finalTimeoutFlag == False:
            print self.name, '... Thread stopped'
        else:
            print self.name, '... Thread timed out'

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