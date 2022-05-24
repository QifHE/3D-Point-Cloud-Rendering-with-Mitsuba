import os
import sys

import mitsuba
import numpy as np
import open3d as o3d
from tqdm import tqdm
import cv2


### SET VARIABLES HERE ###
categories = []  # categories that you wish to render, set [] to to deal with all categories
exr_dir = ""    # EXR file directary, '' will use the original directary 
png_dir = ""    # PNG file directary, '' will use the original directary 

''' # Examples:
categories = ["airplane","bag"]
exr_dir = "../mitsubaRenders/exr_files"
png_dir = "../mitsubaRenders/png_files"
'''

### FUNCTIONS ###

def exr_to_png(input_path, output_path):
    hdr = cv2.imread(input_path, -1)
    # Simply clamp values to a 0-1 range for tone-mapping
    ldr = np.clip(hdr, 0, 1)
    # Color space conversion
    ldr = ldr**(1/2.2)
    # 0-255 remapping for bit-depth conversion
    ldr = 255.0 * ldr
    cv2.imwrite(output_path, ldr)


### MAIN ###
if __name__ == "__main__":

    exr_files = []
    os.environ['OPENCV_IO_ENABLE_OPENEXR'] = "1"

    print("OpenEXR to PNG")
    print("Selected Categories ('None' for all): ")
    print(categories)

    for root, dirs, files in os.walk(exr_dir, topdown=False):
        if root.split("/")[-1] in categories or not categories:
            for name in files:
                if name.endswith(".exr"):
                    exr_files.append(os.path.join(root, name))

    print("Converting EXR Images:")
    i = 0
    for exr_file in tqdm(exr_files):
        i += 1
        if not png_dir:
            png_path = exr_file.replace(".exr",".png")
        else:
            cat = exr_file.split("/")[-2]
            cat_dir = path = os.path.join(png_dir, cat)
            if not os.path.exists(cat_dir):
                os.makedirs(cat_dir)

            file = exr_file.replace(".exr",".png")
            png_path = os.path.join(png_dir, "/".join(file.split("/")[-2:]))
        
        print("Converting: {} / {}".format(i, len(exr_files)))
        exr_to_png(exr_file, png_path)
