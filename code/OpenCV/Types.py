# Copyright (c) 2014, Adam J. Rossi. All rights reserved. See README for licensing details.
import copy, string, os
import numpy

from .. import FeatureExtraction

class ImagesFeatures(FeatureExtraction.KeypointDescriptors):
    
    def __init__(self, path=""):
        FeatureExtraction.KeypointDescriptors.__init__(self,
                                                       path=path, 
                                                       kdList=[], 
                                                       genKeylist=False)
        self.__keypointDescriptors = []
        
    def append(self, v): self.__keypointDescriptors.append(v)
    def GetDescriptors(self): return self.__keypointDescriptors
            

class ImageFeatures:
    
    def __init__(self, imagePath):
        self.__imagePath = imagePath
        self.__features = []
        self.__descriptorLength = 0
        
    def append(self, v): self.__features.append(v)
    
    def GetImagePath(self): return self.__imagePath
    def GetFilePath(self): return os.path.splitext(self.__imagePath)[0]+".key"
    def GetFileName(self): return os.path.split(self.GetFilePath())[1]
    
    def Serialize(self, filePath, dt):
        
        dfmt = "%d"
        if (dt==float):dfmt="%f"
        
        f = open(filePath,"w")
        f.write("%d %d\n" % (len(self.__features),self.__descriptorLength))
        for feature in self.__features:
            
#             f.write("%f %f %d %f %f %f\n" % (feature.Row(), 
#                                              feature.Column(), 
#                                              feature.Scale(), 
#                                              feature.Orientation(),
#                                              feature.Response(), 
#                                              feature.NeighborhoodDiameter()))

            f.write("%f %f %d %f\n" % (feature.Row(), 
                                       feature.Column(), 
                                       feature.Scale(), 
                                       feature.Orientation()))
            
            idx = 0
            dLength = len(feature.Descriptor())
            while (idx<dLength):
                numVals = min(20,dLength-idx)
                
                f.write((string.join([dfmt]*numVals," ")+"\n") % \
                        tuple(feature.Descriptor()[idx:idx+numVals]))
                
                idx+=numVals
        f.close()
        
        
    @staticmethod
    def FromFile(filePath, imagePath, offsetX=0,offsetY=0,dt=int):
        
        import cv2
        
        ifs = ImageFeatures(imagePath)
        
        f = open(filePath, "r")

        # parse data into list of strings
        data = []
        for l in f.readlines():
            data += l.strip().split(" ")
        f.close()

        idx = 0
        # get # keypoints and descriptor length
        numKeypointDescriptors = int(data[idx]); idx+=1
        ifs.__descriptorLength = int(data[idx]); idx+=1

        # read descriptors
        for i in range(numKeypointDescriptors):
#             row, column, scale, orientation, response, neighborhoodDiameter = data[idx:idx+6]
#             idx+=6
            
            row, column, scale, orientation = data[idx:idx+4]
            response=0;neighborhoodDiameter=0
            idx+=4
            
            vector = [dt(x) for x in data[idx:idx+ifs.__descriptorLength]]
            idx+=ifs.__descriptorLength
            feature = Feature(cv2.KeyPoint(float(column),float(row),float(neighborhoodDiameter),
                                           float(orientation),float(response),int(scale)),
                              tuple(vector))
            ifs.append(feature)
        
        return ifs
        
    @staticmethod
    def FromOCVFeatures(imagePath, keypoints, descriptors):
        
        ifs = ImageFeatures(imagePath)
        ifs.__descriptorLength = 0
        
        for i,descriptor in enumerate(descriptors):
            
            if (ifs.__descriptorLength==0):
                ifs.__descriptorLength = len(descriptor)
            elif (len(descriptor)!=ifs.__descriptorLength):
                raise Exception("Inconsistent descriptor vector length")            
                
            ifs.append(Feature(keypoints[i], tuple(descriptor)))

        return ifs
        
    def GetDescriptorsArray(self, dtype=None):
        d = [f.Descriptor() for f in self.__features]
        if (dtype): return numpy.array(d,dtype)
        else:       return numpy.array(d)
        
    def GetDescriptors(self): return self.__features


class Feature:
    def __init__(self, keypoint, descriptor):
        self.__keypoint = keypoint
        self.__descriptor = descriptor
        
    def Row(self): return self.__keypoint.pt[1]
    def Column(self): return self.__keypoint.pt[0]
    def Scale(self): return self.__keypoint.octave
    def Orientation(self): return self.__keypoint.angle
    def Response(self): return self.__keypoint.response
    def NeighborhoodDiameter(self): return self.__keypoint.size
    def Vector(self): return self.__descriptor
    def Descriptor(self): return self.__descriptor

