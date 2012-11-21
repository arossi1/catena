# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing details.
import Common, Chain, BundleAdjustment, Cluster
import os, multiprocessing

class CMVS(Chain.StageBase):

    def __init__(self, inputStages=None, cpus=None):
        Chain.StageBase.__init__(self,
                                 inputStages,
                                 "Runs CMVS",
                                 {"CPUs":"Number of CPUs to utilize"})
        
        if (cpus==None): self._properties["CPUs"] = multiprocessing.cpu_count()
        else:            self._properties["CPUs"] = cpus        

    def GetInputInterface(self):
        return {"bundleFile":(0,BundleAdjustment.BundleFile),
                "images":(0,Common.sfmImages)}
    
    def GetOutputInterface(self):
        return {"bundleFile":BundleAdjustment.BundleFile,
                "images":Common.sfmImages,
                "visFile":Cluster.VisFile,
                "clusterFile":Cluster.ClusterFile,
                "cameraCentersAll":Cluster.PlyFile}

    def Process(self, pmvsPath, numImages):
        pmvsPathParent, pmvsDir = os.path.split(pmvsPath)
        cmd = "\"%s\" ./%s/ %d %d" % \
            (Common.Utility.GetAbsoluteFilePath(__file__, Common.ExecutablePath.EXE_CMVS), 
             pmvsDir, numImages, self._properties["CPUs"])        
        Common.Utility.RunCommand(cmd, cwd=pmvsPathParent)        
    
    def Execute(self):
        bundleFile = self.GetInputStageValue(0, "bundleFile")
        images = self.GetInputStageValue(0, "images")
        
        self.StartProcess()
        
        pmvsPath = os.path.split(bundleFile.GetBundleFilePath())[0]
        numImages = len(images.GetImages())
        self.Process(pmvsPath, numImages)
        
        visFile = Cluster.VisFile(os.path.join(pmvsPath, "vis.dat"))
        clusterFile = Cluster.ClusterFile(os.path.join(pmvsPath, "ske.dat"))
        cameraCentersAll = Cluster.PlyFile(os.path.join(pmvsPath, "centers-all.ply"))        
        
        self.SetOutputValue("bundleFile", bundleFile)
        self.SetOutputValue("images", images)
        self.SetOutputValue("visFile", visFile)
        self.SetOutputValue("clusterFile", clusterFile)
        self.SetOutputValue("cameraCentersAll", cameraCentersAll)

