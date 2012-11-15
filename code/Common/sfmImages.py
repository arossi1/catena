# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing for details.
import os, glob, string
from multiprocessing import Pool
import Common

_multiThreaded = True
__parseSift = False
def RunSiftSingle(im):          return im.RunSift(__parseSift)
def RunDaisySingle(im):         return im.RunDaisy(__parseSift)
def RunVLFeatSiftSingle(im):    return im.ConvertKDFToSiftWin32(im.RunVLFeatSift(__parseSift), __parseSift)
def ConvertToPGMSingle((im, path)):  return im.ConvertToPGM(path)
def ConvertSingle((im, path, type)): return im.Convert(path, type)



class sfmImages:
    
    def __init__(self, path="", extension="", images=None, focalPixelOverride=0):
        self._path = path
        self._extension = extension
        self._focalPixelOverride = focalPixelOverride
        if (images==None):
            self._images = []
            self._fillImages()
        else:
            self._images = images
        
    def GetPath(self):              return self._path
    def GetImageListPath(self):     return self._imageListPath
    def GetTileListPath(self):      return self._tileListPath
    def GetExtension(self):         return self._extension
    def GetFocalPixelOverride(self):return self._focalPixelOverride
    def GetImages(self):            return self._images
    def GetImage(self, fileName):
        for im in self._images:
            if (im.GetFileName()==fileName): return im
        return None
    
    def _fillImages(self):        
        for p in glob.glob(os.path.join(self._path,"*."+self._extension)):
            self._images.append(Common.sfmImage(p))    
    
    
    def ConvertToPGM(self, outputPath):
        Common.Utility.MakeDir(outputPath)
        images = sfmImages(outputPath, "pgm")

        # single threaded
        images._images = []
        for im in self._images: 
            images._images.append(im.ConvertToPGM(outputPath))
        
        # multi-threaded
#        images._images = Pool().map(ConvertToPGMSingle, [(im, outputPath) for im in self._images])        
        return images
    
    def Convert(self, outputPath, type):
        if (type=="pgm"):
            return self.ConvertToPGM(outputPath)
        else:
            Common.Utility.MakeDir(outputPath)
            images = sfmImages(outputPath, type)
            #images._images = Pool().map(ConvertSingle, [(im, outputPath, type) for im in self._images])   
            
            images._images = []
            for im in self._images: 
                images._images.append(im.Convert(outputPath, type))     
            return images
    
    def SplitTiles(self, outputPath, dim=512):
        Common.Utility.MakeDir(outputPath)
        for im in self._images: im.SplitTiles(outputPath, dim)
        self.WriteTileList(outputPath, dim)
        return sfmImages(outputPath, self._extension)
    
    def WriteTileList(self, outputPath, dim):
        self._tileListPath = os.path.join(self._path, "tilelist.txt")
        f = open(self._tileListPath,"w")
        for im in self._images:
            tileDims = im.GetTileDims(dim)
            f.write("%s,%d\n" % (im.GetFileName(),len(tileDims)))
            for tdims in tileDims:
                tilePath = os.path.join(outputPath, im.GetTileFileName(tdims))
                params = [str(x) for x in [tilePath.replace(self._path,"")]+list(tdims)]
                f.write(string.join(params,",") + "\n")
        f.close()
    
    def WriteFileList(self, includeFocalPixels=True):        
        self._imageListPath = os.path.join(self._path, "imagelist.txt")
        f = open(self._imageListPath,"w")
        for im in self._images:
            if (includeFocalPixels and im.GetFocalPixels()):
                f.write("%s 0 %0.5f\n" % (im.GetFileName(), im.GetFocalPixels()))
            elif (includeFocalPixels and self._focalPixelOverride>0):
                f.write("%s 0 %0.5f\n" % (im.GetFileName(), self._focalPixelOverride))
            elif (includeFocalPixels):
                raise Exception("Unknown focal pixels")
            else:
                f.write("%s\n" % im.GetFileName())
        f.close()
        
    def __str__(self):
        s = "[%s, %s]" % (self._path, self._extension)
        for im in self._images: s += "  %s\n" % im
        return s
    
    
    
    