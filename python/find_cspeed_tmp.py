from importlib import reload
import sys
import os
import psutil
import time

import numpy as np
import datetime
import pytz
from scipy import signal

sys.path.insert(0, '/home/dpe000/EnGIOPS/python')
import read_dia
import read_grid
import check_date

import cplot
import read_dia
import soundspeed
import fft_giops
import find_profile

import find_cspeed_maxmin

#test_2020_anal=check_date.check_date(2020,10, 14, outtype=datetime.datetime)
#test_2020_date=check_date.check_date(2020,10, 9, outtype=datetime.datetime)
test_2020_anal=datetime.datetime(2020, 10, 14, 0,0,0,0, pytz.UTC)
test_2020_date=datetime.datetime(2020, 10, 9, 0,0,0,0, pytz.UTC)
test_date=datetime.datetime(2021, 10, 13, 0,0,0,0, pytz.UTC)
test_2021_date=datetime.datetime(2021, 10, 12, 0,0,0,0, pytz.UTC)
hir5='/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_hpcarchives'
mir5='/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives'
lonn, latn, orca_area = read_grid.read_coord()

def read_test():
    depthT, lone, late, ETFLD = read_dia.read_ensemble_plus_depth(mir5, 'GIOPS_T', test_date, fld='T', file_pre='ORCA025-CMC-ANAL_1d_')
    depthS, lone, late, ESFLD = read_dia.read_ensemble_plus_depth(mir5, 'GIOPS_T', test_date, fld='S', file_pre='ORCA025-CMC-ANAL_1d_')
    tmask = np.squeeze(read_grid.read_mask(var='tmask'))
    ETFLD = [np.squeeze(TFLD) for TFLD in ETFLD]
    ESFLD = [np.squeeze(SFLD) for SFLD in ESFLD]
    #ETFLD = [np.ma.array(np.squeeze(TFLD), mask=1-tmask) for TFLD in ETFLD]
    #ESFLD = [np.ma.array(np.squeeze(SFLD), mask=1-tmask) for SFLD in ESFLD]
    ETFLD = find_cspeed_maxmin.add_mask(ETFLD)
    ESFLD = find_cspeed_maxmin.add_mask(ESFLD)
    ECFLD = find_cspeed_maxmin.calc_sound_speed_ensemble(ETFLD, ESFLD, depthT, mp_ensemble=True)
    #t0=time.time(); ECFLD_sq = find_cspeed_maxmin.calc_sound_speed_ensemble(ETFLD, ESFLD, depthT, mp_ensemble=False); print('TIME-C-CALC SQ', time.time()-t0)
    #t0=time.time(); ECFLD_mp = find_cspeed_maxmin.calc_sound_speed_ensemble(ETFLD, ESFLD, depthT, mp_ensemble=True); print('TIME-C-CALC MP', time.time()-t0)
    #ECFLD_match = []
    #for ie in range(len(ECFLD)):
    #    ECFLD_match.append(np.all(ECFLD_sq[ie] == ECFLD_mp[ie] ))
    #print('READ match', all(ECFLD_match))
    return depthT, lone, late, ETFLD, ESFLD, ECFLD

