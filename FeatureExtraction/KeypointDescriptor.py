# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing for details.
import math

class KeypointDescriptor:

    def __init__(self, row, column, scale, orientation, vector):
        self._row = row
        self._column = column
        self._scale = scale
        self._orientation = orientation
        self._vector = vector
        
    def Row(self):          return self._row
    def Column(self):       return self._column
    def Scale(self):        return self._scale
    def Orientation(self):  return self._orientation
    def Vector(self):       return self._vector
    
    def Compare(self, o):
        if (self.Row() != o.Row()): return cmp(self.Row(), o.Row())
        else:                       return cmp(self.Column(), o.Column())
        
    def DistanceSquared(self, kd):        
        if (len(self._vector) != len(kd._vector)):
            raise Exception("keypoint descriptor vector lengths differ (%d & %d)" % (len(self._vector),len(kd._vector)))

        distanceSquared = 0
        for i in range(len(self._vector)):
            distanceSquared += math.pow(self._vector[i] - kd._vector[i], 2.0)

        return distanceSquared
        
    def __str__(self):
        s =  "        Row: %f\n" % self._row
        s += "     Column: %f\n" % self._column
        s += "      Scale: %f\n" % self._scale
        s += "Orientation: %f\n" % self._orientation
        s += "     Vector: %s\n" % self._vector
        return s









