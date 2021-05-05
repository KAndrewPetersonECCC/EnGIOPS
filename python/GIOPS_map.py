

# Inputs:

# var   : Variable to map (needs to be 3D or 1x2D)
# label : Colorbar label
# ticks : Colorbar Ticks; Including maximum and minimum of map to be set
# hour  : dimension 0 tuple of the array. Can correspond to z or time axis.
# cmap  : colormap
# contmask : mask of the continent, should be the same dims as var.
# lon, lat : 2D, should be of dims 1,2 of var

import numpy as np
import matplotlib.pyplot as plt
from math import log10, floor
import matplotlib.colors as colors
from matplotlib.ticker import LogFormatter 



def round_to_1(x):
   return round(x, -int(floor(log10(abs(x)))))

def map(var,label,ticks,hour,cmap,contmask,lon,lat):

    # create a mask where the steep gradient between 180 and -180 is masked.
    A = lon-np.roll(lon,5)
    lons1 = lon.copy(); lons2 = lon.copy()
    lons1[np.where(A<0)] = np.nan
    lons2[np.where(A>=0)] = np.nan
    lons2-= 0.5
    lat[lat<=-65.0]=np.nan
    lons1[:5,:]=np.nan
    vmin = ticks[0];vmax = ticks[-1]
    TEMP = var.copy()
    TEMP[var>vmax]=vmax; TEMP[var<vmin]=vmin
    # if var is 2d, make 3d
    if len(TEMP.shape) == 2: TEMP = TEMP[np.newaxis,...];var=var[np.newaxis,...]
    if len(contmask.shape) == 2: contmask = contmask[np.newaxis,...]
    TEMP[:,:3]=np.nan

    #plt.contourf(np.arange(TEMP.shape[1]),np.arange(TEMP.shape[0]),TEMP[dep_tup],100,cmap =cmap,vmin = vmin, vmax = vmax)
    #cbaxes = fig.add_axes([0.8, 0.1, 0.03, 0.8])
    plt.pcolor(TEMP[hour],vmin = vmin,vmax = vmax,cmap = cmap)
    cb = plt.colorbar(orientation='horizontal',ticks = ticks,extend = 'both',label = label)#,cax = cbaxes)
    cb.set_label(label=label, size='large')

    #if varname == 'Temperature':cb.ax.set_title(r'($^{\circ}$C)')
    #elif varname == 'Salinity':cb.ax.set_title(r'(psu)')
    plt.contour(contmask[hour],[0],colors = 'k',linewidths = 0.5)
    CS1 = plt.contour(lons1,[-120,-60,0,60,120,180], colors = 'k', linewidths = 0.4)
    CS2 = plt.contour(lons2,[-180], colors = 'k', linewidths = 0.4)
    CS = plt.contour(lat,[-60,-40,-20,0,20,40,60,80],colors = 'k', linewidths= 0.4, linestyles = ':')

    #CS2W = plt.contour(lons2,[-180,-120], colors = 'k', linewidths = 0.4)

    fmt1 = {};fmt2 = {};fmt3={}
    strs1 = [r'120$^{\circ}$W',r'60$^{\circ}$W',r'$0^{\circ}$E',r'$60^{\circ}$E',r'$120^{\circ}$E',r'$180^{\circ}$E']
    strs2 = [r'180$^{\circ}$',r'120$^{\circ}$W',r'120$^{\circ}$E']
    strs3 = [r'60$^{\circ}$S',r'40$^{\circ}$S',r'20$^{\circ}$S',r'0$^{\circ}$',r'20$^{\circ}$N',r'40$^{\circ}$N',r'60$^{\circ}$N',r'80$^{\circ}$N']
    for l, s in zip(CS1.levels, strs1):
        fmt1[l] = s
    for l, s in zip(CS2.levels, strs2):
        fmt2[l] = s
    for l, s in zip(CS.levels, strs3):
        fmt3[l] = s

    plt.clabel(CS1,CS1.levels,fmt=fmt1,fontsize = 'small')#,manual = [(400,70),(1100,70),(1500,1100),(0,0)])
    #plt.clabel(CS2,CS2.levels,fmt=fmt2,size = 6,manual = [(750,2000),(100,1500),(1300,1650)])
    plt.clabel(CS,CS.levels,fmt=fmt3,fontsize='small')
    plt.xlabel('i',size = 12);plt.ylabel('j',size = 12)
    plt.xticks(size = 8)
    plt.yticks(size = 8)
    
    
    if (np.nanmin(var[hour])) !=0 and (abs(np.nanmin(var[hour])<0.1)):
       plt.text(10, 310, 'Min= '+str(round_to_1(np.nanmin(var[hour]))), size=8)
    else: plt.text(10, 310, 'Min= '+str(np.round(np.nanmin(var[hour]),1)), size=8)
    if np.nanmax(var[hour]) !=0 and (abs(np.nanmax(var[hour])<0.1)):
        plt.text(10, 300, 'Max= '+str(round_to_1(np.nanmax(var[hour]))), size=8)
    else: plt.text(10, 300, 'Max= '+str(np.round(np.nanmax(var[hour]),1)), size=8)
    if np.nanmean(var[hour]) !=0 and (abs(np.nanmean(var[hour])<0.1)):
        plt.text(10, 290, 'Mean= '+str(round_to_1(np.nanmean(var[hour]))), size=8)
    else: plt.text(10, 290, 'Mean= '+str(np.round(np.nanmean(var[hour]),1)), size=8)


