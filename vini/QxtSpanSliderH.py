# The MIT License (MIT)

# Copyright (c) 2011-2014 Marvin Killing

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from PyQt5.QtWidgets import (QApplication,
                            QAbstractSlider, QSlider,
                            QStyle, QStylePainter, QStyleOptionSlider)
from PyQt5.QtGui import QPalette, QLinearGradient, QPen, QColor
from PyQt5.QtCore import (Qt, 
                         QRect, QRectF, QPoint,
                         pyqtSignal as Signal, pyqtProperty as Property)
#qtpy can also be used
#from qtpy.QtWidgets import (QApplication,
#                            QAbstractSlider, QSlider,
#                            QStyle, QStylePainter, QStyleOptionSlider)
#from qtpy.QtGui import QPalette, QLinearGradient, QPen, QColor
#from qtpy.QtCore import (Qt, 
#                         QRect, QRectF, QPoint,
#                         Signal, Property)

def clamp(v, lower, upper):
    return min(upper, max(lower, v))

class QxtSpanSliderH(QSlider):
    NoHandle = None
    LowerHandle = 1
    UpperHandle = 2
    
    FreeMovement = None
    NoCrossing = 1
    NoOverlapping = 2
    
    spanChanged = Signal(int, int)
    lowerValueChanged = Signal(int)
    upperValueChanged = Signal(int)
    lowerPositionChanged = Signal(int)
    upperPositionChanged = Signal(int)
    sliderPressed = Signal(object)

    def __init__(self, parent = None):
        QSlider.__init__(self, Qt.Horizontal, parent)
        self.rangeChanged.connect(self.updateRange)
        self.sliderReleased.connect(self.movePressedHandle)

        self.lower = 0
        self.upper = 0
        self.lowerPos = 0
        self.upperPos = 0
        self.offset = 0
        self.position = 0
        self.lastPressed = QxtSpanSliderH.NoHandle
        self.upperPressed = QStyle.SC_None
        self.lowerPressed = QStyle.SC_None
        self.movement = QxtSpanSliderH.FreeMovement
        self.mainControl = QxtSpanSliderH.LowerHandle
        self.firstMovement = False
        self.blockTracking = False
        self.gradientLeft = self.palette().color(QPalette.Dark).lighter(110)
        self.gradientRight = self.palette().color(QPalette.Dark).lighter(110)
        

    @Property(int)
    def lowerValue(self):
        return min(self.lower, self.upper)
        
    
    def setLowerValue(self, lower):
        self.setSpan(lower, self.upper)
        
    
    @Property(int)
    def upperValue(self):
        return max(self.lower, self.upper)
        
       
    def setUpperValue(self, upper):
        self.setSpan(self.lower, upper)
        

    @Property(object)
    def handleMovementMode(self):
        return self.movement
        
    
    def setHandleMovementMode(self, mode):
        self.movement = mode
        

    def setSpan(self, lower, upper):
        low = clamp(min(lower, upper), self.minimum(), self.maximum())
        upp = clamp(max(lower, upper), self.minimum(), self.maximum())
        changed = False
        if low != self.lower:
            self.lower = low
            self.lowerPos = low
            changed = True
        if upp != self.upper:
            self.upper = upp
            self.upperPos = upp
            changed = True
        if changed:
            self.spanChanged.emit(self.lower, self.upper)
            self.update()
            

    @Property(int)
    def lowerPosition(self):
        return self.lowerPos
        

    def setLowerPosition(self, lower):
        if self.lowerPos != lower:
            self.lowerPos = lower
            if not self.hasTracking():
                self.update()
            if self.isSliderDown():
                self.lowerPositionChanged.emit(lower)
            if self.hasTracking() and not self.blockTracking:
                main = (self.mainControl == QxtSpanSliderH.LowerHandle)
                self.triggerAction(QxtSpanSliderH.SliderMove, main)
                

    @Property(int)
    def upperPosition(self):
        return self.upperPos
        

    def setUpperPosition(self, upper):
        if self.upperPos != upper:
            self.upperPos = upper
            if not self.hasTracking():
                self.update()
            if self.isSliderDown():
                self.upperPositionChanged.emit(upper)
            if self.hasTracking() and not self.blockTracking:
                main = (self.mainControl == QxtSpanSliderH.UpperHandle)
                self.triggerAction(QxtSpanSliderH.SliderMove, main)
             
             
    @Property(object)
    def gradientLeftColor(self):
        return self.gradientLeft
        
        
    def setGradientLeftColor(self, color):
        self.gradientLeft = color
        self.update()
        
        
    @Property(object)
    def gradientRightColor(self):
        return self.gradientRight
      
      
    def setGradientRightColor(self, color):
        self.gradientRight = color
        self.update()
        
    
    def movePressedHandle(self):
        if self.lastPressed == QxtSpanSliderH.LowerHandle:
            if self.lowerPos != self.lower:
                main = (self.mainControl == QxtSpanSliderH.LowerHandle)
                self.triggerAction(QAbstractSlider.SliderMove, main)
        elif self.lastPressed == QxtSpanSliderH.UpperHandle:
            if self.upperPos != self.upper:
                main = (self.mainControl == QxtSpanSliderH.UpperHandle)
                self.triggerAction(QAbstractSlider.SliderMove, main)
                

    def pick(self, p):
        if self.orientation() == Qt.Horizontal:
            return p.x()
        else:
            return p.y()
            
    
    def triggerAction(self, action, main):
        value = 0
        no = False
        up = False
        my_min = self.minimum()
        my_max = self.maximum()
        altControl = QxtSpanSliderH.LowerHandle
        if self.mainControl == QxtSpanSliderH.LowerHandle:
            altControl = QxtSpanSliderH.UpperHandle

        self.blockTracking = True
        
        isUpperHandle = (main and self.mainControl == QxtSpanSliderH.UpperHandle) or (not main and altControl == QxtSpanSliderH.UpperHandle)
        
        if action == QAbstractSlider.SliderSingleStepAdd:
            if isUpperHandle:
                value = clamp(self.upper + self.singleStep(), my_min, my_max)
                up = True
            else:
                value = clamp(self.lower + self.singleStep(), my_min, my_max)
        elif action == QAbstractSlider.SliderSingleStepSub:
            if isUpperHandle:
                value = clamp(self.upper - self.singleStep(), my_min, my_max)
                up = True
            else:
                value = clamp(self.lower - self.singleStep(), my_min, my_max)
        elif action == QAbstractSlider.SliderToMinimum:
            value = my_min
            if isUpperHandle:
                up = True
        elif action == QAbstractSlider.SliderToMaximum:
            value = my_max
            if isUpperHandle:
                up = True
        elif action == QAbstractSlider.SliderMove:
            if isUpperHandle:
                up = True
            no = True
        elif action == QAbstractSlider.SliderNoAction:
            no = True

        if not no and not up:
            if self.movement == QxtSpanSliderH.NoCrossing:
                value = min(value, self.upper)
            elif self.movement == QxtSpanSliderH.NoOverlapping:
                value = min(value, self.upper - 1)

            if self.movement == QxtSpanSliderH.FreeMovement and value > self.upper:
                self.swapControls()
                self.setUpperPosition(value)
            else:
                self.eetLowerPosition(value)
        elif not no:
            if self.movement == QxtSpanSliderH.NoCrossing:
                value = max(value, self.lower)
            elif self.movement == QxtSpanSliderH.NoOverlapping:
                value = max(value, self.lower + 1)

            if self.movement == QxtSpanSliderH.FreeMovement and value < self.lower:
                self.swapControls()
                self.setLowerPosition(value)
            else:
                self.setUpperPosition(value)

        self.blockTracking = False
        self.setLowerValue(self.lowerPos)
        self.setUpperValue(self.upperPos)
        
    
    def swapControls(self):
        self.lower, self.upper = self.upper, self.lower
        self.lowerPressed, self.upperPressed = self.upperPressed, self.lowerPressed

        if self.lastPressed == QxtSpanSliderH.LowerHandle:
            self.lastPressed = QxtSpanSliderH.UpperHandle
        else:
            self.lastPressed = QxtSpanSliderH.LowerHandle
            
        if self.mainControl == QxtSpanSliderH.LowerHandle:
            self.mainControl = QxtSpanSliderH.UpperHandle
        else:
            self.mainControl = QxtSpanSliderH.LowerHandle
            

    def updateRange(self, min, max):
        # setSpan() takes care of keeping span in range
        self.setSpan(self.lower, self.upper)
        
    
    def paintEvent(self, event):
        painter = QStylePainter(self)
        
        # ticks
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)
        opt.subControls = QStyle.SC_SliderTickmarks
        painter.drawComplexControl(QStyle.CC_Slider, opt)

        # groove
        opt.sliderPosition = 20
        opt.sliderValue = 0
        opt.subControls = QStyle.SC_SliderGroove
        painter.drawComplexControl(QStyle.CC_Slider, opt)

        # handle rects
        opt.sliderPosition = self.lowerPos
        lr = self.style().subControlRect(QStyle.CC_Slider, opt, QStyle.SC_SliderHandle, self)
        lrv  = self.pick(lr.center())
        opt.sliderPosition = self.upperPos
        ur = self.style().subControlRect(QStyle.CC_Slider, opt, QStyle.SC_SliderHandle, self)
        urv  = self.pick(ur.center())

        # span
        minv = min(lrv, urv)
        maxv = max(lrv, urv)
        c = self.style().subControlRect(QStyle.CC_Slider, opt, QStyle.SC_SliderGroove, self).center()
        spanRect = QRect(QPoint(c.x() - 2, minv), QPoint(c.x() + 1, maxv))
        if self.orientation() == Qt.Horizontal:
            spanRect = QRect(QPoint(minv, c.y() - 2), QPoint(maxv, c.y() + 1))
        self.drawSpan(painter, spanRect)

        # handles
        if self.lastPressed == QxtSpanSliderH.LowerHandle:
            self.drawHandle(painter, QxtSpanSliderH.UpperHandle)
            self.drawHandle(painter, QxtSpanSliderH.LowerHandle)
        else:
            self.drawHandle(painter, QxtSpanSliderH.LowerHandle)
            self.drawHandle(painter, QxtSpanSliderH.UpperHandle)
            

    def setupPainter(self, painter, orientation, x1, y1, x2, y2):
        highlight = self.palette().color(QPalette.Highlight)
        gradient = QLinearGradient(x1, y1, x2, y2)
        gradient.setColorAt(0, highlight.darker(120))
        gradient.setColorAt(1, highlight.lighter(108))
        painter.setBrush(gradient)

        if orientation == Qt.Horizontal:
            painter.setPen(QPen(highlight.darker(130), 0))
        else:
            painter.setPen(QPen(highlight.darker(150), 0))
            

    def drawSpan(self, painter, rect):
        opt = QStyleOptionSlider()
        QSlider.initStyleOption(self, opt)

        # area
        groove = self.style().subControlRect(QStyle.CC_Slider, opt, QStyle.SC_SliderGroove, self)
        if opt.orientation == Qt.Horizontal:
            groove.adjust(0, 0, -1, 0);
        else:
            groove.adjust(0, 0, 0, -1);

        # pen & brush
        painter.setPen(QPen(self.gradientLeftColor, 0))
        if opt.orientation == Qt.Horizontal:
            self.setupPainter(painter, opt.orientation, groove.center().x(), groove.top(), groove.center().x(), groove.bottom())
        else:
            self.setupPainter(painter, opt.orientation, groove.left(), groove.center().y(), groove.right(), groove.center().y())

        # draw groove
        intersected = QRectF(rect.intersected(groove))
        gradient = QLinearGradient(intersected.topLeft(), intersected.topRight())
        gradient.setColorAt(0, self.gradientLeft)
        gradient.setColorAt(1, self.gradientRight)
        painter.fillRect(intersected, gradient)
        
    
    def drawHandle(self, painter, handle):
        opt = QStyleOptionSlider()
        self._initStyleOption(opt, handle)
        opt.subControls = QStyle.SC_SliderHandle
        pressed = self.upperPressed
        if handle == QxtSpanSliderH.LowerHandle:
            pressed = self.lowerPressed
        
        if pressed == QStyle.SC_SliderHandle:
            opt.activeSubControls = pressed
            opt.state |= QStyle.State_Sunken
        painter.drawComplexControl(QStyle.CC_Slider, opt)
        
    
    def _initStyleOption(self, option, handle):
        self.initStyleOption(option)

        option.sliderPosition = self.upperPos
        if handle == QxtSpanSliderH.LowerHandle:
            option.sliderPosition = self.lowerPos

        option.sliderValue = self.upper
        if handle == QxtSpanSliderH.LowerHandle:
            option.sliderPosition = self.lower
            
    
    def handleMousePress(self, pos, control, value, handle):
        opt = QStyleOptionSlider()
        self._initStyleOption(opt, handle)
        oldControl = control
        control = self.style().hitTestComplexControl(QStyle.CC_Slider, opt, pos, self)
        sr = self.style().subControlRect(QStyle.CC_Slider, opt, QStyle.SC_SliderHandle, self)
        if control == QStyle.SC_SliderHandle:
            self.position = value
            self.offset = self.pick(pos - sr.topLeft())
            self.lastPressed = handle
            self.setSliderDown(True)
            self.sliderPressed.emit(handle)
        if control != oldControl:
            self.update(sr)
        return control
        
    
    def mousePressEvent(self, event):
        if self.minimum() == self.maximum() or event.buttons() ^ event.button():
            event.ignore()
            return

        self.upperPressed = self.handleMousePress(event.pos(), self.upperPressed, self.upper, QxtSpanSliderH.UpperHandle)
        if self.upperPressed != QStyle.SC_SliderHandle:
            self.lowerPressed = self.handleMousePress(event.pos(), self.lowerPressed, self.lower, QxtSpanSliderH.LowerHandle)

        self.firstMovement = True
        event.accept()
        
    
    def mouseMoveEvent(self, event):
        if self.lowerPressed != QStyle.SC_SliderHandle and self.upperPressed != QStyle.SC_SliderHandle:
            event.ignore()
            return

        opt = QStyleOptionSlider()
        self.initStyleOption(opt)
        m = self.style().pixelMetric(QStyle.PM_MaximumDragDistance, opt, self)
        newPosition = self.pixelPosToRangeValue(self.pick(event.pos()) - self.offset)
        if m >= 0:
            r = self.rect().adjusted(-m, -m, m, m)
            if not r.contains(event.pos()):
                newPosition = self.position

        # pick the preferred handle on the first movement
        if self.firstMovement:
            if self.lower == self.upper:
                if newPosition < self.lowerValue:
                    self.swapControls()
                    self.firstMovement = False
            else:
                self.firstMovement = False

        if self.lowerPressed == QStyle.SC_SliderHandle:
            if self.movement == QxtSpanSliderH.NoCrossing:
                newPosition = min(newPosition, self.upper)
            elif self.movement == QxtSpanSliderH.NoOverlapping:
                newPosition = min(newPosition, self.upper - 1)

            if self.movement == QxtSpanSliderH.FreeMovement and newPosition > self.upper:
                self.swapControls()
                self.setUpperPosition(newPosition)
            else:
                self.setLowerPosition(newPosition)
        elif self.upperPressed == QStyle.SC_SliderHandle:
            if self.movement == QxtSpanSliderH.NoCrossing:
                newPosition = max(newPosition, self.lowerValue)
            elif self.movement == QxtSpanSliderH.NoOverlapping:
                newPosition = max(newPosition, self.lowerValue + 1);

            if self.movement == QxtSpanSliderH.FreeMovement and newPosition < self.lower:
                self.swapControls()
                self.setLowerPosition(newPosition)
            else:
                self.setUpperPosition(newPosition)
        event.accept()
        
    
    def mouseReleaseEvent(self, event):
        QSlider.mouseReleaseEvent(self, event)
        self.setSliderDown(False)
        self.lowerPressed = QStyle.SC_None
        self.upperPressed = QStyle.SC_None
        self.update()
        
    
    def pixelPosToRangeValue(self, pos):
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)

        sliderMin = 0
        sliderMax = 0
        sliderLength = 0
        gr = self.style().subControlRect(QStyle.CC_Slider, opt, QStyle.SC_SliderGroove, self)
        sr = self.style().subControlRect(QStyle.CC_Slider, opt, QStyle.SC_SliderHandle, self)
        if self.orientation() == Qt.Horizontal:
            sliderLength = sr.width()
            sliderMin = gr.x()
            sliderMax = gr.right() - sliderLength + 1
        else:
            sliderLength = sr.height()
            sliderMin = gr.y()
            sliderMax = gr.bottom() - sliderLength + 1
        
        return QStyle.sliderValueFromPosition(self.minimum(), self.maximum(), pos - sliderMin, sliderMax - sliderMin, opt.upsideDown)

    
