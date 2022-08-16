# Gaze Plotter
#
# Produces different kinds of plots that are generally used in eye movement
# research, e.g. heatmaps, scanpaths, and fixation locations as overlays of
# images.

import os
import numpy
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import pyplot, image
from matplotlib.patches import Ellipse

# COLOURS
# all colours are from the Tango colourmap, see:
# http://tango.freedesktop.org/Tango_Icon_Theme_Guidelines#Color_Palette
COLS = {	"butter": [	'#fce94f',
					'#edd400',
					'#c4a000'],
		"orange": [	'#fcaf3e',
					'#f57900',
					'#ce5c00'],
		"chocolate": [	'#e9b96e',
					'#c17d11',
					'#8f5902'],
		"chameleon": [	'#8ae234',
					'#73d216',
					'#4e9a06'],
		"skyblue": [	'#729fcf',
					'#3465a4',
					'#204a87'],
		"plum": 	[	'#ad7fa8',
					'#75507b',
					'#5c3566'],
		"scarletred":[	'#ef2929',
					'#cc0000',
					'#a40000'],
		"aluminium": [	'#eeeeec',
					'#d3d7cf',
					'#babdb6',
					'#888a85',
					'#555753',
					'#2e3436'],
		}
# FONT
FONT = {	'family': 'Ubuntu',
		'size': 12}
matplotlib.rc('font', **FONT)


# # # # #
# FUNCTIONS

def draw_fixations(fixations, bbox, dispsize, imagefile=None, durationsize=True, durationcolour=True, alpha=0.5, savefilename=None):
	
	"""Draws circles on the fixation locations, optionally on top of an image,
	with optional weigthing of the duration for circle size and colour
	
	arguments
	
	fixations		-	a list of fixation ending events from a single trial,
					as produced by edfreader.read_edf, e.g.
					edfdata[trialnr]['events']['Efix']
	dispsize		-	tuple or list indicating the size of the display,
					e.g. (1024,768)
	
	keyword arguments
	
	imagefile		-	full path to an image file over which the heatmap
					is to be laid, or None for no image; NOTE: the image
					may be smaller than the display size, the function
					assumes that the image was presented at the centre of
					the display (default = None)
	durationsize	-	Boolean indicating whether the fixation duration is
					to be taken into account as a weight for the circle
					size; longer duration = bigger (default = True)
	durationcolour	-	Boolean indicating whether the fixation duration is
					to be taken into account as a weight for the circle
					colour; longer duration = hotter (default = True)
	alpha		-	float between 0 and 1, indicating the transparancy of
					the heatmap, where 0 is completely transparant and 1
					is completely untransparant (default = 0.5)
	savefilename	-	full path to the file in which the heatmap should be
					saved, or None to not save the file (default = None)
	
	returns
	
	fig			-	a matplotlib.pyplot Figure instance, containing the
					fixations
	"""

	# FIXATIONS
	fix = parse_fixations(fixations)
	
	# IMAGE
	fig, ax = draw_display(dispsize, imagefile=imagefile)

	# CIRCLES
	# duration weigths
	if durationsize:
		siz = 100000.0 * (fix['dur']/30.0)
	else:
		siz = 100000.0 * numpy.median(fix['dur']/30.0)
	if durationcolour:
		col = fix['dur']
	else:
		col = COLS['chameleon'][2]
	# draw circles
	ax.scatter(fix['x'],fix['y'], s=siz, c=col, cmap='jet', marker='o', alpha=alpha, edgecolors='none')

	#Annotate
	# Loop for annotation of all points

	fix_words = parse_fixations_words(fixations)

	x = fix_words['x']
	y = fix_words['y']
	text = fix_words['word']

	for i in range(len(x)):
		ax.annotate(text[i], (x[i], y[i]), size=10, \
			bbox=dict(boxstyle="square", fc="cyan", ec="b", lw=2))

	#DRAW ELLIPSES
	NUM = bbox.index.tolist()

	ells = [Ellipse(xy=(bbox.at[i,'h'],bbox.at[i,'k']),
					width=bbox.at[i, 'a']*2,
					height=bbox.at[i, "b"]*2, 
					edgecolor='red',
                    facecolor='None',
					linewidth=10)
					for i in NUM]

	for e in ells:
		ax.add_artist(e)
		e.set_clip_box(ax.bbox)
		e.set_alpha(alpha)

	ax.legend(ells, ['Certainty {}'.format( bbox.at[i, "certainty"]) for i in NUM], fontsize='xx-large')

	# FINISH PLOT
	# invert the y axis, as (0,0) is top left on a display
	ax.invert_yaxis()

	# save the figure if a file name was provided
	if savefilename != None:
		fig.savefig(savefilename)
	
	return fig


