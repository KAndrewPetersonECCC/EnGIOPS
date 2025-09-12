#from importlib import reload
import sys
sys.path.insert(0, '/home/dpe000/EnGIOPS/python')
import xarray as xr
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.colors as clr
import matplotlib.dates as mdates
from matplotlib.lines import Line2D

#import read_DF_VP
from make_regions import PAREAS
import read_qcola
import inside_polygon
import cplot

region1 = [[-180,  45], [-120,  45], [-120, 65], [-180, 65], [-180, 45]]
region2 = [[ 120, -20], [ 330, -20], [ 330, 20], [ 120, 20], [ 120, -20]]
region3 = [[-180, -50], [-100, -50], [-100,-20], [-180,-20], [-100, -50]]
area_extra = ['NW Pacific', 'Tropical Pacific', 'SW Pacific']

def longitude_to_360(longitude):
    return longitude%360
    
def longitude_to_pm180(longitude):
    longitude = longitude_to_360(longitude)
    iwest = np.where(longitude > 180.0)
    longitude[iwest ] = longitude[iwest] - 360.0
    return longitude
 
def check_polygon_longitudes(polygon):
    longitudes = np.array([ latlon[0] for latlon in polygon ])
    center_prime = True
    print(longitudes)
    print(type(longitudes))
    print(type(np.max(longitudes)))
    if ( np.max(longitudes) > 180 ): center_prime=False
    if ( np.min(longitudes) < 0): center_prime=True
    return center_prime
    
def test_points_are_inside(longitude, latitude, polygon=None):

    if ( isinstance(polygon, type(None) ) ): polygon='global'

    if ( polygon == 'global' ):
        points_are_inside = np.where(~np.isnan(longitude))
    else:    
        if ( isinstance(polygon, str) ): polygon=PAREAS[polygon]    
        points_are_inside = inside_polygon.test_inside_xyarray(polygon, longitude, latitude )[0]

    return points_are_inside    
    

def take_mean(VP, variable, points_are_inside, do_rmse=False):
    if ( isinstance(variable, list) ):
        mean = []
        for var in variable:
            mna = take_mean(VP, var, points_are_inside, do_rmse=do_rmse)
            mean.append(mna)
        return mean
        
    if do_rmse:
        mean = np.sqrt(np.square(VP[variable][points_are_inside].mean(axis=0))).compute().values
    else:
        mean = VP[variable][points_are_inside].mean(axis=0).compute().values
        
    return mean
    
def take_means(VP, points_are_inside):
    vars = ['mis_temperature', 'mis_salinity']
    mean = take_mean(VP, vars, points_are_inside)
    rmse = take_mean(VP, vars, points_are_inside, do_rmse=True)
    return [ [mean[0], rmse[0]], [mean[1], rmse[1]] ]

def take_area_means(VP, polygons=['global']+list(PAREAS.keys())+[region1, region2]):
    area_means = []
    longitude = VP['longitude'].values
    latitude = VP['latitude'].values
    for region in polygons:
        longitude_to_pass = longitude.copy()
        if ( not isinstance(region, str) ):
            center_prime = check_polygon_longitudes(region)
            if ( not center_prime ): longitude_to_pass = longitude_to_360(longitude)
        points_are_inside = test_points_are_inside(longitude_to_pass, latitude, polygon=region)
        means = take_means(VP, points_are_inside)
        area_means.append(means)
    return area_means
    
Levels = [  [0, 200.0], [0, 500.0], [200.0, 500.0], [500.0, 2000.0], [0, 50.0], [0, 10.0], [0, 5.0] ]

