# Copyright (c) 2012, Adam J. Rossi. All rights reserved. See README for licensing details.
from .. import Chain, Common, FeatureMatch, BundleAdjustment
import os

class Bundler(Chain.StageBase):
    
    BUNDLER_MAP = {"Initial Focal Length"                 :"init_focal_length",
                   "Variable Focal Length"                :"variable_focal_length",
                   "Fixed Focal Length"                   :"fixed_focal_length",
                   "Use Focal Length Estimate"            :"use_focal_estimate",
                   "Trust Focal Estimate"                 :"trust_focal_estimate",
                   "Constrain Focal"                      :"constrain_focal",
                   "Constrain Focal Weight"               :"constrain_focal_weight",
                   "Fisheye Parameters"                   :"fisheye",
                   "Seed Image Index 1"                   :"init_pair1",
                   "Seed Image Index 2"                   :"init_pair2",
                   "Estimate Radial Distortion"           :"estimate_distortion",
                   "Ray Angle Threshold"                  :"ray_angle_threshold",
                   "Projection Estimation Threshold"      :"projection_estimation_threshold",
                   "Minimum Projection Error Threshold"   :"min_proj_error_threshold",
                   "Maximum Projection Error Threshold"   :"max_proj_error_threshold",
                   "Previous Bundler Results File"        :"bundle",
                   "Run Slow Bundler"                     :"slow_bundle"}

    def __init__(self, inputStages=None,
                 initialFocalLength=Common.Utility.InvalidFloat(),
                 variableFocalLength=True,
                 fixedFocalLength=False,
                 useFocalLengthEstimate=True,
                 trustFocalLengthEstimate=False,
                 constrainFocalLength=True,
                 constrainFocalLengthWeight=0.0001,
                 fisheyeParameterFile=Common.Utility.InvalidString(),
                 seedImageIndex1=Common.Utility.InvalidInt(),
                 seedImageIndex2=Common.Utility.InvalidInt(),
                 estimateRadialDistortion=True,
                 rayAngleThreshold=2,
                 projectionEstimationThreshold=4,
                 minimumProjectionErrorThreshold=8,
                 maximumProjectionErrorThreshold=16,
                 previousBundlerResultsFile=Common.Utility.InvalidString(),
                 runSlowBundler=False,
                 forceRun=False):
        
        Chain.StageBase.__init__(self,
                                 inputStages,
                                 "Performs bundle adjustment on the given images",
                                 {"Initial Focal Length"                :"Initial focal length",
                                  "Variable Focal Length"               :"Use variable focal length",
                                  "Fixed Focal Length"                  :"Use fixed focal length (Initial Focal Length)",
                                  "Use Focal Length Estimate"           :"Initialize using focal length estimates specified in the list file",
                                  "Trust Focal Estimate"                :"Trust the provided focal length estimates (i.e., don't attempt to cross-check with self-calibration)",
                                  "Constrain Focal"                     :"Add a soft constraint on focal lengths to stay near their estimated values",
                                  "Constrain Focal Weight"              :"Strength of the focal length constraints",
                                  "Fisheye Parameter File"              :"Fisheye parameter file path",
                                  "Seed Image Index 1"                  :"First image index to seed bundle adjustment",
                                  "Seed Image Index 2"                  :"Second image index to seed bundle adjustment",
                                  "Estimate Radial Distortion"          :"Whether to estimate radial distortion parameters",
                                  "Ray Angle Threshold"                 :"Triangulation ray angle threshold",
                                  "Projection Estimation Threshold"     :"RANSAC threshold when performing pose estimation to add in a new image",
                                  "Minimum Projection Error Threshold"  :"The minimum value of the adaptive outlier threshold",
                                  "Maximum Projection Error Threshold"  :"The maximum value of the adaptive outlier threshold",
                                  "Previous Bundler Results File"       :"Previous bundle adjustment results file path",
                                  "Run Slow Bundler"                    :"Run slow bundle adjustment (adds one image at a time)",
                                  "Force Run"                           :"Force run if outputs already exist"})
        
        self._properties["Initial Focal Length"]                = initialFocalLength
        self._properties["Variable Focal Length"]               = variableFocalLength
        self._properties["Fixed Focal Length"]                  = fixedFocalLength
        self._properties["Use Focal Length Estimate"]           = useFocalLengthEstimate
        self._properties["Trust Focal Estimate"]                = trustFocalLengthEstimate
        self._properties["Constrain Focal"]                     = constrainFocalLength
        self._properties["Constrain Focal Weight"]              = constrainFocalLengthWeight
        self._properties["Fisheye Parameter File"]              = fisheyeParameterFile
        self._properties["Seed Image Index 1"]                  = seedImageIndex1
        self._properties["Seed Image Index 2"]                  = seedImageIndex2
        self._properties["Estimate Radial Distortion"]          = estimateRadialDistortion
        self._properties["Ray Angle Threshold"]                 = rayAngleThreshold
        self._properties["Projection Estimation Threshold"]     = projectionEstimationThreshold
        self._properties["Minimum Projection Error Threshold"]  = minimumProjectionErrorThreshold
        self._properties["Maximum Projection Error Threshold"]  = maximumProjectionErrorThreshold
        self._properties["Previous Bundler Results File"]       = previousBundlerResultsFile
        self._properties["Run Slow Bundler"]                    = runSlowBundler
        self._properties["Force Run"]                           = forceRun
        
    
    def GetInputInterface(self):
        return {"keyMatches":(0,FeatureMatch.KeyMatches),
                "images":(1,Common.sfmImages)}
    
    def GetOutputInterface(self):
        return {"bundleFile":BundleAdjustment.BundleFile}
