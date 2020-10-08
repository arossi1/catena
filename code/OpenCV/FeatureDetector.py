# Copyright (c) 2014, Adam J. Rossi. All rights reserved. See README for licensing details.
from .. import Chain, Common
from . import Types
from itertools import product
import os
import cv2


class FeatureDetector(Chain.StageBase):

    #GENERATE DETECTOR LIST AND INPUT DATA
    DETECTORS = ("Fast","Star","SIFT","SURF","ORB","BRISK","MSER","GFTT","Harris","SimpleBlob","Agast","AKAZE","KAZE","MSD")
    DETECTOR_ADAPTERS = ("","Grid")  # these don't work: "Pyramid"
    FEATURE_DETECTORS = tuple([a+d for a,d in product(DETECTOR_ADAPTERS, DETECTORS)])

    #GENERATE DESCRIPTOR LIST AND INPUT DATA
    DESCRIPTORS = ("BoostDesc","Brief","DAISY","FREAK","LATCH","LUCID","VGG")
    DESCRIPTOR_ADAPTERS = ("")  # these don't work: "Opponent"
    FEATURE_DESCRIPTORS = DESCRIPTORS
    # FEATURE_DESCRIPTORS = tuple([str(a)+str(d) for a in DESCRIPTOR_ADAPTERS for d in DESCRIPTORS])
    DESCRIPTORS_DATATYPES = {"SIFT": float,"SURF": float,"ORB": int,"BRISK": int,"AKAZE": int,"KAZE": float,
                             "BoostDesc": int,"Brief": int,"DAISY": float,"FREAK": int,"LATCH": int,"LUCID": int,"VGG": float}

    def __init__(self,
                 inputStages=None,
                 detector="SIFT",
                 descriptor="SIFT",
                 forceRun=False):
        Chain.StageBase.__init__(self,
                                 inputStages,
                                 "Generates features for images",
                                 {"Detector":"Detector type {"+", ".join(FeatureDetector.FEATURE_DETECTORS)+"}",
                                  "Descriptor": 'Descriptor type{'+", ".join(FeatureDetector.FEATURE_DESCRIPTORS)+'}',
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
        self.__ocvProperties = {}
        self.__intializeOCVProperties(stageProps["Detector"], "Detector")
        self.__intializeOCVProperties(stageProps["Descriptor"], "Descriptor")
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
        if d == 'Agast':
            props = dict(threshold=10, nonmaxSuppression=True, type=cv2.AGAST_FEATURE_DETECTOR_OAST_9_16)
        elif d == "AKAZE":
            props = dict(descriptor_type=cv2.AKAZE_DESCRIPTOR_MLDB, descriptor_size=0, descriptor_channels=3,
                         threshold=0.001, nOctaves=4, nOctaveLayers=4, diffusity=cv2.KAZE_DIFF_PM_G2)
        elif d == "BRISK":
             props = dict(thresh=30, octaves=3, patternScale=1.0)
        elif d == "Fast":
            props = dict(threshold=10, nonmaxSuppression=True, type=cv2.FAST_FEATURE_DETECTOR_TYPE_9_16)
        elif d == "GFTT":
            props = dict(maxCorners=1000, qualityLevel=0.01, minDistance=1,
                         blockSize=3, useHarrisDetector=False, k=0.04)
        elif d == "KAZE":
            props = dict(extended=False, upright=False, threshold=0.001,
                         nOctaves=4, nOctaveLayers=4, diffusivity=cv2.KAZE_DIFF_PM_G2)
        elif d == "MSER":
            props = dict(_delta=5, _min_area=60, _max_area=14400, _max_variation=0.25,
                         _min_diversity=.2, _max_evolution=200, _area_threshold=1.01,
                         _min_margin=0.003, _edge_blur_size=5)
        elif d == "ORB":
            props = dict(nfeatures=500, scaleFactor=1.2, nlevels=8,
                         edgeThreshold=31, firstLevel=0, WTA_K=2,
                         scoreType=cv2.ORB_HARRIS_SCORE, patchSize=31, fastThreshold=20)
        elif d == "SIFT":
            props = dict(nfeatures=0, nOctaveLayers=3, contrastThreshold=0.04,
                         edgeThreshold=10, sigma=1.6)
        elif d == "SimpleBlob":
            params = cv2.SimpleBlobDetector_Params()
            props= dict()
            for attr in dir(params):
                if attr.startswith("__"): continue
                props[attr] = getattr(params, attr)
        elif d == "Harris":
            props = dict(numOctaves=6, corn_thresh=0.01, DOG_thresh=0.01,
                         maxCorners=5000, num_layers=4)
        elif d == "MSD":
            props = dict(m_patch_radius=3, m_search_area_radius=5, m_nms_radius=5,
                         m_nms_scale_radius=0, m_th_saliency=250.0, m_kNN=4,
                         m_scale_factor=1.25, m_n_scales=-1, m_compute_orientation=False)
        elif d == "Star":
            props = dict(maxSize=45, responseThreshold=30, lineThresholdProjected=10,
                         lineThresholdBinarized=8, suppressNonmaxSize=5)
        elif d == "SURF":
            props = dict(hessianThreshold=100, nOctaves=4, nOctaveLayers=3,
                         extended=False, upright=False)
        elif d == "BoostDesc":
            props = dict(desc=302, use_scale_orientation=True, scale_factor=6.25)
        elif d == "Brief":
            props = dict(bytes=32, use_orientation=False)
        elif d == "DAISY":
            props = dict(radius=15, q_radius=3, q_theta=8, q_hist=8, norm=100,
                         H=None, interpolation=True, use_orientation=False)
        elif d == "FREAK":
            props = dict(orientationNormalized=True, scaleNormalized=True,
                         patternScale=22.0, nOctaves=4, selectedPairs=None)
        elif d == "LATCH":
            props = dict(bytes=32, rotationInvariance=True, half_ssd_size=3, sigma=2.0)
        elif d == "LUCID":
            props = dict(lucid_kernel=1, blur_kernel=2)
        elif d == "VGG":
            props = dict(desc=100, isigma=1.4, img_normalize=True,
                         use_scale_orientation=True, scale_factor=6.25, dsc_normalize=False)
        else:
            raise Exception("Unknown feature detector | descriptor : {}".format(d))

        for p,v in props.items():
            propName = label+":"+p
            paramType = type(v).__name__
            self._properties[propName] = v
            self.SetPropertyDescription(propName, paramType)


    def __setOCVProperties(self, label):
        for k in self._properties.keys():
            if (k.startswith(label+":")):
                propName = k[len(label)+1:]
                self.__ocvProperties[propName] = self._properties[k]

    def __createFeatureDetector(self, d):
        self.__setOCVProperties("Detector")

        ocvProperties = self.__ocvProperties
        if d == "Agast":
            featureDetector = cv2.AgastFeatureDetector_create(**ocvProperties)
        elif d == "AKAZE":
            featureDetector = cv2.AKAZE_create(**ocvProperties)
        elif d == "BRISK":
            featureDetector = cv2.BRISK_create(**ocvProperties)
        elif d == "Fast":
            featureDetector = cv2.FastFeatureDetector_create(**ocvProperties)
        elif d == "GFTT":
            featureDetector = cv2.GFTTDetector_create(**ocvProperties)
        elif d == "KAZE":
            featureDetector = cv2.KAZE_create(**ocvProperties)
        elif  d == "MSER":
            featureDetector = cv2.MSER_create(**ocvProperties)
        elif d == "ORB":
            featureDetector = cv2.ORB_create(**ocvProperties)
        elif d == "SIFT":
            featureDetector = cv2.xfeatures2d.SIFT_create(**ocvProperties)
        elif d == "SimpleBlob":
            featureDetector = cv2.SimpleBlobDetector_create(**ocvProperties)
        elif d == "Harris":
            featureDetector = cv2.xfeatures2d.HarrisLaplaceFeatureDetector_create(**ocvProperties)
        elif d == "MSD":
            featureDetector = cv2.MSDDetector_create(**ocvProperties)
        elif d == "Star":
            featureDetector = cv2.xfeatures2d.StarDetector_create(**ocvProperties)
        elif d == "SURF":
            featureDetector = cv2.xfeatures2d.SURF_create(**ocvProperties)
        elif d == "SIFT":
            featureDetector = cv2.xfeatures2d.SIFT_create(**ocvProperties)
        else:
            raise Exception("Unknown feature detector: {}".format(d))
        return featureDetector

    def __createFeatureDescriptor(self, d):
        self.__setOCVProperties("Descriptor")

        ocvProperties = self.__ocvProperties
        if d == "BoostDesc":
            featureDescriptor = cv2.xfeatures2d.BoostDesc_create(**ocvProperties)
        elif d == "Brief":
            featureDescriptor = cv2.xfeatures2d.BriefDescriptorExtractor_create(**ocvProperties)
        elif d == "DAISY":
            featureDescriptor = cv2.xfeatures2d.DAISY_create(**ocvProperties)
        elif d == "FREAK":
            featureDescriptor = cv2.xfeatures2d.FREAK_create(**ocvProperties)
        elif d == "LATCH":
            featureDescriptor = cv2.xfeatures2d.LATCH_create(**ocvProperties)
        elif d == "LUCID":
            featureDescriptor = cv2.xfeatures2d.LUCID_create(**ocvProperties)
        elif d == "VGG":
            featureDescriptor = cv2.xfeatures2d.VGG_create(**ocvProperties)
        else:
            raise Exception("Unknown feature descriptor: {}".format(d))
        return featureDescriptor


    def Execute(self):
        images = self.GetInputStageValue(0, "images")

        self.StartProcess()

        isfs = Types.ImagesFeatures(images.GetPath())

        for im in images.GetImages():

            keyFile = os.path.join(os.path.splitext(im.GetFilePath())[0]+".key")

            
            if (Common.Utility.ShouldRun(self._properties["Force Run"], keyFile)):

                bands = cv2.imread(im.GetFilePath()).shape[2]
                if (bands==1):
                    cvim = cv2.imread(im.GetFilePath(), cv2.IMREAD_GRAYSCALE)
                elif (bands==3):
                    cvim = cv2.imread(im.GetFilePath(), cv2.IMREAD_COLOR)
                    cvim = cv2.cvtColor(cvim, cv2.COLOR_RGB2GRAY)
                else:
                    raise Exception("Unhandled number of bands (%d) for image: %s"%(bands,im.GetFilePath()))

                detector = self._properties["Detector"]
                descriptor = self._properties["Descriptor"]

                if descriptor == "AKAZE" and detector not in ["AKAZE","KAZE"]:
                    raise Exception("AKAZE descriptors can only be used with KAZE or AKAZE keypoints")

                d = self.__createFeatureDetector(self._properties["Detector"])
                
                # Constructors that create detector and descriptors
                if descriptor == detector and detector in ["AKAZE","BRISK","KAZE","SIFT","SURF","ORB"]:
                    # Provides better performance, when using detect followed by compute scale space pyramid is computed twice
                    keypoints, descriptors = d.detectAndCompute(cvim,None)
                else:
                    de = self.__createFeatureDescriptor(self._properties["Descriptor"])
                    # There are combinations that might not work together like LUCId descriptor only works with grayscale
                    keypoints = d.detect(cvim,None)
                    keypoints, descriptors = de.compute(cvim,keypoints)
                
                ifs = Types.ImageFeatures.FromOCVFeatures(im.GetFilePath(),
                                                                  keypoints,descriptors)
                ifs.Serialize(keyFile,
                    FeatureDetector.DESCRIPTORS_DATATYPES[descriptor])
            else:
                ifs = Types.ImageFeatures.FromFile(keyFile, im.GetFilePath(),
                    dt=FeatureDetector.DESCRIPTORS_DATATYPES[descriptor])

            Chain.Analyze.WriteStatus("[%s] Features: %d" % \
                                      (im.GetFileName(), len(ifs.GetDescriptors())))

            isfs.append(ifs)

        isfs.GenerateKeyList()

        self.SetOutputValue("keypointDescriptors", isfs)

