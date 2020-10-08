# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing details.
import os, unittest, tempfile, shutil

from catena import Chain # Chain must be imported first, requirement of registry
from catena import Sources, FeatureExtraction, FeatureMatch, BundleAdjustment, Cluster, Common


class ChainTester(unittest.TestCase):

    def setUp(self):
        self.output_dir = tempfile.mkdtemp()
        self.output_path = os.path.join(self.output_dir, 'output.atm')
        self.imagePath = os.path.abspath(os.path.join(os.path.dirname(__file__), "../Datasets/ET"))
        #self.imagePath = os.path.abspath("../../Datasets/ET")

    def testImageConvertChain(self):

        imageSource = Sources.ImageSource(self.imagePath, "jpg")
        imageConvert = Sources.ImageConvert(imageSource, self.imagePath, "pgm")
        Chain.Render(imageConvert, os.path.join(self.output_dir, "UnitTest-imageConvertChain-log.txt"))

    def testSiftChains(self):
        #SiftWin32, SiftHess, SiftGPU, VLFeat

        imageSource = Sources.ImageSource(self.imagePath, "pgm")
        sift = FeatureExtraction.Sift(imageSource, False, "SiftWin32", forceRun=True)

        # SiftWin32 only on windows
        if (Common.Utility.OSName=="Windows"):
            Chain.Render(sift, os.path.join(self.output_dir, "UnitTest-siftChains-SiftWin32-log.txt"))

            sift.SetProperty("Sift Method", "VLFeat")
            Chain.Render(sift,os.path.join(self.output_dir, "UnitTest-siftChains-VLFeat-log.txt"))

        # daisy only on windows (note: this should not be the last test, as the descriptors are for ROIs)
        if (Common.Utility.OSName=="Windows"):
            imageSource = Sources.ImageSource(self.imagePath, "jpg")
            daisy = FeatureExtraction.Daisy(imageSource, False, roi="0,0,50,50", forceRun=True)
            Chain.Render(daisy, os.path.join(self.output_dir,"UnitTest-siftChains-daisy-log.txt"))

        sift.SetProperty("Sift Method", "SiftHess")
        Chain.Render(sift, os.path.join(self.output_dir, "UnitTest-siftChains-SiftHess-log.txt"))

#        sift.SetProperty("Sift Method", "SiftGPU")
#        print Chain.Render(sift,"UnitTest-siftChains-SiftGPU-log.txt")

    def testKeymatchChains(self):
        # KeyMatchFull, KeyMatchGPU

        imageSource = Sources.ImageSource(self.imagePath, "pgm")
        sift = FeatureExtraction.Sift(imageSource, False, "SiftHess")
        keyMatch = FeatureMatch.KeyMatch(sift, True, "KeyMatchFull", forceRun=True)

        Chain.Render(keyMatch, os.path.join(self.output_dir, "UnitTest-keymatchChains-KeyMatchFull-log.txt"))
#
##        keyMatch.SetProperty("Key Match Method", "KeyMatchGPU")
##        print Chain.Render(keyMatch,"UnitTest-keymatchChains-KeyMatchGPU-log.txt")

    def testBundlerChain(self):

        # PMVS path
        pmvsPath = os.path.join(self.imagePath,"pmvs")

        # build chain
        imageSource = Sources.ImageSource(self.imagePath, "jpg")
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
        print(Chain.Render(pmvs, os.path.join(self.output_dir, "UnitTest-bundlerChain-log.txt")))

    def tearDown(self):
        shutil.rmtree(self.output_dir)

