#!/bin/bash
#ord_soumet /fs/homeu1/eccc/mrd/ords/rpnenv/dpe000/EnGIOPS/jobscripts_drew/loop_dates.sh -cpus 1 -mpi -cm 64000M -t 10800 -shell=/bin/bash

#bash /fs/homeu1/eccc/mrd/ords/rpnenv/dpe000/EnGIOPS/jobscripts_drew/loop_dates.sh


TDIR=/fs/homeu1/eccc/mrd/ords/rpnenv/dpe000/EnGIOPS

command=/fs/homeu1/eccc/mrd/ords/rpnenv/dpe000/EnGIOPS/jobscripts_drew/produce_ensemble_plots.sh
date_start=20190313
date_final=20201230
date_sta21=20190313
date_fin21=20201230

date_start=20190605
date_final=20190925
date_sta21=20190313
date_fin21=20191225


export MPLBACKEND=agg
source /home/dpe000/GEOPS/jobscripts/preconda.sh
source activate metcarto

python << EOD
import sys
sys.path.insert(0, '/home/dpe000/EnGIOPS/python_drew')
import matplotlib as mpl
mpl.use('Agg')
import numpy as np
import datetime

import subprocess
import datadatefile
import read_dia

daterange=[${date_start}, ${date_final}]
expts = ['GIOPS_T', 'GIOPS_S', 'GIOPS_P', 'GIOPS_Q', 'GIOPS_E']
plots = ['TSIX', 'SSIX', 'PSIX', 'QSIX', 'ESIX']
expts=['GIOPS_T']
plots=['TSIX']
command=read_dia.get_COMMAND('RATIO')
ensemble=read_dia.get_ENSEMBLE(6)

for command in [read_dia.get_COMMAND('PLOTS'), read_dia.get_COMMAND('RATIO')]:
#for command in [read_dia.get_COMMAND('RATIO')]:
    read_dia.loop_dates_with_command(daterange, command=command, expts=expts, pdirs=plots, ensemble=ensemble)

daterange=[${date_sta21}, ${date_fin21}]
expts = ['GIOPS_T', 'GIOPS_E', 'GIOPS_S']
plots = ['TFIG', 'EFIG', 'SFIG']
expts = ['GIOPS_T']
plots = ['TFIG']
command=read_dia.get_COMMAND('RATIO')
ensemble=read_dia.get_ENSEMBLE(21)

for command in [read_dia.get_COMMAND('PLOTS'), read_dia.get_COMMAND('RATIO')]:
#for command in [read_dia.get_COMMAND('RATIO')]:
    read_dia.loop_dates_with_command(daterange, command=command, expts=expts, pdirs=plots, ensemble=ensemble)

EOD