if __name__ == "__main__":
    import sys
    
    app = QApplication(sys.argv)
    slider = QxtSpanSliderH()
    slider.setSpan(30, 70)
    slider.setRange(0, 100)
    color = QColor(Qt.blue).lighter(150)
    slider.setGradientLeftColor(color)
    slider.setGradientRightColor(color)
    slider.show()
    sys.exit(app.exec_())


# """ For license see https://github.com/mkilling/QxtSpanSliderH.py """

# from PyQt5.QtCore import pyqtSignature, pyqtProperty, SIGNAL, SLOT, QRect, QPoint
# from PyQt5.QtGui import QWidget, QAbstractSlider, QSlider, QStyle, QGridLayout, QLabel, QDoubleSpinBox, QGridLayout, QStylePainter, QStyleOption, QStyleOptionSlider, QPen, QPalette, QLinearGradient, QStyleFactory
# import PyQt5.QtCore as QtCore

# def clamp(v, lower, upper):
#     return min(upper, max(lower, v))


# class QxtSpanSliderH(QSlider):
#     NoHandle = None
#     LowerHandle = 1
#     UpperHandle = 2

#     FreeMovement = None
#     NoCrossing = 1
#     NoOverlapping = 2

#     __pyqtSignals__ = ("spanChanged(int, int)",
#                        "lowerValueChanged(int)", "upperValueChanged(int)",
#                        "lowerPositionChanged(int)", "upperPositionChanged(int)",
#                        "sliderPressed(PyQt_PyObject)")
#     __pyqtSlots__ = ("setLowerValue(int)",
#                       "setUpperValue(int)",
#                       "setSpan(int, int)",
#                       "setLowerPosition(int)",
#                       "setUpperPosition(int)",
#                       "setGradientLeftColor(PyQt_PyObject)",
#                       "setGradientRightColor(PyQt_PyObject)")

