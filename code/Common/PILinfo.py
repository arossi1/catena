# Copyright (c) 2014, Adam J. Rossi. All rights reserved. See README for licensing details.
import os, time
from . import jhead

class PILinfo(jhead.jheadInfo):
    
    def __init__(self, imagePath):
        jhead.jheadInfo.__init__(self, imagePath)
        
    def _fillInfo(self):
        from PIL import Image
        im = Image.open(self._imagePath)
        
        self.__dict__["Date/Time"] = None
        self.__dict__["File name"] = os.path.split(self._imagePath)[1]
        self.__dict__["File date"] = None
        self.__dict__["File size"] = "%d bytes" % os.stat(self._imagePath).st_size
        self.__dict__["Resolution"] = "%d x %d" % im.size
        self.__dict__["XResolution"] = im.size[0]
        self.__dict__["YResolution"] = im.size[1]
        
        im = None

