import numpy as np

import read_SynObsArgo
import soundspeed
import find_cspeed_maxmin

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
        monthst=0
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

    BRSC=np.sum( np.square((TorF_OBS - TorF_EXP)) ) / nobs
    #print(BRSC)
    return BRSC
    
    
    
