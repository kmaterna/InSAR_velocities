#!/usr/bin/python
# Reviewing the NSBAS core functions
# July 2019

import numpy as np
import matplotlib.pyplot as plt
import glob
import scipy.io.netcdf as netcdf
import readmytupledata as rmd
import netcdf_read_write as rwr
import math
import datetime as dt
import sys


def configure():
	myfiles_phase = glob.glob("intf_all_remote/???????_???????/unwrap_ref.grd")
	myfiles_no_ramp = glob.glob("intf_all_remote/???????_???????/unwrap_ref_corrected.grd")
	manual_remove="Metadata/manual_remove.txt";
	wavelength=56; # mm
	nsbas_good_num=50; # % of images above coherence threshold
	wls_flag = 1
	remove_ramp_flag = 0
	smoothing=0.05;
	outfile='Stacking/NSBAS/Ionosphere_corrected/Experimental_Smooth/velocity_NSBAS_reasonable_smooth4.grd'
	signal_spread_file="signalspread_please_test.nc"
	return myfiles_no_ramp, remove_ramp_flag, wls_flag, myfiles_phase, manual_remove, signal_spread_file, wavelength, nsbas_good_num, smoothing, outfile;


# ------------ INPUTS ------------ #
def inputs(myfiles_no_ramp, remove_ramp_flag, myfiles_phase, signal_spread_file, manual_remove, number_of_excluded_images, wls_flag=0):
	signal_spread_data=rwr.read_grd(signal_spread_file);
	f = open(manual_remove, 'r')
	raw, content = f.readlines()[0:number_of_excluded_images], []
	for i in range(len(raw)):
		content.append(raw[i].strip('\n'))
	filesmodified = []
	for i in range(len(myfiles_phase)):
		if myfiles_phase[i][16:31] not in content:
			filesmodified.append(myfiles_phase[i])
	if remove_ramp_flag != 0:
		f = open("Metadata/Ramp_need_fix.txt", 'r')
		raw, content = f.readlines()[:], []
		for i in range(len(raw)):
		    content.append(raw[i].strip('\n'))
		myfiles_new = []
		for i in range(len(filesmodified)):
			test = filesmodified[i].replace("ref", "ref_corrected")
			if test in myfiles_no_ramp:
				myfiles_new.append(test)
			if filesmodified[i][16:31] not in content:
				myfiles_new.append(filesmodified[i])
		print(len(myfiles_new))
		datatuple=rmd.reader(myfiles_new);
	if remove_ramp_flag == 0:
		print(len(filesmodified))
		datatuple=rmd.reader(filesmodified);
	if wls_flag == 1:
		filesmodified_coherence = [x.replace(x[32:], "corr.grd") for x in filesmodified]
		coherence_cube = rmd.reader(filesmodified_coherence)
		coherence_cube = coherence_cube.zvalues
	else:
		coherence_cube = np.ones(np.shape(datatuple.zvalues))
	print(datatuple.dates_correct)
	dates = read_dates(myfiles_phase);
	date_pairs = datatuple.dates_correct
	print("Reading %d interferograms from %d acquisitions. " % (len(date_pairs), len(dates) ) );
	return datatuple, signal_spread_data, dates, date_pairs, coherence_cube;


def read_dates(myfiles_phase):
	dates=[];
	for ifile in myfiles_phase:
		pairname=ifile.split('/')[-2][0:15];
		image1=pairname.split('_')[0];
		image2=pairname.split('_')[1];
		dates.append(image1);
		dates.append(image2);
	dates=list(set(dates)); # find the unique days.
	dates=sorted(dates);
	for i in range(len(dates)):
		dates[i] = str(int(dates[i]) + 1)
	return dates


# ------------ COMPUTE ------------ #
def compute(coherence_cube, datatuple, nsbas_good_num, signal_spread_data, dates, date_pairs, smoothing, wavelength, outfile, wls_flag=0):
    zdata=datatuple.zvalues;
    # The point here is to loop through each pixel, determine if there's enough data to use, and then
    # make an SBAS matrix describing each image that's a real number (not nan).
    print("Analyzing the nsbas timeseries per pixel.")
    [zdim, xdim, ydim] = np.shape(zdata)
    print(np.shape(zdata))
    vel = np.zeros([xdim, ydim]);
    # for i in range(xdim):  # A loop through each pixel.
    # 	for j in range(ydim):
    i,j,f,c = 0,0,0,0
    pixel_value, coherence_value = [], []
    for z in np.nditer(zdata, order='F'):
        pixel_value.append(zdata[f][i][j]);  # slicing the values of phase for a pixel across the various interferograms
        coherence_value.append(coherence_cube[f][i][j])
        f+=1
        if f == zdim:
            if signal_spread_data[i][j] >= nsbas_good_num:
                vel[i][j] = do_nsbas_pixel(coherence_value, pixel_value, dates, date_pairs, smoothing, wavelength, wls_flag)
            else:
                vel[i][j] = np.nan
            pixel_value = []
            coherence_value = []
            c+=1
            print(c)
            f=0
            j+=1
            if j== ydim:
                j=0
                i+=1
                if i == xdim:
                    i=0
    return vel;



