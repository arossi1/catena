# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing details.
import sys, os, glob, math, _thread
sys.path.append(os.path.abspath("."))
#sys.path.append(os.path.abspath(".."))

from PyQt4 import QtCore, QtGui, QtXml
from PyQt4.QtCore import pyqtSlot,pyqtSignal
from catena.code import Chain # Chain must be imported first, requirement of registry
from catena.code import BundleAdjustment, Common


def GetAbsImagePath(fileName):
    return os.path.join(os.path.split(os.path.abspath(__file__))[0],"images",fileName)

class Manager(QtCore.QObject):
    
    renderRequestSignal = QtCore.pyqtSignal(object)
    
    def __init__(self):
        QtCore.QObject.__init__(self)
        
    def renderRequest(self, o):
        self.renderRequestSignal.emit(o)
        
_manager = Manager()

############################################################################### 
class ContextHandlerChain(QtCore.QObject):
    
    def __init__(self):
        QtCore.QObject.__init__(self)        
        self._menu = QtGui.QMenu()        
        self._actionMap = {}
        for package in Chain.StageRegistry.registry.GetPackages():
            menu = self._menu.addMenu(package)
            for stage in Chain.StageRegistry.registry.GetStages(package):
                action = QtGui.QAction(stage, self)
                stageDesc = Chain.StageRegistry.registry.GetStageDescription(package,stage)
                action.setToolTip(stageDesc)
                action.setStatusTip(stageDesc)
                menu.addAction(action)
                self._actionMap[action] = (package, stage)
                    
    def getAction(self, event):
        r = self._menu.exec_(event.screenPos())
        if (r==None): return None
        else:         return self._actionMap[r]
        
        
        
############################################################################### 
class ContextHandlerStage(QtCore.QObject):
    
    def __init__(self):
        QtCore.QObject.__init__(self)        
        self._menu = QtGui.QMenu()      
        
        self._actionMap = {}        
        action = QtGui.QAction("Render Stage", self)
        self._actionMap[action] = "Render"
        self._menu.addAction(action)
                    
    def getAction(self, event):
        r = self._menu.exec_(event.screenPos())
        if (r==None): return None
        else:         return self._actionMap[r]
    
    

############################################################################### 
class Arrow(QtGui.QGraphicsLineItem):
    def __init__(self, startItem, endItem, parent=None, scene=None):
        super(Arrow, self).__init__(parent, scene)

        self.arrowHead = QtGui.QPolygonF()

        self.myStartItem = startItem
        self.myEndItem = endItem
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True)
        self.myColor = QtCore.Qt.black
        self.setPen(QtGui.QPen(self.myColor, 2, QtCore.Qt.SolidLine,
                QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))

    def setColor(self, color):
        self.myColor = color

    def startItem(self):
        return self.myStartItem

    def endItem(self):
        return self.myEndItem

    def boundingRect(self):
        extra = (self.pen().width() + 20) / 2.0
        p1 = self.line().p1()
        p2 = self.line().p2()
        return QtCore.QRectF(p1, QtCore.QSizeF(p2.x() - p1.x(), p2.y() - p1.y())).normalized().adjusted(-extra, -extra, extra, extra)

    def shape(self):
        path = super(Arrow, self).shape()
        path.addPolygon(self.arrowHead)
        return path

    def updatePosition(self):
        line = QtCore.QLineF(self.mapFromItem(self.myStartItem, 0, 0), self.mapFromItem(self.myEndItem, 0, 0))
        self.setLine(line)
        
    def keyPressEvent(self, event):
        if (event.key()==QtCore.Qt.Key_Delete):
            Chain.StageRegistry.registry.RemoveInstance(self.__stageObject)
            self.removeArrows()
            self.scene().removeItem(self)

    def paint(self, painter, option, widget=None):
        if (self.myStartItem.collidesWithItem(self.myEndItem)):
            return

        myStartItem = self.myStartItem
        myEndItem = self.myEndItem
        myColor = self.myColor
        myPen = self.pen()
        myPen.setColor(self.myColor)
        arrowSize = 20.0
        painter.setPen(myPen)
        painter.setBrush(self.myColor)

        centerLine = QtCore.QLineF(myStartItem.pos(), myEndItem.pos())
        endPolygon = myEndItem.polygon()
        p1 = endPolygon.first() + myEndItem.pos()

        intersectPoint = QtCore.QPointF()
        for i in endPolygon:
            p2 = i + myEndItem.pos()
            polyLine = QtCore.QLineF(p1, p2)
            intersectType = polyLine.intersect(centerLine, intersectPoint)
            if intersectType == QtCore.QLineF.BoundedIntersection:
                break
            p1 = p2

        self.setLine(QtCore.QLineF(intersectPoint, myStartItem.pos()))
        line = self.line()

        angle = math.acos(line.dx() / line.length())
        if line.dy() >= 0:
            angle = (math.pi * 2.0) - angle

        arrowP1 = line.p1() + QtCore.QPointF(math.sin(angle + math.pi / 3.0) * arrowSize,
                                        math.cos(angle + math.pi / 3) * arrowSize)
        arrowP2 = line.p1() + QtCore.QPointF(math.sin(angle + math.pi - math.pi / 3.0) * arrowSize,
                                        math.cos(angle + math.pi - math.pi / 3.0) * arrowSize)

        self.arrowHead.clear()
        for point in [line.p1(), arrowP1, arrowP2]:
            self.arrowHead.append(point)

        painter.drawLine(line)
        painter.drawPolygon(self.arrowHead)
        if self.isSelected():
            painter.setPen(QtGui.QPen(myColor, 1, QtCore.Qt.DashLine))
            myLine = QtCore.QLineF(line)
            myLine.translate(0, 4.0)
            painter.drawLine(myLine)
            myLine.translate(0,-8.0)
            painter.drawLine(myLine)



