#!/bin/bash -x
#ord_soumet /home/dpe000/EnGIOPS/jobscripts/analysis_VP_SynObsV2.sh -cpus 80 -cm 180000M -t 21600 -shell=/bin/bash

WDIR=/home/dpe000/EnGIOPS
cd ${WDIR}

export MPLBACKEND=agg
source jobscripts/prepython.sh

python << EOD

#from importlib import reload
import sys
import os
sys.path.insert(0, '/home/dpe000/EnGIOPS/python')
import traceback
import matplotlib as mpl
import matplotlib.pyplot as pltl
mpl.use('Agg')
import numpy as np
import datetime
import read_DF_VP
import rank_histogram

dates = rank_histogram.create_dates(20200101, 20210714, 7)

orig = ['CNTL', 'NoArgo', 'NoAlt', 'HalfArgo', 'NoSST', 'CNTL', 'NoInsitu', 'SSTonly', 'NoMoor', 'Oper', 'Free']
oria = ['CNTL', 'NoArgo', 'NoAlt', 'HalfArgo', 'NoInsitu', 'Free']
orib = ['CNTL', 'NoSST', 'SSTonly', 'NoMoor', 'Oper', 'Free']
good = ['Oper', 'Free']
redo = [ expt for expt in orig if expt not in good]
reda = [ expt for expt in oria if expt not in good]
redb = [ expt for expt in orib if expt not in good]
alV2 = [ expt+'V2' for expt in redo]+good
aV2a = [ expt+'V2' for expt in reda]+['Free']
aV2b = [ expt+'V2' for expt in redb]+good

compare_V2 = [ (expt+'V2', expt) for expt in redo ]
compare_CN = [ ('CNTLV2', expt) for expt in alV2 if expt not in ['CNTL'] ] 
compare_CO = [ ('CNTL', expt) for expt in orig if expt not in ['CNTL'] ]
dirlabel=['v2_', 'v2a_', 'v2b_', 'v0_', 'v0a_', 'v0b_', 'v2v0_']
for iexpts, expts  in enumerate([alV2, aV2a, aV2b, orig, oria, orib]+compare_V2):
    if ( iexpts < 6 ): 
       outdirpre=dirlabel[iexpts]
    else:
       outdirpre=dirlabel[-1]
    nexpt=len(expts)
    labels=expts
    outdir=[expt for expt in expts]
    enss=tuple([0]*nexpt)
    ddir=[read_DF_VP.get_mdir(5,user='saqu500', grp='cmd', rpn='e')+'/SynObs']*nexpt
    # default mp_read=True only makes sense for ensemble experiments.
    #mp_date option might be good.
    try:
        read_DF_VP.produce_stats_plot( dates, expts, enss, labels, outdir=outdir, ddir=ddir, mp_date=True, outdirpre=outdirpre)
    except:
         print(traceback.print_exc())

EOD