def do_nsbas_pixel(coherence_value, pixel_value, dates, date_pairs, smoothing, wavelength, wls_flag=0):
	# pixel_value: if we have 62 intf, this is a (62,) array of the phase values in each interferogram.
	# dates: if we have 35 images, this is the date of each image
	# date_pairs: if we have 62 intf, this is a (62) list with the image pairs used in each image
	# for x in range(len(dates)-1):
	d = np.array([]);
	diagonals = []
	dates=sorted(dates);
	date_pairs_used=[];
	for i in range(len(pixel_value)):
		if not math.isnan(pixel_value[i]):
			d = np.append(d, pixel_value[i]);  # removes the nans from the computation.
			diagonals.append(coherence_value[i])
			date_pairs_used.append(date_pairs[i]); # might be a slightly shorter array of which interferograms actually got used.
	model_num=len(dates)-1;

	Wavg = np.nanmean(diagonals)
	for i in range(model_num-1):
		diagonals.append(Wavg)
	W = np.diag(diagonals);
	G = np.zeros([len(date_pairs_used)+model_num-1, model_num]);  # in one case, 91x35
	# print(np.shape(G));

	for i in range(len(d)):  # building G matrix line by line.
		ith_intf = date_pairs_used[i];
		first_image=ith_intf.split('_')[0]; # in format '2017082'
		second_image=ith_intf.split('_')[1]; # in format '2017094'
		first_index=dates.index(first_image);
		second_index=dates.index(second_image);
		for j in range(second_index-first_index):
			G[i][first_index+j]=1;

	# Building the smoothing matrix with 1, -1 pairs
	for i in range(len(date_pairs_used),len(date_pairs_used)+model_num-1):
		position=i-len(date_pairs_used);
		G[i][position]=1*smoothing;
		G[i][position+1]=-1*smoothing;
		d = np.append(d,0);

	# solving the SBAS linear least squares equation for displacement between each epoch.
	if wls_flag == 1:
		GTWG = np.dot(np.transpose(G), np.dot(W,G))
		GTWd = np.dot(np.transpose(G), np.dot(W,d))
		m = np.dot(np.linalg.inv(GTWG), GTWd )
	else:
		m = np.linalg.lstsq(G,d)[0];

	# modeled_data=np.dot(G,m);
	# plt.figure();
	# plt.plot(d,'.b');
	# plt.plot(modeled_data,'.--g');
	# plt.savefig('d_vs_m.eps')
	# plt.close();

	# Adding up all the displacement.
	m_cumulative=[];
	m_cumulative.append(0);
	for i in range(len(m)):
		m_cumulative.append(np.sum(m[0:i]));  # The cumulative phase from start to finish!


	# Solving for linear velocity
	x_axis_datetimes=[dt.datetime.strptime(x,"%Y%j") for x in dates];
	x_axis_days=[(x - x_axis_datetimes[0]).days for x in x_axis_datetimes];  # number of days since first acquisition.

	x=np.zeros([len(x_axis_days),2]);
	y=np.array([]);
	for i in range(len(x_axis_days)):
		x[i][0]=x_axis_days[i];
		x[i][1]=1;
		y=np.append(y,[m_cumulative[i]]);
	model_slopes = np.linalg.lstsq(x,y)[0];  # units: phase per day.
	model_line = [model_slopes[1]+ x*model_slopes[0] for x in x_axis_days];

	# Velocity conversion: units in mm / year
	vel=model_slopes[0];  # in radians per day
	vel=vel*wavelength*365.24/2.0/(2*np.pi);

	return vel;

def estimated_gpsvel(netcdfname):
	z = rwr.read_grd(netcdfname)
	est = []
	for i in range(len(xfinal_ratioed)):
		est.append(np.nanmean(z[(yfinal_ratioed[i]-50):(yfinal_ratioed[i]+51),(xfinal_ratioed[i]-50):(xfinal_ratioed[i]+51) ]))
	return est

