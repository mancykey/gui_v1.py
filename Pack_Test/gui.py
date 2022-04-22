import tkinter
import tkinter.ttk
import tkinter.font as tf
from tkinter import *
from tkinter import filedialog
import os
import shutil
import pandas as pd
import numpy as np
import time
import math
import operator
from PIL import Image
from PIL import ImageTk
from django.conf.locale import tk
from scipy.spatial import distance
import networkx as nx
import configparser
import base64
from cover_jpg import img as cover
from content_jpg import img as content

'''
数据准备：
1、Index_Line.csv，索引表，字段：Line_ID_GPS、Line_ID_Transaction、Line_ID_GIS、Line_Name
2、Stop.csv，站点表，来自于公交图层导出，其中坐标系需要核实是否与其他文件一致，字段：Route_ID、Line_ID、Stop_ID、Order、Lng、Lat
3、Link_Ride.csv，乘车距离表，来自于公交图层导出，字段：Route_ID、On_Stop_ID、Off_Stop_ID、Off_Route_ID、Distance
4、T_Bus_GPS_2019.09.01.csv，公交GPS表，字段：Line_ID、Bus_ID、Timestamp（或DateTime）, Lng, Lat, Speed
5、T_Bus_Transaction_2019.09.01.csv，公交交易表，字段：Card_ID、Timestamp（或DateTime）、Bus_ID、Line_ID、Card_Type、Price
'''

class MY_GUI():
    def __init__(self,init_window_name):
        self.init_window_name = init_window_name


    #设置窗口，坐标原点在左上角
    def set_init_window(self):
        for i in range(100):
            # 每次更新加1
            self.progressbarOne['value'] = i + 1
            # 更新画面
            self.init_window_name.update()
            time.sleep(0.005)

        # 主窗口
        self.init_window_name.title("公交OD识别及客流分配工具箱") #窗口名
        self.init_window_name.geometry('1000x600+250+80') #1000x600为窗口大小，+250 +80 定义窗口弹出时的默认展示位置
        self.init_window_name["bg"] = "LightYellow" #窗口背景色，其他背景色见：blog.csdn.net/chl0000/article/details/7657887
        # self.init_window_name.attributes("-alpha",0.9) #透明化，值越小透明化程度越高
        # self.init_window_name.PhotoImage(file=r"assassins creed1.jpg")

        #背景图片:主色调：Goldenrod、LemonChiffon、CadetBlue
        self.tmp2=open("content.jpg","wb")
        self.tmp2.write(base64.b64decode(content))
        self.tmp2.close()
        self.pil_image=Image.open("content.jpg")#公交车.png,http://www.puhuajia.com/tool/webcolor/
        self.w,self.h=self.pil_image.size
        self.factor=1.1#min(1000/self.w,600/self.h)
        print(self.factor)
        self.w2=int(1000*self.factor)
        self.h2 =int(600*self.factor)
        print(self.w2,self.h2 )
        self.img2=self.pil_image.resize((self.w2,self.h2),Image.LANCZOS)#https://blog.csdn.net/znix1116/article/details/123777479
        self.tk_image=ImageTk.PhotoImage(self.img2)
        self.canvas = Canvas(self.init_window_name, width=1000, height=600)
        self.canvas.place(x=0, y=0)
        self.canvas.create_image(1000// 2, 600// 2, image=self.tk_image)
        # 左边画布
        self.canvas2 = Canvas(self.init_window_name, width=900, height=380)
        self.canvas2.place(x=50, y=130)
        self.canvas2.create_image(1000 // 2, 600 // 2, image=self.tk_image)
        #尺度滑尺
        self.s = Scale(self.init_window_name, from_=1, to=4, orient="horizontal", length=800,
                       activebackground="CadetBlue",background="CadetBlue",sliderrelief="flat",
                       highlightbackground="LemonChiffon",showvalue=0, resolution=1)#cursor=,relief="flat",tickinterval=1,sliderrelief="groove",
        self.s.place(x=100, y=150)
        # self.s['value'] = 100

        # self.s = self.init_window_name.Scale(self.init_window_name, label='try me', from_=0, to=10, orient="horizontal", length=200, showvalue=0,tickinterval=2, resolution=0.01)
        #进度条
        # self.progressbarOne = tkinter.ttk.Progressbar(self.init_window_name,orient=tkinter.HORIZONTAL, length=800, mode='determinate')
        # self.progressbarOne.place(x=50, y=550)
        # self.progressbarOne['maximum'] = 100


        # logo
        self.txtid = self.canvas2.create_text(780, 350, font=("Purisa", 12), fill="LightYellow",anchor="center")
        self.canvas2.insert(self.txtid, 1, "华设设计集团规划院大数据中心")
        # 标题
        self.set_top_lable = self.canvas.create_text(500,100, font=("黑体", 18, "bold"))
        self.canvas.insert(self.set_top_lable, 1, "公交OD识别及客流分配工具箱")
        # 进度条按钮
        # self.set_progress_button = Button(self.init_window_name,font=("黑体",12), text="开始", bg="CadetBlue", command=self.set_progress)#, command=self.set_progress
        # self.set_progress_button.place(x=70, y=120, width=100, height=40)

        self.set_dir_button = Button(self.init_window_name,font=("黑体",12), text="第一步\n设置模型目录", bg="CadetBlue", command=self.set_dir)
        self.set_dir_button.place(x=100, y=200, width=160, height=80)

        self.open_config_button = Button(self.init_window_name,font=("黑体",12), text="第二步\n修改配置参数", bg="CadetBlue", command=self.open_config, state='disabled')
        self.open_config_button.place(x=310, y=200, width=160, height=80)

        self.run_odest_button = Button(self.init_window_name,font=("黑体",12), text="第三步\n运行OD识别算法", bg="CadetBlue", command=self.run_odest, state='disabled')
        self.run_odest_button.place(x=520, y=200, width=160, height=80)

        self.run_assign_button = Button(self.init_window_name,font=("黑体",12), text="第四步\n运行客流分配算法", bg="CadetBlue", command=self.run_assign, state='disabled')
        self.run_assign_button.place(x=730, y=200, width=160, height=80)

        self.open_help_button = Button(self.init_window_name,font=("黑体",9), text="打开帮助文档", bg="Goldenrod", command=self.open_help, state='disabled')
        self.open_help_button.place(x=100, y=470, width=120, height=30)

        self.recover_config_button = Button(self.init_window_name,font=("黑体",9), text="恢复配置参数", bg="Goldenrod", command=self.recover_config, state='disabled')
        self.recover_config_button.place(x=240, y=470, width=120, height=30)

        self.open_log_button = Button(self.init_window_name,font=("黑体",9), text="查看日志文件", bg="Goldenrod", command=self.open_log, state='disabled')
        self.open_log_button.place(x=380, y=470, width=120, height=30)

        self.open_output_button = Button(self.init_window_name,font=("黑体",9), text="打开输出文件夹", bg="Goldenrod", command=self.open_output, state='disabled')
        self.open_output_button.place(x=520, y=470, width=120, height=30)

        self.log_data_text = Text(self.init_window_name,font=("黑体",16),bg="LemonChiffon")#LightSkyBlue
        self.log_data_text.place(x=100, y=350, width=800, height=100)
        self.log_data_text.insert(END, '欢迎使用公交OD识别及客流分配工具箱!\n请设置模型目录。\n')

    def set_cover_window(self):

        # 主窗口
        self.init_window_name.title("公交OD识别及客流分配工具箱") #窗口名
        self.init_window_name.geometry('600x400+250+80') #1000x600为窗口大小，+250 +80 定义窗口弹出时的默认展示位置
        self.init_window_name["bg"] = "LightYellow" #窗口背景色，其他背景色见：blog.csdn.net/chl0000/article/details/7657887
        # 背景图片
        # self.pil_image = Image.open("公交车背景图05.jpg")  # 公交车.png,http://www.puhuajia.com/tool/webcolor/
        self.tmp=open("cover.jpg","wb")
        self.tmp.write(base64.b64decode(cover))
        self.tmp.close()
        self.pil_image = Image.open('cover.jpg')
        self.w, self.h = self.pil_image.size
        self.factor = 1  # min(1000/self.w,600/self.h)
        self.w2 = int(600 * self.factor)
        self.h2 = int(400 * self.factor)
        self.img2 = self.pil_image.resize((self.w2, self.h2),
                                          Image.LANCZOS)  # https://blog.csdn.net/znix1116/article/details/123777479
        self.tk_image = ImageTk.PhotoImage(self.img2)
        self.canvas = Canvas(self.init_window_name, width=600, height=400)
        self.canvas.place(x=0, y=0)
        self.canvas.create_image(600 // 2, 400 // 2, image=self.tk_image)

        # 进度条
        self.progressbarOne = tkinter.ttk.Progressbar(self.init_window_name,length=500)
        self.progressbarOne.place(x=50, y=300)
        # 进度值最大值
        self.progressbarOne['maximum'] = 100
        # 进度值初始值
        self.progressbarOne['value'] = 0
        button = tkinter.Button(self.init_window_name, text='启动', command=self.set_init_window)
        button.place(x=275, y=350)
        # 标题
        self.set_cover_lable = self.canvas.create_text(300, 260, font=("黑体", 18, "bold"))
        self.canvas.insert(self.set_cover_lable, 1, "公交OD识别及客流分配工具箱")
        self.init_window_name.mainloop()

    # 方法
    # def show(self):
    #     for i in range(100):
    #         # 每次更新加1
    #         self.progressbarOne['value'] = i + 1
    #         # 更新画面
    #         self.init_window_name.update()
    #         time.sleep(0.005)
    #     self.set_init_window

    def set_progress(self):
        self.log_data_text.insert(END, '模型开始运行\n')
        self.log_data_text.insert(END, '请运行下面步骤。\n')
        self.set_dir_button['state'] = 'normal'

    def set_dir(self):
        self.model_dir = filedialog.askdirectory(title='选择模型目录')
        if self.model_dir:
            self.log_data_text.insert(END, '模型目录已设置为：{}\n'.format(self.model_dir))
            self.log_data_text.insert(END, '请配置模型参数。\n')
            self.open_config_button['state'] = 'normal'
            self.recover_config_button['state'] = 'normal'
            self.open_help_button['state'] = 'normal'
            self.open_output_button['state'] = 'normal'
            self.open_log_button['state'] = 'normal'
            self.s.set(1)
        else:
            self.log_data_text.insert(END, '请重新设置模型目录。\n')
            tkinter.messagebox.showinfo(title='Hi', message='请重新设置模型目录！')
    # def set_dir(self):
    #     self.model_dir2 = filedialog.askdirectory(title='选择模型目录')
    #     if self.model_dir2:
    #         self.log_data_text.insert(END, '模型目录已设置为：{}\n'.format(self.model_dir2))
    #         self.log_data_text.insert(END, '请配置模型参数。\n')
    #         self.open_config_button['state'] = 'normal'
    #         self.recover_config_button['state'] = 'normal'
    #         self.open_help_button['state'] = 'normal'
    #         self.open_output_button['state'] = 'normal'
    #         self.open_log_button['state'] = 'normal'
    #         progressbarOne['value'] = 5
    #     else:
    #         self.log_data_text.insert(END, '请重新设置模型目录。\n')
    #         tkinter.messagebox.showinfo(title='Hi', message='请重新设置模型目录！')

    def open_config(self):
        self.s.set(2)
        os.startfile(self.model_dir + '/Input/parameter.ini')
        self.log_data_text.insert(END, '参数配置完毕，请运行OD识别算法。\n')
        self.log_data_text.insert(END, '如果之前已运行过OD识别算法，也可直接运行客流分配算法。\n')
        self.run_odest_button['state'] = 'normal'
        self.run_assign_button['state'] = 'normal'

    def run_odest(self):
        self.log_data_text.insert(END, 'OD识别算法运行中………………………………………………………………\n')
        self.s.set(3)
        main(1)
        self.log_data_text.insert(END, 'OD识别算法运行完成，请查看日志或打开输出文件夹。\n')

    def run_assign(self):
        self.log_data_text.insert(END, '客流分配算法运行中………………………………………………………………\n')
        self.s.set(4)
        main(2)
        self.log_data_text.insert(END, '客流分配算法运行完成，请查看日志或打开输出文件夹。\n')

    def open_help(self):
        os.startfile(self.model_dir + '/公交OD识别及客流分配工具箱使用指南.docx')

    def recover_config(self):
        shutil.copy(self.model_dir + '/Input/parameter_backup.ini', self.model_dir + '/Input/parameter.ini')
        self.log_data_text.insert(END, '参数文件已还原，请重新配置参数。\n')

    def open_output(self):
        os.startfile(self.model_dir + '/Output')

    def open_log(self):
        os.startfile(self.model_dir + '/Output/result.txt')


# #设置窗口，坐标原点在左上角
# def set_init_window(init_window_name):
#     global progressbarOne,canvas,canvas2
#
#     # 主窗口
#     init_window_name.title("公交OD识别及客流分配工具箱") #窗口名
#     init_window_name.geometry('1000x600+250+80') #1000x600为窗口大小，+250 +80 定义窗口弹出时的默认展示位置
#     init_window_name["bg"] = "LightYellow" #窗口背景色，其他背景色见：blog.csdn.net/chl0000/article/details/7657887
#     # self.init_window_name.attributes("-alpha",0.9) #透明化，值越小透明化程度越高
#     # self.init_window_name.PhotoImage(file=r"assassins creed1.jpg")
#
#     #背景图片
#     # pil_image=Image.open("暗黑色1.jpg")#公交车.png,http://www.puhuajia.com/tool/webcolor/
#     # w,h=pil_image.size
#     # factor=1#min(1000/self.w,600/self.h)
#     # print(factor)
#     # w2=int(1000*factor)
#     # h2 =int(600*factor)
#     # img2=pil_image.resize((1000,600),Image.LANCZOS)#https://blog.csdn.net/znix1116/article/details/123777479
#     # tk_image=ImageTk.PhotoImage(img2)
#     # canvas = Canvas(init_window_name, width=1000, height=600)
#     # canvas.place(x=0, y=0)
#     # canvas.create_image(1000// 2, 600// 2, image=tk_image)
#
#     tk_image=init_window_name.PhotoImage(file="暗黑色1.jpg")
#     root=init_window_name.Tk()
#     imgLabel=tk.Lable(root,image=tk_image,compound=init_window_name.CENTER)
#     imgLabel.place(x=50, y=130)
#     # 左边画布
#     canvas2 = Canvas(init_window_name, width=400, height=380)
#     canvas2.place(x=50, y=130)
#     canvas2.create_image(1000 // 2, 600 // 2, image=tk_image)
#     # 右边画布
#     canvas3 = Canvas(init_window_name, width=400, height=380)
#     canvas3.place(x=550, y=130)
#     canvas3.create_image(1000 // 2, 600 // 2, image=tk_image)
#     #进度条
#     # self.progressbarOne = tkinter.ttk.Progressbar(self.init_window_name,orient=tkinter.HORIZONTAL, length=800, mode='determinate')
#     # self.progressbarOne.place(x=50, y=550)
#     # self.progressbarOne['maximum'] = 100
#     global progressbarOne,set_progress_button,set_dir_button,open_config_button,run_odest_button,run_assign_button
#     global open_help_button,recover_config_button,open_log_button,open_output_button,log_data_text
#     progressbarOne = tkinter.ttk.Progressbar(init_window_name, orient=tkinter.HORIZONTAL, length=800,
#                                              mode='determinate')
#     progressbarOne.place(x=50, y=550)
#     progressbarOne['maximum'] = 100
#     # 进度值初始值
#
#
#     # logo
#     txtid = canvas.create_text(900, 580, font=("Purisa", 12), fill="red",anchor="center")
#     canvas.insert(txtid, 1, "华设设计集团大数据部")
#     # 标题
#     set_top_lable = canvas.create_text(500,100, font=("黑体", 18, "bold"))
#     canvas.insert(set_top_lable, 1, "公交OD识别及客流分配工具箱")
#     # 进度条按钮
#     set_progress_button = Button(init_window_name,font=("黑体",12), text="开始", bg="CadetBlue", command=set_progress)#, command=self.set_progress
#     set_progress_button.place(x=70, y=120, width=100, height=40)
#
#     set_dir_button = Button(init_window_name,font=("黑体",12), text="第一步：设置模型目录", bg="CadetBlue", command=set_dir, state='disabled')
#     set_dir_button.place(x=70, y=180, width=200, height=40)
#
#     open_config_button = Button(init_window_name,font=("黑体",12), text="第二步：修改配置参数", bg="CadetBlue", command=open_config, state='disabled')
#     open_config_button.place(x=70, y=250, width=200, height=40)
#
#     run_odest_button = Button(init_window_name,font=("黑体",12), text="第三步：运行OD识别算法", bg="CadetBlue", command=run_odest, state='disabled')
#     run_odest_button.place(x=70, y=320, width=200, height=40)
#
#     run_assign_button = Button(init_window_name,font=("黑体",12), text="第四步：运行客流分配算法", bg="CadetBlue", command=run_assign, state='disabled')
#     run_assign_button.place(x=70, y=390, width=200, height=40)
#
#     open_help_button = Button(init_window_name,font=("黑体",8), text="打开帮助文档", bg="LightGrey", command=open_help, state='disabled')
#     open_help_button.place(x=50, y=570, width=100, height=20)
#
#     recover_config_button = Button(init_window_name,font=("黑体",8), text="恢复配置参数", bg="LightGrey", command=recover_config, state='disabled')
#     recover_config_button.place(x=200, y=570, width=100, height=20)
#
#     open_log_button = Button(init_window_name,font=("黑体",8), text="查看日志文件", bg="LightGrey", command=open_log, state='disabled')
#     open_log_button.place(x=350, y=570, width=100, height=20)
#
#     open_output_button = Button(init_window_name,font=("黑体",8), text="打开输出文件夹", bg="LightGrey", command=open_output, state='disabled')
#     open_output_button.place(x=500, y=570, width=100, height=20)
#
#     log_data_text = Text(init_window_name,font=("黑体",12),bg="LightGrey")#LightSkyBlue
#     log_data_text.place(x=70, y=450, width=360, height=50)
#     log_data_text.insert(END, '欢迎使用公交OD识别及客流分配工具箱!\n请设置模型目录。\n')


# 方法
#
#
# def set_progress(log_data_text):
#     log_data_text.insert(END, '模型开始运行\n')
#     log_data_text.insert(END, '请运行下面步骤。\n')
#     set_dir_button['state'] = 'normal'
#     progressbarOne['value'] = 2
#
# def set_dir():
#     global model_dir2
#     model_dir2 = filedialog.askdirectory(title='选择模型目录')
#     if model_dir2:
#         log_data_text.insert(END, '模型目录已设置为：{}\n'.format(model_dir2))
#         log_data_text.insert(END, '请配置模型参数。\n')
#         open_config_button['state'] = 'normal'
#         recover_config_button['state'] = 'normal'
#         open_help_button['state'] = 'normal'
#         open_output_button['state'] = 'normal'
#         open_log_button['state'] = 'normal'
#         progressbarOne['value'] = 5
#     else:
#         log_data_text.insert(END, '请重新设置模型目录。\n')

# def open_config(self):
#     os.startfile(model_dir2 + '/Input/parameter.ini')
#     log_data_text.insert(END, '参数配置完毕，请运行OD识别算法。\n')
#     log_data_text.insert(END, '如果之前已运行过OD识别算法，也可直接运行客流分配算法。\n')
#     run_odest_button['state'] = 'normal'
#     run_assign_button['state'] = 'normal'
#     progressbarOne['value'] = 10
#
# def run_odest(self):
#     log_data_text.insert(END, 'OD识别算法运行中………………………………………………………………\n')
#     main(1)
#     log_data_text.insert(END, 'OD识别算法运行完成，请查看日志或打开输出文件夹。\n')
#     progressbarOne['value'] = 50
#
# def run_assign(self):
#     log_data_text.insert(END, '客流分配算法运行中………………………………………………………………\n')
#     main(2)
#     log_data_text.insert(END, '客流分配算法运行完成，请查看日志或打开输出文件夹。\n')
#
# def open_help(self):
#     os.startfile(model_dir2 + '/公交OD识别及客流分配工具箱使用指南.docx')
#
# def recover_config(log_data_text):
#     shutil.copy(model_dir2 + '/Input/parameter_backup.ini', model_dir2 + '/Input/parameter.ini')
#     log_data_text.insert(END, '参数文件已还原，请重新配置参数。\n')
#
# def open_output(model_dir):
#     os.startfile(model_dir + '/Output')
#
# def open_log(model_dir):
#     os.startfile(model_dir + '/Output/result.txt')

def gui_start():

    # 实例化出一个父窗口
    init_window = Tk()
    cover_PORTAL = MY_GUI(init_window)
    cover_PORTAL.set_cover_window()
    # ZMJ_PORTAL = MY_GUI(init_window)

    # 设置根窗口默认属性
    # ZMJ_PORTAL.set_init_window()

    # 父窗口进入事件循环，可以理解为保持窗口运行，否则界面不展示
    init_window.mainloop()



# 火星坐标系(GCJ-02)转百度坐标系(BD-09)
# 谷歌、高德——>百度
def gcj02_to_bd09(lng, lat):
    z = math.sqrt(lng * lng + lat * lat) + 0.00002 * math.sin(lat * x_pi)
    theta = math.atan2(lat, lng) + 0.000003 * math.cos(lng * x_pi)
    bd_lng = z * math.cos(theta) + 0.0065
    bd_lat = z * math.sin(theta) + 0.006
    return [bd_lng, bd_lat]


# 百度坐标系(BD-09)转火星坐标系(GCJ-02)
# 百度——>谷歌、高德
def bd09_to_gcj02(bd_lon, bd_lat):
    x = bd_lon - 0.0065
    y = bd_lat - 0.006
    z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * x_pi)
    theta = math.atan2(y, x) - 0.000003 * math.cos(x * x_pi)
    gg_lng = z * math.cos(theta)
    gg_lat = z * math.sin(theta)
    return [gg_lng, gg_lat]


# WGS84转GCJ02(火星坐标系)
def wgs84_to_gcj02(lng, lat):
    # 判断是否在国内
    if out_of_china(lng, lat):
        return [lng, lat]
    dlat = _transformlat(lng - 105.0, lat - 35.0)
    dlng = _transformlng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
    mglat = lat + dlat
    mglng = lng + dlng
    return [mglng, mglat]


#  GCJ02(火星坐标系)转GPS84
def gcj02_to_wgs84(lng, lat):
    if out_of_china(lng, lat):
        return [lng, lat]
    dlat = _transformlat(lng - 105.0, lat - 35.0)
    dlng = _transformlng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
    mglat = lat + dlat
    mglng = lng + dlng
    return [lng * 2 - mglng, lat * 2 - mglat]


# 百度坐标系转84坐标
def bd09_to_wgs84(bd_lon, bd_lat):
    lon, lat = bd09_to_gcj02(bd_lon, bd_lat)
    return gcj02_to_wgs84(lon, lat)


# 84坐标转百度坐标
def wgs84_to_bd09(lon, lat):
    lon, lat = wgs84_to_gcj02(lon, lat)
    return gcj02_to_bd09(lon, lat)


def _transformlat(lng, lat):
    ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + \
          0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * pi) + 40.0 *
            math.sin(lat / 3.0 * pi)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * pi) + 320 *
            math.sin(lat * pi / 30.0)) * 2.0 / 3.0
    return ret


