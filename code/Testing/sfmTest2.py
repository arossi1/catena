# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing details.
import sys, os
sys.path.append(os.path.abspath("."))
import Chain # Chain must be imported first, requirement of registry
import Sources, FeatureExtraction, FeatureMatch, BundleAdjustment, Cluster

# path to images
imagePath = r"C:\Datasets\ETsub"
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
#cmvs = Cluster.CMVS(prepCmvsPmvs)
pmvs = Cluster.PMVS(prepCmvsPmvs)

# render chain
print Chain.Render(pmvs,logPath)

# persist chain
Chain.StageRegistry.Save("sfmChain.dat")