def read_test_2020():
    timeT, depthT, lone, late, ETFLD = read_dia.read_ensemble_plus_depthandtime(mir5, 'GIOPS_T', test_2020_anal, fld='T', file_pre='ORCA025-CMC-TRIAL_1d_',time_fld='time_instant')
    timeS, depthS, lone, late, ESFLD = read_dia.read_ensemble_plus_depthandtime(mir5, 'GIOPS_T', test_2020_anal, fld='S', file_pre='ORCA025-CMC-TRIAL_1d_',time_fld='time_instant')
    tmask = np.squeeze(read_grid.read_mask(var='tmask'))
    itime = find_cspeed_maxmin.close_match_of_date(timeT, test_2020_date)
    print(itime, timeT[itime], test_2020_anal, test_2020_date)
    ETFLD = [ np.squeeze(TFLD[itime]) for TFLD in ETFLD]
    ESFLD = [ np.squeeze(SFLD[itime]) for SFLD in ESFLD]
    #ETFLD = [np.ma.array(np.squeeze(TFLD), mask=1-tmask) for TFLD in ETFLD]
    #ESFLD = [np.ma.array(np.squeeze(SFLD), mask=1-tmask) for SFLD in ESFLD]
    ETFLD = find_cspeed_maxmin.add_mask(ETFLD)
    ESFLD = find_cspeed_maxmin.add_mask(ESFLD)
    ECFLD = find_cspeed_maxmin.calc_sound_speed_ensemble(ETFLD, ESFLD, depthT, mp_ensemble=True)
    #t0=time.time(); ECFLD_sq = find_cspeed_maxmin.calc_sound_speed_ensemble(ETFLD, ESFLD, depthT, mp_ensemble=False); print('TIME-C-CALC SQ', time.time()-t0)
    #t0=time.time(); ECFLD_mp = find_cspeed_maxmin.calc_sound_speed_ensemble(ETFLD, ESFLD, depthT, mp_ensemble=True); print('TIME-C-CALC MP', time.time()-t0)
    #ECFLD_match = []
    #for ie in range(len(ECFLD)):
    #    ECFLD_match.append(np.all(ECFLD_sq[ie] == ECFLD_mp[ie] ))
    #print('READ match', all(ECFLD_match))
    return depthT, lone, late, ETFLD, ESFLD, ECFLD

def maxmin_test(ECFLD, depthT):
    t0=time.time(); SC_sq, SB_sq = find_cspeed_maxmin.find_sound_channels(ECFLD, depth=depthT, mp=False); print('TIME', time.time()-t0)
    t0=time.time(); SC_mp, SB_mp = find_cspeed_maxmin.find_sound_channels(ECFLD, depth=depthT, mp=True); print('TIME', time.time()-t0)
    SC_match = []
    SB_match = []
    for ie in range(len(ECFLD)):
        SC_match.append(np.any(SC_sq[ie] == SC_mp[ie] ) )
        SB_match.append(np.any(SB_sq[ie] == SB_mp[ie] ) )
    print( 'SB/SC match' , all(SC_match), all(SB_match) )
    return SC_mp, SB_mp

def sound_channel_var(lone, late, SC, SB):
    SCM, SCV = read_dia.ensemble_var(SC)
    SBM, SBV = read_dia.ensemble_var(SB)
    cplot.grd_pcolormesh(lone, late, SCM, outfile='SCM.png', project='PlateCarree', obar='horizontal')
    cplot.grd_pcolormesh(lone, late, SCV, outfile='SCV.png', project='PlateCarree', obar='horizontal')
    cplot.grd_pcolormesh(lone, late, SBM, outfile='SBM.png', project='PlateCarree', obar='horizontal')
    cplot.grd_pcolormesh(lone, late, SBV, outfile='SBV.png', project='PlateCarree', obar='horizontal')
    cplot.pcolormesh(lone, late, SCM, outfile='SCM_NP.png', project='NorthPolarStereo', obar='horizontal', box=[-180, 180, 50, 90])
    cplot.pcolormesh(lone, late, SCV, outfile='SCV_NP.png', project='NorthPolarStereo', obar='horizontal', box=[-180, 180, 50, 90])
    cplot.pcolormesh(lone, late, SBM, outfile='SBM_NP.png', project='NorthPolarStereo', obar='horizontal', box=[-180, 180, 50, 90])
    cplot.pcolormesh(lone, late, SBV, outfile='SBV_NP.png', project='NorthPolarStereo', obar='horizontal', box=[-180, 180, 50, 90])
    return SCM, SCV, SBM, SBV
    
