# Copyright (c) 2014, Adam J. Rossi. All rights reserved. See README for licensing details.
import sys, os
sys.path.append(os.path.abspath("."))
import Chain

def typeString(t):
    return str(t)[7:-2]

reg = Chain.StageRegistry.registry


thesis = True

for package in reg.GetPackages():

    stages = reg.GetStages(package)
    if (len(stages)>0):
        print r"\begin{landscape}"
        if (thesis):    print r"\begin{longtable}{P{5cm} P{1cm} P{2.5cm} P{9cm}}"
        else:           print r"\begin{longtable}{P{5cm} P{1cm} P{2.5cm} P{13cm}}"
        
        print r"\midrule"
        print r"\multicolumn{4}{l}{\LARGE{\textbf{%s}}} \\" % package
        print r"\midrule"
        
        for stage in stages:
            print r"\textbf{\Large{%s}} & " % stage

            if (thesis):    print r"\multicolumn{3}{P{9cm}}{\emph{\large{%s}}} \\ " % reg.GetStageDescription(package,stage)
            else:           print r"\multicolumn{3}{P{14cm}}{\emph{\large{%s}}} \\ " % reg.GetStageDescription(package,stage)

            stageInstance = reg.CreateInstance(package, stage)
            pMap = reg.GetStagePropertyMap(package, stage)
            if (len(pMap)>0):
                print r"\cmidrule(l){1-4}"
                print r"\textbf{Property Name} & \textbf{Data Type} & \textbf{Default Value} & \textbf{Description}\\"
                print r"\cmidrule(l){1-4}"
                for prop in sorted(reg.GetStagePropertyMap(package, stage).keys()):
                    typeStr = typeString(reg.GetStagePropertyType(package,stage,prop))
                    propDesc = reg.GetStagePropertyDescription(package,stage,prop).replace("{","\\{").replace("}","\\}")
                    defaultVal = str(stageInstance.GetProperty(prop))
                    if ((typeStr=="dict") or (typeStr=="str" and len(defaultVal)==0)):
                        defaultVal = "[empty]"
                    isEnum = (propDesc.find("{")>=0 and propDesc.find("}")>=0)
                    if (isEnum): typeStr="enum"                    
                    print r"%s & %s & %s & %s\\" % (prop, typeStr, defaultVal, propDesc)
            print r"\cmidrule(l){1-4}"

        print r"\caption{Auto-documentation for \textbf{%s} package}"%package
        print r"\end{longtable}"
        print r"\end{landscape}"
