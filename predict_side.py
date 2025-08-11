import onnx
import onnxruntime 
import numpy as np
import json 
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import os
#Import some useful functions from https://github.com/onnx/onnx-docker/blob/master/onnx-ecosystem/inference_demos/resnet50_modelzoo_onnxruntime_inference.ipynb
def load_labels(path):
    with open(path) as f:
        data = json.load(f)
    return np.asarray(data)

def preprocess(input_data):
    # convert the input data into the float32 input
    img_data = input_data.astype('float32')

    #normalize
    mean_vec = np.array([0.485, 0.456, 0.406])
    stddev_vec = np.array([0.229, 0.224, 0.225])
    norm_img_data = np.zeros(img_data.shape).astype('float32')
    for i in range(img_data.shape[0]):
        norm_img_data[i,:,:] = (img_data[i,:,:]/255 - mean_vec[i]) / stddev_vec[i]
        
    #add batch channel
    norm_img_data = norm_img_data.reshape(1, 3, 224, 224).astype('float32')
    return norm_img_data

def softmax(x):
    x = x.reshape(-1)
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum(axis=0)

def postprocess(result):
    return softmax(np.array(result)).tolist()


#Define model source 
model_src = '/mnt/share/temp/DCDL_labelfiles/Models/BEET_ORIENTATION/BEET_ORIENTATION.onnx'
#Load model
session = onnxruntime.InferenceSession(model_src, None)
# get the name of the first input of the model
input_name = session.get_inputs()[0].name 
#Load file with images 
alllabels = '/mnt/share/temp/DCDL_labelfiles/REDBEET/detailed_labels.xlsx'
alllabels = pd.read_excel(alllabels)
scores = []
i = 0
for file in alllabels['imagefile']:
    if file != 'file not present':
        image_raw = Image.open(file)
        image = image_raw.resize((224,224))
        image_data = np.array(image).transpose(2, 0, 1)
        input_data = preprocess(image_data)
        raw_result = session.run([], {input_name: input_data})
        res = postprocess(raw_result)
        if res[0] < 0.7:
            scores.append('top')
        else:
            i += 1
            scores.append('side')
            dst = '/mnt/d/Datasets/DCDL/Experimentsroot/Multigerm/Measurements/XRay/multigerm'
            sidefilename = os.path.join(dst,f"side_{i}.bmp")
            image_raw.save(sidefilename)
    else:
        scores.append('None')

alllabels['side_prediction'] = scores
#Write to Excel
label_src = '/mnt/share/temp/DCDL_labelfiles/REDBEET'
#alllabels.to_excel(os.path.join(label_src,'detailed_labels_side.xlsx'),index=False)


#Load image and resize
#image = Image.open('XRAY_T01_G02.bmp')
#image = image.resize((224,224))
#print("Image size: ", image.size)
#image_data = np.array(image).transpose(2, 0, 1)
#input_data = preprocess(image_data)

#Start inference
#raw_result = session.run([], {input_name: input_data})
#res = postprocess(raw_result)
#print(res)
#0 = side 1 = top
