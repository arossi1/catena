# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing details.
import os, glob

from PyQt4 import QtCore, QtGui, QtXml
import BundleAdjustment
import Common
import Dialogs


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
class KeyPoints(QtGui.QGroupBox):
    
    def __init__(self, bundleFile, parent=None):
        QtGui.QGroupBox.__init__(self, "Cameras / Key Points", parent)
        
        formLayout = QtGui.QFormLayout()

        self._cameraComboBox = QtGui.QComboBox()
        formLayout.addRow("Cameras", self._cameraComboBox)
        self.connect(self._cameraComboBox, QtCore.SIGNAL("currentIndexChanged(int)"), self.cameraChangedSlot) 
        
        self._3DPointComboBox = QtGui.QComboBox()
        formLayout.addRow("3D Points", self._3DPointComboBox)
        self.connect(self._3DPointComboBox, QtCore.SIGNAL("currentIndexChanged(int)"), self.pointChangedSlot) 
        
        self.setLayout(formLayout)
        self.SetBundleFile(bundleFile)        
    
    @QtCore.pyqtSignature("int")
    def cameraChangedSlot(self, val):
        self.emit(QtCore.SIGNAL("cameraChangedSignal(PyQt_PyObject)"), self.selectedCamera())
        
    @QtCore.pyqtSignature("int")
    def pointChangedSlot(self, val):
        self.emit(QtCore.SIGNAL("pointChangedSignal(PyQt_PyObject)"), self.selected3DPoint())
        
    def SetBundleFile(self, bundleFile):
        self._bundleFile = bundleFile
        self.loadWidgets()
    
    def selectedCamera(self):
        selectedItem = self._cameraComboBox.itemData(self._cameraComboBox.currentIndex())
        if (selectedItem.isValid()): return selectedItem.toPyObject()
        else: return None
        
    def selected3DPoint(self):
        selectedItem = self._3DPointComboBox.itemData(self._3DPointComboBox.currentIndex())
        if (selectedItem.isValid()): return selectedItem.toPyObject()
        else: return None        
        
    def loadWidgets(self):
        self._cameraComboBox.clear()
        self._3DPointComboBox.clear()

        if (self._bundleFile==None): return
        
        for i, camera in enumerate(self._bundleFile.GetCameras()):
            self._cameraComboBox.addItem("Camera %d" % i, QtCore.QVariant(camera))
            
        for i, point in enumerate(self._bundleFile.Get3DPoints()):
            self._3DPointComboBox.addItem("3D point %d" % i, QtCore.QVariant(point))


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
class SFMgui(QtGui.QMainWindow):
    
    DEFAULT_IMAGES_PER_ROW = 4
    
    def __init__(self, parent=None):

        # initial setup
        QtGui.QMainWindow.__init__(self, parent, QtCore.Qt.WindowMinMaxButtonsHint)
        self.setWindowTitle("SFM")
        self.setMinimumSize(500,500)
        self.setDockOptions(QtGui.QMainWindow.AllowTabbedDocks)
        self.setAnimated(True)
        self.createMenu()
        
        self._imageWidgets = {}
        
        self._keypointGroupBox = KeyPoints(None, self)
        self.connect(self._keypointGroupBox, QtCore.SIGNAL("cameraChangedSignal(PyQt_PyObject)"), self.cameraChangedSlot)
        self.connect(self._keypointGroupBox, QtCore.SIGNAL("pointChangedSignal(PyQt_PyObject)"), self.pointChangedSlot)        

        self._imageWidgetLayout = QtGui.QGridLayout()
        
        optionsGroupBox = QtGui.QGroupBox("Options")
        imPerRowLayout = QtGui.QFormLayout()
        self._imPerRow = QtGui.QSpinBox()
        self._imPerRow.setRange(1,10)
        imPerRowLayout.addRow("Images Per Row", self._imPerRow)
        self._imPerRow.setValue(SFMgui.DEFAULT_IMAGES_PER_ROW)
        self.connect(self._imPerRow, QtCore.SIGNAL("valueChanged (int)"), self.imPerRowChangedSlot)
        optionsGroupBox.setLayout(imPerRowLayout)
        
        self._viewFrame = QtGui.QFrame()
        self._mainLayout = QtGui.QGridLayout()
        kpAndIW = QtGui.QHBoxLayout()
        kpAndIW.addWidget(self._keypointGroupBox)
        kpAndIW.addWidget(optionsGroupBox)
        self._mainLayout.addLayout(kpAndIW, 0,0)        
        self._mainLayout.addLayout(self._imageWidgetLayout, 1,0)
        self._viewFrame.setLayout(self._mainLayout)
        self.setCentralWidget(self._viewFrame)

    def createMenu(self):
        openBundleAct = QtGui.QAction("&Open Bundle File And Images...", self)
        self.connect(openBundleAct, QtCore.SIGNAL("triggered()"), self.openBundleFile)
        
        exitAct = QtGui.QAction(self.tr("&Exit"), self)
        self.connect(exitAct, QtCore.SIGNAL("triggered()"), self.close)
        
        fileMenu = self.menuBar().addMenu("&File")
        fileMenu.addAction(openBundleAct)
        fileMenu.addSeparator()
        fileMenu.addAction(exitAct)

    @QtCore.pyqtSignature("int")
    def imPerRowChangedSlot(self, val):
        self.loadImageWidgets(val)
        
    def openBundleFile(self):
        dialog = Dialogs.ImagesAndBundlerPathDialog(self)
        
        dialog._imageDirectoryText.setText(r"C:\Documents and Settings\Adam Rossi\Desktop\thesis\root\Datasets\Jamie\jpg\rd\pmvs\visualize")
        dialog._bundlerFileText.setText(r"C:\Documents and Settings\Adam Rossi\Desktop\thesis\root\Datasets\Jamie\jpg\rd\bundle.rd.out")
        
        if (dialog.exec_()):
            ext = os.path.splitext(glob.glob(os.path.join(dialog.GetImageDirectory(), "*.*"))[0])[1][1:]
            images = Common.sfmImages(dialog.GetImageDirectory(), ext)
            self._bundleFile = BundleAdjustment.BundleFile(dialog.GetBundlerFilePath(), images.GetImages())
            self.loadImageWidgets()
            self._keypointGroupBox.SetBundleFile(self._bundleFile)
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
        for image in self._bundleFile.GetImages():
            iw = ImageWidget(image)
            self._imageWidgets[image] = iw
            self._imageWidgetLayout.addWidget(iw, row, column)
            column = ((column+1) % iwPerRow)
            if (column==0): row+=1
            
    def cameraChangedSlot(self, camera):
        print camera

    def pointChangedSlot(self, point):
        for iw in self._imageWidgets.values():
            iw.clearHighlight()
            iw.removePoints()
            
        for point2D in point.Get2DPoints():
            self._imageWidgets[point2D.GetImage()].addPoint(point2D.GetCoordinateImage())
            self._imageWidgets[point2D.GetImage()].setHighlight()
            print point2D



###############################################################################
if __name__=="__main__":    
    app = QtGui.QApplication(sys.argv)
    gui = SFMgui()
    gui.show()
    sys.exit(app.exec_())

    
