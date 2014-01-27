# Copyright (c) 2014, Adam J. Rossi. All rights reserved. See README for licensing details.
import sys, os, copy, collections, math
sys.path.append(os.path.abspath("."))
from PySide import QtCore, QtGui
import Chain, Sources, Common

    
############################################################################### 
class WidgetFrame(QtGui.QFrame):
    def refresh(self):
        self.emit(QtCore.SIGNAL("refresh()"))
        
    def resizeEvent(self, event):
        QtGui.QFrame.resizeEvent(self, event)
        self.emit(QtCore.SIGNAL("resize()"))

############################################################################### 
class CorrespondenceWidget(QtGui.QGraphicsScene):
    
    def __init__(self, stages, imagePair, parent=None):
        QtGui.QGraphicsScene.__init__(self, -400, -400, 800, 800, parent)        

        self.__stages = stages
        self.__imagePair = imagePair
        self.__xTestPosCoeff = 1.0
        self.__yTestPosCoeff = 0.0
        self.__autoZoom = True
        self.__pmRef = None
        self.__pmTest = None
        
    def horizontalSlot(self):
        self.__yTestPosCoeff = 0.0
        if (self.__xTestPosCoeff==0.0):
            self.__xTestPosCoeff = 1.0
        else:
            self.__xTestPosCoeff*=-1
        self.refresh(False)
        
    def verticalSlot(self):
        self.__xTestPosCoeff = 0.0
        if (self.__yTestPosCoeff==0.0):
            self.__yTestPosCoeff = 1.0
        else:
            self.__yTestPosCoeff*=-1
        self.refresh(False)
        
    def autoZoomSlot(self, val):
        self.__autoZoom = (val!=0)
        if (self.__autoZoom): self.views()[0].autoZoom()
        
    def matchIndexChangedSlot(self, val):
        self.refresh(False)
    
    @staticmethod
    def create(stages, label):
        
        images = stages[0].GetOutput()["images"]
        matches = stages[1].GetOutput()["keyMatches"]
        
        ivs = []
        imagePairs = []
        for kmf in matches.GetKeyMatchFiles():
            
            imagePair = sorted([kmf.GetImageIndex1(), kmf.GetImageIndex2()])
            if (imagePair in imagePairs): continue
            imagePairs.append(imagePair)
                
            cw = CorrespondenceWidget(stages,imagePair)
            
            frame = WidgetFrame()
            QtCore.QObject.connect(frame, QtCore.SIGNAL("refresh()"), cw.refresh)
            QtCore.QObject.connect(frame, QtCore.SIGNAL("resize()"), cw.resize)
            
            layout = QtGui.QVBoxLayout()
            blayout = QtGui.QHBoxLayout()
            
            autoZoom = QtGui.QCheckBox("Auto Zoom")
            autoZoom.setCheckState(QtCore.Qt.Checked)
            blayout.addWidget(autoZoom, 1, QtCore.Qt.AlignLeft)
            QtCore.QObject.connect(autoZoom, QtCore.SIGNAL("stateChanged(int)"), cw.autoZoomSlot)
            
            cw._sbMatch = QtGui.QSpinBox()
            cw._sbMatch.setRange(-1,0)
            cw._sbMatch.setValue(-1)
            QtCore.QObject.connect(cw._sbMatch, QtCore.SIGNAL("valueChanged(int)"), cw.matchIndexChangedSlot)
            blayout.addWidget(QtGui.QLabel("Match Index:"))
            blayout.addWidget(cw._sbMatch, 1, QtCore.Qt.AlignLeft)
            
            fliplayout = QtGui.QHBoxLayout()
            fliplayout.setContentsMargins(0,0,0,0)
            
            horizontal = QtGui.QPushButton("Horizontal Flip")
            QtCore.QObject.connect(horizontal, QtCore.SIGNAL("clicked()"), cw.horizontalSlot)
            fliplayout.addWidget(horizontal)
            
            vertical = QtGui.QPushButton("Vertical Flip")
            QtCore.QObject.connect(vertical, QtCore.SIGNAL("clicked()"), cw.verticalSlot)
            fliplayout.addWidget(vertical)
            
            flipFrame = QtGui.QFrame()
            flipFrame.setLayout(fliplayout)
            blayout.addWidget(flipFrame, 1, QtCore.Qt.AlignLeft)
            
            blayout.addWidget(
                QtGui.QLabel("%s | %s"%(images.GetImages()[kmf.GetImageIndex1()].GetFileName(),
                                        images.GetImages()[kmf.GetImageIndex2()].GetFileName())))
            
            iv = ImageView(cw)
            layout.addLayout(blayout)
            layout.addWidget(iv)
            frame.setLayout(layout)
            ivs.append(frame)
        return ivs
    
    def createPixmap(self, imagePath):
        return QtGui.QPixmap(imagePath)
    
    def createFeaturePoint(self, coord, parent=None, scene=None):
        pt = QtGui.QGraphicsEllipseItem(-2.0,-2.0, 4.0,4.0, 
                                        parent,scene)
        pt.setFlag(QtGui.QGraphicsItem.ItemIsMovable, False)
        pt.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, False)
        pt.setFlag(QtGui.QGraphicsItem.ItemIsFocusable, False)
        pt.setBrush(QtGui.QBrush(QtGui.QColor(250,250,10,150)))
        pt.setPos(coord[0],coord[1])
        return pt
    
    def resize(self):
        if (self.__autoZoom): self.views()[0].autoZoom()
        
    def refresh(self, reloadImages=True):
        self.clear()
        
        images = self.__stages[0].GetOutput()["images"]
        matches = self.__stages[1].GetOutput()["keyMatches"]
        
        mykmf = None
        for kmf in matches.GetKeyMatchFiles():
            
            imagePair = sorted([kmf.GetImageIndex1(), kmf.GetImageIndex2()])
            if (imagePair != self.__imagePair): continue
            mykmf = kmf
            break
        
        if (mykmf==None):
            print "[CorrespondenceWidget] Warning: did not find key matches for: " + str(self.__imagePair)
            return
        
        if (reloadImages or (self.__pmRef==None)):
            self.__pmRef = self.createPixmap(images.GetImages()[self.__imagePair[0]].GetFilePath())
        if (reloadImages or (self.__pmTest==None)):
            self.__pmTest = self.createPixmap(images.GetImages()[self.__imagePair[1]].GetFilePath())
        
        
        tiRef = QtGui.QGraphicsPixmapItem(self.__pmRef)
        tiRef.setFlag(QtGui.QGraphicsItem.ItemIsMovable, False)
        tiRef.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, False)
        tiRef.setFlag(QtGui.QGraphicsItem.ItemIsFocusable, False)

        tiTest = QtGui.QGraphicsPixmapItem(self.__pmTest)
        tiTest.setFlag(QtGui.QGraphicsItem.ItemIsMovable, False)
        tiTest.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, False)
        tiTest.setFlag(QtGui.QGraphicsItem.ItemIsFocusable, False)        
        
        self.addItem(tiRef)
        self.addItem(tiTest)

        SPACING = 50
        tiTest.moveBy(self.__xTestPosCoeff*(tiRef.sceneBoundingRect().width()+SPACING),
                      self.__yTestPosCoeff*(tiRef.sceneBoundingRect().height()+SPACING))
        
        colors = (QtCore.Qt.red, QtCore.Qt.green, QtCore.Qt.yellow, QtCore.Qt.blue)
        lis = []

        self._sbMatch.setMaximum(len(mykmf.GetMatches())-1)
        
        for i,(d0,d1,m0,m1) in enumerate(mykmf.GetMatches()):
            
            if (self._sbMatch.value()>=0):
                i = self._sbMatch.value()
                (d0,d1,m0,m1) = mykmf.GetMatches()[self._sbMatch.value()]
            
            match = ((d1.Column(),d1.Row()),
                     (d0.Column(),d0.Row()))
            
            self.createFeaturePoint(match[0], tiTest, self)
            self.createFeaturePoint(match[1], tiRef, self)
            
            pointRef = tiRef.mapToScene(match[1][0], match[1][1])
            pointTest = tiTest.mapToScene(match[0][0], match[0][1])
            li = QtGui.QGraphicsLineItem(pointRef.x(),pointRef.y(),
                                         pointTest.x(),pointTest.y(),
                                         scene=self)
            li.setPen(QtGui.QPen(colors[i%len(colors)], 1))
            lis.append(li)
            
            if (self._sbMatch.value()>=0): break

        self.__matchesGroup = self.createItemGroup(lis)
        
        self.setSceneRect(self.itemsBoundingRect())
        if (self.__autoZoom): self.views()[0].autoZoom()
    

