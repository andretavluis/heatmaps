import os
import pickle
import gazeplotter_ellipses
import gazeplotter_normal
import pandas as pd

from matplotlib.pyplot import close

XAMI_MIMIC_PATH = "D:\XAMI-MIMIC"

# Top 3 conditions
# conditions = ['pab', 'ate', 'cns']
conditions = ['ate']

# Test with 2 patients
# conditions = ['15752803', '19565653']

# conditions = ['13977589']

# All conditions
# conditions = ['abnmc', 'afr', 'awt', 'ate', 'cns', 'epy', 'ecs', 'ehi', 'fbr', 'frc', 
# 'gop', 'hhe', 'hlv', 'ild', 'lnm', 'mss', 'nod', 'pab', 'pef', 'pti', 'pne', 'ped', 'wmd']

for condition in conditions:
    print(condition)

    # Get the path to the current folder
    DIR = os.path.dirname(os.path.abspath(__file__))
    # Get the path to the image folder
    img_folder = 'images/images_' + condition
    IMGDIR = os.path.join(DIR, img_folder)
    # Get a list of all image names
    IMGNAMES = os.listdir(IMGDIR)
    # Sort IMGNAMES in alphabetical order
    IMGNAMES.sort()

    # Construct the name of the output directory
    output_folder = 'output/output_'+condition
    OUTPUTDIR = os.path.join(DIR, output_folder)

    # Check if the output directory exists yet
    if not os.path.isdir(OUTPUTDIR):
        # If the output directory does not exist yet, make it
        os.mkdir(OUTPUTDIR)

    # Read fixations data
    file_name = 'fixations/fixations_'+condition+'.pkl'
    with open(file_name, 'rb') as f:
        data = pickle.load(f)

    print(data[0].keys())

    # Read bbox data
    bbox_filename = 'bboxes/bboxes_'+condition+'.csv'
    bbox = pd.read_csv(bbox_filename)

    # Get the amount of trials in this dataset
    ntrials = len(data)

    count=0

    # Loop through all trials
    for trialnr in range(ntrials):

        # Get the image name
        imgname = data[trialnr]['image_name']+'.jpg'

        # Get the path to the image
        imgpath = os.path.join(IMGDIR, imgname)

        # Get the fixations in this trial
        fixations = data[trialnr]['events']['Efix']

        # Delete the first fixation
        fixations.pop(0)

        # Get the raw x and y gaze coordinates
        x = data[trialnr]['x']
        y = data[trialnr]['y']

        id_trial = int(data[trialnr]['id'])

        print(id_trial)

        bbox_new = bbox.loc[bbox['patient_id'].astype(int)==id_trial]
        # print(id_trial) 

        for study in bbox_new['study_id'].unique(): 
                
            id_study = study
            print(id_study)

            bbox_new = bbox.loc[(bbox['patient_id'].astype(int)==id_trial) & (bbox['study_id']==id_study)]

            # patients with condition
            if bbox_new.shape[0]>0 and imgname in os.listdir(IMGDIR):

                DISPSIZE = (bbox_new['img_width'].tolist()[0], bbox_new['img_height'].tolist()[0])

                # Plot a duration heatmap
                savename_h = 'heatmap_%s_%s_%s' % (id_trial, id_study, imgname)
                savepath = os.path.join(OUTPUTDIR, savename_h)
                fig = gazeplotter_ellipses.draw_heatmap(fixations, bbox_new, DISPSIZE, \
                    imagefile=imgpath, savefilename=savepath)
                close(fig)

                # Plot a pupil heatmap
                savename_h = 'pupil_heatmap_%s_%s_%s' % (id_trial, id_study, imgname)
                savepath = os.path.join(OUTPUTDIR, savename_h)
                fig = gazeplotter_ellipses.draw_heatmap(fixations, bbox_new, DISPSIZE, \
                    imagefile=imgpath, savefilename=savepath, pupil=True)
                close(fig)
                
                # # Plot the fixations
                # savename_f = 'fixations_%s_%s_%s' % (id_trial, id_study, imgname)
                # savepath = os.path.join(OUTPUTDIR, savename_f)
                # fig = gazeplotter_ellipses.draw_fixations(fixations, bbox_new, DISPSIZE, \
                #     durationsize=True, durationcolour=True, \
                #     imagefile=imgpath, savefilename=savepath)
                # close(fig)

                # #Plot raw gaze data
                # savename = 'gaze_%s_%s_%s' % (id_trial, id_study, imgname)
                # savepath = os.path.join(OUTPUTDIR, savename)
                # fig = gazeplotter_ellipses.draw_raw(x, y, bbox_new, DISPSIZE, 
                #                 imagefile=imgpath, savefilename=savepath)
                # close(fig)

                
                if count==11:
                    break
                count+=1

                exit()

            # patients without condition - normal
            elif bbox_new.shape[0]==0 and imgname in os.listdir(IMGDIR):

                img_width = data[trialnr]['img_width']
                img_height = data[trialnr]['img_height']

                print(id_trial)

                DISPSIZE = (img_width, img_height)

                # Plot a duration heatmap
                savename_h = 'heatmap_%s_%s_%s' % (id_trial, id_study, imgname)
                savepath = os.path.join(OUTPUTDIR, savename_h)
                fig = gazeplotter_normal.draw_heatmap(fixations, DISPSIZE, \
                    imagefile=imgpath, savefilename=savepath)
                close(fig)

                # Plot a pupil heatmap
                savename_h = 'pupil_heatmap_%s_%s_%s' % (id_trial, id_study, imgname)
                savepath = os.path.join(OUTPUTDIR, savename_h)
                fig = gazeplotter_normal.draw_heatmap(fixations, DISPSIZE, \
                    imagefile=imgpath, savefilename=savepath, pupil=True)
                close(fig)
                
                # # Plot the fixations
                # savename_f = 'fixations_%s_%s_%s' % (id_trial, id_study, imgname)
                # savepath = os.path.join(OUTPUTDIR, savename_f)
                # fig = gazeplotter_normal.draw_fixations(fixations, DISPSIZE, \
                #     durationsize=True, durationcolour=True, \
                #     imagefile=imgpath, savefilename=savepath)
                # close(fig)

                # #Plot raw gaze data
                # savename = 'gaze_%s_%s_%s' % (id_trial, id_study, imgname)
                # savepath = os.path.join(OUTPUTDIR, savename)
                # fig = gazeplotter_normal.draw_raw(x, y, DISPSIZE, 
                #                 imagefile=imgpath, savefilename=savepath)
                close(fig)




