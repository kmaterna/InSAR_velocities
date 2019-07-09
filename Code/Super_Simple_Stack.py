#!/usr/bin/python
import numpy as np
import glob
import netcdf_read_write as rwr
import readmytupledata as rmd
import scipy.io.netcdf as netcdf
import matplotlib.pyplot as plt


def velocity_simple_stack(filepathslist, wavelength, manual_exclude):
    """This function takes in a list of files that contain arrays of phases and times. It
    will compute the velocity of each pixel using the given wavelength of the satellite.
    Finally, it will return a 2D array of velocities, ready to be plotted. For the manual exclude
    argument, enter either 0 (no images excluded), 1 (15 images excluded), or 2 (40 images excluded)."""
    if manual_exclude != 0:
        f = open('Metadata/manual_remove.txt', 'r')
        if manual_exclude == 1:
            content, x = f.readlines()[0:15], []
            for i in range(len(content)):
                x.append(content[i].strip('\n'))
        if manual_exclude == 2:
            content = f.read()
            x = content.split('\n')
        f.close()
        filesmodified = []
        filepathslist = filesmodified
        for i in range(len(myfiles)):
            if myfiles[i][16:31] not in x:
                filesmodified.append(myfiles[i])
    print('Number of files being stacked: ' + str(len(filepathslist)))
    mytuple = rmd.reader(filepathslist)
    phases, times = [], []
    velocities = np.zeros((len(mytuple.yvalues), len(mytuple.xvalues)))
    i,j,f,c = 0,0,0,0
    for z in np.nditer(mytuple.zvalues, order='F'):
        if np.isnan(z) == False:
            phases.append(mytuple.zvalues[f][i][j])
            times.append(mytuple.date_deltas[f])
        if np.isnan(z) == True:
            times.append(np.nan)
        f+=1
        if f == len(mytuple.zvalues):
            velocities[i,j] = (wavelength/(4*(np.pi)))*((np.sum(phases))/(np.sum(times)))
            phases, times = [], []
            c+=1
            print('Done with ' + str(c) + ' out of ' + str(len(mytuple.xvalues)*len(mytuple.yvalues)) + ' pixels')
            f=0
            j+=1
            if j==len(mytuple.xvalues):
                j=0
                i+=1
                if i == len(mytuple.yvalues):
                    i=0
    return velocities, mytuple.xvalues, mytuple.yvalues

if __name__ == "__main__":
    myfiles = glob.glob("intf_all_remote/???????_???????/unwrap_ref.grd")
    velocities, x, y = velocity_simple_stack(myfiles, 56, 1)
    rwr.produce_output_netcdf(x, y, velocities, 'mm/yr', 'velo_prof_reasonable.grd')
    rwr.flip_if_necessary('velo_prof_reasonable.grd')
    rwr.produce_output_plot('velo_prof_reasonable.grd', 'Velocity Profile Reasonable (15 images removed)', 'velo_prof_reasonable.png', 'velocity (mm/yr)')