############################################################################### 
class StageItem(QtGui.QGraphicsPolygonItem):
    
    def __init__(self, stageObject, parent=None):
        super(StageItem, self).__init__(parent)
        #QtGui.QGraphicsPolygonItem.__init__(self, parent)
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable)
        self.setFlag(QtGui.QGraphicsItem.ItemIsFocusable)
        self.__stageObject = stageObject
        self.arrows = []
        label = QtGui.QGraphicsTextItem(stageObject.GetStageName(), self)
        font = label.font()
        font.setBold(True)
        font.setPointSize(12)
        label.setFont(font)
        label.setPos(-55,-20)
        label.setZValue(10)
        label.adjustSize()
        self.setZValue(9)
        self.setBrush(QtGui.QBrush(QtGui.QPixmap(GetAbsImagePath("graybg.png"))))


        if (False):
            path = QtGui.QPainterPath()
            path.moveTo(200, 50)
            path.arcTo(150, 0, 50, 50, 0, 90)
            path.arcTo(50, 0, 50, 50, 90, 90)
            path.arcTo(50, 50, 50, 50, 180, 90)
            path.arcTo(150, 50, 50, 50, 270, 90)
            path.lineTo(200, 25)
            self.setPolygon(path.toFillPolygon())
        else:
            myPolygon = QtGui.QPolygonF([
                        QtCore.QPointF(-120, -80), QtCore.QPointF(-70, 80),
                        QtCore.QPointF(120, 80), QtCore.QPointF(70, -80),
                        QtCore.QPointF(-120, -80)])
            self.setPolygon(myPolygon)

        
    def GetStageObject(self): return self.__stageObject
    
    def removeArrow(self, arrow):
        try:
            self.arrows.remove(arrow)
        except ValueError:
            pass

    def removeArrows(self):
        for arrow in self.arrows[:]:
            arrow.startItem().removeArrow(arrow)
            arrow.endItem().removeArrow(arrow)
            self.scene().removeItem(arrow)

    def addArrow(self, arrow):
        arrow.setZValue(1)
        self.arrows.append(arrow)
        
    def itemChange(self, change, value):
        if change == QtGui.QGraphicsItem.ItemPositionChange:
            for arrow in self.arrows:
                arrow.updatePosition()

        return value
    
    def keyPressEvent(self, event):
        if (event.key()==QtCore.Qt.Key_Delete):
            Chain.StageRegistry.registry.RemoveInstance(self.__stageObject)
            self.removeArrows()
            self.scene().removeItem(self)
            
    def contextMenuEvent(self, event): 
        ch = ContextHandlerStage()
        res = ch.getAction(event)
        if (res=="Render"):
            _manager.renderRequest(self.__stageObject)
        


