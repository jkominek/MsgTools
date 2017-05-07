#!/usr/bin/env python3
"""
Plot message data in scrolling window
"""

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np

import os
srcroot=os.path.abspath(os.path.dirname(os.path.abspath(__file__))+"/..")

import sys
# import the MsgApp baseclass, for messages, and network I/O
sys.path.append(srcroot+"/MsgApp")
from Messaging import Messaging

from datetime import datetime
from datetime import timedelta

start_time = datetime.now()

from collections import namedtuple

# make tuple for line, and have multiple of them in a MsgPlot, as long as their units match and they are from the same message
LineInfo = namedtuple('LineInfo', 'fieldInfo fieldSubindex dataArray timeArray curve ptr1')

def elapsedSeconds():
   dt = datetime.now() - start_time
   seconds = float(dt.days * 24 * 60 * 60 + dt.seconds) + dt.microseconds / 1000000.0
   return seconds

class MsgPlot:
    MAX_LENGTH = 100
    def __init__(self, msgClass, fieldInfo, subindex):
        self.msgClass = msgClass
        self.pause = 0
        self.lineCount = 0
        self.units = fieldInfo.units
        self.lines = []

        yAxisLabel = fieldInfo.units
        xAxisLabel = "time (s)"
        self.plotWidget = pg.PlotWidget(labels={'left':yAxisLabel,'bottom':xAxisLabel})
        self.plotWidget.addLegend()
        self.addPlot(msgClass, fieldInfo, subindex)

        # set up click handler to pause graph
        self.plotWidget.scene().sigMouseClicked.connect(self.mouseClicked)
        
        self.plotWidget.dragEnterEvent = self.dragEnterEvent
        self.plotWidget.dragMoveEvent = self.dragMoveEvent
        self.plotWidget.dropEvent = self.dropEvent
        self.plotWidget.setAcceptDrops(1)
        
    def dragEnterEvent(self, ev):
        # need to accept enter event, or we won't get move event
        ev.accept()

    def dragMoveEvent(self, ev):
        # need to accept move event, or we won't get drop event
        ev.accept()

    def dropEvent(self, ev):
        ev.accept()
        try:
            item = ev.source().currentItem()
            # don't add if it's already there!
            for line in self.lines:
                if item.fieldInfo == line.fieldInfo:
                    return
            if item.fieldInfo.units == self.units and item.msg_class == self.msgClass:
                fieldIndex = 0
                try:
                    fieldIndex = item.index
                except AttributeError:
                    pass
                self.addPlot(item.msg_class, item.fieldInfo, fieldIndex)
        except AttributeError:
            pass

    def addPlot(self, msgClass, fieldInfo, subindex):
        lineName = fieldInfo.name
        try:
            if fieldInfo.count != 1:
                lineName += "["+str(self.fieldSubindex)+"]"
        except AttributeError:
            pass
        dataArray = []
        timeArray = []
        ptr1 = 0
        self.useHeaderTime = 0
        curve = self.plotWidget.plot(timeArray, dataArray, name=lineName, pen=(len(self.lines),3))
        lineInfo = LineInfo(fieldInfo, subindex, dataArray, timeArray, curve, ptr1)
        self.lines.append(lineInfo)
        
    def mouseClicked(self, ev):
        if ev.button() == QtCore.Qt.LeftButton:
            self.pause = not self.pause
        if self.pause:
            print("Paused")
        else:
            print("Not paused")

    def addData(self, msg):
        # TODO what to do for things that can't be numerically expressed?  just ascii strings, i guess?
        for line in self.lines:
            newDataPoint = Messaging.getFloat(msg, line.fieldInfo, line.fieldSubindex)
            try:
                newTime = float(msg.hdr.GetTime()/1000.0)
                if newTime != 0:
                    self.useHeaderTime = 1
                if not self.useHeaderTime:
                    newTime = elapsedSeconds()
            except AttributeError:
                # if header has no time, fallback to PC time.
                newTime = elapsedSeconds()
            
            # add data in the array until MAX_LENGTH is reached, then drop data off start of array
            # such that plot appears to scroll.  The array size is limited to MAX_LENGTH.
            if len(line.dataArray) >= MsgPlot.MAX_LENGTH:
                line.dataArray[:-1] = line.dataArray[1:]  # shift data in the array one sample left
                line.dataArray[-1] = newDataPoint
                line.timeArray[:-1] = line.timeArray[1:]  # shift data in the array one sample left
                line.timeArray[-1] = newTime
            else:
                line.dataArray.append(newDataPoint)
                line.timeArray.append(newTime)

            if not self.pause:
                line.curve.setData(line.timeArray, line.dataArray)
                line.curve.setPos(line.ptr1, 0)

import MsgGui

class MessagePlotGui(MsgGui.MsgGui):
    def __init__(self, argv, parent=None):
        MsgGui.MsgGui.__init__(self, "Message Plot 0.1", argv, [], parent)
        from UnknownMsg import UnknownMsg
        self.unknownMsg = UnknownMsg

        vbox = QVBoxLayout()
        centralWidget = QWidget()
        centralWidget.setLayout(vbox)
        self.setCentralWidget(centralWidget)
        self.msgPlots = {}
        self.RxMsg.connect(self.ProcessMessage)

        if len(sys.argv) < 1:
            sys.stderr.write('Usage: ' + sys.argv[0] + ' msg1=field1[,field2] [msg2=field1,field2,field3]\n')
            sys.exit(1)
        
        for arg in argv[1:]:
            argComponentList = arg.split("=")
            msgName = argComponentList[0]
            fieldNameList = argComponentList[1]

            msgClass = Messaging.MsgClassFromName[msgName]
            
            fieldNames = fieldNameList.split(",")
            firstField = 1
            for fieldName in fieldNames:
                fieldInfo = Messaging.findFieldInfo(msgClass.fields, fieldName)
                if fieldInfo != None:
                    if firstField:
                        plot = MsgPlot(msgClass, fieldInfo, 0)
                        vbox.addWidget(plot.plotWidget)
                        firstField = 0
                        plotListForID = []
                        if msgClass.ID in self.msgPlots:
                            plotListForID = self.msgPlots[msgClass.ID]
                        else:
                            self.msgPlots[msgClass.ID] = plotListForID
                        plotListForID.append(plot)
                    else:
                        plot.addPlot(msgClass, fieldInfo, 0)

    def ProcessMessage(self, msg):
        msg_id = hex(msg.hdr.GetMessageID())

        if msg_id in Messaging.MsgNameFromID:
            msg_name = Messaging.MsgNameFromID[msg_id]
            msgClass = Messaging.MsgClassFromName[msg_name]

        #msg_key = ",".join(self.MsgRoute(msg)) + "," + msg_id
        try:
            if msgClass.ID in self.msgPlots:
                plotListForID = self.msgPlots[msgClass.ID]
                for plot in plotListForID:
                    plot.addData(msg)
        except AttributeError:
            pass

# main starts here
if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = MessagePlotGui(sys.argv)
    gui.show()    
    sys.exit(app.exec_())
