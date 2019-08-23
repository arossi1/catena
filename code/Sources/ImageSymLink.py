# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing details.
from catena import Chain, Common
import os

class ImageSymLink(Chain.StageBase):

    def __init__(self, inputStage=None, symLinkPath="", delExisting=False, linkKeys=False):
        Chain.StageBase.__init__(self,
                                 inputStage,
                                 "Creates symbolic links for a list of images",
                                 {"Symbolic Link Path":"Path to create symbolic links", 
                                  "Delete Existing Links":"Whether to delete existing symbolic links",
                                  "Link Keys":"Whether to attempt linking corresponding key files"})
        
        self._properties["Symbolic Link Path"] = symLinkPath
        self._properties["Delete Existing Links"] = delExisting
        self._properties["Link Keys"] = linkKeys
                

    def GetInputInterface(self):
        return {"images":(0,Common.sfmImages)}
    
    def GetOutputInterface(self):
        return {"images":Common.sfmImages}

    def Execute(self):
        images = self.GetInputStageValue(0, "images")
        
        self.StartProcess()
        
        if (self._properties["Delete Existing Links"]):
            Common.Utility.DeleteDir(self._properties["Symbolic Link Path"])
        
        Common.Utility.MakeDir(self._properties["Symbolic Link Path"])
        
        imageList = []
        for i,im in enumerate(images.GetImages()):
            linkName = os.path.join(self._properties["Symbolic Link Path"], "%08d%s" % (i,os.path.splitext(im.GetFilePath())[1]))
            Common.Utility.CreateSymbolicLink(im.GetFilePath(), linkName)
            imageList.append(Common.sfmImage(linkName))

            if (self._properties["Link Keys"]):
                keyLinkName = os.path.splitext(linkName)[0] + ".key"
                keySource = os.path.splitext(im.GetFilePath())[0] + ".key"
                Common.Utility.CreateSymbolicLink(keySource, keyLinkName)

        
        images = Common.sfmImages(self._properties["Symbolic Link Path"],
                                  extension=images.GetExtension(), 
                                  images=imageList,
                                  focalPixelOverride=images.GetFocalPixelOverride())
            
        self.SetOutputValue("images", images)
        
