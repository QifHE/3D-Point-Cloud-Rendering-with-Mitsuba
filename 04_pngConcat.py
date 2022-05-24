import os
from re import L
from sqlite3 import adapt
import sys

import mitsuba
import numpy as np
import open3d as o3d
from tqdm import tqdm
import cv2


### SET VARIABLES HERE ###
categories = ["airplane","bag"]             # categories that you wish to render, set [] to deal with all categories
png_dir = "../mitsubaRenders/png_files"         # Must! PNG file directary
concat_output_dir = "../mitsubaRenders/concat_files"  # final image directary, '' will use the original directary 
img_name = "output"                  # Must! image name

concat_direction = "v"               # Must! 'v' for vertical, 'h' for horizontal
adaptive_size = True                # all img will resize according to the minimum width/height within the image list
compress2jpg = True                 # lossy compression to jepg file
jpg_quality = 85

### FUNCTIONS ###

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
if __name__ == "__main__":

    png_files = []

    print("Image Concatenation")
    print("Selected Categories ('None' for all): ")
    print(categories)

    for root, dirs, files in os.walk(png_dir, topdown=False):
        if root.split("/")[-1] in categories or not categories:
            for name in files:
                if name.endswith(".png"):
                    png_files.append(os.path.join(root, name))

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