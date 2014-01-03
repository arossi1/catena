# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing details.
import Chain
import Common
import random

class ImageSubset(Chain.StageBase):

    def __init__(self, inputStage=None, 
                 maxOutputImages=0, 
                 startIndex=0):
        Chain.StageBase.__init__(self,
                                 inputStage,
                                 "Takes a subset of the source of images",
                                 {"Max Images":"Maximum images in the output set",
                                  "Start Index":"Starting index of subset"})
        
        self._properties["Max Images"] = maxOutputImages
        self._properties["Start Index"] = startIndex


    def GetInputInterface(self):
        return {"images":(0,Common.sfmImages)}
    
    def GetOutputInterface(self):
        return {"images":Common.sfmImages}

    def Execute(self):
        images = self.GetInputStageValue(0, "images")
        
        self.StartProcess()
        
        imageList = images.GetImages()

        if (self._properties["Max Images"]>0):
            imageList = imageList[self._properties["Start Index"]:
                                  self._properties["Start Index"]+self._properties["Max Images"]]
        else:
            imageList = imageList[self._properties["Start Index"]:]

        images = Common.sfmImages(images.GetPath(),
                                  images.GetExtension(), 
                                  imageList,
                                  images.GetFocalPixelOverride())

        self.SetOutputValue("images", images)
        
