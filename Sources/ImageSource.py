# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing for details.
import Chain
import Common
import os

class ImageSource(Chain.StageBase):

    def __init__(self, imagePath="", extension="", recursive=False, focalPixelOverride=0):
        Chain.StageBase.__init__(self,
                                 None,
                                 "Provides a source of images from disk",
                                 {"Image Path":"Path to images", 
                                  "Image Extension":"Image extension",
                                  "Recursive":"Whether to perform a recursive search",
                                  "Focal Pixel Override":"Focal pixel value when metadata not found"})
        
        self._properties["Image Path"] = imagePath
        self._properties["Image Extension"] = extension
        self._properties["Recursive"] = recursive
        self._properties["Focal Pixel Override"] = focalPixelOverride
                

    def GetInputInterface(self):
        return None
    
    def GetOutputInterface(self):
        return {"images":Common.sfmImages}

    def Execute(self):
        self.StartProcess()
        
        if (not self._properties["Recursive"]):
            images = Common.sfmImages(self._properties["Image Path"],
                                      self._properties["Image Extension"],
                                      focalPixelOverride=self._properties["Focal Pixel Override"])
        else:
            
            def visit((imageList,ext),dirname,names):
                for n in names:
                    if (os.path.splitext(n)[1][1:]==ext):
                        imageList.append(Common.sfmImage(os.path.join(dirname,n)))
            
            imageList = []
            os.path.walk(self._properties["Image Path"], visit, (imageList,self._properties["Image Extension"]))            
            images = Common.sfmImages(extension=self._properties["Image Extension"], 
                                      images=imageList,
                                      focalPixelOverride=self._properties["Focal Pixel Override"])
            
        self.SetOutputValue("images", images)
        
