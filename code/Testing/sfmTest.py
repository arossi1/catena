# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing details.
import sys, os
sys.path.append(os.path.abspath("."))
import Chain # Chain must be imported first, requirement of registry
import Sources, FeatureExtraction, FeatureMatch, BundleAdjustment, Cluster

# path to images
imagePath = r"C:\Datasets\ETsub"

# PMVS path
pmvsPath = os.path.join(imagePath,"pmvs")

# log file / whether to parse keypoint descriptors
logPath = "log.txt"
parseKDF = False

# build chain
imageSource = Sources.ImageSource(imagePath, "jpg")
sift = FeatureExtraction.Sift(imageSource, parseKDF, "SiftHess")
keyMatch = FeatureMatch.KeyMatch(sift, parseKDF, "KeyMatchFull")
bundler = BundleAdjustment.Bundler([keyMatch, imageSource])
radialUndistort = Cluster.RadialUndistort([bundler, imageSource])
prepCmvsPmvs = Cluster.PrepCmvsPmvs(radialUndistort, pmvsPath)
cmvs = Cluster.CMVS(prepCmvsPmvs)
pmvs = Cluster.PMVS(cmvs)

# render chain
print Chain.Render(pmvs,logPath)

# persist chain
Chain.StageRegistry.Save("sfmChain.dat")
