# 3D Point Cloud Rendering with Mitsuba and Batch Processing

## May 24th, 2022 updated with brand-new pipeline design!
<img src="https://github.com/QifHE/3D-Point-Cloud-Rendering-with-Mitsuba/blob/main/imgs/RenderingPipeline.png?raw=true" style="width:100%"/>

## Introduction

This repository provides a tool that automatically renders all of your selected point cloud files into visually stunning images by using Mitsuba2. You can simply input one-line command, and then the code will generate all images, before concatenating them into a single image which will be suitable to be put in your academic papers. Moreover, each submodule of the tool can be used independently to deal with corresponding tasks. 

---

## Acknowledgement

This repository has borrowed and modified some code from the following work. You can refer to their homepage for more details.

 - [Mitsuba Renderer 2](https://github.com/mitsuba-renderer/mitsuba2)
 - [AnTao97/PointCloudDatasets](https://github.com/AnTao97/PointCloudDatasets/blob/master/visualize.py)
 - [PointFlowRenderer](https://github.com/zekunhao1995/PointFlowRenderer)
 - [xchhuang/PointFlowRenderer-mitsuba2](https://github.com/xchhuang/PointFlowRenderer-mitsuba2/blob/master/exr2png.py)
 - [Concatenate images using OpenCV in Python](https://www.geeksforgeeks.org/concatenate-images-using-opencv-in-python/)

Other Similar Project:
 - [tolgabirdal/Mitsuba2PointCloudRenderer](https://github.com/tolgabirdal/Mitsuba2PointCloudRenderer)

---

## Tested Environment

 - Ubuntu 20.04
 - Python 3.9
 - Anaconda 4.10.3

---

## Prerequisite
 - Mitsuba 2
 - Python 3.x
 - open3d
 - opencv-python
 - tqdm

 To intall the above packages:
 
 ```
 pip install -r requirements.txt
 ```
**[Important!] Mitsuba 2 Installation Guide**

 - [Linux](https://mitsuba2.readthedocs.io/en/latest/src/getting_started/compiling.html)
 
 About Linux version:

 > You might encounter the "syntax" error when running "setpath.sh" file. Do the following:
 ```
 pip install dos2unix
 dos2unix -do *
 ``` 
 > The GPU Variant fails to run on my setting. The problem has not being soloved yet, and you can refer to this [issue](https://github.com/mitsuba-renderer/mitsuba2/issues/565). Additionally, the GPU usage is very low and cannot render large images. Thus, I recommend you to install the default CPU variant.

 - [Windows](https://github.com/QifHE/3D-Point-Cloud-Rendering-with-Mitsuba/tree/main/Redacted)
 
  > Do notice that the Windows version of this repo is redacted, which is not compatible with the new version.

---

## Usage Guidance
### Set Variables
If you want to run any of the scripts, please set the variables within the code please (or else the code will not know where your point cloud files are).

Within each python script, you can find the **"SET VARIABLE HERE"** section. Modify the default values during this section.(I didn't use argparser because I'm lazy.) What you might encounter are as follows:
```python
### SET VARIABLES HERE ###
pc_data_dir = "../mitsubaRenders/pc_files"   # Must! original point cloud (pc) files
categories = []                 # categories that you wish to render, set [] to render all categories
xml_dir = ""                  # directory that will contain the scene XML files, set '' will generate the XML under the path of corresponding pc files
point_number = 2048             # Important! Make sure that all pc shapes have the same point number            
categories = []                 # categories that you wish to render, set [] to render all categories

png_dir = "../mitsubaRenders/png_files"     # PNG file directary, '' will use the original directary
concat_output_dir = "../mitsubaRenders/concat_files" # final image directary, '' will use the original directary 
img_name = "output"                # Must! image name

concat_direction = "v"               # Must! 'v' for vertical, 'h' for horizontal
adaptive_size = True                # if True, all img will resize according to the minimum width/height within the image list
compress2jpg = True                 # if True, perform lossy compression to jepg format
jpg_quality = 85
```
### Point Cloud File Directary Stucture

If you want to only process the **selected categories**, the code will assume that your Point Cloud File Directary Stucture look similar to this:
```
Dataset Root
└───airplane
│   │   pc1.ply
│   │   pc2.ply
  
└───bag
    │   pc1.ply
    │   pc2.ply
...
```

### Start Mitsuba 2
Go to your Mitsuba root directary, and
```
source setpath.sh
```


### Run Scripts

### 01_pc2xml.py
 > Go through all of your selected point cloud files and generate corresponding Mitsuba Scene XML file.
```
python 01_pc2xml.py
```
### 02_xml2exr.py
 > Go through all of your selected Mitsuba Scene XML file and render.

```
python 02_xml2exr.py
```
### 03_exr2png.py
 > Convert selected OpenEXR images to PNG format.
```
python 03_exr2png.py
```
### 04_pngConcat.py
 > Concatenate selected PNG images.
```
python 04_pngConcat.py
```
---

## One command to run them all!
### 01-03_pc2png.py
 > Go through all of your selected point cloud files and give you rendered PNG images. Note that this script uses Mitsuba's API to convert EXR to PNG, which will theorectically give a more accurate conversion.
```
python 01-03_pc2png.py
```
### 02-03_xml2png.py
 > Go through all of your selected XML files and give you rendered PNG images.
```
python 01-03_pc2png.py
```
### 01-04_pc2concat.py
 > **RECOMMEND!** Go through all of your selected point cloud files and give you a concatenated image representing them all!
```
python 01-04_pc2concat.py
```