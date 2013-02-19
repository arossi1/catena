# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing details.
import Chain

class MuxStage(Chain.StageBase):

    def __init__(self, inputStages=None, stagesToMux=None, selectedStageIndex=0):
        Chain.StageBase.__init__(self,
                                 inputStages,
                                 "A stage that takes a collection of stages and allows for the selection of one of the given stages to mimic")

        self._selectedStageIndex = selectedStageIndex
        self._stagesToMux = stagesToMux
        
    def NumStages(self): return len(self._stagesToMux)
    def SelectStage(self, index): self._selectedStageIndex = index

    def GetInputInterface(self):        
        return self._stagesToMux[self._selectedStageIndex].GetInputInterface()
    
    def GetOutputInterface(self):
        return self._stagesToMux[self._selectedStageIndex].GetOutputInterface()
    
    def SetOutputValue(self, key, value):
        self._stagesToMux[self._selectedStageIndex].SetOutputValue(key, value)
        
    def Prepare(self):
        self._stagesToMux[self._selectedStageIndex].Prepare()
        
    def GetInputStageValue(self, index, key):
        self._stagesToMux[self._selectedStageIndex].GetInputStageValue(index, key)

    def Execute(self):
        return self._stagesToMux[self._selectedStageIndex].Execute()

