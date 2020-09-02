# Copyright (c) 2014, Adam J. Rossi. All rights reserved. See README for licensing details.
import os

from .. import Chain
from .. import Sources, OpenCV

imagePath = os.path.abspath(os.path.join(os.path.dirname(__file__), 
                                         "../Datasets/ET"))
imageSource = Sources.ImageSource(imagePath, "jpg")

fd = OpenCV.FeatureDetector(imageSource,
                            forceRun=True)

fm = OpenCV.FeatureMatcher(fd,
                           "BruteForce",
                           os.path.join(imagePath,"matches.txt"),
                           forceRun=True)

print((Chain.Render(fm, 'openCV.txt')))
