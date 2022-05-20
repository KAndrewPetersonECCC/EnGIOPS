#!/bin/bash
#ord_soumet plot_rank_histograph.sh -cpus 1 -mpi -cm 64000M -t 10800 -shell=/bin/bash

WDIR=/home/dpe000/EnGIOPS

export MPLBACKEND=agg
source /home/dpe000/GEOPS/jobscripts/preconda.sh
source activate metcarto

python < EOD
import sys
sys.path.insert(0, '/home/dpe000/EnGIOPS/python_drew')
import matplotlib as mpl
import numpy as np
import datetime
import rank_histogram

plot_rank_over_range('TFIG/', 'GIOPS_T', [20200102,  20201230], type='DS')


EOD
