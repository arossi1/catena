# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing for details.
import Common
import string, os
from DaisyKeypointDescriptorFile import DaisyKeypointDescriptorFile

# normalization types
NORMALIZATION_PARTIAL = 0
NORMALIZATION_FULL = 1
NORMALIZATION_SIFT_LIKE = 2

def Process(image,
            roi=None,
            normalizationType=NORMALIZATION_SIFT_LIKE,
            diableInterpolation=False,
            writeASCIIDescriptorFile=False,
            keypointDescriptorFile="",
            parseKDF=True,
            randomSamples=False,
            numRandomSamples=100,
            scaleInvariant=True,
            rotationInvariant=True,
            orientationResolution=36,
            forceRun=False):

    # image
    pImage = "-i \"%s\"" % image
    
    # ROI
    pROI = ""
    if (roi!=None):
        pROI = "-xMin %d -yMin %d -width %d -height %d" % roi

    # normalization type
    pNT = "-nt %d" % normalizationType

    # disable interpolation
    pDisableInterpolation = ""
    if (diableInterpolation): pDisableInterpolation = "-di"

    # descriptor file
    if (len(keypointDescriptorFile)==0):
        basePath, fileName = os.path.split(image)
        baseName, extension = os.path.splitext(fileName)
        keypointDescriptorFile = os.path.join(basePath, "%s.daisy"%baseName)
    pDescriptorFile = "-dp \"%s\"" % keypointDescriptorFile
    keypointDescriptorFileScales = keypointDescriptorFile + ".scales"
    keypointDescriptorFileOrientation = keypointDescriptorFile + ".orientations"
    
    pRandomSamples = ""
    if (randomSamples): pRandomSamples = "-rs %d"%numRandomSamples
    
    pScaleInvariant = ""
    if (scaleInvariant): pScaleInvariant = "-si"
    
    pRotationInvariant = ""
    if (rotationInvariant): pRotationInvariant = "-ri %d" % orientationResolution

    # save type (ascii/binary), note: binary is much faster
    if (writeASCIIDescriptorFile): pSaveType = "-sa"
    else:                          pSaveType = "-sb"        

    cmd = string.join(["\""+Common.Utility.GetAbsoluteFilePath(__file__, Common.ExecutablePath.EXE_Daisy)+"\"",
                       pImage, pROI, pNT, pDisableInterpolation, pDescriptorFile, pSaveType, pRandomSamples, pScaleInvariant, pRotationInvariant], " ")
    
    if ((not(os.path.exists(keypointDescriptorFile) and
        os.path.exists(keypointDescriptorFileScales) and
        os.path.exists(keypointDescriptorFileOrientation))) or
        forceRun):
        
        Common.Utility.RunCommand(cmd)
        
    
    return DaisyKeypointDescriptorFile(keypointDescriptorFile, 
                                       keypointDescriptorFileScales, 
                                       keypointDescriptorFileOrientation,
                                       (normalizationType==NORMALIZATION_SIFT_LIKE),
                                       parseKDF)