def _transformlng(lng, lat):
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + \
          0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lng * pi) + 40.0 *
            math.sin(lng / 3.0 * pi)) * 2.0 / 3.0
    ret += (150.0 * math.sin(lng / 12.0 * pi) + 300.0 *
            math.sin(lng / 30.0 * pi)) * 2.0 / 3.0
    return ret


# 判断是否在国内，不在国内不做偏移
def out_of_china(lng, lat):
    return not (lng > 73.66 and lng < 135.05 and lat > 3.86 and lat < 53.55)


# 日期列表
def _get_lst_date(date_start, date_end):
    year = date_start.split('.')[0]
    month = date_start.split('.')[1]
    day1 = date_start.split('.')[2]
    day2 = date_end.split('.')[2]
    d1 = int(day1)
    d2 = int(day2)
    lst = []
    for d in range(d1, d2 + 1):
        day = str(d)
        if d < 10:
            day = '0' + day
        lst.append(year + '.' + month + '.' + day)

    return lst


# 字符串转换为时间戳
def _time_str_to_timestamp(string_time):

    try:
        if string_time.find(r'/') >= 0 and len(string_time) >= 17:
            return int(time.mktime(time.strptime(string_time, "%Y/%m/%d %H:%M:%S")))
        elif string_time.find(r'-') >= 0 and len(string_time) >= 17:
            return int(time.mktime(time.strptime(string_time, "%Y-%m-%d %H:%M:%S")))
        elif string_time.find(r'/') >= 0 and len(string_time) <= 10:
            return int(time.mktime(time.strptime(string_time, "%Y/%m/%d")))
        elif string_time.find(r'-') >= 0 and len(string_time) <= 10:
            return int(time.mktime(time.strptime(string_time, "%Y-%m-%d")))

    # 出错
    except:
        return 0


# 时间戳转换为时间片
def _timestamp_to_time_interval(timestamp):

    timeArray = time.localtime(timestamp)
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    hh = int(otherStyleTime[11 : 13])
    mm = int(otherStyleTime[14 : 16])
    time_interval = int((hh * 60 + mm) / unit_time_interval)
    return time_interval

# 查找无效的字符串
def _find_inmatch_string(str):

    str_new = 'Match'
    for i in range(len(lst_inmatch_route_name)):
        if str.find(lst_inmatch_route_name[i]) >= 0:
            str_new = None
    return str_new

# 点到直线段的最短距离与垂足
def _get_foot(point, line_p1, line_p2):
    [x0, y0] = point
    [x1, y1] = line_p1
    [x2, y2] = line_p2

    u1 = (((x0 - x1) * (x2 - x1)) + ((y0 - y1) * (y2 - y1)))
    u = u1 / ((x1 - x2) ** 2 + (y1 - y2) ** 2)
    # 点到直线的投影不在线段内, 计算点到两个端点距离的最小值即为"点到线段最小距离"
    if (u < 0.00001) or (u > 1):
        d1 = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5
        d2 = ((x2 - x0) ** 2 + (y2 - y0) ** 2) ** 0.5
        if d1 > d2:
            dist = d2
            [x3, y3] = line_p2
        else:
            dist = d1
            [x3, y3] = line_p1
    # 投影点在线段内部, 计算方式同点到直线距离, u 为投影点距离x1在x1x2上的比例, 以此计算出投影点的坐标
    else:
        x3 = x1 + u * (x2 - x1)
        y3 = y1 + u * (y2 - y1)
        dist = ((x3 - x0) ** 2 + (y3 - y0) ** 2) ** 0.5

    return [dist, [x3, y3]]


