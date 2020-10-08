# Copyright (c) 2014, Adam J. Rossi. All rights reserved. See README for licensing details.
import os
from . import jhead, PILinfo
from PIL import Image as PILImage


class sfmImage:
    
    def __init__(self, filePath, metadata=None):
        self._filePath = filePath
        self._metadata = metadata
        
    def GetFileName(self):      return os.path.split(self._filePath)[1]
    def GetFilePath(self):      return self._filePath
    def GetFocalPixels(self):   return self._getMetadata().GetFocalPixels()
    def GetXResolution(self):   return self._getMetadata().GetXResolution()
    def GetYResolution(self):   return self._getMetadata().GetYResolution()    
    
    def ConvertToPGM(self, outputPath):
        pgmFilePath = os.path.join(outputPath, os.path.splitext(os.path.split(self._filePath)[1])[0] + ".pgm")
        if (not os.path.exists(pgmFilePath)):
            with PILImage.open(self._filePath) as im:
                im.convert("L").save(pgmFilePath)
        return sfmImage(pgmFilePath, self._getMetadata())
    
    def Convert(self, outputPath, type):
        outputFilePath = os.path.join(outputPath, os.path.splitext(os.path.split(self._filePath)[1])[0] + "." + type)
        if (not os.path.exists(outputFilePath)):
            with PILImage.open(self._filePath) as im:
                im.save(outputFilePath)
        return sfmImage(outputFilePath) #, self._getMetadata())
    
    def SplitTiles(self, outputPath, dim=512):
        tiles = []
        
        im = PILImage.open(self._filePath)
        for tdims in self.GetTileDims(dim):
            tilePath = os.path.join(outputPath, self.GetTileFileName(tdims))
            im.crop(tdims).save(tilePath) # left, upper, right, and lower pixel coordinate
            tiles.append(tilePath)
        im.close()
        return tiles
    
    def GetTileFileName(self, tdims):
        fn,ext = os.path.splitext(self.GetFileName())
        return "%s_%d_%d_%d_%d%s" % (fn,tdims[0],tdims[1],tdims[2],tdims[3],ext)
    
    def GetTileDims(self, dim=512):
        tiles = []
        im = PILImage.open(self._filePath)
        w,h = im.size
        for ty in range(0,h,dim):
            th = min(ty+dim, h)
            for tx in range(0,w,dim):
                tw = min(tx+dim, w)
                tiles.append((tx,ty,tw,th))
        im.close()                
        return tiles
    
    def _getMetadata(self):
        if (not self._metadata):
            try:    self._metadata = jhead.jheadInfo(self._filePath)  # try jhead (EXIF tags)
            except: self._metadata = PILinfo.PILinfo(self._filePath)  # otherwise, use PIL
        return self._metadata
    
    def __str__(self):
        return "%s" % os.path.split(self._filePath)[1]
    
    def __hash__(self):
        return self._filePath.__hash__()
    
    def __eq__(self, other):
        if (not other):return False
        else:return self._filePath==other._filePath
    
    