def bin_fields(XR, variable, ddeg=2.0, is_3d=True, depth_dim='levels', depth_name='dep_temperature'):
    if ( 'mis' in variable ):
        cntvable=variable.replace('mis','cnt')
        rmsvable=variable.replace('mis','rms')
    else:
        cntvable = 'cnt_'+variable
        rmsvable = 'sqr_'+variable
    lon = XR['longitude'].values
    lat = XR['latitude'].values
    dep = XR[depth_name].mean(axis=0).values
    isz = list(range(1))
    if ( is_3d ): izs = XR[depth_dim].values
    
    binned_levels=[]
    binned_square=[]
    binned_counts=[]
    NPA = XR[variable].values
    grid_lon, grid_lat, lon_bin, lat_bin, grid_sum, grid_cnt = cplot.make_bin_grid(ddeg=ddeg, central_longitude=0)
    for iz in izs:
       if ( is_3d ): 
           NPZ = NPA[:,iz]
       else:
           NPZ = NPA.copy()
       issea = np.where(np.isfinite(NPZ))
       NPS = NPZ[issea]
       lon_sea = lon[issea]
       lat_sea = lat[issea]
       if ( len(issea[0]) != 0 ):
           __, __, grid_sum = cplot.binfld(lon_sea, lat_sea, NPS, ddeg=ddeg,central_longitude=0, statistic='sum')
           __, __, grid_sqr = cplot.binfld(lon_sea, lat_sea, np.square(NPS), ddeg=ddeg,central_longitude=0, statistic='sum')
           __, __, grid_cnt  = cplot.binfld(lon_sea, lat_sea, NPS, ddeg=ddeg,central_longitude=0, statistic='count')
       else:
           grid_sum = np.zeros(grid_lon.shape)
           grid_sqr = np.zeros(grid_lon.shape)
           grid_cnt = np.zeros(grid_lon.shape)
       binned_levels.append(grid_sum)
       binned_square.append(grid_sum)
       binned_counts.append(grid_cnt)
        
    bin3d = np.squeeze(np.array(binned_levels))
    bsn3d = np.squeeze(np.array(binned_square))
    bnn3d = np.squeeze(np.array(binned_counts))

    if ( is_3d ):    
        bin_xr = xr.Dataset(
            coords=dict(
                longitude=(("nx", "ny"), grid_lon),
                latitude =(("nx", "ny"), grid_lat),
                depth   =("levels", dep)
            )
        )
    else:
        bin_xr = xr.Dataset(
            coords=dict(
                longitude=(("nx", "ny"), grid_lon),
                latitude =(("nx", "ny"), grid_lat),
            )
        )
    bin_xr[variable] = ("levels", "nx", "ny"), bin3d
    bin_xr[rmsvable] = ("levels", "nx", "ny"), bsn3d
    bin_xr[cntvable] = ("levels", "nx", "ny"), bnn3d.astype(int)
    return bin_xr

def subset_to_level_and_mean(bXR, depth_range=[200.0, 500.0], depname='depth', var_names=['mis_temperature', 'rms_temperature'], cnt_name='cnt_temperature'):
    depth_min = depth_range[0]
    depth_max = depth_range[1]
    belowminD = bXR[depname] >= depth_min
    if ( depth_max == -1 ):
        abovemaxD = bXR.levels
    else:
        abovemaxD = bXR[depname] <  depth_max
    bXR_subset = bXR.loc[dict(levels= (belowminD & abovemaxD) )]
    bXR_level = bXR_subset.sum(dim='levels')
    bXR_means = bXR_level.copy()
    for var_name in var_names:
        bXR_means[var_name] = bXR_level[var_name] / bXR_level[cnt_name]
    return bXR_means

def mean_over_levels(bXR, Levels_here=Levels, depname='depth', var_names=['mis_temperature', 'rms_temperature'], cnt_name='cnt_temperature'):
    bXR_list = []
    for depth_range in Levels_here:
        bXR_mean = subset_to_level_and_mean(bXR, depth_range=depth_range, depname=depname, var_names=var_names, cnt_name=cnt_name)   
        bXR_list.append(bXR_mean)
    bXR_levs = xr.concat(bXR_list, 'levels')
    bXR_levs['depths'] = (('levels', 'bounds'), Levels_here)

    return bXR_levs

     