# 求方位角：指北方向线起，依顺时针方向到目标方向线之间的水平夹角
def _get_azimuth(p1, p2):
    angle = 0.0
    [x1, y1] = p1
    [x2, y2] = p2
    dx = x2 - x1
    dy = y2 - y1
    if x2 == x1:
        angle = math.pi / 2.0
        if y2 == y1:
            angle = 0.0
        elif y2 < y1:
            angle = 3.0 * math.pi / 2.0
    elif x2 > x1 and y2 > y1:
        angle = math.atan(dx / dy)
    elif x2 > x1 and y2 < y1:
        angle = math.pi / 2 + math.atan(-dy / dx)
    elif x2 < x1 and y2 < y1:
        angle = math.pi + math.atan(dx / dy)
    elif x2 < x1 and y2 > y1:
        angle = 3.0 * math.pi / 2.0 + math.atan(dy / -dx)

    return angle * 180 / math.pi


# 求方位角差值
def _get_azimuth_diff(angle1, angle2):

    return min(abs(angle1 - angle2), 360 - abs(angle1 - angle2))




# 求两点之间直线长度
def _get_point_dist(p1, p2):

    dist = ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5 * unit_coord2km

    return round(dist, 4)


# 求多段线长度
def _get_link_dist(lst_node, order1, order2):
    dist = 0
    # 依次计算从 order1 点 开始，order2-order1 个点的路段距离
    for i in range(order1, order2):
        dist += _get_point_dist(lst_node[i], lst_node[i + 1])

    return round(dist, 4)



# 在网络中寻找最短路径和距离
def _get_path(G, on_stop_id, off_stop_id):

    try:
        path = nx.dijkstra_path(G, source=on_stop_id, target=off_stop_id)
        dist = nx.dijkstra_path_length(G, source=on_stop_id, target=off_stop_id)
        if path:
            return [path, dist]

    except nx.NetworkXNoPath:
        return [None, None]


# 创建路径表
def _create_path(df_link_ride):

    df_stop = pd.read_csv(r'.\Output\Stop.csv', low_memory=False, encoding='gbk')
    df_link_walk = pd.read_csv(r'.\Output\Link_Walk.csv', low_memory=False, encoding='gbk')

    # 第一步：创建有向图
    G = nx.DiGraph()

    # 增加节点
    for i in range(df_stop.shape[0]):
        G.add_node(df_stop.loc[i, 'Stop_ID'])

    # 增加边（不含步行换乘）：起点ID，终点ID，阻抗
    lst_edge = []
    for i in range(df_link_ride.shape[0]):
        lst_edge.append([df_link_ride.loc[i, 'On_Stop_ID'], df_link_ride.loc[i, 'Off_Stop_ID'], df_link_ride.loc[i, 'Cost']])

    for i in range(0, len(lst_edge)):
        G.add_weighted_edges_from([(lst_edge[i][0], lst_edge[i][1], lst_edge[i][2])])

    arr_stop_id = df_stop['Stop_ID'].values
    arr_stop_route = df_stop['Route_ID'].values
    arr_stop_order = df_stop['Order'].values


    # 第二步：计算同线路站点间路径df_path_ride，即只有一次上车和下车
    lst_ride_path = []
    for i in range(df_stop.shape[0]):
        for j in range(df_stop.shape[0]):
            if i != j and arr_stop_route[i] == arr_stop_route[j] and arr_stop_order[i] < arr_stop_order[j]:
                [path, cost] = _get_path(G, arr_stop_id[i], arr_stop_id[j])
                lst_ride_path.append([arr_stop_route[i], arr_stop_id[i], arr_stop_id[j], arr_stop_order[i], arr_stop_order[j], path, cost])

    df_path_ride = pd.DataFrame(lst_ride_path, columns=['Route_ID', 'On_Stop_ID', 'Off_Stop_ID', 'On_Order', 'Off_Order', 'Path', 'Cost'])

    # 增加Cell字段
    df_path_ride = pd.merge(df_path_ride, df_stop, left_on='On_Stop_ID', right_on='Stop_ID', how='left')
    df_path_ride.rename(columns={'Cell': 'On_Cell'}, inplace=True)
    df_path_ride = pd.merge(df_path_ride, df_stop, left_on='Off_Stop_ID', right_on='Stop_ID', how='left')
    df_path_ride.rename(columns={'Cell': 'Off_Cell'}, inplace=True)
    df_path_ride = df_path_ride[['Route_ID', 'On_Stop_ID', 'Off_Stop_ID', 'On_Order', 'Off_Order', 'Path', 'On_Cell', 'Off_Cell', 'Cost']]


    # 第三步：建立包含第一次上下车和第二次上车的三站换乘路径
    df_path_transfer = pd.merge(df_path_ride, df_link_walk, left_on='Off_Stop_ID', right_on='On_Stop_ID', how='inner')
    df_path_transfer.rename(columns={
        'On_Route_ID': '1st_Route_ID',
        'Off_Route_ID': '2nd_Route_ID',
        'On_Stop_ID_x': '1st_On_Stop_ID',
        'Off_Stop_ID_x': '1st_Off_Stop_ID',
        'Off_Stop_ID_y': '2nd_On_Stop_ID',
        'On_Order_x': '1st_On_Order',
        'Off_Order_x': '1st_Off_Order',
        'Off_Order_y': '2nd_On_Order',
        'On_Cell': '1st_On_Cell',
        'Path': '1st_Path',
        'Cost_x': 'Cost_Ride',
        'Cost_y': 'Cost_Walk'}, inplace=True)
    df_path_transfer = df_path_transfer[['1st_Route_ID', '2nd_Route_ID',
                     '1st_On_Stop_ID', '1st_Off_Stop_ID', '2nd_On_Stop_ID',
                     '1st_On_Order', '1st_Off_Order', '2nd_On_Order', '1st_On_Cell', '1st_Path', 'Cost_Ride', 'Cost_Walk']]

    return [df_path_ride, df_path_transfer]


# 创建地图文件
def     create_gis():

    t0 = time.time()

    # 导入索引表
    df_index_line = pd.read_csv(r'.\Input\Index_Line.csv', low_memory=False, encoding='gbk')

    # 第一步：导入物理站点表，将物理站点转换为线路站点(不分方向），对站点进行清洗，建立临时站点表df_stop_temp
    df_phy_stop = pd.read_csv(r'.\Input\Phy_Stop.csv', low_memory=False, encoding='gbk')

    df_phy_stop['Stop_Name'] = df_phy_stop['Stop_Name'].str.replace('(', '', regex=True)
    df_phy_stop['Stop_Name'] = df_phy_stop['Stop_Name'].str.replace('公交站', '', regex=True)
    df_phy_stop['Stop_Name'] = df_phy_stop['Stop_Name'].str.replace(')', '', regex=True)

    lst_stop = []
    for i in range(df_phy_stop.shape[0]):
        phy_stop_id = df_phy_stop.loc[i, 'Phy_Stop_ID']
        stop_name = df_phy_stop.loc[i, 'Stop_Name']
        lng = df_phy_stop.loc[i, 'Lng']
        lat = df_phy_stop.loc[i, 'Lat']
        lst_lines = df_phy_stop.loc[i, 'Pass_Line_Name'].split(';')
        for j in range(len(lst_lines)):
            lst_stop.append([phy_stop_id, stop_name, lng, lat, lst_lines[j]])
    df_stop_temp = pd.DataFrame(lst_stop, columns=['Phy_Stop_ID', 'Stop_Name', 'Lng', 'Lat', 'Line_Name'])

    df_stop_temp = pd.merge(df_stop_temp, df_index_line, left_on='Line_Name', right_on='Line_Name', how='inner')
    df_stop_temp.drop_duplicates(inplace=True, subset=['Stop_Name', 'Line_Name'])
    df_stop_temp.rename(columns={'Line_ID_GIS': 'Line_ID'}, inplace=True)
    df_stop_temp.sort_values(by=['Line_ID', 'Phy_Stop_ID'], inplace=True)
    df_stop_temp = df_stop_temp.reset_index(drop=True)


    # 第二步：导入geo文件和Route文件，创建线路表（分方向），并对线路进行清洗，建立线路表df_route
    df_route = pd.read_csv(r'.\Input\Route.csv', low_memory=False, encoding='gbk')
    f1 = open(r'.\Input\Route.geo', 'r')
    lst_route_shp = []
    line = f1.readline()
    while line:
        lst_line_str = line.split(',')
        lst_line = [float(x) for x in lst_line_str]
        lst_xy = []
        p1 = [0, 0]
        for i in range(int(lst_line[1])):

            # 不存储过于接近的控制点
            p2 = [lst_line[2 + 2 * i], lst_line[3 + 2 * i]]
            if _get_point_dist(p1, p2) > 0.001:
                lst_xy.append([lst_line[2 + 2 * i], lst_line[3 + 2 * i]])
                p1 = p2

        line = f1.readline()
        lst_route_shp.append([int(lst_line[0]), lst_xy])

    df_route_shp = pd.DataFrame(lst_route_shp, columns=['Route_ID', 'Trail'])
    df_route = pd.merge(df_route, df_route_shp, left_on='Route_ID', right_on='Route_ID', how='inner')
    df_route['Match'] = df_route['Route_Name'].apply(_find_inmatch_string)
    df_route.dropna(axis=0, subset=['Match'], inplace=True)
    df_route = pd.merge(df_route, df_index_line, left_on='Line_ID', right_on='Line_ID_GIS', how='inner')
    df_route.drop_duplicates(inplace=True, subset=['Route_ID'])
    df_route.rename(columns={'Line_Name_x': 'Line_Name'}, inplace=True)
    df_route.sort_values(by=['Line_ID'], inplace=True)
    df_route = df_route.reset_index(drop=True)

    # 第三步：以不分方向的站点对分方向的线路轨迹逐段作垂线，确定站点顺序和方位角，建立新的站点表df_stop，同时将垂足信息加入轨迹列表以更新线路表df_route
    # 第一次遍历线路
    # 存储分方向的站点，并包含Route_ID、Order、方位角信息
    df_stop = pd.DataFrame()
    # 线路字段：轨迹
    lst_all_trail = []
    # 站点字段：垂足坐标、方位角、线路编号、线路名称
    lst_foot = []
    lst_azimuth = []
    lst_route_id = []
    lst_route_name = []

    for i in range(df_route.shape[0]):

        line_id = df_route.loc[i, 'Line_ID']
        route_id = df_route.loc[i, 'Route_ID']
        route_name = df_route.loc[i, 'Route_Name']
        df_stop_selected = df_stop_temp[(df_stop_temp['Line_ID'] == line_id)]
        df_stop_selected = df_stop_selected.reset_index(drop=True)

        # 提取线路轨迹集合
        lst_trail = df_route.loc[i, 'Trail']

        # 遍历与该线路Line_ID相同的站点
        for j in range(df_stop_selected.shape[0]):

            df_stop_current = df_stop_selected.loc[j]
            stop_xy = [df_stop_current['Lng'], df_stop_current['Lat']]

            # 距离、垂足坐标、在轨迹中的序号
            [dist, foot, order] = [max_foot_dist, [None, None], None]
            for k in range(len(lst_trail) - 1):
                [temp_dist, temp_foot] = _get_foot(stop_xy, lst_trail[k], lst_trail[k + 1])
                temp_dist = temp_dist * unit_coord2km
                if temp_dist < dist:
                    [dist, foot, order] = [temp_dist, temp_foot, k]

           # 如果能匹配到，即order不为空，则更新轨迹列表，并根据轨迹前后位置计算站点的方位角，将站点信息存起来
            if order:
                foot[0] = round(foot[0], 6)
                foot[1] = round(foot[1], 6)

                # 如果站点与既有轨迹点重合
                if foot in lst_trail:
                    # 如果与起点重合
                    if lst_trail.index(foot) == 0:
                        azimuth = _get_azimuth(lst_trail[0], lst_trail[1])
                    # 如果与其他点重合
                    else:
                        azimuth = _get_azimuth(lst_trail[lst_trail.index(foot) - 1], lst_trail[lst_trail.index(foot)])

                # 如果站点与既有轨迹点不重合
                else:
                    # 如果是距离起点最短
                    if order == 0 and foot == lst_trail[0]:
                        lst_trail.insert(0, foot)
                        azimuth = _get_azimuth(lst_trail[0], lst_trail[1])
                    # 如果是距离终点最短
                    elif order == len(lst_trail) - 1 and foot == lst_trail[-1]:
                        lst_trail.insert(-1, foot)
                        azimuth = _get_azimuth(lst_trail[-2], lst_trail[-1])
                    # 否则，一般情况下
                    else:
                        lst_trail.insert(order + 1, foot)
                        azimuth = _get_azimuth(lst_trail[order], lst_trail[order + 1])

                # 将能匹配到的站点信息添加至站点表
                lst_foot.append(foot)
                lst_azimuth.append(int(azimuth))
                lst_route_id.append(route_id)
                lst_route_name.append(route_name)
                df_stop = df_stop.append(df_stop_current)
                # df_stop = pd.concat([df_stop,df_stop_current])#ym修改2022.04.15

        # 遍历所有站点后，更新轨迹列表，添加站点方位角信息
        lst_all_trail.append(lst_trail)

    # 将列表添加为表字段
    df_stop['Foot'] = lst_foot
    df_stop['Azimuth'] = lst_azimuth
    df_stop['Route_ID'] = lst_route_id
    df_stop['Route_Name'] = lst_route_name
    df_route['Trail'] = lst_all_trail
    # 重置索引
    df_stop = df_stop.reset_index(drop=True)

    # 第二次遍历站点，寻找Order
    lst_foot_order = []
    for i in range(df_stop.shape[0]):
        route_id = df_stop.loc[i, 'Route_ID']
        foot = df_stop.loc[i, 'Foot']

        lst_trail = df_route[df_route['Route_ID'] == route_id]['Trail'].values[0]
        arr_dist = distance.cdist([foot], lst_trail) * unit_coord2km
        lst_foot_order.append(np.argmin(arr_dist))
    # 增加Foot_Order
    df_stop['Foot_Order'] = lst_foot_order

    # 根据Foot_Order排序并得到站点顺序
    df_stop.sort_values(by=['Line_ID', 'Route_ID', 'Foot_Order'], inplace=True)
    df_stop = df_stop.reset_index(drop=True)
    # 增加Stop_ID
    df_stop['Stop_ID'] = list(range(1, df_stop.shape[0] + 1))
    lst_order = [1]
    k = 1
    for i in range(df_stop.shape[0] - 1):
        route1 = df_stop.loc[i, 'Route_ID']
        route2 = df_stop.loc[i + 1, 'Route_ID']
        if route1 == route2:
            k += 1
        else:
            k = 1
        lst_order.append(k)
    df_stop['Order'] = lst_order


    # 第四步：构建公交网络，建立前后站间成本表df_link_ride和步行换乘成本表df_link_walk
    arr_route_id = df_stop['Route_ID'].values
    arr_stop_id = df_stop['Stop_ID'].values
    arr_foot_order = df_stop['Foot_Order'].values
    arr_order = df_stop['Order'].values
    arr_xy = df_stop[['Lng', 'Lat']].values
    arr_dist = distance.cdist(arr_xy, arr_xy) * unit_coord2km

    # 乘车成本，单向
    list_ride = []
    for i in range(df_stop.shape[0] - 1):
        if arr_route_id[i] == arr_route_id[i + 1]:
            lst_trail = df_route[df_route['Route_ID'] == arr_route_id[i]]['Trail'].values[0]
            dist = _get_link_dist(lst_trail, arr_foot_order[i], arr_foot_order[i + 1])
            list_ride.append([arr_route_id[i], arr_stop_id[i], arr_stop_id[i + 1], arr_order[i], arr_order[i + 1], dist])
    df_link_ride = pd.DataFrame(list_ride, columns=['Route_ID', 'On_Stop_ID', 'Off_Stop_ID', 'On_Order', 'Off_Order', 'Dist'])
    df_link_ride['Time'] = df_link_ride['Dist'] / bus_speed * 60
    df_link_ride['Volume'] = 0
    df_link_ride['Voc'] = df_link_ride['Volume'] / bus_capacity / (60 / bus_headway)
    df_link_ride['Cost'] = df_link_ride['Time'] * (1 + bpr_alpha * df_link_ride['Voc'] ** bpr_beta)


    # 步行换乘成本，双向
    lst_walk = []
    for i in range(df_stop.shape[0]):
        for j in range(df_stop.shape[0]):
            if arr_dist[i, j] <= max_transfer_dist and i != j:
                lst_walk.append([arr_route_id[i], arr_route_id[j], arr_stop_id[i], arr_stop_id[j], arr_order[i], arr_order[j], arr_dist[i, j]])
    df_link_walk = pd.DataFrame(lst_walk, columns=['On_Route_ID', 'Off_Route_ID', 'On_Stop_ID','Off_Stop_ID', 'On_Order', 'Off_Order', 'Dist'])
    df_link_walk['Time'] = df_link_walk['Dist'] / walk_speed * 60
    df_link_walk['Volume'] = 0
    df_link_walk['Cost'] = df_link_walk['Time']


    # 第五步：将站点坐标从高德转换为wgs84
    lst_wgs_x = []
    lst_wgs_y = []
    arr_xy = df_stop[['Lng', 'Lat']].values
    for i in range(df_stop.shape[0]):
        lst_wgs_x.append(gcj02_to_wgs84(arr_xy[i][0],arr_xy[i][1])[0])
        lst_wgs_y.append(gcj02_to_wgs84(arr_xy[i][0],arr_xy[i][1])[1])
    df_stop['Lng'] = lst_wgs_x
    df_stop['Lat'] = lst_wgs_y

    # 第六步：站点增加栅格信息
    # 精度西低东高，纬度南低北高，因此坐标轴方向与平面坐标系一致
    df_stop['Cell_X'] = ((df_stop['Lng'] - df_stop['Lng'].min()) * unit_coord2km / unit_cell).astype(int)
    df_stop['Cell_Y'] = ((df_stop['Lat'] - df_stop['Lat'].min()) * unit_coord2km / unit_cell).astype(int)

    # 一般城市的东西向在百公里级别，因为可以按照6位进行栅格化编号
    df_stop['Cell'] = df_stop['Cell_X'] * 1000 + df_stop['Cell_Y']
    df_stop['Cell_lng'] = df_stop['Lng'].min() + df_stop['Cell_X'] / unit_coord2km * unit_cell
    df_stop['Cell_lat'] = df_stop['Lat'].min() + df_stop['Cell_Y'] / unit_coord2km * unit_cell

    # 导出
    df_stop.to_csv(r'.\Output\Stop.csv', sep=',', header=True, index=False,
                          columns=['Stop_ID', 'Stop_Name', 'Phy_Stop_ID', 'Route_ID', 'Route_Name', 'Line_ID', 'Line_Name',
                                   'Lng', 'Lat', 'Cell_X', 'Cell_Y', 'Cell', 'Cell_lng', 'Cell_lat',
                                   'Azimuth', 'Foot_Order', 'Order'], encoding='gbk')
    df_route.to_csv(r'.\Output\Route.csv', sep=',', header=True, index=False,
                    columns=['Route_ID', 'Route_Name', 'Line_ID', 'Line_Name', 'Company', 'Mode_ID', 'Mode_Name', 'Trail'], encoding='gbk')
    df_link_ride.to_csv(r'.\Output\Link_Ride.csv', sep=',', header=True, index=False, encoding='gbk')
    df_link_walk.to_csv(r'.\Output\Link_Walk.csv', sep=',', header=True, index=False, encoding='gbk')


    # 第七步：创建路径
    [df_path_ride, df_path_transfer] = _create_path(df_link_ride)
    df_path_ride.to_csv(r'.\Output\Path_Ride.csv', sep=',', header=True, index=False, encoding='gbk')
    df_path_transfer.to_csv(r'.\Output\Path_Transfer.csv', sep=',', header=True, index=False, encoding='gbk')

    print(time.asctime(time.localtime(time.time())) + '创建地图文件完成，耗时：{:.1f}秒'.format(time.time() - t0))
    f.write(time.asctime(time.localtime(time.time())) + '创建地图文件完成，耗时：{:.1f}秒\n'.format(time.time() - t0))





