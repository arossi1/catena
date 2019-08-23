# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing details.
from catena import Chain, Common
import shutil, os

class ImageRename(Chain.StageBase):

    def __init__(self, inputStage=None, baseName="", outputPath="", moveFiles=True):
        Chain.StageBase.__init__(self,
                                 inputStage,
                                 "Renames the source of images",
                                 {"Base Name":"Base name of images",
                                  "Output Path":"Output image path",
                                  "Move Files":"Whether to move files, if not copy"})

        self._properties["Base Name"] = baseName
        self._properties["Output Path"] = outputPath
        self._properties["Move Files"] = moveFiles
        

    def GetInputInterface(self):
        return {"images":(0,Common.sfmImages)}
    
    def GetOutputInterface(self):
        return {"images":Common.sfmImages}

    def Execute(self):
        images = self.GetInputStageValue(0, "images")
        
        self.StartProcess()

        cImages = []
        decimalPlaces = len(str(len(images.GetImages())-1))
        fName = self._properties["Base Name"] + "%0" + str(decimalPlaces) + "d"
        
        for i,im in enumerate(images.GetImages()):
            outputFilePath = os.path.join(self._properties["Output Path"],
                                          (fName % i) + os.path.splitext(os.path.split(im.GetFilePath())[1])[1])

            if (self._properties["Move Files"]):
                shutil.move(im.GetFilePath(), outputFilePath)
            else:
                shutil.copy(im.GetFilePath(), outputFilePath)
            
            cImages.append(Common.sfmImage(outputFilePath))
            
        
        images = Common.sfmImages(path=images.GetPath(),
                                  extension=images.GetExtension(),
                                  images=cImages,
                                  focalPixelOverride=images.GetFocalPixelOverride())

        self.SetOutputValue("images", images)
        
