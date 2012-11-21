# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing details.

import os, glob

class CameraMatrices:
    
    def __init__(self, path):
        self.__path = path
        self.__readMatrices()
        
    def GetMatrices(self): return self.__matrices
        
    def __readMatrices(self):
        self.__matrices = {}
        for fp in glob.glob(os.path.join(self.__path,"*.txt")):
            self.__matrices[fp] = CameraMatrix(fp)            
        
    def __str__(self):
        s = ""
        for k in sorted(self.__matrices.keys()):
            s += "%s\n%s\n" % (k, self.__matrices[k])
        return s

class CameraMatrix:

    def __init__(self, filePath):
        self.__filePath = filePath
        self.__parse()
        
    def GetMatrixList(self): return self.__matrix
    
    def __parse(self):
        self.__matrix = []
        f = open(self.__filePath, "r")
        sent = f.readline().strip()
        if (sent!="CONTOUR"): raise Exception("Invalid Camera Matrix file: " + self.__filePath)
        l = f.readline()
        while (l!=""):
            self.__matrix.append([float(x) for x in l.split(" ")])
            l = f.readline()
        f.close()
        
    def __str__(self):
        s = ""
        for x in self.__matrix:
            s += str(x) + "\n"
        return s
                       
        
    

        
