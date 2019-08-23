# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing details.
from catena import Chain, Common
from KeypointDescriptors import KeypointDescriptors
from KeypointDescriptorFileLowe import KeypointDescriptorFileLowe

import os

class KeypointCombine(Chain.StageBase):

    def __init__(self, inputStages=None): #, cppver=False):
        Chain.StageBase.__init__(self,
                                 inputStages,
                                 "Combines 2 sets of keypoint descriptors")
        #self._cppver = cppver

    def GetInputInterface(self):
        return {"keypointDescriptors"   :(0,KeypointDescriptors),
                "images"                :(1,Common.sfmImages),
                "images"                :(2,Common.sfmImages)}
    
    def GetOutputInterface(self):
        return {"keypointDescriptors":KeypointDescriptors}

    def Execute(self):
        #if (self._cppver): self.CppVer()
        #else:              
        self.PythonVer() 
    
#    def CppVer(self):
#        keypointDescriptors = self.GetInputStageValue(0, "keypointDescriptors")
#        images = self.GetInputStageValue(1, "images")
#        imageTiles = self.GetInputStageValue(2, "images")
#        
#        self.StartProcess()
#        
#        Utility.RunCommand("\"%s\" \"%s\"" % (Utility.GetAbsoluteFilePath(__file__, ExecutablePath.EXE_KeypointCombine), 
#                                              images.GetTileListPath()),
#                           cwd=os.path.split(tileListPath)[0], shell=True)
#        kdList = []
#        for im in images.GetImages():
#            path,fn = os.path.split(im.GetFilePath())
#            kpPath = os.path.join(path, os.path.splitext(fn)[0]+".key")
#            kdList.append(KeypointDescriptorFileLowe(kpPath, False))
#        
#        self.SetOutputValue("keypointDescriptors", KeypointDescriptors(images.GetPath(), kdList))
        
    def PythonVer(self):
        
        keypointDescriptors = self.GetInputStageValue(0, "keypointDescriptors")
        images = self.GetInputStageValue(1, "images")
        imageTiles = self.GetInputStageValue(2, "images")
        
        self.StartProcess()
        
        kdList = []
        for im in images.GetImages():
            descriptors = []
            for tdim in im.GetTileDims():
                tFileName = im.GetTileFileName(tdim)
                fn,ext = os.path.splitext(tFileName)
                kd = keypointDescriptors.GetDescriptor(fn+".key")
                kd.Parse(tdim[0],tdim[1])
                descriptors += kd.GetDescriptors()
            kdf = KeypointDescriptorFileLowe(descriptors)
            kdf.SortDescriptors()
            baseDir, fileName = os.path.split(im.GetFilePath())
            fn,ext = os.path.splitext(fileName)
            kdf.Write(os.path.join(baseDir, fn+".key"))
            kdList.append(kdf)
     
        
        self.SetOutputValue("keypointDescriptors", KeypointDescriptors(os.path.split(images.GetImages()[0].GetFilePath())[0], kdList))

        
