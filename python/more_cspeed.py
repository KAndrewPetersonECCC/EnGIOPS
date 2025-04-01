import numpy as np

import read_SynObsArgo
import soundspeed
import find_cspeed_maxmin
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cplot

file='/home/dpe000/data/ppp6/SynObs2/5/OP-AN/GIOPS/CNTL/OPA-PL/ArRef/OPA-PL_ArRef_202001_GIOPS_CNTL.nc'
filf='/home/dpe000/data/ppp6/JAMSTEC_MIRROR/www.jamstec.go.jp/jcope/data/synobs_frontiers/OP-AN/FOAM/CNTL/OPA-PL/ArRef/OPA-PL_ArRef_202001_FOAM_CNTL.nc'
filg='/home/dpe000/data/ppp6/JAMSTEC_MIRROR/www.jamstec.go.jp/jcope/data/synobs_frontiers/OP-AN/FOAM/NoArgo/OPA-PL/ArRef/OPA-PL_ArRef_202001_FOAM_NoArgo.nc'
odird='/home/dpe000/data/ppp6/SynObs2/5/'
ddirS='/home/dpe000/data/ppp6/JAMSTEC_MIRROR/www.jamstec.go.jp/jcope/data/synobs_frontiers/'

#(lon, lat, time, depth), (TEMP, SALW), (TEMP_obs, SALW_obs) = read_SynObsArgo.read_argo_data(file, obs=True)
#(lon, lat, time, depth), (TEMP, SALW) = read_SynObsArgo.read_argo_data(filf, obs=False)
#(lon, lat, time, depth), (TEMP_a, SALW_a) = read_SynObsArgo.read_argo_data(filg, obs=False)

#depth_tile = np.tile(depth, (2899, 1))

#C_argo = soundspeed.sound_speed(depth, TEMP_obs, SALW_obs)
#C_mode = soundspeed.sound_speed(depth, TEMP, SALW)    
#C_expt = soundspeed.sound_speed(depth, TEMP_a, SALW_a)    

#TorF_argo = np.array(find_cspeed_maxmin.find_mins_obs(C_argo, depth_tile, mp=False)).astype(int)
#TorF_mode = np.array(find_cspeed_maxmin.find_mins_obs(C_mode, depth_tile, mp=False)).astype(int)
#TorF_expt = np.array(find_cspeed_maxmin.find_mins_obs(C_expt, depth_tile, mp=False)).astype(int)

#BRSC=np.sum( np.square((TorF_mode - TorF_argo)) ) 
#BRSC_expt=np.sum( np.square((TorF_expt - TorF_argo)) ) 