############################################################################### 
class StageScene(QtGui.QGraphicsScene):
    
    InsertItem, InsertLine, InsertText, MoveItem  = range(4)
    
    def __init__(self, parent=None):
        QtGui.QGraphicsScene.__init__(self, -400, -400, 800, 800, parent)
        
        self.myMode = self.MoveItem
        self.line = None
        QtCore.QObject.connect(self, QtCore.SIGNAL("selectionChanged ()"), self.selectionChangedSlot)    
    
    def selectionChangedSlot(self):
        if (len(self.selectedItems())==1):
            self.emit(QtCore.SIGNAL("stageSelectedSignal(PyQt_PyObject)"), self.selectedItems()[0])
    
    def setMode(self, mode):
        self.myMode = mode
        
    def mousePressEvent(self, mouseEvent):
        if (mouseEvent.button() == QtCore.Qt.LeftButton):
            if self.myMode == self.InsertLine:
                self.line = QtGui.QGraphicsLineItem(QtCore.QLineF(mouseEvent.scenePos(),
                                                                  mouseEvent.scenePos()))
                self.line.setPen(QtGui.QPen(QtCore.Qt.black, 2))
                self.addItem(self.line)
                self.line.setZValue(100000)

        super(StageScene, self).mousePressEvent(mouseEvent)

    def mouseMoveEvent(self, mouseEvent):
        if self.myMode == self.InsertLine and self.line:
            newLine = QtCore.QLineF(self.line.line().p1(), mouseEvent.scenePos())
            self.line.setLine(newLine)
        elif self.myMode == self.MoveItem:
            super(StageScene, self).mouseMoveEvent(mouseEvent)

    def mouseReleaseEvent(self, mouseEvent):
        if self.line and self.myMode == self.InsertLine:
            
            startItems = self.items(self.line.line().p1())
            if len(startItems) and startItems[0] == self.line:
                startItems.pop(0)
                
            endItems = self.items(self.line.line().p2())
            if len(endItems) and endItems[0] == self.line:
                endItems.pop(0)

            self.removeItem(self.line)
            self.line = None

            if (len(startItems) and 
                len(endItems) and
                startItems[0] != endItems[0]):
#               isinstance(startItems[0], StageItem) and
#               isinstance(endItems[0], StageItem) and
                
                startItem = startItems[0]
                endItem = endItems[0]
                
                valid = True
                if (not isinstance(startItem, StageItem)): startItem = startItem.parentItem()
                if (not isinstance(startItem, StageItem)): valid = False
                
                if (not isinstance(endItem, StageItem)): endItem = endItem.parentItem()
                if (not isinstance(endItem, StageItem)): valid = False
                
                if (valid):
                    arrow = Arrow(startItem, endItem)
                    arrow.setColor(QtCore.Qt.black)
                    startItem.addArrow(arrow)
                    endItem.addArrow(arrow)
                    self.addItem(arrow)
                    arrow.updatePosition()
                    endItem.GetStageObject().AddInputStage(startItem.GetStageObject())

        self.line = None
        super(StageScene, self).mouseReleaseEvent(mouseEvent)
        
    def contextMenuEvent(self, event):
        
        if (len(self.selectedItems())):
            #if one item is selected, pass contextMenuEvent to it...
            self.selectedItems()[0].contextMenuEvent(event)
            
        else:
            ch = ContextHandlerChain()
            res = ch.getAction(event)
            
            if (res!=None):
                o = Chain.StageRegistry.registry.CreateInstance(res[0],res[1])
                si = StageItem(o)
                si.setPos(event.scenePos())
                self.addItem(si)
        
    def keyPressEvent(self, event):
        return QtGui.QGraphicsScene.keyPressEvent(self,event)    


    def loadFromRegistry(self):
        self.clear()
        
        stages = {}
        # add stages
        for stage in Chain.StageRegistry.registry.GetStageInstances():
            si = StageItem(stage)
            self.addItem(si)
            stages[stage] = si
            
        #link
        for stage in stages.keys():
            for outputStage in stage.GetOutputStages():
                arrow = Arrow(stages[stage], stages[outputStage])
                arrow.setColor(QtCore.Qt.black)
                stages[stage].addArrow(arrow)
                stages[outputStage].addArrow(arrow)
                self.addItem(arrow)
                arrow.updatePosition()
                
        self.autoArrangeStages()
                
    def autoArrangeStages(self):
        PAD = 20
        pt = self.sceneRect().topLeft()
        pt.setX(pt.x()+PAD)
        pt.setY(pt.y()+PAD)
        for item in reversed(list(self.items())):
            if (isinstance(item, StageItem)):
                item.setPos(pt)
                pt.setX(pt.x()+item.boundingRect().width())
                if (not self.sceneRect().contains(pt)):
                    pt.setY(pt.y()+item.boundingRect().height()+PAD)
                    pt.setX(self.sceneRect().left()+PAD)
            


