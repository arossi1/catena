# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing details.
import Common
import os
from SiftWin32KeypointDescriptorFile import SiftWin32KeypointDescriptorFile




def Process(imagePath, keypointDescriptorFile="", parseKDF=True, forceRun=False):
    
    if (len(keypointDescriptorFile)==0):
        keypointDescriptorFile = os.path.join(os.path.splitext(imagePath)[0]+".key")

    if (not os.path.exists(keypointDescriptorFile) or
        Common.Utility.GetFileSize(keypointDescriptorFile)==0 or
        forceRun):
        
        Common.Utility.RunCommand("\"%s\" \"%s\" \"%s\"" % \
                                  (Common.Utility.GetAbsoluteFilePath(__file__, Common.ExecutablePath.EXE_SiftGPU),
                                  imagePath, keypointDescriptorFile))
    
    return SiftWin32KeypointDescriptorFile(keypointDescriptorFile, parseKDF)