###############################################################################
class FeatureWidget(QtGui.QGraphicsScene):
    
    def __init__(self, stages, index, parent=None):
        QtGui.QGraphicsScene.__init__(self, -400, -400, 800, 800, parent)        

        self.__stages = stages
        self.__index = index
        self.__autoZoom = True
        
    @staticmethod
    def create(stages, label):
        kds = stages[1].GetOutput()["keypointDescriptors"]
        ivs = []
        for i in range(len(kds.GetDescriptors())):
            w = FeatureWidget(stages,i)
            iv = ImageView(w)
            
            frame = WidgetFrame()
            QtCore.QObject.connect(frame, QtCore.SIGNAL("refresh()"), w.refresh)
            QtCore.QObject.connect(frame, QtCore.SIGNAL("resize()"), w.resize)
            
            layout = QtGui.QVBoxLayout()
            blayout = QtGui.QHBoxLayout()
            
            autoZoom = QtGui.QCheckBox("Auto Zoom")
            autoZoom.setCheckState(QtCore.Qt.Checked)
            blayout.addWidget(autoZoom, 1, QtCore.Qt.AlignLeft)
            QtCore.QObject.connect(autoZoom, QtCore.SIGNAL("stateChanged(int)"), w.autoZoomSlot)
            
            blayout.addWidget(QtGui.QLabel(stages[0].GetOutput()["images"].GetImages()[i].GetFileName()))                
            
            layout.addLayout(blayout)
            layout.addWidget(iv)
            frame.setLayout(layout)
            
            ivs.append(frame)
            
        return ivs
    
    def createPixmap(self, imagePath):
        pm = QtGui.QGraphicsPixmapItem(QtGui.QPixmap(imagePath))
        pm.setFlag(QtGui.QGraphicsItem.ItemIsMovable, False)
        pm.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, False)
        pm.setFlag(QtGui.QGraphicsItem.ItemIsFocusable, False)
        return pm
    
    def createFeaturePoint(self, coord, parent=None, scene=None):
        pt = QtGui.QGraphicsEllipseItem(-2.0,-2.0, 4.0,4.0, 
                                        parent,scene)
        pt.setFlag(QtGui.QGraphicsItem.ItemIsMovable, False)
        pt.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, False)
        pt.setFlag(QtGui.QGraphicsItem.ItemIsFocusable, False)
        pt.setBrush(QtGui.QBrush(QtGui.QColor(250,250,10,150)))
        pt.setPos(coord[0],coord[1])
        return pt
    
    def resize(self):
        if (self.__autoZoom): self.views()[0].autoZoom()
        
    def autoZoomSlot(self, val):
        self.__autoZoom = (val!=0)
        if (self.__autoZoom): self.views()[0].autoZoom()
        
    def refresh(self):
        self.clear()
        
        image = self.__stages[0].GetOutput()["images"].GetImages()[self.__index]
        kd = self.__stages[1].GetOutput()["keypointDescriptors"].GetDescriptors()[self.__index]
        
        pm = self.createPixmap(image.GetFilePath())
        self.addItem(pm)
            
        for d in kd.GetDescriptors():
            self.createFeaturePoint((d.Column(),d.Row()), pm, self)
                    
        self.setSceneRect(self.itemsBoundingRect())
        if (self.__autoZoom): self.views()[0].autoZoom() 
    
