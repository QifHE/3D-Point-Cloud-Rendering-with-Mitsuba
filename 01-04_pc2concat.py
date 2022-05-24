import os
import sys

import mitsuba
import numpy as np
import open3d as o3d
from tqdm import tqdm
import cv2

### SET VARIABLES HERE ###
mitsuba.set_variant('scalar_rgb')   # set this before importing!
from mitsuba.core import Bitmap, Struct, Thread
from mitsuba.core.xml import load_file

pc_data_dir = "../mitsubaRenders/pc_files"  # Must! original point cloud (pc) files
point_number = 2048             # Important! Make sure that all pc shapes have the same point number

categories = []                 # categories that you wish to render, set [] to render all categories
png_dir = "../mitsubaRenders/png_files"     # PNG file directary, '' will use the original directary

concat_output_dir = "../mitsubaRenders/concat_files"  # final image directary, '' will use the original directary 
img_name = "output"                  # Must! image name

concat_direction = "v"               # Must! 'v' for vertical, 'h' for horizontal
adaptive_size = True                # if True, all img will resize according to the minimum width/height within the image list
compress2jpg = True                 # if True, perform lossy compression to jepg format
jpg_quality = 85

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
            <integer name="width" value="800"/>
            <integer name="height" value="600"/>
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

def mitsuba_render(filename, output_path):

    # Add the scene directory to the FileResolver's search path
    Thread.thread().file_resolver().append(os.path.dirname(filename))

    # Load the actual scene
    scene = load_file(filename)

    # Call the scene's integrator to render the loaded scene
    scene.integrator().render(scene, scene.sensors()[0])

    # After rendering, the rendered data is stored in the film
    film = scene.sensors()[0].film()

    # Write out rendering as high dynamic range OpenEXR file
    exr_temp = output_path.replace(".png",".exr")
    film.set_destination_file(exr_temp)
    film.develop()

    # Write out a tonemapped PNG of the same rendering
    bmp = film.bitmap(raw=True)
    bmp.convert(Bitmap.PixelFormat.RGB, Struct.Type.UInt8, srgb_gamma=True).write(output_path)
    os.remove(exr_temp)

# define a function for horizontally
# concatenating images of different
# heights
def hconcat_resize(img_list,
				interpolation
				= cv2.INTER_CUBIC):
	# take minimum hights
	h_min = min(img.shape[0]
				for img in img_list)
	
	# image resizing
	im_list_resize = [cv2.resize(img,
					(int(img.shape[1] * h_min / img.shape[0]),
						h_min), interpolation
								= interpolation)
					for img in img_list]
	
	# return final image
	return cv2.hconcat(im_list_resize)


# define a function for vertically
# concatenating images of different
# widths
def vconcat_resize(img_list, interpolation
				= cv2.INTER_CUBIC):
    img_list = [cv2.imread(img) for img in img_list]
	# take minimum width
    w_min = min(img.shape[1] for img in img_list)
	
	# resizing images
    im_list_resize = [cv2.resize(img,
					(w_min, int(img.shape[0] * w_min / img.shape[1])),
								interpolation = interpolation)
					for img in img_list]
	# return final image
    return cv2.vconcat(im_list_resize)

### MAIN ###
if __name__ == '__main__':

    pc_files = []
    png_files = []

    print("--- Point Cloud to XML ---")

    # walk through all point cloud files
    for root, dirs, files in os.walk(pc_data_dir, topdown=False):
        if root.split("/")[-1] in categories or not categories:  # check category
            for name in files:
                if check_format(name):  # check extension
                    pc_files.append(os.path.join(root, name))

    print("--- XML to PNG ---")
    for pc_file in tqdm(pc_files):
        pts = o3d.io.read_point_cloud(pc_file)
        pts = np.asarray(pts.points)

        if not png_dir:
            # use the original directory then
            xml_path = pc_file.replace(check_format(pc_file), "xml")
        else:
            # create seperate category directories and store the files
            cat = pc_file.split("/")[-2]
            cat_dir = xml_path = os.path.join(png_dir, cat)
            if not os.path.exists(cat_dir):
                os.makedirs(cat_dir)

            pc_file = pc_file.replace(check_format(pc_file), "xml")
            xml_path = os.path.join(png_dir, "/".join(pc_file.split("/")[-2:]))
            
        write_xml(pts, xml_path)
        mitsuba_render(xml_path, xml_path.replace(".xml",".png"))
        os.remove(xml_path)
        png_files.append(xml_path.replace(".xml",".png"))


    print("--- Image Concatenation ---")
    if not concat_output_dir:
        concat_output_dir = png_dir

    if not os.path.exists(concat_output_dir):
        os.makedirs(concat_output_dir)

    format = ".jpg" if compress2jpg else ".png"
    img_output = os.path.join(concat_output_dir, img_name + format)

    if concat_direction == "v":
        if adaptive_size:
            if compress2jpg:
                cv2.imwrite(img_output, vconcat_resize(png_files), [int(cv2.IMWRITE_JPEG_QUALITY), int(jpg_quality)])
            else:
                cv2.imwrite(img_output, vconcat_resize(png_files))
        else:
            if compress2jpg:
                cv2.imwrite(img_output, cv2.vconcat(png_files), [int(cv2.IMWRITE_JPEG_QUALITY), int(jpg_quality)])
            else:
                cv2.imwrite(img_output, cv2.vconcat(png_files))
    elif concat_direction == "h":
        if adaptive_size:
            if compress2jpg:
                cv2.imwrite(img_output, hconcat_resize(png_files), [int(cv2.IMWRITE_JPEG_QUALITY), int(jpg_quality)])
            else:
                cv2.imwrite(img_output, hconcat_resize(png_files))
        else:
            if compress2jpg:
                cv2.imwrite(img_output, cv2.hconcat(png_files), [int(cv2.IMWRITE_JPEG_QUALITY), int(jpg_quality)])
            else:
                cv2.imwrite(img_output, cv2.hconcat(png_files))