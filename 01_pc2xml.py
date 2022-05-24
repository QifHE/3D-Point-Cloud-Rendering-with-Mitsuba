import os
import sys

import numpy as np
import open3d as o3d
from tqdm import tqdm

### SET VARIABLES HERE ###

pc_data_dir = "../mitsubaRenders/pc_files"   # Must! original point cloud (pc) files
categories = []                 # categories that you wish to render, set [] to render all categories
xml_dir = ""                  # directory that will contain the scene XML files, set '' will generate the XML under the path of corresponding pc files
point_number = 2048               # Important! Make sure that all pc shapes have the same point number

''' #Examples:
pc_data_dir = "../mitsubaRenders/pc_files"
categories = ["airplane","bag"] 
xml_dir = "../mitsubaRenders/xml_files"
point_number = 2048 
'''


### XML PARAMETERS ###
# Modify the scene parameters in this section
# xml_head: camera, sampler, film, texture
# xml_ball_segment: point mesh balls
# xml_tail: lighting

xml_head = \
"""
<scene version="0.5.0">
    <integrator type="path">
        <integer name="maxDepth" value="-1"/>
    </integrator>
    <sensor type="perspective">
        <float name="farClip" value="100"/>
        <float name="nearClip" value="0.1"/>
        <transform name="toWorld">
            <translate x="0" y="0" z="0"/>
            <rotate x="0" y="0" z="0" angle="0"/>
            <lookat origin="2.5,2.5,2.5" target="0,0,0" up="0,0,1"/>
        </transform>
        <float name="fov" value="25"/>
        
        <sampler type="ldsampler">
            <integer name="sampleCount" value="256"/>
        </sampler>
        <film type="hdrfilm">
            <integer name="width" value="1600"/>
            <integer name="height" value="1200"/>
            <rfilter type="gaussian"/>
            <boolean name="banner" value="false"/>
        </film>
    </sensor>
    
    <bsdf type="roughplastic" id="surfaceMaterial">
        <string name="distribution" value="ggx"/>
        <float name="alpha" value="0.05"/>
        <float name="intIOR" value="1.46"/>
        <rgb name="diffuseReflectance" value="1,1,1"/> <!-- default 0.5 -->
    </bsdf>
    
"""

xml_ball_segment = \
"""
    <shape type="sphere">
        <float name="radius" value="0.02"/>
        <transform name="toWorld">
            <translate x="{}" y="{}" z="{}"/>
            <scale value="0.7"/>
        </transform>
        <bsdf type="diffuse">
            <rgb name="reflectance" value="{},{},{}"/>
        </bsdf>
    </shape>
"""

xml_tail = \
"""
    <shape type="rectangle">
        <ref name="bsdf" id="surfaceMaterial"/>
        <transform name="toWorld">
            <scale x="10" y="10" z="10"/>
            <translate x="0" y="0" z="-0.5"/>
        </transform>
    </shape>
    
    <shape type="rectangle">
        <transform name="toWorld">
            <scale x="10" y="10" z="1"/>
            <lookat origin="-4,4,20" target="0,0,0" up="0,0,1"/>
        </transform>
        <emitter type="area">
            <rgb name="radiance" value="6,6,6"/>
        </emitter>
    </shape>
</scene>
"""


### FUNCTIONS ###

def standardize_bbox(pcl, points_per_object):
    pt_indices = np.random.choice(pcl.shape[0], points_per_object, replace=False)
    np.random.shuffle(pt_indices)
    pcl = pcl[pt_indices] # n by 3
    mins = np.amin(pcl, axis=0)
    maxs = np.amax(pcl, axis=0)
    center = ( mins + maxs ) / 2.
    scale = np.amax(maxs-mins)
    #print("Center: {}, Scale: {}".format(center, scale))
    result = ((pcl - center)/scale).astype(np.float32) # [-0.5, 0.5]
    return result

def colormap(x,y,z):
    '''
    Custom your color here
    '''
    vec = np.array([x,y,z])
    vec = np.clip(vec, 0.001,1.0)
    norm = np.sqrt(np.sum(vec**2))
    vec /= norm
    return [vec[0], vec[1], vec[2]] # (R,G,B)∈[0,1]

def write_xml(pcl, path, clr=None):
    xml_segments = [xml_head]

    pcl = standardize_bbox(pcl, point_number)
    pcl = pcl[:,[2,0,1]]        # put the pc shape on the ground
    
    # Rotations
    theta_X = np.radians(0) 
    theta_Y = np.radians(0) 
    theta_Z = np.radians(0) 
    
    translation_X = np.array([[1,0,0],
                 [0, np.cos(theta_X), -np.sin(theta_X)],
                 [0, np.sin(theta_X), np.cos(theta_X)]])
    
    translation_Y = np.array([[np.cos(theta_Y),0,np.sin(theta_Y)],
                 [0,1,0],
                 [-np.sin(theta_Y),0,np.cos(theta_Y)]])
    
    
    translation_Z = np.array([[np.cos(theta_Z), -np.sin(theta_Z), 0],
                 [np.sin(theta_Z), np.cos(theta_Z), 0,],
                 [0, 0, 1]])
    
    pcl = pcl.transpose(1,0)
    pcl = np.dot(translation_X, pcl)
    pcl = np.dot(translation_Y, pcl)
    pcl = np.dot(translation_Z, pcl) 
    pcl = pcl.transpose(1,0)
    
    # Flipping
    pcl[:, 0] *= 1
    pcl[:, 1] *= 1
    pcl[:, 2] *= 1
    
    h = np.min(pcl[:,2])

    # Colorization
    for i in range(pcl.shape[0]):
        if clr == None:
            color = colormap(pcl[i,0]+0.5,pcl[i,1]+0.5,pcl[i,2]+0.5)
        else: 
            color = clr
        if h < -0.25:
            xml_segments.append(xml_ball_segment.format(pcl[i,0],pcl[i,1],pcl[i,2]-h-0.6875, *color))
        else:
            xml_segments.append(xml_ball_segment.format(pcl[i,0],pcl[i,1],pcl[i,2], *color))
    xml_segments.append(xml_tail)

    xml_content = str.join('', xml_segments)

    with open(path, 'w') as f:
        f.write(xml_content)

def check_format(pc):
    accept_format = ["xyz","ply","pts","pcd"]
    pc_format = pc.split(".")[-1]
    if pc_format in accept_format:
        return pc_format
    else:
        print("Format not acceptable by open3d. Only accept the following format: ")
        print(accept_format)
        sys.exit()


### MAIN ###
if __name__ == '__main__':

    pc_files = []

    print("Point Cloud to XML")
    print("Selected Categories ('None' for all): ")
    print(categories)

    # walk through all point cloud files
    for root, dirs, files in os.walk(pc_data_dir, topdown=False):
        if root.split("/")[-1] in categories or not categories:  # check category
            for name in files:
                if check_format(name):  # check extension
                    pc_files.append(os.path.join(root, name))

    print("Generating XML files:")
    for pc_file in tqdm(pc_files):
        pts = o3d.io.read_point_cloud(pc_file)
        pts = np.asarray(pts.points)

        if not xml_dir:
            # use the original directory then
            path = pc_file.replace(check_format(pc_file), "xml")
        else:
            # create seperate category directories and store the files
            cat = pc_file.split("/")[-2]
            cat_dir = path = os.path.join(xml_dir, cat)
            if not os.path.exists(cat_dir):
                os.makedirs(cat_dir)

            pc_file = pc_file.replace(check_format(pc_file), "xml")
            path = os.path.join(xml_dir, "/".join(pc_file.split("/")[-2:]))
            
        write_xml(pts, path)


    
