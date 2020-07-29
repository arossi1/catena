# Copyright (c) 2014, Adam J. Rossi. All rights reserved. See README for licensing details.
from .. import Chain, Common
from . import Types
import os, string
import cv2
import numpy
import numpy.numarray

class FeatureDetector(Chain.StageBase):

    #GENERATE DETECTOR LIST AND INPUT DATA
    DETECTORS = ("FAST","STAR","SIFT","SURF","ORB","BRISK","MSER","GFTT","HARRIS","Dense","SimpleBlob")
    DETECTOR_ADAPTERS = ("","Grid")  # these don't work: "Pyramid"    
    FEATURE_DETECTORS = tuple([str(a)+str(d) for a in DETECTOR_ADAPTERS for d in DETECTORS])

    #GENERATE DESCRIPTOR LIST AND INPUT DATA
    DESCRIPTORS = ("SIFT","SURF","ORB","BRISK","BRIEF")
    DESCRIPTOR_ADAPTERS = ("")  # these don't work: "Opponent"
    FEATURE_DESCRIPTORS = DESCRIPTORS
    # FEATURE_DESCRIPTORS = tuple([str(a)+str(d) for a in DESCRIPTOR_ADAPTERS for d in DESCRIPTORS])
    DESCRIPTORS_DATATYPES = {"SIFT":int,"SURF":float,"ORB":int,"BRISK":int,"BRIEF":int}
    
    def __init__(self, 
                 inputStages=None,
                 detector="SIFT",
                 descriptor="SIFT",
                 forceRun=False):
        Chain.StageBase.__init__(self,
                                 inputStages,
                                 "Generates features for images",
                                 {"Detector":"Detector type {"+string.join(FeatureDetector.FEATURE_DETECTORS,", ")+"}",
                                  "Descriptor": 'Descriptor type{'+string.join(FeatureDetector.FEATURE_DESCRIPTORS,", ")+'}',
                                  "Force Run":"Force run if outputs already exist"})
        
        self.__setStageProperties({"Detector":detector,
                                   "Descriptor":descriptor,
                                   "Force Run":forceRun})        
        self.__resetStageProperties()

    def GetInputInterface(self):
        return {"images":(0,Common.sfmImages)}
    
    def GetOutputInterface(self):
        return {"keypointDescriptors":Types.ImagesFeatures}
    
    def SetProperty(self, name, val):
        Chain.StageBase.SetProperty(self, name, val)
        if (name=="Detector" or name=="Descriptor"):
            self.__resetStageProperties()
    
    def __resetStageProperties(self):
        stageProps = self.__getStageProperties()
        self._properties = {}
        self.__ocvPropertyType = {}
        self.__intializeOCVProperties(
            cv2.FeatureDetector_create(stageProps["Detector"]), "Detector")
        self.__intializeOCVProperties(
            cv2.DescriptorExtractor_create(stageProps["Descriptor"]), "Descriptor")
        self.__setStageProperties(stageProps)
    
    def __getStageProperties(self):
        props = {}
        for k in ("Detector","Descriptor","Force Run"):
            props[k] = self._properties[k]
        return props
    
    def __setStageProperties(self, props):
        for k in props.keys():
            self._properties[k] = props[k]

    def __intializeOCVProperties(self, d, label):   
        for p in d.getParams():
            if (p=="detector"):continue
            propName = label+":"+p
            if (d.paramType(p) in [0,8,11]):
                self._properties[propName] = d.getInt(p)
                self.SetPropertyDescription(propName, "Int")
                self.__ocvPropertyType[propName] = "Int"
            elif d.paramType(p) == 1:
                self._properties[propName] = d.getBool(p)
                self.SetPropertyDescription(propName, "Bool")
                self.__ocvPropertyType[propName] = "Bool"
            elif (d.paramType(p) in [2,7]):
                self._properties[propName] = d.getDouble(p)
                self.SetPropertyDescription(propName, "Double")
                self.__ocvPropertyType[propName] = "Double"
            elif d.paramType(p) == 6:
                self._properties[propName] = d.getAlgorithm(p)
                self.SetPropertyDescription(propName, "Algorithm")
                self.__ocvPropertyType[propName] = "Algorithm"
            else:
                raise Exception("Unknown property type: %s,%s,%d" % (f,p,detect.paramType(p)))
            
    def __setOCVProperties(self, d, label):
        for k in self._properties.keys():
            if (k.startswith(label+":")):
                propName = k[len(label)+1:]
                if (self.__ocvPropertyType[k]=="Int"):
                    d.setInt(propName, self._properties[k])
                elif (self.__ocvPropertyType[k]=="Bool"):
                    d.setBool(propName, self._properties[k])
                elif (self.__ocvPropertyType[k]=="Double"):
                    d.setDouble(propName, self._properties[k])
                elif (self.__ocvPropertyType[k]=="Algorithm"):
                    d.setAlgorithm(propName, self._properties[k])
                else:
                    raise Exception("Unknown property type: " + k)

    def Execute(self):
        images = self.GetInputStageValue(0, "images")
        
        self.StartProcess()
        
        isfs = Types.ImagesFeatures(images.GetPath())
        
        for im in images.GetImages():
            
            keyFile = os.path.join(os.path.splitext(im.GetFilePath())[0]+".key")
            
            if (Common.Utility.ShouldRun(self._properties["Force Run"], keyFile)):
                
                bands = cv2.imread(im.GetFilePath()).shape[2]
                if (bands==1):
                    cvim = cv2.imread(im.GetFilePath(), cv2.CV_LOAD_IMAGE_GRAYSCALE)
                elif (bands==3):
                    cvim = cv2.imread(im.GetFilePath(), cv2.CV_LOAD_IMAGE_COLOR)
                    cvim = cv2.cvtColor(cvim, cv2.COLOR_RGB2GRAY)
                else:
                    raise Exception("Unhandled number of bands (%d) for image: %s"%(bands,im.GetFilePath()))
                
                d = cv2.FeatureDetector_create(self._properties["Detector"])
                self.__setOCVProperties(d, "Detector")
                de = cv2.DescriptorExtractor_create(self._properties["Descriptor"])
                self.__setOCVProperties(de, "Descriptor")
                
                keypoints = d.detect(cvim)
                keypoints, descriptors = de.compute(cvim,keypoints)
                ifs = Types.ImageFeatures.FromOCVFeatures(im.GetFilePath(),
                                                          keypoints,descriptors)
                ifs.Serialize(keyFile, 
                    FeatureDetector.DESCRIPTORS_DATATYPES[self._properties["Descriptor"]])
            else:
                ifs = Types.ImageFeatures.FromFile(keyFile, im.GetFilePath(),
                    dt=FeatureDetector.DESCRIPTORS_DATATYPES[self._properties["Descriptor"]])
            
            Chain.Analyze.WriteStatus("[%s] Features: %d" % \
                                      (im.GetFileName(), len(ifs.GetDescriptors())))
            
            isfs.append(ifs)
            
        isfs.GenerateKeyList()
            
        self.SetOutputValue("keypointDescriptors", isfs)

