# Copyright (c) 2014, Adam J. Rossi. All rights reserved. See README for licensing details.
import sys, os
sys.path.append(os.path.abspath("."))
import Chain
import Sources, OpenCV

imagePath = os.path.abspath("../Datasets/ET")
imageSource = Sources.ImageSource(imagePath, "jpg")

fd = OpenCV.FeatureDetector(imageSource,
                            forceRun=True)

fm = OpenCV.FeatureMatcher(fd,
                           "BruteForce",
                           os.path.join(imagePath,"matches.txt"),
                           forceRun=True)

print((Chain.Render(fm, 'openCV.txt')))
