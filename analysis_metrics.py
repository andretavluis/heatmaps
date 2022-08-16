import os
import pickle
import gazeplotter_ellipses
import gazeplotter_normal
import pandas as pd
from metrics import *

conditions = ['afr']

# conditions = ['15752803', '19565653']
# conditions = ['13977589']

# conditions = ['abnmc', 'afr', 'awt', 'ate', 'cns', 'epy', 'ecs', 'ehi', 'fbr', 'frc', 
# 'gop', 'hhe', 'hlv', 'ild', 'lnm', 'mss', 'nod', 'pab', 'pef', 'pti', 'pne', 'ped', 'wmd']

for condition in conditions:
    print(condition)

    # Read fixations data
    file_name = 'fixations/fixations_'+condition+'.pkl'
    with open(file_name, 'rb') as f:
        data = pickle.load(f)

    # Read bbox data
    bbox_filename = 'bboxes/bboxes_'+condition+'.csv'
    bbox = pd.read_csv(bbox_filename)

    # Get the amount of trials in this dataset
    ntrials = len(data)

    count=0

    # Loop through all trials
    for trialnr in range(ntrials):

        # count+=1
        
        # if count==6:
        #     break

        # Get the raw x and y gaze coordinates
        x = data[trialnr]['x']
        y = data[trialnr]['y']
        pupil = data[trialnr]['pupil_area_normalized']

        id_trial = int(data[trialnr]['id'])
        id_study = data[trialnr]['study_id']

        bbox_new = bbox.loc[(bbox['patient_id'].astype(int)==id_trial) & (bbox['study_id']==id_study)]   

        print(id_trial)

        if bbox_new.shape[0]>0:

            for index, row in bbox_new.iterrows():

                diag_duration, \
                percentage_gaze_inside_ellipse, \
                percentage_initial_inside_ellipse, \
                percentage_middle_inside_ellipse,\
                percentage_end_inside_ellipse, \
                avg_pupil_inside_el, \
                avg_pupil_initial_inside_el, \
                avg_pupil_middle_inside_el, \
                avg_pupil_end_inside_el = metrics(x, y, pupil, row, id_trial)

                index = bbox[(bbox['patient_id']==id_trial) & (bbox['h']==row['h'])].index[0]

                # print(index)
                bbox.at[index, 'diag_duration'] = diag_duration
                bbox.at[index, 'percentage_gaze_inside_el'] = percentage_gaze_inside_ellipse
                bbox.at[index, 'percentage_initial_inside_ellipse'] = percentage_initial_inside_ellipse          
                bbox.at[index, 'percentage_middle_inside_ellipse'] = percentage_middle_inside_ellipse     
                bbox.at[index, 'percentage_end_inside_ellipse'] = percentage_end_inside_ellipse  
                bbox.at[index, 'avg_pupil_inside_el'] = avg_pupil_inside_el
                bbox.at[index, 'avg_pupil_initial_inside_el'] = avg_pupil_initial_inside_el
                bbox.at[index, 'avg_pupil_middle_inside_el'] = avg_pupil_middle_inside_el
                bbox.at[index, 'avg_pupil_end_inside_el'] = avg_pupil_end_inside_el

        else:
            print('no bboxes')
                
                
    bbox[['patient_id','study_id','image_id','certainty','diag_duration', 'percentage_gaze_inside_el',\
        'percentage_initial_inside_ellipse', 'percentage_middle_inside_ellipse',\
        'percentage_end_inside_ellipse',   'avg_pupil_inside_el', 'avg_pupil_initial_inside_el', \
		   'avg_pupil_middle_inside_el', 'avg_pupil_end_inside_el']].to_csv('output/metrics_%s.csv' % condition)