############################################################################### 
class StageView(QtGui.QGraphicsView):
    def __init__(self, graphicsScene=None):
        QtGui.QGraphicsView.__init__(self, graphicsScene)
        #self.rubberBandSelectionMode(QtGui.QGraphicsView.IntersectsItemBoundingRect)
        self.setDragMode(QtGui.QGraphicsView.RubberBandDrag)

        # note: background (grids) do not update without this setting
        self.setViewportUpdateMode(QtGui.QGraphicsView.FullViewportUpdate)
        
        #TODO: background
        self.scene().setBackgroundBrush(QtGui.QBrush(QtGui.QPixmap(GetAbsImagePath("graybg.png"))))
        
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setRenderHint(QtGui.QPainter.TextAntialiasing)
        self.setRenderHint(QtGui.QPainter.SmoothPixmapTransform)
        
    def wheelEvent(self, event):
        self.scaleView(math.pow(2.0, -event.delta() / 240.0))
    
    def scaleView(self, scaleFactor):
        factor = self.matrix().scale(scaleFactor, scaleFactor).mapRect(QtCore.QRectF(0, 0, 1, 1)).width()
        if factor < 0.07 or factor > 100:
            return
        self.scale(scaleFactor, scaleFactor)


###############################################################################
class StagePropertyEditor(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)    
            
        self.stagePropertiesView = QtGui.QTableWidget(self)
        p = self.stagePropertiesView.palette()
        p.setColor(QtGui.QPalette.Normal, QtGui.QPalette.Highlight, QtGui.QColor(0,0,220,120))
        self.stagePropertiesView.setPalette(p)
        self.stagePropertiesView.verticalHeader().setVisible(False)
        self.stagePropertiesView.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.stagePropertiesView.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
                
        self.propertyLabel = QtGui.QLabel(self)
        self.propertyLabel.setWordWrap(True)
        self.propertyLabel.setFrameStyle(QtGui.QFrame.StyledPanel | QtGui.QFrame.Raised);
        self.propertyLabel.setLineWidth(2);
        self.propertyLabel.setAlignment(QtCore.Qt.AlignTop)
        
        self.interfaceLabel = QtGui.QLabel(self)
        self.interfaceLabel.setWordWrap(True)
        self.interfaceLabel.setFrameStyle(QtGui.QFrame.StyledPanel | QtGui.QFrame.Raised);
        self.interfaceLabel.setLineWidth(2);
        self.interfaceLabel.setAlignment(QtCore.Qt.AlignTop)
        
        layout = QtGui.QVBoxLayout()
        splitter = QtGui.QSplitter(QtCore.Qt.Vertical)
        splitter.addWidget(self.stagePropertiesView)
        splitter.addWidget(self.propertyLabel)
        splitter.addWidget(self.interfaceLabel)
        layout.addWidget(splitter)
        self.setLayout(layout)
    
    def GetWidgetForType(self, t, initVal, pd):
        if (t==type(0)):
            sb = QtGui.QSpinBox()
            sb.setMinimum(-sys.maxsize)
            sb.setMaximum(sys.maxsize)
            sb.setValue(initVal)
            sb.installEventFilter(self)
            QtCore.QObject.connect(sb, QtCore.SIGNAL("valueChanged(int)"), self.valChangedSlot)
            return sb
        elif (t==type(0.0)):
            sb = QtGui.QDoubleSpinBox()
            sb.setMinimum(-sys.maxsize)
            sb.setMaximum(sys.maxsize)
            sb.setValue(initVal)
            sb.installEventFilter(self)
            QtCore.QObject.connect(sb, QtCore.SIGNAL("valueChanged(double)"), self.valChangedSlot)
            return sb
        elif (t==type(True)):
            cb = QtGui.QCheckBox()
            cb.setChecked(initVal)
            cb.installEventFilter(self)
            QtCore.QObject.connect(cb, QtCore.SIGNAL("stateChanged(int)"), self.valChangedBoolSlot)
            frame = QtGui.QFrame()
            layout = QtGui.QHBoxLayout()
            layout.addWidget(cb)
            frame.setLayout(layout)
            return frame, cb
        elif ((t==type("")) and ("{" in pd) and ("}" in pd)):
            cb = QtGui.QComboBox()
            cb.installEventFilter(self)
            cb.addItems([x.strip() for x in pd[pd.find("{")+1:pd.find("}")].split(",")])
            cb.setCurrentIndex(cb.findText(initVal))
            QtCore.QObject.connect(cb, QtCore.SIGNAL("currentIndexChanged(const QString&)"), self.valChangedSlot)                
            return cb
        else:
            le = QtGui.QLineEdit()
            le.setText(initVal)
            le.installEventFilter(self)
            QtCore.QObject.connect(le, QtCore.SIGNAL("textChanged(const QString&)"), self.valChangedSlot)            
            return le
        
        
    def eventFilter(self, o, event):
        if (event.type() == QtCore.QEvent.Enter and o in self.__widgetIndexMap):
            self.stagePropertiesView.setCurrentCell(self.__widgetIndexMap[o],0)
        return False
    
    def valChangedSlot(self, val):
        if (isinstance(val,QtCore.QString)):
            val = str(val)
        propName = str(self.stagePropertiesView.item(self.stagePropertiesView.currentRow(), 0).text())
        self.__stageObject.SetProperty(propName, val)
        
    def valChangedBoolSlot(self, val):
        val = (val!=0)
        propName = str(self.stagePropertiesView.item(self.stagePropertiesView.currentRow(), 0).text())
        self.__stageObject.SetProperty(propName, val)

    def SetInterfaceDescription(self):
        
        s = "[%s]\n\n" % self.__stageObject.GetStageDescription()
        s += "Input Interface:\n"
        if (self.__stageObject.GetInputInterface()==None):
            s += "  (None)\n"
        else:
            inputInterface = []
            for kv in self.__stageObject.GetInputInterface().items():
                try:
                    inputName,(inputIndex,inputType) = kv
                    inputInterface.append((inputIndex,inputType.__name__))
                except:
                    s+="ERROR!\n"
                    
            inputInterface.sort()
            for i in inputInterface:
                s += "  [%d] %s\n" % i
        s+="\n"
        
        s += "Output Interface:\n"
        if (self.__stageObject.GetOutputInterface()==None):
            s += "  (None)\n"
        else:
            outputInterface = []
            for kv in self.__stageObject.GetOutputInterface().items():
                try:
                    outputName,outputType = kv
                    outputInterface.append(outputType.__name__)                    
                except:
                    s+="ERROR!\n"
            outputInterface.sort()
            for o in outputInterface:
                s += "  %s\n" % o
            
        self.interfaceLabel.setText(s)        
    
    def SetStageObject(self, stageObject):

        QtCore.QObject.disconnect(self.stagePropertiesView, 
                                  QtCore.SIGNAL("itemSelectionChanged()"), 
                                  self.itemSelectionChanged)
        
        self.propertyLabel.setText("")
        self.__stageObject = stageObject
        self.SetInterfaceDescription()
        
        self.__widgetIndexMap = {}
        propMap = self.__stageObject.GetPropertyMap()
        self.stagePropertiesView.setRowCount(len(propMap))
        self.stagePropertiesView.setColumnCount(2)
        for i,k in enumerate(sorted(propMap.keys())):
            label = QtGui.QTableWidgetItem(k)
            label.setFlags(label.flags() or QtCore.Qt.ItemIsSelectable)
            self.stagePropertiesView.setItem(i,0,label)
            w = self.GetWidgetForType(propMap[k], self.__stageObject.GetProperty(k), self.__stageObject.GetPropertyDescription(k))
            if (isinstance(w,tuple)):
                self.stagePropertiesView.setCellWidget(i,1,w[0])
                w = w[1]
            else:
                self.stagePropertiesView.setCellWidget(i,1,w)
            self.__widgetIndexMap[w] = i

        self.stagePropertiesView.resizeColumnsToContents()
        self.stagePropertiesView.horizontalHeader().setStretchLastSection(True)
        self.stagePropertiesView.setHorizontalHeaderLabels(["Property","Value"])
        
        QtCore.QObject.connect(self.stagePropertiesView,
                               QtCore.SIGNAL("itemSelectionChanged()"), 
                               self.itemSelectionChanged)         
        
        self.stagePropertiesView.setCurrentCell(1,0)
        self.stagePropertiesView.setCurrentCell(0,0)
    
    def propertyItemDataChangedSlot(self, item):
        print(item)       

    
    def itemSelectionChanged(self):
        if (len(self.stagePropertiesView.selectedItems())==1):
            row = self.stagePropertiesView.selectedItems()[0].row()
            property = str(self.stagePropertiesView.item(row,0).text())
            self.propertyLabel.setText(self.__stageObject.GetPropertyDescription(property))
                 
    