#     def __init__(self, parent = None):
#         QSlider.__init__(self, QtCore.Qt.Horizontal, parent)
#         self.connect(self, SIGNAL("rangeChanged(int, int)"), self.updateRange)
#         self.connect(self, SIGNAL("sliderReleased()"), self.movePressedHandle)

#         self.setStyle(QStyleFactory.create('Plastique'))

#         self.lower = 0
#         self.upper = 0
#         self.lowerPos = 0
#         self.upperPos = 0
#         self.offset = 0
#         self.position = 0
#         self.lastPressed = QxtSpanSliderH.NoHandle
#         self.upperPressed = QStyle.SC_None
#         self.lowerPressed = QStyle.SC_None
#         self.movement = QxtSpanSliderH.FreeMovement
#         self.mainControl = QxtSpanSliderH.LowerHandle
#         self.firstMovement = False
#         self.blockTracking = False
#         self.gradientLeft = self.palette().color(QPalette.Dark).light(110)
#         self.gradientRight = self.palette().color(QPalette.Dark).light(110)

#     def lowerValue(self):
#         return min(self.lower, self.upper)

#     def setLowerValue(self, lower):
#         self.setSpan(lower, self.upper)

#     def upperValue(self):
#         return max(self.lower, self.upper)

#     def setUpperValue(self, upper):
#         self.setSpan(self.lower, upper)

