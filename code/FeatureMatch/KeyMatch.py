# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing details.
from catena import Chain, Common, FeatureExtraction
from KeyMatches import KeyMatches
import os

class KeyMatch(Chain.StageBase):

    def __init__(self, inputStages=None, parseMatches=False, method="KeyMatchFull", forceRun=False):
        Chain.StageBase.__init__(self,
                                 inputStages,
                                 "Performs keypoint matching",
                                 {"Parse Matches":"Whether to parse the keypoint matches",
                                  "Key Match Method":"Key matching implementation to employ {KeyMatchFull, KeyMatchGPU}",
                                  "Force Run":"Force run if outputs already exist"})
        
        self._properties["Parse Matches"] = parseMatches
        self._properties["Key Match Method"] = method
        self._properties["Force Run"] = forceRun
        
        
    def GetInputInterface(self):
        return {"keypointDescriptors":(0,FeatureExtraction.KeypointDescriptors)}
    
    def GetOutputInterface(self):
        return {"keyMatches":KeyMatches}
    
    def Execute(self):
        keypointDescriptors = self.GetInputStageValue(0, "keypointDescriptors")
        
        self.StartProcess()
        
        if (self._properties["Key Match Method"] == "KeyMatchFull"):
            keymatchExe = "KeyMatchFull"
        elif (self._properties["Key Match Method"] == "KeyMatchGPU"):
            keymatchExe = "SiftGPUMatch"
        else:
            raise Exception("Unknown Key Match method: " + self._properties["Key Match Method"])
            
        matchesFile = keypointDescriptors.GetKeyListPath() + ".matches.init.txt"
        
        if (Common.Utility.ShouldRun(self._properties["Force Run"], matchesFile)):
            
            self.RunCommand(keymatchExe, 
                            Common.Utility.CommandArgs(Common.Utility.Quoted(keypointDescriptors.GetKeyListPath()),
                                                       Common.Utility.Quoted(matchesFile)),
                            cwd = os.path.split(matchesFile)[0])
            
            
    	keyMatches = KeyMatches(matchesFile, keypointDescriptors, self._properties["Parse Matches"])
        
        self.SetOutputValue("keyMatches", keyMatches)