def draw_heatmap(fixations, bbox=None, dispsize=None, imagefile=None, durationweight=True, alpha=0.5, savefilename=None, pupil=False):
	
	"""Draws a heatmap of the provided fixations, optionally drawn over an
	image, and optionally allocating more weight to fixations with a higher
	duration.
	
	arguments
	
	fixations		-	a list of fixation ending events from a single trial,
					as produced by edfreader.read_edf, e.g.
					edfdata[trialnr]['events']['Efix']
	dispsize		-	tuple or list indicating the size of the display,
					e.g. (1024,768)
	
	keyword arguments
	
	imagefile		-	full path to an image file over which the heatmap
					is to be laid, or None for no image; NOTE: the image
					may be smaller than the display size, the function
					assumes that the image was presented at the centre of
					the display (default = None)
	durationweight	-	Boolean indicating whether the fixation duration is
					to be taken into account as a weight for the heatmap
					intensity; longer duration = hotter (default = True)
	alpha		-	float between 0 and 1, indicating the transparancy of
					the heatmap, where 0 is completely transparant and 1
					is completely untransparant (default = 0.5)
	savefilename	-	full path to the file in which the heatmap should be
					saved, or None to not save the file (default = None)
	
	returns
	
	fig			-	a matplotlib.pyplot Figure instance, containing the
					heatmap
	"""

	if pupil:
		# FIXATIONS
		fix = parse_pupil(fixations)
	else:
		# FIXATIONS
		fix = parse_fixations(fixations)
	
	# IMAGE
	fig, ax = draw_display(dispsize, imagefile=imagefile)

	# HEATMAP
	# Gaussian
	gwh = 200
	gsdwh = gwh/6
	gaus = gaussian(gwh,gsdwh)
	# matrix of zeroes
	strt = gwh/2
	heatmapsize = dispsize[1] + 2*strt, dispsize[0] + 2*strt

	heatmapsize = (int(heatmapsize[0]), int(heatmapsize[1]))

	heatmap = numpy.zeros(heatmapsize, dtype=float)
	# create heatmap
	for i in range(0,len(fix['x'])):
		# get x and y coordinates
		x = strt + fix['x'][i] - int(gwh/2)
		y = strt + fix['y'][i] - int(gwh/2)
		# correct Gaussian size if either coordinate falls outside of
		# display boundaries
		if (not 0 < x < dispsize[0]) or (not 0 < y < dispsize[1]):
			hadj=[0,gwh];vadj=[0,gwh]
			if 0 > x:
				hadj[0] = abs(x)
				x = 0
			elif dispsize[0] < x:
				hadj[1] = gwh - int(x-dispsize[0])
			if 0 > y:
				vadj[0] = abs(y)
				y = 0
			elif dispsize[1] < y:
				vadj[1] = gwh - int(y-dispsize[1])
			# add adjusted Gaussian to the current heatmap
			try:
				if pupil:
					heatmap[y:y+vadj[1],x:x+hadj[1]] += gaus[vadj[0]:vadj[1],hadj[0]:hadj[1]] * fix['pupil'][i]
				else: 
					heatmap[y:y+vadj[1],x:x+hadj[1]] += gaus[vadj[0]:vadj[1],hadj[0]:hadj[1]] * fix['dur'][i]
			except:
				# fixation was probably outside of display
				pass
		else:				
			# add Gaussian to the current heatmap
			if pupil:
				heatmap[int(y):int(y+gwh),int(x):int(x+gwh)] += gaus * fix['pupil'][i]
			else:
				heatmap[int(y):int(y+gwh),int(x):int(x+gwh)] += gaus * fix['dur'][i]

	# resize heatmap
	heatmap = heatmap[int(strt):int(dispsize[1]+strt),int(strt):int(dispsize[0]+strt)]
	# remove zeros
	lowbound = numpy.mean(heatmap[heatmap>0])
	heatmap[heatmap<lowbound] = numpy.NaN
	# draw heatmap on top of image
	ax.imshow(heatmap, cmap='jet', alpha=alpha)

	#DRAW ELLIPSES ON TOP OF HEATMAPS
	# NUM = bbox.index.tolist()

	# ells = [Ellipse(xy=(bbox.at[i,'h'],bbox.at[i,'k']),
	# 				width=bbox.at[i, 'a']*2,
	# 				height=bbox.at[i, "b"]*2, 
	# 				edgecolor='red',
    #                 facecolor='None',
	# 				linewidth=10)
	# 				for i in NUM]

	# for e in ells:
	# 	ax.add_artist(e)
	# 	e.set_clip_box(ax.bbox)
	# 	e.set_alpha(alpha)

	# ax.legend(ells, ['Certainty {}'.format( bbox.at[i, "certainty"]) for i in NUM], fontsize='xx-large')

	# FINISH PLOT
	# invert the y axis, as (0,0) is top left on a display
	ax.invert_yaxis()
	# save the figure if a file name was provided
	if savefilename != None:
		fig.savefig(savefilename)
	
	return fig

