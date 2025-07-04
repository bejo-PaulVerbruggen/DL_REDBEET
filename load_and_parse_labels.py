import numpy as np
import pandas as pd
import os
import re
import string

#Define labelfiles source directory
label_src = '/mnt/share/tempdata/Pauls_tijdelijke_rotzooi/DCDL_labelfiles/REDBEET'
#Find labelfiles
labelfilenames = [os.path.join(label_src,file) for file in os.listdir(label_src) if re.search('^Beoordelingsformulier',file) is not None]

def getlabels(labelfilename):
    titlerows = [1,13,27,39]
    rawlabels = pd.read_excel(labelfilename)
    variety = re.search(r'(?<=_)[A-Z]{5,8}(?=_)',labelfilename).group(0)
    for row in titlerows:
        testno = rawlabels.iloc[row,2]
        trayno = rawlabels.iloc[row,5].replace(" ","")
        labels = rawlabels.iloc[row+2:row+12,1:16]
        labels.columns = [str(number).zfill(2) for number in range(1,16)]
        labels.index = [f'{testno}-{trayno}-{letter}' for letter in string.ascii_uppercase[0:10]]
        labels = labels.melt(var_name='column',value_name='score',ignore_index=False)
        #labels['test'] = labels.index.str.split('-')[0][0]
        labels.insert(0,'test',labels.index.str.split('-')[0][0])
        labels.insert(1,'variety',variety)
        labels.insert(2,'tray',labels.index.str.split('-')[0][1])
        labels.insert(3,'row',[item[2] for item in labels.index.str.split('-') ])
        if row > 1:
            final_labels = pd.concat((final_labels,labels))
        else:
            final_labels = labels
    return final_labels
        
alllabels = pd.concat([getlabels(labelfilename) for labelfilename in labelfilenames])
#Add number of seedlings and number of healthy seedlings
no_seedlings = []
healthy_seedlings = []
label_valid = []
for score in alllabels['score']:
    if score == "M" or score=="L":
        valid = 0
    else:
        valid = 1
    if score == "NG" or score=="L" or score == "M":
        numberofplants = 0
        healthyplants = 0
    elif re.search(r'^[0-9]',score) is not None:
        numberofplants = int(re.search(r'^[0-9]',score).group(0))
    else: 
        numberofplants = 1
        if re.search(f'C2',score) is not None:
            healthyplants = numberofplants
        else:
            healthyplants = 0
    if numberofplants > 1:
        if len(score) < 4:
            healthyplants = numberofplants
        elif re.search(f'(?<={numberofplants})C2',score) is not None:
            healthyplants = numberofplants-1
        else:
            healthyplants = 0
    no_seedlings.append(numberofplants)
    healthy_seedlings.append(healthyplants)
    label_valid.append(valid)
alllabels['label_valid'] = label_valid
alllabels['no_seedlings'] = no_seedlings
alllabels['healthy_seedlings'] = healthy_seedlings

#Merge with the test and sample numbers
metadata = pd.read_csv(os.path.join(label_src,'sample_test.csv'),sep=";")
metadata['variety'] = [variety.upper() for variety in metadata['variety']]
alllabels = metadata.merge(alllabels,left_on=['test','variety'],right_on=['test','variety'])

#Add image locations 
image_src = '/mnt/share/SDC-ROBOT'
redbeet_dirs = [os.path.join(image_src,dir) for dir in os.listdir(image_src) if re.search(r'REDBEET',dir) is not None]
xray_file = []
for index, row in alllabels.iterrows():
    tray_no = row['tray'][0]
    tray_parallel = row['tray'][1]
    #Find the right dir
    xray_dir = [dir for dir in redbeet_dirs if re.search(f'{row['lot']}-{row['sample']}.*{tray_no}-{tray_parallel}$',dir) is not None][0]
    #Infer the image name
    xray_name = os.path.join(xray_dir,f'XRAY_T01_{row['row']}{row['column']}.bmp')
    #Check if the file exists
    if os.path.exists(xray_name):
        xray_file.append(xray_name)
    else:
        xray_file.append('file not present')

alllabels['imagefile'] = xray_file
#    xray_dir = re.search(f'^{row['lot']}-{row['sample']}-[0-9]{8}-{row['variety']}-{tray_no}-{tray_parallel}',os.listdir(image_src)[0])
#    print(xray_dir)
    

#Write to Excel
alllabels.to_excel(os.path.join(label_src,'detailed_labels.xlsx'),index=False)