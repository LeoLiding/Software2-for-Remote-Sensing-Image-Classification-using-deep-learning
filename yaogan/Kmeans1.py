import numpy as np
from sklearn import cluster
from osgeo import gdal, gdal_array
import matplotlib.pyplot as plt

def Kmeans(path,newpath,k1):
    # 让GDAL抛出Python异常，并注册所有驱动程序
    gdal.UseExceptions()
    gdal.AllRegister()

    #所有频段上分类
    # 栅格文件读取
    img_ds = gdal.Open(path, gdal.GA_ReadOnly)
    n= img_ds.RasterCount #波段数
    print("有",n,"个波段")
    # 将多波段图像加载到numpy中(最快的方法)
    img = np.zeros((img_ds.RasterYSize, img_ds.RasterXSize, img_ds.RasterCount),
                   gdal_array.GDALTypeCodeToNumericTypeCode(img_ds.GetRasterBand(1).DataType))


    for b in range(img.shape[2]):
        img[:, :, b] = img_ds.GetRasterBand(b + 1).ReadAsArray()

    new_shape =(img.shape [0] * img.shape [1],img.shape [2])

    # spot有n个波段，将列重塑保持为n
    X = img[:, :, :n].reshape(new_shape)

    #设置分为几类
    k=int(k1)
    k_means = cluster.KMeans(n_clusters=k)
    print("训练模型……")
    k_means.fit(X)
    print("开始聚类……")
    X_cluster = k_means.labels_
    X_cluster = X_cluster.reshape(img[:, :, 0].shape)
    print("聚类结束")

    plt.figure(figsize=(10,10))
    plt.imshow(X_cluster, cmap="hsv")
    f = plt.gcf()  #获取当前图像
    f.savefig(newpath)
    f.clear()  #释放内存

    plt.show()


    # #保存分类结果
    # driver = gdal.GetDriverByName("GTiff")
    # save_path="Kmeans_output01.tif"
    # datasetnew = driver.Create(save_path, img_ds.RasterXSize, img_ds.RasterYSize, 1, gdal.GDT_Float32)
    # # datasetnew.SetGeoTransform(self.adf_GeoTransform)
    # # datasetnew.SetProjection(self.im_Proj)
    # band = datasetnew.GetRasterBand(1)
    # band.WriteArray(X_cluster)
    # datasetnew.FlushCache()  # Write to disk.必须有清除缓存


