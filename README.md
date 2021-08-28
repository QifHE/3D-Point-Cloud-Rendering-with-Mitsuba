# 3D-Point-Cloud-Rendering-with-Mitsuba
<p align="center">
  <img src="https://user-images.githubusercontent.com/34999814/131210917-3cb04fb7-5605-4289-86ff-dd87b116d73c.jpg" height="500">
</p>
  
## 利用Open3D读取PLY格式点云，生成Mitsuba的XML场景配置文件，再由Mitsuba 0.6进行渲染。

### 需要配置：
 - Python 3+
 - numpy
 - open3d

### 文件说明：

 - mitsuba_test.py：XML生成文件
 - open3d_test.py：open3d渲染测试文件

### 参数设置：
在mitsuba_test.py中：

'''
<float name="farClip" value="100"/>
<float name="nearClip" value="0.1"/>
<transform name="toWorld">
    <translate x="0" y="0" z="0"/>
    <rotate x="0" y="0" z="0" angle="0"/>
    <lookat origin="0,0,10" target="0,0,0" up="0,0,0"/>
</transform>
<float name="fov" value="25"/>
'''
上块调整相机视野：
farClip和nearClip：限制场景景深
translate：顾名思义
rotate：""中数值代表旋转比例，乘以angle(单位°)为最终旋转角度
lookat origin：相机所处位置
target：相机正对的坐标
up：""中填写1代表这个方向是“上”方向
fov：顾名思义

'''
<shape type="rectangle">
    <transform name="toWorld">
        <scale x="10" y="10" z="1"/>
        <lookat origin="-4,4,22" target="0,0,0" up="0,0,1"/>
    </transform>
    <emitter type="area">
        <rgb name="radiance" value="6,6,6"/>
    </emitter>
</shape>
'''
上块调整光照：
shape type：顾名思义
scale：顾名思义
lookat origin：顾名思义
rgb name：顾名思义
