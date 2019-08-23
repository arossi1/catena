# Copyright (c) 2014, Adam J. Rossi. All rights reserved. See README for licensing details.
import os
import Chain # Chain must be imported first, requirement of registry
import Sources, FeatureExtraction, FeatureMatch, BundleAdjustment, Cluster, Visualization

# path to images / PMVS
imagePath = os.path.abspath("../Datasets/ET")
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


stagesVisualizations = [(imageSource,"Images",Visualization.ChainGUI.ImageWidget),
                        ((imageSource,sift),"Features",Visualization.ChainGUI.FeatureWidget),
                        ((imageSource,keyMatch),"Correspondences",Visualization.ChainGUI.CorrespondenceWidget)
                        ]

stagesDisplayProperty = [(imageSource,"Source"),
                         (sift,"Features"),
                         (keyMatch,"Keymatch"),
                         (bundler,"Bundler"),
                         (radialUndistort,"Radial Undistort"),
                         (prepCmvsPmvs,"Prep CMVS/PMVS"),
                         (cmvs,"CMVS"),
                         (pmvs,"PMVS")
                         ]

stagesPropertyRanges={pmvs:{"Cell Size":(1,40),
                            "Maximum Camera Angle Threshold":(1,45),
                            "Patch Threshold":(0.0,10.0),
                            "Sample Window Size":(1,20)}}

Visualization.ChainGUI.display(stagesVisualizations,
                               stagesDisplayProperty,
                               stagesPropertyRanges)

