#!/usr/bin/python
import numpy as np
import glob
import netcdf_read_write as rwr
import readmytupledata as rmd
import scipy.io.netcdf as netcdf
import matplotlib.pyplot as plt
import sys
import Super_Simple_Stack as sss


date = "2018101_2018137"
date = "2018149_2018161"
corr = "intf_all_remote/" + date + "/corr.grd"
unwrap_ref = "intf_all_remote/" + date + "/unwrap_ref.grd"
unwrap_ref_corrected = "intf_all_remote/" + date + "/unwrap_ref_corrected.grd"
# unwrap_ref_corrected = unwrap_ref
# signalspread_old = "Stacking/signalspread.nc"
# signalspread_please = "Stacking/signalspread_please.nc"
signalspread_please_final = "signalspread_please_test.nc"
version = "final"

# xo, yo, so = rwr.read_grd_xyz(signalspread_old)
# xp, yp, sp = rwr.read_grd_xyz(signalspread_please)
xpf, ypf, spf = rwr.read_grd_xyz(signalspread_please_final)

# ranger = 1039.01664145
# azimuth = 7225.63016393
ranger = xpf[32]
azimuth = ypf[621]
print(spf[1524-621, 32])


#
# xold, xplease, xpleasefinal = [], [], []
# for i in range(len(xo)):
#     if xo[i] == ranger:
#         print("Range value in old signal spread corresponds to index of: " + str(i) )
#         xold.append(i)
#     if xp[i] == ranger:
#         print("Range value in new signal spread corresponds to index of: " + str(i) )
#         xplease.append(i)
#     if xpf[i] == ranger:
#         print("Range value in new final signal spread corresponds to index of: " + str(i) )
#         xpleasefinal.append(i)
#
#
# for i in range(len(yo)):
#     if yo[i] == azimuth:
#         print("Azimuth value in old signal spread corresponds to index of: " + str(i) )
#         yl = i
#         print("Old Signal value of: " + str(so[yl, xold[0]]))
#     if yp[i] == azimuth:
#         print("Azimuth value in new signal spread corresponds to index of: " + str(i) )
#         ypl = i
#         print("New Signal value of: " + str(sp[ypl, xplease[0]]))
#     if ypf[i] == azimuth:
#         print("Azimuth value in new final signal spread corresponds to index of: " + str(i) )
#         ypfl = i
#         print("New final signal value of: " + str(spf[ypfl, xpleasefinal[0]]))

# print("New signal: " + str(sn[621, 32]))
# print("Old signal: " + str(so[621, 32]))
#
# xratio, yratio = (21116.0151286-15.984871407)/661 , 7.9973770491803275
# r1, r2 = 4600, 12000
# a1, a2 = 8900, 11800
# x1, x2 = round(r1/xratio), round(r2/xratio)
# y1, y2 = round(a1/yratio), round(a2/yratio)
#
#
# xcorr, ycorr, corr_data = rwr.read_grd_xyz(corr)
# xraw, yraw, unwrap_ref_data = rwr.read_grd_xyz(unwrap_ref_corrected)
#
# # print(corr + ': '  + str(np.nanmean(corr_data[1113:1475, 144:376])) + ' , x: ' + str(xcorr[258]) + ' , \ny: ' + str(ycorr[1200]) )
# # print(unwrap_ref + ': '  + str(np.nanmean(unwrap_ref_data[1113:1475, 144:376])) + ' , x: ' + str(xraw[32]) + ' , \ny: ' + str(yraw[621])  )
# # print(unwrap_ref_data[621,32])
#
# print('unwrap ref corrected:')
# print(unwrap_ref_data[621, 32])
# print(xraw[32])
# print(yraw[621])
#
# print("signal spread:")
# print(sn[621,32])
# print(x[32])
# print(y[621])

# # first plot

xread, yread, zread_copy = rwr.read_grd_xyz(corr)
[X,Y] = np.meshgrid(xread, yread)
#

