# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing details.

import string
from KeypointDescriptorFile import KeypointDescriptorFile
from KeypointDescriptor import KeypointDescriptor


class SiftWin32KeypointDescriptorFile(KeypointDescriptorFile):

    def __init__(self, fpOrkdfOrList, parse=True):
        if (type(fpOrkdfOrList)==str):
            KeypointDescriptorFile.__init__(self, fpOrkdfOrList)
            if (parse): self._parse()
        elif (type(fpOrkdfOrList)==list):
            self._keypointDescriptorFile = None
            self._keypointDescriptorLength = len(fpOrkdfOrList[0].Vector())
            self._keypointDescriptors = fpOrkdfOrList            
        else:
            self._keypointDescriptorLength = fpOrkdfOrList._keypointDescriptorLength
            self._keypointDescriptors = fpOrkdfOrList._keypointDescriptors

    def _parse(self, offsetX=0, offsetY=0):
        
        f = open(self._keypointDescriptorFile, "r")

        # parse data into list of strings
        data = []
        for l in f.readlines():
            data += l.strip().split(" ")
        f.close()

        # get # keypoints and descriptor length
        numKeypointDescriptors = int(data.pop(0))
        self._keypointDescriptorLength = int(data.pop(0))

        # read descriptors
        for i in range(numKeypointDescriptors):
            row, column, scale, orientation = data[:4]
            data = data[4:]
            vector = [int(x) for x in data[:self._keypointDescriptorLength]]
            data = data[self._keypointDescriptorLength:]
            kpd = KeypointDescriptor(float(row)+offsetY, float(column)+offsetX,
                                     float(scale), float(orientation), vector)
            self._keypointDescriptors.append(kpd)
                
    
            
            
            
    
