#!/bin/bash
#ord_soumet /home/dpe000/EnGIOPS/jobscripts_drew/plot_scatter.sh -cpus 1 -mpi -cm 64000M -t 10800 -shell=/bin/bash

WDIR=/home/dpe000/EnGIOPS
cd ${WDIR}

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
import rank_histogram

rank_histogram.plot_scatter_in_range('EFIG/','GIOPS_E', [20201202, 20201230])

EOD