# GPS数据到站识别
def get_arrival_time(date):

    # 第一步：GPS数据清洗
    '''
    清洗原则：
    1、删除重复记录
    2、删除不在索引表中的记录
    3、删除无效记录，如坐标为0、速度超过一定值（取10km/h）等
    4、转换日期时间为时间戳Timestamp（如有）
    5、按照线路编号、车辆编号和时间戳排序
    6、统一输出字段及顺序
    '''

    t0 = time.time()

    df_index_line = pd.read_csv(r'.\Input\Index_Line.csv', low_memory=False, encoding='gbk')
    df_gps = pd.read_csv(r'.\Input\T_Bus_GPS_{}.csv'.format(date), low_memory=False, encoding='gbk')
    df_stop = pd.read_csv(r'.\Output\Stop.csv', low_memory=False, encoding='gbk')
    rows1 = df_gps.shape[0]

    df_gps.drop_duplicates(inplace=True)
    df_gps = pd.merge(df_gps, df_index_line, left_on='Line_ID', right_on='Line_ID_GPS', how='inner')
    df_gps.drop(df_gps[(df_gps['Lng'] == 0) | (df_gps['Lat'] == 0) | (df_gps['Speed'] > 10)].index, inplace=True)
    df_gps['Timestamp'] = df_gps['DateTime'].apply(_time_str_to_timestamp)
    df_gps.drop(df_gps[(df_gps['Timestamp'] == 0)].index, inplace=True)
    df_gps = pd.DataFrame(df_gps, columns=['Line_ID', 'Bus_ID', 'Timestamp', 'Lng', 'Lat', 'Speed', 'Azimuth'])
    df_gps.drop_duplicates(inplace=True)
    df_gps.sort_values(by=['Line_ID', 'Bus_ID', 'Timestamp'], inplace=True)
    rows2 = df_gps.shape[0]

    print(time.asctime(time.localtime(time.time())) + '{}的GPS数据清洗完成，耗时：{:.1f}秒，清洗前行数：{}，清洗后行数：{}，清洗率：{:.0%}'.format(date, time.time() - t0, rows1, rows2,
                                                                        rows2 / rows1))
    f.write(time.asctime(time.localtime(time.time())) + '{}的GPS数据清洗完成，耗时：{:.1f}秒，清洗前行数：{}，清洗后行数：{}，清洗率：{:.0%}\n'.format(date, time.time() - t0, rows1, rows2,
                                                                            rows2 / rows1))

    # 第二步：到站时间识别
    t0 = time.time()
    rows1 = df_gps.shape[0]
    df_gps_match = pd.DataFrame()

    # 遍历线路
    for i in range(df_index_line.shape[0]):

        # 必须分块运算，不然效率太低
        line_id_gps = df_index_line.loc[i, 'Line_ID_GPS']
        line_id_gis = df_index_line.loc[i, 'Line_ID_GIS']
        df_gps_selected = df_gps[(df_gps['Line_ID'] == line_id_gps)]
        df_stop_selected = df_stop[(df_stop['Line_ID'] == line_id_gis)]

        # 保存相关列为数组
        arr_gps_xy = df_gps_selected[['Lng', 'Lat']].values
        arr_gps_azimuth = df_gps_selected['Azimuth'].values

        arr_stop_xy = df_stop_selected[['Lng', 'Lat']].values
        arr_stop_id = df_stop_selected['Stop_ID'].values
        arr_stop_azimuth = df_stop_selected['Azimuth'].values
        arr_route_id = df_stop_selected['Route_ID'].values
        arr_order = df_stop_selected['Order'].values

        # 利用dist模块计算距离矩阵
        arr_dist = distance.cdist(arr_gps_xy, arr_stop_xy) * unit_coord2km

        # 将距离矩阵转化为GPS对应的站点信息列表
        lst_stops = []
        for j in range(df_gps_selected.shape[0]):
            lst_stop = []
            temp_dist = max_gps2stop_dist
            for k in range(df_stop_selected.shape[0]):

                # 满足距离和方位角满足筛选条件，选择距离最近的一个站点
                if arr_dist[j, k] <= temp_dist and _get_azimuth_diff(arr_gps_azimuth[j], arr_stop_azimuth[k]) < max_azimuth_diff:
                    # stop列表格式
                    lst_stop = ([arr_stop_id[k], arr_route_id[k], arr_order[k], arr_dist[j, k]])
                    temp_dist = round(arr_dist[j, k], 4)

            # 空list转化为None，便于删除
            if len(lst_stop) == 0:
                lst_stop = None
            lst_stops.append(lst_stop)

        # 新建df_gps_selected_match数组，对无效GPS进行第二次清洗，原则为：
        # 1、去掉无匹配到站点的记录
        # 2、对于同一条Line下的相同车辆编号，时间间隔低于min_gps_interval（取5秒）并匹配同一站点的，只保留第1条记录
        df_gps_selected_match = df_gps_selected.copy()
        df_gps_selected_match['Stops'] = lst_stops
        df_gps_selected_match['Match'] = 1
        df_gps_selected_match['Stop_ID'] = None
        df_gps_selected_match.dropna(axis=0, subset=['Stops'], inplace=True)
        df_gps_selected_match = df_gps_selected_match.reset_index(drop=True)

        for j in range(df_gps_selected_match.shape[0] - 1):
            bus1 = df_gps_selected_match.loc[j, 'Bus_ID']
            bus2 = df_gps_selected_match.loc[j + 1, 'Bus_ID']
            timestamp1 = df_gps_selected_match.loc[j, 'Timestamp']
            timestamp2 = df_gps_selected_match.loc[j + 1, 'Timestamp']
            lst_stops1 = df_gps_selected_match.loc[j, 'Stops']
            lst_stops2 = df_gps_selected_match.loc[j + 1, 'Stops']
            if bus1 == bus2 and abs(timestamp1 - timestamp2) <= min_gps_interval and operator.eq(lst_stops1, lst_stops2):
                df_gps_selected_match.loc[j + 1, 'Match'] = 0
        df_gps_selected_match.drop(df_gps_selected_match[(df_gps_selected_match['Match'] == 0)].index, inplace=True)
        df_gps_selected_match = df_gps_selected_match.reset_index(drop=True)

        # 填充字段
        for j in range(df_gps_selected_match.shape[0]):
            lst_stops = df_gps_selected_match.loc[j, 'Stops']
            df_gps_selected_match.loc[j, 'Stop_ID'] = lst_stops[0]
            df_gps_selected_match.loc[j, 'Route_ID'] = lst_stops[1]
            df_gps_selected_match.loc[j, 'Order'] = lst_stops[2]
            df_gps_selected_match.loc[j, 'Dist'] = lst_stops[3]

        # 循环合并
        df_gps_match = df_gps_match.append(df_gps_selected_match)

    # 输出合并结果
    rows2 = df_gps_match.shape[0]
    df_gps_match.to_csv(r'.\Output\T_Bus_GPS_{}.csv'.format(date), sep=',', header=True, index=False,
                        columns=['Line_ID', 'Bus_ID', 'Timestamp', 'Lng',
                                 'Lat', 'Speed', 'Azimuth', 'Stop_ID', 'Route_ID', 'Order', 'Dist'], encoding='gbk')
    print(time.asctime(time.localtime(time.time())) + '{}的到站时间识别完成，耗时：{:.1f}秒，匹配前行数：{}，匹配后行数：{}，匹配率：{:.0%}'.format(date, time.time() - t0, rows1, rows2, rows2/rows1))
    f.write(time.asctime(time.localtime(time.time())) + '{}的到站时间识别完成，耗时：{:.1f}秒，清洗前行数：{}，清洗后行数：{}，清洗率：{:.0%}\n'.format(date, time.time() - t0, rows1, rows2, rows2 / rows1))


