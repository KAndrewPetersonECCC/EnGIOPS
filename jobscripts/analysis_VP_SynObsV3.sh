#!/bin/bash -x
#ord_soumet /home/dpe000/EnGIOPS/jobscripts/analysis_VP_SynObsV3.sh -cpus 80 -cm 180000M -t 21600 -shell=/bin/bash

WDIR=/home/dpe000/EnGIOPS
cd ${WDIR}

export MPLBACKEND=agg
source jobscripts/prepython.sh

python << EOD

from importlib import reload
import sys
import os
sys.path.insert(0, '/home/dpe000/EnGIOPS/python')
import traceback
import matplotlib as mpl
mpl.use('Agg')
import numpy as np
import datetime
import read_DF_VP
import rank_histogram

datep = rank_histogram.create_dates(20200101, 20211201, 7)
datet = rank_histogram.create_dates(20200101, 20230104, 7)

orig = ['CNTLV2', 'NoArgoV2', 'NoMoorV2', 'HalfArgoV2', 'Oper', 'CNTLV2', 'NoSSTV2', 'SSTonly', 'NoAltV2', 'NoInsituV3', 'Free']

oria = ['CNTLV2', 'NoArgoV2', 'NoMoorV2', 'HalfArgoV2', 'Oper', 'Free']
orib = ['CNTLV2', 'NoSSTV2', 'SSTonlyV3', 'NoAltV2', 'NoInsituV3', 'Free']

oriaa = ['CNTLV2', 'NoArgoV2', 'NoAltV2', 'HalfArgoV2', 'Free']

exptss=[orig, oria, orib, oriaa]
dirlabel=['v3Z_', 'v3A_', 'v3B_', 'v3AA_']
datess=[datet, datet, datet, datet]

sub_exptss = exptss.copy()
sub_exptss = [orig, oria, orib, oriaa]
sub_exptss = [oria, orib, orig]
for iexpts, expts  in enumerate(sub_exptss):
    jexpts = exptss.index(expts)
    print('jexpts', jexpts)
    outdirpre=dirlabel[jexpts]
    dates=datess[jexpts]
    nexpt=len(expts)
    labels=expts
    outdir=[expt for expt in expts]
    enss=tuple([0]*nexpt)
    ## THIS IS NICE AND CONCISE
    datadir=read_DF_VP.get_mdir(5,user='saqu500', grp='cmd', rpn='e')+'/SynObs'
    ## BUT THIS IS SOO MUCH MORE USEFUL
    datadir='/fs/site5/eccc/cmd/e/saqu500/maestro_archives/SynObs'
    ddir=[datadir]*nexpt
    # default mp_read=True only makes sense for ensemble experiments.
    #mp_date option might be good.
    try:
        read_DF_VP.produce_stats_plot( dates, expts, enss, labels, outdir=outdir, ddir=ddir, mp_date=True, outdirpre=outdirpre,noensstat=True, nostdstat=True)
    except:
         print(traceback.print_exc())

EOD
