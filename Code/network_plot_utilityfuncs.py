#!/usr/bin/python
# Useful utility functions
# For making network plots

import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import netcdf_read_write as rwr
import scipy.io.netcdf as netcdf


def read_baseline_table(baselinefilename):
	# Ex file: baseline_table.dat
    baselineFile = np.genfromtxt(baselinefilename,dtype=str);
    stems = baselineFile[:,0].astype(str);
    times = baselineFile[:,1].astype(float);
    missiondays = baselineFile[:,2].astype(str);
    baselines = baselineFile[:,4].astype(float);
    return [stems, times, baselines, missiondays];


def read_intf_table(tablefilename):
	# ex file: intf_record.in
    tablefile = np.genfromtxt(tablefilename,dtype=str);
    intf_all = tablefile[:].astype(str);
    return intf_all;

def remove_manual_excludes(intf_all, excludefilename, no_of_images):
    f = open(excludefilename, 'r')
    raw, content = f.readlines()[0:no_of_images], []
    for i in range(len(raw)):
        content.append(raw[i].strip('\n'))
    for i in range(len(content)):
        content[i] = content[i].replace(content[i][0:7], str(int(content[i][0:7]) + 1))
        content[i] = content[i].replace(content[i][8:15], str(int(content[i][8:15]) + 1))
        date1, date2 = dt.datetime.strptime(content[i][0:7], '%Y%j').date(), dt.datetime.strptime(content[i][8:15], '%Y%j').date()
        content[i] = 'S1A' + date1.strftime('%Y%m%d') + '_ALL_F1:S1A' + date2.strftime('%Y%m%d') + '_ALL_F1'
    included_intf = []
    for i in range(len(intf_all)):
        if intf_all[i] not in content:
            included_intf.append(intf_all[i])
    return included_intf


def make_network_plot(intf_pairs, stems, tbaseline, xbaseline, plotname):
    print("printing network plot");
    if len(intf_pairs)==0:
        print("Error! Cannot make network plot because there are no interferograms. "); sys.exit(1);
    xstart=[]; xend=[]; tstart=[]; tend=[];

    # If there's a format like "S1A20160817_ALL_F2:S1A20160829_ALL_F2"
    if "S1" in intf_pairs[0]:
        for item in intf_pairs:
            scene1=item[0:18];    # has some format like S1A20160817_ALL_F2
            scene2=item[19:];     # has some format like S1A20160817_ALL_F2
            for x in range(len(stems)):
                if stems[x]==scene1:
                    xstart.append(xbaseline[x]);
                    tstart.append(dt.datetime.strptime(str(int(tbaseline[x])+1),'%Y%j'));
                if stems[x]==scene2:
                    xend.append(xbaseline[x]);
                    tend.append(dt.datetime.strptime(str(int(tbaseline[x])+1),'%Y%j'));


    # # If there's a format like "2017089:2018101"....
    # if len(intf_pairs[0])==15:
    #     dtarray=[]; im1_dt=[]; im2_dt=[];
    #     for i in range(len(times)):
    #         dtarray.append(dt.datetime.strptime(str(times[i])[0:7],'%Y%j'));

    #     # Make the list of datetimes for the images.
    #     for i in range(len(intf_pairs)):
    #         scene1=intf_pairs[i][0:7];
    #         scene2=intf_pairs[i][8:15];
    #         im1_dt.append(dt.datetime.strptime(scene1,'%Y%j'));
    #         im2_dt.append(dt.datetime.strptime(scene2,'%Y%j'));

    #     # Find the appropriate image pairs and baseline pairs
    #     for i in range(len(intf_pairs)):
    #         for x in range(len(dtarray)):
    #             if dtarray[x] == im1_dt[i]:
    #                 xstart.append(baselines[x]);
    #                 tstart.append(dtarray[x]);
    #             if dtarray[x] == im2_dt[i]:
    #                 xend.append(baselines[x]);
    #                 tend.append(dtarray[x]);


    plt.figure();
    plt.plot_date(tstart,xstart,'.b');
    plt.plot_date(tend,xend,'.b');
    for i in range(len(tstart)):
        plt.plot_date([tstart[i],tend[i]],[xstart[i],xend[i]],'b');
    yrs_formatter=mdates.DateFormatter('%m-%y');
    plt.xlabel("Date");
    plt.gca().xaxis.set_major_formatter(yrs_formatter);
    plt.ylabel("Baseline (m)");
    plt.title("Network Geometry - Inclusive");
    plt.savefig(plotname);
    plt.close();
    print("finished printing network plot");
    return;



#
# table = read_baseline_table('Metadata/baseline_table.dat')
# intf = read_intf_table('Metadata/intf_record.in')
# included_intf = remove_manual_excludes(intf, 'Metadata/manual_remove.txt', 0 );
# print(len(included_intf))
#
# make_network_plot(included_intf, table[0], table[1], table[2], 'Network Geometry - 0 images removed')
