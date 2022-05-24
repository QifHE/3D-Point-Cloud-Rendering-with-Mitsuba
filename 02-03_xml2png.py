import os
import sys

import mitsuba
import numpy as np
import open3d as o3d
from tqdm import tqdm

### SET VARIABLES HERE ###
mitsuba.set_variant('scalar_rgb')   # set this before importing!
from mitsuba.core import Bitmap, Struct, Thread
from mitsuba.core.xml import load_file

categories = []  # categories that you wish to render, set [] to to deal with all categories
xml_dir = ""    #  XML file directary, '' will use the original directary  
png_dir = ""    #  PNG file directary, '' will use the original directary  

''' # Examples:
categories = ["airplane","bag"]
xml_dir = "../mitsubaRenders/xml_files"
png_dir = "../mitsubaRenders/png_files"
'''

### FUNCTIONS ###

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




### MAIN ###
if __name__ == "__main__":

    png_files = []

    print("XML to PNG")
    print("Selected Categories ('None' for all): ")
    print(categories)

    for root, dirs, files in os.walk(xml_dir, topdown=False):
        if root.split("/")[-1] in categories or not categories:
            for name in files:
                if name.endswith(".xml"):
                    png_files.append(os.path.join(root, name))

    print("Rendering PNG Images:")
    i = 0
    for png_file in tqdm(png_files):
        i += 1
        if not png_dir:
            png_path = png_file.replace(".xml",".png")
        else:
            cat = png_file.split("/")[-2]
            cat_dir = path = os.path.join(png_dir, cat)
            if not os.path.exists(cat_dir):
                os.makedirs(cat_dir)

            file = png_file.replace(".xml",".png")
            png_path = os.path.join(png_dir, "/".join(file.split("/")[-2:]))
        
        print("Rendering: {} / {}".format(i, len(png_files)))
        mitsuba_render(png_file, png_path)
