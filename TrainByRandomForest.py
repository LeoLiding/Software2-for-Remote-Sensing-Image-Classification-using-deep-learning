
from sklearn.ensemble import RandomForestClassifier
import osgeo
from osgeo import gdal
from osgeo import osr
from osgeo import ogr
import numpy
import os
import sys
import math
import psutil

def ReadVectorFile(strVectorFile,id="Id"):
    # 注册所有的驱动
    ogr.RegisterAll()
 
    #打开数据
    ds = ogr.Open(strVectorFile)
    if ds == None:
            print("打开文件【%s】失败！", strVectorFile)
            return
 
 
    # 获取第一个图层
    oLayer = ds.GetLayerByIndex(0)
    if oLayer == None:
            print("获取第%d个图层失败！\n", 0)
            return
 
    oLayer.ResetReading()
 


    oFeature = oLayer.GetNextFeature()
    # 下面开始遍历图层中的要素
    values = list()
    while oFeature is not None:
        value = oFeature.GetField(id)
        #print(value)
        oGeometry = oFeature.GetGeometryRef()
        x = oGeometry.GetX(0)
        y = oGeometry.GetY(0)
        #print(f"x:{x},y:{y}")
        values.append([x,y,value])
        oFeature = oLayer.GetNextFeature()
    sp = oLayer.GetSpatialRef()
    
    ds = None
    return values,sp

def xyTansform(spatial1,spatial2,x,y):
    ct=osr.CreateCoordinateTransformation(spatial1,spatial2)
    return  xyTansformCT(ct,x,y)
def xyTansformCT(ct,x,y):
    pC=ct.TransformPoint(x,y,0)
    nX=pC[0]
    nY=pC[1]

    return nX,nY

def createClassifierByPoint(ClassifyFile,trainFile,treenum,max_depth,field="Id"):
    #训练点数据
    rds = gdal.Open(ClassifyFile) 
    #print((rds.GetRasterBand(1).DataType))
    transform = (rds.GetGeoTransform())
    lX = transform[0]#左上角点
    lY = transform[3]
    rX = transform[1]#分辨率
    rY = transform[5]

    values,sp = ReadVectorFile(trainFile,field)
    rsp = osr.SpatialReference()
    rsp.ImportFromWkt(rds.GetProjectionRef())
    ct = osr.CreateCoordinateTransformation(sp,rsp)
    BandsCount = rds.RasterCount
    trainX = list()
    trainY = list()
    for value in values:
        x,y = xyTansformCT(ct,value[0],value[1])
        ClassifyFile,row = getPathRow(value[0],value[1],lX,lY,rX,rY)
        try:
            arr = rds.ReadAsArray(ClassifyFile,row,1,1)
            tem = list()
            for i in range(BandsCount):
                tem.append(int(arr[i]))
            trainX.append(tem)
            trainY.append(int(value[2]))
        except Exception as e:
            print(e)
    if len(trainY) == 0:
        print("未获取到训练样本,程序退出")
        os._exit(0)
    clf = RandomForestClassifier(n_estimators=treenum)
    clf.fit(trainX, trainY)#训练样本
    return clf
def CheckPointInPolygon(X,Y,polygonPoints:list):
    #判断点在多边形内部
    count=0
    for k in range(len(polygonPoints)-1):
        point1=polygonPoints[k]
        point2=polygonPoints[k+1]
        if (point1.Y>=Y and point2.Y<=Y) or (point1.Y<=Y and point2.Y>=Y):


            if point1.X==point2.X:
                intersectX=point1.X
                if intersectX>X:count+=1
            else:
                k=(point2.Y-point1.Y)/(point2.X-point1.X)
                if k==0:
                    if X<point1.X or X<point2.X:
                        count+=1
                    continue
                intersectX=(Y-point1.Y)/k+point1.X
                if intersectX>X:count+=1

    if count%2==1:
        return True
    return False
def GetSubRaster(inraster,polygonPoints:list):
    polygonPoints.append(polygonPoints[0])#面多边形坐标封闭
    print("当前多边形节点数量："+str(len(polygonPoints)))
    minX=10000000000000
    maxX=-minX
    minY=100000000000000000
    maxY=-minY

    for point in polygonPoints:
        print("points=",point)
        if point.X<minX:minX=point.X
        if point.X>maxX:maxX=point.X
        if point.Y<minY:minY=point.Y
        if point.Y>maxY:maxY=point.Y
    leftX=minX
    upY=maxY
    rightX=maxX
    bottomY=minY

    print("point.X=",point.X,"point.Y=",point.Y)
    print("leftX=",leftX,"upY=",upY,"rightX=",rightX,"bottomY",bottomY)

    rds = gdal.Open(inraster) 
    #print((rds.GetRasterBand(1).DataType))
    transform = (rds.GetGeoTransform())
    lX = transform[0]#左上角点
    lY = transform[3]
    rX = transform[1]#分辨率
    rY = transform[5]

    print("lX=",lX,"lY",lY,"rX",rX,"rY",rY)

    wpos=int((leftX-lX)/rX)
    hpos=int((upY-lY)/rY)

    width=int((rightX-leftX)/rX)
    height=int((bottomY-upY)/rY)
    BandsCount = rds.RasterCount
    arr = rds.ReadAsArray(wpos,hpos,width,height)
    fixX=list()
    #for i in range(height):
    #    for k in range(width):
    #        tem = list()
    #        for bc in range(BandsCount):
    #            tem.append(int(arr[bc][i][k]))
    #        fixX.append(tem)
    nodatavalue=rds.GetRasterBand(1).GetNoDataValue()
    for i in range(height):
        if height>200:
            print(f"多边形裁剪进度：{round(((i+1)/height)*100,4)}%")
        #for k in range(width):
        #    r=CheckPointInPolygon(leftX+k*rX,upY+i*rY,polygonPoints)
        #    if r==False:
        #        for bc in range(BandsCount):
        #            arr[bc][i][k]=int(nodatavalue)
        Y=upY+i*rY+.00001
        pointsindex=list()
        for k in range(len(polygonPoints)-1):
                point1=polygonPoints[k]
                point2=polygonPoints[k+1]
                if (point1.Y>=Y and point2.Y<=Y) or (point1.Y<=Y and point2.Y>=Y):
                    pointsindex.append(k)
        for j in range(width):
            count=0
            for m in (pointsindex):
                point1=polygonPoints[m]
                point2=polygonPoints[m+1]
                X=leftX+j*rX+.00001
                if point1.X==point2.X:
                    intersectX=point1.X
                    if intersectX>X:count+=1
                else:
                    k=(point2.Y-point1.Y)/(point2.X-point1.X)
                    if k==0:
                        if X<point1.X or X<point2.X:
                            count+=1
                    else:
                        intersectX=(Y-point1.Y)/k+point1.X
                        if intersectX>X:count+=1

            if count%2==0:
                if BandsCount>1:
                    for bc in range(BandsCount):
                        arr[bc][i][j]=(nodatavalue)
                else:
                    arr[i][j]=-1
    #WriteRaster("test.tif",arr,inraster,width,height,BandsCount,leftX,upY)
    return arr,width,height,BandsCount,leftX,upY

