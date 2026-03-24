#!/bin/bash
#bash $THIS -d=date

for i in "$@"
do
case $i in 
    -d=*|--date=*)
    date="${i#*=}"
    shift # past argument=value
    ;;
esac
done

if [[ -z ${date} ]] ; then 
   echo "NO DATE"
   echo ${date}
   exit 99
fi
if [[ ${#date} -ne 8 ]] ; then 
   echo "WRONG DATE"
   echo ${date}
   echo CCYYMMDD
   exit 99
fi

dat1=$(date --date "${date} - 1 day" +%Y%m%d)
echo DATE:  ${date} ${dat1}

dest=/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/GEPS_STOT_restarts/gridpt/anal/

mkdir -p ${dest}/oce ${dest}/ice

rdir=/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives
adir=/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_hpcarchives

for E in 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20; do 
  typeset ENS=$(printf "%04d" ${E})
  file=${rdir}/GIOPS_T${E}/SAM2/${date}/RESTART_ANAL/ORCA025-CMC-ANAL_00001008_restart_oce_${dat1}.nc
  aile=${adir}/GIOPS_T${E}/SAM2/${date}/RESTART_ANAL/ORCA025-CMC-ANAL_00001008_restart_oce_${dat1}.nc
  if [[ -e ${file} && -e ${aile} ]] ; then diff ${file} ${aile} ; fi
  if [[ ! -e ${file} ]] ; then 
    mkdir -p ${rdir}/GIOPS_T${E}/SAM2/${date}/RESTART_ANAL
    cp ${aile} ${rdir}/GIOPS_T${E}/SAM2/${date}/RESTART_ANAL/
  fi
  if [[ -e ${file} ]] ; then ln -sf ${file} ${dest}/oce/${date}00_000_${ENS}.nc ; fi

  file=${rdir}/GIOPS_T${E}/SAM2/${date}/CICE/${date}00_000_anal
  aile=${adir}/GIOPS_T${E}/SAM2/${date}/CICE/${date}00_000_anal
  if [[ -e ${file} && -e ${aile} ]] ; then diff ${file} ${aile} ; fi
  if [[ ! -e ${file} ]] ; then 
    mkdir -p ${rdir}/GIOPS_T${E}/SAM2/${date}/CICE
    cp ${aile} ${rdir}/GIOPS_T${E}/SAM2/${date}/CICE/
  fi
  if [[ -e ${file} ]] ; then ln -sf ${file} ${dest}/ice/${date}00_000_${ENS}_anal ; fi

done

NOCE=$(ls -l ${dest}/oce/${date}00_000_????.nc | wc -l)
NICE=$(ls -l ${dest}/ice/${date}00_000_????_anal | wc -l)

if [[ $NOCE -eq 21 && ${NICE} -eq 21 ]] ; then
    echo "SUCCESS LINKING ALL MEMBERS ${NOCE}/${NICE}"
else
    echo "FAILURE LINKING ALL MEMBERS: ${NOCE}/${NICE}"
fi
