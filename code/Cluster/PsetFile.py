# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing details.

import os

class Point3D:
    def __init__(self, x,y,z, xn,yn,zn):
        self.__x = x
        self.__y = y
        self.__z = z
        self.__xn = xn
        self.__yn = yn
        self.__zn = zn

    def X(self): return self.__x
    def Y(self): return self.__y
    def Z(self): return self.__z
    def Xn(self): return self.__xn
    def Yn(self): return self.__yn
    def Zn(self): return self.__zn

    def __str__(self):
        return "(%f,%f,%f) [normal=(%f,%f,%f)]" % \
            (self.__x,self.__y,self.__z,self.__xn,self.__yn,self.__zn)
        
class PsetFile:

    def __init__(self, filePath):
        self.__filePath = filePath
        self.__parsed = False
        self.__points = []
        
    def __checkParse(self):
        if (not self.__parsed):
            self.__parse()
            self.__parsed = True

    def Points(self):
        self.__checkParse()
        return self.__points
    
    def __parse(self):
        f = open(self.__filePath, "r")
        for l in f.readlines():
            v = [float(x) for x in l.split(" ")]
            if (len(v)==6):
                self.__points.append(Point3D(v[0],v[1],v[2],v[3],v[4],v[5]))
        f.close()                      
        
    def __str__(self):
        self.__checkParse()
        s = ""
        for pt in self.__points:
            s += str(pt) + "\n"
        return s

        
