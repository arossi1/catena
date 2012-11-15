# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing for details.
import Utility

class CCDdatabase:
    
    def __init__(self, dbPath):
        self._fillInfo(dbPath)
        
    def _fillInfo(self, dbPath):
        self._db = {}
        for l in open(dbPath,"r"):
            v = l.strip().split("|")
            self._db[v[0]] = (float(v[1]),v[2])
    
    def GetCameraCCDWidth(self, camera):
        if (self._db.has_key(camera)): return self._db[camera][0]
        else: return None

CCD_DB_FILE = "ccdwidths.csv"
Instance = CCDdatabase(Utility.GetAbsoluteFilePath(__file__, CCD_DB_FILE))