# 交易数据上车站点识别
def get_on_stop(date):

    # 第一步：交易数据清洗
    '''
    清洗原则：
    1、删除重复记录
    2、删除不在索引表中的记录
    3、删除无效记录，如无卡号、无车辆、无线路编号、非常规交易类型等
    4、转换日期时间为时间戳Timestamp（如有）
    5、按照卡号、时间戳排序
    6、统一输出字段及顺序
    '''

    t0 = time.time()

    df_index_line = pd.read_csv(r'.\Input\Index_Line.csv', low_memory=False, encoding='gbk')
    df_gps = pd.read_csv(r'.\Output\T_Bus_GPS_{}.csv'.format(date), low_memory=False, encoding='gbk')
    df_transaction = pd.read_csv(r'.\Input\T_Bus_Transaction_{}.csv'.format(date), low_memory=False, encoding='gbk')
    rows1 = df_transaction.shape[0]

    df_transaction.drop_duplicates(inplace=True)
    df_transaction = pd.merge(df_transaction, df_index_line, left_on='Line_ID', right_on='Line_ID_Transaction',
                              how='inner')
    df_transaction.drop(df_transaction[(df_transaction['Card_ID'] == 0) | ~(
        df_transaction['Card_Type'].isin(lst_match_card_type)) | (df_transaction['Bus_ID'] == 0) | (
                                                   df_transaction['Line_ID'] == 0)].index, inplace=True)
    df_transaction['Timestamp'] = df_transaction['DateTime'].apply(_time_str_to_timestamp)
    df_transaction = pd.DataFrame(df_transaction,
                                  columns=['Card_ID', 'Timestamp', 'Bus_ID', 'Line_ID', 'Card_Type', 'Price'])
    df_transaction.drop_duplicates(inplace=True)
    df_transaction.sort_values(by=['Card_ID', 'Timestamp'], inplace=True)
    rows2 = df_transaction.shape[0]


    print(time.asctime(time.localtime(time.time())) + '{}的交易数据清洗完成，耗时：{:.1f}秒，清洗前行数：{}，清洗后行数：{}，清洗率：{:.0%}'.format(date, time.time() - t0, rows1, rows2,
                                                                       rows2 / rows1))
    f.write(time.asctime(time.localtime(time.time())) + '{}的交易数据清洗完成，耗时：{:.1f}秒，清洗前行数：{}，清洗后行数：{}，清洗率：{:.0%}\n'.format(date, time.time() - t0, rows1, rows2,
                                                                           rows2 / rows1))

    # 第二步：上车站点识别
    t0 = time.time()

    rows1 = df_transaction.shape[0]
    df_transaction_on = pd.DataFrame()

    # 生成Bus_ID索引
    arr_bus_id = df_transaction['Bus_ID'].drop_duplicates().values

    # 遍历线路
    for i in range(len(arr_bus_id)):

        # 寻找相同车辆编号
        bus_id = arr_bus_id[i]
        df_gps_selected = df_gps[(df_gps['Bus_ID'] == bus_id)]
        df_transaction_selected = df_transaction[(df_transaction['Bus_ID'] == bus_id)]

        # 保存相关列为数组
        arr_transaction_timestamp = df_transaction_selected['Timestamp'].values
        arr_gps_timestamp = df_gps_selected['Timestamp'].values
        arr_stop_id = df_gps_selected['Stop_ID'].values
        arr_route_id = df_gps_selected['Route_ID'].values
        arr_order = df_gps_selected['Order'].values

        # 计算时间戳差值的绝对值矩阵
        arr_timestamp_diff = abs(np.subtract.outer(arr_transaction_timestamp, arr_gps_timestamp))

        # 寻找与交易时间最接近的GPS记录
        lst_stop_id = []
        lst_route_id = []
        lst_order = []
        for i in range(df_transaction_selected.shape[0]):
            [stop_id, route_id, order] = [None, None, None]
            temp_diff = max_transaction2gps_time
            for j in range(df_gps_selected.shape[0]):
                if arr_timestamp_diff[i, j] <= temp_diff:
                    [stop_id, route_id, order] = [arr_stop_id[j], arr_route_id[j], arr_order[j]]
                    temp_diff = arr_timestamp_diff[i, j]
            lst_stop_id.append(stop_id)
            lst_route_id.append(route_id)
            lst_order.append(order)

        # 新建df_transaction_selected_match数组，对无效数据进行第二次清洗，原则为：
        # 1、去掉无匹配到站点的记录
        df_transaction_selected_match = df_transaction_selected.copy()
        df_transaction_selected_match['Route_ID'] = lst_route_id
        df_transaction_selected_match['On_Stop_ID'] = lst_stop_id
        df_transaction_selected_match['On_Order'] = lst_order
        df_transaction_selected_match.dropna(axis=0, subset=['On_Stop_ID'], inplace=True)
        df_transaction_selected_match = df_transaction_selected_match.reset_index(drop=True)

        # 循环合并
        df_transaction_on = df_transaction_on.append(df_transaction_selected_match)

    rows2 = df_transaction_on.shape[0]

    df_transaction_on.to_csv(r'.\Output\T_Bus_Transaction_On_{}.csv'.format(date), sep=',', header=True, index=False,
                          columns=['Card_ID', 'Timestamp', 'Bus_ID', 'Line_ID', 'Card_Type', 'Price', 'Route_ID', 'On_Stop_ID', 'On_Order'], encoding='gbk')
    print(time.asctime(time.localtime(time.time())) + '{}的上车站点识别完成，耗时：{:.1f}秒，匹配前行数：{}，匹配后行数：{}，匹配率：{:.0%}'.format(date, time.time() - t0, rows1, rows2, rows2 / rows1))
    f.write(time.asctime(time.localtime(time.time())) + '{}的上车站点识别完成，耗时：{:.1f}秒，匹配前行数：{}，匹配后行数：{}，匹配率：{:.0%}\n'.format(date, time.time() - t0, rows1, rows2, rows2 / rows1))


# 统计上客量特征指标
def get_on_statictics():

    t0 = time.time()

    # 创建所有日的用户站点上客量表
    df_on_user_stop_date = pd.DataFrame()

    for k in range(len(lst_date)):
        date = lst_date[k]

        # 导入Transaction表
        df_transaction = pd.read_csv(r'.\Output\T_Bus_Transaction_On_{}.csv'.format(date), low_memory=False, encoding='gbk')

        # 合并指定用户在指定站点的上客量
        df_temp = df_transaction.groupby(['Card_ID', 'On_Stop_ID'])['On_Stop_ID'].count().reset_index(name='Count')
        df_temp['Date'] = date

        df_on_user_stop_date = df_on_user_stop_date.append(df_temp)

    # 合并日期，统计所有天中每个用户在各站点上客的比例
    df_on_user_stop = df_on_user_stop_date.groupby(['Card_ID', 'On_Stop_ID'])['Count'].sum().reset_index(name='Count')

    # 合并站点，统计每个用户在所有站点的总上客量并进行分类
    df_on_user_date = df_on_user_stop_date.groupby(['Card_ID', 'Date'])['On_Stop_ID'].count().reset_index(name='Count')
    df1 = df_on_user_date.groupby('Card_ID')['Card_ID'].count().reset_index(name='Total_Days')
    df2 = df_on_user_date.groupby('Card_ID')['Count'].sum().reset_index(name='Total_Trips')
    df_on_user = pd.merge(df1, df2, on='Card_ID', how='inner')
    df_on_user['User_Frequency'] = 'Low'
    df_on_user.loc[df_on_user['Total_Days'] >= frequent_rate * len(lst_date), ['User_Frequency']] = 'High'

    # 合并用户，统计各日期各站点的总上客量
    df_on_stop_date = df_on_user_stop_date.groupby(['On_Stop_ID', 'Date'])['Count'].sum().reset_index(name='Count')

    df_on_user_stop.to_csv(r'.\Output\T_On_User_Stop_{}.csv'.format(date_range), sep=',', header=True, index=False, encoding='gbk')
    df_on_user.to_csv(r'.\Output\T_On_User_{}.csv'.format(date_range), sep=',', header=True, index=False, encoding='gbk')
    df_on_stop_date.to_csv(r'.\Output\T_On_Stop_Date_{}.csv'.format(date_range), sep=',', header=True, index=False, encoding='gbk')

    print(time.asctime(time.localtime(time.time())) + '上客量统计完成，耗时：{:.1f}秒'.format(time.time() - t0))
    f.write(time.asctime(time.localtime(time.time())) + '上客量统计完成，耗时：{:.1f}秒\n'.format(time.time() - t0))


