# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing details.
import sys, os
sys.path.append(os.path.abspath("."))
import Chain


def typeString(t):
    return str(t)[7:-2]


reg = Chain.StageRegistry.registry

print(r"\begin{enumerate}")
for package in reg.GetPackages():
    stages = reg.GetStages(package)
    if (len(stages)>0):
        print(r"  \item %s" % package)
        print(r"    \begin{description}")
        for stage in stages:
            print(r"      \item[%s] %s" % (stage, reg.GetStageDescription(package,stage)))
            pMap = reg.GetStagePropertyMap(package, stage)

            if (len(pMap)>0):
                print(r"        \begin{description}")
                for property in sorted(reg.GetStagePropertyMap(package, stage).keys()):
                    print("          \\item[%s] \\hfill \\\\ \n            %s (%s)" % (property, 
                                             reg.GetStagePropertyDescription(package,stage,property).replace("{","\\{").replace("}","\\}"), 
                                             typeString(reg.GetStagePropertyType(package,stage,property))))
                print(r"        \end{description}")
        print(r"    \end{description}")
print(r"\end{enumerate}")
