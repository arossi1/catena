# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing details.

import os, string

class PlyFile:
    
    VERSION = "1.0"
    
    def __init__(self, filePath):
        self.__filePath = filePath
        self.__parsed = False
        
    def __checkParse(self):
        if (not self.__parsed):
            self.__parse()
            self.__parsed = True
    
    @staticmethod
    def readLine(f):
        s = f.readline().strip()
        cs = s.find("{")
        if (cs>=0): s = s[:cs]
        return s
    
    @staticmethod
    def toString(v): return str(v)
    @staticmethod
    def toInteger(v): return int(v)
    @staticmethod
    def toFloat(v): return float(v)
    
    @staticmethod
    def getConvFunctor(t):
        if (t=="char"):     return PlyFile.toInteger
        elif (t=="uchar"):  return PlyFile.toInteger
        elif (t=="short"):  return PlyFile.toInteger
        elif (t=="ushort"): return PlyFile.toInteger
        elif (t=="int"):    return PlyFile.toInteger
        elif (t=="uint"):   return PlyFile.toInteger
        elif (t=="float"):  return PlyFile.toFloat
        elif (t=="double"): return PlyFile.toFloat
        else: raise Exception("Unknown type: " + t)
        
    
    def getElementNames(self):
        self.__checkParse()
        return [en for en,num,props in self.__elements]
    
    def getNumElements(self, elementName):
        self.__checkParse()
        for en,num,props in self.__elements:
            if (en==elementName): return num
        return 0
    
    def getPropertyNames(self, elementName):
        self.__checkParse()
        for en,num,props in self.__elements:
            if (en==elementName): return tuple([pn for dt,pn in props])
        return ()
    
    def getData(self, elementName, properties):
        self.__checkParse()
        elementIndex = -1
        elementProps = None
        for i,(en,num,props) in enumerate(self.__elements):
            if (en==elementName): 
                elementIndex = i
                elementProps = props
                
        if (elementIndex==-1): 
            raise Exception("Unknown element: " + elementName)
        
        propIndices = []
        for i,p in enumerate(elementProps):
            if (p[1] in properties):
                propIndices.append(i)
                
        data = []
        for d in self.__data[elementIndex]:
            data.append([d[i] for i in propIndices])
            
        return data
        
        
    def __parse(self):
        # see: http://paulbourke.net/dataformats/ply/
        
        self.__format = ""
        self.__version = ""
        self.__comments = []
        self.__elements = []
        self.__data = []
        
        f = open(self.__filePath, "r")
        
        # verify sentinel
        sent = PlyFile.readLine(f)
        if (sent!="ply"):
            f.close()
            raise Exception("Invalid PLY file")
        
        junk,self.__format,self.__version = PlyFile.readLine(f).split(" ")
        
        # check format
        if (self.__format!="ascii"):
            f.close()
            raise Exception("Only ascii PLY files supported")
        
        # check version
        if (self.__version!=PlyFile.VERSION):
            f.close()
            raise Exception("Unhandled PLY file version (%s), expected %s" % 
                            (self.__version,PlyFile.VERSION))
        
        # read header
        l = PlyFile.readLine(f)
        while (l!="end_header"):
            t = l.split(" ")
            if (t[0]=="element"):
                self.__elements.append((t[1],int(t[2]),[]))
            elif (t[0]=="property"):
                self.__elements[-1][2].append(tuple(t[1:3]))
            else:
                f.close()
                raise Exception("Unknown header string: " + l)
            l = PlyFile.readLine(f)
            
        # create conversion functors
        convFunctorsList = [[PlyFile.getConvFunctor(prop[0]) for prop in el[2]] for el in self.__elements]
        
        # parse data
        for iElement, element in enumerate(self.__elements):
            self.__data.append([[func(x) for func,x in zip(convFunctorsList[iElement], 
                                                           PlyFile.readLine(f).split(" "))] for i in range(element[1])])
        f.close()

    @staticmethod
    def getFormatString(t):
        if (t=="char"):     return "%d"
        elif (t=="uchar"):  return "%d"
        elif (t=="short"):  return "%d"
        elif (t=="ushort"): return "%d"
        elif (t=="int"):    return "%d"
        elif (t=="uint"):   return "%d"
        elif (t=="float"):  return "%e"
        elif (t=="double"): return "%e"
        else: raise Exception("Unknown type: " + t)
        
    @staticmethod
    def write(filePath, elementNames, propertyNames, propertyTypes, data):
        
        f = open(filePath,"w")
        f.write("ply\nformat ascii 1.0\n")

        formatStrings = []
        for i,eName in enumerate(elementNames):
            formatStrings.append([])
            f.write("element %s %d\n" % (eName,len(data[i])))
            for j,pName in enumerate(propertyNames[i]):
                f.write("property %s %s\n" % (propertyTypes[i][j],pName))
                formatStrings[-1].append(PlyFile.getFormatString(propertyTypes[i][j]))
        f.write("end_header\n")
        
        for i,elements in enumerate(data):
            formatString = string.join(formatStrings[i]) + "\n"
            for element in elements:                
                f.write(formatString % tuple(element))
        
        f.close()
        
        
    def __str__(self):
        s = ""
        # TODO
        return s
                       

if __name__=="__main__":

    # 3D list
    if (False):
        # create test data
        data = []
        for i in range(2):
            data.append([])
            for j in range(100):
                d = []
                for k in range(3):
                    d.append((i+1)*(j+1)*k)
                data[-1].append(d)
                
        PlyFile.write("test.ply", 
                      ("vertex1","vertex2"),
                      (("x","y","z"),( "xp","yp","zp")),
                      (("float","float","double"), ("float","float","float")),
                      data)
        
        ply = PlyFile(r"E:\Adam\Datasets\ETsub\pmvs\models\pmvs_options.txt.ply")
        for en in ply.getElementNames():
            print "%s, %d elements" % (en,ply.getNumElements(en))
            for pn in ply.getPropertyNames(en):
                print "  %s" % pn
            
        
        print ply.getData("vertex", ("x","y"))

    # np.matrix, typical of a column vector representation
    if (True):
        import numpy
        data = numpy.random.uniform(size=(3,100)) # each column is a 3D point

        # tack on color triplet
        data = numpy.concatenate((data, numpy.ones((3,100))*200))

        # write ply file
        PlyFile.write("test.ply", 
                      ["vertex"],
                      [("x","y","z", "diffuse_red","diffuse_green","diffuse_blue")],
                      [("float","float","float", "uchar","uchar","uchar")],
                      [data.T]) # need to transpose matrix because PlyFile expects row-major order

        
        
            
