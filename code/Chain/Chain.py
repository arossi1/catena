# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing details.
import Analyze
import traceback, sys

def Render(lastStages, logFilePath=None):
    try:
        if (not isinstance(lastStages,list)):
            lastStages = [lastStages]
        
        Analyze.Initialize(logFilePath)
        
        out = []
        for stage in lastStages:
            stage.Reset()
            out.append(stage.GetOutput())
        
        Analyze.PrintResults()
        return out
    except Exception, e:
#            exc_type, exc_value, exc_traceback = sys.exc_info()
        Analyze.WriteStatus(traceback.format_exc())            
#            traceback.print_exception(exc_type, exc_value, exc_traceback, file=Analyze.GetLog())
#            traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stderr)
#            sys.stderr.write("\n"*2)
        raise e