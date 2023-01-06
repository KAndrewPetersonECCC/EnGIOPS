#from importlib import reload
import sys
import os
sys.path.insert(0, '/home/dpe000/EnGIOPS/python')
import numpy as np
import read_dia
import read_grid
import datetime
import pytz

import multiprocessing
import itertools
from functools import partial

import matplotlib.pyplot as plt
import matplotlib.colors as clr

import find_value_at_point
import check_date
import write_nc_grid

def write_profile(name, pt, depth, Tprofile, Sprofile, file):
    if ( Tprofile.ndim == 2 ):
        ne, nz = Tprofile.shape
    elif ( Tprofile.ndim == 1 ):
        ne, nz = 1, Tprofile.shape[0]
        Tprofile = np.reshape(Tprofile, (ne,nz))
        Sprofile = np.reshape(Sprofile, (ne,nz))
    with open(file,'w') as ofile:
        ofile.write(("{}\r\n").format(name))
        ofile.write(("{:13.8g}"*2+"\r\n").format(*tuple(pt)))
        ofile.write(("{}\r\n").format('Temperature'))
        for iz in range(nz):
            ofile.write(("{:13.8g}"*(ne+1)+"\r\n") .format( depth[iz], *tuple(Tprofile[:,iz]) ))
        ofile.write(("{}\r\n").format('Salinity'))
        for iz in range(nz):
            ofile.write(("{:13.8g}"*(ne+1)+"\r\n") .format( depth[iz], *tuple(Sprofile[:,iz]) ))
    return
        
#Dates were:
 
#09 Oct 2020
#12 Oct 2021
 
#Centre of the box: (41.8795 N, 61.783 W)
#NE Corner: (42.0047 N, 61.6143 W)
#SE Corner: (41.7535 N, 61.6247 W)
#SW Corner: (41.7542 N, 61.9565 W)
#NW Corner: (42.0059 N, 61.9446 W)

YEARS=[2020, 2021]
EXD = (datetime.datetime(2020, 10, 9, 0,0,0,0, pytz.UTC) , datetime.datetime(2021, 10, 12, 0,0,0,0, pytz.UTC))
GDD = [ date+datetime.timedelta(days=(2-date.weekday())%7) for date in EXD]
TITLE = ['CN', 'NE', 'SE', 'SW', 'NW']
LITLE = ['BOX CENTRE', 'NE CORNER', 'SE CORNER', 'SW CORNER', 'NW CORNER']
PTS = ( (41.8795, -61.783), (42.0047, -61.6143),  (41.7535, -61.6247), (41.7542, -61.9565), (42.0059, -61.9446))
LATPTS = [PT[0] for PT in PTS]
LONPTS = [PT[1] for PT in PTS]

iyear=0
EGIOPS='GIOPS_T'

sl='/'
eg_file='/fs/site6/eccc/mrd/rpnenv/dpe000/maestro_archives/GIOPS_320_GU/SAM2/20201009/DIA/ORCA025-CMC-ANAL_1d_grid_T_2020100900.nc'
hir5='/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_hpcarchives'
hir6='/fs/site6/eccc/mrd/rpnenv/dpe000/maestro_hpcarchives'
mir5='/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives'
mir6='/fs/site6/eccc/mrd/rpnenv/dpe000/maestro_archives'

Nmask = read_grid.read_mask()
nz, nx, ny = Nmask.shape

