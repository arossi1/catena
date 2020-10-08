# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing details.
from .. import Common, Chain, BundleAdjustment, Cluster
import os, multiprocessing

class CMVS(Chain.StageBase):

    def __init__(self, inputStages=None, cpus=None, forceRun=False):
        Chain.StageBase.__init__(self,
                                 inputStages,
                                 "Runs CMVS",
                                 {"CPUs":"Number of CPUs to utilize",
                                  "Force Run":"Force run if outputs already exist"})
        
        if (cpus==None): self._properties["CPUs"] = multiprocessing.cpu_count()
        else:            self._properties["CPUs"] = cpus
        self._properties["Force Run"] = forceRun 
        

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
        
        self.RunCommand("cmvs", 
                        Common.Utility.CommandArgs("./%s/"%pmvsDir,
                                                   str(numImages),
                                                   str(self._properties["CPUs"])),
                        cwd = pmvsPathParent)
    
    def Execute(self):
        bundleFile = self.GetInputStageValue(0, "bundleFile")
        images = self.GetInputStageValue(0, "images")
        
        self.StartProcess()
        
        pmvsPath = os.path.split(bundleFile.GetBundleFilePath())[0]
        numImages = len(images.GetImages())
        
        visFile = os.path.join(pmvsPath, "vis.dat")
        clusterFile = os.path.join(pmvsPath, "ske.dat")
        cameraCentersAll = os.path.join(pmvsPath, "centers-all.ply")
        
        if (Common.Utility.ShouldRun(self._properties["Force Run"],
                                     visFile,clusterFile,cameraCentersAll)):
        
            self.Process(pmvsPath, numImages)
        
                
        
        self.SetOutputValue("bundleFile", bundleFile)
        self.SetOutputValue("images", images)
        self.SetOutputValue("visFile", Cluster.VisFile(visFile))
        self.SetOutputValue("clusterFile", Cluster.ClusterFile(clusterFile))
        self.SetOutputValue("cameraCentersAll", Cluster.PlyFile(cameraCentersAll))

