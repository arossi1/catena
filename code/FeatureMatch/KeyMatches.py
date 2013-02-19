# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing details.


class KeyMatch:
    
    def __init__(self, kdf1, kdf2, idxIm1, idxIm2, matchIndices):
        self.__kdf1 = kdf1
        self.__kdf2 = kdf2
        self.__idxIm1 = idxIm1
        self.__idxIm2 = idxIm2
        self.__matchIndices = matchIndices
        self.__kdMatches = []
    
    def GetKeypointDescriptorFile1(self): return self.__kdf1
    def GetKeypointDescriptorFile2(self): return self.__kdf2
    def GetImageIndex1(self):             return self.__idxIm1
    def GetImageIndex2(self):             return self.__idxIm2
    
    def GetMatches(self):
        if (len(self.__kdMatches)==0): self.Parse()
        return self.__kdMatches
    
    def Parse(self):
        self.__populateMatches()
    
    def __populateMatches(self):        
        for m1,m2 in self.__matchIndices:
            self.__kdMatches.append( (self.__kdf1.GetDescriptors()[m1],
                                      self.__kdf2.GetDescriptors()[m2],
                                      m1,m2) )

class KeyMatches:

    def __init__(self, keyMatchFile, keypointDescriptors, parseKDF):
        self.__keyMatchFile = keyMatchFile
        self.__keypointDescriptors = keypointDescriptors
        self.__parse(parseKDF)
    
    def GetPath(self):
        return self.__keyMatchFile
    
    def GetKeyMatchFiles(self):
        if (len(self.__keyMatches)==0): 
            self.__parse()
        return self.__keyMatches

    @staticmethod
    def ReadIntPair(f, delimiter=" "):
        l = f.readline()
        if (l==""): return (None,None)
        i1,i2 = l.strip().split(delimiter)
        return (int(i1), int(i2))

    def __parse(self, parseKDF):        
        self.__keyMatches = []

        f = open(self.__keyMatchFile,"r")

        idxIm1, idxIm2 = KeyMatches.ReadIntPair(f)
        
        while (idxIm1!=None and idxIm2!=None):
            numMatches = int(f.readline())
            matchIndices = []
            for i in range(numMatches):
                matchIndices.append( KeyMatches.ReadIntPair(f) )
            
            km = KeyMatch(self.__keypointDescriptors.GetDescriptors()[idxIm1],
                          self.__keypointDescriptors.GetDescriptors()[idxIm2],
                          idxIm1,idxIm2,
                          matchIndices)
            if (parseKDF): km.Parse()
            self.__keyMatches.append(km)
            idxIm1, idxIm2 = KeyMatches.ReadIntPair(f)
        f.close()
        
        