def find_profile(years=[2020, 2021]):

    for year in years:
        iyear = YEARS.index(year)
        datestr_gu = check_date.check_date(EXD[iyear], dtlen=8)
        datestr_gd = check_date.check_date(GDD[iyear], dtlen=8)
        file_gu  = mir6+sl+'GIOPS_320_GU/SAM2/'+datestr_gu+'/DIA/ORCA025-CMC-ANAL_1d_grid_T_'+datestr_gu+'00.nc'
        file_gda = mir6+sl+'GIOPS_320_GD/SAM2/'+datestr_gd+'/DIA/ORCA025-CMC-ANAL_1d_grid_T_'+datestr_gd+'00.nc'
        file_gdt = mir6+sl+'GIOPS_320_GD/SAM2/'+datestr_gd+'/DIA/ORCA025-CMC-TRIAL_1d_grid_T_'+datestr_gd+'00.nc'

        # FOR TESTING ONLY
        file_e0='/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_hpcarchives/GIOPS_T0/SAM2/'+datestr_gd+'/DIA/ORCA025-CMC-TRIAL_1d_grid_T_'+datestr_gd+'00.nc'
        file_e3='/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_hpcarchives/GIOPS_T3/SAM2/'+datestr_gd+'/DIA/ORCA025-CMC-TRIAL_1d_grid_T_'+datestr_gd+'00.nc'

        lonn, latn, TFLD_gu, SFLD_gu = read_dia.read_sam2_grid_t(file_gu)
        lonn, latn, TFLD_gd, SFLD_gd = read_dia.read_sam2_grid_t(file_gdt)
        lon0, lat0, TFLD_e0, SFLD_e0 = read_dia.read_sam2_grid_t(file_e0)
        lon3, lat3, TFLD_e3, SFLD_e3 = read_dia.read_sam2_grid_t(file_e3)
        lone, late, ETFLD = read_dia.read_ensemble(hir5, EGIOPS, GDD[iyear], fld='T', file_pre='ORCA025-CMC-TRIAL_1d_')
        lone, late, ESFLD = read_dia.read_ensemble(hir5, EGIOPS, GDD[iyear], fld='S', file_pre='ORCA025-CMC-TRIAL_1d_')

        depthT =  read_dia.read_sam2_levels(file_e0)
        TIMES = read_dia.read_sam2_times(file_gdt)

        lat_pt, lon_pt = PTS[0]
        ipt, jpt = find_value_at_point.find_nearest_glcpt(lon_pt, lat_pt, lonn, latn)

        # NOT ACTUALLY DEPENDENT ON YEAR -- but you need the model LAT/LON
        IJPTS=[]
        for PT in PTS:
            lat_pt, lon_pt = PT
            IJPTS.append(find_value_at_point.find_nearest_glcpt(lon_pt, lat_pt, lonn, latn))

        IPTS = [IJPT[0] for IJPT in IJPTS]
        JPTS = [IJPT[1] for IJPT in IJPTS]


        it = TIMES.index(EXD[iyear])

        Tpro_gu = np.squeeze(TFLD_gu[0,:,IPTS, JPTS])
        Tpro_gd = np.squeeze(TFLD_gd[it,:,IPTS,JPTS])
        Tpro_e3 = np.squeeze(TFLD_e3[it,:,IPTS,JPTS])
        Spro_gu = np.squeeze(SFLD_gu[0,:,IPTS, JPTS])
        Spro_gd = np.squeeze(SFLD_gd[it,:,IPTS,JPTS])
        Spro_e3 = np.squeeze(SFLD_e3[it,:,IPTS,JPTS])
        TPRO_en = []
        SPRO_en = []
        for TFLD in ETFLD:
            TPRO_en.append( np.squeeze(TFLD[it,:,IPTS, JPTS]) )
        for SFLD in ESFLD:
            SPRO_en.append( np.squeeze(SFLD[it,:,IPTS, JPTS]) )

        TPRO_arr = np.transpose(np.array(TPRO_en), [1, 0, 2])
        SPRO_arr = np.transpose(np.array(SPRO_en), [1, 0, 2])
        Tpro_mn = sum(TPRO_en) / len(TPRO_en)
        Spro_mn = sum(SPRO_en) / len(SPRO_en)

        Tpri_gu = Tpro_gu.copy()
        Tpri_gd = Tpro_gd.copy()
        TPRI_en = TPRO_en.copy()

        Tfig, Taxes = plt.subplots(3,3)
        Sfig, Saxes = plt.subplots(3,3)
        for ipl,tit in enumerate(TITLE):
            if ( tit == 'CN' ):  iax, iay = (1,1)
            if ( tit == 'NE' ):  iax, iay = (0,2)
            if ( tit == 'SE' ):  iax, iay = (2,2)
            if ( tit == 'SW' ):  iax, iay = (2,0)
            if ( tit == 'NW' ):  iax, iay = (0,0)
            Taxes[iax,iay].plot(Tpro_gu[ipl,:], depthT, color='red', linewidth=2.0)
            #Taxes[iax,iay].plot(Tpri_gu[ipl,:], depthT, color='magenta')
            Taxes[iax,iay].plot(Tpro_gd[ipl,:], depthT, color='blue')
            #Taxes[iax,iay].plot(Tpri_gd[ipl,:], depthT, color='cyan')
            Taxes[iax,iay].plot(Tpro_mn[ipl,:], depthT, color='k')
            Saxes[iax,iay].plot(Spro_gu[ipl,:], depthT, color='red', linewidth=2.0)
            #Saxes[iax,iay].plot(Spri_gu[ipl,:], depthT, color='magenta')
            Saxes[iax,iay].plot(Spro_gd[ipl,:], depthT, color='blue')
            #Saxes[iax,iay].plot(Spri_gd[ipl,:], depthT, color='cyan')
            Saxes[iax,iay].plot(Spro_mn[ipl,:], depthT, color='k')
            for ipro, Tpro in enumerate(TPRO_en):
                #Tpro = TPRO_en[ipro]
                #Tpri = TPRI_en[ipro]
                Taxes[iax,iay].plot(Tpro[ipl,:], depthT, color='gray', linewidth=0.1) 
                #Taxes[iax,iay].plot(Tpri[ipl,:], depthT, color='khaki', linewidth=0.1) 
            for ipro, Spro in enumerate(SPRO_en):
                #Spro = TPRO_en[ipro]
                #Spri = TPRI_en[ipro]
                Saxes[iax,iay].plot(Spro[ipl,:], depthT, color='gray', linewidth=0.1) 
                #Saxes[iax,iay].plot(Spri[ipl,:], depthT, color='khaki', linewidth=0.1) 
            Taxes[iax,iay].set_ylim([0, 200])                                                    
            Taxes[iax,iay].set_xlim([10,25])                                                    
            Taxes[iax,iay].invert_yaxis()   
            Taxes[iax,iay].set_title(tit+' '+'Temperature')                                      
            Saxes[iax,iay].set_ylim([0, 200])                                                    
            Saxes[iax,iay].set_xlim([30,40])                                                    
            Saxes[iax,iay].invert_yaxis()   
            Saxes[iax,iay].set_title(tit+' '+'Saliniity')                                      

        Tfig.delaxes(Taxes[0,1])
        Tfig.delaxes(Taxes[2,1])
        Tfig.delaxes(Taxes[1,0])
        Tfig.delaxes(Taxes[1,2])
        Sfig.delaxes(Saxes[0,1])
        Sfig.delaxes(Saxes[2,1])
        Sfig.delaxes(Saxes[1,0])
        Sfig.delaxes(Saxes[1,2])
        syear=str(year)
        Tfig.savefig('MNDprofiles/Tprofiles_'+syear+'.png')
        Sfig.savefig('MNDprofiles/Sprofiles_'+syear+'.png')
        plt.close(Tfig)
        plt.close(Sfig)

        for ipl,tit in enumerate(TITLE):
            Tfig, Taxes = plt.subplots()
            Sfig, Saxes = plt.subplots()
            Taxes.plot(Tpro_gu[ipl,:], depthT, color='red', linewidth=2.0)
            #Taxes.plot(Tpri_gu[ipl,:], depthT, color='magenta')
            Taxes.plot(Tpro_gd[ipl,:], depthT, color='blue')
            #Taxes.plot(Tpri_gd[ipl,:], depthT, color='cyan')
            Taxes.plot(Tpro_mn[ipl,:], depthT, color='k')
            Saxes.plot(Spro_gu[ipl,:], depthT, color='red', linewidth=2.0)
            #Saxes.plot(Spri_gu[ipl,:], depthT, color='magenta')
            Saxes.plot(Spro_gd[ipl,:], depthT, color='blue')
            #Saxes.plot(Spri_gd[ipl,:], depthT, color='cyan')
            Saxes.plot(Spro_mn[ipl,:], depthT, color='k')
            for ipro, Tpro in enumerate(TPRO_en):
            #Tpro = TPRO_en[ipro]
                #Tpri = TPRI_en[ipro]
                Taxes.plot(Tpro[ipl,:], depthT, color='gray', linewidth=0.2) 
                #Taxes.plot(Tpri[ipl,:], depthT, color='khaki', linewidth=0.2)
            for ipro, Spro in enumerate(SPRO_en):
                #Spro = SPRO_en[ipro]
                #Spri = SPRI_en[ipro]
                Saxes.plot(Spro[ipl,:], depthT, color='gray', linewidth=0.2) 
                #Saxes.plot(Spri[ipl,:], depthT, color='khaki', linewidth=0.2)
            Taxes.set_ylim([0, 200])                                                    
            Taxes.set_xlim([10,25])                                                    
            Taxes.invert_yaxis()   
            Taxes.set_title(tit+' '+'Temperature')                                      
            Saxes.set_ylim([0, 200])                                                    
            Saxes.set_xlim([30,40])                                                    
            Saxes.invert_yaxis()   
            Saxes.set_title(tit+' '+'Saliniity')                                      
            syear=str(year)
            Tfig.savefig('MNDprofiles/Tprofiles_'+tit+'_'+syear+'.png')
            Sfig.savefig('MNDprofiles/Sprofiles_'+tit+'_'+syear+'.png')
            plt.close(Tfig)
            plt.close(Sfig)

        ncfile='MNDprofiles/profile_'+syear+'.nc'  
        write_nc_grid.write_profiles([Tpro_gu, Spro_gu, Tpro_gd, Spro_gd, TPRO_arr, SPRO_arr], LONPTS, LATPTS, depthT, ['T_gu', 'S_gu', 'T_gd', 'S_gd', 'T_ens', 'S_ens'], ncfile)

        for ipt, PT in enumerate(PTS):
            file='MNDprofiles/enGIOPS.profile_'+TITLE[ipt]+'_'+syear+'.txt'
            write_profile(LITLE[ipt], PT, depthT, TPRO_arr[ipt,:,:], SPRO_arr[ipt,:,:], file)
            file='MNDprofiles/GIOPS_gu.profile_'+TITLE[ipt]+'_'+syear+'.txt'
            write_profile(LITLE[ipt], PT, depthT, Tpro_gu[ipt,:], Spro_gu[ipt,:], file)
            file='MNDprofiles/GIOPS_gd.profile_'+TITLE[ipt]+'_'+syear+'.txt'
            write_profile(LITLE[ipt], PT, depthT, Tpro_gd[ipt,:], Spro_gd[ipt,:], file)
        
