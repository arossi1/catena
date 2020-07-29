# Copyright (c) 2014, Adam J. Rossi. All rights reserved. See README for licensing details.
import sys, os
sys.path.append(os.path.abspath("."))
import Chain # Chain must be imported first, requirement of registry
import Sources, FeatureExtraction, FeatureMatch, BundleAdjustment, Cluster, OpenCV

# path to images / PMVS
imagePath = os.path.abspath("../Datasets/ET")
pmvsPath = os.path.join(imagePath,"pmvs")

# build chain
imageSource = Sources.ImageSource(imagePath, "jpg")
sift = OpenCV.FeatureDetector(imageSource)
keyMatch = OpenCV.FeatureMatcher(sift)
bundler = BundleAdjustment.Bundler([keyMatch, imageSource])
radialUndistort = Cluster.RadialUndistort([bundler, imageSource])
prepCmvsPmvs = Cluster.PrepCmvsPmvs(radialUndistort, pmvsPath)
cmvs = Cluster.CMVS(prepCmvsPmvs)
pmvs = Cluster.PMVS(cmvs)

# render chain
print(Chain.Render(pmvs, "sfmOpenCV.txt"))