# Note; vmin cannot be smaller than 1
def map_log(var,label,ticks,hour,cmap,contmask,lon,lat,fig,ax):
    # create a mask where the steep gradient between 180 and -180 is masked.
    A = lon-np.roll(lon,5)
    lons1 = lon.copy(); lons2 = lon.copy()
    lons1[np.where(A<0)] = np.nan
    lons2[np.where(A>=0)] = np.nan
    lons2-= 0.5

    vmin = ticks[0];vmax = ticks[-1]
    TEMP = var.copy()
    #TEMP[var>vmax]=vmax; TEMP[var<vmin]=vmin
    # if var is 2d, make 3d
    if len(TEMP.shape) == 2: TEMP = TEMP[np.newaxis,...];var=var[np.newaxis,...]
    if len(contmask.shape) == 2: contmask = contmask[np.newaxis,...]

    TEMP[:,:3]=np.nan
    #plt.contourf(TEMP[dep_tup],100,cmap =cmap,vmin = vmin, vmax = vmax)
    #cbaxes = fig.add_axes([0.8, 0.1, 0.03, 0.8])
    plt.pcolor(TEMP[hour],norm=colors.LogNorm(vmin=vmin,vmax=vmax),cmap = cmap)
    formatter = LogFormatter(10, labelOnlyBase=False)
    cb = plt.colorbar(orientation='horizontal',ticks = ticks,format=formatter,extend = 'both',label = label)#,cax = cbaxes)
    cb.set_label(label=label, size='large')
    
    cb.ax.set_xticklabels(ticks)
    
    #if varname == 'Temperature':cb.ax.set_title(r'($^{\circ}$C)')
    #elif varname == 'Salinity':cb.ax.set_title(r'(psu)')
    plt.contour(contmask[hour],[0],colors = 'k',linewidths = 0.5)
    CS1 = plt.contour(lons1,[-120,-60,0,60,120,180], colors = 'k', linewidths = 0.4)
    CS2 = plt.contour(lons2,[-180], colors = 'k', linewidths = 0.4)
    CS = plt.contour(lat,[-60,-40,-20,0,20,40,60,80],colors = 'k', linewidths= 0.4, linestyles = ':')

    fmt1 = {};fmt2 = {};fmt3={}
    strs1 = [r'120$^{\circ}$W',r'60$^{\circ}$W',r'$0^{\circ}$E',r'$60^{\circ}$E',r'$120^{\circ}$E',r'$180^{\circ}$E']
    strs2 = [r'180$^{\circ}$',r'120$^{\circ}$W',r'120$^{\circ}$E']
    strs3 = [r'60$^{\circ}$S',r'40$^{\circ}$S',r'20$^{\circ}$S',r'0$^{\circ}$',r'20$^{\circ}$N',r'40$^{\circ}$N',r'60$^{\circ}$N',r'80$^{\circ}$N']
    for l, s in zip(CS1.levels, strs1):
        fmt1[l] = s
    for l, s in zip(CS2.levels, strs2):
        fmt2[l] = s
    for l, s in zip(CS.levels, strs3):
        fmt3[l] = s

    plt.clabel(CS1,CS1.levels,fmt=fmt1,fontsize = 'small')
    plt.clabel(CS,CS.levels,fmt=fmt3,fontsize='small')

    plt.xlabel('i',size = 12);plt.ylabel('j',size = 12)
    
    # change ticks
    """
    fig.canvas.draw()
    a = [item for item in ax.get_xticklabels()]
    b = [item for item in ax.get_yticklabels()]
    
    ilabel = [(int(item.get_text())-1)*3-1 for item in a[:-1]]
    jlabel = [(int(item.get_text())-1)*3-1 for item in b[:-1]]
    
    istrlabel = [str(item) for item in ilabel]
    istrlabel[0] = '0'
    jstrlabel = [str(item) for item in jlabel]
    jstrlabel[0] = '0'
    
    #ax.set_xtickslabels(ilabel)
    plt.xticks(np.arange(0,501,100),istrlabel,size = 8)
    plt.yticks(np.arange(0,701,100),jstrlabel,size = 8)
    """

    plt.xticks(size = 8)
    plt.yticks(size = 8)

    if (np.nanmin(var[hour])) !=0 and (abs(np.nanmin(var[hour])<0.1)):
       plt.text(10, 310, 'Min= '+str(round_to_1(np.nanmin(var[hour]))), size=8)
    else: plt.text(10, 310, 'Min= '+str(np.round(np.nanmin(var[hour]),1)), size=8)
    if np.nanmax(var[hour]) !=0 and (abs(np.nanmax(var[hour])<0.1)):
        plt.text(10, 300, 'Max= '+str(round_to_1(np.nanmax(var[hour]))), size=8)
    else: plt.text(10, 300, 'Max= '+str(np.round(np.nanmax(var[hour]),1)), size=8)
    if np.nanmean(var[hour]) !=0 and (abs(np.nanmean(var[hour])<0.1)):
        plt.text(10, 290, 'Mean= '+str(round_to_1(np.nanmean(var[hour]))), size=8)
    else: plt.text(10, 290, 'Mean= '+str(np.round(np.nanmean(var[hour]),1)), size=8)

