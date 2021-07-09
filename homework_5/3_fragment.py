import os  # 文件

import vtk  # 可视化

########
# PATH #
########

# 注意：所有路径必须为全英文！！！
HOME_PATH = os.getcwd()  # 主目录
DATA_PATH = os.path.join(HOME_PATH, 'data')  # 数据目录
RESULT_PATH = os.path.join(HOME_PATH, 'result')  # 结果目录

##########
# SOURCE #
##########

source = vtk.vtkNIFTIImageReader()  # 数据源
source.SetFileName(os.path.join(DATA_PATH, 'heart.nii.gz'))  # 读取体数据

##########
# FILTER #
##########

# EXTRACTOR
extractor = vtk.vtkMarchingCubes()  # 过滤器：三角面片
extractor.SetInputConnection(source.GetOutputPort())  # 读取数据源
extractor.ComputeNormalsOn()  # 计算等值面法向量以增强渲染效果
extractor.SetValue(0, 150)  # 设定等值面

# STRIPPER
isosurface = vtk.vtkStripper()  # 过滤器：等值面
isosurface.SetInputConnection(extractor.GetOutputPort())  # 读取过滤器：三角面片

##########
# Mapper #
##########

mapper = vtk.vtkPolyDataMapper()  # 映射器：等值面
mapper.SetInputConnection(isosurface.GetOutputPort())  # 读取过滤器：等值面
mapper.ScalarVisibilityOff()  # 关闭颜色映射关系

#########
# ACTOR #
#########

actor = vtk.vtkActor()  # 演员：等值面
actor.SetMapper(mapper)  # 读取映射器：等值面
actor.GetProperty().SetColor(0.7, 0.7, 0.5)  # 设定颜色
actor.GetProperty().SetAmbient(0.25)  # 设定环境光系数
actor.GetProperty().SetDiffuse(0.6)  # 设定散射光系数
actor.GetProperty().SetSpecular(0.9)  # 设定反射光系数
actor.GetProperty().SetOpacity(1.0)  # 设定透射光系数

############
# RENDERER #
############

renderer = vtk.vtkRenderer()  # 渲染器
renderer.AddActor(actor)  # 读取演员：等值面
renderer.SetBackground(0.8, 0.8, 0.8)  # 设定背景颜色

##########
# WINDOW #
##########

window = vtk.vtkRenderWindow()  # 窗口
window.AddRenderer(renderer)  # 读取渲染器
window.Render()  # 渲染窗口
window.SetSize(750, 750)  # 设定窗口大小
window.SetWindowName('Fragment')  # 设定窗口名称

########
# SAVE #
########

writer_filter = vtk.vtkWindowToImageFilter()  # 过滤器：截图
writer_filter.SetInput(window)  # 读取窗口
writer = vtk.vtkPNGWriter()  # 图像生成器
writer.SetFileName(os.path.join(RESULT_PATH, 'fragment.png'))  # 设定图像路径
writer.SetInputConnection(writer_filter.GetOutputPort())  # 读取窗口截图
writer.Write()  # 保存图片

##############
# INTERACTOR #
##############

interactor = vtk.vtkRenderWindowInteractor()  # 交互器
interactor.SetRenderWindow(window)  # 读取窗口
interactor.Initialize()  # 初始化交互器
interactor.Start()  # 运行交互器
