# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing details.
import pickle


class StageRegistry:
    
    def __init__(self):
        self.__initialized = False
        self.__stageInstances = {}
        self.__populate()
        self.__initialized = True
        
    def GetPackages(self):
        return sorted(self.__regDict.keys())
    
    def GetStages(self, package):
        return sorted(self.__regDict[package].keys())
    
    def GetStageDescription(self, package, stage):
        return self.__regDict[package][stage][0].GetStageDescription()
    
    def GetStagePropertyMap(self, package, stage):
        return self.__regDict[package][stage][0].GetPropertyMap()
    
    def GetStagePropertyDescription(self, package, stage, property):
        return self.__regDict[package][stage][0].GetPropertyDescription(property)
    
    def GetStagePropertyType(self, package, stage, property):
        return self.__regDict[package][stage][0].GetPropertyMap()[property]
    
    def CreateInstance(self, package, stage):
        return self.__regDict[package][stage][1]()
    
    def AddInstance(self, stageObject):
        self.__stageInstances[stageObject._uid] = stageObject
    
    def RemoveInstance(self, stageObject):
        stageObject.RemoveConnections()
        del self.__stageInstances[stageObject._uid]
        
    def GetStageInstances(self): return list(self.__stageInstances.values())
        
    def IsInitialized(self): return self.__initialized
    
    def Save(self, filePath):
        # save:
        #  - dictionary of uid-> (package name, stage name, property dictionary)
        #  - dictionary of uid-> (<input stage uid's>)
        d1 = {}
        d2 = {}
        for uidKey in list(self.__stageInstances.keys()):
            d1[uidKey] = (self.__stageInstances[uidKey].GetPackageName(),
                          self.__stageInstances[uidKey].GetStageName(),
                          self.__stageInstances[uidKey]._properties)
            
            d2[uidKey] = tuple([inputStage._uid for inputStage in self.__stageInstances[uidKey].GetInputStages()])
        
        f = open(filePath,"wb")
        pickle.dump(d1,f)
        pickle.dump(d2,f)
        f.close()
        
    def Load(self, filePath):
        # load:
        #  - dictionary of uid-> (package name, stage name, property dictionary)
        #  - dictionary of uid-> (<input stage uid's>)
        f = open(filePath,"rb")
        d1 = pickle.load(f)
        d2 = pickle.load(f)
        f.close()
        
        # create instances
        stageInstances = {}
        for uidKey in list(d1.keys()):
            o = self.CreateInstance(d1[uidKey][0], d1[uidKey][1])
            o._uid = uidKey
            for propName in list(d1[uidKey][2].keys()):
                o.SetProperty(propName, d1[uidKey][2][propName])
            stageInstances[o._uid] = o
            
        self.__stageInstances = stageInstances
        
        # link
        for uidKey in list(d2.keys()):
            stageInstances[uidKey].AddInputStage([stageInstances[uid] for uid in d2[uidKey]])
            
        
        # return head & tail stages
        return self.GetHeadTailStages()
    
    
    def GetHeadTailStages(self):
        headStages = []
        tailStages = []
        for stage in list(self.__stageInstances.values()):
            if (len(stage.GetInputStages())==0):
                headStages.append(stage)
            if (len(stage.GetOutputStages())==0):
                tailStages.append(stage)                
        return (tuple(headStages), tuple(tailStages))
    
    
    def __print(self):
        for package in self.GetPackages():
            print("%s" % package)
            for stage in self.GetStages(package):
                print(" %s" % stage)
                for property in sorted(self.GetStagePropertyMap(package, stage).keys()):
                    print("  %s: %s (%s)" % (property, 
                                             self.GetStagePropertyDescription(package,stage,property), 
                                             str(self.GetStagePropertyType(package,stage,property))))
        
    def __populate(self):
        
        from .StageBase import StageBase
        import os
        
        #curPath = os.path.abspath(".")
        #os.chdir("..")
        
        self.__regDict = {}
        for dn in os.listdir("."):
            packageName = dn
            if (os.path.isdir(packageName)):
                try:
                    mod = __import__(packageName, fromlist=[])
                    for className in dir(mod):
                        try:
                            co = getattr(mod, className)
                            if (issubclass(co, StageBase) and co!=StageBase):
                                if (packageName not in self.__regDict): self.__regDict[packageName] = {}
                                o = co()
                                self.__regDict[packageName][o.GetStageName()] = (o,co)
                        except Exception as e:
                            pass
                except:
                    pass                
        #os.chdir(curPath)
        
    
registry = StageRegistry()
def Load(filePath): return registry.Load(filePath)
def Save(filePath): registry.Save(filePath)


    
    




            
            
            
            