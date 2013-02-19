# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing details.

import string
from KeypointDescriptorFile import KeypointDescriptorFile
from KeypointDescriptor import KeypointDescriptor


class KeypointDescriptorFileVLFeat(KeypointDescriptorFile):

    def __init__(self, keypointDescriptorFile, parse=True):
        KeypointDescriptorFile.__init__(self, keypointDescriptorFile)
        if (parse): self._parse()
        
    def _parse(self, offsetX=0, offsetY=0):
        
        f = open(self._keypointDescriptorFile, "r")
        
        self._keypointDescriptorLength = None
        for l in f.readlines():
            data = l.strip().split(" ")
            row, column, scale, orientation = data[:4]
            data = data[4:]            
            vector = [int(x) for x in data]
            
            if (self._keypointDescriptorLength==None): 
                self._keypointDescriptorLength = len(vector)
            elif (len(vector)!=self._keypointDescriptorLength): 
                raise Exception("[KeypointDescriptorFileVLFeat] Inconsistent descriptor length")
            
            kpd = KeypointDescriptor(float(row)+offsetY, float(column)+offsetX,
                                     float(scale), float(orientation), vector)
            
            self._keypointDescriptors.append(kpd)
        f.close()
            
            
            
    
