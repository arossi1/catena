# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing details.
from PlyFile import PlyFile
import os

class ClusterEntry:
    
    def __init__(self, id, numImagesCluster, clusterImageIndices, path):
        self.__id = id
        self.__numImagesCluster = numImagesCluster
        self.__clusterImageIndices = clusterImageIndices
        self.__parseCameraCenterFile(path)
        
    def GetID(self): return self.__id
    def GetNumImagesCluster(self): return self.__numImagesCluster
    def GetClusterImageIndices(self): return self.__clusterImageIndices
    def GetCameraCenterPlyFile(self): return self.__cameraCenterFile
    
    def __parseCameraCenterFile(self, path):
        self.__cameraCenterFile = PlyFile(os.path.join(path, "centers-%04d.ply" % self.__id))
        
    def __str__(self):
        return "Cluster Index: %d\nImages in cluster: %d\nCluster indices: %s" % \
            (self.__id, self.__numImagesCluster, str(self.__clusterImageIndices))

class ClusterFile:

    def __init__(self, filePath):
        self.__filePath = filePath
        self.__parse()
        
    def GetEntries(self): return self.__entries
    
    def __parse(self):
        self.__entries = []
        f = open(self.__filePath, "r")
        sent = f.readline().strip()
        if (sent!="SKE"): raise Exception("Invalid Cluster file")
        numImagesDataset, numClusters  = [int(i) for i in f.readline().strip().split(" ")]
                
        for iCluster in range(numClusters):
            numImagesCluster, zero  = [int(i) for i in f.readline().strip().split(" ")]
            if (numImagesCluster>0):
                clusterImageIndices = tuple([int(i) for i in f.readline().strip().split(" ")])
            else:
                clusterImageIndices = ()
            self.__entries.append( ClusterEntry(iCluster, 
                                                numImagesCluster, 
                                                clusterImageIndices, 
                                                os.path.split(self.__filePath)[0]) )
        f.close()
        
    def __str__(self):
        s = ""
        for e in self.__entries:
            s += str(e) + "\n"
        return s
                       

        