def plot_profile_multi( means, labels, depth, fld='T', maxdepths=[200, 2000], outpre='PLOTS/Ex', lines=['mean', 'rmse'], linel = [ '--', '-']):
    flabel = 'Temperature (\N{degree sign}C)'
    if ( fld=='S'): flabel = 'Salinity (PSU)'
    nexpts = len(means)
    title = fld+'-profile'
    dvar = 'depth_'+fld
    if ( ( not isinstance(maxdepths, list) ) and ( not isinstance(maxdepths, tuple) ) ): maxdepths=[maxdepths]
    
    figL, axeL = plt.subplots()
    axeL.axvline(x=0, color='k', linestyle='-')
    figD=[]; axeD=[]
    for maxdepth in maxdepths:
        fig, axe = plt.subplots()
        axe.axvline(x=0, color='k', linestyle='-')
        figD.append(fig); axeD.append(axe)

    colors = ['r', 'b', 'g', 'c', 'm']    

    line_elementsL = []
    line_elementsD = []
    expt_elementsL = []
    expt_elementsD = []
    #lines = [ 'mean', 'rmse', 'sprd', 'crps', 'stde' ]
    #linel = [ '--', '-', ':', '-.', linestyle_tup['-..-..'] ]
    these_lines = lines.copy()

    nlines = len(these_lines)
    for lina in these_lines:
        iline = lines.index(lina)
        linestyle = linel[iline]
        line_elementsL.append( Line2D([0], [0], color='k', ls=linestyle, label=lina) )
        line_elementsd = []
        for iplot, maxdepth in enumerate(maxdepths):
           line_elementsd.append( Line2D([0], [0], color='k', ls=linestyle, label=lina) )
        line_elementsD.append(line_elementsd)

    nlinee = []
    for ip, these_err in enumerate(means):
        lwidth=1
        if ( ip == 0 ): lwidth=3
        label = labels[ip]
        color = colors[ip%5]

        #Possibility exists I may want different number of lines depending on expt (i.e. no spread / no crps)
        nlinee.append(len(these_lines))
        for lina in these_lines:
            iline=lines.index(lina)
            linestyle = linel[iline]
            if ( iline == 1 ):
                ll, = axeL.semilogy( these_err[iline], depth, linestyle=linestyle, linewidth=lwidth, color=color, label=label)
                expt_elementsL.append(ll)
                expt_elementsd=[]
                for iplot, maxdepth in enumerate(maxdepths):
                    lt, = axeD[iplot].plot( these_err[iline], depth, linewidth=lwidth, linestyle=linestyle, color=color, label=label)
                    expt_elementsd.append(lt)
                expt_elementsD.append(expt_elementsd)
            else:
                ll, = axeL.semilogy( these_err[iline], depth, linestyle=linestyle, color=color)
                for iplot, maxdepth in enumerate(maxdepths):
                    lt, = axeD[iplot].plot( these_err[iline], depth, linewidth=lwidth, linestyle=linestyle, color=color)

    expt_legendL = axeL.legend(handles=expt_elementsL, loc='upper right')
    line_legendL = axeL.legend(handles=line_elementsL, loc='lower right')
    axeL.set_title(title)
    axeL.add_artist(expt_legendL)
    axeL.add_artist(line_legendL)
    axeL.invert_yaxis()
    axeL.set_xlabel(flabel)
    axeL.set_ylabel('depth (m)')
    figL.savefig(outpre+fld+'profile.png')
    figL.savefig(outpre+fld+'profile.pdf')
    plt.close(figL)
    return