############################################################################### 
class ImageWidget(QtGui.QGraphicsScene):
    
    def __init__(self, stage, outputName, index=-1, parent=None):
        QtGui.QGraphicsScene.__init__(self, 0,0, 800,800, parent)        
        self.__stage = stage
        self.__outputName = outputName
        self.__index = index
        self.__pixmapItem = QtGui.QGraphicsPixmapItem(QtGui.QPixmap())
        self.__pixmapItem.setFlag(QtGui.QGraphicsItem.ItemIsMovable, True) #False)
        self.__pixmapItem.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, False)
        self.__pixmapItem.setFlag(QtGui.QGraphicsItem.ItemIsFocusable, False)
        self.__pixmapItem.setTransformationMode(QtCore.Qt.SmoothTransformation)
        self.addItem(self.__pixmapItem)
        self.__loaded = False
        self.__autoZoom = True

    @staticmethod
    def create(stage, label):
        
        widgets = []
        
        oif = stage.GetOutputInterface()

        if ("image" in oif.keys()):    
            outputName = "image"
            numImages = 1
        elif ("images" in oif.keys()): 
            outputName = "images"
            numImages = len(stage.GetOutput()["images"].GetImages())
        else: 
            raise Exception("Unknown stage interface for ImageWidget")
        
        
        for i in range(numImages):
            
            if (outputName=="image"): index = -1
            else: index = i
            
            w = ImageWidget(stage, outputName, index=index)
            iv = ImageView(w)
            
            frame = WidgetFrame()
            QtCore.QObject.connect(frame, QtCore.SIGNAL("refresh()"), w.refresh)
            QtCore.QObject.connect(frame, QtCore.SIGNAL("resize()"), w.resize)
            
            layout = QtGui.QVBoxLayout()
            blayout = QtGui.QHBoxLayout()
            
            autoZoom = QtGui.QCheckBox("Auto Zoom")
            autoZoom.setCheckState(QtCore.Qt.Checked)
            blayout.addWidget(autoZoom, 1, QtCore.Qt.AlignLeft)
            QtCore.QObject.connect(autoZoom, QtCore.SIGNAL("stateChanged(int)"), w.autoZoomSlot)
            
            if (index<0):
                blayout.addWidget(QtGui.QLabel(stage.GetOutput()[outputName].GetFileName()))
            else:
                blayout.addWidget(QtGui.QLabel(stage.GetOutput()[outputName].GetImages()[index].GetFileName()))
                
            layout.addLayout(blayout)
            layout.addWidget(iv)
            frame.setLayout(layout)            
            widgets.append(frame)
            
        return widgets
                    
    
    def autoZoomSlot(self, val):
        self.__autoZoom = (val!=0)
        if (self.__autoZoom): 
            self.setSceneRect(self.itemsBoundingRect())
            self.views()[0].autoZoom()
        
    def resize(self):
        if (self.__autoZoom): 
            self.setSceneRect(self.itemsBoundingRect())
            self.views()[0].autoZoom()        
        
    def refresh(self):

        imagePath = ""
        try:
            if (self.__index<0):
                imagePath = self.__stage.GetOutput()[self.__outputName].GetFilePath()
            else:
                imagePath = self.__stage.GetOutput()[self.__outputName].GetImages()[self.__index].GetFilePath()
        except Exception, e:
            print "Exception rendering visualization image:" + str(e)
            print
            
        self.__pixmapItem.setPixmap(QtGui.QPixmap())
        self.__pixmapItem.setPixmap(QtGui.QPixmap(imagePath))
        if (not self.__loaded):
            self.setSceneRect(self.itemsBoundingRect())
            self.__loaded = True
        self.resize()

            
