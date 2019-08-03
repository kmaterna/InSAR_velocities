#!/usr/bin/python

import numpy as np
import matplotlib.pyplot as plt
import glob
import scipy.io.netcdf as netcdf
from subprocess import call
import readmytupledata as rmd
import netcdf_read_write as rwr
import math
import datetime as dt
import sys
import nsbas_core_functions as ncf


filenames = [["Stacking/Simple_Stack/velo_prof_reasonable50_remastered.grd", 0],
["Stacking/Simple_Stack/Ionosphere_corrected/velo_prof_reasonable50_remastered.grd", 0],
["Stacking/NSBAS/velocity_NSBAS_reasonable_smooth1_thres50.grd", 1],
["Stacking/NSBAS/velocity_NSBAS_reasonable_thresh50_smoothlowest.grd", 0.05],
["Stacking/NSBAS/Ionosphere_corrected/Smooth_low/velo_NSBAS_reasonable_smoothlower.grd", 0.25],
["Stacking/NSBAS/Ionosphere_corrected/Smooth_1/velo_NSBAS_reasonable_smooth1.grd", 1],
# ["Stacking/NSBAS/Ionosphere_corrected/Smooth_1/velo_NSBAS_reasonable50_smooth1.grd", 1], could not find file - so restack!
["Stacking/NSBAS/Ionosphere_corrected/Smooth_4/velocity_NSBAS_reasonable_smooth4.grd", 4],
["Stacking/NSBAS/Ionosphere_corrected/Smooth_8/velo_NSBAS_reasonable50_smooth8.grd", 8],
["Stacking/NSBAS/Ionosphere_corrected/Smooth_4/velocity_weighted50NSBAS_reasonable_smooth4.grd", 4],
["Stacking/NSBAS/Ionosphere_corrected/Smooth_1/velocity_weighted50NSBAS_reasonable_smooth1.grd", 1],
["Stacking/NSBAS/Ionosphere_corrected/Smooth_low/velocity_weighted50NSBAS_reasonable_smoothlow.grd", 0.5],
["Stacking/NSBAS/Ionosphere_corrected/Smooth_low/velocity_weighted50NSBAS_reasonable_smoothlower.grd", 0.25],
["Stacking/NSBAS/Ionosphere_corrected/Smooth_low/velocity_weighted50NSBAS_reasonable_smoothlowest.grd", 0.05],
["Stacking/NSBAS/velocity_weighted50NSBAS_reasonable_smoothlowest.grd", 0.05],
["Stacking/NSBAS/velocity_weighted50NSBAS_reasonable_smooth1.grd", 1]]
method = ['Simple Stack', 'NSBAS', 'WNSBAS']
smoothing = ['0.05', '0.25', '0.5', '1', '4', '8']
signal_threshold = ['50', '65']

f = open('Metadata/gps_ra_los_3D.xyz', 'r')
raw = f.read()
content = raw.split('\n')
content.pop()
for i in range(len(content)):
	content[i] = content[i].split(" ", 2)

x, y , vel = [], [], []
for i in range(len(content)):
	x.append(float(content[i][0]))
	y.append(float(content[i][1]))
	vel.append(float(content[i][2]))


xfinal, yfinal, velfinal = [], [], []

for i in range(len(x)):
	if x[i] > 15.984871407 and x[i] < 21116.0151286 and y[i] > 4.4408920985*(10**-16) and y[i] < 12196:
		xfinal.append(x[i])
		yfinal.append(y[i])
		velfinal.append(vel[i])


xratio, yratio = (21116.0151286-15.984871407)/661 , 7.9973770491803275
xfinal_ratioed, yfinal_ratioed = [int(round(i/xratio)) for i in xfinal], [int(round(i/yratio)) for i in yfinal]

def estimated_gpsvel(netcdfname):
	z = rwr.read_grd(netcdfname)
	est = []
	for i in range(len(xfinal_ratioed)):
		pixel_box = z[(yfinal_ratioed[i]-50):(yfinal_ratioed[i]+51),(xfinal_ratioed[i]-50):(xfinal_ratioed[i]+51) ]
		est.append(np.nanmean(pixel_box))
	return est

