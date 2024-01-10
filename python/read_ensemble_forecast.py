
import find_geps_fcst
import stfd
import find_cspeed_maxmin
import soundspeed
import os
import numpy as np

datadir='/fs/site5/eccc/mrd/rpnenv/dpe000/'
dat5dir='/fs/site5/eccc/mrd/rpnenv/dpe000/'
dat6dir='/fs/site5/eccc/mrd/rpnenv/dpe000/'
mdir=datadir+'/maestro_archives'
hdir=dat6dir+'/maestro_hpcarchives'

def read_ensemble_forecast(fld, expt, date, lhr, ensemble=range(21), src='ocn', ddir=datadir+'/maestro'):

    FLD_ENSEMBLE = []
    for iens in ensemble:
        FLD, lat, lon, lev = read_member_forecast(fld, expt, date, lhr, iens, src=src, ddir=ddir)
        FLD_ENSEMBLE.append(FLD)
    return FLD_ENSEMBLE, lat, lon, lev   

def read_member_forecast(fld, expt, date, lhr, iens, src='ocn', ddir=datadir+'/maestro', vfreq=24):

    var=fld
    if ( fld == 'T' ):  var='TM'
    if ( fld == 'S' ):  var='SALW'

    if ( fld == 'T' ):  DM=3
    if ( fld == 'S' ):  DM=3
    
    lon=None
    lat=None
    lev=0
    FLD=None    

    if ( expt[0:4] == 'oper' or expt[0:4] == 'OPER' or expt == 'GEPS' ):
        file=find_geps_fcst.find_geps_fcst_file(date, lhr, iens, sys='OP', src=src, execute=True, only_this_ens=False)
        exists=os.path.isfile(file)
    elif ( expt == 'parallel' ):
        file=find_geps_fcst.find_geps_fcst_file(date, lhr, iens, sys='PS', src=src, execute=True, only_this_ens=False)
        exists=os.path.isfile(file)
    else:  # Assume a maestro suite.
        file, exists = find_geps_fcst.geps_in_maestro(expt, date, lhr, iens, src=src, ddir=ddir)

    #print(file)
    if ( ( not lon ) and ( not lat ) and exists ):
        lon, lat = stfd.read_latlon(file)
    
    if ( ( DM==3 ) and exists ):
        if ( expt[0:4] == 'oper' or expt[0:4] == 'OPER' or expt == 'GEPS' ):
            if ( date.weekday() != 3 ):
                print('DAY IS NOT THURSDAY')
                print('CURRENTLY NO 3D FIELDS')
                return None, lat, lon, None
        # vfreq removes unwanted 3h values -- but there is still an unwanted daily SST
        lev , FLD = stfd.read_fstd_multi_lev(file, var, typvar='P@', vfreq=vfreq)
        lev , MSK = stfd.read_fstd_multi_lev(file, var, typvar='@@', vfreq=vfreq)
        if ( 0.0 in lev ): 
            zlev = lev.index(0.0)
            FLD = np.delete(FLD, zlev, 0)
            MSK = np.delete(MSK, zlev, 0)
            lev.pop(zlev)
        
    if ( ( DM==2) and exists):
        __, __, FLD = stfd.read_fstd_var(file, var, typvar='P@', vfreq=24)
        __, __, MSK = stfd.read_fstd_var(file, var, typvar='@@', vfreq=24)
    
    FLM = np.ma.array(FLD, mask=1-MSK)
        
    return FLM, lat, lon, np.array(lev)

def get_ensemble_cspeed(expt, date, lhr, ensemble=range(21), ddir=hdir):
    TeFLD, lat, lon, lev =read_ensemble_forecast('T', expt, date, lhr, ensemble=ensemble, src='ocn', ddir=ddir)
    SeFLD, __, __ , __   =read_ensemble_forecast('S', expt, date, lhr, ensemble=ensemble, src='ocn', ddir=ddir)
    TCeFLD = [soundspeed.Kelvin_to_Celsius(Tfld) for Tfld in TeFLD]
    CeFLD = find_cspeed_maxmin.calc_sound_speed_ensemble(TCeFLD, SeFLD, lev, mp_ensemble=True) 
    ## NOTE returned temperature is in Celsius.
    return lev, lon, lat, CeFLD, TCeFLD, SeFLD
    
    
