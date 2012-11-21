# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing details.
import Chain
import Common
import os, random

class ImageFilter(Chain.StageBase):

    def __init__(self, inputStage=None, dayMonth="", startTime="", endTime="", skipImages=0, randomize=False):
        Chain.StageBase.__init__(self,
                                 inputStage,
                                 "Filters a source of images according to date/time and optionally randomizes the list",
                                 {"Day Month":"Day and month of filter",
                                  "Start Time":"Starting time of filter",
                                  "End Time":"Ending time of filter",
                                  "Skip Images":"Number of images to skip",
                                  "Randomize":"Whether to randomize the image list"})
        
        self._properties["Day Month"] = dayMonth
        self._properties["Start Time"] = startTime
        self._properties["End Time"] = endTime
        self._properties["Skip Images"] = skipImages
        self._properties["Randomize"] = randomize
        

    def GetInputInterface(self):
        return {"images":(0,Common.sfmImages)}
    
    def GetOutputInterface(self):
        return {"images":Common.sfmImages}

    def Execute(self):
        images = self.GetInputStageValue(0, "images")
        
        self.StartProcess()
        
        imageIndex = 0
        imageList = []
        for im in images.GetImages():
            fn = os.path.split(im.GetFilePath())[1]
            if (fn.startswith(self._properties["Day Month"])):
                prefixLen = len(self._properties["Day Month"])
                t = int(fn[prefixLen:prefixLen+7])
                if (self._properties["Start Time"] <= t <= self._properties["End Time"]):
                    if (self._properties["Skip Images"]<=0 or (imageIndex % self._properties["Skip Images"]) == 0):
                        imageList.append(im)
                    imageIndex+=1
        
        if (self._properties["Randomize"]): random.shuffle(imageList)
        images = Common.sfmImages(extension=images.GetExtension(),
                                  images=imageList, 
                                  focalPixelOverride=images.GetFocalPixelOverride())

        self.SetOutputValue("images", images)
        
