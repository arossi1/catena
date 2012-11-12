# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing for details.

import os

class PsetFile:

    def __init__(self, filePath):
        self.__filePath = filePath
        self.__parse()
    
    def __parse(self):
        pass
    #TODO see: http://paulbourke.net/dataformats/ply/
#        self.__matrix = []
#        f = open(self.__filePath, "r")
#        sent = f.readline().strip()
#        if (sent!="CONTOUR"): raise Exception("Invalid Camera Matrix file")
#        l = f.readline()
#        while (l!=""):
#            self.__matrix.append([float(x) for x in l.split(" ")])
#            l = f.readline()
#        f.close()
        
    def __str__(self):
        s = ""
        # TODO
        return s
                       
        
    

        
