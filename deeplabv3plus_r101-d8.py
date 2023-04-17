from mmseg.apis import inference_segmentor, init_segmentor
import mmcv

def deeplabv3plus_r101(inputimage):
    config_file = 'configs\deeplabv3plus\deeplabv3plus_r101-d8_512x512_80k_loveda.py'
    checkpoint_file = 'checkpoints/deeplabv3plus_r101-d8_512x512_80k_loveda_20211105_110759-4c1f297e.pth'

# build the model from a config file and a checkpoint file
    model = init_segmentor(config_file, checkpoint_file, device='cuda:0')

# test a single image and show the results
# img = 'test.jpg'  # or img = mmcv.imread(img), which will only load it once
#    img = 'demo/0.png'
    img = inputimage
    result = inference_segmentor(model, img)

    model.show_result(img, result, out_file='result_deeplabv3plus_r101.jpg', opacity=0.5)