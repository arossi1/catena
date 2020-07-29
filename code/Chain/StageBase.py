# Copyright (c) 2014, Adam J. Rossi. All rights reserved. See README for licensing details.
import sys, uuid, string, os
from . import Chain, Analyze

class StageBase:
    
    MAX_INPUT_STAGES = sys.maxsize
    
    def __init__(self, inputStages=None, stageDoc="", parameterDoc=None):
        self.__stageDoc = stageDoc
        if (parameterDoc==None): self.__parameterDoc = {}
        else:                    self.__parameterDoc = parameterDoc
        self._properties = {}
        self.__inputStages = []
        self.__outputStages = []
        self.__outputCache = None
        self.__prepared = False
        self._uid = uuid.uuid1()
        if (inputStages!=None):
            self.AddInputStage(inputStages)
        from . import StageRegistry
        if ("registry" in dir(StageRegistry) and 
            StageRegistry.registry.IsInitialized()):
            StageRegistry.registry.AddInstance(self)

    def AddInputStage(self, stages):
        self.__prepared = False
        if (isinstance(stages, list)):
            self.__inputStages += stages
            for stage in stages: stage.AddOutputStage(self)
        else:
            self.__inputStages.append(stages)
            stages.AddOutputStage(self)

    def AddOutputStage(self, stages):
        if (isinstance(stages, list)):  self.__outputStages += stages
        else:                           self.__outputStages.append(stages)
        
    def RemoveConnections(self):
        for outputStage in self.__outputStages:
            outputStage.__inputStages.remove(self)
        for inputStage in self.__inputStages:
            inputStage.__outputStages.remove(self)
        
    def GetInputStages(self):
        return self.__inputStages
    
    def GetOutputStages(self):
        return self.__outputStages 
    
    def NumInputStages(self):
        return len(self.__inputStages)
    
    def GetPropertyMap(self):
        d = {}
        for n in self._properties:
            d[n] = type(self._properties[n])                
        return d
    
    def GetPackageName(self):
        return str(self.__class__).split(".")[0]
    
    def GetStageName(self):
        return self.__class__.__name__
    
    def GetStageDescription(self):
        return self.__stageDoc
        
    def GetPropertyDescription(self, name):
        if (name in list(self.__parameterDoc.keys())):
            return self.__parameterDoc[name]
        else:
            raise Exception("Property does not exist: " + name)
        
    def SetPropertyDescription(self, name, desc):
        self.__parameterDoc[name] = desc
        
    def GetProperty(self, name):
        if (name in list(self._properties.keys())):
            return self._properties[name]
        else:
            raise Exception("Property does not exist: " + name)
        
    def SetProperty(self, name, val):
        if (name in list(self._properties.keys())):
            self._properties[name] = val
        else:
            raise Exception("Property does not exist: " + name)

    def __GetInputStagesInterfaces(self):
        # return list of dictionaries that represent the input stages' interface
        return [stage.GetOutputInterface() for stage in self.__inputStages]
    
    def Reset(self):        
        self.__prepared = False
        for stage in self.GetInputStages(): stage.Reset()
        
    def Prepare(self):
        # check:
        #   - parameters
        #   - inputs' outputs
        #   - max number of input stages

        # depth-first prepare
        for stage in self.GetInputStages(): stage.Prepare()
        if (self.__prepared): return
        
        # clear cache
        self.__outputCache = None
        