###############################################################################
class ChainBuilderGUI(QtGui.QMainWindow):
    
    statusSignal = pyqtSignal(str)
    
    def __init__(self, parent=None):

        # initial setup
        QtGui.QMainWindow.__init__(self, parent, QtCore.Qt.WindowMinMaxButtonsHint)
        self.setWindowTitle("Chain Builder")
        self.setMinimumSize(700,700)
        self.setDockOptions(QtGui.QMainWindow.AllowTabbedDocks)
        self.setAnimated(True)
        self.createMenu()
        self.setWindowIcon(QtGui.QIcon(GetAbsImagePath("chain.png")))
        #self.setStatusBar(QtGui.QStatusBar(self))
        
        self.stageScene = StageScene(self)
        _manager.renderRequestSignal.connect(self.renderRequested)
        QtCore.QObject.connect(self.stageScene, QtCore.SIGNAL("stageSelectedSignal(PyQt_PyObject)"), self.stageSelectedSlot)
        self.stageView = StageView(self.stageScene)
        self.stagePropertiesEditor = StagePropertyEditor()
        
        self.statusBox = QtGui.QTextEdit()
        Chain.Analyze.SetStatusObject(self)
        self.statusSignal.connect(self.appendStatusSlot)
        
        viewFrame = QtGui.QFrame()
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.stageView)
        viewFrame.setLayout(layout)
        self.setCentralWidget(viewFrame)
                
        
        stagePropertiesDock = QtGui.QDockWidget("Stage Properties")
        stagePropertiesDock.setObjectName("Stage Properties")
        stagePropertiesDock.setWidget(self.stagePropertiesEditor)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, stagePropertiesDock)
        #self.tabifiedDockWidgets(stagePropertiesDock)
        
        dock = QtGui.QDockWidget("Status")
        dock.setObjectName("Status")
        dock.setWidget(self.statusBox)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, dock)
        
        self.addToolbar()
    
    
    
    def stageSelectedSlot(self, stage):        
        if (isinstance(stage,StageItem)):
            self.stagePropertiesEditor.SetStageObject(stage.GetStageObject())       
        
        
    def addToolbar(self):
        pointerButton = QtGui.QToolButton()
        pointerButton.setCheckable(True)
        pointerButton.setChecked(True)
        pointerButton.setToolTip("Stage Selection")
        pointerButton.setIcon(QtGui.QIcon(GetAbsImagePath("pointer.png")))
        linePointerButton = QtGui.QToolButton()
        linePointerButton.setCheckable(True)
        linePointerButton.setToolTip("Stage Connector")
        linePointerButton.setIcon(QtGui.QIcon(GetAbsImagePath("linepointer.png")))

        self.pointerTypeGroup = QtGui.QButtonGroup()
        self.pointerTypeGroup.addButton(pointerButton, StageScene.MoveItem)
        self.pointerTypeGroup.addButton(linePointerButton,
                StageScene.InsertLine)
        self.pointerTypeGroup.buttonClicked[int].connect(self.pointerGroupClicked)

        self.pointerToolbar = self.addToolBar("Pointer type")
        self.pointerToolbar.addWidget(pointerButton)
        self.pointerToolbar.addWidget(linePointerButton)
        
        
        
        renderButton = QtGui.QToolButton()
        renderButton.setCheckable(False)
        renderButton.setIcon(QtGui.QIcon(GetAbsImagePath("render.png")))
        
        aaButton = QtGui.QToolButton()
        aaButton.setCheckable(False)
        aaButton.setToolTip("Auto Arrange")
        aaButton.setIcon(QtGui.QIcon(GetAbsImagePath("sendtoback.png")))
        
        self.chainGroup = QtGui.QButtonGroup()
        self.chainGroup.addButton(renderButton, 0)
        self.chainGroup.addButton(aaButton, 1)
        self.chainGroup.buttonClicked[int].connect(self.renderGroupClicked)
        
        self.chainToolbar = self.addToolBar("Chain")
        #self.chainToolbar.addWidget(renderButton)
        self.chainToolbar.addWidget(aaButton)
        
    def pointerGroupClicked(self, i):
        self.stageScene.setMode(self.pointerTypeGroup.checkedId())
        
    def renderGroupClicked(self, i):
        if (i==0): print("render")
        elif (i==1): self.stageScene.autoArrangeStages()

    def createMenu(self):
