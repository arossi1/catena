# Copyright (c) 2014, Adam J. Rossi. All rights reserved. See README for licensing details.
from .. import Common
import math, os

class KeypointDescriptors:

    def __init__(self, path="", kdList=[], genKeylist=True):
        self.__path = path
        self.__keypointDescriptors = kdList
        if (genKeylist): self.GenerateKeyList()
        
    def GetPath(self): return self.__path
    def GetKeyListPath(self): return self.__keyListPath
    def GetDescriptors(self): return self.__keypointDescriptors
    def GetDescriptor(self, fileName):
        for kd in self.GetDescriptors():
            if (kd.GetFileName()==fileName): return kd
        return None
    
    def GenerateKeyList(self):
        self.__keyListPath = os.path.join(self.__path, "keylist.txt")
        f = open(self.__keyListPath,"w")
        for kd in self.GetDescriptors():
            kdPath,kdFile = os.path.split(kd.GetFilePath())
            if (kdPath==self.__path):
                f.write(kdFile+"\n")
        f.close()