############################################################################### 
class ImageView(QtGui.QGraphicsView):
    def __init__(self, graphicsScene=None):
        QtGui.QGraphicsView.__init__(self, graphicsScene)
        self.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)
        self.setViewportUpdateMode(QtGui.QGraphicsView.FullViewportUpdate)
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setRenderHint(QtGui.QPainter.TextAntialiasing)
        self.setRenderHint(QtGui.QPainter.SmoothPixmapTransform)
        self.__graphicsScene = graphicsScene
        
    def wheelEvent(self, event):
        self.scaleView(math.pow(2.0, -event.delta() / 240.0))
    
    def scaleView(self, scaleFactor):
        factor = self.matrix().scale(scaleFactor, scaleFactor).mapRect(QtCore.QRectF(0, 0, 1, 1)).width()
        self.scale(scaleFactor, scaleFactor)
        
    def refresh(self):
        self.__graphicsScene.refresh()
    
    def autoZoom(self):
        self.fitInView(self.__graphicsScene.itemsBoundingRect(), QtCore.Qt.KeepAspectRatio)

###############################################################################
class cgSpinBoxSlider(QtGui.QFrame):
    def __init__(self, name, initVal, minVal, maxVal):
        QtGui.QFrame.__init__(self)
        self.__disableSliderSlot = False
        
        self.__slider = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.__slider.setRange(0,100)
        self.__slider.setSingleStep(1)
        self.__slider.setPageStep(10)
        
        self.__spinbox = cgSpinBox(name)
        self.__spinbox.setMinimum(minVal)
        self.__spinbox.setMaximum(maxVal)

        layout = QtGui.QHBoxLayout()
        layout.setContentsMargins(0,0,5,0)
        layout.addWidget(self.__slider)
        layout.addWidget(self.__spinbox)
        self.setLayout(layout)

        QtCore.QObject.connect(self.__spinbox, QtCore.SIGNAL("valueChangedSignal(object,object)"), self.valChangedSlot)
        QtCore.QObject.connect(self.__slider, QtCore.SIGNAL("valueChanged(int)"), self.sliderValChangedSlot)
        
        self.__spinbox.setValue(initVal)
        
    
    def valChangedSlot(self, name,val):
        self.emit(QtCore.SIGNAL("valueChangedSignal(object,object)"), name,val)
        self.__disableSliderSlot = True
        self.__slider.setValue((val-self.__spinbox.minimum())/float(self.__spinbox.maximum()-self.__spinbox.minimum())*100)
        self.__disableSliderSlot = False

    def sliderValChangedSlot(self, val):
        if (self.__disableSliderSlot): return
        sbVal = int(round((self.__spinbox.maximum() - self.__spinbox.minimum()) * (val/100.0) + self.__spinbox.minimum()))
        self.__spinbox.setValue(sbVal)
        
