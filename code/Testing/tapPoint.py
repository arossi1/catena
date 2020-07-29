# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing details.
import sys, os
sys.path.append(os.path.abspath("."))
import Chain # Chain must be imported first, requirement of registry
import Sources, FeatureExtraction, Common

# path to images
imagePath = os.path.abspath("../Datasets/ET")

# build chain
imageSource = Sources.ImageSource(imagePath, "jpg")

# insert tap point stage with print function
tap = Common.TapPoint(imageSource, {Common.sfmImages:lambda x: "Image Path: " + x.GetPath()})

# insert tap point stage without print function
tap = Common.TapPoint(tap)

sift = FeatureExtraction.Sift(tap, False, "SiftHess")

# render chain
print(Chain.Render(sift,"tapPoint.txt"))

