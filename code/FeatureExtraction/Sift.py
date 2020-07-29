# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing details.
from .. import Chain, Common, FeatureExtraction
from .KeypointDescriptorFileVLFeat import KeypointDescriptorFileVLFeat
import os, string
import threading, multiprocessing

class Sift(Chain.StageBase):

    def __init__(self, 
                 inputStages=None, 
                 parseKDF=False, 
                 method="SiftWin32",
                 CPUs=multiprocessing.cpu_count(),
                 forceRun=False):
        Chain.StageBase.__init__(self,
                                 inputStages,
                                 "Generates Sift descriptors for images",
                                 {"Parse Descriptors":"Whether to parse the keypoint descriptors after generation",
                                  "Sift Method":"Sift implementation to use {SiftWin32, SiftHess, SiftGPU, VLFeat}",
                                  "CPUs":"Number of CPUs to utilize",
                                  "Force Run":"Force run if outputs already exist"})
        
        self._properties["Parse Descriptors"] = parseKDF
        self._properties["Sift Method"] = method
        self._properties["CPUs"] = CPUs
        self._properties["Force Run"] = forceRun

    def GetInputInterface(self):
        return {"images":(0,Common.sfmImages)}
    
    def GetOutputInterface(self):
        return {"keypointDescriptors":FeatureExtraction.KeypointDescriptors}
    
    
    class Worker(threading.Thread):
        def __init__(self, Q, outputList, parent):
            threading.Thread.__init__(self)
            self.__Q = Q
            self.__outputList = outputList
            self.__parent = parent
            self.__errors = []
            
        def getErrors(self): return self.__errors
            
        def run(self):
            
            while (True):
                try:
                    i,im = self.__Q.get_nowait()                    
                    try:
                        self.__outputList[i] = self.process(im)
                    except Exception as e:
                        self.__errors.append(str(e))
                except:
                    break
                
        def process(self, im):
            # special case
            if (self.__parent._properties["Sift Method"] == "VLFeat"):
                
                exeName = "sift"
                argsPattern = "--orientations \"%s\" -o \"%s\""                
                
                keypointDescriptorFile = os.path.join(os.path.splitext(im.GetFilePath())[0]+".key")
                
                if (Common.Utility.ShouldRun(self.__parent._properties["Force Run"], keypointDescriptorFile)):
                    
                    self.__parent.RunCommand(exeName,
                                             argsPattern % (im.GetFilePath(),keypointDescriptorFile))
                    
                    vlkd = KeypointDescriptorFileVLFeat(keypointDescriptorFile, True)
                    kd = FeatureExtraction.KeypointDescriptorFileLowe(vlkd)
                    kd.Write(vlkd.GetFilePath())
                    
                else:
                    kd = FeatureExtraction.KeypointDescriptorFileLowe(keypointDescriptorFile, 
                                                                      self.__parent._properties["Parse Descriptors"])
                return kd
                    
            else:    
                
                if (self.__parent._properties["Sift Method"] == "SiftWin32"):
                    exeName = "siftWin32"
                    argsPattern = "<\"%s\"> \"%s\""
                elif (self.__parent._properties["Sift Method"] == "SiftHess"):
                    exeName = "sifthess"
                    argsPattern = "\"%s\" \"%s\""
                elif (self.__parent._properties["Sift Method"] == "SiftGPU"):
                    exeName = "SiftGPUKeypoint"
                    argsPattern = "\"%s\" \"%s\""
                else:
                    raise Exception("Unknown Sift method: " + self.__parent._properties["Sift Method"])                
                
                keypointDescriptorFile = os.path.join(os.path.splitext(im.GetFilePath())[0]+".key")
                
                if (Common.Utility.ShouldRun(self.__parent._properties["Force Run"], keypointDescriptorFile)):
                    
                    self.__parent.RunCommand(exeName,
                                             argsPattern % (im.GetFilePath(),keypointDescriptorFile))
                
                kd = FeatureExtraction.KeypointDescriptorFileLowe(keypointDescriptorFile, 
                                                                  self.__parent._properties["Parse Descriptors"])
                return kd
                

    def Execute(self):
        images = self.GetInputStageValue(0, "images")
        
        self.StartProcess()
    
        q = multiprocessing.Queue()
        for i,im in enumerate(images.GetImages()):
            q.put_nowait((i,im))
            
        kds = [None]*len(images.GetImages())
        workers = []
        for i in range(self._properties["CPUs"]):
            w = Sift.Worker(q, kds, self)
            w.start()
            workers.append(w)
        
        errors = []
        for w in workers:
            w.join()
            errors.extend(w.getErrors())
            
        if (len(errors)>0):
            raise Exception(string.join(errors,"\n"))
        
        kds = FeatureExtraction.KeypointDescriptors(images.GetPath(), kds)
        self.SetOutputValue("keypointDescriptors", kds)        
