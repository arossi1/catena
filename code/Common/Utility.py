# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing details.

from .. import Chain
import glob, os, shutil, sys, stat, time, subprocess, platform, string

def IsWindows():
    return (sys.platform=="win32")

def WriteFileList(path, pattern, fileListName):    
    f = open(os.path.join(path, fileListName),"w")
    for p in sorted(glob.glob(os.path.join(path,pattern))):
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
        raise Exception("CreateSymbolicLink not implemented on windows")
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
def InvalidInt():    return -sys.maxsize
def InvalidFloat():  return float(-sys.maxsize)

def Quoted(s):          return "\"%s\""%s    
def CommandArgs(*args): 
    return string.join([str(a) for a in args], " ")

def ShouldRun(forceRun, *args):
    if (forceRun): return True
    l = []
    for f in args:
        if (isinstance(f,list) or isinstance(f,tuple)):
            l.extend(f)
        else:
            l.append(f)
    for f in l:            
        if (os.path.isdir(f)): continue
        if (not os.path.exists(f) or GetFileSize(f)==0):
            return True
    return False

def GetExePath(moduleFile, exe, checkExistence=True):
    
    # special case for win64
    if (PlatformName == "Windows64bit"):
        
        # prefer 64-bit, but use 32-bit if it exists
        exe64 = GetAbsoluteFilePath(moduleFile, os.path.join("Windows64bit","bin",exe))+".exe"
        exe32 = GetAbsoluteFilePath(moduleFile, os.path.join("Windows32bit","bin",exe))+".exe"        
        
        exe = exe64
        if (checkExistence):
            if   (os.path.exists(exe64)): exe = exe64
            elif (os.path.exists(exe32)): exe = exe32
            else:
                raise Exception("Executables do not exist: (%s) (%s)" % (exe64,exe32))
    
    else:
        exe = GetAbsoluteFilePath(moduleFile, os.path.join(PlatformName,"bin",exe))
            
        if (IsWindows() and not exe.lower().endswith(".exe")):
            exe += ".exe"
        
        if (not os.path.exists(exe) and checkExistence):
            raise Exception("Executable does not exist: " + exe)
    
    # add lib to LD_LIBRARY_PATH
    if (not IsWindows()):
        libDir = GetAbsoluteFilePath(moduleFile,
                                     os.path.join(PlatformName,"lib"))
        if (os.path.exists(libDir)):
            if ("LD_LIBRARY_PATH" not in os.environ or os.environ["LD_LIBRARY_PATH"]==""):
                os.environ["LD_LIBRARY_PATH"] = "."
            
            if (libDir not in os.environ["LD_LIBRARY_PATH"]):
                os.environ["LD_LIBRARY_PATH"] += ":%s" % libDir
    
    return exe
    

#def RunCommand(cmd, cwd=None, shell=(not IsWindows()), printStdout=False, captureCout=False):
def RunCommand(cmd, cwd=None, shell=True, printStdout=False, captureCout=False):
    
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
                         cwd=cwd, shell=shell, text=True)
    
        

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
                if (printStdout): print(l.strip())
                
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
                         cwd=cwd, shell=shell, text=True)

    if (not captureCout):
        Chain.Analyze.ProcessStart()
    
    stdoutLines = []
    
    while (True):
        p.poll()
        
        if (captureCout):
            for l in p.stdout.readlines():
                stdoutLines.append(l.strip())
                if (printStdout): print(l.strip())
                
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
        
        
OSName = platform.system()
Machine = platform.machine()
ArchitectureName = platform.architecture()[0]
if (Machine=="AMD64" and OSName=="Windows"):
    PlatformName = "Windows64bit"
else:
    PlatformName = "%s%s"%(OSName,ArchitectureName)
        
