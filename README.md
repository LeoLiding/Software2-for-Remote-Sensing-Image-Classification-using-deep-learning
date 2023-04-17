本项目制作了基于像素的遥感影像分类系统
主要使用了非监督分类＋监督分类进行分类，软件制作基于QT框架进行

主要系统介绍如下:

![image](https://user-images.githubusercontent.com/87323344/232573995-ec34bb23-ca95-4a45-8f0b-cc480adf9fe2.png)

其中监督分类主要使用：

![image](https://user-images.githubusercontent.com/87323344/232575934-6cc6b317-b577-4e48-8756-c70ee2387797.png)

![image](https://user-images.githubusercontent.com/87323344/232575962-d60924e5-e179-4be4-98f8-1a79b47ce768.png)


其中监督分类主要采取FCN架构，包括pspnet/deeplabv3plus/resnet/HRNet等

![image](https://user-images.githubusercontent.com/87323344/232574827-900fa159-47dc-406e-94f8-e669e99a1b12.png)

![image](https://user-images.githubusercontent.com/87323344/232574848-0bdb76c3-1cfc-42cc-a254-09d30da2d8e3.png)

![image](https://user-images.githubusercontent.com/87323344/232574883-8e6855c0-0528-4e86-98d8-96b35e837ba5.png)

预训练权重来自OpenMMLab，深度学习部分使用了mmseg团队的结果



软件效果展示如下：


![image](https://user-images.githubusercontent.com/87323344/232574973-6cf7aa82-b419-4605-8c0b-985a21fe90b3.png)

分类结果：

![image](https://user-images.githubusercontent.com/87323344/232575042-fcf16612-3165-4199-91da-bd702f23cc61.png)

![image](https://user-images.githubusercontent.com/87323344/232575089-13db738d-adc8-4260-a334-ac64a20683c4.png)

![image](https://user-images.githubusercontent.com/87323344/232575120-2920fc12-dc8f-4186-b181-22b4a767f55b.png)

![image](https://user-images.githubusercontent.com/87323344/232575153-6f88aee2-d962-439e-9183-7286d82b25d7.png)

![image](https://user-images.githubusercontent.com/87323344/232575194-546e9643-8e9f-4840-9e83-d7e453628ed7.png)

整体工作来自本人以及绿、廖、朱四人（虚拟现实组）