def draw_ellipses(bbox, dispsize, imagefile=None, alpha=0.5, savefilename=None):

	NUM = bbox.index.tolist()

	ells = [Ellipse(xy=(bbox.at[i,'h'],bbox.at[i,'k']),
					width=bbox.at[i, 'a']*2,
					height=bbox.at[i, "b"]*2, 
					edgecolor='red',
                    facecolor='None',
					linewidth=10)
					for i in NUM]
	
	# IMAGE
	fig, ax = draw_display(dispsize, imagefile=imagefile)

	for e in ells:
		ax.add_artist(e)
		e.set_clip_box(ax.bbox)
		e.set_alpha(alpha)

	ax.legend(ells, ['Certainty {}'.format( bbox.at[i, "certainty"]) for i in NUM], fontsize='xx-large')

	ax.invert_yaxis()

	if savefilename != None:
		fig.savefig(savefilename)
	
	return fig


def draw_raw(x, y, bbox, dispsize, imagefile=None, savefilename=None, alpha=0.5):
	
	"""Draws the raw x and y data
	
	arguments
	
	x			-	a list of x coordinates of all samples that are to
					be plotted
	y			-	a list of y coordinates of all samples that are to
					be plotted
	dispsize		-	tuple or list indicating the size of the display,
					e.g. (1024,768)
	
	keyword arguments
	
	imagefile		-	full path to an image file over which the heatmap
					is to be laid, or None for no image; NOTE: the image
					may be smaller than the display size, the function
					assumes that the image was presented at the centre of
					the display (default = None)
	savefilename	-	full path to the file in which the heatmap should be
					saved, or None to not save the file (default = None)
	
	returns
	
	fig			-	a matplotlib.pyplot Figure instance, containing the
					fixations
	"""	
	# image
	fig, ax = draw_display(dispsize, imagefile=imagefile)

	n = int(x.shape[0]/3)

	# plot raw data points
	ax.plot(x[:n], y[:n], 'o', color='green', markeredgecolor='green')
	ax.plot(x[n:n*2], y[n:n*2], 'o', color='yellow', markeredgecolor='yellow')
	ax.plot(x[n*2:n*3], y[n*2:n*3], 'o', color='blue', markeredgecolor='blue')

	#Draw ellipses on top of gaze
	NUM = bbox.index.tolist()

	ells = [Ellipse(xy=(bbox.at[i,'h'],bbox.at[i,'k']),
					width=bbox.at[i, 'a']*2,
					height=bbox.at[i, "b"]*2, 
					edgecolor='red',
                    facecolor='None',
					linewidth=10)
					for i in NUM]

	for e in ells:
		ax.add_artist(e)
		e.set_clip_box(ax.bbox)
		e.set_alpha(alpha)

	ax.legend(ells, ['Certainty {}'.format( bbox.at[i, "certainty"]) for i in NUM], fontsize='xx-large')

	# invert the y axis, as (0,0) is top left on a display
	ax.invert_yaxis()
	# save the figure if a file name was provided
	if savefilename != None:
		fig.savefig(savefilename)
	
	return fig

# # # # #
# HELPER FUNCTIONS


def draw_display(dispsize, imagefile=None):
	
	"""Returns a matplotlib.pyplot Figure and its axes, with a size of
	dispsize, a black background colour, and optionally with an image drawn
	onto it
	
	arguments
	
	dispsize		-	tuple or list indicating the size of the display,
					e.g. (1024,768)
	
	keyword arguments
	
	imagefile		-	full path to an image file over which the heatmap
					is to be laid, or None for no image; NOTE: the image
					may be smaller than the display size, the function
					assumes that the image was presented at the centre of
					the display (default = None)
	
	returns
	fig, ax		-	matplotlib.pyplot Figure and its axes: field of zeros
					with a size of dispsize, and an image drawn onto it
					if an imagefile was passed
	"""
	
	# construct screen (black background)
	screen = numpy.zeros((int(dispsize[1]),int(dispsize[0])), dtype='uint8')
	# if an image location has been passed, draw the image
	# if imagefile != None:
	# 	# check if the path to the image exists
	# 	if not os.path.isfile(imagefile):
	# 		raise Exception("ERROR in draw_display: imagefile not found at '%s'" % imagefile)
	# 	# load image
	# 	img = image.imread(imagefile)


	# 	# # flip image over the horizontal axis
	# 	# # (do not do so on Windows, as the image appears to be loaded with
	# 	# # the correct side up there; what's up with that? :/)
	# 	# if os.name == 'nt':
	# 	# 	img = numpy.flipud(img)
	# 	# width and height of the image
	# 	w, h = len(img[0]), len(img)
	# 	# x and y position of the image on the display
	# 	x = dispsize[0]/2 - w/2
	# 	y = dispsize[1]/2 - h/2

	# 	screen[int(y):int(y+h),int(x):int(x+w)] = img


	# dots per inch
	dpi = 100.0
	# determine the figure size in inches
	figsize = (dispsize[0]/dpi, dispsize[1]/dpi)
	# create a figure
	fig = pyplot.figure(figsize=figsize, dpi=dpi, frameon=False)
	ax = pyplot.Axes(fig, [0,0,1,1])
	ax.set_axis_off()
	fig.add_axes(ax)
	# plot display
	ax.axis([0,dispsize[0],0,dispsize[1]])
	ax.imshow(screen, cmap='binary')#, origin='upper')
	
	return fig, ax


