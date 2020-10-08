# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing details.
from .. import Chain, Common, FeatureExtraction
import os

class ASIFT(Chain.StageBase):

    def __init__(self, 
                 inputStages=None,
                 numTilts=7,
                 downsample=False,
                 forceRun=False):
        Chain.StageBase.__init__(self,
                                 inputStages,
                                 "Generates ASIFT descriptors for images",
                                 {"Number of Tilts":"Number of tilts to use in algorithm",
                                  "Downsample":"Whether to downsample the image before feature extraction",
                                  "Force Run":"Force run if outputs already exist"})
        
        self._properties["Number of Tilts"] = numTilts
        self._properties["Downsample"] = downsample
        self._properties["Force Run"] = forceRun

    def GetInputInterface(self):
        return {"images":(0,Common.sfmImages)}
    
    def GetOutputInterface(self):
        return {"keypointDescriptors":FeatureExtraction.KeypointDescriptors}

    def Execute(self):
        images = self.GetInputStageValue(0, "images")
        
        self.StartProcess()
    
        kds = []
        images.WriteFileList()
        ds = 0
        if (self._properties["Downsample"]):ds=1
        
        for im in images.GetImages():
            keypointDescriptorFile = os.path.join(os.path.splitext(im.GetFilePath())[0]+".key")
            
            if (Common.Utility.ShouldRun(self._properties["Force Run"], keypointDescriptorFile)):
                
                self.RunCommand("ASIFTkeypoint",
                                Common.Utility.CommandArgs(Common.Utility.Quoted(im.GetFilePath()),
                                                           Common.Utility.Quoted(keypointDescriptorFile),
                                                           self._properties["Number of Tilts"],
                                                           ds))
            
            kd = FeatureExtraction.KeypointDescriptorFileLowe(keypointDescriptorFile, False)
            kds.append(kd)
                
        
        kds = FeatureExtraction.KeypointDescriptors(images.GetPath(), kds)
        self.SetOutputValue("keypointDescriptors", kds)

        

        
