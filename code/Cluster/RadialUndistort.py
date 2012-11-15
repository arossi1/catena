# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing for details.
import Common, Chain, BundleAdjustment
import os

class RadialUndistort(Chain.StageBase):

    def __init__(self, inputStages=None):
        Chain.StageBase.__init__(self,
                                 inputStages,
                                 "Radially undistorts images")        

    def GetInputInterface(self):
        return {"bundleFile":(0,BundleAdjustment.BundleFile),
                "images":(1,Common.sfmImages)}
    
    def GetOutputInterface(self):
        return {"bundleFile":BundleAdjustment.BundleFile,
                "images":Common.sfmImages}

    def RunRadialUndistort(self, imagePath, imageListPath, bundlerOutputFilePath):
        outputPath = os.path.join(imagePath, "rd")
        Common.Utility.MakeDir(outputPath)
        
        cmd = "\"%s\" \"%s\" \"%s\" \"%s\"" % \
        (Common.Utility.GetAbsoluteFilePath(__file__, Common.ExecutablePath.EXE_RadialUndistort), 
         imageListPath, bundlerOutputFilePath, outputPath)
        
# unix: shell=True
        Common.Utility.RunCommand(cmd, cwd=os.path.split(imageListPath)[0])
        
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

