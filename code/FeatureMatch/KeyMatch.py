# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing details.
import Chain, Common, FeatureMatch, FeatureExtraction

class KeyMatch(Chain.StageBase):

    def __init__(self, inputStages=None, parseMatches=False, method="KeyMatchFull"):
        Chain.StageBase.__init__(self,
                                 inputStages,
                                 "Performs keypoint matching",
                                 {"Parse Matches":"Whether to parse the keypoint matches",
                                  "Key Match Method":"Key matching implementation to employ {KeyMatchFull, KeyMatchGPU}"})
        
        self._properties["Parse Matches"] = parseMatches
        self._properties["Key Match Method"] = method
        
        
    def GetInputInterface(self):
        return {"keypointDescriptors":(0,FeatureExtraction.KeypointDescriptors)}
    
    def GetOutputInterface(self):
        return {"keyMatches":FeatureMatch.KeyMatches}
    
    def Execute(self):
        keypointDescriptors = self.GetInputStageValue(0, "keypointDescriptors")
        
        self.StartProcess()
        
    	if (self._properties["Key Match Method"] == "KeyMatchFull"):
            matchesFile = FeatureMatch.KeyMatchFull.Process(keypointDescriptors.GetKeyListPath(), forceRun=False)
        elif (self._properties["Key Match Method"] == "KeyMatchGPU"):
            matchesFile = FeatureMatch.KeyMatchGPU.Process(keypointDescriptors.GetKeyListPath(), forceRun=False)
    	else:
            raise Exception("Unknown Key Match method: " + self._properties["Key Match Method"])
    	
    	keyMatches = FeatureMatch.KeyMatches(matchesFile, keypointDescriptors, self._properties["Parse Matches"])
        
        self.SetOutputValue("keyMatches", keyMatches)

