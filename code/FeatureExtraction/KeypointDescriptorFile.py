# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing details.

from KeypointDescriptor import KeypointDescriptor
import sys, os, string, copy

class KeypointDescriptorFile:

    def __init__(self, 
                 keypointDescriptorFile,
                 keypointDescriptorLength=0,
                 keypointDescriptors=[]):
        self._keypointDescriptorFile = keypointDescriptorFile
        self._keypointDescriptorLength = keypointDescriptorLength
        self._keypointDescriptors = keypointDescriptors
        
    def Clone(self):
        kdfClone = KeypointDescriptorFile(self._keypointDescriptorFile)
        kdfClone._keypointDescriptorLength = self._keypointDescriptorLength
        kdfClone._keypointDescriptors = copy.deepcopy(self.GetDescriptors())
        return kdfClone
    
    def Filter(self, x,y, w,h):
        if (x<0 or y<0 or w<=0 or h<=0): return
        
        x1 = x+w
        y1 = y+h
        
        kds = []
        for kd in self._keypointDescriptors:
            if (kd.Column()>=x and kd.Column()<=x1 and
                kd.Row()>=y and kd.Row()<=y1):
                kds.append(kd)
        self._keypointDescriptors = kds
            
    
    def GetFileName(self): return os.path.split(self._keypointDescriptorFile)[1]
    def GetFilePath(self): return self._keypointDescriptorFile
    def GetDescriptors(self):
        if (len(self._keypointDescriptors)==0): self.Parse()
        return self._keypointDescriptors
    def SortDescriptors(self): self._keypointDescriptors.sort(cmp=lambda x,y: x.Compare(y))
    
    def Parse(self, offsetX=0, offsetY=0):
        self._parse(offsetX, offsetY)    
        
    def MatchDescriptors(self, kdf):        
        matches = []
        
        for kd1 in self._keypointDescriptors:
            minDistance1 = sys.maxint
            minDistance2 = sys.maxint
            
            for kd2 in kdf._keypointDescriptors:
                d = kd1.DistanceSquared(kd2)
                if (d < minDistance1):
                    kdMatch = kd2
                    minDistance1 = d
                elif (d < minDistance2):
                    minDistance2 = d

            # Check whether closest distance is less than 0.6 of second
            if (10 * 10 * minDistance1 < 6 * 6 * minDistance2):
                matches.append((kd1, kdMatch))

        return matches
    
    
    def Write(self, keypointDescriptorFile):
        
        f = open(keypointDescriptorFile, "w")
        f.write("%d %d\n" % (len(self._keypointDescriptors), self._keypointDescriptorLength))
        for kd in self._keypointDescriptors:            
            f.write("%f %f %f %f\n" % (kd.Row(), kd.Column(), kd.Scale(), kd.Orientation()))
            v = copy.copy(kd.Vector())
            while (len(v)):
                numVals = min(20,len(v))
                vals = v[:numVals]
                v = v[numVals:]
                f.write((string.join(["%d"]*numVals," ")+"\n") % tuple(vals))
        f.close()


    def ClearKeypointDescriptors(self):
        self._keypointDescriptors = []
        
    
    def __str__(self):
        s  = "      Keypoint Descriptor File: %s\n" % self._keypointDescriptorFile
        s += "Number of Keypoint Descriptors: %d\n" % len(self._keypointDescriptors)
        s += "    Keypoint Descriptor Length: %d\n" % self._keypointDescriptorLength
        s += "\n"
        for i, kd in enumerate(self._keypointDescriptors):
            s += "[Keypoint Descriptor %d]\n%s\n" % (i, kd)
        return s