# 下车站点识别
def get_off_stop(date):

    t0 = time.time()

    # 导入若干表
    df_transaction = pd.read_csv(r'.\Output\T_Bus_Transaction_On_{}.csv'.format(date), low_memory=False, encoding='gbk')
    df_stop = pd.read_csv(r'.\Output\Stop.csv', low_memory=False, encoding='gbk')
    df_path_ride = pd.read_csv(r'.\Output\Path_Ride.csv', low_memory=False, encoding='gbk')
    df_path_transfer = pd.read_csv(r'.\Output\Path_Transfer.csv', low_memory=False, encoding='gbk')
    df_on_user = pd.read_csv(r'.\Output\T_On_User_{}.csv'.format(date_range), low_memory=False, encoding='gbk')
    df_on_user_stop = pd.read_csv(r'.\Output\T_On_User_Stop_{}.csv'.format(date_range), low_memory=False, encoding='gbk')
    df_on_stop_date = pd.read_csv(r'.\Output\T_On_Stop_Date_{}.csv'.format(date_range), low_memory=False, encoding='gbk')
    df_on_stop_date = df_on_stop_date[(df_on_stop_date['Date'] == date)]

    # 计算本次上车在各其他站点下车的概率，优先级依次为：
    # 如果用户当天存在出行链，根据下一次出行上车地点确定
    # 如果用户为高频乘客，根据该乘客在该线路下游站点的多天上客量确定
    # 如果用户为低频乘客，根据所有乘客在该线路下游车站当天上客量确定

    # 换乘初始化
    df_transaction['Transfer'] = 0

    # 根据用户出行天数，赋值Priority
    df_transaction = pd.merge(df_transaction, df_on_user, on='Card_ID', how='inner')
    df_transaction.loc[df_transaction['User_Frequency'] == 'High', 'Priority'] = 2
    df_transaction.loc[df_transaction['User_Frequency'] == 'Low', 'Priority'] = 3

    # 第一轮开始
    # 通过索引错位结合，提高效率
    df_transaction['Index'] = range(df_transaction.shape[0])
    df_transaction_copy = df_transaction.copy()
    df_transaction_copy['Index'] = range(-1, df_transaction.shape[0] - 1)
    df_transaction_copy = pd.DataFrame(df_transaction_copy,
                            columns=['Index', 'Card_ID', 'Route_ID', 'On_Stop_ID', 'On_Order', 'Timestamp'])
    df_transaction_1st = pd.merge(df_transaction, df_transaction_copy, on='Index', how='left')

    # 出行链必须同用户、异线路、时间存在先后关系
    df_transaction_1st = df_transaction_1st[(df_transaction_1st['Card_ID_x'] == df_transaction_1st['Card_ID_y']) &
                                                (df_transaction_1st['Route_ID_x'] != df_transaction_1st['Route_ID_y']) &
                                                (df_transaction_1st['Timestamp_y'] > df_transaction_1st['Timestamp_x'])]

    df_transaction_1st.rename(columns={'Card_ID_x': 'Card_ID', 'Route_ID_x': 'Route_ID'}, inplace=True)

    df_transaction_1st = pd.merge(df_transaction_1st, df_path_transfer,
                                                        left_on=['On_Stop_ID_x', 'On_Stop_ID_y'],
                                                        right_on=['1st_On_Stop_ID', '2nd_On_Stop_ID'], how='left')
    df_transaction_1st.drop(df_transaction_1st[(df_transaction_1st['Cost_Ride'].isnull())].index, inplace=True)
    df_transaction_1st.rename(columns={
                                    'Timestamp_x': 'Timestamp', 'On_Stop_ID_x': 'On_Stop_ID', 'On_Order_x': 'On_Order',
                                    '1st_Off_Stop_ID': 'Off_Stop_ID', '1st_Off_Order': 'Off_Order'}, inplace=True)
    df_transaction_1st['Priority'] = 1
    df_transaction_1st['Volume'] = 1
    df_transaction_1st = pd.DataFrame(df_transaction_1st,
                              columns=['Card_ID', 'Timestamp', 'Bus_ID', 'Line_ID', 'Card_Type', 'Price',
                                       'Route_ID', 'On_Stop_ID', 'On_Order', 'User_Frequency', 'Priority',
                                       'Off_Stop_ID', 'Off_Order', 'Off_Timestamp', 'Volume', 'Transfer', 'Timestamp_y'])

    # 估算车内时间，计算下车站点时间戳，通过前一次下车时间戳与后一次上车时间戳的间隔识别换乘
    df_transaction_1st = pd.merge(df_transaction_1st, df_path_ride,
                                  left_on=['On_Stop_ID', 'Off_Stop_ID', 'Route_ID'],
                                  right_on=['On_Stop_ID', 'Off_Stop_ID', 'Route_ID'], how='left')

    df_transaction_1st['Off_Timestamp'] = df_transaction_1st['Timestamp'] + (df_transaction_1st['Cost'] * 60).astype(int)
    df_transaction_1st['Diff_Timestamp'] = (df_transaction_1st['Off_Timestamp'] - df_transaction_1st['Timestamp_y']).abs().astype(int)
    df_transaction_1st.loc[(df_transaction_1st['Diff_Timestamp'] < max_transfer_time), 'Transfer'] = 1
    df_transaction_1st.rename(columns={'On_Order_x': 'On_Order', 'Off_Order_x': 'Off_Order'}, inplace=True)

    df_transaction_1st = df_transaction_1st.reset_index(drop=True)
    df_transaction_1st = pd.DataFrame(df_transaction_1st,
                              columns=['Card_ID', 'Timestamp', 'Bus_ID', 'Line_ID', 'Card_Type', 'Price',
                                       'Route_ID', 'On_Stop_ID', 'On_Order', 'User_Frequency', 'Priority',
                                       'Off_Stop_ID', 'Off_Order', 'Off_Timestamp', 'Volume', 'Transfer'])

    # 更新df_transaction
    df_temp = pd.DataFrame(df_transaction_1st, columns= ['Card_ID', 'Timestamp', 'On_Stop_ID', 'Volume'])
    df_transaction = pd.merge(df_transaction, df_temp, on=['Card_ID', 'Timestamp', 'On_Stop_ID'], how='left')
    df_transaction.loc[(df_transaction['Volume'] > 0), 'Priority'] = 1

    # 第二轮开始
    # 高频客：优先级二级
    df_transaction_2nd = df_transaction[(df_transaction['Priority'] == 2)]
    # 匹配df_on_user_stop与df_stop，获得站点的Route_ID和Order
    df_on_user_stop = pd.merge(df_on_user_stop, df_stop, left_on='On_Stop_ID', right_on='Stop_ID', how='inner')
    # 匹配df_transaction_2nd与df_on_user_stop，与用户和站点顺序有关
    df_transaction_2nd = pd.merge(df_transaction_2nd, df_on_user_stop, on=['Card_ID', 'Route_ID'], how='inner')
    df_transaction_2nd['Off_Stop_ID'] = df_transaction_2nd['Stop_ID']
    df_transaction_2nd['Off_Order'] = df_transaction_2nd['Order']
    df_transaction_2nd['Volume'] = df_transaction_2nd['Count']
    df_transaction_2nd.rename(columns={'Line_ID_x': 'Line_ID', 'On_Stop_ID_x': 'On_Stop_ID'}, inplace=True)
    df_transaction_2nd.drop(df_transaction_2nd[(df_transaction_2nd['On_Order'] >= df_transaction_2nd['Off_Order'])].index, inplace=True)
    df_transaction_2nd = df_transaction_2nd.reset_index(drop=True)
    # 计算概率
    df_transaction_2nd_sum = df_transaction_2nd.groupby(['Card_ID', 'Timestamp', 'On_Stop_ID'])['Volume'].sum().reset_index(name='Sum')
    df_transaction_2nd = pd.merge(df_transaction_2nd, df_transaction_2nd_sum, on=['Card_ID', 'Timestamp', 'On_Stop_ID'], how='inner')
    df_transaction_2nd['Volume'] = df_transaction_2nd['Volume'] / df_transaction_2nd['Sum']

    # 更新df_transaction，将匹配不到的优先级降为三级
    df_temp = pd.DataFrame(df_transaction_2nd, columns= ['Card_ID', 'Timestamp', 'On_Stop_ID', 'Volume'])
    df_temp.drop_duplicates(inplace=True, subset=['Card_ID', 'Timestamp', 'On_Stop_ID'])
    df_transaction = pd.merge(df_transaction, df_temp, on=['Card_ID', 'Timestamp', 'On_Stop_ID'], how='left')
    df_transaction.loc[(df_transaction['Volume_y'].isnull()) & (df_transaction['Priority'] > 1), 'Priority'] = 3
    df_transaction.rename(columns={'Volume_x': 'Volume'}, inplace=True)

    # 第三轮开始
    # 低频客：优先级三级
    df_transaction_3rd = df_transaction[(df_transaction['Priority'] == 3)]
    # 匹配df_on_stop_date与df_stop，获得站点的Route_ID和Order
    df_on_stop_date = pd.merge(df_on_stop_date, df_stop, left_on='On_Stop_ID', right_on='Stop_ID', how='inner')
    # 匹配df_transaction_2nd与df_on_user_stop，与用户和站点顺序有关
    df_transaction_3rd = pd.merge(df_transaction_3rd, df_on_stop_date, on='Route_ID', how='inner')
    df_transaction_3rd['Off_Stop_ID'] = df_transaction_3rd['Stop_ID']
    df_transaction_3rd['Off_Order'] = df_transaction_3rd['Order']
    df_transaction_3rd['Volume'] = df_transaction_3rd['Count']
    df_transaction_3rd.rename(columns={'Line_ID_x': 'Line_ID', 'On_Stop_ID_x': 'On_Stop_ID'}, inplace=True)
    df_transaction_3rd.drop(df_transaction_3rd[(df_transaction_3rd['On_Order'] >= df_transaction_3rd['Off_Order'])].index, inplace=True)
    df_transaction_3rd = df_transaction_3rd.reset_index(drop=True)
    # 计算概率
    df_transaction_3rd_sum = df_transaction_3rd.groupby(['Card_ID', 'Timestamp', 'On_Stop_ID'])['Volume'].sum().reset_index(name='Sum')
    df_transaction_3rd = pd.merge(df_transaction_3rd, df_transaction_3rd_sum, on=['Card_ID', 'Timestamp', 'On_Stop_ID'], how='inner')
    df_transaction_3rd['Volume'] = df_transaction_3rd['Volume'] / df_transaction_3rd['Sum']

    # 三张表合并
    df_transaction_off = pd.concat([df_transaction_1st, df_transaction_2nd, df_transaction_3rd], axis=0)

    # 估算车内时间，计算下车站点时间戳
    df_transaction_off = pd.merge(df_transaction_off, df_path_ride,
                                  left_on=['On_Stop_ID', 'Off_Stop_ID', 'Route_ID'],
                                  right_on=['On_Stop_ID', 'Off_Stop_ID', 'Route_ID'], how='left')
    df_transaction_off.rename(columns={'On_Order_x': 'On_Order', 'Off_Order_x': 'Off_Order'}, inplace=True)
    df_transaction_off['Off_Timestamp'] = df_transaction_off['Timestamp'] + (df_transaction_off['Cost'] * 60).astype(int)

    # 标准化
    df_transaction_off.sort_values(by=['Card_ID', 'Timestamp'], inplace=True)
    df_transaction_off = df_transaction_off.reset_index(drop=True)
    df_transaction_off = pd.DataFrame(df_transaction_off, columns=['Card_ID', 'Timestamp', 'Bus_ID', 'Line_ID', 'Card_Type', 'Price',
                                       'Route_ID', 'On_Stop_ID', 'On_Order', 'User_Frequency', 'Priority',
                                       'Off_Stop_ID', 'Off_Order', 'Off_Timestamp', 'Volume', 'Transfer'])

    df_transaction_off.to_csv(r'.\Output\T_Bus_Transaction_Off_{}.csv'.format(date), sep=',', header=True, index=False, encoding='gbk')

    # 统计优先级比例
    df_transaction_off_group = df_transaction_off.groupby('Priority')['Volume'].sum().reset_index(name='Sum')
    df_transaction_off_group['Rate'] = df_transaction_off_group['Sum'] / df_transaction_off_group['Sum'].sum()
    arr_rate = df_transaction_off_group['Rate'].values
    transfer_rate = df_transaction_off[df_transaction_off['Transfer'] == 1]['Volume'].sum() / df_transaction_off[df_transaction_off['Priority'] == 1]['Volume'].sum()

    print(time.asctime(time.localtime(time.time())) + '下车站点识别完成，耗时：{:.1f}秒，其中出行链识别率：{:.0%}，高频旅客单次出行占比：{:.0%}，低频旅客单次出行占比：{:.0%}，换乘占比：{:.0%}'.format(time.time() - t0, arr_rate[0], arr_rate[1], arr_rate[2], transfer_rate))
    f.write(time.asctime(time.localtime(time.time())) + '下车站点识别完成，耗时：{:.1f}秒，其中出行链识别率：{:.0%}，高频旅客单次出行占比：{:.0%}，低频旅客单次出行占比：{:.0%}，换乘占比：{:.0%}\n'.format(time.time() - t0, arr_rate[0], arr_rate[1], arr_rate[2], transfer_rate))


def get_transfer(date):

    t0 = time.time()

    df_transaction = pd.read_csv(r'.\Output\T_Bus_Transaction_Off_{}.csv'.format(date), low_memory=False, encoding='gbk')
    df_transaction = pd.DataFrame(df_transaction, columns=['Card_ID', 'Card_Type', 'On_Stop_ID', 'Timestamp', 'Off_Stop_ID', 'Off_Timestamp', 'Volume', 'Transfer'])

    lst_flag = df_transaction[df_transaction['Transfer'] == 1].index.tolist()
    lst_row = []
    lst_on_stop_id = []
    lst_timestamp = []

    # 找到换乘记录
    for i in range(len(lst_flag)):
        row1 = lst_flag[i]
        on_stop_id1 = df_transaction.iloc[row1]['On_Stop_ID']
        timestamp1 = df_transaction.iloc[row1]['Timestamp']

        # 查找换乘记录后续若干字段相同的行
        row2 = lst_flag[i] + 1
        card_id2 = df_transaction.iloc[row2]['Card_ID']
        on_stop_id2 = df_transaction.iloc[row2]['On_Stop_ID']
        timestamp2 = df_transaction.iloc[row2]['Timestamp']
        volume2 = df_transaction.iloc[row2]['Volume']

        lst_row2 = df_transaction[(df_transaction['Card_ID'] == card_id2) &
                                  (df_transaction['On_Stop_ID'] == on_stop_id2) &
                                  (df_transaction['Timestamp'] == timestamp2)].index.tolist()
        lst_row += lst_row2
        lst_on_stop_id += [on_stop_id1] * len(lst_row2)
        lst_timestamp += [timestamp1] * len(lst_row2)

    # 修正
    df_transaction.iloc[lst_row, df_transaction.columns.get_loc('On_Stop_ID')] = lst_on_stop_id
    df_transaction.iloc[lst_row, df_transaction.columns.get_loc('Timestamp')] = lst_timestamp
    df_transaction.iloc[lst_row, df_transaction.columns.get_loc('Volume')] *= 2

    df_transaction.loc[(df_transaction['Transfer'] == 1), 'Volume'] = 0
    df_transaction = df_transaction.reset_index(drop=True)

    df_transaction.to_csv(r'.\Output\T_Bus_Transaction_No_Transfer_{}.csv'.format(date), sep=',', header=True, index=False, encoding='gbk')

    print(time.asctime(time.localtime(time.time())) + '换乘修正完成，耗时：{:.1f}秒'.format(time.time() - t0))
    f.write(time.asctime(time.localtime(time.time())) + '换乘修正完成，耗时：{:.1f}秒\n'.format(time.time() - t0))

