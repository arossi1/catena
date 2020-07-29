# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing details.
from .. import Common, Chain, BundleAdjustment, Cluster
import os, sys, multiprocessing

class PMVS(Chain.StageBase):
    
    PMVS_MAP = {"Target Images"                 :"timages",
                "Other Images"                  :"oimages",
                "Image Pyramid Level"           :"level",
                "Cell Size"                     :"csize",
                "Patch Threshold"               :"threshold",
                "Sample Window Size"            :"wsize",
                "Minimum Image Number"          :"minImageNum",
                "CPUs"                          :"CPU",
                "Use Visualize Data"            :"useVisData",
                "Maximum Image Sequence"        :"sequence",
                "Spurious 3D Point Threshold"   :"quad",
                "Maximum Camera Angle Threshold":"maxAngle"}
    
        
    def __init__(self, inputStages=None,
                 timages="",
                 oimages=-3,
                 level=1,
                 csize=2,
                 threshold=0.7,
                 wsize=7,
                 minImageNum=3,
                 cpus=multiprocessing.cpu_count(),
                 useVisData=1,
                 sequence=-1,
                 quad=2.5,
                 maxAngle=10,
                 forceRun=False):
        Chain.StageBase.__init__(self,
                                 inputStages,
                                 "Runs PMVS",
                                 {"Target Images"                   :"The software tries to reconstruct 3D points until image projections " + 
                                    "of these points cover all the target images (only foreground pixels if segmentation masks are given) " + 
                                    "specified in this field (also see an explanation for the parameter csize). There are 2 ways to specify " +
                                    "such images.  Enumeration: a positive integer representing the number of target images, followed by actual image indexes. " +
                                    "Note that an image index starts from 0. For example, '5  1 3 5 7 9' means that there are 5 target images, and " + 
                                    "their indexes are '1 3 5 7 9'.  Range specification: there should be three numbers. The first number must be " + 
                                    "'-1' to distinguish itself from enumeration, and the remaining 2 numbers (a, b) specify the range of image " +
                                    "indexes [a, b). For example, '-1  0 6' means that target images are '0, 1, 2, 3, 4 and 5'. Note that '6' is " + 
                                    "not included.",
                                  "Other Images"                    :"Specifies image indexes that are used for reconstruction. However, the " +
                                    "difference from timages is that the software keeps reconstructing points until they cover all timages, but " + 
                                    "not oimages. In other words, oimages are simply used to improve accuracy of reconstructions, but not to check " + 
                                    "the completeness of reconstructions. There are two ways to specify oimages, which are the same as timages.",
                                  "Image Pyramid Level"             :"The software internally builds an image pyramid, and this parameter specifies " + 
                                    "the level in the image pyramid that is used for the computation. When level is 0, original (full) resolution " + 
                                    "images are used. When level is 1, images are halved (or 4 times less pixels). When level is 2, images are 4 " +
                                    "times smaller (or 16 times less pixels). In general, level = 1 is suggested, because cameras typically do not " + 
                                    "have r,g,b sensors for each pixel (bayer pattern). Note that increasing the value of level significantly speeds-up " + 
                                    "the whole computation, while reconstructions become significantly sparse.",
                                  "Cell Size"                       :"Controls the density of reconstructions. The software tries to reconstruct at least " + 
                                    "one patch in every csize x csize pixel square region in all the target images specified by timages. Therefore, " + 
                                    "increasing the value of csize leads to sparser reconstructions. Note that if a segmentation mask is specified " + 
                                    "for a target image, the software tries to reconstruct only foreground pixels in that image instead of the whole.",
                                  "Patch Threshold"                 :"A patch reconstruction is accepted as a success and kept, if its associated " + 
                                    "photometric consistency measure is above this threshold. Normalized cross correlation is used as a photometric " + 
                                    "consistency measure, whose value ranges from -1 (bad) to 1 (good). The software repeats three iterations of the " + 
                                    "reconstruction pipeline, and this threshold is relaxed (decreased) by 0.05 at the end of each iteration. For " + 
                                    "example, if you specify threshold=0.7, the values of the threshold are 0.7, 0.65, and 0.6 for the three iterations " + 
                                    "of the pipeline, respectively.",
                                  "Sample Window Size"              :"The software samples wsize x wsize pixel colors from each image to compute " + 
                                    "photometric consistency score. For example, when wsize=7, 7x7=49 pixel colors are sampled in each image. " + 
                                    "Increasing the value leads to more stable reconstructions, but the program becomes slower.",
                                  "Minimum Image Number"            :"Each 3D point must be visible in at least minImageNum images for being reconstructed. " + 
                                    "3 is suggested in general. The software works fairly well with minImageNum=2, but you may get false 3D points where " + 
                                    "there are only weak texture information. On the other hand, if your images do not have good textures, you may want to " + 
                                    "increase this value to 4 or 5.",
                                  "CPUs"                            :"Number of CPUs to utilize.",
                                  "Use Visualize Data"              :"Whether to use the visualize data.",
                                  "Maximum Image Sequence"          :"Sometimes, images are given in a sequence, in which case, you can enforce the software " + 
                                    "to use only images with similar indexes to reconstruct a point. sequence gives an upper bound on the difference of " + 
                                    "images indexes that are used in the reconstruction. More concretely, if sequence=3, image 5 can be used with " + 
                                    "images 2, 3, 4, 6, 7 and 8 to reconstruct points.",
                                  "Spurious 3D Point Threshold"     :"The software removes spurious 3D points by looking at its spatial consistency. In other " + 
                                    "words, if 3D oriented points agree with many of its neighboring 3D points, the point is less likely to be filtered out. " + 
                                    "You can control the threshold for this filtering step with quad. Increasing the threshold is equivalent with loosing the " + 
                                    "threshold and allows more noisy reconstructions. Typically, there is no need to tune this parameter.",
                                  "Maximum Camera Angle Threshold"  :"Stereo algorithms require certain amount of baseline for accurate 3D reconstructions. " + 
                                    "We measure baseline by angles between directions of visible cameras from each 3D point. More concretely, a 3D point is " + 
                                    "not reconstructed if the maximum angle between directions of 2 visible cameras is below this threshold. The unit is " + 
                                    "in degrees. Decreasing this threshold allows more reconstructions for scenes far from cameras, but results tend to " + 
                                    "be pretty noisy at such places.",
                                  "Force Run":"Force run if outputs already exist"})
        
        self._properties["Target Images"] = timages
        self._properties["Other Images"] = oimages
        self._properties["Image Pyramid Level"] = level
        self._properties["Cell Size"] = csize
        self._properties["Patch Threshold"] = threshold
        self._properties["Sample Window Size"] = wsize
        self._properties["Minimum Image Number"] = minImageNum
        self._properties["CPUs"] = cpus
        self._properties["Use Visualize Data"] = useVisData
        self._properties["Maximum Image Sequence"] = sequence
        self._properties["Spurious 3D Point Threshold"] = quad
        self._properties["Maximum Camera Angle Threshold"] = maxAngle
        self._properties["Force Run"] = forceRun
                 

    def GetInputInterface(self):
        return {"bundleFile":(0,BundleAdjustment.BundleFile),
                "images":(0,Common.sfmImages)}
    
    def GetOutputInterface(self):
        return {"model":Cluster.PlyFile,
                "patch":Cluster.PatchFile,
                "pset":Cluster.PsetFile}
                
        
    def WriteOptionsFile(self, outputPath, numImages):
        
        f = open(outputPath,"w")
        
        # standard options
        f.write("setEdge 0\n")
        f.write("useBound 0\n")
        if (self._properties["Target Images"]==""):
            f.write("timages -1 0 %d\n" % numImages)
            
        
        # options based on stage properties
        for propName in list(self._properties.keys()):
            if (propName=="Force Run"):continue
            
            if (self._properties[propName] != None):
                
                if (isinstance(self._properties[propName],bool)):
                    if (self._properties[propName] == True):
                        f.write("%s\n" % PMVS.PMVS_MAP[propName])
                
                elif (isinstance(self._properties[propName],int)   or
                      isinstance(self._properties[propName],float) or
                      isinstance(self._properties[propName],str)):
                    
                    if ((isinstance(self._properties[propName],int) and self._properties[propName]!=Common.Utility.InvalidInt())  or
                        (isinstance(self._properties[propName],float) and self._properties[propName]!=Common.Utility.InvalidFloat()) or
                        (isinstance(self._properties[propName],str) and self._properties[propName]!=Common.Utility.InvalidString())):
                        f.write("%s %s\n" % (PMVS.PMVS_MAP[propName], str(self._properties[propName])))
                    
                else:
                    raise Exception("Unhandled property %s: %s" % \
                                    (propName, str(type(self._properties[propName]))))
        f.close()
        
    
    def Execute(self):
        bundleFile = self.GetInputStageValue(0, "bundleFile")
        images = self.GetInputStageValue(0, "images")
        
        self.StartProcess()
        
        numImages = len(images.GetImages())
        pmvsPath = os.path.split(bundleFile.GetBundleFilePath())[0]
        optionsFileName = "pmvs_options.txt"
        
        optionsFilePath = os.path.join(pmvsPath, optionsFileName)
        modelFile = os.path.join(pmvsPath, "models", optionsFileName+".ply")
        patchFile = os.path.join(pmvsPath, "models", optionsFileName+".patch")
        psetFile = os.path.join(pmvsPath, "models", optionsFileName+".pset")
        
        if (Common.Utility.ShouldRun(self._properties["Force Run"],
                                     optionsFilePath,modelFile,patchFile,psetFile)):

            self.WriteOptionsFile(optionsFilePath, numImages)
        
            self.RunCommand("pmvs2", 
                            Common.Utility.CommandArgs("\"%s/\"" % pmvsPath,
                                                       optionsFileName))
        
        
        self.SetOutputValue("model", Cluster.PlyFile(modelFile))
        self.SetOutputValue("patch", Cluster.PatchFile(patchFile))
        self.SetOutputValue("pset", Cluster.PsetFile(psetFile))

