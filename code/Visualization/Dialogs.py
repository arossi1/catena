# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing details.
from PyQt4 import QtCore, QtGui, QtXml
import traceback

def ShowWarning(text):
    QtGui.QMessageBox.warning(None, "Warning", text)
    
def ShowError(text):
    QtGui.QMessageBox.critical(None, "Error", text)
    
def ShowException(e):
    QtGui.QMessageBox.critical(None, "Error", str(e)+"\n\n"+traceback.format_exc())
            
###############################################################################
class ImagesAndBundlerPathDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setMinimumWidth(600)
        formLayout = QtGui.QFormLayout()
        
        # image directory 
        self._imageDirectoryText = QtGui.QLineEdit()
        self._imageDirectoryButton = QtGui.QPushButton("Browse...")
        self.connect(self._imageDirectoryButton, QtCore.SIGNAL("clicked()"), self.browseImageDirectory)
        layout = QtGui.QHBoxLayout()
        layout.addWidget(self._imageDirectoryText)
        layout.addWidget(self._imageDirectoryButton)
        formLayout.addRow("Image Directory", layout)
        
        # bundler file
        self._bundlerFileText = QtGui.QLineEdit()
        self._bundlerFileButton = QtGui.QPushButton("Browse...")
        self.connect(self._bundlerFileButton, QtCore.SIGNAL("clicked()"), self.browseBundlerFile)
        layout = QtGui.QHBoxLayout()
        layout.addWidget(self._bundlerFileText)
        layout.addWidget(self._bundlerFileButton)
        formLayout.addRow("Bundler File", layout)
        
        
        acceptButton = QtGui.QPushButton("Apply")
        rejectButton = QtGui.QPushButton("Cancel")
        buttonLayout = QtGui.QHBoxLayout()
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(acceptButton)
        buttonLayout.addWidget(rejectButton)
        self.connect(acceptButton, QtCore.SIGNAL("clicked()"), self.accept)
        self.connect(rejectButton, QtCore.SIGNAL("clicked()"), self.reject)
        
        #viewFrame = QtGui.QFrame()
        layout = QtGui.QVBoxLayout()
        layout.addLayout(formLayout)
        layout.addLayout(buttonLayout)
        #viewFrame.setLayout(layout)
        #self.setCentralWidget(viewFrame)
        self.setLayout(layout)
        

    def browseImageDirectory(self):
        ret = QtGui.QFileDialog.getExistingDirectory(self, "Choose Image Directory")
        if (ret != ""): self._imageDirectoryText.setText(ret)
        
    def browseBundlerFile(self):
        ret = QtGui.QFileDialog.getOpenFileName(self, "Choose Bundler File", self.GetImageDirectory())
        if (ret != ""): self._bundlerFileText.setText(ret)
        
    def GetImageDirectory(self):    return str(self._imageDirectoryText.text())
    def GetBundlerFilePath(self):   return str(self._bundlerFileText.text())
    
            

