import cv2
import os
import pandas as pd

#define label source
label_src = '/mnt/share/tempdata/Pauls_tijdelijke_rotzooi/DCDL_labelfiles/REDBEET/detailed_labels_side.xlsx'

metadata = pd.read_excel(label_src)

for _,row in metadata.iterrows():
    no_seedlings = row['no_seedlings']
    healthy_seedlings = row['healthy_seedlings']
    side = row['side_prediction']
    score = row['score']
    if row['imagefile'] != 'file not present':
        image = cv2.imread(row['imagefile'])
        cv2.putText(image,f'no: {str(no_seedlings)}',(10,15),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,255,255),1,cv2.LINE_AA)
        cv2.putText(image,f'no healthy: {str(healthy_seedlings)}',(10,30),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,255,255),1,cv2.LINE_AA)
        cv2.putText(image,f'side: {str(side)}',(10,45),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,255,255),1,cv2.LINE_AA)
        cv2.putText(image,f'score: {str(score)}',(10,60),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,255,255),1,cv2.LINE_AA)
        cv2.namedWindow('test')        
        cv2.moveWindow('test', 40,30)
        cv2.imshow('test',image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