#     def handleMovementMode(self):
#         return self.movement

#     def setHandleMovementMode(self, mode):
#         self.movement = mode

#     def setSpan(self, lower, upper):
#         low = clamp(min(lower, upper), self.minimum(), self.maximum())
#         upp = clamp(max(lower, upper), self.minimum(), self.maximum())
#         changed = False
#         if low != self.lower:
#             self.lower = low
#             self.lowerPos = low
#             changed = True
#         if upp != self.upper:
#             self.upper = upp
#             self.upperPos = upp
#             changed = True
#         if changed:
#             self.emit(SIGNAL("spanChanged(int, int)"), self.lower, self.upper)
#             self.update()

#     def lowerPosition(self):
#         return self.lowerPos

#     def setLowerPosition(self, lower):
#         if self.lowerPos != lower:
#             self.lowerPos = lower
#             if not self.hasTracking():
#                 self.update()
#             if self.isSliderDown():
#                 self.emit(SIGNAL("lowerPositionChanged(int)"), lower)
#             if self.hasTracking() and not self.blockTracking:
#                 main = (self.mainControl == QxtSpanSliderH.LowerHandle)
#                 self.triggerAction(QxtSpanSliderH.SliderMove, main)

#     def upperPosition(self):
#         return self.upperPos

#     def setUpperPosition(self, upper):
#         if self.upperPos != upper:
#             self.upperPos = upper
#             if not self.hasTracking():
#                 self.update()
#             if self.isSliderDown():
#                 self.emit(SIGNAL("upperPositionChanged(int)"), upper)
#             if self.hasTracking() and not self.blockTracking:
#                 main = (self.mainControl == QxtSpanSliderH.UpperHandle)
#                 self.triggerAction(QxtSpanSliderH.SliderMove, main)

