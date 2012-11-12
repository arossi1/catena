# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing for details.
import os, sys

if (sys.platform=="win32"):
    ROOT = os.path.join(os.path.abspath("."), "3rdParty/winxp32/bin")

    EXE_IvaInfo = os.path.join(r"C:\svn\Iva\winxp_vs100\bin", "ivaInfo")
    EXE_IvaMath = os.path.join(r"C:\svn\Iva\winxp_vs100\bin", "ivaMath")
    EXE_IvaCopy = os.path.join(r"C:\svn\Iva\winxp_vs100\bin", "ivaCopy")    
    EXE_Bundler = os.path.join(ROOT, "Bundler")

elif (sys.platform=="linux2"): 
    ROOT = os.path.join(os.path.abspath("."), "3rdParty/linux2/bin")

    EXE_IvaInfo = os.path.join("/home/ajrossi/Source/Iva/linux_x64_gcc434/bin", "ivaInfo")
    EXE_IvaMath = os.path.join("/home/ajrossi/Source/Iva/linux_x64_gcc434/bin", "ivaMath")
    EXE_IvaCopy = os.path.join("/home/ajrossi/Source/Iva/linux_x64_gcc434/bin", "ivaCopy")
    EXE_Bundler = os.path.join(ROOT, "bundler")

else:
    raise Exception("Unhandled platform: " + sys.platform)


IVA_JPEG_OCF = os.path.join(os.path.abspath("."), "3rdParty/config", "jpeg.ocf")

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
EXE_SiftWin32 = os.path.join(ROOT, "siftWin32")
EXE_SiftHess = os.path.join(ROOT, "sifthess")
EXE_SiftGPU = os.path.join(ROOT, "SiftGPUKeypoint")

