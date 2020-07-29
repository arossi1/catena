# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing details.
from .. import Chain, Common, FeatureMatch, FeatureExtraction
import os

class ASIFTMatch(Chain.StageBase):

    def __init__(self, inputStages=None, parseMatches=False, forceRun=False):
        Chain.StageBase.__init__(self,
                                 inputStages,
                                 "Performs keypoint matching",
                                 {"Parse Matches":"Whether to parse the keypoint matches",
                                  "Force Run":"Force run if outputs already exist"})
        
        self._properties["Parse Matches"] = parseMatches
        self._properties["Force Run"] = forceRun
        
        
    def GetInputInterface(self):
        return {"keypointDescriptors":(0,FeatureExtraction.KeypointDescriptors)}
    
    def GetOutputInterface(self):
        return {"keyMatches":FeatureMatch.KeyMatches}
    
    def Execute(self):
        keypointDescriptors = self.GetInputStageValue(0, "keypointDescriptors")
        
        self.StartProcess()
        
        matchesFile = keypointDescriptors.GetKeyListPath() + ".matches.init.txt"
        
        if (Common.Utility.ShouldRun(self._properties["Force Run"], matchesFile)):
            
            self.RunCommand("ASIFTmatch", 
                            Common.Utility.CommandArgs(Common.Utility.Quoted(keypointDescriptors.GetKeyListPath()),
                                                       Common.Utility.Quoted(matchesFile)),
                            cwd = os.path.split(matchesFile)[0])            
            
        keyMatches = FeatureMatch.KeyMatches(matchesFile, keypointDescriptors, self._properties["Parse Matches"])
        
        self.SetOutputValue("keyMatches", keyMatches)

