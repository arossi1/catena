## Overview ##

Catena is a generalized workflow framework developed in Python.  Initial applications have been developed in the areas of structure from motion (SfM), computer vision, and image processing.

## Quick Start ##

Checkout / export the source: http://code.google.com/p/catena/source/checkout

Running the **unitTest.py** script in the Testing package will determine whether all the SfM stages are operating correctly on your system.  It can be executed from the **code** directory using the following command:

```
python Testing\unitTest.py
```

There are other scripts in the Testing directory that demonstrate how to programmatically build a chain and use the features of Catena:

  * **sfm.py**: basic SfM chain
  * **sfmOpenCV.py**: basic SfM chain using OpenCV feature extraction & matching
  * **sfmChainGUI.py**: basic SfM chain using _ChainGUI_ visualization tool
  * **persistence.py**: demonstrates persist/restore capability
  * **asift.py**: SfM chain using the ASIFT feature extractor and matcher
  * **tapPoint.py**: illustrates use of _Common.TapPoint_ stage
  * **exampleImageProcessStageBase.py**: illustrates use of _Common.ImageProcessStageBase_ class

The Chain Builder GUI can be utilized for graphical chain building.  Execute **ChainBuilder.py** from the root source directory.

```
python Visualization\ChainBuilder.py
```

## Documentation ##

Please refer to the [IEEE paper](http://catena.googlecode.com/svn/trunk/doc/Catena.pdf) for a high level overview of Catena.

The [programmer's guide](http://catena.googlecode.com/svn/trunk/doc/CatenaProgrammersGuide.pdf) provides further detail of the framework.

The Catena [charts](http://catena.googlecode.com/svn/trunk/doc/Catena%20-%2020121112%20-%20WNYIPW.pdf) from the WNYIPW2012 conference provides a presentation-level overview.

[Doxygen](http://catena.googlecode.com/svn/trunk/doc/Catena.chm) was used to digest the source (download locally before opening).

## Components ##
The following components have been built and included with the Catena distribution.  Please consult the respective project for licensing terms.

| **Name** | **Version** | **Associated Stage** | **Website** | **Description** |
|:---------|:------------|:---------------------|:------------|:----------------|
| Bundler| v0.4 <br> (4/10/2010) <table><thead><th> BundleAdjustment.Bundler </th><th> <a href='http://www.cs.cornell.edu/~snavely/bundler/'>http://www.cs.cornell.edu/~snavely/bundler/</a> </th><th> Accepts an unordered collection of images and generates a sparse point cloud, camera matrices, and other artifacts of SfM via a bundle adjustment process </th></thead><tbody>
<tr><td> CMVS </td><td> Fix2 <br> (3/27/2011) </td><td> Cluster.CMVS </td><td> <a href='http://www.di.ens.fr/cmvs/'>http://www.di.ens.fr/cmvs/</a> </td><td> Takes the output of SfM software (such as Bundler) and decomposes the input images into a set of image clusters of manageable size </td></tr>
<tr><td> PMVS </td><td> Fix0 <br> (7/13/2010) </td><td> Cluster.PMVS </td><td> <a href='http://www.di.ens.fr/pmvs/'>http://www.di.ens.fr/pmvs/</a> </td><td> Multi-view stereo software that takes a set of images and camera parameters, then reconstructs 3D structure of an object or a scene visible in the images, generating a dense point cloud </td></tr>
<tr><td> jhead </td><td> v2.90 <br> (2/5/2010) </td><td>  Common.jhead </td><td> <a href='http://www.sentex.net/~mwandel/jhead/'>http://www.sentex.net/~mwandel/jhead/</a> </td><td>Extracts EXIF metadata from JPEG images </td></tr>
<tr><td> ASIFT </td><td> v2.1.2 <br> (01/09/2010) </td><td> FeatureExtraction.ASIFT <br> FeatureMatch.ASIFTMatch </td><td> <a href='http://www.cmap.polytechnique.fr/~yu/research/ASIFT/demo.html'>http://www.cmap.polytechnique.fr/~yu/research/ASIFT/demo.html</a> <br> <a href='http://www.ipol.im/pub/art/2011/my-asift/'>http://www.ipol.im/pub/art/2011/my-asift/</a> </td><td> A fully affine-invariant image comparison method </td></tr>
<tr><td> Daisy </td><td> v1.8.1 <br> (10/11/2009) </td><td> FeatureExtraction.Daisy </td><td> <a href='http://cvlab.epfl.ch/software/daisy'>http://cvlab.epfl.ch/software/daisy</a> </td><td> A fast local descriptor for dense matching </td></tr>
<tr><td> SIFT <br> (SiftWin32) </td><td> v4.0 <br> (7/2005) </td><td> FeatureExtraction.Sift </td><td> <a href='http://www.cs.ubc.ca/~lowe/keypoints/'>http://www.cs.ubc.ca/~lowe/keypoints/</a> </td><td> Lowe's reference implementation of the Scale-Invariant Feature Transform </td></tr>
<tr><td> SIFT <br> (SiftHess) </td><td> abf933aa73 </td><td> FeatureExtraction.Sift </td><td> <a href='http://robwhess.github.io/opensift/'>http://robwhess.github.io/opensift/</a> </td><td> Rob Hess's OpenCV implementation of SIFT </td></tr>
<tr><td> SIFT <br> (SiftGPU) </td><td> v400 </td><td> FeatureExtraction.Sift </td><td> <a href='http://cs.unc.edu/~ccwu/siftgpu/'>http://cs.unc.edu/~ccwu/siftgpu/</a> </td><td> GPU implementation of SIFT </td></tr>
<tr><td> SIFT <br> (VLFeat) </td><td> v0.9.17 </td><td> FeatureExtraction.Sift </td><td> <a href='http://www.vlfeat.org/'>http://www.vlfeat.org/</a> </td><td> VLFeat implementation of SIFT </td></tr>
<tr><td> SURF <br> (OpenCV) </td><td> variable, tested with v2.4.7.0 </td><td> FeatureExtraction.Surf </td><td> <a href='http://docs.opencv.org/modules/nonfree/doc/feature_detection.html'>http://docs.opencv.org/modules/nonfree/doc/feature_detection.html</a> </td><td> Speeded Up Robust Features, OpenCV implementation via Python bindings </td></tr>
<tr><td> Keymatch <br> (KeyMatchFull) </td><td> v0.4 <br> (4/10/2010) </td><td> FeatureMatch.KeyMatch </td><td> <a href='http://www.cs.cornell.edu/~snavely/bundler/'>http://www.cs.cornell.edu/~snavely/bundler/</a> </td><td> Keymatch implementation included in Bundler software </td></tr>
<tr><td> Keymatch <br> (KeyMatchGPU) </td><td> v400 </td><td> FeatureMatch.KeyMatch </td><td> <a href='http://cs.unc.edu/~ccwu/siftgpu/'>http://cs.unc.edu/~ccwu/siftgpu/</a> </td><td> GPU implementation of key matching </td></tr></tbody></table>


<a href='Hidden comment: 
==News==
==History==
==Releases==
'></a><br>
<br>
<br>
<h2>License</h2>

The software is open source under GNU Public License (GPL). If the viral nature of GPL is not suitable for your deployment, an alternative commercial license is available. In particular, the alternative commercial license allows you to combine pieces of our software with your other proprietary elements.  Contact the owner for more details.<br>
<br>
<h2>Links</h2>
Also refer to <a href='http://code.google.com/p/osm-bundler/'>OSM</a>, as there exists some overlap with respect to the SfM application.