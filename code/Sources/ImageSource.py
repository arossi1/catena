# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing details.
from catena import Chain, Common
import os, glob

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
        
        if (isinstance(self._properties["Image Path"],str)):
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
                
        elif (isinstance(self._properties["Image Path"],list)):
            
            cImages = []
            for p in self._properties["Image Path"]:
                if (self._properties["Recursive"]):
                    for root, dirs, files in os.walk(p):
                        for fn in files:
                            if (os.path.splitext(fn)[1][1:]==self._properties["Image Extension"]):
                                cImages.append(Common.sfmImage(os.path.join(root,fn)))
                else:
                    for fn in glob.glob(os.path.join(p, "*.%s"%self._properties["Image Extension"])):
                        cImages.append(Common.sfmImage(fn))
            
            images = Common.sfmImages(path="", 
                                      extension=self._properties["Image Extension"],
                                      images=cImages,
                                      focalPixelOverride=self._properties["Focal Pixel Override"])
            
        else:
            raise Exception("Unhandled type for Image Path: " + str(type(self._properties["Image Path"])))
                            
        self.SetOutputValue("images", images)
        
