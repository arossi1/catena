# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing details.

class VisEntry:
    
    def __init__(self, id, numImagesForReconstruction, imageIndices):
        self.__id = id
        self.__numImagesForReconstruction = numImagesForReconstruction
        self.__imageIndices = imageIndices
        
    def ID(self):                           return self.__id
    def NumImagesForReconstruction(self):   return self.__numImagesForReconstruction
    def ImageIndices(self):                 return self.__imageIndices
        
    def __str__(self):
        return "Image Index: %d\nImages used for reconstruction: %d\nImage indices: %s" % \
            (self.__id, self.__numImagesForReconstruction, str(self.__imageIndices))

class VisFile:

    def __init__(self, filePath):
        self.__filePath = filePath
        self.__parse()
        
    def GetEntries(self): return self.__entries
    
    def __parse(self):
        self.__entries = []
        f = open(self.__filePath, "r")
        sent = f.readline().strip()
        if (sent!="VISDATA"): raise Exception("Invalid Vis file")
        numImages = int(f.readline())
        for iImage in range(numImages):
            l = f.readline().strip()
            while ("  " in l): l = l.replace("  ", " ")
            v = l.split(" ")
            id = int(v[0])
            numImagesForReconstruction = int(v[1])
            imageIndices = tuple([int(i) for i in v[2:]])
            self.__entries.append( VisEntry(id, numImagesForReconstruction, imageIndices) )
        f.close()
        
    def __str__(self):
        s = ""
        for e in self.__entries:
            s += str(e) + "\n"
        return s
                       
        
    

        
