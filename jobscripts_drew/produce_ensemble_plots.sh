#!/bin/bash
#ord_soumet /fs/homeu2/eccc/mrd/ords/rpnenv/dpe000/EnGIOPS/jobscripts_drew/produce_ensemble_plots.sh -cpus 1 -mpi -cm 64000M -t 10800 -shell=/bin/bash
#bash /fs/homeu2/eccc/mrd/ords/rpnenv/dpe000/EnGIOPS/jobscripts_drew/produce_ensemble_plots.sh

TDIR=/fs/homeu2/eccc/mrd/ords/rpnenv/dpe000/EnGIOPS
DDIR=/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives
date=20201104
PYENSB="[]"
ENSB=(0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20)

## GET arguments
for i in "$@"
do
case $i in
    -d=*|--date=*)
    DATE="${i#*=}"
    shift # past argument=value
    ;;
    -x=*|--expt=*)
    EXPT="${i#*=}"
    shift # past argument=value
    ;;
    -p=*|--plot=*)
    PLOT="${i#*=}"
    shift # past argument=value
    ;;
    -e=*|--ensemble=*)
    ENSB=(${i#*=})
    shift # past argument=value
    ;;
esac
done
if [[ -z ${DATE} ]]; then
   echo "DATE required"
   echo ${USAGE}
   exit 99
fi
if [[ ${#DATE} -lt 8 ]] ; then
   echo "DATE CCYYMMDD required"
   echo $USAGE
   exit 99
fi
DATE=${DATE:0:8}

if [[ -z ${EXPT} ]]; then
   echo "EXPT required"
   echo ${USAGE}
   exit 99
fi
if [[ -z ${PLOT} ]]; then
   echo "PLOT required"
   echo ${USAGE}
   exit 99
fi
if [[ ! -z ${ENSB} ]] ; then 
   PYENSB="["
   for ENS in ${ENSB[*]} ; do
       PYENSB="${PYENSB} ${ENS},"
   done
   PYENSB="${PYENSB/%,/ ]}"
fi

cd ${TDIR}
if [[ $? -ne 0 ]] ; then 
   echo "Cannot reach ${TDIR}"
   exit 99
fi

mkdir /fs/site5/eccc/mrd/rpnenv/dpe000/EnGIOPS/${PLOT}
ln -s /fs/site5/eccc/mrd/rpnenv/dpe000/EnGIOPS/${PLOT} .
PJOB=${TDIR}/JOBS/produce_ensemble_plots.${EXPT}.${PLOT}.${DATE}.py
BJOB=${TDIR}/JOBS/produce_ensemble_plots.${EXPT}.${PLOT}.${DATE}.sh
SJOB="ord_soumet ${BJOB} -cpus 1 -mpi -cm 64000M -t 10800 -shell=/bin/bash"

cat > ${BJOB} << EOB
#!/bin/bash
#${SJOB}

. ssmuse-sh -x hpci/opt/hpcarchive-latest
cd ${DDIR}
if [[ \$? -eq 0 ]] ; then 
    for E in ${ENSB[*]} ; do 
        EEXPT=${EXPT}\${E}
	if [[ \${E} == 0 && ${EXPT} != GIOPS_E ]]; then
	    EEXPT=GIOPS_S0
	fi
	if [[ ! -e \${EEXPT}/SAM2/${DATE}/DIA/ORCA025-CMC-ANAL_1d_grid_T_${DATE}00.nc || ! -e \${EEXPT}/SAM2/${DATE}/DIA/ORCA025-CMC-ANAL_1d_grid_U_${DATE}00.nc || ! -e \${EEXPT}/SAM2/${DATE}/DIA/ORCA025-CMC-ANAL_1d_grid_V_${DATE}00.nc || ! -e \${EEXPT}/SAM2/${DATE}/DIA/ORCA025-CMC-ANAL_1h_grid_T_2D_${DATE}00.nc ]] ; then
	    echo "RETRIEVE FILES: ORCA025-CMC-ANAL_1d_grid_[UVT]_${DATE}00.nc ORCA025-CMC-ANAL_1h_grid_T_2D_${DATE}00.nc"
	    echo "hpcarchive -p rpnenv_5ans -xc \${EEXPT}.${DATE} -f \${EEXPT}/SAM2/${DATE}/DIA/ORCA025-CMC-ANAL_1[dh]_grid_?_ -r ."
            hpcarchive -p rpnenv_5ans -xc \${EEXPT}.${DATE} -f \${EEXPT}/SAM2/${DATE}/DIA/ORCA025-CMC-ANAL_1[dh]_grid_?_ -r . 
       else
           echo "Files exist.  CONTINUE"
       fi
    done
fi

cd ${TDIR}
export MPLBACKEND=agg

source  /fs/homeu2/eccc/mrd/ords/rpnenv/dpe000/EnGIOPS/jobscripts_drew/prepython.sh
#source /home/dpe000/GEOPS/jobscripts/preconda.sh
#source activate metcarto
python ${PJOB}
exit 0
EOB

cat > $PJOB << EOP
import sys
sys.path.insert(0, '/home/dpe000/EnGIOPS/python_drew')
import matplotlib as mpl
mpl.use('Agg')
import numpy as np
import datetime

import read_dia
import datadatefile

datestr='${DATE}'
ensembles=${PYENSB}
date=datadatefile.convert_strint_date(datestr)
read_dia.plot_date(date, ens_pre='${EXPT}', pdir='${PLOT}',ensembles=ensembles)

EOP

${SJOB}
