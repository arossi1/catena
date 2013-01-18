# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing details.

import os,string

class Patch:

    def __init__(self,point3d,normal3d,scores,goodImageIndices,badImageIndices):
        self.__point3d = point3d
        self.__normal3d = normal3d
        self.__scores = scores
        self.__goodImageIndices = goodImageIndices
        self.__badImageIndices = badImageIndices

    def Point3D(self): return self.__point3d
    def Normal3D(self): return self.__normal3d
    def Scores(self): return self.__scores
    def GoodImageIndices(self): return self.__goodImageIndices
    def BadImageIndices(self): return self.__badImageIndices

    def __str__(self):
        print self.__point3d+self.__normal3d+self.__scores+[str(self.__goodImageIndices),str(self.__badImageIndices)]
        return "(%f,%f,%f,%f)\n  [normal=(%f,%f,%f,%f)]\n  [scores=(%f,%f,%f)] [good indices=[%s]\n  [bad indices=[%s]" % \
            tuple(self.__point3d+self.__normal3d+self.__scores+[str(self.__goodImageIndices),str(self.__badImageIndices)])
        

class PatchFile:

    def __init__(self, filePath):
        self.__filePath = filePath
        self.__parsed = False
        self.__patches = []
        
    def __checkParse(self):
        if (not self.__parsed):
            self.__parse()
            self.__parsed = True

    def Patches(self):
        self.__checkParse()
        return self.__patches
                       

    def __parse(self):
        f = open(self.__filePath, "r")
        
        # verify sentinel
        sent = f.readline().strip()
        if (sent!="PATCHES"):
            f.close()
            raise Exception("Invalid patch file")

        numPatches = int(f.readline().strip())

        while(True):
            
            # find PATCHS sentinel
            while (True):
                sent=f.readline()
                if (sent.strip()=="PATCHS" or sent==""):break
            if (sent.strip()!="PATCHS"):break

            # 3D location
            point3d = [float(x) for x in f.readline().strip().split(" ")]
            
            # 3D normal
            normal3d = [float(x) for x in f.readline().strip().split(" ")]
            
            # photometric consistency score (average normalized cross correlation -1.0 worse to +1.0 best)
            # next 2 numbers are for debugging (not documented)
            scores = [float(x) for x in f.readline().strip().split(" ")]
            
            # # of images that the point is visibile in and textures agree well
            numGoodImages = int(f.readline().strip())

            # good image indices
            goodImageIndices = []
            if (numGoodImages>0): goodImageIndices = [int(x) for x in f.readline().strip().split(" ")]
            if (numGoodImages!=len(goodImageIndices)):
                raise Exception("Inconsistent good image indices")

            # # of images that the point is visibile in but textutres do not agree well
            numBadImages = int(f.readline().strip())

            # bad image indices
            badImageIndices = []
            if (numBadImages>0): badImageIndices = [int(x) for x in f.readline().strip().split(" ")]
            if (numBadImages!=len(badImageIndices)):
                raise Exception("Inconsistent bad image indices")

            self.__patches.append(Patch(point3d,normal3d,scores,goodImageIndices,badImageIndices))

        if (numPatches!=len(self.__patches)):
            raise Exception("Inconsistent number of patches: read %d, expected %d" % (len(self.__patches),numPatches))
            
    def __str__(self):
        self.__checkParse()
        s = ""
        for patch in self.__patches:
            s += str(patch) + "\n"
        return s


    
