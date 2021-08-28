import numpy as np
import open3d as o3d

ply_path = "D:\\Codes\\ours\\dataset_test_only\\airplane\\1a04e3eab45ca15dd86060f189eb133\\00_partial.ply"

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
            <translate x="0" y="-8.75" z="0"/>
            <rotate x="1" y="0" z="0" angle="-60"/>
            <lookat origin="0,0,10" target="0,0,0" up="0,0,0"/>
        </transform>
        <float name="fov" value="25"/>
        
        <sampler type="ldsampler">
            <integer name="sampleCount" value="256"/>
        </sampler>
        <film type="ldrfilm">
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
            <lookat origin="-4,4,22" target="0,0,0" up="0,0,1"/>
        </transform>
        <emitter type="area">
            <rgb name="radiance" value="6,6,6"/>
        </emitter>
    </shape>
</scene>
"""

def colormap(x,y,z):
    vec = np.array([x,y,z])
    vec = np.clip(vec, 0.001,1.0)
    norm = np.sqrt(np.sum(vec**2))
    vec /= norm
    return [vec[0], vec[1], vec[2]]

def mitsuba(pcl, path, clr=None):
    xml_segments = [xml_head]

    # pcl = standardize_bbox(pcl, 2048)
    pcl = pcl[:,[2,0,1]] # 把物体水平放到平面上
    
    theta_X = np.radians(-10) 
    theta_Y = np.radians(-30) 
    theta_Z = np.radians(80) 
    
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
    
    pcl[:, 0] *= -1
    pcl[:, 1] *= 1
    pcl[:, 2] *= 1
    
    h = np.min(pcl[:,2])

    for i in range(pcl.shape[0]):
        if clr == None:
            color = colormap(0.5, 0.5, 0.5) # 灰色
            #color = colormap(pcl[i,0]+0.5,pcl[i,1]+0.5,pcl[i,2]+0.5)
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
    print("Load a ply point cloud, print it, and render it")
    pts = o3d.io.read_point_cloud(ply_path)
    pts = np.asarray(pts.points)
    path = "D:\\Codes\\ours\\dataset_test_only\\airplane\\1a04e3eab45ca15dd86060f189eb133\\00_partial.xml"
    mitsuba(pts, path)


    