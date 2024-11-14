#!/bin/bash -x
#ord_soumet /home/dpe000/EnGIOPS/jobscripts/produce_obs_scatter.sh -cpus 80 -cm 180000M -t 21600 -shell=/bin/bash

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

import multiprocessing
from functools import partial
import itertools

years=[2020, 2021, 2022]
nproc=len(years)
loop_pool = multiprocessing.Pool(nproc)
izip = list(zip(years))

None_list = loop_pool.starmap(produce_scatter_obs.scatter_obs_for_year, izip)
loop_pool.close()
loop_pool.join()
EOD
