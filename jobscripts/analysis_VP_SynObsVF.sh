#!/bin/bash -x
#ord_soumet /home/dpe000/EnGIOPS/jobscripts/analysis_VP_SynObsVF.sh -cpus 80 -cm 180000M -t 21600 -shell=/bin/bash

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
mpl.use('Agg')
import numpy as np
import datetime
import read_DF_VP
import rank_histogram

datet = rank_histogram.create_dates(20200101, 20230104, 7)

oria = ['CNTLV2', 'HalfArgoV2', 'NoArgoV2', 'NoInsituV3', 'NoAlt',        'Free']
laba = ['CONTROL','Half Argo',  'No Argo',  'No InSitu',  'No Altimeter', 'Free']
orib = ['CNTLV2', 'HalfArgoV2', 'NoArgoV2', 'NoInsituV3', 'SSTonlyV3', 'Free']
labb = ['CONTROL','Half Argo',  'No Argo',  'No InSitu',  'SST only',  'Free']
oric = ['CNTLV2', 'HalfArgoV2', 'NoArgoV2', 'NoInsituV3', 'NoMoorV2',    'Free']
labc = ['CONTROL','Half Argo',  'No Argo',  'No InSitu',  'No Moorings', 'Free']
orid = ['Free', 'NoArgoV2', 'NoMoorV2', 'NoInsituV3', 'HalfArgoV2', 'CNTLV2']
labd = ['Free', 'No Argo', 'No Moorings', 'NoInSitu', 'HalfArgoV2', 'CNTL'] 
orie = ['NoInsituV3', 'NoArgoV2', 'NoMoorV2']
labe = ['No InSitu',  'No Argo',  'No Moorings'] 
exptss=[oria, orib, oric, orid, orie]
labess=[laba, labb, labc, labd, labe]
dirlabel=['vFA_', 'vFB_', 'vFC_', 'vFD_', 'vFE_']
datess=[datet, datet, datet, datet, datet, datet]

sub_exptss = exptss.copy()
sub_exptss = [orid, orie, oria, orib, oric]
for iexpts, expts  in enumerate(sub_exptss):
    jexpts = exptss.index(expts)
    print('jexpts', jexpts)
    subset=0
    outdirpre=dirlabel[jexpts]
    dates=datess[jexpts]
    nexpt=len(expts)
    labels=labess[jexpts]
    outdir=[expt for expt in expts]
    enss=tuple([0]*nexpt)
    ## THIS IS NICE AND CONCISE
    datadir=read_DF_VP.get_mdir(5,user='saqu500', grp='cmd', rpn='e')+'/SynObs'
    ## BUT THIS IS SOO MUCH MORE USEFUL
    datadir='/fs/site5/eccc/cmd/e/saqu500/maestro_archives/SynObs'
    ddir=[datadir]*nexpt
    if ( 'NoBias' in labels ): ddir[labels.index('NoBias')]='/home/kch001/data/ppp5/maestro_archives/SynObs'
    # default mp_read=True only makes sense for ensemble experiments.
    #mp_date option might be good.
    try:
         read_DF_VP.produce_stats_plot( dates, expts, enss, labels, outdir=outdir, ddir=ddir, mp_date=True, outdirpre=outdirpre, noensstat=True, nostdstat=True, subset=subset)
         print("SUCCESS PRODUCE STATS")
    except:
         print(traceback.print_exc())
         print("FAILURE PRODUCE STATS")

EOD