#    TODO: add the following file outputs
#        - constraints.txt
#        - matches.corresp.txt
#        - matches.prune.txt
#        - matches.ransac.txt
#        - nmatches.corresp.txt
#        - nmatches.prune.txt
#        - nmatches.ransac.txt
#        - pairwise_scores.txt

    def WriteBundlerOptionsFile(self, bundlerFile, matchesFile, bundlerOutputFile):
        
        f = open(bundlerFile,"w")
        
        # standard options
        f.write("--match_table %s\n" % (matchesFile))
        f.write("--output %s\n" % (bundlerOutputFile))
        f.write("--output_all bundle_\n")
        f.write("--output_dir bundle\n")
        
        # options based on stage properties
        for propName in self._properties.keys():
            if (propName=="Force Run"):continue
            
            if (self._properties[propName] != None):
                
                if (isinstance(self._properties[propName],bool)):
                    if (self._properties[propName] == True):
                        f.write("--%s\n" % Bundler.BUNDLER_MAP[propName])
                
                elif (isinstance(self._properties[propName],int)   or
                      isinstance(self._properties[propName],float) or
                      isinstance(self._properties[propName],str)):
                    
                    if ((isinstance(self._properties[propName],int) and self._properties[propName]!=Common.Utility.InvalidInt())  or
                        (isinstance(self._properties[propName],float) and self._properties[propName]!=Common.Utility.InvalidFloat()) or
                        (isinstance(self._properties[propName],str) and self._properties[propName]!=Common.Utility.InvalidString())):
                        f.write("--%s %s\n" % (Bundler.BUNDLER_MAP[propName], str(self._properties[propName])))
                    
                else:
                    raise Exception("Unhandled property %s: %s" % \
                                    (propName, str(type(self._properties[propName]))))
        
        
        # choose either previous or new bundler run            
        if (self._properties["Previous Bundler Results File"] != ""):
            f.write("--rerun_bundle\n")
        else:
            f.write("--run_bundle\n")
        
        f.close()
        
        
    def Execute(self):
        matchesFilePath = self.GetInputStageValue(0, "keyMatches").GetPath()
        images = self.GetInputStageValue(1, "images")
        
        self.StartProcess()
        
        bundlerOptionsFilePath = os.path.join(images.GetPath(), "bundlerOptions.txt")
        bundlerOutputPath = os.path.join(images.GetPath(), "bundle")
        bundlerOutputFilePath = os.path.join(bundlerOutputPath, "bundler.out")
        
        if (Common.Utility.ShouldRun(self._properties["Force Run"],
                                     bundlerOptionsFilePath,bundlerOutputPath,bundlerOutputFilePath)):
            
            images.WriteFileList()
            Common.Utility.MakeDir(bundlerOutputPath)
            self.WriteBundlerOptionsFile(bundlerOptionsFilePath, os.path.split(matchesFilePath)[1], "bundler.out")
            
            self.RunCommand("bundler", 
                            Common.Utility.CommandArgs(Common.Utility.Quoted(images.GetImageListPath()),
                                                       "--options_file",
                                                       Common.Utility.Quoted(bundlerOptionsFilePath)),
                            cwd = os.path.split(images.GetImageListPath())[0])
        
        bundleFile = BundleAdjustment.BundleFile(bundlerOutputFilePath, images.GetImages())
        
        self.SetOutputValue("bundleFile", bundleFile)
        
        


