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
        labels.columns = [number for number in range(1,16)]
        labels.index = [f'{testno}-{trayno}-{letter}' for letter in string.ascii_uppercase[0:10]]
        labels = labels.melt(var_name='column',value_name='score',ignore_index=False)
        #labels['test'] = labels.index.str.split('-')[0][0]
        labels.insert(0,'test',labels.index.str.split('-')[0][0])
        labels.insert(1,'tray',labels.index.str.split('-')[0][1])
        labels.insert(2,'row',labels.index.str.split('-')[0][2])
        labels.insert(3,'variety',variety)
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
    if score == "NG" or score=="L":
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
    no_seedlings.append(numberofplants)
    healthy_seedlings.append(healthyplants)
    label_valid.append(valid)
alllabels['label_valid'] = label_valid
alllabels['no_seedlings'] = no_seedlings
alllabels['healthy_seedlings'] = healthy_seedlings

#Write to Excel
alllabels.to_excel(os.path.join(label_src,'detailed_labels.xlsx'),index=False)