#     def gradientLeftColor(self):
#         return self.gradientLeft

#     def setGradientLeftColor(self, color):
#         self.gradientLeft = color
#         self.update()

#     def gradientRightColor(self):
#         return self.gradientRight

#     def setGradientRightColor(self, color):
#         self.gradientRight = color
#         self.update()

#     def movePressedHandle(self):
#         if self.lastPressed == QxtSpanSliderH.LowerHandle:
#             if self.lowerPos != self.lower:
#                 main = (self.mainControl == QxtSpanSliderH.LowerHandle)
#                 self.triggerAction(QAbstractSlider.SliderMove, main)
#         elif self.lastPressed == QxtSpanSliderH.UpperHandle:
#             if self.upperPos != self.upper:
#                 main = (self.mainControl == QxtSpanSliderH.UpperHandle)
#                 self.triggerAction(QAbstractSlider.SliderMove, main)

#     def pick(self, p):
#         if self.orientation() == QtCore.Qt.Horizontal:
#             return p.x()
#         else:
#             return p.y()

#     def triggerAction(self, action, main):
#         value = 0
#         no = False
#         up = False
#         my_min = self.minimum()
#         my_max = self.maximum()
#         altControl = QxtSpanSliderH.LowerHandle
#         if self.mainControl == QxtSpanSliderH.LowerHandle:
#             altControl = QxtSpanSliderH.UpperHandle