def gaussian(x, sx, y=None, sy=None):
	
	"""Returns an array of numpy arrays (a matrix) containing values between
	1 and 0 in a 2D Gaussian distribution
	
	arguments
	x		-- width in pixels
	sx		-- width standard deviation
	
	keyword argments
	y		-- height in pixels (default = x)
	sy		-- height standard deviation (default = sx)
	"""
	
	# square Gaussian if only x values are passed
	if y == None:
		y = x
	if sy == None:
		sy = sx
	# centers	
	xo = x/2
	yo = y/2
	# matrix of zeros
	M = numpy.zeros([y,x],dtype=float)
	# gaussian matrix
	for i in range(x):
		for j in range(y):
			M[j,i] = numpy.exp(-1.0 * (((float(i)-xo)**2/(2*sx*sx)) + ((float(j)-yo)**2/(2*sy*sy)) ) )

	return M


def parse_fixations(fixations):
	
	"""Returns all relevant data from a list of fixation ending events
	
	arguments
	
	fixations		-	a list of fixation ending events from a single trial,
					as produced by edfreader.read_edf, e.g.
					edfdata[trialnr]['events']['Efix']

	returns
	
	fix		-	a dict with three keys: 'x', 'y', and 'dur' (each contain
				a numpy array) for the x and y coordinates and duration of
				each fixation
	"""
	
	# empty arrays to contain fixation coordinates
	fix = {	'x':numpy.zeros(len(fixations)),
			'y':numpy.zeros(len(fixations)),
			'dur':numpy.zeros(len(fixations)),
			'word': []}
	# get all fixation coordinates
	for fixnr in range(len( fixations)):
		stime, etime, dur, pupil, ex, ey, word = fixations[fixnr]
		fix['x'][fixnr] = ex
		fix['y'][fixnr] = ey
		fix['dur'][fixnr] = dur
		fix['word'].append(word)
	
	return fix


def parse_fixations_words(fixations):
	
	# empty arrays to contain fixation coordinates

	fix = {	'x':numpy.zeros(len(fixations)),
			'y':numpy.zeros(len(fixations)),
			'pupil':numpy.zeros(len(fixations)),
			'word': numpy.zeros(len(fixations), dtype = 'object')}

	# filter fixatons with higher pupil
	for fixnr in range(len( fixations)):
		stime, etime, dur, pupil, ex, ey, word = fixations[fixnr]

		fix['pupil'][fixnr] = pupil

	for fixnr in range(len( fixations)):
		stime, etime, dur, pupil, ex, ey, word = fixations[fixnr]

		if pupil>numpy.quantile(fix['pupil'], 0.75):
			fix['x'][fixnr] = ex
			fix['y'][fixnr] = ey
			fix['word'][fixnr] = word

	# print(fix['x'])
	# print(fix['y'])
	# print(fix['word'])
			
	return fix

	
def parse_pupil(fixations):
	
	"""Returns all relevant data from a list of fixation ending events
	
	arguments
	
	fixations		-	a list of fixation ending events from a single trial,
					as produced by edfreader.read_edf, e.g.
					edfdata[trialnr]['events']['Efix']

	returns
	
	fix		-	a dict with three keys: 'x', 'y', and 'dur' (each contain
				a numpy array) for the x and y coordinates and duration of
				each fixation
	"""
	
	# empty arrays to contain fixation coordinates
	fix = {	'x':numpy.zeros(len(fixations)),
			'y':numpy.zeros(len(fixations)),
			'pupil':numpy.zeros(len(fixations))}
	# get all fixation coordinates
	for fixnr in range(len( fixations)):
		stime, etime, dur, pupil, ex, ey, word = fixations[fixnr]
		fix['x'][fixnr] = ex
		fix['y'][fixnr] = ey
		fix['pupil'][fixnr] = pupil
	
	return fix