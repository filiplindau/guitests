'''
Created on Mar 26, 2015

@author: Filip Lindau
'''
from PyQt4 import QtGui, QtCore

import time
import sys
import threading
import PyTango as pt


# noinspection PyAttributeOutsideInit
class AttributeEventClass(QtCore.QObject):
    '''This class encapsulates the tango events for an attribute and re-emits
    a Qt signal. The main purpose of this is that the Qt gui obejcts cannot 
    be called from other threads than the gui thread, causing problems with tango events.  
    '''
    attrSignal = QtCore.pyqtSignal(pt.device_attribute.DeviceAttribute)
    attrInfoSignal = QtCore.pyqtSignal(pt.AttributeInfoEx)
    def __init__(self, name, device, eventType = pt.EventType.CHANGE_EVENT, minInterval=0.0, slot=None):
        ''' Init the attribute listener.
         
        name: Attribute tango name
        device: DeviceProxy for the tango device server
        eventType: Type of event (member of PyTango.EventType)
        minInterval: Minimum time in s between pushing QSignals for limiting 
                    the rate of gui redraw. The event rate could be higher.
        slot: Method to send the attrSignal to
        '''
        super(AttributeEventClass, self).__init__()
        self.name = name
        self.device = device
        self.eventType = eventType
        self.minInterval = minInterval
        if slot != None:
            self.attrSignal.connect(slot)

        self.eventId = None
        
        self.lastRead = 0
        
        self.subscribe_event()

        
    def subscribe_event(self):
        self.eventId = self.device.subscribe_event(self.name, self.eventType, self.attr_read, stateless = True)
        
    def unsubscribe_event(self):
        if self.eventId != None:
            self.device.unsubscribe_event(self.eventId)

    def attr_read(self, event):
        if event.err == False:
            t = time.time()
            if (t-self.lastRead) > self.minInterval:
                self.attrSignal.emit(event.attr_value)
                self.lastRead = t
        

    def attr_write(self, wvalue):
        self.device.write_attribute(self.name, wvalue)

    def stopRead(self):
        self.unsubscribe_event()

    def startRead(self):
        self.subscribe_event()

    def getInfo(self):
        try:
            self.attrInfo = self.device.get_attribute_config(self.name)

        except pt.DevFailed, e:
            if e[0].reason == 'API_DeviceTimeOut':
                print 'AttrInfo Timeout'
            else:
                print self.name, '  attrinfo error ', e[0].reason
            self.attrInfo = pt.AttributeInfoEx()
            
        except Exception, e:
            print self.name, ' recovering from attrInfo ', str(e)
            self.attrInfo = pt.AttributeInfoEx()

        return self.attrInfo