# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing details.
import Chain, Common, FeatureExtraction
import SiftWin32, SiftVLFeat, Daisy, SiftHess, SiftGPU
import os

class Sift(Chain.StageBase):

    def __init__(self, inputStages=None, parseKDF=False, method="SiftWin32"):
        Chain.StageBase.__init__(self,
                                 inputStages,
                                 "Generates Sift descriptors for images",
                                 {"Parse Descriptors":"Whether to parse the keypoint descriptors after generation",
                                  "Sift Method":"Sift implementation to use {SiftWin32, SiftHess, SiftGPU, VLFeat, Daisy}"})
        
        self._properties["Parse Descriptors"] = parseKDF
        self._properties["Sift Method"] = method

    def GetInputInterface(self):
        return {"images":(0,Common.sfmImages)}
    
    def GetOutputInterface(self):
        return {"keypointDescriptors":FeatureExtraction.KeypointDescriptors}

    def Execute(self):
        images = self.GetInputStageValue(0, "images")
        
        self.StartProcess()
        
        kds = []
        
        if (self._properties["Sift Method"] == "SiftWin32"):
            for im in images.GetImages():
                kds.append(SiftWin32.Process(im.GetFilePath(),
                                             parseKDF=self._properties["Parse Descriptors"],
                                             forceRun=False))

        elif (self._properties["Sift Method"] == "SiftHess"):
            for im in images.GetImages():
                kds.append(SiftHess.Process(im.GetFilePath(),
                                            parseKDF=self._properties["Parse Descriptors"],
                                            forceRun=False))
                
        elif (self._properties["Sift Method"] == "SiftGPU"):
            for im in images.GetImages():
                kds.append(SiftGPU.Process(im.GetFilePath(),
                                            parseKDF=self._properties["Parse Descriptors"],
                                            forceRun=False))
        
	elif (self._properties["Sift Method"] == "VLFeat"):
            for im in images.GetImages():
                vlkd = SiftVLFeat.Process(im.GetFilePath(),
                                          parseKDF=True, #self._properties["Parse Descriptors"],
                                          forceRun=True)
                kd = FeatureExtraction.SiftWin32KeypointDescriptorFile(vlkd)
                kd.Write(vlkd.GetFilePath())
                kds.append(kd)
                
        elif (self._properties["Sift Method"] == "Daisy"):
            for im in images.GetImages():
                daisyKD = Daisy.Process(im.GetFilePath(),
                                        parseKDF=self._properties["Parse Descriptors"],
                                        forceRun=False)
                kd = FeatureExtraction.SiftWin32KeypointDescriptorFile(daisyKD)
                kd.Write(os.path.splitext(daisyKD.GetFilePath())[0]+".key")
                kds.append(kd)
        
        else:
            raise Exception("Unknown Sift method: " + self._properties["Sift Method"])
        
        kds = FeatureExtraction.KeypointDescriptors(images.GetPath(), kds)
        self.SetOutputValue("keypointDescriptors", kds)

        

        
