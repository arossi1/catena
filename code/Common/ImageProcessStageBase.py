# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing details.
import Chain, Common
import os, collections

class ImageProcessStageBase(Chain.StageBase):

    def __init__(self, inputStages,
                 outputImagePath,
                 imageExtension,
                 forceRun,
                 enableStage,
                 stageDoc,
                 parameterDoc):
        
        if (inputStages==None):
            raise Exception("No input stages provided")

        parameterDoc["Output Image Path"] = "Output image path"
        parameterDoc["Image Extension"] = "Image extension"
        parameterDoc["Force Run"] = "Force run if output already exists"
        parameterDoc["Enable Stage"] = "Whether stage is enabled"
        
        Chain.StageBase.__init__(self, inputStages, stageDoc, parameterDoc)
        
        if (isinstance(inputStages,collections.Iterable)):
            self.__multipleImages = inputStages[0].GetOutputInterface().has_key("images")
        else:
            self.__multipleImages = inputStages.GetOutputInterface().has_key("images")
        
        self._properties["Output Image Path"] = outputImagePath
        self._properties["Image Extension"] = imageExtension
        self._properties["Force Run"] = forceRun
        self._properties["Enable Stage"] = enableStage
        
        
    def GetInputInterface(self):
        if (self.__multipleImages):
            return {"images":(0,Common.sfmImages)}
        else:
            return {"image":(0,Common.sfmImage)}
    
    
    def GetOutputInterface(self):
        if (self.__multipleImages):
            return {"images":Common.sfmImages}
        else:
            return {"image":Common.sfmImage}
        
        
    def ProcessImage(self, inputImagePath, outputImagePath):
        raise Exception("Derived class (%s) must implement ProcessImage" % self.__class__.__name__)
    
        
    def GetOutputImagePath(self, inputImagePath):
        return os.path.join(self._properties["Output Image Path"], 
                            os.path.splitext(os.path.basename(inputImagePath))[0] + 
                            "."+self._properties["Image Extension"])


    def Execute(self):
        
        # short-circuit if stage disabled
        if (not self._properties["Enable Stage"]):
            if (self.__multipleImages):
                images = self.GetInputStageValue(0, "images")
                self.StartProcess()
                self.SetOutputValue("images", images)
            else:
                image = self.GetInputStageValue(0, "image")
                self.StartProcess()
                self.SetOutputValue("image", image)
            return
                
        
        if (self.__multipleImages):
            images = self.GetInputStageValue(0, "images")
        else:
            image = self.GetInputStageValue(0, "image")
            images = Common.sfmImages(os.path.split(image.GetFilePath())[0],
                                      os.path.splitext(image.GetFilePath())[1][1:], 
                                      [image])
        self.StartProcess()
         
        cImages = []
        for im in images.GetImages():
            
            outputImagePath = self.GetOutputImagePath(im.GetFilePath())
            
            if (Common.Utility.ShouldRun(self._properties["Force Run"], outputImagePath)):
                self.ProcessImage(im.GetFilePath(), outputImagePath)
            
            cImages.append(Common.sfmImage(outputImagePath))
        
        if (self.__multipleImages):
            self.SetOutputValue("images",
                                Common.sfmImages(path=self._properties["Output Image Path"],
                                                 extension=self._properties["Image Extension"],
                                                 images=cImages,
                                                 focalPixelOverride=images.GetFocalPixelOverride()))
        else:
            self.SetOutputValue("image", cImages[0])

