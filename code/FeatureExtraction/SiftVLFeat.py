# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing details.
import Common
import os
from SiftVLFeatKeypointDescriptorFile import SiftVLFeatKeypointDescriptorFile


def Process(imagePath, keypointDescriptorFile="", parseKDF=True, forceRun=False):
    
    if (len(keypointDescriptorFile)==0):
        keypointDescriptorFile = os.path.join(os.path.splitext(imagePath)[0]+".key")

    if (not os.path.exists(keypointDescriptorFile) or
        Common.Utility.GetFileSize(keypointDescriptorFile)==0 or
        forceRun):
        
        Common.Utility.RunCommand("\"%s\" --orientations \"%s\" -o \"%s\"" % \
                                  (Common.Utility.GetAbsoluteFilePath(__file__, Common.ExecutablePath.EXE_SiftVLFeat),
                                  imagePath, keypointDescriptorFile))
        
    return SiftVLFeatKeypointDescriptorFile(keypointDescriptorFile, parseKDF)