def get_od():

    t0 = time.time()

    df_stop = pd.read_csv(r'.\Output\Stop.csv', low_memory=False, encoding='gbk')

    df_od1 = pd.DataFrame()
    df_od2 = pd.DataFrame()

    for k in range(len(lst_date)):

        date = lst_date[k]

        # 统计含换乘的OD
        df_transaction = pd.read_csv(r'.\Output\T_Bus_Transaction_Off_{}.csv'.format(date), low_memory=False, encoding='gbk')

        # 将时间戳转化为时间片
        df_transaction['Time_Interval'] = df_transaction['Timestamp'].apply(_timestamp_to_time_interval)

        # 统计用户上客量
        df_od1_date = df_transaction.groupby(['On_Stop_ID', 'Off_Stop_ID', 'Route_ID', 'Time_Interval'])['Volume'].sum().reset_index(name='Volume')
        df_od1_date['Date'] = date
        df_od1 = df_od1.append(df_od1_date)

        # 统计不含换乘的OD
        df_transaction = pd.read_csv(r'.\Output\T_Bus_Transaction_No_Transfer_{}.csv'.format(date), low_memory=False,
                                     encoding='gbk')

        # 将时间戳转化为时间片
        df_transaction['Time_Interval'] = df_transaction['Timestamp'].apply(_timestamp_to_time_interval)

        # 统计用户上客量
        df_od2_date = df_transaction.groupby(['On_Stop_ID', 'Off_Stop_ID', 'Time_Interval'])['Volume'].sum().reset_index(
            name='Volume')
        df_od2_date['Date'] = date
        df_od2 = df_od2.append(df_od2_date)

    # 不含换乘OD：增加的线路编号
    df_od2 = pd.merge(df_od2, df_stop, left_on='On_Stop_ID', right_on='Stop_ID', how='left')
    df_od2 = df_od2[['On_Stop_ID', 'Off_Stop_ID', 'Route_ID', 'Time_Interval', 'Volume', 'Date']]
    df_od2.rename(columns={'Route_ID': 'On_Route_ID'}, inplace=True)

    df_od2 = pd.merge(df_od2, df_stop, left_on='Off_Stop_ID', right_on='Stop_ID', how='left')
    df_od2 = df_od2[['On_Stop_ID', 'Off_Stop_ID', 'On_Route_ID', 'Route_ID', 'Time_Interval', 'Volume', 'Date']]
    df_od2.rename(columns={'Route_ID': 'Off_Route_ID'}, inplace=True)

    df_od1.to_csv(r'.\Output\T_OD_Transfer_{}.csv'.format(date_range), sep=',', header=True, index=False, encoding='gbk')
    df_od2.to_csv(r'.\Output\T_OD_No_Transfer_{}.csv'.format(date_range), sep=',', header=True, index=False, encoding='gbk')

    # 对不含换乘的OD栅格化，获得分区OD
    df_od2 = pd.merge(df_od2, df_stop, left_on='On_Stop_ID', right_on='Stop_ID', how='left')
    df_od2 = df_od2[
        ['On_Stop_ID', 'Off_Stop_ID', 'On_Route_ID', 'Off_Route_ID', 'Cell', 'Time_Interval', 'Volume', 'Date']]
    df_od2.rename(columns={'Cell': 'On_Cell'}, inplace=True)

    df_od2 = pd.merge(df_od2, df_stop, left_on='Off_Stop_ID', right_on='Stop_ID', how='left')
    df_od2 = df_od2[
        ['On_Stop_ID', 'Off_Stop_ID', 'On_Route_ID', 'Off_Route_ID', 'On_Cell', 'Cell', 'Time_Interval', 'Volume',
         'Date']]
    df_od2.rename(columns={'Cell': 'Off_Cell'}, inplace=True)

    # 按栅格聚合
    df_od_zonal = df_od2.groupby(['On_Cell', 'Off_Cell', 'Time_Interval', 'Date'])['Volume'].sum().reset_index(
        name='Volume')
    df_od_zonal.to_csv(r'.\Output\T_OD_No_Transfer_Zonal_{}.csv'.format(date_range), sep=',', header=True, index=False,
                       encoding='gbk')

    # 再按时间片聚合
    df_od_zonal_daily = df_od_zonal.groupby(['On_Cell', 'Off_Cell', 'Date'])['Volume'].sum().reset_index()
    df_od_zonal_daily.to_csv(r'.\Output\T_OD_No_Transfer_Zonal_Daily_{}.csv'.format(date_range), sep=',', header=True, index=False,
                       encoding='gbk')

    # 再按日期聚合
    df_trips_daily = df_od_zonal_daily.groupby(['Date'])['Volume'].sum().reset_index()
    df_trips_daily.to_csv(r'.\Output\T_Trips_Daily_{}.csv'.format(date_range), sep=',', header=True, index=False,
                       encoding='gbk')

    print(time.asctime(time.localtime(time.time())) + '站点OD统计完成，耗时：{:.1f}秒'.format(time.time() - t0))
    f.write(time.asctime(time.localtime(time.time())) + '站点OD统计完成，耗时：{:.1f}秒\n'.format(time.time() - t0))


# 对含换乘的OD，统计客流指标
def statistics(date=None):

    t0 = time.time()

    df_link_ride = pd.read_csv(r'.\Output\Link_Ride.csv', low_memory=False, encoding='gbk')
    df_path_ride = pd.read_csv(r'.\Output\Path_Ride.csv', low_memory=False, encoding='gbk')
    df_od = pd.read_csv(r'.\Output\T_OD_Transfer_{}.csv'.format(date_range), low_memory=False, encoding='gbk')

    # 如果有参数，则某一天，否则所有天
    if date:
        df_od = df_od[(df_od['Date'] == date)]

    # 第一步：统计分时客流
    df_statistics_time_interval = df_od.groupby(['Time_Interval'])['Volume'].sum().reset_index()

    # 第二步：统计线路客流
    # 合并Date和Time_Interval
    df_od = df_od.groupby(['On_Stop_ID', 'Off_Stop_ID', 'Route_ID'])['Volume'].sum().reset_index(name='Volume')

    # 添加路径和成本
    df_od = pd.merge(df_od, df_path_ride, on=['Route_ID', 'On_Stop_ID', 'Off_Stop_ID'], how='left')

    # 计算VHT
    df_od['VHT'] = df_od['Volume'] * df_od['Cost']

    # 统计线路客流，包含客运量、VMT、乘距
    df_statistics_route = df_od.groupby(['Route_ID'])[['Volume', 'VHT']].sum().reset_index()
    df_statistics_route['Avg_IVT'] = round(df_statistics_route['VHT'] / df_statistics_route['Volume'], 2)

    # 第三步：统计断面客流
    # 将客流添加至link
    lst_link_volume = []
    for i in range(df_od.shape[0]):
        vol = df_od.loc[i, 'Volume']

        path = df_od.loc[i, 'Path']
        if path:
            # 注意：将字符串转化为向量
            path = path.strip('[]').split(',')
            path = list(map(int, path))
            for j in range(len(path) - 1):
                lst_link_volume.append([path[j], path[j + 1], vol])

    df_link_volume = pd.DataFrame(lst_link_volume, columns=['On_Stop_ID', 'Off_Stop_ID', 'Volume'])
    df_link_volume = df_link_volume.groupby(['On_Stop_ID', 'Off_Stop_ID'])['Volume'].sum().reset_index(name='Volume')

    # 更新df_link_ride
    df_link_ride_statistics = pd.merge(df_link_ride, df_link_volume, on=['On_Stop_ID', 'Off_Stop_ID'], how='left')
    df_link_ride_statistics['Volume_y'].fillna(0, inplace=True)
    df_link_ride_statistics.rename(columns={'Volume_y': 'Volume'}, inplace=True)
    df_link_ride_statistics['Voc'] = df_link_ride_statistics['Volume'] / bus_capacity / (60 / bus_headway)
    df_link_ride_statistics['Cost'] = df_link_ride_statistics['Time'] * (1 + bpr_alpha * df_link_ride_statistics['Voc'] ** bpr_beta)
    df_link_ride_statistics = df_link_ride_statistics[
        ['Route_ID', 'On_Stop_ID', 'Off_Stop_ID', 'On_Order', 'Off_Order', 'Dist', 'Time', 'Cost', 'Volume', 'Voc']]

    # 导出
    if date:
        df_statistics_time_interval.to_csv(r'.\Output\T_Statistics_Time_Interval_{}.csv'.format(date), sep=',', header=True, index=False, encoding='gbk')
        df_statistics_route.to_csv(r'.\Output\T_Statistics_Route_{}.csv'.format(date), sep=',', header=True, index=False, encoding='gbk')
        df_link_ride_statistics.to_csv(r'.\Output\Link_Ride_Statistics_{}.csv'.format(date), sep=',', header=True, index=False, encoding='gbk')
    else:
        df_statistics_time_interval.to_csv(r'.\Output\T_Statistics_Time_Interval_{}.csv'.format(date_range), sep=',', header=True, index=False, encoding='gbk')
        df_statistics_route.to_csv(r'.\Output\T_Statistics_Route_{}.csv'.format(date_range), sep=',', header=True, index=False,  encoding='gbk')
        df_link_ride_statistics.to_csv(r'.\Output\T_Link_Ride_Statistics_{}.csv'.format(date_range), sep=',', header=True, index=False, encoding='gbk')

    print(time.asctime(time.localtime(time.time())) + '结果统计完成，耗时：{:.1f}秒'.format(time.time() - t0))
    f.write(time.asctime(time.localtime(time.time())) + '结果统计完成，耗时：{:.1f}秒\n'.format(time.time() - t0))


# 对不含换乘的OD，进行多路径增量公交分配
def assignment(date):

    t0 = time.time()

    df_link_ride = pd.read_csv(r'.\Output\Link_Ride.csv', low_memory=False, encoding='gbk')
    df_path_ride = pd.read_csv(r'.\Output\Path_Ride.csv', low_memory=False, encoding='gbk')
    df_path_transfer = pd.read_csv(r'.\Output\Path_Transfer.csv', low_memory=False, encoding='gbk')

    df_od_zonal = pd.read_csv(r'.\Output\T_OD_No_Transfer_Zonal_{}.csv'.format(date_range), low_memory=False, encoding='gbk')
    df_od_zonal = df_od_zonal[(df_od_zonal['Date'] == date) & (df_od_zonal['Time_Interval'] >= peak_time_interval) & (df_od_zonal['Time_Interval'] < peak_time_interval + 4)]
    df_od_zonal.drop(df_od_zonal[(df_od_zonal['On_Cell'] == df_od_zonal['Off_Cell'])].index, inplace=True)
    df_od_zonal = df_od_zonal.groupby(['On_Cell', 'Off_Cell'])['Volume'].sum().reset_index(name='Volume')
    df_od_zonal['Volume'] = df_od_zonal['Volume'] / iters

    for iter in range(iters):

        print('公交分配第{}/{}次迭代计算中'.format(iter + 1, iters))

        # 第一步：关联换乘路径表的第二次上客站与非换乘路径表的上客站，得到经过一次换乘的完整路径表，即第一次上车、第一次下车、第二次上车、第二次下车的四站换乘路径
        df_path_chain = pd.merge(df_path_transfer, df_path_ride, left_on='2nd_On_Stop_ID', right_on='On_Stop_ID',
                                 how='left')
        df_path_chain.rename(columns={'Off_Stop_ID': '2nd_Off_Stop_ID',
                                      'Off_Cell': '2nd_Off_Cell',
                                      'Cost_Ride': '1st_Cost_Ride',
                                      'Cost': '2nd_Cost_Ride',
                                      'Path': '2nd_Path',
                                      }, inplace=True)

        # 阻抗为两次乘车时间+步行时间加权+候车时间加权+准点率惩罚
        df_path_chain['Cost'] = df_path_chain['1st_Cost_Ride'] + \
                                df_path_chain['Cost_Walk'] * weight_walk + \
                                df_path_chain['2nd_Cost_Ride'] + \
                                min(max_wait_time, bus_headway / 2) * weight_wait + \
                                (df_path_chain['1st_Cost_Ride'] + df_path_chain['2nd_Cost_Ride']) * penalty_on_time_rate

        df_path_chain = df_path_chain[['1st_Route_ID', '2nd_Route_ID',
                                       '1st_On_Stop_ID', '1st_Off_Stop_ID', '2nd_On_Stop_ID', '2nd_Off_Stop_ID',
                                       '1st_Path', '2nd_Path',
                                       '1st_On_Cell', '2nd_Off_Cell', 'Cost']]

        # 每个站点对最多只保留3条路径
        df_path_chain.sort_values(by=['1st_On_Stop_ID', '2nd_Off_Stop_ID', 'Cost'], inplace=True)
        arr_1st_on_stop_id = df_path_chain['1st_On_Stop_ID'].values
        arr_2nd_off_stop_id = df_path_chain['2nd_Off_Stop_ID'].values
        lst_flag = []
        on_stop_id = 0
        off_stop_id = 0
        k = 0
        for i in range(len(arr_1st_on_stop_id)):
            if arr_1st_on_stop_id[i] == on_stop_id and arr_2nd_off_stop_id[i] == off_stop_id:
                k += 1
            else:
                on_stop_id = arr_1st_on_stop_id[i]
                off_stop_id = arr_2nd_off_stop_id[i]
                k = 1
            lst_flag.append(k)
        df_path_chain['Flag'] = lst_flag
        df_path_chain.drop(df_path_chain[(df_path_chain['Flag'] > 3)].index, inplace=True)


        # 第二步：拼接df_Path_ride与df_path_chain为df_path_all，包含直达及一次换乘的全路径
        # 临时变更，便于合并表格及寻找路径
        df_path_ride.rename(columns={'Route_ID': '1st_Route_ID',
                                     'On_Stop_ID': '1st_On_Stop_ID',
                                     'Off_Stop_ID': '1st_Off_Stop_ID',
                                     'On_Cell': '1st_On_Cell',
                                     'Off_Cell': '2nd_Off_Cell',
                                     'Path': '1st_Path'}, inplace=True)
        df_path_ride = df_path_ride[
            ['1st_Route_ID', '1st_On_Stop_ID', '1st_Off_Stop_ID', '1st_On_Cell', '2nd_Off_Cell', '1st_Path', 'Cost']]

        df_path_all = pd.concat([df_path_ride, df_path_chain], ignore_index=True)


        # 第三步：df_path_all与OD关联，获得OD对所有可能的路径
        # 每个Cell对最多只保留3条路径
        df_od_multi_path = pd.merge(df_od_zonal, df_path_all, left_on=['On_Cell', 'Off_Cell'], right_on=['1st_On_Cell', '2nd_Off_Cell'], how='left')
        df_od_multi_path.sort_values(by=['On_Cell', 'Off_Cell', 'Cost'], inplace=True)
        arr_on_cell = df_od_multi_path['On_Cell'].values
        arr_off_cell = df_od_multi_path['Off_Cell'].values
        lst_flag = []
        on_cell = 0
        off_cell = 0
        k = 0
        for i in range(len(arr_on_cell)):
            if arr_on_cell[i] == on_cell and arr_off_cell[i] == off_cell:
                k += 1
            else:
                on_cell = arr_on_cell[i]
                off_cell = arr_off_cell[i]
                k = 1
            lst_flag.append(k)
        df_od_multi_path['Flag'] = lst_flag
        df_od_multi_path.drop(df_od_multi_path[(df_od_multi_path['Flag'] > 3)].index, inplace=True)


        # 第四步：计算多路径概率
        df_od_multi_path_mean = df_od_multi_path.groupby(['On_Cell', 'Off_Cell'])['Cost'].mean().reset_index(name='Mean')
        df_od_multi_path = pd.merge(df_od_multi_path, df_od_multi_path_mean, on=['On_Cell', 'Off_Cell'], how='left')
        df_od_multi_path['Func_Cost'] = (- 3 * df_od_multi_path['Cost'] / df_od_multi_path['Mean']).apply(np.exp)
        df_od_multi_path_sum = df_od_multi_path.groupby(['On_Cell', 'Off_Cell'])['Func_Cost'].sum().reset_index(name='Sum')
        df_od_multi_path = pd.merge(df_od_multi_path, df_od_multi_path_sum, on=['On_Cell', 'Off_Cell'], how='left')
        df_od_multi_path['Pro'] = df_od_multi_path['Func_Cost'] / df_od_multi_path['Sum']
        df_od_multi_path['Volume'] = df_od_multi_path['Volume'] * df_od_multi_path['Pro']

        df_od_multi_path = df_od_multi_path[['On_Cell', 'Off_Cell', 'Volume', '1st_Route_ID', '2nd_Route_ID',
                             '1st_Path', '2nd_Path', 'Cost', 'Pro']]
        df_od_multi_path.dropna(subset=['1st_Path'], inplace=True)
        df_od_multi_path = df_od_multi_path.reset_index(drop=True)
        df_od_multi_path.fillna(value={'2nd_Path': 0}, inplace=True)

        # 第五步：将客流添加至link
        lst_link_volume = []
        for i in range(df_od_multi_path.shape[0]):
            vol = df_od_multi_path.loc[i, 'Volume']

            path = df_od_multi_path.loc[i, '1st_Path']
            if path:
                # 注意：将字符串转化为向量
                if isinstance(path, str):
                    path = path.strip('[]').split(',')
                    path = list(map(int, path))
                for j in range(len(path) - 1):
                    lst_link_volume.append([path[j], path[j + 1], vol])

            path = df_od_multi_path.loc[i, '2nd_Path']
            # 考虑不换乘情况
            if path != 0:
                # 注意：将字符串转化为向量
                if isinstance(path, str):
                    path = path.strip('[]').split(',')
                    path = list(map(int, path))
                for j in range(len(path) - 1):
                    lst_link_volume.append([path[j], path[j + 1], vol])

        df_link_volume = pd.DataFrame(lst_link_volume, columns=['On_Stop_ID', 'Off_Stop_ID', 'Volume'])
        df_link_volume = df_link_volume.groupby(['On_Stop_ID', 'Off_Stop_ID'])['Volume'].sum().reset_index(name='Volume')


        # 第六步：更新df_link_ride，注意增量分配法
        df_link_ride = pd.merge(df_link_ride, df_link_volume, on=['On_Stop_ID', 'Off_Stop_ID'], how='left')
        df_link_ride['Volume_x'].fillna(0, inplace=True)
        df_link_ride['Volume_y'].fillna(0, inplace=True)
        df_link_ride['Volume_x'] = df_link_ride['Volume_x'] + df_link_ride['Volume_y']
        df_link_ride.rename(columns={'Volume_x': 'Volume'}, inplace=True)
        df_link_ride['Voc'] = df_link_ride['Volume'] / bus_capacity / (60 / bus_headway)
        df_link_ride['Cost'] = df_link_ride['Time'] * (1 + bpr_alpha * df_link_ride['Voc'] ** bpr_beta)
        df_link_ride = df_link_ride[['Route_ID', 'On_Stop_ID', 'Off_Stop_ID', 'On_Order', 'Off_Order', 'Dist', 'Time', 'Cost', 'Volume', 'Voc']]

        # 第七步：更新路径表
        [df_path_ride, df_path_transfer] = _create_path(df_link_ride)

    df_link_ride.to_csv(r'.\Output\T_Link_Ride_Assignment_{}.csv'.format(date), sep=',', header=True, index=False, encoding='gbk')

    print(time.asctime(time.localtime(time.time())) + '公交分配完成，耗时：{:.1f}秒'.format(time.time() - t0))
    f.write(time.asctime(time.localtime(time.time())) + '公交分配完成，耗时：{:.1f}秒\n'.format(time.time() - t0))


