#!/usr/bin/python
# Little function that removes trend from unwrapped grd file (give it the order of coefficients in the plane)
# and makes KML files. Yay!

from subprocess import call
import numpy as np
import matplotlib.pyplot as plt
import glob
import scipy.io.netcdf as netcdf
import readmytupledata as rmd
import netcdf_read_write as rwr
import math
import datetime as dt
import sys
import phase_ref as phr

def remove_trend2d(grdname, order):
    # Python Version.

    order=str(order)
    call(["gmt","grd2xyz",grdname,"-s",">","unwrap_mask.xyz"]);  # make xyz file with no NaNs in it.

    # Trend fitting: Get the residuals and the planar model
    call(["gmt","trend2d","unwrap_mask.xyz","-Fxyr","-N"+order,"-V",">","detrended_unwrapped.xyz"])
    call(["gmt","trend2d","unwrap_mask.xyz","-Fxym","-N"+order,"-V",">","planar_model_N"+order+".xyz"])

    # Convert to grd output files for plotting
    call(["gmt xyz2grd planar_model_N"+order+".xyz -Gplanar_model_N"+order+".grd `gmt grdinfo -I "+grdname+"` `gmt grdinfo -I- "+grdname+"`"],shell=True);
    call(["gmt xyz2grd detrended_unwrapped.xyz -Gdetrended_unwrapped_N"+order+".grd `gmt grdinfo -I "+grdname+"` `gmt grdinfo -I- "+grdname+"`"],shell=True);

    # kml plotting with a certain color bar. (Uses GMTSAR functions)
    # call(["gmt","makecpt","-T-2.5/2.5/0.1","-Z","-Cpolar",">","mycpt.cpt"]);
    # call(["grd2kml.csh","detrended_unwrapped_N"+order,"mycpt.cpt"])
    # call(["grd2kml.csh","planar_model_N"+order,"mycpt.cpt"])

def plane_fitter(filename , outfile):
    """This function fits the inputted data (filename) to the model: z = A + Bx + Cy. It saves the model in
    outfile. It plots a comparison of the data and the model, and also returns the model parameters A, B and C."""
    xvalues, yvalues, zvalues = rwr.read_grd_xyz(filename)
    i,j = 0,0
    d,x,y = [], [], []
    for z in np.nditer(zvalues):
        if np.isnan(z) == False:
            d.append(zvalues[i,j])
            x.append(xvalues[j])
            y.append(yvalues[i])
        j+=1
        if j==len(xvalues):
            j=0
            i+=1
            if i == len(yvalues):
                i=0
    temp = np.ones(len(d))
    G = np.column_stack((temp,x,y))
    GTG = np.dot(np.transpose(G), G)
    GTd = np.dot(np.transpose(G), d)
    soln = np.dot(np.linalg.inv(GTG), GTd)
    i,j = 0,0
    model_z = np.zeros((len(yvalues), len(xvalues)))
    for z in np.nditer(zvalues):
        model_z[i,j] = soln[0] + soln[1]*xvalues[j] + soln[2]*yvalues[i]
        j+=1
        if j==len(xvalues):
            j=0
            i+=1
            if i == len(yvalues):
                i=0
    rwr.produce_output_netcdf(xvalues, yvalues, model_z, 'unwrapped phase', outfile)
    rwr.flip_if_necessary(outfile)
    outfile1 = outfile.replace("model.grd", "model_comparison.png")
    fr = netcdf.netcdf_file(outfile,'r');
    xread=fr.variables['x'];
    yread=fr.variables['y'];
    zread=fr.variables['z'];
    zread_copy=zread[:][:].copy();

    fr2 = netcdf.netcdf_file(filename,'r');
    xread2=fr2.variables['x'];
    yread2=fr2.variables['y'];
    zread2=fr2.variables['z'];
    zread2_copy=zread2[:][:].copy();

    fig = plt.figure(figsize=(7,10))
    ax1 = plt.subplot(121)
    old = ax1.imshow(zread2_copy,aspect=1.2);
    ax1.invert_xaxis()
    ax1.get_xaxis().set_ticks([]);
    ax1.get_yaxis().set_ticks([]);
    ax1.set_xlabel("Range",fontsize=16);
    ax1.set_ylabel("Azimuth",fontsize=16);

    ax2 = plt.subplot(122)
    new = ax2.imshow(zread_copy,aspect=1.2, vmin=np.nanmin(zread_copy), vmax=np.nanmax(zread2_copy));
    ax2.invert_xaxis()
    ax2.get_xaxis().set_ticks([]);
    ax2.get_yaxis().set_ticks([]);
    ax2.set_xlabel("Range",fontsize=16);
    cb = plt.colorbar(new)
    cb.set_label('unwrapped phase', size=16);

    plt.savefig(outfile1);
    plt.close();

    return soln[0], soln[1], soln[2]

