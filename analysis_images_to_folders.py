import os
import pickle
import gazeplotter_ellipses
import pandas as pd

from matplotlib.pyplot import close

XAMI_MIMIC_PATH = "D:\XAMI-MIMIC"

# Top 3 conditions
conditions = ['pab', 'ate', 'cns']
# conditions = ['ate']

# Test with 2 patients
# conditions = ['15752803', '19565653']

# conditions = ['13977589']

# All conditions
# conditions = ['abnmc', 'afr', 'awt', 'ate', 'cns', 'epy', 'ecs', 'ehi', 'fbr', 'frc', 
# 'gop', 'hhe', 'hlv', 'ild', 'lnm', 'mss', 'nod', 'pab', 'pef', 'pti', 'pne', 'ped', 'wmd']

# Master with paths
reflacx_with_fixations_df = pd.read_csv('reflacx_with_fixations.csv')

df = pd.DataFrame()

for condition in conditions:
    print(condition)

    # Read fixations data
    file_name = 'fixations/fixations_'+condition+'.pkl'
    with open(file_name, 'rb') as f:
        data = pickle.load(f)

    # Get the amount of trials in this dataset
    ntrials = len(data)

    count=0

    # Loop through all trials
    for trialnr in range(ntrials):

        print('Patient '+str(data[trialnr]['id'])+', study '+str(data[trialnr]['study_id']))

        paths = reflacx_with_fixations_df.loc[(reflacx_with_fixations_df['id']==data[trialnr]['study_id']) &
                                      (reflacx_with_fixations_df['subject_id']==data[trialnr]['id']) &
                                      (reflacx_with_fixations_df['dicom_id']==data[trialnr]['image_name'])]

        # Get the path to the image
        imgpath = paths['image_path']

        # Get output path
        savepath = "D:\XAMI-MIMIC" + paths['fixations_path'].values[0][17:]

        # Get the fixations in this trial
        fixations = data[trialnr]['events']['Efix']

        # Delete the first fixation
        fixations.pop(0)

        id_trial = int(data[trialnr]['id'])

        # print(id_trial)

        DISPSIZE = (int(paths['image_size_x']), int(paths['image_size_y']))

        # Plot a duration heatmap
        savename_h = 'time_heatmap'
        fig = gazeplotter_ellipses.draw_heatmap(fixations, None, DISPSIZE, \
            imagefile=imgpath, savefilename=savepath)
        close(fig)

        # # Plot a pupil heatmap
        # savename_h = 'pupil_heatmap'
        # savepath = os.path.join(OUTPUTDIR, savename_h)
        # fig = gazeplotter_ellipses.draw_heatmap(fixations, None, DISPSIZE, \
        #     imagefile=imgpath, savefilename=savepath, pupil=True)
        # close(fig)


        df = df.append(paths)

        count+=1
        if count==11:
            break

    df.to_csv('printed_paths.csv') 
    


