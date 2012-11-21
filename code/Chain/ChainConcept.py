# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing details.
import os, sys
from StageBase import StageBase
from Chain import Chain

###############################################################################
class StringSource(StageBase):
    
    def __init__(self, s):
        StageBase.__init__(self)
        self.__string = s

    def GetInputInterface(self):
        return None
    
    def GetOutputInterface(self):
        return {"string":str}

    def Execute(self):
        self.StartProcess()
        
        self.SetOutputValue("string", self.__string)
    
    
###############################################################################
class StringToInt(StageBase):

    def __init__(self, inputStages):
        StageBase.__init__(self, inputStages)

    def GetInputInterface(self):
        return {"string":(0,str)}
    
    def GetOutputInterface(self):
        return {"integer":int}

    def Execute(self):
        input = self.GetInputStageValue(0, "string")
        
        self.StartProcess()
        
        val = int(input)
        
        self.SetOutputValue("integer", val)


###############################################################################
class Multiply(StageBase):

    def __init__(self, inputStages):
        StageBase.__init__(self, inputStages)

    def GetInputInterface(self):
        return {"integer":(0,int)}
    
    def GetOutputInterface(self):
        return {"integer":int}

    def Execute(self):
        values = []
        for i in range(self.NumInputStages()):
            values.append(self.GetInputStageValue(i, "integer"))
            
        self.StartProcess()

        product = 1
        for value in values:
            product *= value
        
        self.SetOutputValue("integer", product)
        

###############################################################################
class IntSink(StageBase):

    def __init__(self, inputStages):
        StageBase.__init__(self, inputStages)

    def GetInputInterface(self):
        return {"integer":(0,int)}
    
    def GetOutputInterface(self):
        return None

    def Execute(self):
        input = self.GetInputStageValue(0, "integer")
        
        self.StartProcess()
        
        print "Result = %d" % input
        
        
        
###############################################################################
if __name__=="__main__":

    stringSource1 = StringSource("2")
    stringToInt1 = StringToInt(stringSource1)

    stringSource2 = StringSource("3")
    stringToInt2 = StringToInt(stringSource2)
    
    multiply = Multiply([stringToInt1, stringToInt2, stringToInt2, stringToInt1])
    
    intSink = IntSink([stringSource1,multiply])
   
    Chain.Render(intSink)
    
    
    #
    # Errors Detected:
    #
    # connect too many input stages
    # change type of output
    # do not fill output parameter
    # incorrect output type 
    # invalid input stage index
    # invalid input stage key (GetInputStageValue)
    # set invalid output parameter
    #
    
    
    
