# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing details.

import struct, array, os
from .KeypointDescriptorFile import KeypointDescriptorFile
from .KeypointDescriptor import KeypointDescriptor


class DaisyOutput:
    
    # data types
    DATA_TYPE_CHAR = 0
    DATA_TYPE_FLOAT = 1
    DATA_TYPE_DOUBLE = 2
    DATA_TYPE_INT = 3
    
    def __init__(self, filePath, defaultValue=0.0):
        self._defaultValue = defaultValue
        self._f = None
        if (os.path.isfile(filePath)):
            self._filePath = filePath
            self._f = open(self._filePath,"rb")
            self._readHeader()
            self._determineDataTypeFormatChar()
        
    def __del__(self):
        self._f.close()    
    
    def getDataType(self):      return self._dataType
    def getHeight(self):        return self._height
    def getWidth(self):         return self._width
    def getDataLength(self):    return self._dataLength    
    
    def _readHeader(self):
        SIZE_INT = 4
        self._dataType, self._height, self._width, self._dataLength = struct.unpack("@iiii", self._f.read(4*SIZE_INT))
        
    def _determineDataTypeFormatChar(self):
        # determine data type format
        if   (self._dataType==DaisyOutput.DATA_TYPE_CHAR):   self._formatChar = "b"
        elif (self._dataType==DaisyOutput.DATA_TYPE_FLOAT):  self._formatChar = "f"
        elif (self._dataType==DaisyOutput.DATA_TYPE_DOUBLE): self._formatChar = "d"
        elif (self._dataType==DaisyOutput.DATA_TYPE_INT):    self._formatChar = "i"
        else: raise Exception("Unknown data type: %d" % self._dataType)
        
    def readNextElement(self):
        if (self._f):
            vector = array.array(self._formatChar)
            vector.fromfile(self._f, self._dataLength)
            return vector.tolist()
        else:
            return [self._defaultValue]
    
    

class DaisyKeypointDescriptorFile(KeypointDescriptorFile):   
    
    def __init__(self, keypointDescriptorFile,
                 keypointDescriptorFileScales="",
                 keypointDescriptorFileOrientation="",
                 siftNormalize=False,
                 parse=True):
        
        KeypointDescriptorFile.__init__(self, keypointDescriptorFile)
        self._keypointDescriptorFileScales = keypointDescriptorFileScales
        self._keypointDescriptorFileOrientation = keypointDescriptorFileOrientation
        self._siftNormalize = siftNormalize
        if (parse): self._parse(keypointDescriptorFileScales, keypointDescriptorFileOrientation, siftNormalize)
        
    def Parse(self):
        self._parse(self._keypointDescriptorFileScales,
                    self._keypointDescriptorFileOrientation,
                    self._siftNormalize)

    def _parse(self, keypointDescriptorFileScales, keypointDescriptorFileOrientation, siftNormalize):

        # descriptors file
        descriptors = DaisyOutput(self._keypointDescriptorFile)
        self._keypointDescriptorLength = descriptors.getDataLength()
        
        # scales file
        scales = DaisyOutput(keypointDescriptorFileScales, 1.0)
        if (os.path.isfile(keypointDescriptorFileScales)):
            if (scales.getHeight()!=descriptors.getHeight() or scales.getWidth()!=descriptors.getWidth()):
                raise Exception("Scales header is different from keypoint descriptor header")

        # orientations file
        orientations = DaisyOutput(keypointDescriptorFileOrientation, 0.0)
        if (os.path.isfile(keypointDescriptorFileOrientation)):
            if (orientations.getHeight()!=descriptors.getHeight() or orientations.getWidth()!=descriptors.getWidth()):
                raise Exception("Orientation header is different from keypoint descriptor header")
        
        # read descriptors
        if (siftNormalize):
            maxVal = 0.154
            scaleFactor = 255.0/maxVal
            
            for row in range(descriptors.getHeight()):
                for column in range(descriptors.getWidth()):
                    descriptor = [int(round(x*scaleFactor)) for x in descriptors.readNextElement()]
                    scale = scales.readNextElement()[0]
                    orientation = orientations.readNextElement()[0]
                    kpd = KeypointDescriptor(float(row), float(column),
                                             scale, orientation, descriptor)
                    self._keypointDescriptors.append(kpd)
        else:
            for row in range(descriptors.getHeight()):
                for column in range(descriptors.getWidth()):
                    descriptor = descriptors.readNextElement()
                    scale = scales.readNextElement()[0]
                    orientation = orientations.readNextElement()[0]
                    kpd = KeypointDescriptor(float(row), float(column),
                                             scale, orientation, descriptor)
                    self._keypointDescriptors.append(kpd)
        
        del descriptors
        del scales
        del orientations
            
        
        
