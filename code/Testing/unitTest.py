# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing details.
import sys, os
sys.path.append(os.path.abspath("."))
import Chain # Chain must be imported first, requirement of registry
import Sources, FeatureExtraction, FeatureMatch, BundleAdjustment, Cluster, Common


def bundlerChain(imagePath):
    
    # PMVS path
    pmvsPath = os.path.join(imagePath,"pmvs")

    # build chain
    imageSource = Sources.ImageSource(imagePath, "jpg")
    sift = FeatureExtraction.Sift(imageSource, False, "SiftHess")
    keyMatch = FeatureMatch.KeyMatch(sift, False, "KeyMatchFull")
    bundler = BundleAdjustment.Bundler([keyMatch, imageSource], forceRun=True)
    radialUndistort = Cluster.RadialUndistort([bundler, imageSource], forceRun=True)
    prepCmvsPmvs = Cluster.PrepCmvsPmvs(radialUndistort, pmvsPath, forceRun=True)
    
    # cmvs not build on 32bit Linux yet
    if (Common.Utility.PlatformName != "Linux32bit"):
        cmvs = Cluster.CMVS(prepCmvsPmvs, forceRun=True)
        pmvs = Cluster.PMVS(cmvs, forceRun=True)
    else:
        pmvs = Cluster.PMVS(prepCmvsPmvs, forceRun=True)
        
    # render chain
    print Chain.Render(pmvs,"UnitTest-bundlerChain-log.txt")


def keymatchChains(imagePath):
    # KeyMatchFull, KeyMatchGPU
    
    imageSource = Sources.ImageSource(imagePath, "pgm")
    sift = FeatureExtraction.Sift(imageSource, False, "SiftHess")
    keyMatch = FeatureMatch.KeyMatch(sift, True, "KeyMatchFull", forceRun=True)
    
    print Chain.Render(keyMatch,"UnitTest-keymatchChains-KeyMatchFull-log.txt")
    
#    keyMatch.SetProperty("Key Match Method", "KeyMatchGPU")
#    print Chain.Render(keyMatch,"UnitTest-keymatchChains-KeyMatchGPU-log.txt")

    
def siftChains(imagePath):
    #SiftWin32, SiftHess, SiftGPU, VLFeat
    
    imageSource = Sources.ImageSource(imagePath, "pgm")
    sift = FeatureExtraction.Sift(imageSource, False, "SiftWin32", forceRun=True)
    
    # SiftWin32 only on windows
    if (Common.Utility.OSName=="Windows"):
        print Chain.Render(sift,"UnitTest-siftChains-SiftWin32-log.txt")
	
	sift.SetProperty("Sift Method", "VLFeat")
	print Chain.Render(sift,"UnitTest-siftChains-VLFeat-log.txt")

    # daisy only on windows (note: this should not be the last test, as the descriptors are for ROIs)
    if (Common.Utility.OSName=="Windows"):
        imageSource = Sources.ImageSource(imagePath, "jpg")
        daisy = FeatureExtraction.Daisy(imageSource, False, roi="0,0,50,50", forceRun=True)
        print Chain.Render(daisy,"UnitTest-siftChains-daisy-log.txt")    
    
    sift.SetProperty("Sift Method", "SiftHess")
    print Chain.Render(sift,"UnitTest-siftChains-SiftHess-log.txt")

#    sift.SetProperty("Sift Method", "SiftGPU")
#    print Chain.Render(sift,"UnitTest-siftChains-SiftGPU-log.txt")




def imageConvertChain(imagePath):
    
    imageSource = Sources.ImageSource(imagePath, "jpg")
    imageConvert = Sources.ImageConvert(imageSource, imagePath, "pgm")
    print Chain.Render(imageConvert,"UnitTest-imageConvertChain-log.txt")

if __name__=="__main__":
    
    try:
        imagePath = os.path.abspath("../Datasets/ET")
        
        imageConvertChain(imagePath)
        siftChains(imagePath)
        keymatchChains(imagePath)
        bundlerChain(imagePath)
        
        print "\n\nUnit Test PASSED"
    
    except:
        print "\n\nUnit Test FAILED"
    
    
