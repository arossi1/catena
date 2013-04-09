# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing details.
import Chain, Common, FeatureExtraction
import os, math

class Surf(Chain.StageBase):

    def __init__(self, 
                 inputStages=None,
                 hessianThreshold=500,
                 numOctaves=3,
                 numOctaveLayers=4,
                 forceRun=False):
        Chain.StageBase.__init__(self,
                                 inputStages,
                                 "Generates Surf descriptors for images",
                                 {"Hessian Threshold":"Only features with hessian larger than that are extracted. good default value is ~300-500 (can depend on the average local contrast and sharpness of the image)",
                                  "Number Octaves":"The number of octaves to be used for extraction. With each next octave the feature size is doubled",
                                  "Number Octave Layers":"The number of layers within each octave",
                                  "Force Run":"Force run if outputs already exist"})
        
        self._properties["Hessian Threshold"] = hessianThreshold
        self._properties["Number Octaves"] = numOctaves
        self._properties["Number Octave Layers"] = numOctaveLayers
        self._properties["Force Run"] = forceRun

    def GetInputInterface(self):
        return {"images":(0,Common.sfmImages)}
    
    def GetOutputInterface(self):
        return {"keypointDescriptors":FeatureExtraction.KeypointDescriptors}

    def Execute(self):
        images = self.GetInputStageValue(0, "images")
        
        self.StartProcess()
    
        import cv
        MIN_DESC_VAL = -0.5
        MAX_DESC_VAL = 0.8
        CONV_FACTOR = 255.0 / (MAX_DESC_VAL-MIN_DESC_VAL)
        kds = []
        
        for im in images.GetImages():
            keypointDescriptorFile = os.path.join(os.path.splitext(im.GetFilePath())[0]+".key")
            
            if (Common.Utility.ShouldRun(self._properties["Force Run"], keypointDescriptorFile)):
                
                cvim = cv.LoadImageM(im.GetFilePath(), cv.CV_LOAD_IMAGE_GRAYSCALE)
                keypoints, descriptors = cv.ExtractSURF(cvim, None, cv.CreateMemStorage(), 
                                                        (1,
                                                         self._properties["Hessian Threshold"],
                                                         self._properties["Number Octaves"],
                                                         self._properties["Number Octave Layers"]))                
                l = []
                for i,descriptor in enumerate(descriptors):
                    
                    descr = [int((x-MIN_DESC_VAL)*CONV_FACTOR) for x in descriptor]

                    l.append(FeatureExtraction.KeypointDescriptor(keypoints[i][0][1],
                                                                  keypoints[i][0][0],
                                                                  keypoints[i][2],
                                                                  math.radians(keypoints[i][3]),
                                                                  descr))                    
                    
                kdfl = FeatureExtraction.KeypointDescriptorFileLowe(l)
                kdfl.Write(keypointDescriptorFile)
                kdfl = FeatureExtraction.KeypointDescriptorFileLowe(keypointDescriptorFile, False)
                kds.append(kdfl)
        
        kds = FeatureExtraction.KeypointDescriptors(images.GetPath(), kds, False)
        self.SetOutputValue("keypointDescriptors", kds)       

        