def test_find_duct(CFLD, depthT, lone, late ):
    t0=time.time();
    TorF1, MDep1 =  find_cspeed_maxmin.find_mins_arr(CFLD, depth=depthT, mindepth=10.0, maxdepth=100.0, mp_depth=False, bySea=True)
    print('mp_depth=False, bySea=True')
    print('TIME', time.time()-t0)
    t0=time.time();
    TorF2, MDep2 =  find_cspeed_maxmin.find_mins_arr(CFLD, depth=depthT, mindepth=10.0, maxdepth=100.0, mp_depth=False, bySea=False)
    print('mp_depth=False, bySea=False')
    print('TIME', time.time()-t0)
    t0=time.time();
    TorF3, MDep3 = find_cspeed_maxmin.find_mins_arr(CFLD, depth=depthT, mindepth=10.0, maxdepth=100.0, mp_depth=False, bySea=False, byxy=True)
    print('mp_depth=False, bySea=False, byxy=True')
    print('TIME', time.time()-t0)
    t0=time.time();
    TorF4, MDep4 = find_cspeed_maxmin.find_mins_arr(CFLD, depth=depthT, mindepth=10.0, maxdepth=100.0, mp_depth=True, bySea=True)
    print('mp_depth=True, bySea=True')
    print('TIME', time.time()-t0)
    t0=time.time();
    TorF6, MDep6 = find_cspeed_maxmin.find_mins_arr(CFLD, depth=depthT, mindepth=10.0, maxdepth=100.0, mp_depth=True, bySea=False, byxy=True)
    print('mp_depth=True, bySea=False, byxy=True')
    print('TIME', time.time()-t0)
    t0=time.time();
    TorF5, MDep5 = find_cspeed_maxmin.find_mins_arr(CFLD, depth=depthT, mindepth=10.0, maxdepth=100.0, mp_depth=True, bySea=True)  #NOT TESTING mp_depth=True, bySea=False
    print('mp_depth=True, bySea=False')
    print('TIME', time.time()-t0)
    t0=time.time();
    TorF, MDep = find_cspeed_maxmin.find_mins_arr(CFLD, depth=depthT, mindepth=10.0, maxdepth=100.0, mp_depth=True, bySea=True)
    print('mp_depth=True, bySea=True')
    print('TIME', time.time()-t0)
    print('TorF1', np.all(TorF1 == TorF))
    print('TorF2', np.all(TorF2 == TorF))
    print('TorF3', np.all(TorF3 == TorF))
    print('TorF4', np.all(TorF4 == TorF))
    print('TorF5', np.all(TorF5 == TorF))
    print('TorF6', np.all(TorF6 == TorF))
    print('MDep1', np.all(MDep1 == MDep))
    print('MDep2', np.all(MDep2 == MDep))
    print('MDep3', np.all(MDep3 == MDep))
    print('MDep4', np.all(MDep4 == MDep))
    print('MDep5', np.all(MDep5 == MDep))
    print('MDep6', np.all(MDep6 == MDep))
    IS0=np.where(TorF == True) ; print(len(IS0[0])) 
    IS1=np.where(TorF1 == True) ; print(len(IS1[0])) 
    IS2=np.where(TorF2 == True) ; print(len(IS2[0])) 
    IS3=np.where(TorF3 == True) ; print(len(IS3[0])) 
    IS4=np.where(TorF4 == True) ; print(len(IS4[0])) 
    IS5=np.where(TorF5 == True) ; print(len(IS5[0])) 
    IS6=np.where(TorF6 == True) ; print(len(IS6[0])) 
    print(np.min(MDep1))
    print(np.min(MDep2))
    print(np.min(MDep3))
    print(np.min(MDep4))
    print(np.min(MDep5))
    print(np.min(MDep6))
    cplot.grd_pcolormesh(lone, late, TorF.astype(float), outfile='TorF.png', project='PlateCarree', obar='horizontal')
    cplot.grd_pcolormesh(lone, late, TorF1.astype(float), outfile='TorF1.png', project='PlateCarree', obar='horizontal')
    cplot.grd_pcolormesh(lone, late, TorF2.astype(float), outfile='TorF2.png', project='PlateCarree', obar='horizontal')
    cplot.grd_pcolormesh(lone, late, TorF3.astype(float), outfile='TorF3.png', project='PlateCarree', obar='horizontal')
    cplot.grd_pcolormesh(lone, late, TorF4.astype(float), outfile='TorF4.png', project='PlateCarree', obar='horizontal')
    cplot.grd_pcolormesh(lone, late, TorF5.astype(float), outfile='TorF5.png', project='PlateCarree', obar='horizontal')
    cplot.grd_pcolormesh(lone, late, TorF6.astype(float), outfile='TorF6.png', project='PlateCarree', obar='horizontal')
    return TorF, MDep