#         self.blockTracking = True

#         isUpperHandle = (main and self.mainControl == QxtSpanSliderH.UpperHandle) or (not main and altControl == QxtSpanSliderH.UpperHandle)

#         if action == QAbstractSlider.SliderSingleStepAdd:
#             if isUpperHandle:
#                 value = clamp(self.upper + self.singleStep(), my_min, my_max)
#                 up = True
#             else:
#                 value = clamp(self.lower + self.singleStep(), my_min, my_max)
#         elif action == QAbstractSlider.SliderSingleStepSub:
#             if isUpperHandle:
#                 value = clamp(self.upper - self.singleStep(), my_min, my_max)
#                 up = True
#             else:
#                 value = clamp(self.lower - self.singleStep(), my_min, my_max)
#         elif action == QAbstractSlider.SliderToMinimum:
#             value = my_min
#             if isUpperHandle:
#                 up = True
#         elif action == QAbstractSlider.SliderToMaximum:
#             value = my_max
#             if isUpperHandle:
#                 up = True
#         elif action == QAbstractSlider.SliderMove:
#             if isUpperHandle:
#                 up = True
#             no = True
#         elif action == QAbstractSlider.SliderNoAction:
#             no = True

#         if not no and not up:
#             if self.movement == QxtSpanSliderH.NoCrossing:
#                 value = min(value, self.upper)
#             elif self.movement == QxtSpanSliderH.NoOverlapping:
#                 value = min(value, self.upper - 1)

#             if self.movement == QxtSpanSliderH.FreeMovement and value > self.upper:
#                 self.swapControls()
#                 self.setUpperPosition(value)
#             else:
#                 self.setLowerPosition(value)
#         elif not no:
#             if self.movement == QxtSpanSliderH.NoCrossing:
#                 value = max(value, self.lower)
#             elif self.movement == QxtSpanSliderH.NoOverlapping:
#                 value = max(value, self.lower + 1)

#             if self.movement == QxtSpanSliderH.FreeMovement and value < self.lower:
#                 self.swapControls()
#                 self.setLowerPosition(value)
#             else:
#                 self.setUpperPosition(value)

#         self.blockTracking = False
#         self.setLowerValue(self.lowerPos)
#         self.setUpperValue(self.upperPos)

#     def swapControls(self):
#         self.lower, self.upper = self.upper, self.lower
#         self.lowerPressed, self.upperPressed = self.upperPressed, self.lowerPressed

#         if self.lastPressed == QxtSpanSliderH.LowerHandle:
#             self.lastPressed = QxtSpanSliderH.UpperHandle
#         else:
#             self.lastPressed = QxtSpanSliderH.LowerHandle

#         if self.mainControl == QxtSpanSliderH.LowerHandle:
#             self.mainControl = QxtSpanSliderH.UpperHandle
#         else:
#             self.mainControl = QxtSpanSliderH.LowerHandle

#     def updateRange(self, min, max):
#         # setSpan() takes care of keeping span in range
#         self.setSpan(self.lower, self.upper)

#     def paintEvent(self, event):
#         painter = QStylePainter(self)

#         # ticks
#         opt = QStyleOptionSlider()
#         self.initStyleOption(opt)
#         opt.subControls = QStyle.SC_SliderTickmarks
#         painter.drawComplexControl(QStyle.CC_Slider, opt)

#         # groove
#         opt.sliderPosition = 20
#         opt.sliderValue = 0
#         opt.subControls = QStyle.SC_SliderGroove
#         painter.drawComplexControl(QStyle.CC_Slider, opt)

#         # handle rects
#         opt.sliderPosition = self.lowerPos
#         lr = self.style().subControlRect(QStyle.CC_Slider, opt, QStyle.SC_SliderHandle, self)
#         lrv  = self.pick(lr.center())
#         opt.sliderPosition = self.upperPos
#         ur = self.style().subControlRect(QStyle.CC_Slider, opt, QStyle.SC_SliderHandle, self)
#         urv  = self.pick(ur.center())

