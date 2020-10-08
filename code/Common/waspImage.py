# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing details.
import os, glob



class waspImage:
    
    def __init__(self, metadata, dirPath):
        self._dirPath = dirPath
        self.parseMetadata(metadata)
        
    def parseMetadata(self, metadata):
        metadata = metadata.replace("\t", " ").strip()
        while (metadata.find("  ") >= 0): metadata = metadata.replace("  ", " ")
        self._id, self._event, self._time, self._easting, self._northing, self._orthometricHeight, self._omega, self._phi, self._kappa, self._lat, self._long = \
            metadata.split(" ")
            
    def getId(self):                return self._id
    def getEvent(self):             return self._event
    def getTime(self):              return self._time
    def getEasting(self):           return self._easting
    def getNorthing(self):          return self._northing
    def getOrthometricHeight(self): return self._orthometricHeight
    def getOmega(self):             return self._omega
    def getPhi(self):               return self._phi
    def getKappa(self):             return self._kappa
    def getLat(self):               return self._lat
    def getLong(self):              return self._long
    
    def fileExists(self):
        return (self.getFilePath()!=None)
        
    def getFilePath(self):
        fn = os.path.join(self._dirPath, self._id+"*.*")
        l = glob.glob(fn)
        if (len(l)==1): return l[0]
        else: return None
    
    def __str__(self):
        p = (self._id, self._event, self._time, self._easting, self._northing, self._orthometricHeight, self._omega, self._phi, self._kappa, self._lat, self._long)
        return ", ".join(p)
    
    