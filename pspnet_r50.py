from mmseg.apis import inference_segmentor, init_segmentor
import mmcv

def pspnet_r50(inputimage):
    config_file = 'configs\pspnet\pspnet_r50-d8_512x512_80k_loveda.py'
    checkpoint_file = 'checkpoints/pspnet_r50-d8_512x512_80k_loveda_20211104_155728-88610f9f.pth'
# build the model from a config file and a checkpoint file
    model = init_segmentor(config_file, checkpoint_file, device='cuda:0')

# test a single image and show the results
# img = 'test.jpg'  # or img = mmcv.imread(img), which will only load it once
#    img = 'demo/0.png'
    img = inputimage
    result = inference_segmentor(model, img)

    model.show_result(img, result, out_file='result_pspnet_r50.jpg', opacity=0.5)