class cgDoubleSpinBoxSlider(QtGui.QFrame):
    def __init__(self, name, initVal, minVal, maxVal):
        QtGui.QFrame.__init__(self)
        self.__disableSliderSlot = False
        
        self.__slider = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.__slider.setRange(0,100)
        self.__slider.setSingleStep(1)
        self.__slider.setPageStep(10)
        
        self.__spinbox = cgDoubleSpinBox(name)
        self.__spinbox.setMinimum(minVal)
        self.__spinbox.setMaximum(maxVal)

        layout = QtGui.QHBoxLayout()
        layout.setContentsMargins(0,0,5,0)
        layout.addWidget(self.__slider)
        layout.addWidget(self.__spinbox)
        self.setLayout(layout)

        QtCore.QObject.connect(self.__spinbox, QtCore.SIGNAL("valueChangedSignal(object,object)"), self.valChangedSlot)
        QtCore.QObject.connect(self.__slider, QtCore.SIGNAL("valueChanged(int)"), self.sliderValChangedSlot)
        
        self.__spinbox.setValue(initVal)
        
    
    def valChangedSlot(self, name,val):
        self.emit(QtCore.SIGNAL("valueChangedSignal(object,object)"), name,val)
        self.__disableSliderSlot = True
        self.__slider.setValue((val-self.__spinbox.minimum())/float(self.__spinbox.maximum()-self.__spinbox.minimum())*100)
        self.__disableSliderSlot = False

    def sliderValChangedSlot(self, val):
        if (self.__disableSliderSlot): return
        sbVal = (self.__spinbox.maximum() - self.__spinbox.minimum()) * (val/100.0) + self.__spinbox.minimum()
        self.__spinbox.setValue(sbVal)

class cgSpinBox(QtGui.QSpinBox):
    def __init__(self, name):
        QtGui.QSpinBox.__init__(self)
        self.__name = name
        QtCore.QObject.connect(self, QtCore.SIGNAL("valueChanged(int)"), self.valChangedSlot)
    def valChangedSlot(self, val):
        self.emit(QtCore.SIGNAL("valueChangedSignal(object,object)"), self.__name, val)

class cgDoubleSpinBox(QtGui.QDoubleSpinBox):
    def __init__(self, name):
        QtGui.QDoubleSpinBox.__init__(self)
        self.__name = name
        QtCore.QObject.connect(self, QtCore.SIGNAL("valueChanged(double)"), self.valChangedSlot)
    def valChangedSlot(self, val):
        self.emit(QtCore.SIGNAL("valueChangedSignal(object,object)"), self.__name, val)

class cgCheckBox(QtGui.QCheckBox):
    def __init__(self, name):
        QtGui.QCheckBox.__init__(self)
        self.__name = name
        QtCore.QObject.connect(self, QtCore.SIGNAL("stateChanged(int)"), self.valChangedSlot)
    def valChangedSlot(self, val):
        self.emit(QtCore.SIGNAL("valueChangedSignal(object,object)"), self.__name, (val!=0))

class cgComboBox(QtGui.QComboBox):
    def __init__(self, name):
        QtGui.QComboBox.__init__(self)
        self.__name = name
        QtCore.QObject.connect(self, QtCore.SIGNAL("currentIndexChanged(const QString&)"), self.valChangedSlot)
    def valChangedSlot(self, val):
        self.emit(QtCore.SIGNAL("valueChangedSignal(object,object)"), self.__name, str(val))

class cgLineEdit(QtGui.QLineEdit):
    def __init__(self, name):
        QtGui.QLineEdit.__init__(self)
        self.__name = name
        QtCore.QObject.connect(self, QtCore.SIGNAL("textChanged(const QString&)"), self.valChangedSlot)
    def valChangedSlot(self, val):
        self.emit(QtCore.SIGNAL("valueChangedSignal(object,object)"), self.__name, str(val))
                         