def do_cspeed_expt(inst, expt, start, final, ref="Ref", ddir=ddirS, odir=odird):
    startyr = start[0]
    startmn = start[1]
    finalyr = final[0]
    finalmn = final[1]
    
    instt=inst
    if ( inst == 'MOVE-G3' ): instt=inst+'F'
    
    TIMA=None
    oiles=[]
    files=[]
    for year in range(startyr, finalyr+1):
        months=range(1,13)
        monthst=1
        monthfi=12
        if ( year == startyr ): monthst=startmn
        if ( year == finalyr ): monthfi=finalmn
        for month in range(monthst, monthfi+1):
            datest = str(year)+str(month).zfill(2)
            file=ddir+"/OP-AN/"+inst+'/'+expt+'/OPA-PL/Ar'+ref+'/'+'OPA-PL_Ar'+ref+'_'+datest+'_'+instt+'_'+expt+'.nc'
            oile=odir+"/OP-AN/"+'GIOPS'+'/'+'CNTL'+'/OPA-PL/Ar'+ref+'/'+'OPA-PL_Ar'+ref+'_'+datest+'_'+'GIOPS'+'_'+'CNTL'+'.nc'
            #print(file, oile)
            files.append(file)
            oiles.append(oile)
            
    for iif,file in enumerate(files):
        oile=oiles[iif]
        (lon, lat, time, depth), (TJ, SJ), (TO, SO) = read_SynObsArgo.read_argo_data(oile, obs=True)
        (lon, lat, time, depth), (TW, SW) = read_SynObsArgo.read_argo_data(file, obs=False)
        if ( isinstance(TIMA, type(None)) ):
            TIMA = time
            LONA = lon
            LATA = lat
            T_OBS = TO
            S_OBS = SO
            T_EXP = TW
            S_EXP = SW
        else:
            TIMA = np.append(TIMA, time, axis=0)
            LONA = np.append(LONA, lon, axis=0)
            LATA = np.append(LATA, lat, axis=0)
            T_OBS = np.append(T_OBS, TO, axis=0)
            S_OBS = np.append(S_OBS, SO, axis=0)
            T_EXP = np.append(T_EXP, TW, axis=0)
            S_EXP = np.append(S_EXP, SW, axis=0)

    nobs = TIMA.shape[0]
    depth_tile = np.tile(depth, (nobs, 1))
    
    C_OBS = soundspeed.sound_speed(depth, T_OBS, S_OBS)
    C_EXP = soundspeed.sound_speed(depth, T_EXP, S_EXP)    

    TorF_OBS = np.array(find_cspeed_maxmin.find_mins_obs(C_OBS, depth_tile, mp=False)).astype(int)
    TorF_EXP = np.array(find_cspeed_maxmin.find_mins_obs(C_EXP, depth_tile, mp=False)).astype(int)

    is_true = np.where( TorF_OBS )
    is_model = np.where( TorF_EXP )
    is_false = np.where( TorF_OBS == False )
    is_fcst = np.where( ( TorF_OBS == True ) & ( TorF_EXP == True ) )
    is_null = np.where( ( TorF_OBS == False ) * ( TorF_EXP == False ) )
    is_miss = np.where( ( TorF_OBS == True ) & ( TorF_EXP == False ) )
    is_alarm = np.where( ( TorF_OBS == False ) & ( TorF_EXP == True ) )
    ntrue, nfalse, nfcst, nnull, nmiss, nalarm = len(is_true[0]), len(is_false[0]), len(is_fcst[0]), len(is_null[0]), len(is_miss[0]), len(is_alarm[0])
    BRSC=np.sum( np.square((TorF_OBS - TorF_EXP)) ) / nobs
    MISS=nmiss/nobs
    ALARM=nalarm/nobs
    FCST=nfcst/nobs
    NULL=nnull/nobs
    print(BRSC, nobs )
    print(FCST, nfcst, ntrue)
    print(MISS, nmiss, ntrue)
    print(NULL, nnull, nfalse)
    print(ALARM, nalarm, nfalse)
    trange=f"{start[0]}/{start[1]:02} -- {final[0]}/{final[1]:02}"
    orange=f"{start[0]}{start[1]:02}-{final[0]}{final[1]:02}"
    make_scatter([is_fcst, is_miss, is_alarm, is_null], (LONA, LATA), expt=expt, inst=inst, ref=ref, trange=trange, orange=orange)
    
    return BRSC, MISS, ALARM

def make_scatter(IS_RESULT, LONLAT, expt='EXPT', inst='INST', ref='Ref', trange='', orange=''):
    [is_fcst, is_miss, is_alarm, is_null] = IS_RESULT
    nfcst, nnull, nmiss, nalarm = len(is_fcst[0]), len(is_null[0]), len(is_miss[0]), len(is_alarm[0])
    LONS = LONLAT[0]
    LATS = LONLAT[1]
    outfile='CSPEED/SynObsIC/'+inst+'_'+expt+'_'+ref
    if ( len(orange) > 0 ): outfile=outfile+'_'+orange
    outfile=outfile+'.png'
    fig, axe = ini_scatter()
    add_scatter(fig, axe, (LONS[is_miss], LATS[is_miss]), color='k', marker='.', s=1, label='Null Forecast (neither) = '+str(nnull))
    add_scatter(fig, axe, (LONS[is_miss], LATS[is_miss]), color='red', marker='o', s=5, label='Missed Forecast (obs only) = '+str(nmiss))
    add_scatter(fig, axe, (LONS[is_alarm], LATS[is_alarm]), color='magenta', marker='o', s=5, label='False Alarm (model only) = '+str(nalarm))
    add_scatter(fig, axe, (LONS[is_fcst], LATS[is_fcst]), color='green', marker='o', s=5, label='Forecast hit (obs&fcst) = '+str(nfcst))
    title='DUCTS for '+expt+'/'+inst
    if ( len(trange) > 0 ): title=title+' for '+trange
    fin_scatter(fig, axe, title=title, output=outfile)
    
def ini_scatter(project='PlateCarree'):
    fig = plt.figure()
    projections, pcarree = cplot.make_projections()
    axe = plt.subplot(projection=projections[project])
    axe.set_global()
    axe.coastlines()
    return fig, axe

def add_scatter(fig, axe, lonlat, color='k', marker='.', label='ALL', s=5):  
    lon = lonlat[0]
    lat = lonlat[1]
    scat = axe.scatter(x=lon.flatten(), y=lat.flatten(), c=color, s=s, alpha=0.5, transform=ccrs.PlateCarree(), marker=marker, label=label)
    return scat
    
def fin_scatter(fig, axe, title='TITLE', output='scatter.png'):
   axe.legend(fontsize='x-small')
   axe.set_title(title)
   fig.savefig(output, bbox_inches='tight')
   plt.close(fig)
   return
   
    
    