cmap_anom = 'seismic'
cmap_zero = 'RdYlBu_r'
cmap_posd = 'gist_stern_r'
def do_profiles(dates=[20200101, 20201230, 7], expts=['noobs_Oper_obsUS', 'noobs_noUSArgo_obsUS'], Levels_here=Levels, labels=None):
    if ( isinstance(labels, type(None)) ):
        labels = expts
    N_area_means = []
    L_bins_means = []
    areas=['Global']+list(PAREAS.keys())+area_extra
    polygons=['global']+[parea[1] for parea in list(PAREAS.items())]+[region1, region2, region3]
    for expt in expts:
        VP = read_qcola.read_VPOLA_dates(dates,  expt, trial='trial', ext='000', group='VP/VP_GEN_INSITU_REALTIME')
        N_area_means.append(take_area_means(VP, polygons=polygons))
        depths = [VP['dep_temperature'].mean(axis=0).values, VP['dep_salinity'].mean(axis=0).values]
        bin_TP = bin_fields(VP, 'mis_temperature', ddeg=2.0, is_3d=True, depth_dim='levels', depth_name='dep_temperature')
        bin_SP = bin_fields(VP, 'mis_salinity', ddeg=2.0, is_3d=True, depth_dim='levels', depth_name='dep_salinity')
        binTP_levs = mean_over_levels(bin_TP, , Levels_here=Levels_here, var_names=['mis_temperature', 'rms_temperature'], cnt_name='cnt_temperature')
        binSP_levs = mean_over_levels(bin_SP, , Levels_here=Levels_here, var_names=['mis_salinity', 'rms_salinity'], cnt_name='cnt_salinity')
        L_bins_means.append((binTP_levs, binSP_levs))
        #del VP

    for iarea, area in enumerate(areas):
        for ifld, fld in enumerate(['T', 'S']):
            means = [ these_means[iarea][ifld] for these_means in N_area_means ]
            outpre='POLATS/'+area
            plot_profile_multi( means, labels, depths[ifld], fld=fld, maxdepths=[200, 2000], outpre=outpre, lines=['mean', 'rmse'], linel = [ '--', '-'])

    for ilevel, depth_range in enumerate(Levels_here):
        Level_string = str(int(depth_range[0]))+'_'+str(int(depth_range[1]))
        Level_string_word = str(int(depth_range[0]))+'m -- '+str(int(depth_range[1]))+'m'
        for iexpt, expt in expts:
            binTP = L_bins_means[iexpt][ilevel][0]
            binSP = L_bins_means[iexpt][ilevel][1]
            if ( iexpt == 0 ):
                binTP_R = binTP
                binSP_R = binSP
            else:
                binTP_D = binTP - binTP_R
                binSP_D = binSP - binSP_R
                for ivar, var in enumerate['mis', 'rms', 'cnt']:
                    lvar = ['misfit', 'rmse', 'count']
                    plt_Tvar=var+'_temperature'
                    plt_Svar=var+'_salinity'
                    Gtitle = ' '+lvar[ivar]+' difference '+expt+' - '+expts[0]
                    Ttitle='Temperature'+Gtitle
                    Stitle='Salinity'+Gtitle
                    Toutfile='POLATS/TLev_'+Level_string+'_d'+var+'.png'
                    Soutfile='POLATS/SLev_'+Level_string+'_d'+var+'.png'
                    cplot.bin_pcolormesh(lon_bin, lat_bin, binTP_D[plt_Tvar], title=Ttitle, levels=None, outfile=Toutfile, obar='horizontal', cmap=cmap_anom)
                    cplot.bin_pcolormesh(lon_bin, lat_bin, binSP_D[plt_Svar], title=Stitle, levels=None, outfile=Soutfile, obar='horizontal', cmap=cmap_anom)
                
            for ivar, var in enumerate['mis', 'rms', 'cnt']:
                lvar = ['misfit', 'rmse', 'count']
                plt_Tvar=var+'_temperature'
                plt_Svar=var+'_salinity'
                Gtitle = ' '+lvar[ivar]+' '+expt
                Ttitle='Temperature'+Gtitle
                Stitle='Salinity'+Gtitle
                Toutfile='POLATS/TLev_'+Level_string+'_'+str(iexpt)+var+'.png'
                Soutfile='POLATS/SLev_'+Level_string+'_'+str(iexpt)+var+'.png'
                cmap_here=cmap_posd
                if ( var == 'mis' ): cmap_here=cmap_anom
                cplot.bin_pcolormesh(lon_bin, lat_bin, binTP[plt_Tvar], title=Ttitle, levels=None, outfile=Toutfile, obar='horizontal', cmap=cmap_here)
                cplot.bin_pcolormesh(lon_bin, lat_bin, binSP[plt_Svar], title=Stitle, levels=None, outfile=Soutfile, obar='horizontal', cmap=cmap_here)
                        

    return