#         # span
#         minv = min(lrv, urv)
#         maxv = max(lrv, urv)
#         c = self.style().subControlRect(QStyle.CC_Slider, opt, QStyle.SC_SliderGroove, self).center()
#         spanRect = QRect(QPoint(c.x() - 2, minv), QPoint(c.x() + 1, maxv))
#         if self.orientation() == QtCore.Qt.Horizontal:
#             spanRect = QRect(QPoint(minv, c.y() - 2), QPoint(maxv, c.y() + 1))
#         self.drawSpan(painter, spanRect)

#         # handles
#         if self.lastPressed == QxtSpanSliderH.LowerHandle:
#             self.drawHandle(painter, QxtSpanSliderH.UpperHandle)
#             self.drawHandle(painter, QxtSpanSliderH.LowerHandle)
#         else:
#             self.drawHandle(painter, QxtSpanSliderH.LowerHandle)
#             self.drawHandle(painter, QxtSpanSliderH.UpperHandle)

#     def setupPainter(self, painter, orientation, x1, y1, x2, y2):
#         highlight = self.palette().color(QPalette.Highlight)
#         gradient = QLinearGradient(x1, y1, x2, y2)
#         gradient.setColorAt(0, highlight.dark(120))
#         gradient.setColorAt(1, highlight.light(108))
#         painter.setBrush(gradient)

#         if orientation == QtCore.Qt.Horizontal:
#             painter.setPen(QPen(highlight.dark(130), 0))
#         else:
#             painter.setPen(QPen(highlight.dark(150), 0))

#     def drawSpan(self, painter, rect):
#         opt = QStyleOptionSlider()
#         QSlider.initStyleOption(self, opt)

#         # area
#         groove = self.style().subControlRect(QStyle.CC_Slider, opt, QStyle.SC_SliderGroove, self)
#         if opt.orientation == QtCore.Qt.Horizontal:
#             groove.adjust(0, 0, -1, 0);
#         else:
#             groove.adjust(0, 0, 0, -1);

#         # pen & brush
#         painter.setPen(QPen(self.gradientLeftColor, 0))
#         if opt.orientation == QtCore.Qt.Horizontal:
#             self.setupPainter(painter, opt.orientation, groove.center().x(), groove.top(), groove.center().x(), groove.bottom())
#         else:
#             self.setupPainter(painter, opt.orientation, groove.left(), groove.center().y(), groove.right(), groove.center().y())

#         # draw groove
#         intersected = QtCore.QRectF(rect.intersected(groove))
#         gradient = QLinearGradient(intersected.topLeft(), intersected.topRight())
#         gradient.setColorAt(0, self.gradientLeft)
#         gradient.setColorAt(1, self.gradientRight)
#         painter.fillRect(intersected, gradient)

#     def drawHandle(self, painter, handle):
#         opt = QStyleOptionSlider()
#         self._initStyleOption(opt, handle)
#         opt.subControls = QStyle.SC_SliderHandle
#         pressed = self.upperPressed
#         if handle == QxtSpanSliderH.LowerHandle:
#             pressed = self.lowerPressed

#         if pressed == QStyle.SC_SliderHandle:
#             opt.activeSubControls = pressed
#             opt.state |= QStyle.State_Sunken
#         painter.drawComplexControl(QStyle.CC_Slider, opt)

#     def _initStyleOption(self, option, handle):
#         self.initStyleOption(option)

#         option.sliderPosition = self.upperPos
#         if handle == QxtSpanSliderH.LowerHandle:
#             option.sliderPosition = self.lowerPos

#         option.sliderValue = self.upper
#         if handle == QxtSpanSliderH.LowerHandle:
#             option.sliderPosition = self.lower

#     def handleMousePress(self, pos, control, value, handle):
#         opt = QStyleOptionSlider()
#         self._initStyleOption(opt, handle)
#         oldControl = control
#         control = self.style().hitTestComplexControl(QStyle.CC_Slider, opt, pos, self)
#         sr = self.style().subControlRect(QStyle.CC_Slider, opt, QStyle.SC_SliderHandle, self)
#         if control == QStyle.SC_SliderHandle:
#             self.position = value
#             self.offset = self.pick(pos - sr.topLeft())
#             self.lastPressed = handle
#             self.setSliderDown(True)
#             self.emit(SIGNAL("sliderPressed(PyQt_PyObject)"), handle)
#         if control != oldControl:
#             self.update(sr)
#         return control

