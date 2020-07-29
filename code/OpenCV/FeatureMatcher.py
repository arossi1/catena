# Copyright (c) 2014, Adam J. Rossi. All rights reserved. See README for licensing details.
from ..import Chain, Common
from . import Types
import FeatureMatch
import os, string
import numpy, cv2

class FeatureMatcher(Chain.StageBase):

    FEATURE_MATCHERS = ("BruteForce","BruteForce-L1","FlannBased")  # these don't work: "BruteForce-Hamming","BruteForce-Hamming(2)"
    
    def __init__(self, 
                 inputStages=None,
                 matcher="BruteForce",
                 matchesPath="",
                 distanceThreshold=0.5,
                 forceRun=False):
        Chain.StageBase.__init__(self,
                                 inputStages,
                                 "Generates features for images",
                                 {"Matcher":"Matcher type {"+string.join(FeatureMatcher.FEATURE_MATCHERS,", ")+"}",
                                  "Matches Path":"Path to matches output file",
                                  "Distance Threshold":"Threshold as a percentage of mean distance",
                                  "Force Run":"Force run if outputs already exist"})
        
        self._properties["Matcher"] = matcher
        self._properties["Matches Path"] = matchesPath
        self._properties["Distance Threshold"] = distanceThreshold
        self._properties["Force Run"] = forceRun

    def GetInputInterface(self):
        return {"keypointDescriptors":(0,Types.ImagesFeatures)}
    
    def GetOutputInterface(self):
        return {"keyMatches":FeatureMatch.KeyMatches}
    
    @staticmethod
    def FilterMatches(matches, distanceThreshold=0.5):
        
        dist = [x.distance for x in matches]
        Chain.Analyze.WriteStatus("Input Matches: %d" % len(matches))
        Chain.Analyze.WriteStatus("Distance (min,mean,max): %.3f, %.3f, %.3f" % \
            (min(dist), (sum(dist) / len(dist)), max(dist)))
        
        # threshold matches at half the mean
        dThreshold = (sum(dist) / len(dist)) * distanceThreshold
        fmatches = [m for m in matches if m.distance < dThreshold]
        
        Chain.Analyze.WriteStatus("Output Matches: %d" % len(fmatches))
        return fmatches
    
    @staticmethod
    def PerformMatching(features1,features2,
                        matchesPath,
                        matcher="BruteForce",
                        distanceThreshold=0.5):       
        
        m = cv2.DescriptorMatcher_create(matcher)
        trainDescriptors = features1.GetDescriptorsArray(numpy.float32)
        m.add(trainDescriptors)
        m.train()
        matches = m.match(features2.GetDescriptorsArray(numpy.float32), trainDescriptors)
        
        matches = FeatureMatcher.FilterMatches(matches, distanceThreshold)
        
        f = open(matchesPath,"w")
        f.write("0 1\n%d\n" % len(matches))
        for match in matches:
            f.write("%d %d\n" % (match.trainIdx,match.queryIdx))
        f.close()

    def Execute(self):
        features = self.GetInputStageValue(0, "keypointDescriptors")
        
        self.StartProcess()
        
        matchesPath = self._properties["Matches Path"]
        if (matchesPath==""):
            # for compatibility with Bundler
            matchesPath = os.path.join(features.GetPath(), "keylist.txt.matches.init.txt")
    
        if (Common.Utility.ShouldRun(self._properties["Force Run"], matchesPath)):
            
            # writing out compatible file to be read in by KeyMatches class, a bit of a hack
            f = open(matchesPath,"w")
            for i in range(len(features.GetDescriptors())):
                m = cv2.DescriptorMatcher_create(self._properties["Matcher"])
                trainDescriptors = features.GetDescriptors()[i].GetDescriptorsArray(numpy.float32)
                m.add(trainDescriptors)
                m.train()
                
                for j in range(i+1,len(features.GetDescriptors())):
                    matches = m.match(features.GetDescriptors()[j].GetDescriptorsArray(numpy.float32), 
                                      trainDescriptors)
                    
                    matches = FeatureMatcher.FilterMatches(
                        matches, self._properties["Distance Threshold"])
                    
                    f.write("%d %d\n%d\n" % (i,j,len(matches)))
                    for match in matches:
                        f.write("%d %d\n" % (match.trainIdx,match.queryIdx))
            f.close()        
        
        kms = FeatureMatch.KeyMatches(matchesPath, features, False)            
        self.SetOutputValue("keyMatches", kms)

