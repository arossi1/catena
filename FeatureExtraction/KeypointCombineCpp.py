# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing for details.
import PackagePath, ExecutablePath
import Utility
import os



def Process(tileListPath):
    
    #if (not os.path.exists(keypointDescriptorFile)):
    Utility.RunCommand("\"%s\" \"%s\"" % (Utility.GetAbsoluteFilePath(__file__, ExecutablePath.EXE_KeypointCombine), tileListPath),
                       cwd=os.path.split(tileListPath)[0], shell=True)
        
    #return SiftVLFeatKeypointDescriptorFile(keypointDescriptorFile, parseKDF)
