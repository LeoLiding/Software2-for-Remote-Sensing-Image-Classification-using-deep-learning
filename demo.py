from mmseg.apis import inference_segmentor, init_segmentor
import mmcv

# config_file = 'configs/deeplabv3plus/deeplabv3plus_r18-d8_512x512_80k_loveda.py'
# checkpoint_file = 'checkpoints/deeplabv3plus_r18-d8_512x512_80k_loveda_20211104_132800-ce0fa0ca.pth'

# config_file = 'configs\pspnet\pspnet_r50-d8_512x512_80k_loveda.py'
# checkpoint_file = 'checkpoints/pspnet_r50-d8_512x512_80k_loveda_20211104_155728-88610f9f.pth'

# config_file = 'configs\deeplabv3plus\deeplabv3plus_r101-d8_512x512_80k_loveda.py'
# checkpoint_file = 'checkpoints/deeplabv3plus_r101-d8_512x512_80k_loveda_20211105_110759-4c1f297e.pth'

# hrnet fcn 
config_file = 'configs/hrnet/fcn_hr48_512x512_80k_loveda.py'
checkpoint_file = 'checkpoints/fcn_hr48_512x512_80k_loveda_20211211_044756-67072f55.pth'


# build the model from a config file and a checkpoint file
model = init_segmentor(config_file, checkpoint_file, device='cuda:0')

# test a single image and show the results
# img = 'test.jpg'  # or img = mmcv.imread(img), which will only load it once
img = 'demo/or_196560080.tif'
result = inference_segmentor(model, img)

model.show_result(img, result, out_file='tif.jpg', opacity=0.5)
