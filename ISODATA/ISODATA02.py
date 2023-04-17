#ISODATA全称为 Iterative Selforganizing Data Analysis Techniques Algorithm
import numpy
import math
import random
from osgeo import gdal
import cv2

dataset = gdal.Open("or_196560080.tif")
outputFilename = "ISODATA_out.tif"

argvK = 5#初始类别数（期望）
argvTN = 20#每个类别中样本最小数目
argvTS = 1#每个类别的标准差
argvTC = 0.5#每个类别间的最小距离
argvL = 5#每次允许合并的最大类别对的数量
argvI = 6#迭代次数



class Pixel:
    """Pixel"""
    def __init__(self, initX: int, initY: int, initColor):
        self.x = initX
        self.y = initY
        self.color = initColor

class Cluster:
    """Cluster in Gray"""
    def __init__(self, initCenter):
        self.center = initCenter
        self.pixelList = []

class ClusterPair:
    """Cluster Pair"""
    def __init__(self, initClusterAIndex: int, initClusterBIndex: int, initDistance):
        self.clusterAIndex = initClusterAIndex
        self.clusterBIndex = initClusterBIndex
        self.distance = initDistance
# RGB
def distanceBetween(colorA, colorB) -> float:
  
    dR = int(colorA[0]) - int(colorB[0])
    dG = int(colorA[1]) - int(colorB[1])
    dB = int(colorA[2]) - int(colorB[2])
    return math.sqrt((dR**2)+(dG**2)+(dB**2))
  


