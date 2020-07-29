# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing details.
import sys, os, glob
sys.path.append(os.path.abspath(".."))

from PyQt4 import QtCore, QtGui, QtXml
from catena.code import Common
from catena.code.Visualization import Dialogs


###############################################################################
class TiePoint(QtGui.QGraphicsEllipseItem):
    def __init__(self, setNumber=None, parent=None):
        QtGui.QGraphicsEllipseItem.__init__(self, parent)
        self.setZValue(10)
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
        #self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable)
        self.setFlag(QtGui.QGraphicsItem.ItemIsFocusable)
        
        self.setBrush(QtGui.QBrush(QtGui.QColor(250,250,10,150)))
        self.setRect(-5,-5, 10,10)

        # label
        if (setNumber!=None):
            label = QtGui.QGraphicsTextItem(str(setNumber), self)
            label.setPos(0,0)

    def getCoordinate(self):
        return self.pos()


###############################################################################
class TiePoints(QtGui.QGroupBox):
    
    def __init__(self, tiepointsFile, parent=None):
        QtGui.QGroupBox.__init__(self, "Tie Points", parent)
        
        formLayout = QtGui.QFormLayout()

        self._tiepointsComboBox = QtGui.QComboBox()
        formLayout.addRow("Tiepoints", self._tiepointsComboBox)
        self.connect(self._tiepointsComboBox, QtCore.SIGNAL("currentIndexChanged(int)"), self.tiepointChangedSlot) 
        
        self.setLayout(formLayout)
        self.SetTiepointsFile(tiepointsFile)        
    
    @QtCore.pyqtSignature("int")
    def tiepointChangedSlot(self, val):
        self.emit(QtCore.SIGNAL("tiepointChangedSignal(PyQt_PyObject)"), self.selectedTiepoint())
        
    def SetTiepointsFile(self, tiepointsFile):
        self._tiepointsFile = tiepointsFile
        self.loadWidgets()
    
    def selectedTiepoint(self):
        selectedItem = self._tiepointsComboBox.itemData(self._tiepointsComboBox.currentIndex())
        if (selectedItem.isValid()): return selectedItem.toPyObject()
        else: return None        
        
    def loadWidgets(self):
        self._tiepointsComboBox.clear()
        
        if (self._tiepointsFile==None): return
        
        f = open(self._tiepointsFile,"r")
        for i,l in enumerate(f.readlines()):
            uv,xy = l.split("  ")
            u,v = tuple(float(x) for x in uv.split(","))
            x,y = tuple(float(x) for x in xy.split(","))
            self._tiepointsComboBox.addItem("Tiepoint %d" % i, QtCore.QVariant([u,v,x,y]))
        f.close()
        


###############################################################################
class ImageWidget(QtGui.QGroupBox):
    
    def __init__(self, image, parent=None):
        QtGui.QGroupBox.__init__(self, image.GetFileName(), parent)
        
        self._gs = QtGui.QGraphicsScene()
        self._gv = QtGui.QGraphicsView(self._gs)
        self._gv.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)
        self._pixmap = QtGui.QGraphicsPixmapItem(QtGui.QPixmap(image.GetFilePath()))
        self._gs.addItem(self._pixmap)
        
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self._gv)
        self.setLayout(layout)
        
        self._tiePoint = None
        self._defaultColor = self.palette().color(QtGui.QPalette.Window)
        
    def setHighlight(self):
        self.setAutoFillBackground(True)
        pal = QtGui.QPalette(self.palette())
        pal.setColor(QtGui.QPalette.Window, QtCore.Qt.red)
        self.setPalette(pal);
    
    def clearHighlight(self):
        self.setAutoFillBackground(False)
        pal = QtGui.QPalette(self.palette())
        pal.setColor(QtGui.QPalette.Window, self._defaultColor)
        self.setPalette(pal);
        
    def addPoint(self, coord):
        self._tiePoint = TiePoint()
        self._tiePoint.setPos(coord[0], coord[1])
        self._gs.addItem(self._tiePoint)
        self._gv.centerOn(self._tiePoint)
        
    def removePoints(self):
        if (self._tiePoint!=None):
            self._gs.removeItem(self._tiePoint)
            # remoteItem doesn't seem to be enough for Qt
            del self._tiePoint
            self._tiePoint = None            
            

