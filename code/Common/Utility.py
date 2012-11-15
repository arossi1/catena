# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing for details.

import Chain
import glob, os, shutil, sys, stat, time, subprocess

def IsWindows():
    return (sys.platform=="win32")

def WriteFileList(path, pattern, fileListName):    
    f = open(os.path.join(path, fileListName),"w")
    for p in glob.glob(os.path.join(path,pattern)):
        f.write(os.path.split(p)[1]+"\n")
    f.close()
    
def MakeDir(path):
    if (not os.path.exists(path)): os.mkdir(path)
    
def MakeDirs(paths):
    for path in paths: MakeDir(path)

def DeleteDir(path):
    shutil.rmtree(path)

def CopyFiles(src, dst, ext):
    for f in glob.glob(os.path.join(src,"*."+ext)):
        shutil.copy(f,dst)

def CreateSymbolicLink(source, link):
    if (IsWindows()):
        raise Exception("CreateSymbolicLink not implemented on win32")
#        import ctypes
#        kdll = ctypes.windll.LoadLibrary("kernel32.dll")
#        kdll.CreateSymbolicLinkA(source, link, 0)
    else:
        if (not os.path.exists(link)):
            os.symlink(source, link)

def GetAbsoluteFilePath(moduleFile, relativePath):
    path = os.path.dirname(os.path.abspath(moduleFile))
    return os.path.abspath(os.path.join(path, relativePath))

def GetFileSize(path):
    return os.stat(path)[stat.ST_SIZE]

def InvalidString(): return ""
def InvalidInt():    return -sys.maxint
def InvalidFloat():  return float(-sys.maxint)

def RunCommand(cmd, cwd=None, shell=False, printStdout=False, captureCout=False):
    
#    p = None
#    if (captureCout):
#        p = subprocess.Popen(cmd, 
#                             stdin=subprocess.PIPE, 
#                             stdout=subprocess.PIPE, 
#                             stderr=subprocess.PIPE, 
#                             cwd=cwd, shell=shell)    
#    else:
#        log = Chain.Analyze.GetLog()
#        p = subprocess.Popen(cmd, 
#                             stdin=subprocess.PIPE, 
#                             stdout=log, 
#                             stderr=log, 
#                             cwd=cwd, shell=shell)
        
    p = subprocess.Popen(cmd, 
                         stdin=subprocess.PIPE, 
                         stdout=subprocess.PIPE, 
                         stderr=subprocess.PIPE, 
                         cwd=cwd, shell=shell)
    
        

    #(child_stdin, child_stdout) = (p.stdin, p.stdout)
#    ret = p.wait()
#    if (ret!=0):
#        for l in p.stdout.readlines(): print l.strip()
#        raise Exception("[Return Code = %d] Failed to execute: %s" % (ret, cmd))

    if (not captureCout):
        Chain.Analyze.ProcessStart()
    
    stdoutLines = []
#    stderrLines = []
    while (True):
        p.poll()
        
        if (captureCout):
            for l in p.stdout.readlines():
                stdoutLines.append(l.strip())
                if (printStdout): print l.strip()
                
        else:
            for l in p.stdout.readlines():
                Chain.Analyze.WriteStatus(l.strip())
            for l in p.stderr.readlines():
                Chain.Analyze.WriteStatus(l.strip())
#        
#        if (p.stderr!=None):
#            for l in p.stderr.readlines():
#                stderrLines.append(l.strip())
#                if (printStdout): print l.strip()
        
        if (p.returncode!=None): break
        time.sleep(0.2)
        
    if (p.returncode!=0):
        raise Exception("[Return Code = %d] Failed to execute: %s" % (p.returncode, cmd))
    
#    print stdoutLines, stderrLines
    return stdoutLines
#    ret = p.wait()
#    if (ret!=0):
#        #for l in p.stdout.readlines(): print l.strip()
#        raise Exception("[Return Code = %d] Failed to execute: %s" % (ret, cmd))
    
def RunCommand2(cmd, args=None, cwd=None, shell=False, printStdout=False, captureCout=False):
    
    p = subprocess.Popen(args=args,
                         executable=cmd, 
                         stdin=subprocess.PIPE, 
                         stdout=subprocess.PIPE, 
                         stderr=subprocess.PIPE, 
                         cwd=cwd, shell=shell)

    if (not captureCout):
        Chain.Analyze.ProcessStart()
    
    stdoutLines = []
    
    while (True):
        p.poll()
        
        if (captureCout):
            for l in p.stdout.readlines():
                stdoutLines.append(l.strip())
                if (printStdout): print l.strip()
                
        else:
            for l in p.stdout.readlines():
                Chain.Analyze.WriteStatus(l.strip())
            for l in p.stderr.readlines():
                Chain.Analyze.WriteStatus(l.strip())
        
        if (p.returncode!=None): break
        time.sleep(0.2)
        
    if (p.returncode!=0):
        raise Exception("[Return Code = %d] Failed to execute: %s" % (p.returncode, cmd))
    
    return stdoutLines
    

def ConvertImagesToGrayscalePGM(imagePath, extension):
    import Image
    for p in glob.glob(os.path.join(imagePath,"*."+extension)):
        Image.open(p).convert("L").save(os.path.splitext(p)[0] + ".pgm")
        
        
        
        
        