def test_shallow_ducts_ens(ECFLD, depthT, lone, late, date=test_date):
    datestr=check_date.check_date(date)
    #t0=time.time()
    #ETorF, EMDep, PDuct1, PVar1 = find_cspeed_maxmin.find_mins_ens (ECFLD, depth=depthT, mindepth=10.0, maxdepth=100.0, mp_depth=True, bySea=True, mp_ensemble=False)   
    #print('mp_depth=True,bySea=True, mp_ensemble=False')
    #print('TIME', time.time()-t0)
    t0=time.time();
    print('mp_depth=False, bySea=True, mp_ensemble=True')
    ETorF, EMDep, PDuct, PVar = find_cspeed_maxmin.find_mins_ens (ECFLD, depth=depthT, mindepth=10.0, maxdepth=100.0, mp_depth=False, bySea=True, mp_ensemble=True)   
    print('TIME', time.time()-t0)
    #print(np.all(PDuct1 == PDuct))
    print(np.all(PVar == PDuct*(1-PDuct)), np.min(PDuct), np.max(PDuct), np.max(PVar), np.max((PDuct*(1-PDuct))))
    print(PDuct.shape, lone.shape, late.shape)
    cplot.grd_pcolormesh(lone, late, PDuct, outfile='GIOPS_TC_MND/PDuct'+'_'+datestr+'.png', project='PlateCarree', obar='horizontal', cmap='seismic')
    cplot.pcolormesh(lone, late, PDuct, outfile='GIOPS_TC_MND/PDuct_NP'+'_'+datestr+'.png', project='NorthPolarStereo', obar='horizontal', box=[-180, 180, 50, 90], cmap='seismic')
    cplot.pcolormesh(lone, late, PDuct, outfile='GIOPS_TC_MND/PDuct_SP'+'_'+datestr+'.png', project='SouthPolarStereo', obar='horizontal', box=[-180, 180, -90, -50], cmap='seismic')
    cplot.pcolormesh(lone, late, PVar, outfile='GIOPS_TC_MND/PDvar_NP'+'_'+datestr+'.png', project='NorthPolarStereo', obar='horizontal', box=[-180, 180, 50, 90], cmap='seismic')
    cplot.pcolormesh(lone, late, PDuct*(1-PDuct), outfile='PDmPD_NP'+'_'+datestr+'.png', project='NorthPolarStereo', obar='horizontal', box=[-180, 180, 50, 90], cmap='seismic')

    NA_REG =[-90, 15, 30, 65] 
    BOX = find_profile.PTS
    BOX = list(BOX[1:])+[BOX[1]]
    BOX=[ (corner[1], corner[0]) for corner in BOX]
    BBOX=[(-61.25, 42.5), (-61.25, 41.5), (-62.75, 41.5), (-62.75, 42.5), (-61.25, 42.5)]
    fft_giops.pcolormesh_with_box(lone, late, PDuct, outfile='PDuct_NAtl.png', project='Mercator', obar='horizontal', box=NA_REG, cmap='seismic', plot_boxes=[BOX, BBOX], box_colors=['g','c'])
    fft_giops.pcolormesh_with_box(lone, late, PVar, outfile='PVari_NAtl.png', project='Mercator', obar='horizontal', box=NA_REG, cmap='seismic', plot_boxes=[BOX, BBOX], box_colors=['g','c'])
    NS_REG = [-70, -50, 35, 50]
    fft_giops.pcolormesh_with_box(lone, late, PDuct, project='Mercator',box=NS_REG, obar='horizontal', plot_boxes=[BOX, BBOX], box_colors=['g','c'], outfile='GIOPS_TC_MND/PDuct_EMND'+'_'+datestr+'.png', cmap='seismic')
    return ETorF, EMDep, PDuct, PVar