def result(filename, misfit, smoothing=0):
    result = ''
    if '_NSBAS_' in filename:
        result = result + method[1]
    if 'weighted50NSBAS' in filename:
        result = result +  method[2]
    if 'remastered' in filename:
        result = result + method[0]
    if "Ionosphere_corrected" in filename:
        result = result + ' - ionosphere corrected'
    if '50' not in filename:
        result = result +  ', signal threshold: 65%'
    if '50' in filename:
        result = result +  ', signal threshold: 50%'
    if 'NSBAS' in filename:
        result = result + ', smoothing factor: ' + str(smoothing)
    result = result + ' ' + ', misfit: ' + str(misfit)
    return result

for i in range(len(filenames)):
	est = estimated_gpsvel(filenames[i][0])
	misfit = ncf.misfit(velfinal, est)
	print(result(filenames[i][0], misfit, filenames[i][1] ))

# z = rwr.read_grd(filenames[-2][0])
# counter = []
# i, j = 0,0
# for x in range(len(xfinal_ratioed)):
# 	pixel_box = z[(yfinal_ratioed[x]-50):(yfinal_ratioed[x]+51),(xfinal_ratioed[x]-50):(xfinal_ratioed[x]+51) ]
# 	print(np.shape(pixel_box))
# 	for v in np.nditer(pixel_box):
# 		if np.isnan(v) == False:
# 			counter.append(v)
# 	print(len(counter))

x1, y1, z1 = rwr.read_grd_xyz('signalspread_please_test.nc')
x2,y2, z2 = rwr.read_grd_xyz(filenames[-2][0])
thing1 = z1[1200:1424, 400:660]
thing2 = z2[1200:1424, 400:660]
rwr.produce_output_netcdf(x1[400:660], y1[1200:1424], thing1, 'signal', 'possible_fault_info.grd')
rwr.flip_if_necessary('possible_fault_info.grd')
rwr.produce_output_plot('possible_fault_info.grd', '', 'possible_fault_info.png', '%')
rwr.produce_output_netcdf(x2[400:660], y2[1200:1424], thing2, 'velocity', 'possible_fault_info_vel.grd')
rwr.flip_if_necessary('possible_fault_info_vel.grd')

[x,y] = np.meshgrid(x1[400:660], y1[1200:1424])
[x_,y_] = np.meshgrid(x2[400:660], y2[1200:1424])

fig = plt.figure(figsize=(18,10));
ax1=plt.subplot(121)
image1 = ax1.contourf(x,y,thing1,cmap='jet', vmin=np.nanmin(thing1), vmax=np.nanmax(thing1));
plt.gca().invert_xaxis()
ax1.set_title("Signal Spread", fontsize=25);
ax1.set_xlabel("Range",fontsize=25);
ax1.set_ylabel("Azimuth",fontsize=25);
cb = plt.colorbar(image1);
cb.set_label('%', size=25);

ax2=plt.subplot(122)
image2 = ax2.contourf(x_, y_, thing2, cmap='jet', vmin=-10, vmax=10);
plt.gca().invert_xaxis()
ax2.set_title("Velocity", fontsize=25);
ax2.set_xlabel("Range",fontsize=25);
ax2.set_ylabel("Azimuth",fontsize=25);
cb = plt.colorbar(image2);
cb.set_label('mm/yr', size=25)

plt.savefig("comparison_plots.png");
plt.close();


# obj1d=np.reshape(thing1,(224*260,1));
# plt.hist(obj1d)
# plt.savefig("signalspread_hist.png")


#
vel_grd = "Stacking/NSBAS/velocity_weighted50NSBAS_reasonable_smoothlowest.grd"
vel_ll = vel_grd.split('.grd')[0]+"_ll.grd"
transdat = "Metadata/trans.dat"
call(["proj_ra2ll.csh",transdat,vel_grd,vel_ll],shell=False)

call("./make_insar_profile.gmt",shell=False)