#        # validate interface names/types
#        myInputInterface = self.GetInputInterface()
#        for stage in self.__inputStages:
#            inputStageInterface = stage.GetOutputInterface()
#            for inputKey in myInputInterface.keys():
#                if (not inputStageInterface.has_key(inputKey)):
#                    raise Exception("[%s:Prepare] Input (%s) interface does not include: %s:%s" % (self.__class__.__name__,stage.__class__.__name__,inputKey,myInputInterface[inputKey]))                                    
#                if (inputStageInterface[inputKey] != myInputInterface[inputKey]):
#                    raise Exception("[%s:Prepare] Invalid input (%s) interface type: expected %s, received %s" % (self.__class__.__name__,inputStageInterface[inputKey].__class__.__name__,inputStageInterface[inputKey],myInputInterface[inputKey]))
        
        # ensure input interface is consistent with input stage's output interface
        
        myInputInterface = self.GetInputInterface()
        if (myInputInterface != None):
            for kv in list(myInputInterface.items()):
                
                try:
                    inputName,(inputIndex,inputType) = kv
                except:
                    raise Exception("[%s:Prepare] Input interface definition error" % (self.__class__.__name__))
                
                if (isinstance(inputIndex,tuple)):
                    for iIndex in range(inputIndex[0], inputIndex[0]+inputIndex[1]):
                        if (iIndex < self.NumInputStages()):  # check only valid input stage indices
                            if (inputName not in self.__inputStages[iIndex].GetOutputInterface()):
                                raise Exception("[%s:Prepare] Input stage %d does not include %s:%s" % \
                                                (self.__class__.__name__,iIndex,inputName,inputType))
                                
                            if (not issubclass(self.__inputStages[iIndex].GetOutputInterface()[inputName],inputType)):
                                raise Exception("[%s:Prepare] Input stage %d's output parameter (%s) type is %s, type should be %s" % \
                                                (self.__class__.__name__,
                                                 iIndex,
                                                 inputName,
                                                 self.__inputStages[iIndex].GetOutputInterface()[inputName],
                                                 inputType))
                else:
                    if (inputIndex >= self.NumInputStages()):
                        raise Exception("[%s:Prepare] Expected input stage at index %d" % \
                                        (self.__class__.__name__,inputIndex))
                        
                    if (inputName not in self.__inputStages[inputIndex].GetOutputInterface()):
                        raise Exception("[%s:Prepare] Input stage %d does not include %s:%s" % \
                                        (self.__class__.__name__,inputIndex,inputName,inputType))
                        
                    if (not issubclass(self.__inputStages[inputIndex].GetOutputInterface()[inputName], inputType) and
                        not issubclass(inputType, self.__inputStages[inputIndex].GetOutputInterface()[inputName])):
                        raise Exception("[%s:Prepare] Input stage %d's output parameter (%s) type is %s, type should be %s" % \
                                        (self.__class__.__name__,
                                         inputIndex,
                                         inputName,
                                         self.__inputStages[inputIndex].GetOutputInterface()[inputName],
                                         inputType))
            
        
        # successfully prepared stage
        self.__prepared = True
        
    def __InitializeOutputCache(self):
        self.__outputCache = {}
        if (self.GetOutputInterface()!=None):
            for k in list(self.GetOutputInterface().keys()):
                self.__outputCache[k] = None
            
    def __ValidateCompleteOutputCache(self):
        for k,v in list(self.__outputCache.items()):
            if (v==None):
                raise Exception("[%s::__ValidateCompleteOutputCache] Developer error, output parameter (%s) not filled" % \
                                (self.__class__.__name__,k))
            
            if (str(type(v)) == "<type 'instance'>" or
                str(type(v)).startswith("<class '")):
                if (issubclass(v.__class__, self.GetOutputInterface()[k])):
                    pass                    
                elif (str(self.GetOutputInterface()[k]) not in [v.__class__.__name__, "%s.%s" % (v.__module__, v.__class__.__name__)]):
                    raise Exception("[%s::__ValidateCompleteOutputCache] Developer error, output parameter (%s) type is %s, type should be %s" % \
                                    (self.__class__.__name__,k,v.__class__.__name__,self.GetOutputInterface()[k]))
            else:
                if (self.GetOutputInterface()[k] != type(v)):
                    raise Exception("[%s::__ValidateCompleteOutputCache] Developer error, output parameter (%s) type is %s, type should be %s" % \
                                    (self.__class__.__name__,k,type(v),self.GetOutputInterface()[k]))
            
    def GetOutput(self):
        # this method is called by the next stage
        # the outputs of this stage are cached within this class by ensuring Execute is only called when necessary
        self.Prepare()
        
        if (self.__outputCache==None):
            self.__InitializeOutputCache()            
            self.Execute()
            self.__ValidateCompleteOutputCache()
            
        return self.__outputCache
    
    def GetOutputByKey(self, key):
        
        if (key not in self.__outputCache):
            raise Exception("[%s:GetOutputByKey] Invalid output key: %s" % \
                            (self.__class__.__name__,key))
        
        return self.__outputCache[key]
    
    def GetInputStageValue(self, index, key):
        if (index >= self.NumInputStages()):
            raise Exception("[%s:GetInputStageValue] Invalid input stage index: %d" % \
                            (self.__class__.__name__,index))
        
        outputs = self.GetInputStages()[index].GetOutput()
        
        if (key not in outputs):
            raise Exception("[%s:GetInputStageValue] Invalid input stage (%s) key: %s" % \
                            (self.__class__.__name__,self.GetInputStages()[index].__class__.__name__,key))
        
        return outputs[key]
    
    def SetOutputValue(self, key, value):
        if (key not in self.__outputCache):
            raise Exception("[%s:SetOutputValue] Unknown output parameters: %s" % \
                            (self.__class__.__name__,key))
        
        # TODO: validate value's type        
        self.__outputCache[key] = value
        
    def StartProcess(self):
        name = self.__class__.__name__
        if (len(self._properties)>0):
            sargs = ["%s = %s" %(str(x),self._properties[x]) for x in sorted(self._properties.keys())]
            name = "%s [%s]" % (name, string.join(sargs,", "))
        Analyze.StartProcess(name)
        
    def RunCommand(self, exe, args="", cwd=None, shell=True, captureCout=False):
        import Common
        
        # find executable for given platform
        exe = Common.Utility.GetExePath(sys.modules[self.__class__.__module__].__file__, exe)
        cmd = "\"%s\" %s" % (exe, args)
        return Common.Utility.RunCommand(cmd, cwd=cwd, shell=shell, captureCout=captureCout)
    
    # pure virtual methods...
    def GetInputInterface(self):
        # return dictionary of input types, keyed by name (name->type)
        raise Exception("Derived class (%s) must implement GetInputInterface" % self.__class__.__name__)

    def GetOutputInterface(self):
        # return dictionary of output types, keyed by name (name->type)
        raise Exception("Derived class (%s) must implement GetOutputInterface" % self.__class__.__name__)

    def Execute(self):
        # carry out execution
        # note, this is called by GetOutputs
        # return dictionary of results keyed by name (name->object)
        raise Exception("Derived class (%s) must implement Execute" % self.__class__.__name__)
    
    
    
    