###############################################################################
class TiepointGUI(QtGui.QMainWindow):
    
    DEFAULT_IMAGES_PER_ROW = 2
    
    def __init__(self, parent=None):

        # initial setup
        QtGui.QMainWindow.__init__(self, parent, QtCore.Qt.WindowMinMaxButtonsHint)
        self.setWindowTitle("Tiepoint Viewer")
        self.setMinimumSize(500,500)
        self.setDockOptions(QtGui.QMainWindow.AllowTabbedDocks)
        self.setAnimated(True)
        self.createMenu()
        
        self._imageWidgets = {}
        
        self._tiepointGroupBox = TiePoints(None, self)
        self.connect(self._tiepointGroupBox, QtCore.SIGNAL("tiepointChangedSignal(PyQt_PyObject)"), self.tiepointChangedSlot)        

        self._imageWidgetLayout = QtGui.QGridLayout()
        
        self._viewFrame = QtGui.QFrame()
        self._mainLayout = QtGui.QGridLayout()
        kpAndIW = QtGui.QHBoxLayout()
        kpAndIW.addWidget(self._tiepointGroupBox)
        self._mainLayout.addLayout(kpAndIW, 0,0)        
        self._mainLayout.addLayout(self._imageWidgetLayout, 1,0)
        self._viewFrame.setLayout(self._mainLayout)
        self.setCentralWidget(self._viewFrame)

    def createMenu(self):
        openBundleAct = QtGui.QAction("&Open Images and Tiepoints...", self)
        self.connect(openBundleAct, QtCore.SIGNAL("triggered()"), self.openTiepointsFile)
        
        exitAct = QtGui.QAction(self.tr("&Exit"), self)
        self.connect(exitAct, QtCore.SIGNAL("triggered()"), self.close)
        
        fileMenu = self.menuBar().addMenu("&File")
        fileMenu.addAction(openBundleAct)
        fileMenu.addSeparator()
        fileMenu.addAction(exitAct)
        


    def openTiepointsFile(self):
        dialog = Dialogs.ImagesAndTiepointsDialog(self)
        
        if (dialog.exec_()):
            self._images = Common.sfmImages(images=[Common.sfmImage(dialog.GetTestImage()),
                                                    Common.sfmImage(dialog.GetReferenceImage())])
            self._tiepointsFile = dialog.GetTiepoints()
            self.loadImageWidgets()
            self._tiepointGroupBox.SetTiepointsFile(self._tiepointsFile)
#            self.pointChangedSlot(self._keypointGroupBox.selected3DPoint())

    def loadImageWidgets(self, iwPerRow=DEFAULT_IMAGES_PER_ROW):

        # clear existing widgets
        l = self._imageWidgets.values()
        self._imageWidgets = {}
        while (self._imageWidgetLayout.count() > 0):
            i = self._imageWidgetLayout.takeAt(0)
            x = i.widget()
            x.hide()
            del x
            del i
        self._viewFrame.repaint()

        self._mainLayout.removeItem(self._imageWidgetLayout)
        del self._imageWidgetLayout
        self._imageWidgetLayout = QtGui.QGridLayout()
        self._mainLayout.addLayout(self._imageWidgetLayout, 1,0)

        # fill grid...
        row = 0; column = 0
        for image in self._images.GetImages():
            iw = ImageWidget(image)
            self._imageWidgets[image] = iw
            self._imageWidgetLayout.addWidget(iw, row, column)
            column = ((column+1) % iwPerRow)
            if (column==0): row+=1
            
    def tiepointChangedSlot(self, point):
        for iw in self._imageWidgets.values():
            iw.clearHighlight()
            iw.removePoints()
        
        print("(%f,%f) -> (%f,%f)" % tuple(point))
        self._imageWidgets[self._images.GetImages()[0]].addPoint((point[0],point[1]))
        #self._imageWidgets[self._images.GetImages()[0]].setHighlight()
        
        self._imageWidgets[self._images.GetImages()[1]].addPoint((point[2],point[3]))
        #self._imageWidgets[self._images.GetImages()[1]].setHighlight()



###############################################################################
if __name__=="__main__":    
    app = QtGui.QApplication(sys.argv)
    gui = TiepointGUI()
    gui.show()
    sys.exit(app.exec_())

    
