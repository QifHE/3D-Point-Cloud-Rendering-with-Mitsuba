# 3D-Point-Cloud-Rendering-with-Mitsuba
<p align="center">
  <img src="https://user-images.githubusercontent.com/34999814/131210917-3cb04fb7-5605-4289-86ff-dd87b116d73c.jpg" height="500">
</p>
  
**English Version will be added Soon.**

**批量利用Open3D读取PLY格式点云，生成Mitsuba的XML场景配置文件，再由Mitsuba2进行渲染。**
[利用Mitsuba 0.6的版本](https://github.com/QifHE/3D-Point-Cloud-Rendering-with-Mitsuba/blob/main/README_old.md)

（Linux上没有成功，所以选用Windows）

## 在Windows上安装Mitsuba2
先在Windows电脑上安装：
- git for Windows
- cmake for Windows
- Anaconda3 for Windows
- Visual Studio 2022

后续参考这篇文章：
[【知乎】Mitsuba编译安装踩坑记](https://zhuanlan.zhihu.com/p/359008593)

其中cmake那步需要将
```
cmake -G "Visual Studio 16 2019" -A x64
```
替换为
```
cmake -G "Visual Studio 17 2022" -A x64
```
Mitsuba安装成功后在mitsuba\dist\目录下找到mitsuba.exe并记下它的绝对路径，注意Windows中复制的路径的“\”要替换成Python中的“\\\”或“/”。
这个是CPU版本，GPU版本还待研究。

## 环境
安装好Anaconda3后打开Anaconda Prompt，在其中创建虚拟环境。
- Python 3
- numpy
- open3d==0.9.0.0

## 文件说明：

 - mitsuba_batch.py：读取一个文件夹下所有分类的ply文件，并在原目录下生成xml和exr文件。
 - xml是Mitsuba的场景配置文件。
 - exr是渲染结果，可以使用[InfraView](https://www.irfanview.com/)进行批量转换为jpg或png文件（[InfraView同时需要安装完整插件包](https://www.irfanview.com/64bit.htm)）

 运行前需要自己更改代码中的路径：
 ```python
PATH_TO_MITSUBA2 = "mitsuba.exe的路径"
visual_data_dir = "ply文件路径"
 ```
使用Anaconda3自带的Spyder软件能更方便地运行虚拟环境和调试。


## 参数设置：

在mitsuba_*.py中：

```
<float name="farClip" value="100"/>
<float name="nearClip" value="0.1"/>
<transform name="toWorld">
    <translate x="0" y="0" z="0"/>
    <rotate x="0" y="0" z="0" angle="0"/>
    <lookat origin="0,0,10" target="0,0,0" up="0,0,0"/>
</transform>
<float name="fov" value="25"/>
```
上块调整相机视野：

farClip和nearClip：限制场景景深

translate：平移

rotate：""中数值代表旋转比例，乘以angle(单位°)为最终旋转角度

lookat origin：相机所处位置

target：相机正对的坐标

up：""中填写1代表这个方向是“上”方向

fov：视野
```
<sampler type="ldsampler">
            <integer name="sampleCount" value="256"/>
        </sampler>
        <film type="hdrfilm">
            <integer name="width" value="800"/>
            <integer name="height" value="600"/>
            <rfilter type="gaussian"/>
            <boolean name="banner" value="false"/>
        </film>
```
上块调整渲染结果大小。

```
<shape type="rectangle">
    <transform name="toWorld">
        <scale x="10" y="10" z="1"/>
        <lookat origin="-4,4,22" target="0,0,0" up="0,0,1"/>
    </transform>
    <emitter type="area">
        <rgb name="radiance" value="6,6,6"/>
    </emitter>
</shape>
```
上块调整光照：

shape type：形状

scale：比例

lookat origin：朝向

```
color = colormap(pcl[i,0]+0.5,pcl[i,1]+0.5,pcl[i,2]+0.5)
```
上块调整颜色。

```
visual_data_dir = "ply文件路径"
    ply_files = []
    for root, dirs, files in os.walk(visual_data_dir, topdown=False):
        if root.endswith('Airplane'):
            for name in files:
                if name.endswith('.ply'):
                    ply_files.append(os.path.join(root, name))
```
上块调整ply文件的分类读取逻辑，根据自己的储存结构修改。