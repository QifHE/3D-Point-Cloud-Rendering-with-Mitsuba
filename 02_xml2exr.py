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

categories = []  # categories that you wish to render, set [] to render all categories
xml_dir = ""   # XML file directary, '' will use the original directary    
exr_dir = ""   # EXR file directary, '' will use the original directary  

''' # Example:
categories = ["airplane","bag"]
xml_dir = "../mitsubaRenders/xml_files"
exr_dir = "../mitsubaRenders/exr_files"
'''

### FUNCTIONS ###

def mitsuba_render(input_path, output_path):

    # Add the scene directory to the FileResolver's search path
    Thread.thread().file_resolver().append(os.path.dirname(input_path))

    # Load the actual scene
    scene = load_file(input_path)

    # Call the scene's integrator to render the loaded scene
    scene.integrator().render(scene, scene.sensors()[0])

    # After rendering, the rendered data is stored in the film
    film = scene.sensors()[0].film()

    # Write out rendering as high dynamic range OpenEXR file
    film.set_destination_file(output_path)
    film.develop()


### MAIN ###
if __name__ == "__main__":

    xml_files = []

    print("XML to OpenEXR")
    print("Selected Categories ('None' for all): ")
    print(categories)

    for root, dirs, files in os.walk(xml_dir, topdown=False):
        if root.split("/")[-1] in categories or not categories:
            for name in files:
                if name.endswith(".xml"):
                    xml_files.append(os.path.join(root, name))

    print("Rendering EXR Images:")
    i = 0
    for xml_file in tqdm(xml_files):
        i += 1
        if not exr_dir:
            exr_path = xml_file.replace(".xml",".exr")
        else:
            cat = xml_file.split("/")[-2]
            cat_dir = path = os.path.join(exr_dir, cat)
            if not os.path.exists(cat_dir):
                os.makedirs(cat_dir)

            file = xml_file.replace(".xml",".exr")
            exr_path = os.path.join(exr_dir, "/".join(file.split("/")[-2:]))
        
        print("Rendering: {} / {}".format(i, len(xml_files)))
        mitsuba_render(xml_file, exr_path)
