# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing details.
from catena import Common, Chain, BundleAdjustment
import os

class RadialUndistort(Chain.StageBase):

    def __init__(self, inputStages=None, forceRun=False):
        Chain.StageBase.__init__(self,
                                 inputStages,
                                 "Radially undistorts images",
                                 {"Force Run":"Force run if outputs already exist"})
        
        self._properties["Force Run"] = forceRun

    def GetInputInterface(self):
        return {"bundleFile":(0,BundleAdjustment.BundleFile),
                "images":(1,Common.sfmImages)}
    
    def GetOutputInterface(self):
        return {"bundleFile":BundleAdjustment.BundleFile,
                "images":Common.sfmImages}

    def RunRadialUndistort(self, imagePath, imageListPath, bundlerOutputFilePath):
        outputPath = os.path.join(imagePath, "rd")
        Common.Utility.MakeDir(outputPath)
        rdBundleFile = os.path.join(outputPath, "bundle.rd.out")
        
        if (Common.Utility.ShouldRun(self._properties["Force Run"], rdBundleFile)):
            self.RunCommand("RadialUndistort", 
                            Common.Utility.CommandArgs(Common.Utility.Quoted(imageListPath),
                                                       Common.Utility.Quoted(bundlerOutputFilePath),
                                                       Common.Utility.Quoted(outputPath)),
                            cwd = os.path.split(imageListPath)[0])
        
        # not actual files in list: list.rd.txt, delete to avoid confusion
        #os.remove(os.path.join(outputPath, "list.rd.txt"))
        
        rdBundleFile = os.path.join(outputPath, "bundle.rd.out")
        
        images = Common.sfmImages(outputPath, "jpg")
        return BundleAdjustment.BundleFile(rdBundleFile, images.GetImages()), images
    
    def Execute(self):
        bundleFile = self.GetInputStageValue(0, "bundleFile")
        images = self.GetInputStageValue(1, "images")
        
        self.StartProcess()
        
        images.WriteFileList()
        bundleFile, images = self.RunRadialUndistort(images.GetPath(), images.GetImageListPath(), bundleFile.GetBundleFilePath())
        images.WriteFileList(False)        
        
        self.SetOutputValue("bundleFile", bundleFile)
        self.SetOutputValue("images", images)

