import numpy as np
import open3d as o3d
import subprocess
import os

PATH_TO_MITSUBA2 = "mitsuba.exe的路径"  # mitsuba exectuable

def standardize_bbox(pcl, points_per_object):
    pt_indices = np.random.choice(pcl.shape[0], points_per_object, replace=False)
    np.random.shuffle(pt_indices)
    pcl = pcl[pt_indices] # n by 3
    mins = np.amin(pcl, axis=0)
    maxs = np.amax(pcl, axis=0)
    center = ( mins + maxs ) / 2.
    scale = np.amax(maxs-mins)
    print("Center: {}, Scale: {}".format(center, scale))
    result = ((pcl - center)/scale).astype(np.float32) # [-0.5, 0.5]
    return result

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
            <lookat origin="-3,3,4" target="0,0,0" up="0,0,1"/>
        </transform>
        <emitter type="area">
            <rgb name="radiance" value="9,9,9"/>
        </emitter>
    </shape>
</scene>
"""

def colormap(x,y,z):
    vec = np.array([x,y,z])
    vec = np.clip(vec, 0.001,1.0)
    norm = np.sqrt(np.sum(vec**2))
    vec /= norm
    return [vec[0], vec[1], vec[2]] # 输出的是（R,G,B）在 [0,1] 区间

def mitsuba(pcl, path, clr=None):
    xml_segments = [xml_head]

    pcl = standardize_bbox(pcl, 2048)
    #pcl = pcl[:,[2,0,1]] # 把物体水平放到平面上
    
    # 旋转变化
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
    
    # 三个轴方向上的翻转
    pcl[:, 0] *= 1
    pcl[:, 1] *= 1
    pcl[:, 2] *= 1
    
    h = np.min(pcl[:,2])

    for i in range(pcl.shape[0]):
        if clr == None:
            color = colormap(pcl[i,0]+0.5,pcl[i,1]+0.5,pcl[i,2]+0.5) # 依据点坐标的渐变色
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

if __name__ == '__main__':
    visual_data_dir = "ply文件路径"
    ply_files = []
    for root, dirs, files in os.walk(visual_data_dir, topdown=False):
        if root.endswith('Airplane'):
            for name in files:
                if name.endswith('.ply'):
                    ply_files.append(os.path.join(root, name))
    
    for plyfile in ply_files:
        pts = o3d.io.read_point_cloud(plyfile)
        pts = np.asarray(pts.points)
        path = plyfile.replace(".ply", ".xml")
        mitsuba(pts, path)
        subprocess.run([PATH_TO_MITSUBA2, path])
        print(plyfile)


    
