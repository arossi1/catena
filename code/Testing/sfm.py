# Copyright (c) 2014, Adam J. Rossi. All rights reserved. See README for licensing details.
import os

from .. import Chain # Chain must be imported first, requirement of registry
from .. import Sources, FeatureExtraction, FeatureMatch, BundleAdjustment, Cluster

# path to images / PMVS
imagePath = os.path.abspath(os.path.join(os.path.dirname(__file__), 
                                         "../Datasets/ET"))
pmvsPath = os.path.join(imagePath,"pmvs")

# build chain
imageSource = Sources.ImageSource(imagePath, "jpg")
sift = FeatureExtraction.Sift(imageSource, False, "SiftHess")
keyMatch = FeatureMatch.KeyMatch(sift, False, "KeyMatchFull")
bundler = BundleAdjustment.Bundler([keyMatch, imageSource])
radialUndistort = Cluster.RadialUndistort([bundler, imageSource])
prepCmvsPmvs = Cluster.PrepCmvsPmvs(radialUndistort, pmvsPath)
cmvs = Cluster.CMVS(prepCmvsPmvs)
pmvs = Cluster.PMVS(cmvs)

# render chain
print(Chain.Render(pmvs, "sfm.txt"))
