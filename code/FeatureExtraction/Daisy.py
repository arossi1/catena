# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing details.
from .. import Chain, Common, FeatureExtraction
from .DaisyKeypointDescriptorFile import DaisyKeypointDescriptorFile
import string, os

class Daisy(Chain.StageBase):
    
    # normalization types
    NORMALIZATION_PARTIAL = 0
    NORMALIZATION_FULL = 1
    NORMALIZATION_SIFT_LIKE = 2
    
    def __init__(self, 
                 inputStages=None, 
                 parseKDF=False,
                 roi="",
                 diableInterpolation=False,
                 randomSamples=False,
                 numRandomSamples=100,
                 scaleInvariant=True,
                 rotationInvariant=True,
                 orientationResolution=36,
                 forceRun=False):
        Chain.StageBase.__init__(self,
                                 inputStages,
                                 "Generates Sift descriptors for images",
                                 {"Parse Descriptors":"Whether to parse the keypoint descriptors after generation",
                                  "ROI":"Region of interest to process, in the form: x,y,w,h",
                                  "Disable Interpolation":"Whether to disable interpolation",
                                  "Random Samples":"Whether to take random samples of keypoints",
                                  "Number Random Samples":"If random samples is enabled, the number of samples to take",
                                  "Scale Invariant":"Whether to compute scale invariant features",
                                  "Rotation Invariant":"Whether to computer rotation invariant features",
                                  "Orientation Resolution":"If computing rotation invariant features, number of bins to use",
                                  "Force Run":"Force run if outputs already exist"})
        
        self._properties["Parse Descriptors"] = parseKDF
        self._properties["ROI"] = roi
        self._properties["Disable Interpolation"] = diableInterpolation
        self._properties["Random Samples"] = randomSamples
        self._properties["Number Random Samples"] = numRandomSamples
        self._properties["Scale Invariant"] = scaleInvariant
        self._properties["Rotation Invariant"] = rotationInvariant
        self._properties["Orientation Resolution"] = orientationResolution
        self._properties["Force Run"] = forceRun

    def GetInputInterface(self):
        return {"images":(0,Common.sfmImages)}
    
    def GetOutputInterface(self):
        return {"keypointDescriptors":FeatureExtraction.KeypointDescriptors}
    
    
    def Process(self,
                image,
                normalizationType=NORMALIZATION_SIFT_LIKE,
                writeASCIIDescriptorFile=False,
                keypointDescriptorFile=""):
    
        # image
        pImage = "-i \"%s\"" % image
        
        # ROI
        pROI = ""
        if (self._properties["ROI"]!=""):
            pROI = "-xMin %d -yMin %d -width %d -height %d" % tuple([int(x) for x in self._properties["ROI"].split(",")])
    
        # normalization type
        pNT = "-nt %d" % normalizationType
    
        # disable interpolation
        pDisableInterpolation = ""
        if (self._properties["Disable Interpolation"]): pDisableInterpolation = "-di"
    
        # descriptor file
        if (len(keypointDescriptorFile)==0):
            basePath, fileName = os.path.split(image)
            baseName, extension = os.path.splitext(fileName)
            keypointDescriptorFile = os.path.join(basePath, "%s.daisy"%baseName)
        pDescriptorFile = "-dp \"%s\"" % keypointDescriptorFile
        keypointDescriptorFileScales = keypointDescriptorFile + ".scales"
        keypointDescriptorFileOrientation = keypointDescriptorFile + ".orientations"
        
        pRandomSamples = ""
        if (self._properties["Random Samples"]): pRandomSamples = "-rs %d"%self._properties["Number Random Samples"]
        
        pScaleInvariant = ""
        if (self._properties["Scale Invariant"]): pScaleInvariant = "-si"
        
        pRotationInvariant = ""
        if (self._properties["Rotation Invariant"]): pRotationInvariant = "-ri %d" % self._properties["Orientation Resolution"]
    
        # save type (ascii/binary), note: binary is much faster
        if (writeASCIIDescriptorFile): pSaveType = "-sa"
        else:                          pSaveType = "-sb"        
    
        if (Common.Utility.ShouldRun(self._properties["Force Run"],
                                     keypointDescriptorFile,
                                     keypointDescriptorFileScales,
                                     keypointDescriptorFileOrientation)):
            
            self.RunCommand("daisy", 
                            Common.Utility.CommandArgs(pImage, pROI, pNT, pDisableInterpolation, 
                                                       pDescriptorFile, pSaveType, pRandomSamples, 
                                                       pScaleInvariant, pRotationInvariant))
            
        
        return DaisyKeypointDescriptorFile(keypointDescriptorFile, 
                                           keypointDescriptorFileScales, 
                                           keypointDescriptorFileOrientation,
                                           (normalizationType==Daisy.NORMALIZATION_SIFT_LIKE),
                                           True)

    def Execute(self):
        images = self.GetInputStageValue(0, "images")
        
        self.StartProcess()
    
        kds = []
        
        for im in images.GetImages():
            keypointDescriptorFile = os.path.join(os.path.splitext(im.GetFilePath())[0]+".key")
                
            if (Common.Utility.ShouldRun(self._properties["Force Run"], keypointDescriptorFile)):
                                    
                daisyKD = self.Process(im.GetFilePath())
                
                kd = FeatureExtraction.KeypointDescriptorFileLowe(daisyKD,
                                                                  self._properties["Parse Descriptors"])
                
                kd.Write(os.path.splitext(daisyKD.GetFilePath())[0]+".key")
            
            else:
                kd = FeatureExtraction.KeypointDescriptorFileLowe(keypointDescriptorFile, 
                                                                  self._properties["Parse Descriptors"])
                
            kds.append(kd)
        
        kds = FeatureExtraction.KeypointDescriptors(images.GetPath(), kds)
        self.SetOutputValue("keypointDescriptors", kds)


