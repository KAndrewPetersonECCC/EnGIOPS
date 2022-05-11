!/bin/bash
#ord_soumet /fs/homeu1/eccc/mrd/ords/rpnenv/dpe000/EnGIOPS/jobscripts/diagnostic_DSola.sh -cpus 1 -mpi -cm 8000M -t 21600 -shell=/bin/bash
#bash /fs/homeu1/eccc/mrd/ords/rpnenv/dpe000/EnGIOPS/jobscripts/diagnostic_DSola.sh

export MPLBACKEND=agg

cd /fs/homeu1/eccc/mrd/ords/rpnenv/dpe000/EnGIOPS
source jobscripts/preconda.sh
source activate metpyy

output_reference_path="/fs/site3/eccc/mrd/rpnenv/dpe000/SAM2_diags/GDPS"
start_date=20190320
final_date=20201230
#final_date=20200401
#ensemble=(0 1 2 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20)
ensemble=(0 1 3 4 5 6)
cycle_type="W"

for suite in GIOPS_T6 GIOPS_E6 GIOPS_S6 GIOPS_P6 GIOPS_Q6 GIOPS_T GIOPS_E; do

# Define all scripts arguments

ensemble=(0 1 3 4 5 6)
if [[ ${suite} == GIOPS_T6 ]]; then 
    suit0="GIOPS_T0"
    input_path="/fs/site3/eccc/mrd/rpnenv/dpe000/maestro_archives/GIOPS_T0/SAM2"
    replace="GIOPS_T"
    output_path="/fs/site3/eccc/mrd/rpnenv/dpe000/SAM2_diags/GIOPS_T6"
fi
if [[ ${suite} == GIOPS_E6 ]]; then 
    suit0="GIOPS_E0"
    input_path="/fs/site3/eccc/mrd/rpnenv/dpe000/maestro_archives/GIOPS_E0/SAM2"
    replace="GIOPS_E"
    output_path="/fs/site3/eccc/mrd/rpnenv/dpe000/SAM2_diags/GIOPS_E6"
fi
if [[ ${suite} == GIOPS_S6 ]]; then 
    suit0="GIOPS_E0"
    input_path="/fs/site3/eccc/mrd/rpnenv/dpe000/maestro_archives/GIOPS_S0/SAM2"
    replace="GIOPS_S"
    output_path="/fs/site3/eccc/mrd/rpnenv/dpe000/SAM2_diags/GIOPS_S6"
fi
if [[ ${suite} == GIOPS_Q6 ]]; then 
    suit0="GIOPS_E0"
    input_path="/fs/site3/eccc/mrd/rpnenv/dpe000/maestro_archives/GIOPS_Q0/SAM2"
    replace="GIOPS_Q"
    output_path="/fs/site3/eccc/mrd/rpnenv/dpe000/SAM2_diags/GIOPS_Q6"
fi
if [[ ${suite} == GIOPS_T ]]; then 
    suit0="GIOPS_T0"
    input_path="/fs/site3/eccc/mrd/rpnenv/dpe000/maestro_archives/GIOPS_T0/SAM2"
    replace="GIOPS_T"
    output_path="/fs/site3/eccc/mrd/rpnenv/dpe000/SAM2_diags/GIOPS_T"
    ensemble=(0 1 2 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20)
fi
if [[ ${suite} == GIOPS_E ]]; then 
    suit0="GIOPS_E0"
    input_path="/fs/site3/eccc/mrd/rpnenv/dpe000/maestro_archives/GIOPS_E0/SAM2"
    replace="GIOPS_E"
    output_path="/fs/site3/eccc/mrd/rpnenv/dpe000/SAM2_diags/GIOPS_E"
    ensemble=(0 1 2 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20)
fi

BJOB=JOBS/diagnositcs_DSola_${suite}.sh
SJOB="ord_soumet ${BJOB} -cpus 1 -mpi -cm 8000M -t 21600 -shell=/bin/bash"
cat > ${BJOB} << EOD
export MPLBACKEND=agg

cd /fs/homeu1/eccc/mrd/ords/rpnenv/dpe000/EnGIOPS
source jobscripts/preconda.sh
source activate metpyy
   echo "Running GIOPS_ola_plot_DS_ens.py for ${suite}"
   python python/GIOPS_ola_plot_DS_ens.py  \
       --suite ${suite} \
       --input_dir ${input_path} \
       --output_dir ${output_path}/ola_diag \
       --start_date ${start_date} \
       --final_date ${final_date} \
       --stype ${cycle_type} \
       --replace ${replace} \
       --ensemble ${ensemble[*]}

   echo "GIOPS_ola_plot_DS.py for ${suite} finished."

EOD
${SJOB}

done
