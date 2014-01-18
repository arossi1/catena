# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing details.
import sys, os
sys.path.append(os.path.abspath("."))
import Chain # Chain must be imported first, requirement of registry
import Sources, FeatureExtraction, FeatureMatch, BundleAdjustment, Cluster


def sfmChainProgrammatic(chainFilePath):
    
    # path to images
    imagePath = "ETsub"
    
    # path to converted pgm images
    imagePathPgm = os.path.join(imagePath,"pgm")

    # PMVS path
    pmvsPath = os.path.join(imagePath,"pmvs")

    # log file / whether to parse keypoint descriptors
    logPath = "log.txt"
    parseKDF = False
    
    # build chain
    imageSource = Sources.ImageSource(imagePath, "jpg")
    imageConvert = Sources.ImageConvert(imageSource, imagePathPgm, "pgm")
    sift = FeatureExtraction.Sift(imageConvert, parseKDF, "SiftHess")
    keyMatch = FeatureMatch.KeyMatch(sift, parseKDF, "KeyMatchFull")
    bundler = BundleAdjustment.Bundler([keyMatch, imageConvert])
    radialUndistort = Cluster.RadialUndistort([bundler, imageSource])
    prepCmvsPmvs = Cluster.PrepCmvsPmvs(radialUndistort, pmvsPath)
    cmvs = Cluster.CMVS(prepCmvsPmvs)
    pmvs = Cluster.PMVS(cmvs)
    
    # render chain
    #print Chain.Render(pmvs,logPath)
    
    # persist chain
    Chain.StageRegistry.Save(chainFilePath)
    
    
def sfmChainPersist(chainFilePath):
    
    # log file
    logPath = "log.txt"
    
    # load the sfm chain
    headStages, tailStages = Chain.StageRegistry.Load(chainFilePath)

    # render the tail stage (pmvs)
    print Chain.Render(tailStages[0],logPath)
    
    
if __name__=="__main__":
    
    #sfmSbaChainProgrammatic("sbaChain.dat")
    sfmChainProgrammatic("sfmChain.dat")
    #sfmChainPersist("sfmChain.dat")


