# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing details.
import sys, os
sys.path.append(os.path.abspath("."))
from .. import Chain # Chain must be imported first, requirement of registry
from .. import Sources, FeatureExtraction, FeatureMatch, BundleAdjustment, Cluster, Common

# path to images / PMVS
imagePath = os.path.abspath("../Datasets/ET")
pmvsPath = os.path.join(imagePath,"pmvs")

# build chain
imageSourceJpg = Sources.ImageSource(imagePath, "jpg")
imageSource = Sources.ImageConvert(imageSourceJpg, imagePath, "pgm")
asift = FeatureExtraction.ASIFT(imageSource)
keyMatch = FeatureMatch.ASIFTMatch(asift)
bundler = BundleAdjustment.Bundler([keyMatch, imageSource])
radialUndistort = Cluster.RadialUndistort([bundler, imageSourceJpg])
prepCmvsPmvs = Cluster.PrepCmvsPmvs(radialUndistort, pmvsPath)
cmvs = Cluster.CMVS(prepCmvsPmvs)
pmvs = Cluster.PMVS(cmvs)
    
# render chain
print(Chain.Render(pmvs,"asift.txt"))
    
