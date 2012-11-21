# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing details.
"""
This is my bundle file module
"""


class Camera:
    
    """
    Constructor
    Args:
            focalLength: camera focal length
            k0: camera param1
            k1: camera param2
            R: rotation matrix
            T: translation matrix
    """    
    def __init__(self, focalLength, k0, k1, R, T):
        self._focalLength = focalLength
        self._k0 = k0
        self._k1 = k1
        self._R = R
        self._T = T
    
    def __str__(self):
        s =  "Focal length: %f\n" % self._focalLength
        s += "          K0: %f\n" % self._k0
        s += "          K1: %f\n" % self._k1
        s += "           R: %f %f %f\n" % self._R[0:3]
        s += "              %f %f %f\n" % self._R[3:6]
        s += "              %f %f %f\n" % self._R[6:9]
        s += "           T: %f %f %f\n" % self._T
        return s


class Point3D:
    
    def __init__(self, coordinate, color):
        self._coordinate = coordinate   # 3D coordinate
        self._color = color             # color
        self._2Dpoints = []


    def GetCoordinate(self):
        """GetCoordinate doc"""
        return self._coordinate
    def GetColor(self):      return self._color
    def Get2DPoints(self):   return self._2Dpoints

    def Add2DPoint(self, coordinate, cameraIndex, keypointIndex, image):
        coordinateImage = (coordinate[0] + image.GetXResolution()/2.0,
                           image.GetYResolution() - (coordinate[1] + image.GetYResolution()/2.0))
        self._2Dpoints.append(Point2D(coordinate, coordinateImage, cameraIndex, keypointIndex, image))
                
    def __str__(self):
        s =  "Coordinate: (%f, %f, %f)\n" % self._coordinate
        s += "     Color: (%f, %f, %f)\n" % self._color
        for i, point in enumerate(self._2Dpoints):
            s += "\n  [2D Point %d]\n  %s" % (i, str(point).replace("\n", "\n  "))
        return s
    
    
class Point2D:
    def __init__(self, coordinate, coordinateImage, cameraIndex, keypointIndex, image):
        self._coordinate = coordinate           # 2D coordinate (position of keypoint)
        self._coordinateImage = coordinateImage # 2D image coordinate
        self._cameraIndex = cameraIndex         # camera index
        self._keypointIndex = keypointIndex     # index of SIFT keypoint
        self._image = image                     # image reference
        
    def GetCoordinate(self):        return self._coordinate
    def GetCoordinateImage(self):   return self._coordinateImage
    def GetCameraIndex(self):       return self._cameraIndex
    def GetKeypointIndex(self):     return self._keypointIndex
    def GetImage(self):             return self._image
        
    def __str__(self):
        s =  "      Coordinate: (%f, %f)\n" % self._coordinate
        s += "Image Coordinate: (%f, %f)\n" % self._coordinateImage
        s += "    Camera Index: %d\n" % self._cameraIndex
        s += "  Keypoint Index: %d\n" % self._keypointIndex
        s += "           Image: %s\n" % self._image.GetFileName()
        return s

        
class BundleFile:
    
    VERSION = "0.3"
    """Bundle file version"""
    
    def __init__(self, bundleFilePath, images):
	"""init method"""
        self._bundleFilePath = bundleFilePath
        self._images = images
        self._parse()
    
    def GetBundleFilePath(self):    return self._bundleFilePath
    def GetImages(self):            return self._images
    def GetCameras(self):           return self._cameras
    def Get3DPoints(self):          return self._3Dpoints
        
    def _parse(self):
        
        self._cameras = []
        self._3Dpoints = []
        
        f = open(self._bundleFilePath,"r")
        l = f.readline()
        if (("#" != l[0]) or
            (l.split("v")[1].strip() != BundleFile.VERSION)):
            raise Exception("Unsupported bundler version [%s]" % l)
        
        numCameras, numVisiblePoints = [int(x) for x in f.readline().split(" ")]
        
        # read camera data
        for i in range(numCameras):
            focalLength, k0, k1 = [float(x) for x in f.readline().split(" ")]
            R =  [float(x) for x in f.readline().split(" ")]
            R += [float(x) for x in f.readline().split(" ")]
            R += [float(x) for x in f.readline().split(" ")]
            T =  [float(x) for x in f.readline().split(" ")]
            self._cameras.append(Camera(focalLength, k0, k1, tuple(R), tuple(T)))
            
        # read 3D point data
        for i in range(numVisiblePoints):
            X,Y,Z = [float(x) for x in f.readline().split(" ")]
            r,g,b = [float(x) for x in f.readline().split(" ")]
            point3D = Point3D((X,Y,Z), (r,g,b))
            self._3Dpoints.append(point3D)
            
            vals = f.readline().split(" ")
            numVisible = int(vals.pop(0))
                        
            # read corresponding 2D point data
            for j in range(numVisible):
                cameraIndex = int(vals.pop(0))
                keypointIndex = int(vals.pop(0))
                x = float(vals.pop(0))
                y = float(vals.pop(0))
                point3D.Add2DPoint((x,y), cameraIndex, keypointIndex, self._images[cameraIndex])                
            
        f.close()
        
        
    def __str__(self):
        s = ""
        for i,camera in enumerate(self._cameras):
            s += "\n[Camera %d]\n%s" % (i, camera)
        s += "\n"       
        for i,point in enumerate(self._3Dpoints):
            s += "\n[3D Point %d]\n%s\n" % (i, point)        
        return s


    