###############################################################################
class PropertyEditor(QtGui.QWidget):
    
    def __init__(self, stage, propNames, propRanges, parent=None):
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
        
        self.__stage = stage
        self.__initalPropNames = propNames
        self.__propRanges = propRanges
        
        self.SetProperties()
        self.SetInterfaceDescription()
        
        self.__propModifiedTimer = QtCore.QTimer()
        self.__propModifiedTimer.setSingleShot(True)
        self.__propModifiedTimer.setInterval(750) # 750ms
        QtCore.QObject.connect(self.__propModifiedTimer, QtCore.SIGNAL("timeout()"), self.propModifiedSlot)
        
        
    def SetProperties(self):
        
        if (self.__initalPropNames==None):
            self.__propNames = sorted(self.__stage.GetPropertyMap().keys())
        else:
            self.__propNames = self.__initalPropNames
        
        self.__widgetIndexMap = {}
        self.stagePropertiesView.clear()
        self.stagePropertiesView.setRowCount(len(self.__propNames))
        self.stagePropertiesView.setColumnCount(2)
        
        for i,k in enumerate(self.__propNames):
            
            label = QtGui.QTableWidgetItem(k)
            label.setFlags(label.flags() or QtCore.Qt.ItemIsSelectable)
            self.stagePropertiesView.setItem(i,0,label)
            
            propRange = None
            if (self.__propRanges.has_key(k)):
                propRange = self.__propRanges[k]
            
            w = self.GetWidgetForType(k,
                                      type(self.__stage.GetProperty(k)),
                                      self.__stage.GetProperty(k),
                                      self.__stage.GetPropertyDescription(k),
                                      propRange)
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
    
    def GetWidgetForType(self, name, t, initVal, pd, pRange=None):
        if (t==type(0)):
            if (pRange):
                initVal = max(pRange[0], min(pRange[1],initVal))  # clip initVal
                sb = cgSpinBoxSlider(name, initVal, *pRange)
            else:
                MIN_VAL = -pow(2,31)
                MAX_VAL = pow(2,31)-1
                initVal = max(MIN_VAL, min(MAX_VAL,initVal))  # clip initVal
                sb = cgSpinBox(name)
                sb.setMinimum(MIN_VAL)
                sb.setMaximum(MAX_VAL)
                sb.setValue(initVal)
                
            sb.installEventFilter(self)
            QtCore.QObject.connect(sb, QtCore.SIGNAL("valueChangedSignal(object,object)"), self.valueChangedSlot)
            return sb
        elif (t==type(0.0)):
            if (pRange):
                initVal = max(pRange[0], min(pRange[1],initVal))  # clip initVal
                sb = cgDoubleSpinBoxSlider(name, initVal, *pRange)
            else:
                sb = cgDoubleSpinBox(name)
                sb.setMinimum(-sys.maxint)
                sb.setMaximum(sys.maxint)
                sb.setValue(initVal)
                
            sb.installEventFilter(self)
            QtCore.QObject.connect(sb, QtCore.SIGNAL("valueChangedSignal(object,object)"), self.valueChangedSlot)
            return sb
        elif (t==type(True)):
            cb = cgCheckBox(name)
            cb.setChecked(initVal)
            cb.installEventFilter(self)
            QtCore.QObject.connect(cb, QtCore.SIGNAL("valueChangedSignal(object,object)"), self.valueChangedSlot)
            frame = QtGui.QFrame()
            layout = QtGui.QHBoxLayout()
            layout.setContentsMargins(5,0,0,0)
            layout.addWidget(cb)
            frame.setLayout(layout)
            return frame, cb
        elif ((t==type("")) and ("{" in pd) and ("}" in pd)):
            cb = cgComboBox(name)
            cb.installEventFilter(self)
            cb.addItems([x.strip() for x in pd[pd.find("{")+1:pd.find("}")].split(",")])
            cb.setCurrentIndex(cb.findText(initVal))         
            QtCore.QObject.connect(cb, QtCore.SIGNAL("valueChangedSignal(object,object)"), self.valueChangedSlot)
            return cb
        else:
            try:
                le = cgLineEdit(name)
                le.setText(initVal)
                le.installEventFilter(self)
                QtCore.QObject.connect(le, QtCore.SIGNAL("valueChangedSignal(object,object)"), self.valueChangedSlot)
                return le
            except Exception,e:
                print "WARNING: Unable to create property widget for: " + name
                print e
                return QtGui.QFrame()
    
    def SetInterfaceDescription(self):
        
        s = "[%s]\n\n" % self.__stage.GetStageDescription()
        s += "Input Interface:\n"
        if (self.__stage.GetInputInterface()==None):
            s += "  (None)\n"
        else:
            inputInterface = []
            for kv in self.__stage.GetInputInterface().items():    
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
        if (self.__stage.GetOutputInterface()==None):
            s += "  (None)\n"
        else:
            outputInterface = []
            for kv in self.__stage.GetOutputInterface().items():    
                try:
                    outputName,outputType = kv
                    outputInterface.append(outputType.__name__)                    
                except:
                    s+="ERROR!\n"
            outputInterface.sort()
            for o in outputInterface:
                s += "  %s\n" % o
            
        self.interfaceLabel.setText(s)
        
    def valueChangedSlot(self, name, val):
        props = self.__stage.GetPropertyMap().keys()
        self.__stage.SetProperty(name,val)
        if (props!=self.__stage.GetPropertyMap().keys()):
            self.SetProperties()
        self.__propModifiedTimer.start()
        
    def eventFilter(self, o, event):
        if (event.type() == QtCore.QEvent.Enter and o in self.__widgetIndexMap):
            self.stagePropertiesView.setCurrentCell(self.__widgetIndexMap[o],0)
        return False
    
    def itemSelectionChanged(self):
        if (len(self.stagePropertiesView.selectedItems())==1):
            row = self.stagePropertiesView.selectedItems()[0].row()
            property = str(self.stagePropertiesView.item(row,0).text())
            self.propertyLabel.setText(self.__stage.GetPropertyDescription(property))
            
    def propModifiedSlot(self):
        self.emit(QtCore.SIGNAL("propertyModifiedSignal()"))
                 