def main(dataset, outputfilename,K: int, TN: int, TS: float, TC:int, L: int, I: int):   
    # dataset = gdal.Open("before.img")
    im_bands = dataset.RasterCount #波段数
    imgX = dataset.RasterXSize #栅格矩阵的列数
    imgY = dataset.RasterYSize #栅格矩阵的行数
    im_geotrans = dataset.GetGeoTransform()  #仿射矩阵
    im_proj = dataset.GetProjection() #地图投影信息
    imgArray = dataset.ReadAsArray(0,0,imgX,imgY)#获取数据
    
    clusterList = []
    # 随机生成聚类中心
    for i in range(0, K):
        randomX = random.randint(0, imgX - 1)
        randomY = random.randint(0, imgY - 1)
        duplicated = False
        for cluster in clusterList:
            if (cluster.center[0] == imgArray[0,randomX, randomY] and
                cluster.center[1] == imgArray[1,randomX, randomY] and
                cluster.center[2] == imgArray[2,randomX, randomY]
                ):
                duplicated = True
                break
        if not duplicated:
            clusterList.append(Cluster(numpy.array([imgArray[0,randomX, randomY],
                                                    imgArray[1,randomX, randomY],
                                                    imgArray[2,randomX, randomY]
                                                    ],
                                                    dtype = numpy.uint8)))

    # 开始迭代
    iterationCount = 0
    didAnythingInLastIteration = True
    while True:
        iterationCount += 1

        # 清空每一类内像元
        for cluster in clusterList:
            cluster.pixelList.clear()
        print("------")
        print("迭代第{0}次".format(iterationCount))

        #将所有像元分类
        print("分类...", end = '', flush = True)
        for row in range(0, imgX):
            for col in range(0, imgY):
                targetClusterIndex = 0
                targetClusterDistance = distanceBetween(imgArray[:,row, col], clusterList[0].center)
                # 分类
                for i in range(1, len(clusterList)):
                    currentDistance = distanceBetween(imgArray[:,row, col], clusterList[i].center)
                    if currentDistance < targetClusterDistance:
                        targetClusterDistance = currentDistance
                        targetClusterIndex = i
                clusterList[targetClusterIndex].pixelList.append(Pixel(row, col, imgArray[:,row, col]))
        print(" 结束 ")

        #检查类中样本个数是否满足要求
        gotoNextIteration = False
        for i in range(len(clusterList) - 1, -1, -1):
            if len(clusterList[i].pixelList) < TN:
                # 重新分类
                clusterList.pop(i)
                gotoNextIteration = True
                break
        if gotoNextIteration:
            print("样本个数不满足要求")
            continue
        print("样本个数满足要求")

        # 重新计算聚类中心
        print("重新计算聚类中心...", end = '', flush = True)
        for cluster in clusterList:
            sumR = 0.0
            sumG = 0.0
            sumB = 0.0
           
            for pixel in cluster.pixelList:
                sumR += int(pixel.color[0])
                sumG += int(pixel.color[1])
                sumB += int(pixel.color[2])
            aveR = round(sumR / len(cluster.pixelList))
            aveG = round(sumG / len(cluster.pixelList))
            aveB = round(sumB / len(cluster.pixelList))
            
            if (aveR != cluster.center[0] and
                aveG != cluster.center[1] and
                aveB != cluster.center[2]
                ):
                didAnythingInLastIteration = True
            cluster.center = numpy.array([aveR, aveG, aveB], dtype = numpy.uint8)
        print("结束")
        if iterationCount > I:
            break
        if not didAnythingInLastIteration:
            print("更多迭代次数是不是必要的")
            break

        # 计算平均距离
        print("准备合并或分裂...", end = '', flush = True)
        aveDisctanceList = []
        sumDistanceAll = 0.0
        for cluster in clusterList:
            currentSumDistance = 0.0
            for pixel in cluster.pixelList:
                currentSumDistance += distanceBetween(pixel.color, cluster.center)
            aveDisctanceList.append(float(currentSumDistance) / len(cluster.pixelList))
            sumDistanceAll += currentSumDistance
        aveDistanceAll = float(sumDistanceAll) / (imgX * imgY)
        print(" 结束")

        if (len(clusterList) <= K / 2) or not (iterationCount % 2 == 0 or len(clusterList) >= K * 2):
            # 分裂
            print("开始分裂", end = '', flush = True)
            beforeCount = len(clusterList)
            for i in range(len(clusterList) - 1, -1, -1):
                currentSD = [0.0, 0.0, 0.0]
                for pixel in clusterList[i].pixelList:
                    currentSD[0] += (int(pixel.color[0]) - int(clusterList[i].center[0])) ** 2
                    currentSD[1] += (int(pixel.color[1]) - int(clusterList[i].center[1])) ** 2
                    currentSD[2] += (int(pixel.color[2]) - int(clusterList[i].center[2])) ** 2
                currentSD[0] = math.sqrt(currentSD[0] / len(clusterList[i].pixelList))
                currentSD[1] = math.sqrt(currentSD[1] / len(clusterList[i].pixelList))
                currentSD[2] = math.sqrt(currentSD[2] / len(clusterList[i].pixelList))
               
                # 计算各波段最大标准差
                # Find the max in SD of R, G and B
                maxSD = currentSD[0]
                for j in (1, 2):
                    maxSD = currentSD[j] if currentSD[j] > maxSD else maxSD
                if (maxSD > TS) and ((aveDisctanceList[i] > aveDistanceAll and len(clusterList[i].pixelList) > 2 * (TN + 1)) or (len(clusterList) < K / 2)):
                    gamma = 0.5 * maxSD
                    clusterList[i].center[0] += gamma
                    clusterList[i].center[1] += gamma
                    clusterList[i].center[2] += gamma
                  
                    clusterList.append(Cluster(numpy.array([clusterList[i].center[0],
                                                            clusterList[i].center[1],
                                                            clusterList[i].center[2]
                                                            ],
                                                            dtype = numpy.uint8)))
                    clusterList[i].center[0] -= gamma * 2
                    clusterList[i].center[1] -= gamma * 2
                    clusterList[i].center[2] -= gamma * 2
                    clusterList.append(Cluster(numpy.array([clusterList[i].center[0],
                                                            clusterList[i].center[1],
                                                            clusterList[i].center[2]
                                                            ],
                                                            dtype = numpy.uint8)))
                    clusterList.pop(i)
            print(" {0} -> {1}".format(beforeCount, len(clusterList)))
        elif (iterationCount % 2 == 0) or (len(clusterList) >= K * 2) or (iterationCount == I):
            # 合并
            print("合并:", end = '', flush = True)
            beforeCount = len(clusterList)
            didAnythingInLastIteration = False
            clusterPairList = []
            for i in range(0, len(clusterList)):
                for j in range(0, i):
                    currentDistance = distanceBetween(clusterList[i].center, clusterList[j].center)
                    if currentDistance < TC:
                        clusterPairList.append(ClusterPair(i, j, currentDistance))

            clusterPairListSorted = sorted(clusterPairList, key = lambda clusterPair: clusterPair.distance)
            newClusterCenterList = []
            mergedClusterIndexList = []
            mergedPairCount = 0
            for clusterPair in clusterPairList:
                hasBeenMerged = False
                for index in mergedClusterIndexList:
                    if clusterPair.clusterAIndex == index or clusterPair.clusterBIndex == index:
                        hasBeenMerged = True
                        break
                if hasBeenMerged:
                    continue
                newCenterR = int((len(clusterList[clusterPair.clusterAIndex].pixelList) * float(clusterList[clusterPair.clusterAIndex].center[0]) + len(clusterList[clusterPair.clusterBIndex].pixelList) * float(clusterList[clusterPair.clusterBIndex].center[0])) / (len(clusterList[clusterPair.clusterAIndex].pixelList) + len(clusterList[clusterPair.clusterBIndex].pixelList)))
                newCenterG = int((len(clusterList[clusterPair.clusterAIndex].pixelList) * float(clusterList[clusterPair.clusterAIndex].center[1]) + len(clusterList[clusterPair.clusterBIndex].pixelList) * float(clusterList[clusterPair.clusterBIndex].center[1])) / (len(clusterList[clusterPair.clusterAIndex].pixelList) + len(clusterList[clusterPair.clusterBIndex].pixelList)))
                newCenterB = int((len(clusterList[clusterPair.clusterAIndex].pixelList) * float(clusterList[clusterPair.clusterAIndex].center[2]) + len(clusterList[clusterPair.clusterBIndex].pixelList) * float(clusterList[clusterPair.clusterBIndex].center[2])) / (len(clusterList[clusterPair.clusterAIndex].pixelList) + len(clusterList[clusterPair.clusterBIndex].pixelList)))
                
                newClusterCenterList.append([newCenterR, newCenterG, newCenterB])
                mergedClusterIndexList.append(clusterPair.clusterAIndex)
                mergedClusterIndexList.append(clusterPair.clusterBIndex)
                mergedPairCount += 1
                if mergedPairCount > L:
                    break
            if len(mergedClusterIndexList) > 0:
                didAnythingInLastIteration = True
            mergedClusterIndexListSorted = sorted(mergedClusterIndexList, key = lambda clusterIndex: clusterIndex, reverse = True)
            for index in mergedClusterIndexListSorted:
                clusterList.pop(index)
            for center in newClusterCenterList:
                clusterList.append(Cluster(numpy.array([center[0], center[1], center[2]], dtype = numpy.uint8)))
            print(" {0} -> {1}".format(beforeCount, len(clusterList)))

    # 生成新的图像矩阵
    print("分类结束")
    print("一共分为 {0} 类.".format(len(clusterList)))
    newImgArray = numpy.zeros((7,imgX, imgY), dtype = numpy.uint8)
    for cluster in clusterList:
        for pixel in cluster.pixelList:
            newImgArray[0,pixel.x, pixel.y] = int(cluster.center[0])
            newImgArray[1,pixel.x, pixel.y] = int(cluster.center[1])
            newImgArray[2,pixel.x, pixel.y] = int(cluster.center[2])

    a2 = numpy.ones((3,imgX,imgY), dtype=numpy.uint8)  
    

    unic = numpy.unique(newImgArray[0])
    color = []
    print("对各个类别进行颜色渲染...")
    for i in range(len(unic)): 
        color.append([random.randint(0, 128),random.randint(0, 255),random.randint(128, 255)])


    for i in range(imgY):
        for j in range(imgX):
            for k in range(len(unic)):
                if(newImgArray[0,i,j] == unic[k]):
                    a2[0,i,j] = color[k][0]
                    a2[1,i,j] = color[k][1]
                    a2[2,i,j] = color[k][2]
    
            
        
    print("写出分类后专题图")
    driver = gdal.GetDriverByName("GTiff")
    IsoData = driver.Create(outputfilename, imgX, imgY, 3, gdal.GDT_Byte)
    # for i in range(3):
    #     IsoData.GetRasterBand(i+1).WriteArray(newImgArray[i])
    print("设置坐标参数")
    IsoData.SetGeoTransform(im_geotrans)              #写入仿射变换参数
    print("设置投影信息")
    IsoData.SetProjection(im_proj)   #写入投影
    for i in range(3):                 
        IsoData.GetRasterBand(i+1).WriteArray(a2[i])
    
    del dataset
    print("ISODATA非监督分类完成")
   

if __name__ == '__main__':
    main(dataset,outputFilename,argvK,argvTN,argvTS,argvTC,argvL,argvI)
