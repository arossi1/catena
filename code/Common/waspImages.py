# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing details.
import os, shutil
from . import waspImage


class waspImages:
    
    def __init__(self, applanixFilePath, imagePath, populateImages=True):
        self._applanixFilePath = applanixFilePath
        self._imagePath = imagePath
        if (populateImages): self._populateImages()
        
    def _populateImages(self):
        self._images = []
        f = open(self._applanixFilePath)
        for l in f.readlines()[39:]:
            wi = waspImage.waspImage(l, self._imagePath)
            if (wi.fileExists()): self._images.append(wi)
        f.close()
        
    def splitImages(self, setSize, overlap=0):
        sets = []
        i = 0
        while (i<len(self._images)-1):
            end = min(i+setSize, len(self._images))
            wi = waspImages(self._applanixFilePath, self._imagePath, False)
            wi._images = self._images[i:end]
            sets.append(wi)
            i += (setSize-overlap)            
        return sets
    
    def copyImages(self, destDir):
        self._imagePath = destDir
        for wi in self._images:
            shutil.copy(wi.getFilePath(), destDir)
            wi._dirPath = destDir            
    
    def __str__(self):
        return "\n".join([str(x) for x in self._images])



if __name__=="__main__":
    wi = waspImages(r"C:\Documents and Settings\Adam Rossi\Desktop\thesis\root\Datasets\wasp_downtown_center_250\applanix_full\vnir_eo.txt",
                    r"C:\Documents and Settings\Adam Rossi\Desktop\thesis\root\Datasets\wasp_downtown_center_250\CENTER_250")
    
    dst = r"C:\Documents and Settings\Adam Rossi\Desktop\thesis\root\Datasets\wasp_downtown_center_250\sets"
    for i,x in enumerate(wi.splitImages(20, 3)):
        print(i)
        dd = os.path.join(dst, str(i))
        if (not os.path.exists(dd)): os.makedirs(dd)
        x.copyImages(dd)
    
    
    
    