# 主函数
def main(step):

    # pd.set_option('display.width', 300)  # 设置字符显示宽度
    # pd.set_option('display.max_rows', None)  # 设置显示最大行
    # pd.set_option('display.max_columns', None)  # 设置显示最大列，None为显示所有列

    # 日期列表
    global lst_date, date_range
    # 指定起止日期，1-9月份前面要有0
    date_start = '2019.09.1'
    date_end = '2019.09.30'
    # 指定具体日期列表，可不填，如果填了，则优先级更高
    lst_date = ''
    if len(lst_date) == 0:
        lst_date = _get_lst_date(date_start, date_end)
    date_range = lst_date[0] + '-' + lst_date[-1]

    # 程序运行日志
    t0 = time.time()

    global f
    f = open(r'.\Output\result.txt', 'a')
    f.write('\n----------------------------------------------------\n')

    # 关键参数
    global lst_inmatch_route_name, lst_match_card_type
    global unit_time_interval, unit_coord2km, unit_cell
    global bus_speed, bus_capacity, bus_headway, bpr_alpha, bpr_beta, walk_speed
    global max_foot_dist, max_transfer_dist, max_gps2stop_dist, max_azimuth_diff, min_gps_interval, max_transaction2gps_time, max_transfer_time
    global frequent_rate, weight_walk,  weight_wait, max_wait_time, penalty_on_time_rate
    global iters, peak_time_interval

    lst_inmatch_route_name = ['夜间', '晚班', '区间', '临时', '停运']      # 无效的线路名称关键词
    lst_match_card_type = [2, 3, 4, 6, 10, 11, 101]                    # 有效交易类型：2 - 异型卡；3 - 纪念卡；4 - 学生卡；6 - 老人卡；10 - 离休卡；11 - 老年人免费卡：101 - 正常卡

    unit_time_interval = 15                                            # 时间片划分，单位为分钟，默认15分钟
    unit_coord2km = 111                                                # 坐标换算为距离的转换系数，单位公里，默认111公里
    unit_cell = 0.5                                                    # 栅格大小，单位公里，默认0.5公里

    bus_speed = 20                                                     # 公交速度，单位公里/小时，默认20公里/小时
    bus_capacity = 50                                                  # 公交运输能力，单位人次/车，默认50人次/车
    bus_headway = 5                                                    # 公交发车间隔，单位分钟，默认5分钟
    bpr_alpha = 0.15                                                   # 公交阻抗函数参数，默认0.15
    bpr_beta = 4                                                       # 公交阻抗函数参数，默认4
    walk_speed = 5                                                     # 步行速度，单位公里/小时，默认5公里/小时

    max_foot_dist = 0.05                                               # 站点至线路垂线距离上限，单位公里，默认0.05公里
    max_transfer_dist = 0.2                                            # 站点间步行换乘距离上限，单位公里，默认0.2公里
    max_gps2stop_dist = 0.01                                           # GPS与站点匹配距离上限，单位公里，默认0.01公里
    max_azimuth_diff = 90                                              # GPS与站点匹配方位角差值上限，单位度，默认90度
    min_gps_interval = 5                                               # 匹配到同一站点的GPS记录时间戳最小间隔，单位秒，默认5秒
    max_transaction2gps_time = 300                                     # 交易时间与车辆GPS时间匹配时间上限，单位秒，默认300秒
    max_transfer_time = 1800                                           # 换乘识别，对于同一个卡号前一次下车时间戳（估算）与后一次上车时间戳的间隔，单位秒，默认1800秒

    frequent_rate = 0.3                                                # 高频乘客判断标准，出行天数与总天数的比例，默认0.3
    weight_walk = 3                                                    # 步行距离折算乘车距离系数，默认3
    weight_wait = 2                                                    # 候车时间折算车内时间系数，默认2
    max_wait_time = 10                                                 # 最大候车时间，单位分钟，默认10分钟
    penalty_on_time_rate = 0.1                                         # 准点率惩罚系数，惩罚值为该系数与车内时间的乘积，默认0.1

    iters = 5                                                          # 公交分配迭代次数，默认5
    peak_time_interval = 30                                            # 高峰小时开始时间片段，如29表示高峰小时为7:00至8:00

    # 根据外部文件更新参数
    try:
        # 类实例化
        config = configparser.ConfigParser()
        config.read(r'.\Input\parameter.ini', encoding='utf-8-sig')
        print('找到参数文件，使用参数文件中的参数')
        f.write('找到参数文件，使用参数文件中的参数')

        date_start = config.get('date', 'date_start')
        date_end = config.get('date', 'date_end')
        lst_date = config.get('date', 'lst_date')
        if len(lst_date) == 0:
            lst_date = _get_lst_date(date_start, date_end)
        else:
            lst_date = lst_date.split(',')
        date_range = lst_date[0] + '-' + lst_date[-1]

        lst_inmatch_route_name = config.get('parameter', 'lst_inmatch_route_name').split(',')
        lst_match_card_type = list(map(int, config.get('parameter', 'lst_match_card_type').split(',')))
        unit_time_interval = config.getint('parameter', 'unit_time_interval')
        unit_coord2km = config.getfloat('parameter', 'unit_coord2km')
        unit_cell = config.getfloat('parameter', 'unit_cell')

        bus_speed = config.getfloat('parameter', 'bus_speed')
        bus_capacity = config.getfloat('parameter', 'bus_capacity')
        bus_headway = config.getfloat('parameter', 'bus_headway')
        bpr_alpha = config.getfloat('parameter', 'bpr_alpha')
        bpr_beta = config.getfloat('parameter', 'bpr_beta')
        walk_speed = config.getfloat('parameter', 'walk_speed')

        max_foot_dist = config.getfloat('parameter', 'max_foot_dist')
        max_transfer_dist = config.getfloat('parameter', 'max_transfer_dist')
        max_gps2stop_dist = config.getfloat('parameter', 'max_gps2stop_dist')
        max_azimuth_diff = config.getfloat('parameter', 'max_azimuth_diff')
        min_gps_interval = config.getfloat('parameter', 'min_gps_interval')
        max_transaction2gps_time = config.getfloat('parameter', 'max_transaction2gps_time')
        max_transfer_time = config.getfloat('parameter', 'max_transfer_time')

        frequent_rate = config.getfloat('parameter', 'frequent_rate')
        weight_walk = config.getfloat('parameter', 'weight_walk')
        weight_wait = config.getfloat('parameter', 'weight_wait')
        max_wait_time = config.getfloat('parameter', 'max_wait_time')
        penalty_on_time_rate = config.getfloat('parameter', 'penalty_on_time_rate')

        iters = config.getint('parameter', 'iters')
        peak_time_interval = config.getint('parameter', 'peak_time_interval')

    except IOError:
        print('参数文件不存在，使用默认参数')
        f.write('参数文件不存在，使用默认参数')

    print(time.asctime(time.localtime(time.time())) + '程序运行开始，时间范围：{}'.format(date_range))
    f.write(time.asctime(time.localtime(time.time())) + '程序运行开始，时间范围：{}\n'.format(date_range))

    # # 程序开始
    if step == 1:
        create_gis()                                         # Step1：建立地图数据
        for k in range(len(lst_date)):
            get_arrival_time(lst_date[k])                    # Step2：匹配GPS与站点数据，识别到站时间
            get_on_stop(lst_date[k])                         # Step3：匹配交易与站点数据，识别上车站点
        get_on_statictics()                                  # Step4：上客量特征统计
        for k in range(len(lst_date)):
            get_off_stop(lst_date[k])                        # Step5：识别下车站点
            get_transfer(lst_date[k])                        # Step6：换乘修正
        get_od()                                             # Step7：统计站点OD

        for k in range(len(lst_date)):
            statistics(lst_date[k])                          # Step8：结果统计
        statistics()

    elif step == 2:
        for k in range(len(lst_date)):
            assignment(lst_date[k])                          # Step9：公交分配

    else:
        print('无任何操作')

    print(time.asctime( time.localtime(time.time())) + '所有程序运行结束，总耗时：{:.1f}秒'.format(time.time() - t0))
    f.write(time.asctime(time.localtime(time.time())) + '所有程序运行结束，总耗时：{:.1f}秒\n'.format(time.time() - t0))
    f.close()



x_pi = 3.14159265358979324 * 3000.0 / 180.0
pi = 3.1415926535897932384626  # π
a = 6378245.0  # 长半轴
ee = 0.00669342162296594323  # 偏心率平方
coordinate = []
lng = []
lat = []
converted_lng = []
converted_lat = []


gui_start()