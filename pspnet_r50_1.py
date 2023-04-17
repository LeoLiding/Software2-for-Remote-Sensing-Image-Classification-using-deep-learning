from mmseg.apis import inference_segmentor, init_segmentor
import mmcv
from osgeo import gdal
import numpy as np
import matplotlib.pyplot as plt

def pspnet_r50(inputimage,config_file, checkpoint_file,out_file1):
    config_file = 'configs\pspnet\pspnet_r50-d8_512x512_80k_loveda.py'
    checkpoint_file = 'checkpoints/pspnet_r50-d8_512x512_80k_loveda_20211104_155728-88610f9f.pth'
# build the model from a config file and a checkpoint file
    model = init_segmentor(config_file, checkpoint_file, device='cuda:0')

# test a single image and show the results
# img = 'test.jpg'  # or img = mmcv.imread(img), which will only load it once
#    img = 'demo/0.png'
    img = inputimage
    result = inference_segmentor(model, img)

    model.show_result(img, result, out_file=out_file1, opacity=0.5)

    # data = gdal.Open(out_file1)  # 读取tif文件
    # num_bands = data.RasterCount  # 获取波段数
    # print(num_bands)
    # tmp_img = data.ReadAsArray() #将数据转为数组
    # img_rgb = tmp_img.transpose(1, 2, 0) #由波段、行、列——>行、列、波段
    # img_rgb = np.array(img_rgb, dtype=np.uint8) #设置数据类型，np.unit8可修改
    # r = img_rgb[:, :, 2]
    # g = img_rgb[:, :, 1]
    # b = img_rgb[:, :, 0]
    # img_rgb = np.dstack((r, g, b)) # 波段组合
    # # plt.imshow(img_rgb)
    # # plt.show()
    # # 通过调用plt.axis（“ off”），可以删除编号的轴
    # plt.axis("off")
    # plt.imshow(img_rgb)
    # plt.show()