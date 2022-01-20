#!/bin/bash
#ord_soumet /fs/homeu1/eccc/mrd/ords/rpnenv/dpe000/EnGIOPS/jobscripts_drew/post_process_plots.sh -cpus 1 -mpi -cm 32000M -t 10800 -shell=/bin/bash
#bash /fs/homeu1/eccc/mrd/ords/rpnenv/dpe000/EnGIOPS/jobscripts_drew/post_process_plots.sh


TDIR=/fs/homeu1/eccc/mrd/ords/rpnenv/dpe000/EnGIOPS
PDIR=${TDIR}/EFIG

cd ${TDIR}

for file in ${PDIR}/T_std_????????.png ; do 
  bile=$(basename ${file})
  date=$(echo ${bile} | cut -c 7-14)

  montage ${PDIR}/T_std_${date}.png  ${PDIR}/TX_std_${date}.png  ${PDIR}/TY_std_${date}.png -tile 1x3 -geometry 400x200\>+10+10 ${PDIR}/TA_std_${date}.png

  montage ${PDIR}/S_std_${date}.png  ${PDIR}/SX_std_${date}.png  ${PDIR}/SY_std_${date}.png -tile 1x3 -geometry 400x200\>+10+10 ${PDIR}/SA_std_${date}.png

  montage U_std_${date}.png  UX_std_${date}.png  UY_std_${date}.png HX_std_${date}.png -tile 1x4 -geometry 400x200\>+10+10 UA_std_${date}.png

done

for FD in TA SA UA H; do
    convert -delay 50 ${PDIR}/${FD}_std_????????.png ${PDIR}/${FD}_std.gif
done
mv ${PDIR}/H_std.gif ${PDIR}/HA_std.gif
 
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

import read_dia
read_dia.plot_timeseries(pdir=${PDIR})
plot_timeseries(pdir='/home/dpe000/EnGIOPS/EFIG')

EOD
