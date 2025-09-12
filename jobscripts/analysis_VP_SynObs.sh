#!/bin/bash -x
#ord_soumet /home/dpe000/EnGIOPS/jobscripts/analysis_VP_SynObs.sh -cpus 80 -cm 180000M -t 21600 -shell=/bin/bash

WDIR=/home/dpe000/EnGIOPS
cd ${WDIR}

export MPLBACKEND=agg
source jobscripts/prepython.sh

python << EOD

from importlib import reload
import sys
import os
sys.path.insert(0, '/home/dpe000/EnGIOPS/python')
import matplotlib as mpl
import matplotlib.pyplot as plt
mpl.use('Agg')
import numpy as np
import datetime
import read_DF_VP
import rank_histogram

#dates = rank_histogram.create_dates(20200101, 20230104, 7)
dates = rank_histogram.create_dates(20200101, 20200129, 7)

expts=('CNTLV2', 'NoArgoV2')

nexpt=len(expts)
labels=expts
outdir=[str(nexpt)+'_'+expt for expt in expts]
enss=tuple([0]*nexpt)
#ddir=[read_DF_VP.get_mdir(5,user='saqu500', grp='cmd', rpn='e')+'/SynObs']*nexpt
datadir='/fs/site5/eccc/cmd/e/saqu500/maestro_archives/SynObs'
ddir=[datadir]*nexpt
# default mp_read=True only makes sense for ensemble experiments.
# mp_date option might be good.
#read_DF_VP.produce_stats_plot( dates, expts, enss, labels, outdir=outdir,ddir=ddir, mp_date=True)
#read_DF_VP.produce_stats_plot( dates, expts, enss, labels, outdir=outdir, ddir=ddir, mp_date=True, outdirpre='vFTT_', noensstat=True, nostdstat=True, subset=0)
read_DF_VP.produce_stats_plot( dates, expts, enss, labels, outdir=outdir, ddir=ddir, mp_date=False, outdirpre='vFST_', noensstat=True, nostdstat=True, subset=0)
EOD
