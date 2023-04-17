from mmseg.apis import inference_segmentor, init_segmentor
import mmcv

def fcn_hr48(inputimage):
# hrnet fcn 
    config_file = 'configs/hrnet/fcn_hr48_512x512_80k_loveda.py'
    checkpoint_file = 'checkpoints/fcn_hr48_512x512_80k_loveda_20211211_044756-67072f55.pth'
# build the model from a config file and a checkpoint file
    model = init_segmentor(config_file, checkpoint_file, device='cuda:0')

# test a single image and show the results
# img = 'test.jpg'  # or img = mmcv.imread(img), which will only load it once
#    img = 'demo/0.png'
    img = inputimage
    result = inference_segmentor(model, img)

    model.show_result(img, result, out_file='result_fcn_hr48.jpg', opacity=0.5)