#!/bin/bash -x
#ord_soumet /home/dpe000/EnGIOPS/jobscripts/SynObsSound.sh -cpus 80 -cm 180000M -t 21600 -shell=/bin/bash
#bash /home/dpe000/EnGIOPS/jobscripts/SynObsSound.sh

WDIR=/home/dpe000/EnGIOPS
cd ${WDIR}

BJOB=/home/dpe000/EnGIOPS/JOBS/SO_sound.sh
PJOB=/home/dpe000/EnGIOPS/JOBS/SO_sound.py
OJOB=/home/dpe000/EnGIOPS/python/find_cspeed_tmp.py
SJOB="ord_soumet ${BJOB} -cpus 80 -cm 180000M -t 21600 -shell=/bin/bash"

cat > ${BJOB} << EOB

WDIR=/home/dpe000/EnGIOPS
cd ${WDIR}

export MPLBACKEND=agg
source jobscripts/prepython.sh
python3 ${PJOB}
EOB


cat > ${PJOB} << EOP
#from importlib import reload
import sys
import os
import datetime
import numpy as np

sys.path.insert(0, '/home/dpe000/EnGIOPS/python')
import find_cspeed_maxmin
import more_cspeed
import cplot
import load_cmaps
import zero_levs

cmap_anom, cmap_full = load_cmaps.load1()

levelo = np.arange(0, 0.31, 0.05)
levels, ticks = zero_levs.zero_levs(0.1, 0.01)


start=[2020,1]
final=[2020,12]
trange=f"{start[0]}/{start[1]:02} -- {final[0]}/{final[1]:02}"
orange=f"{start[0]}{start[1]:02}-{final[0]}{final[1]:02}"

print("RESULTS for INST:  CNTL, NoArgo, NoAlt -- smaller better")
BRSC_slist = []
TorF_slist = []
expts = ['CNTL', 'NoArgo', 'NoAlt']
bss_ref='CNTL'

for inst in ['FOAM', 'MOVE-G3', 'GIOPS', 'ORAS6FP']:
    BRSC_list= []
    TorF_list = []
    ddir=more_cspeed.ddirS
    if ( inst == 'GIOPS' ): ddir=more_cspeed.odird
    if ( inst == 'MOVE-G3' ): ddir=more_cspeed.ddirS1
    print(inst, ddir)
    #if ( inst == 'JCOPE_FGO01' ): expts = ['CNTL']
    for expt in expts:
        BRSC, MISS, ALARM, (TorF_OBS, TorF_EXP), (LONA, LATA) = more_cspeed.do_cspeed_expt(inst, expt, start, final, ref="Ref", ddir=ddir, odir=more_cspeed.odird)
        BRSC_list.append(BRSC)
        TorF_list.append((TorF_OBS, TorF_EXP))
    print(inst, 'BRSC-EXPT', BRSC_list)
    #print('shape', [ [ np.shape(TorF_tuple[0]), np.shape(TorF_tuple[1]) ] for TorF_tuple in TorF_list])
    BRSC_ref = BRSC_list[0]
    print("DIFF", [BRSC - BRSC_ref for BRSC in BRSC_list])
    BRSC_slist.append(BRSC_list)
    TorF_slist.append(TorF_list)
    
TorF_xlist = []
TorF_olist = []
BRSC_xlist = []
BRSC_blist = []
brsc_xlist = []

for iexpt, expt in enumerate(expts):
    TorF_expt = np.array([ TorF_list[iexpt][1] for TorF_list in TorF_slist ])
    TorF_eobs = np.array([ TorF_list[iexpt][0] for TorF_list in TorF_slist ])
    print('SHAPE', np.shape(TorF_expt), np.shape(TorF_eobs))
    Prob_expt = np.mean(TorF_expt, axis=0)
    Ones_expt = np.mean(TorF_eobs, axis=0)
    print('SHAPE', np.shape(Prob_expt), np.shape(Ones_expt))
    BRSC_expt = np.square( Prob_expt - Ones_expt )
    TorF_xlist.append(TorF_expt)
    TorF_olist.append(TorF_eobs)
    BRSC_xlist.append(BRSC_expt)
    
    brsc_expt = np.mean(BRSC_expt)
    brsc_xlist.append(brsc_expt)
    bss_expt = ( brsc_xlist[0] - brsc_expt ) / brsc_xlist[0]
    
    print(expt,': ENS. BRSC', brsc_expt)
    print(expt,': ENS. BSS', bss_expt)

    grd_lon, grd_lat, binned_brier = cplot.binfld(LONA, LATA, BRSC_expt, ddeg=10.0)
    BRSC_blist.append(binned_brier)
    outfile='CSPEED/SynObsIC/BRS_'+'MME'+'_'+expt+'_'+'Ref'
    title='Brier Score for '+expt+' for '+trange+' ( BS='+str(brsc_expt)+' )'
    cplot.pcolormesh( grd_lon, grd_lat, binned_brier, levels=levelo, ticks=levelo, cmap=cmap_full, project='PlateCarree', outfile=outfile, title=title, obar='horizontal', add_gridlines=True)
    outfile='CSPEED/SynObsIC/BSS_'+'MME'+'_'+expt+'_'+'Ref'
    title='Brier Score CNTL - '+expt+' for '+trange+' ( BSS='+str(bss_expt)+' )'
    cplot.pcolormesh( grd_lon, grd_lat, BRSC_blist[0]-binned_brier, levels=levels, ticks=ticks, cmap=cmap_anom, project='PlateCarree', outfile=outfile, title=title, obar='horizontal', add_gridlines=True)

    
   





#FOAM [0.11815689395949412, 0.11798001238171045, 0.11845169658913357]
#DIFF [0.0, -0.00017688157778367186, 0.0002948026296394485]
#MOVE-G3 [0.10067509802187435, 0.11010878217033696, 0.09982017039591994]
#DIFF [0.0, 0.009433684148462601, -0.0008549276259544186]
#GIOPS [0.10559830193685328, 0.11836325580024173, 0.10671855192948321]
#DIFF [0.0, 0.012764953863388454, 0.0011202499926299264]

## EN4 results
## CNTL, NoArgo, NoAlt
## 0.1398,  0.1574, 0.1439
## 0.0, 0.0176, 0.0041]                                                                                                                                                               

expts=['CNTL', 'NoArgo', 'NoAlt', 'HalfArgo', 'NoInsitu', 'NoMoor', 'NoSST', 'SSTonly', 'Free']
refs=['Ref', 'Asm']
inst='GIOPS'
ddir=more_cspeed.odird
start=[2020,1]
final=[2022,12]

##for expt in expts:
for expt in []:
    for ref in refs:
        BRSC, MISS, ALARM = more_cspeed.do_cspeed_expt(inst, expt, start, final, ref=ref, ddir=ddir, odir=more_cspeed.odird)
        print(ref, expt, BRSC, MISS, ALARM)
        
                    
EOP

${SJOB}
