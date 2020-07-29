# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing details.
import sys, os
sys.path.append(os.path.abspath("."))
from .. import Chain # Chain must be imported first, requirement of registry
from .. import Sources, FeatureExtraction, FeatureMatch, BundleAdjustment, Cluster


def sfmChainBuild(chainFilePath, imagePath):

    # build chain
    imageSource = Sources.ImageSource(imagePath, "jpg")
    sift = FeatureExtraction.Sift(imageSource, False, "SiftHess")
    keyMatch = FeatureMatch.KeyMatch(sift, False, "KeyMatchFull")
    bundler = BundleAdjustment.Bundler([keyMatch, imageSource])
    radialUndistort = Cluster.RadialUndistort([bundler, imageSource])
    prepCmvsPmvs = Cluster.PrepCmvsPmvs(radialUndistort, os.path.join(imagePath,"pmvs"))
    cmvs = Cluster.CMVS(prepCmvsPmvs)
    pmvs = Cluster.PMVS(cmvs)

    # persist chain
    Chain.StageRegistry.Save(chainFilePath)
    
    
def sfmChainRestoreRender(chainFilePath):
    
    # load the sfm chain
    headStages, tailStages = Chain.StageRegistry.Load(chainFilePath)

    # render the tail stage (pmvs)
    print(Chain.Render(tailStages[0],"persistence.txt"))
    
    
if __name__=="__main__":

    imagePath = os.path.abspath("../Datasets/ET")
    sfmChainBuild("sfmChain.dat", imagePath)
    sfmChainRestoreRender("sfmChain.dat")