def WriteRaster(name,arr,inraster,width,height,bandscount,leftX=0,upY=0):
    #写入栅格数据
    rds = gdal.Open(inraster) 
    transform = (rds.GetGeoTransform())
    driver = gdal.GetDriverByName("GTiff")
    out = driver.Create(name,width,height,3,rds.GetRasterBand(1).DataType)

    out.SetGeoTransform([leftX,transform[1],transform[2],upY,transform[4],transform[5]])
    out.SetProjection(rds.GetProjectionRef())
    out.GetRasterBand(1).WriteArray(arr[0])
    out.GetRasterBand(2).WriteArray(arr[1])
    out.GetRasterBand(3).WriteArray(arr[2])
    out.FlushCache()
    out = None
    rds=None
def WKTToPoints(polygon):
    polygon=polygon.replace("POLYGON","")
    polygon=polygon.replace("(","")
    polygon=polygon.replace(")","")
    polygon=polygon.strip()
    pointSet=list()
    while polygon.find(",")!=-1:
        if(polygon[0]==","):
            polygon=polygon[1::]
        k=polygon.find(",")
        tem=polygon[0:k]
        sp=tem.find(" ")
        lon=float(tem[0:sp].strip())
        lat=float(tem[sp::].strip())

        pointSet.append(Point(lon,lat))
        polygon=polygon[k+1::]
        polygon=polygon.strip()
        sumlon=0
        sumlat=0
    return pointSet

def createClassifier(inraster,inshp,treenum,max_depth,field:str="Id"):
    rasterspatial = gdal.Open(inraster)
    spatial2=osr.SpatialReference()
    spatial2.ImportFromWkt(rasterspatial.GetProjectionRef())
    shpspatial=ogr.Open(inshp)
    layer=shpspatial.GetLayer(0)
    spatial1=layer.GetSpatialRef()
    print("spatial1",spatial1,"spatial2",spatial2)
   
    ct=osr.CreateCoordinateTransformation(spatial1,spatial2)
    #print("ct.type=",ct.type())
    oFeature = layer.GetNextFeature()
    # 下面开始遍历图层中的要素
    geom=oFeature.GetGeometryRef()
    if geom.GetGeometryType()==ogr.wkbPoint:
        return createClassifierByPoint(inraster,inshp,treenum,max_depth)
    k=geom.GetGeometryType()
    if geom.GetGeometryType()!=ogr.wkbPolygon:
        print("样本必须为单部件多边形")
        return False
    trainX = list()
    trainY = list()
    print("读取样本")
    while oFeature is not None:
        geom=oFeature.GetGeometryRef()
        #print(geom.GetGeometryName())
        #print(geom.GetGeometryCount())
        #print(geom.GetPointCount())
        wkt=geom.ExportToWkt()
        points=WKTToPoints(wkt)
        polygonPoints=[]
        value=oFeature.GetField(field)
        for point in points:
            pC=ct.TransformPoint(point.X,point.Y,0)
            polygonPoints.append(Point(pC[0],pC[1]))

        print("polygonPoints:",polygonPoints)

        arr,width,height,BandsCount,leftX,upY=GetSubRaster(inraster,polygonPoints)
        for i in range(height):
            for k in range(width):
                nodata=True
                tem = list()
                for bc in range(BandsCount):
                    v=int(arr[bc][i][k])
                    tem.append(v)
                    if v>0:nodata=False
                if nodata:
                    continue
                trainX.append(tem)
                trainY.append(int(value))
        oFeature = layer.GetNextFeature()

    ct=None
    spatial1=None
    spatial2=None
    print("训练样本")
    clf = RandomForestClassifier(n_estimators=treenum)
    clf.fit(trainX, trainY)#训练样本
    print("训练完成")
    return clf

def getPathRow(x,y,lX,lY,rX,rY):
    path = int((x - lX) / (rX))
    row = int(((y - lY) / rY))
    return path,row
class Point:
    def __init__(self,x,y):
        self.X =x  
        self.Y=y    
#createClassifier("C:\\Users\\user\\Desktop\\MyProject\\1.tif","test.shp")