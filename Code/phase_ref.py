#!/usr/bin/python
import numpy as np
import glob
import netcdf_read_write as rwr
import readmytupledata as rmd

def phase_ref(mytuple, yvalue, xvalue):
    """This function takes in a 3d array of values, along with the indexes of the pixel that
    the user would like to reference the phases to. It returns a 3d array of referenced pixels."""
    store = mytuple.zvalues
    ref_values = []
    for f in range(len(store)):
        ref_values.append(store[f, yvalue, xvalue])

    print(len(ref_values))

    i,j,f = 0,0,0
    while f < len(mytuple.zvalues):
            store[f, i ,j] = store[f, i ,j] - ref_values[f]
            j+=1
            if j==len(mytuple.xvalues):
                j=0
                i+=1
                if i == len(mytuple.yvalues):
                    i=0
                    print('Referencing phases in file ' + str(f+1) + ' out of ' + str(len(mytuple.zvalues)))
                    f+=1

    return store

if __name__ == "__main__":
    myfiles = glob.glob("intf_all_remote/???????_???????/unwrap.grd")
    d=rmd.reader(myfiles)
    store = phase_ref(d, 621, 32)
    for i in range(len(myfiles)):
        print('Dealing with file ' + str(i+1))
        temp = myfiles[i].split('/')[-1]
        stem = myfiles[i][0:-len(temp)]
        rwr.produce_output_netcdf(d.xvalues, d.yvalues, store[i], 'Radians', stem + 'unwrap_ref.grd')
        rwr.flip_if_necessary(stem + 'unwrap_ref.grd')
        rwr.produce_output_plot(stem + 'unwrap_ref.grd', 'Referenced Unwrapped Phase', stem + 'unwrap_ref.png', 'unwrapped phase')