###############################################################################
class ChainGUI(QtGui.QMainWindow):
    
    def __init__(self,
                 stagesVisualizations,          # stages with outputs to visualize [(stage,label,visualization widget), ...]
                 stagesDisplayProperty,         # stages that have properties that need manipulating [(stage,stageLabel,[property name,...]), ...]
                 stagesPropertyRanges={}):      # property ranges {stage:{property name:(min, max),...}, ...}
        # QMainWindow setup
        QtGui.QMainWindow.__init__(self, None, QtCore.Qt.WindowMinMaxButtonsHint)
        self.setWindowTitle("Chain GUI")
        self.setMinimumSize(700,700)
        self.setDockOptions(QtGui.QMainWindow.AllowTabbedDocks)
        self.setAnimated(True)
        self.createMenu()
        
        self.__stagesVisualizations = stagesVisualizations
        self.__visualizationsInitialized = False
        
        # create property editors for stages
        self.initalizePropertyEditors(stagesDisplayProperty, stagesPropertyRanges)

        # create status box
        self.statusBox = QtGui.QTextEdit()
        self.statusBox.setMaximumHeight(200)
        Chain.Analyze.SetStatusObject(self)
        QtCore.QObject.connect(self, QtCore.SIGNAL("statusSignal(object)"), self.appendStatusSlot)        
        dock = QtGui.QDockWidget("Status")
        dock.setObjectName("Status")
        dock.setWidget(self.statusBox)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, dock)

        # create toolbar
        self.addToolbar()
        
    
    def initalizePropertyEditors(self, stagesDisplayProperty, stagesPropertyRanges):
        prevDw = None
        firstDw = None
        for sdp in stagesDisplayProperty:
            if (len(sdp)==3):
                stage,stageLabel,propNames = sdp
            elif (len(sdp)==2):
                stage,stageLabel = sdp
                propNames = None
            else:
                raise Exception("Incorrect stage display property definition")
            
            propRanges = {}
            if (stagesPropertyRanges.has_key(stage)):
                propRanges = stagesPropertyRanges[stage]
            
            pe = PropertyEditor(stage, propNames, propRanges)
            QtCore.QObject.connect(pe, QtCore.SIGNAL("propertyModifiedSignal()"), self.propertyModifiedSlot)
            dw = QtGui.QDockWidget(stageLabel)
            dw.setObjectName(stageLabel)
            dw.setWidget(pe)
            self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dw)
            if (prevDw): self.tabifyDockWidget(prevDw, dw)
            if (not firstDw): firstDw = dw
            prevDw = dw
        firstDw.raise_()
        
    def addToolbar(self):
        
        toolbar = self.addToolBar("Shortcuts")
        self.buttonGroup = QtGui.QButtonGroup()
       
        for i, cmd in enumerate(["Render Chain",
                                 "Save Screenshot"]):
            button = QtGui.QToolButton()
            button.setText(cmd)
            button.setCheckable(False)
            self.buttonGroup.addButton(button, i)
            toolbar.addWidget(button)
            
        self.buttonGroup.buttonClicked[int].connect(self.shorcutClicked)
        
        toolbar.addSeparator()
        self.__autoRender = False
        ar = QtGui.QCheckBox("Auto Render")
        QtCore.QObject.connect(ar, QtCore.SIGNAL("stateChanged(int)"), self.autoRenderSlot)
        toolbar.addWidget(ar) 
        
    def autoRenderSlot(self, val):
        self.__autoRender = (val!=0)
        
    def propertyModifiedSlot(self):
        if (self.__autoRender): self.renderChain()
    
    def shorcutClicked(self, i):
        fMap = [self.renderChain,
                self.saveImage]
        try:
            QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
            fMap[i]()
        except:
            raise
        finally:
            QtGui.QApplication.restoreOverrideCursor()
            
    def initializeVisualizations(self):
        
        prevDw = None
        firstDw = None
        self.__stages = []
        self.__visualizations = []
        for stage,stageLabel,widget in self.__stagesVisualizations:
            
            # keep list of stages
            if (isinstance(stage,collections.Iterable)):
                self.__stages.extend(stage)
            else:
                self.__stages.append(stage)
            
            # create visualization widget
            widgets = widget.create(stage,stageLabel)
            if (not isinstance(widgets,collections.Iterable)): widgets = [widgets]
                
            for i,w in enumerate(widgets):
                self.__visualizations.append(w)
                
                # dock the widget
                sl = stageLabel
                if (len(widgets)>1): sl+=" (%d)"%i
                dw = QtGui.QDockWidget(sl)
                dw.setObjectName(sl)
                dw.setWidget(w)
                self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, dw)
                if (prevDw): self.tabifyDockWidget(prevDw, dw)
                if (not firstDw): firstDw = dw
                prevDw = dw

        if (firstDw): firstDw.raise_()
        
            
    def renderChain2(self):
        self.statusBox.clear()
        
        if (not self.__visualizationsInitialized):
            
            # get all tail stages, build "force run" map
            tails = []
            forceRuns = {}
            for stage in Chain.StageRegistry.registry.GetStageInstances():
                if (len(stage.GetOutputStages())==0): tails.append(stage)
                if ("Force Run" in stage.GetPropertyMap().keys()):
                    forceRuns[stage] = stage.GetProperty("Force Run")            
            
            try:
                # render once with the chain state as the user defined it
                Chain.Render(tails)
            
            except:
                pass
            
            finally:
                # set all force runs to False as image views are initialized
                for stage in forceRuns.keys():
                    stage.SetProperty("Force Run", False)
                
                self.initializeVisualizations()
                self.__visualizationsInitialized = True
                
                for vis in self.__visualizations: 
                    try: vis.refresh()
                    except: pass
    
                # revert force runs
                for stage,fr in forceRuns.iteritems():
                    stage.SetProperty("Force Run", fr)

        else:
            #for stage in self.__stages: stage.Reset()
            
            for vis in self.__visualizations:
                try: vis.refresh()
                except: pass
                
    
    def renderChain(self):
        self.statusBox.clear()
        
        tails = []
        for stage in Chain.StageRegistry.registry.GetStageInstances():
            if (len(stage.GetOutputStages())==0): tails.append(stage)
        try:
            Chain.Render(tails)
        except:
            pass
        
        if (not self.__visualizationsInitialized):            
            self.initializeVisualizations()
            self.__visualizationsInitialized = True            
        
        for vis in self.__visualizations: 
            try: vis.refresh()
            except: pass


    def saveImage(self):
        sz = self.mosaicScene.sceneRect()
        img = QtGui.QImage(sz.width(),sz.height(), QtGui.QImage.Format_ARGB32_Premultiplied)
        p = QtGui.QPainter(img)
        self.mosaicScene.render(p)
        p.end()
        img.save("scene.png");
    
    def createMenu(self):
        
        fileMenu = self.menuBar().addMenu("&File")
        
        fileMenu.addSeparator()
        
        action = QtGui.QAction(self.tr("&Exit"), self)
        self.connect(action, QtCore.SIGNAL("triggered()"), self.close)
        fileMenu.addAction(action)
               
    def appendStatus(self, s):
        self.emit(QtCore.SIGNAL("statusSignal(object)"), s)

    def appendStatusSlot(self, s):
        self.statusBox.append(s)
        c = self.statusBox.textCursor()
        c.movePosition(QtGui.QTextCursor.End)
        self.statusBox.setTextCursor(c)
        
def display(stagesVisualizations,          # stages with outputs to visualize [(stage,label,visualization widget), ...]
            stagesDisplayProperty,         # stages that have properties that need manipulating [(stage,stageLabel,[property name,...]), ...]
            stagesPropertyRanges={}):      # property ranges {stage:{property name:(min, max),...}, ...}
    app = QtGui.QApplication(sys.argv)
    gui = ChainGUI(stagesVisualizations, stagesDisplayProperty, stagesPropertyRanges)
    gui.show()
    return app.exec_()
    
###############################################################################
if __name__=="__main__":
    raise Exception("Do not run directly, use display method")

    
