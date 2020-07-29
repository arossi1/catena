# Copyright (c) 2014, Adam J. Rossi. All rights reserved. See README for licensing details.
from .. import Chain
from .. import Common
import random

class ImageSubset(Chain.StageBase):

    def __init__(self, inputStage=None, 
                 maxOutputImages=0, 
                 startIndex=0,
                 increment=1):
        Chain.StageBase.__init__(self,
                                 inputStage,
                                 "Takes a subset of the source of images",
                                 {"Max Images":"Maximum images in the output set",
                                  "Start Index":"Starting index of subset",
                                  "Increment":"Index increment"})
        
        self._properties["Max Images"] = maxOutputImages
        self._properties["Start Index"] = startIndex
        self._properties["Increment"] = increment

    def GetInputInterface(self):
        return {"images":(0,Common.sfmImages)}
    
    def GetOutputInterface(self):
        return {"images":Common.sfmImages}

    def Execute(self):
        images = self.GetInputStageValue(0, "images")
        
        self.StartProcess()
        
        imageList = images.GetImages()
        
        imageList = imageList[self._properties["Start Index"]::max([self._properties["Increment"],1])]

        if (self._properties["Max Images"]>0):
            imageList = imageList[:self._properties["Max Images"]]
            
        images = Common.sfmImages(images.GetPath(),
                                  images.GetExtension(), 
                                  imageList,
                                  images.GetFocalPixelOverride())

        self.SetOutputValue("images", images)
        
