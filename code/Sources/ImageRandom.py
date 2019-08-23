# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing details.
from catena import Chain, Common
import random

class ImageRandom(Chain.StageBase):

    def __init__(self, inputStage=None):
        Chain.StageBase.__init__(self,
                                 inputStage,
                                 "Randomizes the source of images")
        

    def GetInputInterface(self):
        return {"images":(0,Common.sfmImages)}
    
    def GetOutputInterface(self):
        return {"images":Common.sfmImages}

    def Execute(self):
        images = self.GetInputStageValue(0, "images")
        
        self.StartProcess()
        
        imageList = images.GetImages()
        random.shuffle(imageList)
        images = Common.sfmImages(images.GetPath(),
                                  images.GetExtension(), 
                                  imageList,
                                  images.GetFocalPixelOverride())

        self.SetOutputValue("images", images)
        
