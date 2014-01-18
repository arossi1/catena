# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing details.
import sys, os
sys.path.append(os.path.abspath("."))
import Chain # Chain must be imported first, requirement of registry
import Sources, FeatureExtraction, FeatureMatch, BundleAdjustment, Cluster, Common


imagePath = os.path.abspath("../Datasets/ET")
pmvsPath = os.path.join(imagePath,"pmvs")

# build chain
imageSourceJpg = Sources.ImageSource(imagePath, "jpg")
imageSource = Sources.ImageConvert(imageSourceJpg, imagePath, "pgm")
asift = FeatureExtraction.ASIFT(imageSource)
keyMatch = FeatureMatch.ASIFTMatch(asift)
bundler = BundleAdjustment.Bundler([keyMatch, imageSource], forceRun=True)
radialUndistort = Cluster.RadialUndistort([bundler, imageSourceJpg], forceRun=True)
prepCmvsPmvs = Cluster.PrepCmvsPmvs(radialUndistort, pmvsPath, forceRun=True)

cmvs = Cluster.CMVS(prepCmvsPmvs, forceRun=True)
pmvs = Cluster.PMVS(cmvs, forceRun=True)
    
# render chain
print Chain.Render(pmvs,"asift.txt")
    
