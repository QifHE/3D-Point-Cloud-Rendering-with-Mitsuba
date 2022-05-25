# 3D Point Cloud Rendering with Mitsuba and Batch Processing

## May 24th, 2022 updated with brand-new pipeline design!
<img src="https://github.com/QifHE/3D-Point-Cloud-Rendering-with-Mitsuba/blob/main/imgs/RenderingPipeline.png?raw=true" style="width:100%"/>

## NEW README.MD IS BEING WRITTEN! COMING SOON!


## Introduction

This repository provides a tool that automatically renders all of your selected point cloud files into visually stunning images by using Mitsuba2. You can simply input one-line command, and then the code will generate all images, before concatenating them into a single image which will be suitable to be put in your academic papers. Moreover, each submodule of the tool can be used independently to deal with corresponding tasks. 

## Acknowledgement

This repository has borrowed and modified some code from the following work. You can refer to their homepage for more details.

 - [Mitsuba Renderer 2](https://github.com/mitsuba-renderer/mitsuba2)
 - [AnTao97/PointCloudDatasets](https://github.com/AnTao97/PointCloudDatasets/blob/master/visualize.py)
 - [PointFlowRenderer](https://github.com/zekunhao1995/PointFlowRenderer)
 - [xchhuang/PointFlowRenderer-mitsuba2](https://github.com/xchhuang/PointFlowRenderer-mitsuba2/blob/master/exr2png.py)
 - [Concatenate images using OpenCV in Python](https://www.geeksforgeeks.org/concatenate-images-using-opencv-in-python/)

Other Similar Project:
 - [tolgabirdal/Mitsuba2PointCloudRenderer](https://github.com/tolgabirdal/Mitsuba2PointCloudRenderer)

## Tested Environment

 - Ubuntu 20.04
 - Python 3.9
 - Anaconda 4.10.3

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

 - [Linux(in writing)]()
 - [Windows](https://github.com/QifHE/3D-Point-Cloud-Rendering-with-Mitsuba/tree/main/Redacted)
 
 Do notice that the Windows version of this repo is redacted, and not compatible with the new version.

## Usage Guidance
### 01_pc2xml.py
### 02_xml2exr.py
### 03_exr2png.py
### 04_pngConcat.py