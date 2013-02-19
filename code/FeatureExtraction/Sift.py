# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing details.
import Chain, Common, FeatureExtraction
from KeypointDescriptorFileVLFeat import KeypointDescriptorFileVLFeat
import os

class Sift(Chain.StageBase):

    def __init__(self, 
                 inputStages=None, 
                 parseKDF=False, 
                 method="SiftWin32",
                 forceRun=False):
        Chain.StageBase.__init__(self,
                                 inputStages,
                                 "Generates Sift descriptors for images",
                                 {"Parse Descriptors":"Whether to parse the keypoint descriptors after generation",
                                  "Sift Method":"Sift implementation to use {SiftWin32, SiftHess, SiftGPU, VLFeat}",
                                  "Force Run":"Force run if outputs already exist"})
        
        self._properties["Parse Descriptors"] = parseKDF
        self._properties["Sift Method"] = method
        self._properties["Force Run"] = forceRun

    def GetInputInterface(self):
        return {"images":(0,Common.sfmImages)}
    
    def GetOutputInterface(self):
        return {"keypointDescriptors":FeatureExtraction.KeypointDescriptors}

    def Execute(self):
        images = self.GetInputStageValue(0, "images")
        
        self.StartProcess()
    
        kds = []
        
        # special case
        if (self._properties["Sift Method"] == "VLFeat"):
            
            exeName = "sift"
            argsPattern = "--orientations \"%s\" -o \"%s\""
            
            for im in images.GetImages():
                keypointDescriptorFile = os.path.join(os.path.splitext(im.GetFilePath())[0]+".key")
                
                if (Common.Utility.ShouldRun(self._properties["Force Run"], keypointDescriptorFile)):
                    
                    self.RunCommand(exeName,
                                    argsPattern % (im.GetFilePath(),keypointDescriptorFile))
                    
                    vlkd = KeypointDescriptorFileVLFeat(keypointDescriptorFile, True)
                    kd = FeatureExtraction.KeypointDescriptorFileLowe(vlkd)
                    kd.Write(vlkd.GetFilePath())
                    
                else:
                    kd = FeatureExtraction.KeypointDescriptorFileLowe(keypointDescriptorFile, 
                                                                      self._properties["Parse Descriptors"])
                kds.append(kd)
                
        else:    
            
            if (self._properties["Sift Method"] == "SiftWin32"):
                exeName = "siftWin32"
                argsPattern = "<\"%s\"> \"%s\""
            elif (self._properties["Sift Method"] == "SiftHess"):
                exeName = "sifthess"
                argsPattern = "\"%s\" \"%s\""
            elif (self._properties["Sift Method"] == "SiftGPU"):
                exeName = "SiftGPUKeypoint"
                argsPattern = "\"%s\" \"%s\""
            else:
                raise Exception("Unknown Sift method: " + self._properties["Sift Method"])
            
            for im in images.GetImages():
                keypointDescriptorFile = os.path.join(os.path.splitext(im.GetFilePath())[0]+".key")
                
                if (Common.Utility.ShouldRun(self._properties["Force Run"], keypointDescriptorFile)):
                    
                    self.RunCommand(exeName,
                                    argsPattern % (im.GetFilePath(),keypointDescriptorFile))
                
                kd = FeatureExtraction.KeypointDescriptorFileLowe(keypointDescriptorFile, 
                                                                  self._properties["Parse Descriptors"])
                kds.append(kd)
                
        
        kds = FeatureExtraction.KeypointDescriptors(images.GetPath(), kds)
        self.SetOutputValue("keypointDescriptors", kds)

        

        
