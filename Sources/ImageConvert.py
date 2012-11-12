# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing for details.
import Chain
import Common
import os


class ImageConvert(Chain.StageBase):

    def __init__(self, inputStages=None, imagePath="", extension="", mode="PIL"):
        Chain.StageBase.__init__(self,
                                 inputStages,
                                 "Converts images to a desired format",
                                 {"Image Path":"Output image path", 
                                  "Image Extension":"Image extension",
                                  "Mode":"Conversion mode {PIL,Iva,Iva-12to8bit}"})
        
        self._properties["Image Path"] = imagePath
        self._properties["Image Extension"] = extension
        self._properties["Mode"] = mode
        

    def GetInputInterface(self):
        return {"images":(0,Common.sfmImages)}
    
    def GetOutputInterface(self):
        return {"images":Common.sfmImages}

    def Execute(self):
        images = self.GetInputStageValue(0, "images")
        
        self.StartProcess()

        Common.Utility.MakeDir(self._properties["Image Path"])
        
        if (self._properties["Mode"]=="PIL"):            
            images = images.Convert(self._properties["Image Path"],
                                    self._properties["Image Extension"])
            
        elif (self._properties["Mode"]=="Iva"):
            
            cImages = []
            for im in images.GetImages():
                
                outputFilePath = os.path.join(self._properties["Image Path"],
                                              os.path.splitext(os.path.split(im.GetFilePath())[1])[0] + 
                                              "." + self._properties["Image Extension"])
                
                if (not os.path.exists(outputFilePath) or
                    Common.Utility.GetFileSize(outputFilePath)==0):
                    
                    cmd = "\"%s\" -i \"%s\" -o \"%s\"" % \
                        (Common.ExecutablePath.EXE_IvaCopy,
                         im.GetFilePath(),
                         outputFilePath)
                    
                    if (self._properties["Image Extension"]=="jpg"):
                        cmd += " -ocf \"%s\"" % Common.ExecutablePath.IVA_JPEG_OCF

                    Common.Utility.RunCommand(cmd, shell=True)
                    
                cImages.append(Common.sfmImage(outputFilePath))
            
            images = Common.sfmImages(path=self._properties["Image Path"],
                                      extension=self._properties["Image Extension"], 
                                      images=cImages,
                                      focalPixelOverride=images.GetFocalPixelOverride())
            
        elif (self._properties["Mode"]=="Iva-12to8bit"):
            
            cImages = []
            for im in images.GetImages():
                
                outputFilePath = os.path.join(self._properties["Image Path"],
                                              os.path.splitext(os.path.split(im.GetFilePath())[1])[0] + 
                                              "." + self._properties["Image Extension"])
                
                if (not os.path.exists(outputFilePath) or
                    Common.Utility.GetFileSize(outputFilePath)==0):
                    
                    cmd = "\"%s\" -formula \"i0*255/4096\" -i0 \"%s\" -o \"%s\" -dt U8 -ocf \"%s\"" % \
                        (Common.ExecutablePath.EXE_IvaMath,
                         im.GetFilePath(),
                         outputFilePath,
                         Common.ExecutablePath.IVA_JPEG_OCF)
                    print cmd
                    Common.Utility.RunCommand(cmd, shell=True)
                    
                cImages.append(Common.sfmImage(outputFilePath))
            
            images = Common.sfmImages(path=self._properties["Image Path"], 
                                      extension=self._properties["Image Extension"],
                                      images=cImages,
                                      focalPixelOverride=images.GetFocalPixelOverride())
        
        else:
            raise Exception("Unknown conversion mode: " + self._properties["Mode"])
        
            
        self.SetOutputValue("images", images)

        