#     def mousePressEvent(self, event):
#         if self.minimum() == self.maximum() or event.buttons() ^ event.button():
#             event.ignore()
#             return

#         self.upperPressed = self.handleMousePress(event.pos(), self.upperPressed, self.upper, QxtSpanSliderH.UpperHandle)
#         if self.upperPressed != QStyle.SC_SliderHandle:
#             self.lowerPressed = self.handleMousePress(event.pos(), self.lowerPressed, self.lower, QxtSpanSliderH.LowerHandle)

#         self.firstMovement = True
#         event.accept()

#     def mouseMoveEvent(self, event):
#         if self.lowerPressed != QStyle.SC_SliderHandle and self.upperPressed != QStyle.SC_SliderHandle:
#             event.ignore()
#             return

#         opt = QStyleOptionSlider()
#         self.initStyleOption(opt)
#         m = self.style().pixelMetric(QStyle.PM_MaximumDragDistance, opt, self)
#         newPosition = self.pixelPosToRangeValue(self.pick(event.pos()) - self.offset)
#         if m >= 0:
#             r = self.rect().adjusted(-m, -m, m, m)
#             if not r.contains(event.pos()):
#                 newPosition = self.position

#         # pick the preferred handle on the first movement
#         if self.firstMovement:
#             if self.lower == self.upper:
#                 if newPosition < self.lowerValue:
#                     self.swapControls()
#                     self.firstMovement = False
#             else:
#                 self.firstMovement = False

#         if self.lowerPressed == QStyle.SC_SliderHandle:
#             if self.movement == QxtSpanSliderH.NoCrossing:
#                 newPosition = min(newPosition, self.upper)
#             elif self.movement == QxtSpanSliderH.NoOverlapping:
#                 newPosition = min(newPosition, self.upper - 1)

#             if self.movement == QxtSpanSliderH.FreeMovement and newPosition > self.upper:
#                 self.swapControls()
#                 self.setUpperPosition(newPosition)
#             else:
#                 self.setLowerPosition(newPosition)
#         elif self.upperPressed == QStyle.SC_SliderHandle:
#             if self.movement == QxtSpanSliderH.NoCrossing:
#                 newPosition = max(newPosition, self.lowerValue)
#             elif self.movement == QxtSpanSliderH.NoOverlapping:
#                 newPosition = max(newPosition, self.lowerValue + 1);

#             if self.movement == QxtSpanSliderH.FreeMovement and newPosition < self.lower:
#                 self.swapControls()
#                 self.setLowerPosition(newPosition)
#             else:
#                 self.setUpperPosition(newPosition)
#         event.accept()

#     def mouseReleaseEvent(self, event):
#         QSlider.mouseReleaseEvent(self, event)
#         self.setSliderDown(False)
#         self.lowerPressed = QStyle.SC_None
#         self.upperPressed = QStyle.SC_None
#         self.update()

#     def pixelPosToRangeValue(self, pos):
#         opt = QStyleOptionSlider()
#         self.initStyleOption(opt)

#         sliderMin = 0
#         sliderMax = 0
#         sliderLength = 0
#         gr = self.style().subControlRect(QStyle.CC_Slider, opt, QStyle.SC_SliderGroove, self)
#         sr = self.style().subControlRect(QStyle.CC_Slider, opt, QStyle.SC_SliderHandle, self)
#         if self.orientation() == QtCore.Qt.Horizontal:
#             sliderLength = sr.width()
#             sliderMin = gr.x()
#             sliderMax = gr.right() - sliderLength + 1
#         else:
#             sliderLength = sr.height()
#             sliderMin = gr.y()
#             sliderMax = gr.bottom() - sliderLength + 1

#         return QStyle.sliderValueFromPosition(self.minimum(), self.maximum(), pos - sliderMin, sliderMax - sliderMin, opt.upsideDown)

#     lowerValue = pyqtProperty("int", lowerValue, setLowerValue)
#     upperValue = pyqtProperty("int", upperValue, setUpperValue)
#     upperPosition = pyqtProperty("int", upperPosition, setUpperPosition)
#     lowerPosition = pyqtProperty("int", lowerPosition, setLowerPosition)
#     handleMovementMode = pyqtProperty("PyQt_PyObject", handleMovementMode, setHandleMovementMode)
#     gradientLeftColor = pyqtProperty("PyQt_PyObject", gradientLeftColor, setGradientLeftColor)
#     gradientRightColor = pyqtProperty("PyQt_PyObject", gradientRightColor, setGradientRightColor)