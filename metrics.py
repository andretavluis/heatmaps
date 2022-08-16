#
# Metrics of similarity between points and elipses
#

import os
import numpy
import math
from matplotlib import pyplot, image
from matplotlib.patches import Ellipse

def metrics(x, y, pupil, bbox, id_trial):
	
	h = bbox['h']
	k = bbox['k']
	a = bbox['a']
	b = bbox['b']

	n = int(x.shape[0]/3)

	el_area = a*b*numpy.pi

	count = 0
	count_initial = 0
	count_middle = 0
	count_end = 0

	sum_pupil_inside_ellipse = 0
	sum_pupil_initial = 0
	sum_pupil_middle = 0
	sum_pupil_end = 0

	idx = 0
	for xx,yy,pup in zip(x,y,pupil):
		idx = idx+1
		#assume that points on top of the elipse line are inside the elipse
		if (checkpoint(h, k, xx, yy, a, b) <= 1): 
			sum_pupil_inside_ellipse+=pup
			count+=1

		if (checkpoint(h, k, xx, yy, a, b) <= 1) and idx<=n:
			sum_pupil_initial+=pup
			count_initial+=1

		if (checkpoint(h, k, xx, yy, a, b) <= 1) and idx>n and idx<=2*n:
			sum_pupil_middle+=pup
			count_middle+=1

		if (checkpoint(h, k, xx, yy, a, b) <= 1) and idx>2*n and idx<=3*n:
			sum_pupil_end+=pup
			count_end+=1
	
	# Qual a duração do diagnóstico? - Gaze está com resolução de 1ms, pelo que é multiplicar nº total de pontos por 1ms
	diag_duration = round(x.shape[0]*0.001,2)

	# Da gaze total, qual a percentagem que está dentro da elipse?
	percentage_gaze_inside_ellipse = numpy.log((count/x.shape[0])/el_area)

	# Da gaze no primeiro terço do diagnóstico, qual a percentagem que está dentro da elipse?
	percentage_initial_inside_ellipse = numpy.log((count_initial/n)/el_area)

	# Da gaze intermédia, qual a percentagem dentro da elipse?
	percentage_middle_inside_ellipse = numpy.log((count_middle/n)/el_area)

	# Da gaze final, qual a percentagem dentro da elipse?
	percentage_end_inside_ellipse = numpy.log((count_end/n)/el_area)

	# Qual a média da pupila dentro da elipse
	avg_pupil_inside_el = round(safe_div(sum_pupil_inside_ellipse,count),2)

	# Qual a media da pupila no primeiro terço do diagnóstico, dentro da elipse?
	avg_pupil_initial_inside_el = round(safe_div(sum_pupil_initial,count_initial),2)

	# Qual a media da pupila no meio diagnóstico, dentro da elipse?
	avg_pupil_middle_inside_el = round(safe_div(sum_pupil_middle,count_middle),2)

	# Qual a média da pupila no fim do diagnostico, dentro da elipse?
	avg_pupil_end_inside_el = round(safe_div(sum_pupil_end,count_end),2)

	if count == 0 |	count_initial == 0 |	count_middle == 0 |	count_end == 0:
		print(f'TRIAL WITH NO GAZE INSIDE ELLIPSE {id_trial}')
	
	

	return diag_duration,\
		   percentage_gaze_inside_ellipse, \
		   percentage_initial_inside_ellipse, \
		   percentage_middle_inside_ellipse, \
		   percentage_end_inside_ellipse, \
		   avg_pupil_inside_el, \
		   avg_pupil_initial_inside_el, \
		   avg_pupil_middle_inside_el, \
		   avg_pupil_end_inside_el

# Function to check if the point is
def checkpoint(h, k, x, y, a, b):
 
    # checking the equation of
    # ellipse with the given point
    p = ((math.pow((x - h), 2) / math.pow(a, 2)) +
         (math.pow((y - k), 2) / math.pow(b, 2)))
 
    return p

def safe_div(x,y):
    if y == 0:
        return 0
    return x / y
