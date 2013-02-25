# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing details.
import Common, Chain, BundleAdjustment, Cluster
import os, shutil

class PrepCmvsPmvs(Chain.StageBase):

    def __init__(self, inputStages=None, targetPath="", forceRun=False):
        Chain.StageBase.__init__(self,
                                 inputStages,
                                 "Prepares directories for CMVS/PMVS",
                                 {"Target Path":"Target path for CMVS/PMVS preparation",
                                  "Force Run":"Force run if outputs already exist"})
        
        self._properties["Target Path"] = targetPath
        self._properties["Force Run"] = forceRun

    def GetInputInterface(self):
        return {"bundleFile":(0,BundleAdjustment.BundleFile),
                "images":(0,Common.sfmImages)}
    
    def GetOutputInterface(self):
        return {"bundleFile":BundleAdjustment.BundleFile,
                "images":Common.sfmImages,
                "visFile":Cluster.VisFile,
                "cameraMatrices":Cluster.CameraMatrices}

    def Bundle2PMVS(self, imagelist, bundleFile, outputPath):
    
        Common.Utility.MakeDir(outputPath)
        
        paths = [os.path.join(outputPath, "txt"),
                 os.path.join(outputPath, "visualize"),
                 os.path.join(outputPath, "models")]
        
        Common.Utility.MakeDirs(paths)
        
        self.RunCommand("Bundle2PMVS", 
                        Common.Utility.CommandArgs(Common.Utility.Quoted(imagelist),
                                                   Common.Utility.Quoted(bundleFile),
                                                   Common.Utility.Quoted(outputPath)),
                        cwd = os.path.split(imagelist)[0])

        return paths
    
    def Bundle2Vis(self, outputPath, bundleFile):
        visFile = os.path.join(outputPath, "vis.dat")
        
        if (Common.Utility.ShouldRun(self._properties["Force Run"], visFile)):
            self.RunCommand("Bundle2Vis", 
                            Common.Utility.CommandArgs(Common.Utility.Quoted(bundleFile),
                                                       Common.Utility.Quoted(visFile)))
        
        return visFile
    
    def CopyImagesToVisualizeDirectory(self, images, visualizePath):
        for i,im in enumerate(images.GetImages()):
            shutil.copy(im.GetFilePath(),
                        os.path.join(visualizePath, "%08d%s" % (i, os.path.splitext(im.GetFilePath())[1])))
            
        return Common.sfmImages(visualizePath, images.GetExtension())
            
    def CopyBundleFile(self, bundleFile, outputPath):
        bundleFileDest = os.path.join(outputPath, os.path.split(bundleFile)[1])
        shutil.copy(bundleFile, bundleFileDest)
        return bundleFileDest
    
    def Execute(self):
        bundleFile = self.GetInputStageValue(0, "bundleFile")
        images = self.GetInputStageValue(0, "images")
        pmvsPath = self._properties["Target Path"]
        
        self.StartProcess()
        
        paths = self.Bundle2PMVS(images.GetImageListPath(), bundleFile.GetBundleFilePath(), pmvsPath)
        visFile = self.Bundle2Vis(pmvsPath, bundleFile.GetBundleFilePath())
        images = self.CopyImagesToVisualizeDirectory(images, paths[1])
        bundleFileDest = self.CopyBundleFile(bundleFile.GetBundleFilePath(), pmvsPath)
        
        bundleFile = BundleAdjustment.BundleFile(bundleFileDest, images.GetImages())
        visFile = Cluster.VisFile(visFile)
        
        # TODO: linux hack
        if (not Common.Utility.IsWindows() or Common.Utility.PlatformName=="Windows64bit"):
            Common.Utility.CopyFiles(pmvsPath, paths[0], "txt")
            os.remove(os.path.join(paths[0], "pmvs_options.txt"))

        cameraMatrices = Cluster.CameraMatrices(paths[0])
        
        self.SetOutputValue("bundleFile", bundleFile)
        self.SetOutputValue("images", images)
        self.SetOutputValue("visFile", visFile)
        self.SetOutputValue("cameraMatrices", cameraMatrices)