def misfit(gpsvel, estimated_gpsvel):
	differences = []
	for i in range(len(gpsvel)):
		if np.isnan(estimated_gpsvel[i]) != True:
			differences.append(abs(estimated_gpsvel[i]-gpsvel[i]))
	differences_squared = [d**2 for d in differences]
	misfit = np.sqrt(np.sum(differences_squared)/len(differences_squared))
	return misfit

def overlay_gps(netcdfname, smoothing, misfit):
	z = rwr.read_grd(netcdfname)
	ma = np.nanmax(z, axis=None, out=None)
	mi = np.nanmin(z, axis=None, out=None)

	xread, yread, zread = rwr.read_grd_xyz(netcdfname)

	# Make a plot
	fig = plt.figure(figsize=(7,10));
	ax1 = fig.add_axes([0.0, 0.1, 0.9, 0.8]);
	image = plt.imshow(zread,aspect=1.2,extent=[15.984871407, 21116.0151286,12196 , 4.4408920985*(10**-16) ],cmap='jet', vmin=-10, vmax=10);
	plt.gca().invert_xaxis()
	# plt.gca().invert_yaxis()
	plt.title('Reasonable Weighted NSBAS with ramps - smoothing factor: ' + str(smoothing) + ' -  Misfit: '+ str(misfit));
	plt.gca().set_xlabel("Range",fontsize=16);
	plt.gca().set_ylabel("Azimuth",fontsize=16);
	scatter = plt.gca().scatter(xfinal, yfinal , c=velfinal, marker='v', s=100, cmap='jet', vmin=-10, vmax=10)
	cb = plt.colorbar(image);
	cb.set_label('velocity in mm/yr', size=16);
	plt.show()
	return

if __name__=="__main__":
	myfiles_no_ramp, remove_ramp_flag, wls_flag, myfiles_phase, manual_remove, signal_spread_file, wavelength, nsbas_good_num, smoothing, outfile = configure();
	# datatuple, signal_spread_data, dates, date_pairs, coherence_cube = inputs(myfiles_no_ramp, remove_ramp_flag, myfiles_phase, signal_spread_file, manual_remove, 15, wls_flag);
	# vel = compute(coherence_cube, datatuple, nsbas_good_num, signal_spread_data, dates, date_pairs, smoothing, wavelength, outfile, wls_flag);
	# rwr.produce_output_netcdf(datatuple.xvalues, datatuple.yvalues, vel, 'velocity',outfile);
	# rwr.flip_if_necessary(outfile);
	# rwr.produce_output_plot(outfile, 'Weighted Reasonable NSBAS - smoothing factor: ' + str(smoothing), 'Stacking/NSBAS/velocity_weighted50NSBAS_reasonable_smoothlowest.png', 'velocity in mm/yr')
	
	# x,y,vel = rwr.read_grd_xyz(outfile)
	# signal = rwr.read_grd(signal_spread_file)
	# updated_vel = np.zeros((np.shape(vel)))
	# i, j,c  = 0, 0, 0
	# for v in np.nditer(vel):
	# 	print(c)
	# 	if signal[i,j] < 65 and signal[i,j] > 50:
	# 		updated_vel[i,j] = np.nan
	# 	else:
	# 		updated_vel[i,j] = vel[i,j]
	# 	j+=1
	# 	c+=1
	# 	if j==len(x):
	# 		j=0
	# 		i+=1
	# 		if i == len(y):
	# 			i=0


	# f = open('Metadata/gps_ra_los.xyz', 'r')
	# raw = f.read()
	# content = raw.split('\n')
	# content.pop()
	# for i in range(len(content)):
	# 	content[i] = content[i].split(" ", 2)
	#
	# x, y , vel = [], [], []
	# for i in range(len(content)):
	# 	x.append(float(content[i][0]))
	# 	y.append(float(content[i][1]))
	# 	vel.append(float(content[i][2]))
	#
	# r = len(x)
	# print(len(x))
	# print(len(y))
	# print(len(vel))
	#
	# xfinal, yfinal, velfinal = [], [], []
	#
	# for i in range(r):
	# 	if x[i] > 15.984871407 and x[i] < 21116.0151286 and y[i] > 4.4408920985*(10**-16) and y[i] < 12196:
	# 		xfinal.append(x[i])
	# 		yfinal.append(y[i])
	# 		velfinal.append(vel[i])
	#
	#
	# xratio, yratio = (21116.0151286-15.984871407)/661 , 7.9973770491803275
	# xfinal_ratioed, yfinal_ratioed = [int(round(i/xratio)) for i in xfinal], [int(round(i/yratio)) for i in yfinal]
	#
	# grdfile = outfile
	#
	# est = estimated_gpsvel(grdfile)
	# misfit = misfit(velfinal, est )
	#
	#
	# overlay_gps(grdfile, smoothing, misfit )
