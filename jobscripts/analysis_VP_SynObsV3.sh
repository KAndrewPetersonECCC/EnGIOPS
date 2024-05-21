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
labe = ['CNTL',   'NoArgo',   'NoMoor',   'HalfArgo',   'Oper', 'CNTL',   'NoSST',   'SSTonly', 'NoAlt',   'NoInsitu',   'Free']

oria = ['CNTLV2', 'NoArgoV2', 'NoMoorV2', 'HalfArgoV2', 'Oper', 'Free']
laba = ['CNTL',   'NoArgo',   'NoMoor',   'HalfArgo',   'Oper', 'Free']
orib = ['CNTLV2', 'NoSSTV2', 'SSTonlyV3', 'NoAltV2', 'NoInsituV3', 'Free']
labb = ['CNTL',   'NoSST',   'SSTonly',   'NoAlt',   'NoInsitu',   'Free']
oric = ['CNTLV2', 'NoArgoV2', 'NoMoorV2', 'HalfArgoV2']
labc = ['CNTL',   'NoArgo',   'NoMoor',   'HalfArgo']
orid = ['CNTLV2', 'NoSSTV2', 'SSTonlyV3', 'NoAltV2', 'NoInsituV3']
labd = ['CNTL',   'NoSST',   'SSTonly',   'NoAlt',   'NoInsitu']
orie = ['CNTLV2', 'NoArgoV2', 'HalfArgoV2', 'NoMoorV2', 'NoInsituV3', 'CNTLV2_NoBIAS_correction']
labe = ['CNTL',   'NoArgo',   'HalfArgo',   'NoMoor',   'NoInsitu', 'NoBias']


exptss=[orig, oria, orib, oric, orid, orie]
labess=[labe, laba, labb, labc, labd, labe]
dirlabel=['v3Z_', 'v3A_', 'v3B_', 'z3A_', 'z3B_', 'v3C']
datess=[datet, datet, datet, datet, datet, datet]

sub_exptss = exptss.copy()
sub_exptss = [orie, oric, orid, oria, orib, orig]
for iexpts, expts  in enumerate(sub_exptss):
    jexpts = exptss.index(expts)
    print('jexpts', jexpts)
    subset=0
    if ( expts == oric ): subset=23
    if ( expts == orid ): subset=23
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