def remove_plane(filename, planefile, outfile, m1 , m2 , m3):
    xvalues, yvalues, zvalues = rwr.read_grd_xyz(filename)
    i,j = 0,0
    new_z = np.zeros((len(yvalues), len(xvalues)))
    for z in np.nditer(zvalues):
        new_z[i,j] = zvalues[i,j] - (m1 + m2*xvalues[j] + m3*yvalues[i])
        j+=1
        if j==len(xvalues):
            j=0
            i+=1
            if i == len(yvalues):
                i=0
    print(new_z[0,0])
    new_z = np.flipud(new_z)
    print(new_z[0,0])
    rwr.produce_output_netcdf(xvalues, yvalues, np.flipud(new_z), 'unwrapped phase', outfile)
    rwr.flip_if_necessary(outfile)
    outfile1 = outfile.replace("no_ramp.grd", "no_ramp_comparison.png")

    fr = netcdf.netcdf_file(outfile,'r');
    xread=fr.variables['x'];
    yread=fr.variables['y'];
    zread=fr.variables['z'];
    zread_copy=zread[:][:].copy();

    fr2 = netcdf.netcdf_file(filename,'r');
    xread2=fr2.variables['x'];
    yread2=fr2.variables['y'];
    zread2=fr2.variables['z'];
    zread2_copy=zread2[:][:].copy();

    fig = plt.figure(figsize=(7,10))
    ax1 = plt.subplot(121)
    old = ax1.imshow(zread2_copy,aspect=1.2);
    ax1.invert_xaxis()
    ax1.get_xaxis().set_ticks([]);
    ax1.get_yaxis().set_ticks([]);
    ax1.set_xlabel("Range",fontsize=16);
    ax1.set_ylabel("Azimuth",fontsize=16);

    ax2 = plt.subplot(122)
    new = ax2.imshow(zread_copy,aspect=1.2, vmin=np.nanmin(zread_copy), vmax=np.nanmax(zread2_copy));
    ax2.invert_xaxis()
    ax2.get_xaxis().set_ticks([]);
    ax2.get_yaxis().set_ticks([]);
    ax2.set_xlabel("Range",fontsize=16);
    cb = plt.colorbar(new)
    cb.set_label('unwrapped phase', size=16);

    plt.savefig(outfile1);
    plt.close();

    rwr.produce_output_plot(outfile, 'Ramp removed', outfile.replace('grd', 'png'), 'unwraped phase')

    return


if __name__ == "__main__":
    f = open("Metadata/Ramp_need_fix.txt", 'r')
    raw, content = f.readlines(), []
    for i in range(len(raw)):
        content.append(raw[i].strip('\n'))
    model, content_1 = [], []
    for i in range(len(content)):
        content_1.append('intf_all_remote/' + content[i] + '/unwrap.grd')
        m1,m2,m3 = plane_fitter(content_1[i], content_1[i].replace('unwrap', 'unwrap_model'))
        model.append(content_1[i].replace('unwrap', 'unwrap_model'))
        remove_plane(content_1[i], model[i], model[i].replace('model', 'no_ramp'), m1, m2, m3)
        temp1 = ['intf_all_remote/' + content[i] + '/unwrap_no_ramp.grd']
        d=rmd.reader(temp1)
        store = phr.phase_ref(d, 621, 32)
        temp = temp1[0].split('/')[-1]
        stem = temp1[0][0:-len(temp)]
        rwr.produce_output_netcdf(d.xvalues, d.yvalues, store[0], 'Radians', stem + 'unwrap_ref_corrected.grd')
        rwr.flip_if_necessary(stem + 'unwrap_ref_corrected.grd')
        rwr.produce_output_plot(stem + 'unwrap_ref_corrected.grd', 'Referenced and Corrected Unwrapped Phase', stem + 'unwrap_ref_corrected.png', 'unwrapped phase')
        print('Done with file ' + str(i+1))



# if __name__=="__main__":
	# grdname="intf_all_remote/2018281_2018305/unwrap.grd"
	# remove_trend2d(grdname,4);
	# remove_trend2d(grdname,3);
	# remove_trend2d(grdname,6);
	# outfile = "classic_unwrapped_N4_good.grd"
	# rwr.produce_output_plot(outfile, 'Ramp removed', 'Ramp_remove.png', 'phase')



# # BASH Version
# # Define name and number of coefficients in planar fit.
# grdname="unwrap.grd";
# order="4"

# # Remove NaNs
# gmt grd2xyz $grdname -s > unwrap_mask.xyz

# # Get residuals and model for planar fit.  Put into GRD files.
# gmt trend2d unwrap_mask.xyz -Fxyr -N$order -V > detrended_unwrapped.xyz
# gmt trend2d unwrap_mask.xyz -Fxym -N$order -V > planar_model_N$order.xyz
# gmt xyz2grd planar_model_N$order.xyz -Gplanar_model_N$order.grd `gmt grdinfo -I $grdname` `gmt grdinfo -I- $grdname+`
# gmt xyz2grd detrended_unwrapped.xyz -Gdetrended_unwrapped_N$order.grd `gmt grdinfo -I $grdname` `gmt grdinfo -I- $grdname+`
