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


if __name__=="__main__":
	# grdname="intf_all_remote/2018281_2018305/unwrap.grd"
	# remove_trend2d(grdname,4);
	# remove_trend2d(grdname,3);
	# remove_trend2d(grdname,6);
	outfile = "classic_unwrapped_N4_good.grd"
	rwr.produce_output_plot(outfile, 'Ramp removed', 'Ramp_remove.png', 'phase')



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
