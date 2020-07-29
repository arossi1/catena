# Copyright (c) 2014, Adam J. Rossi. All rights reserved. See README for licensing details.
import sys, os, shutil
sys.path.append(os.path.abspath("."))
from .. import Chain, Common, Sources

#################################################################################
class CopyImages(Common.ImageProcessStageBase):

    def __init__(self,
                 inputStages=None,      # input stages (StageBase)
                 prefixName="",         # file name prefix (CopyImages)
                 outputPath="",         # output path (ImageProcessStageBase)
                 imageExtension="tif",  # image extension (ImageProcessStageBase)
                 forceRun=False,        # force run (ImageProcessStageBase)
                 enableStage=True):     # enable stage (ImageProcessStageBase)
            
            Common.ImageProcessStageBase.__init__(self,
                                                  inputStages,
                                                  outputPath,
                                                  imageExtension,
                                                  forceRun,
                                                  enableStage,
                                                  "Copies images",
                                                  {"Prefix Name":"Output file name prefix"})
            
            self._properties["Prefix Name"] = prefixName


    def GetOutputImagePath(self, inputImagePath):

        # construct the output image path, including the prefix name
        return os.path.join(self._properties["Output Image Path"],
                            self._properties["Prefix Name"] + 
                            os.path.splitext(os.path.basename(inputImagePath))[0] +
                            "."+self._properties["Image Extension"])
    
    def ProcessImage(self, inputImagePath, outputImagePath):

        # copy the input to output
        shutil.copy(inputImagePath, outputImagePath)


################################################################################
        
# input/output image path
imagePath = os.path.abspath("../Datasets/ET")
imagePathOut = os.path.join(imagePath, "test")
Common.Utility.MakeDir(imagePathOut)

imageSource = Sources.ImageSource(imagePath, "jpg")

imageCopy = CopyImages(imageSource, "test-", imagePathOut, "jpg")

print(Chain.Render(imageCopy))
