import cv2
import os
import pandas as pd
import re 
import numpy as np
#define label source
label_src = '/mnt/share/tempdata/Pauls_tijdelijke_rotzooi/DCDL_labelfiles/REDBEET/detailed_labels_side.xlsx'

metadata = pd.read_excel(label_src)

for _,row in metadata.iterrows():
    no_seedlings = row['no_seedlings']
    healthy_seedlings = row['healthy_seedlings']
    side = row['side_prediction']
    score = row['score']
    if row['imagefile'] != 'file not present':
        image = np.invert(cv2.imread(row['imagefile']))
        imagefile_VIS = re.sub("XRAY","VIS",row['imagefile'])
        image_VIS = cv2.imread(imagefile_VIS)
        #imagefile_CF = re.sub("XRAY","CF",row['imagefile'])
        #image_CF = cv2.imread(imagefile_CF)
        #image_CF = cv2.resize(image_CF,(500,500))
        text_color = (0,0,0)
        cv2.putText(image,f'no: {str(no_seedlings)}',(10,15),cv2.FONT_HERSHEY_SIMPLEX,0.5,text_color,1,cv2.LINE_AA)
        cv2.putText(image,f'no healthy: {str(healthy_seedlings)}',(10,30),cv2.FONT_HERSHEY_SIMPLEX,0.5,text_color,1,cv2.LINE_AA)
        cv2.putText(image,f'side: {str(side)}',(10,45),cv2.FONT_HERSHEY_SIMPLEX,0.5,text_color,1,cv2.LINE_AA)
        cv2.putText(image,f'score: {str(score)}',(10,60),cv2.FONT_HERSHEY_SIMPLEX,0.5,text_color,1,cv2.LINE_AA)
        cv2.namedWindow('test')        
        cv2.moveWindow('test', 40,30)
        try:
            final_img = np.hstack((image_VIS,image))
        except Exception as e:
            print(f"Failed with exception: {e}")
            final_img = image
        cv2.imshow('test',final_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()