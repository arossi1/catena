# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing details.
import Chain

class TapPoint(Chain.StageBase):

    def __init__(self, inputStages=None, printFunctionsDict=None):
        Chain.StageBase.__init__(self,
                                 inputStages,
                                 "Generic tap point stage for inspecting output values of a stage",
                                 {"Print Functions":"Dictionary of functions used to print parameters, keyed by type"})

        self._properties["Print Functions"] = {}
        if (printFunctionsDict!=None):
            self._properties["Print Functions"] = printFunctionsDict

    def GetInputInterface(self):
        
        if (len(self.GetInputStages())!=1):
            raise Exception("TapPoint stage must have only one input stage")

        inputInterface = {}
        for valName,valType in self.GetInputStages()[0].GetOutputInterface().items():
            inputInterface[valName] = (0,valType)
        return inputInterface
    
    def GetOutputInterface(self):
        return self.GetInputStages()[0].GetOutputInterface()

    def Execute(self):

        # get output values of input stage
        vals = {}
        for valName,valType in self.GetInputStages()[0].GetOutputInterface().items():
            vals[valName] = self.GetInputStageValue(0,valName)
        
        self.StartProcess()

        # write values and set output values (pass-through)
        Chain.Analyze.WriteStatus("")
        for valName,valType in self.GetInputStages()[0].GetOutputInterface().items():

            Chain.Analyze.WriteStatus(valName+"\n")

            # use print function for type if provided
            if (self._properties["Print Functions"].has_key(valType)):
                Chain.Analyze.WriteStatus(str(self._properties["Print Functions"][valType](vals[valName])))
            else:
                Chain.Analyze.WriteStatus(str(vals[valName]))
                
            Chain.Analyze.WriteStatus("")

            self.SetOutputValue(valName, vals[valName])

        

        

        
