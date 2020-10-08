# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing details.
from .. import Chain
from .. import Common
import os


class ImageConvert(Chain.StageBase):

    def __init__(self, inputStages=None, imagePath="", extension="", mode="PIL"):
        Chain.StageBase.__init__(self,
                                 inputStages,
                                 "Converts images to a desired format",
                                 {"Image Path":"Output image path", 
                                  "Image Extension":"Image extension",
                                  "Mode":"Conversion mode {PIL}"})
        
        self._properties["Image Path"] = imagePath
        self._properties["Image Extension"] = extension
        self._properties["Mode"] = mode
        

    def GetInputInterface(self):
        return {"images":(0,Common.sfmImages)}
    
    def GetOutputInterface(self):
        return {"images":Common.sfmImages}

    def Execute(self):
        images = self.GetInputStageValue(0, "images")
        
        self.StartProcess()

        Common.Utility.MakeDir(self._properties["Image Path"])
        
        if (self._properties["Mode"]=="PIL"):            
            images = images.Convert(self._properties["Image Path"],
                                    self._properties["Image Extension"])
        
        else:
            raise Exception("Unknown conversion mode: " + self._properties["Mode"])
        
            
        self.SetOutputValue("images", images)

        
