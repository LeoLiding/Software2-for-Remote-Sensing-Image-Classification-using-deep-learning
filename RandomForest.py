from sklearn.ensemble import RandomForestClassifier
import osgeo
from osgeo import gdal
from osgeo import osr
from osgeo import ogr
import numpy
import psutil
import os
import sys
import math
import TrainByRandomForest as tbrf
import matplotlib.pyplot as plt

def memory_usage():
    mem_available = psutil.virtual_memory().available
    mem_process = psutil.Process(os.getpid()).memory_info().rss
    return round(mem_process / 1024 / 1024, 2), round(mem_available / 1024 / 1024, 2)





def checkMemory(size=500):
    p,a = memory_usage()
    if a < size:
        print("内存不足：",a)
        os._exit(-2)
def RandomForestClassification(ClassifyRaster,TrainRaster,TrainShp,outfile,blockSize,treenum,max_depth): 

    rds = gdal.Open(ClassifyRaster) 
    #print((rds.GetRasterBand(1).DataType))
    transform = (rds.GetGeoTransform())
    lX = transform[0]#左上角点
    lY = transform[3]
    rX = transform[1]#分辨率
    rY = transform[5]
    width = rds.RasterXSize
    height = rds.RasterYSize
    bX = lX + rX * width#右下角点
    bY = lY + rY * height
    #values,sp=ReadVectorFile(classifiedFile)
    #rsp=osr.SpatialReference()
    #rsp.ImportFromWkt(rds.GetProjectionRef())
    #ct=osr.CreateCoordinateTransformation(sp,rsp)
    BandsCount = rds.RasterCount
    #trainX=list()
    #trainY=list()
    #for value in values:
    #    x,y=xyTansformCT(ct,value[0],value[1])
    #    rasterpath,row=getPathRow(value[0],value[1],lX,lY,rX,rY)
    #    try:
    #        arr=rds.ReadAsArray(rasterpath,row,1,1)
    #        tem=list()
    #        for i in range(BandsCount):
    #            tem.append(int(arr[i]))
    #        trainX.append(tem)
    #        trainY.append(int(value[2]))
    #    except Exception as e:
    #        print(e)
    #if len(trainY)==0:
    #    print("未获取到训练样本,程序退出")
    #    os._exit(0)
    #clf = RandomForestClassifier(n_estimators=treenum,max_depth=max_depth)
    #clf.fit(trainX, trainY)#训练样本
    clf = tbrf.createClassifier(TrainRaster,TrainShp,treenum,max_depth)
    Z = list()
    fixX = list()
    if blockSize == 0:
        p,a = memory_usage()
        pv = 0.6 / 10000
        checkMemory(2000)#内存小于2GB，不在计算
        bl = (a - 2000) / pv / height / BandsCount
        blockSize = math.ceil(height / bl)
        if blockSize < 1:blockSize = 1
        if blockSize > 1:blockSize+=5
    if  blockSize != 1:
        blockHeight = 0
        modHeight = 0
        modHeight = height % blockSize

        if modHeight == 0:
            blockHeight = int(height / blockSize)
            
        else:
            blockHeight = int(height / blockSize)
        print(f"分块大小{width}*{blockHeight}")
        for bs in range(blockSize):
            print(f"计算块{bs+1}/{blockSize}")
            checkMemory(500)
            arr = rds.ReadAsArray(0,bs * blockHeight,width,blockHeight)
            
            for i in range(blockHeight):
                print(f"分块：{bs+1}/{blockSize}添加分类数据{round((i+1)*100/blockHeight,4)}%")
                for k in range(width):
                    tem = list()
                    for bc in range(BandsCount):
                        tem.append(int(arr[bc][i][k]))
                    fixX.append(tem)
            print(f"分块：{bs+1}/{blockSize}计算分类结果……")
            checkMemory(800)
            z = clf.predict(fixX)         
            Z.extend(z)
            fixX = list()
            arr = None
        print(f"计算余数：{width}*{modHeight}")
        checkMemory(500)
        arr = rds.ReadAsArray(0,blockSize * blockHeight,width,modHeight)
        if modHeight > 0:
            for i in range(modHeight):
                print(f"余块：添加分类数据{round((i+1)*100/modHeight,4)}%")
                for k in range(width):
                    tem = list()
                    for bc in range(BandsCount):
                        tem.append(int(arr[bc][i][k]))
                    fixX.append(tem)
            print("余块：计算分类结果……")
            checkMemory(500)
            z = clf.predict(fixX)         
            Z.extend(z)
        Z = numpy.array(Z)
        #Z=Z.reshape(1,width*height)
        Z = Z.reshape(height,width)
        fixX = None
        arr = None

  
    else:
        checkMemory(1000)
        arr = rds.ReadAsArray(0,0,width,height)
        


        
        for i in range(height):
            print(f"添加训练样本{round((i+1)*100/height,4)}%")
            for k in range(width):
                tem = list()
                for bc in range(BandsCount):
                    tem.append(int(arr[bc][i][k]))
                fixX.append(tem)
        arr = None
        print("计算分类结果……")
        Z = clf.predict(fixX)
        Z = numpy.array(Z)
        Z = Z.reshape(height,width)

    driver = gdal.GetDriverByName("GTiff")
    filepath,filename = os.path.split(outfile)
    short,ext = os.path.splitext(filename)
    try:
        print("如果输出文件已存在，将被覆盖")
        if os.path.exists(os.path.join(filepath,short + ".tif")):os.remove(os.path.join(filepath,short + ".tif"))
        if os.path.exists(os.path.join(filepath,short + ".tfw")):os.remove(os.path.join(filepath,short + ".tfw"))
        if os.path.exists(os.path.join(filepath,short + ".tif.aux.xml")):os.remove(os.path.join(filepath,short + ".tif.aux.xml"))
        if os.path.exists(os.path.join(filepath,short + ".tif.ovr")):os.remove(os.path.join(filepath,short + ".tif.ovr"))
    except Exception as e:
        print(e)
        os._exit(2)
    print("创建输出文件")
    out = driver.Create(outfile,width,height,1,rds.GetRasterBand(1).DataType)
    out.SetGeoTransform(transform)
    out.SetProjection(rds.GetProjectionRef())
    print("写入数据……")
    out.GetRasterBand(1).WriteArray(Z)
    out.FlushCache()
    out = None
    print("计算完成")

