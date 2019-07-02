#!/usr/bin/python
import numpy as np
import glob
import netcdf_read_write as rwr
import readcubedata as rcd

def stack_corr(d, cutoff):
    """This function takes in a cube of data (argument 1) and counts how many times a certain
    piece of data is above a specified cutoff value (argument 2) in each 2-D array stored in the cube.
    It returns a 2-D array of percentages, showing how much certain pieces of data satisfy the given cutoff
    condition. """
    a=np.zeros((len(d.yvalues), len(d.xvalues)))
    i,j = 0,0
    for z in np.nditer(d.zvalues):
        if z >= cutoff:
            a[i,j] = a[i,j] + 1
        j+=1
        if j== len(d.xvalues):
            j=0
            i+=1
            if i == len(d.yvalues):
                i=0
    i,j = 0,0
    for n in np.nditer(a):
        a[i,j] = (a[i,j]/(len(d.filepaths)))*100
        j+=1
        if j== len(d.xvalues):
            j=0
            i+=1
            if i == len(d.yvalues):
                i=0
        return a


if __name__ == "__main__":
    myfiles = glob.glob("intf_all_remote/???????_???????/corr.grd")
    d=rcd.reader(myfiles)
    a=stack_corr(d, 0.1)
    rwr.produce_output_netcdf(d.xvalues, d.yvalues, a, 'Percentage', 'signalspread.nc')
    rwr.flip_if_necessary('signalspread.nc')
    rwr.produce_output_plot('signalspread.nc', 'Signal Spread', 'signalspread.png', 'Percentage of coherence (out of 288 images)' )
