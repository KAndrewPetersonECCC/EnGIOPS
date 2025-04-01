#!/bin/bash -x
#ord_soumet /home/dpe000/EnGIOPS/jobscripts/produce_obs_scatter_mp.sh -cpus 80 -cm 180000M -t 21600 -shell=/bin/bash

WDIR=/home/dpe000/EnGIOPS
cd ${WDIR}

export MPLBACKEND=agg
source jobscripts/prepython.sh

python << EOD

#from importlib import reload
import sys
import os
sys.path.insert(0, '/home/dpe000/EnGIOPS/python')
import produce_scatter_obs

startdate=20200101
finaldate=20221231
produce_scatter_obs.scatter_obs_for_range_mp(startdate, finaldate)
EOD