def getPathRow(x,y,lX,lY,rX,rY):
    path = int((x - lX) / (rX))
    row = int(((y - lY) / rY))
    return path,row
def test():
    X = [[1,1,1],[2,2,2],[3,3,3],[4,4,4],[5,5,5]]
    Y = [1,2,3,4,2]


    clf = RandomForestClassifier(n_estimators=100)
    clf.fit(X, Y)

    Z = clf.predict([[5.25505156 ,5.5652961 , 5.17026121]])

    for z in Z:
        print(z)

def WriteOutputError(message,outpath="Record/Error.txt"):
    '''
记录错误消息
    '''
    path,file = os.path.split(outpath)
    if not os.path.exists(path):
        os.makedirs(path)
    with open(outpath,"a+")as code:
        code.write(str(message))
        code.write("\n")

def main():
    openfile="BOA Reflectance-10m_MTD_MSIL2A.tif"
    resultfile="Result1.tif"
    blockSize=0
    treenum=100
    max_depth=10
    Diaoyong(openfile,resultfile,blockSize,treenum,max_depth)
    
def Diaoyong(openfile,resultfile,blockSize,treenum,max_depth):
    RandomForestClassification( openfile,
                               "BOA Reflectance-10m_MTD_MSIL2A.tif",
                               "sample1.shp",
                               resultfile,
                               blockSize,treenum,max_depth)
    # data = gdal.Open(resultfile)  # 读取tif文件
    # num_bands = data.RasterCount # 获取波段数
    # print(num_bands)
    # tmp_img = data.ReadAsArray() #将数据转为数组
    # img_rgb = tmp_img.transpose(1, 2, 0)  #>行、列、波段
    # img_rgb = numpy.array(img_rgb, dtype=numpy.uint8)  #设置数据类型，np.unit8可修改
    # r = img_rgb[:, :, 2]
    # g = img_rgb[:, :, 1]
    # b = img_rgb[:, :, 0]
    # img_rgb = numpy.dstack((r, g, b))# 波段组合
    # # plt.imshow(img_rgb)
    # # plt.show()
    # # 通过调用plt.axis（“ off”），可以删除编号的轴
    # plt.axis("off")
    # plt.imshow(img_rgb)
    # plt.show()

if __name__ == '__main__':
    gdal.AllRegister()
    main()