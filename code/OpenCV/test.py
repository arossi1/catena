# Copyright (c) 2014, Adam J. Rossi. All rights reserved. See README for licensing details.
import os
from catena import Chain, Sources

if __name__=="__main__":
    imagePath = os.path.abspath("../Datasets/ET")
    imageSource = Sources.ImageSource(imagePath, "jpg")

    fd = OpenCV.FeatureDetector(imageSource,
                                forceRun=True)

    fm = OpenCV.FeatureMatcher(fd,
                               "BruteForce",
                               os.path.join(imagePath,"matches.txt"),
                               forceRun=True)

    print(Chain.Render(fm, 'openCV.txt'))
