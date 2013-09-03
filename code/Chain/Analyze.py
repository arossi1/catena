# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing details.
import os, time

class Analyze:
    
    def __init__(self, printProgress=False):
        self._timingPoints = []
        self._printProgress = printProgress
        self._log = None
        self._statusObject = None        
    
        
    def StartProcess(self, name):
#        if (self._printProgress):
#            print "\n{%s}\n"%name
        
        self.WriteStatus("\n" + "-"*80 + "\n{%s}\n"%name)            
        
        self.End()
        self._timingPoints.append([name, time.clock()])
        
    def WriteStatus(self, s):
        
        if (self._printProgress):
            print s,
        if (self._log):
            self._log.flush()
            self._log.write(s)
        if (self._statusObject):
            self._statusObject.appendStatus(s[:-1])
        
    def End(self):
        if (len(self._timingPoints)>0 and 
            len(self._timingPoints[-1])==2):
            self._timingPoints[-1].append(time.clock())
            
    def Clear(self):
        self._timingPoints = []        
    
    def ConvertToElapsedTimes(self):
        self.End()
        tp = []
        for t in self._timingPoints:
            tp.append([t[0], (t[2]-t[1])])
        
        maxElapsed = max([t[1] for t in tp])
        label = "sec";div=1.0;
        if (int(maxElapsed/(60.0*60.0))>0):
            label = "hr";div=60.0*60.0;
        elif (int(maxElapsed/60.0)>0):
            label = "min";div=60.0;
            
        for t in tp: t[1] = "%.2f %s" % (t[1]/div, label)
            
        self._timingPoints = tp
        
    def getTimingAnalysis(self):
        s = "\n"
        for t in self._timingPoints:
            s += ("%s " + "{%s}"*(len(t)-1) + "\n\n") % tuple(t)
        return s[:-2]
    


__analyze = Analyze(True)
def Initialize(logFilePath=None):
    __analyze.Clear()
    if (logFilePath):
        __analyze._log = open(logFilePath, "w")
def StartProcess(name):
    __analyze.StartProcess(name)
def End(): 
    __analyze.End()
def PrintResults():
    __analyze.ConvertToElapsedTimes()
    ta = __analyze.getTimingAnalysis()
#    print ta
    __analyze.WriteStatus("\n(Render Complete)\n")
    __analyze.WriteStatus("*"*80 + "\n")
    __analyze.WriteStatus("-"*80 + 
                          "\nTiming Analysis\n" + 
                          "-"*80 + ta + "\n" + 
                          "-"*80 + "\n")
    __analyze.WriteStatus("*"*80 + "\n")

    if (__analyze._log):
        __analyze._log.close()
        __analyze._log = None


def SetStatusObject(s):
    __analyze._statusObject = s
    
#def GetLog():
#    __analyze.WriteStatus(time.strftime("\n[%Y%m%d--%H:%M:%S]\n\n"))
#    __analyze._log.flush()
##    return __analyze._log
#
#    return os.fdopen(__analyze._writePipe, "w", 0)

def ProcessStart():
    __analyze.WriteStatus(time.strftime("\n[%Y%m%d--%H:%M:%S]\n\n"))
    
def WriteStatus(s):
    __analyze.WriteStatus(s+"\n")

    
if __name__=="__main__":
    
    #a = Analyze(True)
    
#    for i in range(5):
#        a.StartProcess("test%d"%i)
#        time.sleep(0.5*i)
    #a.ConvertToElapsedTimes()
        
    PrintResults()