#        openBundleAct = QtGui.QAction("&Open Bundle File And Images...", self)
#        self.connect(openBundleAct, QtCore.SIGNAL("triggered()"), self.openBundleFile)

        fileMenu = self.menuBar().addMenu("&File")
        
        action = QtGui.QAction(self.tr("&Load..."), self)
        self.connect(action, QtCore.SIGNAL("triggered()"), self.loadChain)
        fileMenu.addAction(action)
        
        action = QtGui.QAction(self.tr("&Save..."), self)
        self.connect(action, QtCore.SIGNAL("triggered()"), self.saveChain)
        fileMenu.addAction(action)
        
        fileMenu.addSeparator()
        
        action = QtGui.QAction(self.tr("&Exit"), self)
        self.connect(action, QtCore.SIGNAL("triggered()"), self.close)
        fileMenu.addAction(action)
        
        
    def loadChain(self):
        ret = QtGui.QFileDialog.getOpenFileName(self, "Load Chain File", ".")
        if (ret != ""):
            Chain.StageRegistry.Load(ret)
            self.stageScene.loadFromRegistry()
        
    def saveChain(self):
        ret = QtGui.QFileDialog.getSaveFileName(self, "Save Chain File", ".")
        if (ret != ""):
            Chain.StageRegistry.Save(ret)
    
    def appendStatus(self, s):
        self.statusSignal.emit(s)

    @pyqtSlot(str)
    def appendStatusSlot(self, s):
        self.statusBox.append(s)
        c = self.statusBox.textCursor()
        c.movePosition(QtGui.QTextCursor.End)
        self.statusBox.setTextCursor(c)

    def renderRequested(self, stageObject):
        self.statusBox.clear()
        _thread.start_new_thread(self.performRender, tuple([stageObject]))
        
    def performRender(self, stageObject):
        print()
        print(Chain.Render(stageObject,"log.txt"))



###############################################################################
if __name__=="__main__":    
    app = QtGui.QApplication(sys.argv)
    gui = ChainBuilderGUI()
    gui.show()
    sys.exit(app.exec_())

    
