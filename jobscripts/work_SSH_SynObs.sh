#!/bin/bash -x
#ord_soumet /home/dpe000/EnGIOPS/jobscripts/work_SSH_SynObs.sh -cpus 80 -cm 64000M -t 21600 -shell=/bin/bash

WDIR=/home/dpe000/EnGIOPS
cd ${WDIR}

export MPLBACKEND=agg
source jobscripts/prepython.sh

python << EOD
#from importlib import reload
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
import read_DF_IS

dates = rank_histogram.create_dates(20200101, 20230104, 7)
expts=('CNTLV2', 'NoAltV2', 'NoArgoV2')
labels=('CNTLV2', 'NoAltV2', 'NoArgoV2')
enss=(0, 0, 0)
ddir=[read_DF_VP.get_mdir(5,user='dpe000')]*3
ddir=['/fs/site5/eccc/cmd/e/saqu500/maestro_archives/SynObs']*3
outdir=[expt for expt in expts]
outdir=['CNTLV2', 'NoAltV2', 'NoArgoV2']
dsite5='/fs/site5/eccc/mrd/rpnenv/dpe000/EnGIOPS/'
read_DF_IS.produce_stats_plot( dates, expts, enss, labels, outdir=outdir, ddir=ddir, mp_date=True, outdirpre=dsite5+'ECMP_', NP=20)
EOD
