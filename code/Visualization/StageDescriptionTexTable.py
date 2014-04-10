# Copyright (c) 2014, Adam J. Rossi. All rights reserved. See README for licensing details.
import sys, os
sys.path.append(os.path.abspath("."))
import Chain

def typeString(t):
    return str(t)[7:-2]

reg = Chain.StageRegistry.registry



for package in reg.GetPackages():

    stages = reg.GetStages(package)
    if (len(stages)>0):
        print r"\begin{landscape}"
        #print r"\begin{figure}"
        print r"\begin{longtable}{P{5cm} P{1cm} P{16cm}}"
        #print r"\toprule"
        #print r"\toprule"
        print r"\midrule"
        
        print r"\multicolumn{3}{l}{\LARGE{\textbf{%s}}} \\" % package
        print r"\midrule"

        for stage in stages:
            print r"\textbf{\Large{%s}} & " % stage
            print r"\multicolumn{2}{P{16cm}}{\emph{\large{%s}}} \\ " % reg.GetStageDescription(package,stage)

            pMap = reg.GetStagePropertyMap(package, stage)
            if (len(pMap)>0):
                print r"\cmidrule(l){1-3}"
                print r"\textbf{Property Name} & \textbf{Data Type} & \textbf{Description}\\"
                print r"\cmidrule(l){1-3}"
                for prop in sorted(reg.GetStagePropertyMap(package, stage).keys()):
                    typeStr = typeString(reg.GetStagePropertyType(package,stage,prop))
                    propDesc = reg.GetStagePropertyDescription(package,stage,prop)
                    isEnum = (propDesc.find("{")>=0 and propDesc.find("}")>=0)
                    if (isEnum): typeStr="enum"                    
                    print r"%s & %s & %s\\" % (prop,
                                               typeStr,
                                               propDesc.replace("{","\\{").replace("}","\\}"))
            print r"\midrule"
        #print r"\bottomrule"

        #print r"\end{figure}"
        print r"\caption{Auto-documentation for \textbf{%s} package}"%package
        print r"\end{longtable}"
        print r"\end{landscape}"
