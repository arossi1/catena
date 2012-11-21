# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing details.
import Common
import math, os

class KeypointDescriptors:

    def __init__(self, path, kdList):
        self.__path = path
        self.__keypointDescriptors = kdList
        self.GenerateKeyList()
        
    def GetKeyListPath(self): return self.__keyListPath
    def GetDescriptors(self): return self.__keypointDescriptors
    def GetDescriptor(self, fileName):
        for kd in self.__keypointDescriptors:
            if (kd.GetFileName()==fileName): return kd
        return None
    
    def GenerateKeyList(self, ext="*.key"):
        self.__keyListPath = os.path.join(self.__path, "keylist.txt")
        Common.Utility.WriteFileList(self.__path, ext, "keylist.txt")



