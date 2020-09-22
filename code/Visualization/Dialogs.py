# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing details.
from PySide2 import QtCore, QtGui, QtXml, QtWidgets
import traceback

def ShowWarning(text):
    QtWidgets.QMessageBox.warning(None, "Warning", text)
    
def ShowError(text):
    QtWidgets.QMessageBox.critical(None, "Error", text)
    
def ShowException(e):
    QtWidgets.QMessageBox.critical(None, "Error", str(e)+"\n\n"+traceback.format_exc())
            
###############################################################################
class ImagesAndBundlerPathDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setMinimumWidth(600)
        formLayout = QtWidgets.QFormLayout()
        
        # image directory 
        self._imageDirectoryText = QtWidgets.QLineEdit()
        self._imageDirectoryButton = QtWidgets.QPushButton("Browse...")
        self.connect(self._imageDirectoryButton, QtCore.SIGNAL("clicked()"), self.browseImageDirectory)
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self._imageDirectoryText)
        layout.addWidget(self._imageDirectoryButton)
        formLayout.addRow("Image Directory", layout)
        
        # bundler file
        self._bundlerFileText = QtWidgets.QLineEdit()
        self._bundlerFileButton = QtWidgets.QPushButton("Browse...")
        self.connect(self._bundlerFileButton, QtCore.SIGNAL("clicked()"), self.browseBundlerFile)
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self._bundlerFileText)
        layout.addWidget(self._bundlerFileButton)
        formLayout.addRow("Bundler File", layout)
        
        
        acceptButton = QtWidgets.QPushButton("Apply")
        rejectButton = QtWidgets.QPushButton("Cancel")
        buttonLayout = QtWidgets.QHBoxLayout()
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(acceptButton)
        buttonLayout.addWidget(rejectButton)
        self.connect(acceptButton, QtCore.SIGNAL("clicked()"), self.accept)
        self.connect(rejectButton, QtCore.SIGNAL("clicked()"), self.reject)
        
        #viewFrame = QtGui.QFrame()
        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(formLayout)
        layout.addLayout(buttonLayout)
        #viewFrame.setLayout(layout)
        #self.setCentralWidget(viewFrame)
        self.setLayout(layout)
        

    def browseImageDirectory(self):
        ret = QtWidgets.QFileDialog.getExistingDirectory(self, "Choose Image Directory")
        if (ret != ""): self._imageDirectoryText.setText(ret)
        
    def browseBundlerFile(self):
        ret = QtWidgets.QFileDialog.getOpenFileName(self, "Choose Bundler File", self.GetImageDirectory())
        if (ret != ""): self._bundlerFileText.setText(ret)
        
    def GetImageDirectory(self):    return str(self._imageDirectoryText.text())
    def GetBundlerFilePath(self):   return str(self._bundlerFileText.text())
    
    
###############################################################################
class ImagesAndTiepointsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setMinimumWidth(600)
        formLayout = QtWidgets.QFormLayout()
        
        # test image
        self._testImageText = QtWidgets.QLineEdit()
        self._testImageButton = QtWidgets.QPushButton("Browse...")
        self.connect(self._testImageButton, QtCore.SIGNAL("clicked()"), self.browseTestImage)
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self._testImageText)
        layout.addWidget(self._testImageButton)
        formLayout.addRow("Test Image", layout)
        
        # reference image
        self._refImageText = QtWidgets.QLineEdit()
        self._refImageButton = QtWidgets.QPushButton("Browse...")
        self.connect(self._refImageButton, QtCore.SIGNAL("clicked()"), self.browseRefImage)
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self._refImageText)
        layout.addWidget(self._refImageButton)
        formLayout.addRow("Reference Image", layout)
        
        # tiepoints
        self._tpText = QtWidgets.QLineEdit()
        self._tpButton = QtWidgets.QPushButton("Browse...")
        self.connect(self._tpButton, QtCore.SIGNAL("clicked()"), self.browseTP)
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self._tpText)
        layout.addWidget(self._tpButton)
        formLayout.addRow("Tiepoints", layout)
        
        
        acceptButton = QtWidgets.QPushButton("Apply")
        rejectButton = QtWidgets.QPushButton("Cancel")
        buttonLayout = QtWidgets.QHBoxLayout()
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(acceptButton)
        buttonLayout.addWidget(rejectButton)
        self.connect(acceptButton, QtCore.SIGNAL("clicked()"), self.accept)
        self.connect(rejectButton, QtCore.SIGNAL("clicked()"), self.reject)
        
        #viewFrame = QtGui.QFrame()
        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(formLayout)
        layout.addLayout(buttonLayout)
        #viewFrame.setLayout(layout)
        #self.setCentralWidget(viewFrame)
        self.setLayout(layout)
        

    def browseTestImage(self):
        ret = QtWidgets.QFileDialog.getOpenFileName(self, "Choose Test Image")
        if (ret != ""): self._testImageText.setText(ret)
        
    def browseRefImage(self):
        ret = QtWidgets.QFileDialog.getOpenFileName(self, "Choose Reference Image")
        if (ret != ""): self._refImageText.setText(ret)
        
    def browseTP(self):
        ret = QtWidgets.QFileDialog.getOpenFileName(self, "Choose Tiepoints")
        if (ret != ""): self._tpText.setText(ret)
        
    def GetTestImage(self):     return str(self._testImageText.text())
    def GetReferenceImage(self):return str(self._refImageText.text())
    def GetTiepoints(self):     return str(self._tpText.text())

