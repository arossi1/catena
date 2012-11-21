# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing details.
import Common
import os


def Process(keylist, matchesFile="", forceRun=False):
    # note, must chdir to image directory
    
    if (len(matchesFile)==0):
        matchesFile = keylist + ".matches.init.txt"

    if (not os.path.exists(matchesFile) or 
        Common.Utility.GetFileSize(matchesFile)==0 or
        forceRun):
        cmd = "\"%s\" \"%s\" \"%s\"" % \
        (Common.Utility.GetAbsoluteFilePath(__file__, Common.ExecutablePath.EXE_KeyMatchFull), 
         keylist, matchesFile)
        Common.Utility.RunCommand(cmd, cwd=os.path.split(keylist)[0])
        
    return matchesFile