xread2, yread2, zread_copy2 = rwr.read_grd_xyz(unwrap_ref)
[X2,Y2] = np.meshgrid(xread2, yread2)
#
xread3, yread3, zread_copy3 = rwr.read_grd_xyz(unwrap_ref_corrected)
[X3,Y3] = np.meshgrid(xread3, yread3)

xread4, yread4, zread_copy4 = rwr.read_grd_xyz(signalspread_please_final)
[X4,Y4] = np.meshgrid(xread4, yread4)
#
#
# # Make a plot
fig = plt.figure(figsize=(18,18));
fig.suptitle("2018149_2018161", fontsize=35)
ax1=plt.subplot(221)
image1 = ax1.contourf(X,Y,zread_copy,cmap='jet', vmin=np.nanmin(zread_copy), vmax=np.nanmax(zread_copy));
plt.gca().invert_xaxis()
ax1.set_title("Correlation", fontsize=25);
ax1.set_xlabel("Range",fontsize=25);
ax1.set_ylabel("Azimuth",fontsize=25);
plt.gca().plot(xread[32], yread[621], 'ko')
print("inside first plot")
print(xread[32])
print(yread[621])
print(zread_copy[621, 32])
cb = plt.colorbar(image1);
cb.set_label('correlation', size=25);

ax2=plt.subplot(222)
image2 = ax2.contourf(X2, Y2, zread_copy2, cmap='jet', vmin=np.nanmin(zread_copy2), vmax=np.nanmax(zread_copy2));
plt.gca().invert_xaxis()
ax2.set_title("Referenced Unwrapped Phase", fontsize=25);
ax2.set_xlabel("Range",fontsize=25);
ax2.set_ylabel("Azimuth",fontsize=25);
plt.gca().plot(xread2[32], yread2[621], 'ko')
print("inside second plot")
print(xread2[32])
print(yread2[621])
print(zread_copy2[621, 32])
cb = plt.colorbar(image2);
cb.set_label('radians', size=25);

ax3=plt.subplot(223)
image3 = ax3.contourf(X3, Y3, zread_copy3, cmap='jet', vmin=np.nanmin(zread_copy3), vmax=np.nanmax(zread_copy3));
plt.gca().invert_xaxis()
ax3.set_title("Referenced Unwrapped Phase - ramps removed", fontsize=25);
ax3.set_xlabel("Range",fontsize=25);
ax3.set_ylabel("Azimuth",fontsize=25);
print("inside third plot")
print(xread3[32])
print(yread3[621])
print(zread_copy3[621,32])
plt.gca().plot(xread3[32], yread3[621], 'ko')
cb = plt.colorbar(image3);
cb.set_label('radians', size=25);

ax4=plt.subplot(224)
image4 = ax4.contourf(X4, Y4, zread_copy4, cmap='jet', vmin=np.nanmin(zread_copy4), vmax=np.nanmax(zread_copy4));
plt.gca().invert_xaxis()
ax4.set_title("Signal Spread ", fontsize=25);
ax4.set_xlabel("Range",fontsize=25);
ax4.set_ylabel("Azimuth",fontsize=25);
print("inside fourth plot")
print(xread4[32])
print(yread4[621])
print(zread_copy4[621, 32])
plt.gca().plot(xread4[32], yread4[621], 'ko')
cb = plt.colorbar(image4);
cb.set_label('percentage', size=25);

plt.savefig("test2.png");
plt.close();

# # ramps, outfile_stem, myfiles, myfiles_no_ramp, remove_ramp = sss.configure()
# # files = sss.inputs(ramps, myfiles, myfiles_no_ramp, remove_ramp)
# # print(len(files))
# # mytuple = rmd.reader(files)
# # for i in range(len(mytuple.zvalues)):
# #     print(mytuple.zvalues[i][621,32])
#
# print(xread[32].copy(), xread2[32].copy(), xread3[32].copy(), xread4[32].copy())
# print(yread[621].copy(), yread2[621].copy(), yread3[621].copy(), yread4[621].copy())
