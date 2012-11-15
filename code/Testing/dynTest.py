# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing for details.
import sys, os
sys.path.append(os.path.abspath(".."))
import Chain


os.chdir("..")

d = {}
for dn in os.listdir("."):
    packageName = dn
    if (os.path.isdir(packageName)):
        try:
            mod = __import__(packageName, fromlist=[])
            for className in dir(mod):
                try:
                    co = getattr(mod, className)
                    if (issubclass(co, Chain.StageBase) and co!=Chain.StageBase):
                        if (not d.has_key(packageName)): d[packageName] = []
                        d[packageName].append(co)
                except:
                    pass
        except:
            pass

for k in d.keys():
    print "Package: " + k
    for c in d[k]:
        o = c()
        print " %s: %s" % (o.GetStageName(), o.GetStageDescription())
        for pk in sorted(o.GetPropertyMap().keys()):
            print "  %s: %s (%s)" % (pk, o.GetPropertyDescription(pk), str(o.GetPropertyMap()[pk]))
            
            
            
            