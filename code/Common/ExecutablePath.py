# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing details.
import os, sys, platform

osName = platform.system()
archName = platform.architecture()[0]
platName = "%s%s"%(osName,archName)
ROOT = os.path.join(os.path.abspath("."), "3rdParty/%s/bin" % platName)

if (osName=="Windows" and archName=="32bit"):    
    EXE_Bundler = os.path.join(ROOT, "Bundler")
    EXE_SiftWin32 = os.path.join(ROOT, "siftWin32")

elif (osName=="Linux" and archName=="32bit"):
    EXE_Bundler = os.path.join(ROOT, "bundler")
    EXE_SiftWin32 = os.path.join(ROOT, "siftLowe")

    if (not os.environ.has_key("LD_LIBRARY_PATH")):
        os.environ["LD_LIBRARY_PATH"] = ""
    os.environ["LD_LIBRARY_PATH"] += ".:%s" % os.path.join(os.path.abspath("."), "3rdParty/%s/lib" % platName)

elif (osName=="Linux" and archName=="64bit"):
    EXE_Bundler = os.path.join(ROOT, "bundler")
    EXE_SiftWin32 = os.path.join(ROOT, "siftLowe")
    
    if (not os.environ.has_key("LD_LIBRARY_PATH")):
        os.environ["LD_LIBRARY_PATH"] = ""
    os.environ["LD_LIBRARY_PATH"] += ".:%s" % os.path.join(os.path.abspath("."), "3rdParty/%s/lib" % platName)

else:
    raise Exception("Unhandled platform: %s %s" % (archName,osName))


EXE_Bundle2PMVS = os.path.join(ROOT, "Bundle2PMVS")
EXE_Bundle2Vis = os.path.join(ROOT, "Bundle2Vis")
EXE_CMVS = os.path.join(ROOT, "cmvs")
EXE_PMVS2 = os.path.join(ROOT, "pmvs2")
EXE_KeyMatchFull = os.path.join(ROOT, "KeyMatchFull")
EXE_KeyMatchGPU = os.path.join(ROOT, "SiftGPUMatch")
EXE_RadialUndistort = os.path.join(ROOT, "RadialUndistort")
EXE_JHead = os.path.join(ROOT, "jhead")
EXE_Daisy = os.path.join(ROOT, "daisy")
EXE_KeypointCombine = os.path.join(ROOT, "keypointCombine")
EXE_SiftVLFeat = os.path.join(ROOT, "sift")
EXE_SiftHess = os.path.join(ROOT, "sifthess")
EXE_SiftGPU = os.path.join(ROOT, "SiftGPUKeypoint")