def plot_shallow_ducts(PDuct, date=test_2021_date):
    datestr=check_date.check_date(date)
    print(PDuct.shape)
    cplot.grd_pcolormesh(lonn, latn, PDuct, outfile='GIOPS_TC_MND/PDuct'+'_'+datestr+'.png', project='PlateCarree', obar='horizontal', cmap='seismic')
    cplot.pcolormesh(lonn, latn, PDuct, outfile='GIOPS_TC_MND/PDuct_NP'+'_'+datestr+'.png', project='NorthPolarStereo', obar='horizontal', box=[-180, 180, 50, 90], cmap='seismic')
    cplot.pcolormesh(lonn, latn, PDuct, outfile='GIOPS_TC_MND/PDuct_SP'+'_'+datestr+'.png', project='SouthPolarStereo', obar='horizontal', box=[-180, 180, -90, -50], cmap='seismic')
    cplot.pcolormesh(lonn, latn, PDuct*(1-PDuct), outfile='PVari_NP'+'_'+datestr+'.png', project='NorthPolarStereo', obar='horizontal', box=[-180, 180, 50, 90], cmap='seismic')

    NA_REG =[-90, 15, 30, 65] 
    BOX = find_profile.PTS
    BOX = list(BOX[1:])+[BOX[1]]
    BOX=[ (corner[1], corner[0]) for corner in BOX]
    BBOX=[(-61.25, 42.5), (-61.25, 41.5), (-62.75, 41.5), (-62.75, 42.5), (-61.25, 42.5)]
    fft_giops.pcolormesh_with_box(lonn, latn, PDuct, outfile='PDuct_NAtl.png', project='Mercator', obar='horizontal', box=NA_REG, cmap='seismic', plot_boxes=[BOX, BBOX], box_colors=['g','c'])
    fft_giops.pcolormesh_with_box(lonn, latn, PDuct*(1-PDuct), outfile='PVari_NAtl.png', project='Mercator', obar='horizontal', box=NA_REG, cmap='seismic', plot_boxes=[BOX, BBOX], box_colors=['g','c'])
    NS_REG = [-70, -50, 35, 50]
    fft_giops.pcolormesh_with_box(lonn, latn, PDuct, project='Mercator',box=NS_REG, obar='horizontal', plot_boxes=[BOX, BBOX], box_colors=['g','c'], outfile='GIOPS_TC_MND/PDuct_EMND'+'_'+datestr+'.png', cmap='seismic')
    return 

def run_test():
  do2021 = True
  do2020 = True
  if ( do2021 ):
    print(test_2021_date, flush=True)
    depthT, lone, late, ETFLD, ESFLD, ECFLD = read_test()
    print(ETFLD[0].shape)
    nz, nx, ny = ETFLD[0].shape
    print(nx, nx, ny)
    print('Performing maxmin test')
    SC, SB = maxmin_test(ECFLD, depthT)
    print('Performing Sound Channel Variability')
    SCM, SCV, SBM, SBV = sound_channel_var(lone, late, SC, SB)
    #TorF, MDep = test_find_duct(ECFLD[0], depthT, lone, late)
    print('Finding DUCTS')
    ETorF, EMDep, PDuct, PVar = test_shallow_ducts_ens(ECFLD, depthT, lone, late, date=test_2021_date)
    print('End', test_2021_date)
  if ( do2020 ):
    print(test_2020_date, flush=True)
    depthT, lone, late, ETFLD, ESFLD, ECFLD = read_test_2020()
    print(ETFLD[0].shape)
    nz, nx, ny = ETFLD[0].shape
    print(nx, nx, ny)
    print('Performing maxmin test')
    SC, SB = maxmin_test(ECFLD, depthT)
    print('Performing Sound Channel Variability')
    SCM, SCV, SBM, SBV = sound_channel_var(lone, late, SC, SB)
    #TorF, MDep = test_find_duct(ECFLD[0], depthT, lone, late)
    print('Finding DUCTS')
    ETorF, EMDep, PDuct, PVar = test_shallow_ducts_ens(ECFLD, depthT, lone, late,date=test_2020_date)
    print('End', test_2020_+date)

def run_easy():
  do2021 = True
  do2020 = True
  if ( do2021 ):
    print(test_2021_date, flush=True)
    ETorF, EMDep, PDuct, PVar = find_cspeed_maxmin.find_ducts_for_date(test_2021_date+datetime.timedelta(days=1), anal=True, expt='GIOPS_T', mindepth=10.0, maxdepth=100.0)
    plot_shallow_ducts(PDuct, date=test_2021_date)

    print('End', test_2021_date)
  if ( do2020 ):
    print(test_2020_date, flush=True)
    ETorF, EMDep, PDuct, PVar = find_cspeed_maxmin.find_ducts_for_date(test_2020_date+datetime.timedelta(days=1), anal=False, expt='GIOPS_T', mindepth=10.0, maxdepth=100.0)
    plot_shallow_ducts(PDuct, date=test_2020_date)
    print('End', test_2020_date)
if ( __name__ == '__main__' ):
    run_easy()
