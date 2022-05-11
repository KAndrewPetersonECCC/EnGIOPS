#!/bin/bash
#ord_soumet /fs/homeu1/eccc/mrd/ords/rpnenv/dpe000/EnGIOPS/jobscripts/diagnostics_ens.sh -cpus 1 -mpi -cm 8000M -t 21600 -shell=/bin/bash

export MPLBACKEND=agg

# Define all scripts arguments
suite="GIOPS_TX"
suit0="GIOPS_T0"
reference_suite="GIOPS_GDPS"
input_path="/fs/site3/eccc/mrd/rpnenv/dpe000/maestro_archives/GIOPS_P0/SAM2"
replace="GIOPS_T"
input_reference_path="/home/kch001/data_hall3/maestro_archives/GX330_CONTROLE/SAM2"
output_path="/fs/site3/eccc/mrd/rpnenv/dpe000/SAM2_diags/GIOPS_P0"

output_reference_path="/fs/site3/eccc/mrd/rpnenv/dpe000/SAM2_diags/GDPS"
start_date=20190320
#final_date=20190424
#start_date=20201202
final_date=20201230
#final_date=20200401
ensemble=(0 1 2 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20)
#ensemble=(0 1 3 4 5 6)
cycle_type="W"

run_IS_DS_dia=T
run_VP_dia=T
run_DS_ola=T
run_DS_ola_ref=T
run_IS_ola=T
run_IS_ola_ref=T
run_VP_ola=T
run_VP_ola_ref=T

cd /fs/homeu1/eccc/mrd/ords/rpnenv/dpe000/EnGIOPS
source jobscripts/preconda.sh
source activate metpyy

if [ "${run_IS_DS_dia}" = "T" ]; then
   echo "Running GIOPS_IS_DS_dia_general_plot.py"
   python python/GIOPS_IS_DS_dia_general_plot.py  \
       --suite ${suit0} \
       --ref_suite ${reference_suite} \
       --path ${input_path} \
       --ref_path ${input_reference_path} \
       --output_path ${output_path} \
       --start_date ${start_date} \
       --final_date ${final_date} \
       --stype ${cycle_type} \

   echo "GIOPS_IS_DS_dia_general_plot.py finished"

   echo "Running GIOPS_IS_DS_dia_general_plot_ens.py"
   python python/GIOPS_IS_DS_dia_general_plot_ens.py  \
       --suite ${suite} \
       --ref_suite ${reference_suite} \
       --path ${input_path} \
       --replace ${replace} \
       --ref_path ${input_reference_path} \
       --output_path ${output_path} \
       --start_date ${start_date} \
       --final_date ${final_date} \
       --stype ${cycle_type} \
       --ensemble ${ensemble[*]}

   echo "GIOPS_IS_DS_dia_general_plot_ens.py finished"
   
 fi

if [ "${run_VP_dia}" = "T" ]; then

   python python/GIOPS_VP_dia_general_plot_v3.py  \
       --suite ${suit0} \
       --ref_suite ${reference_suite} \
       --path ${input_path}  \
       --ref_path ${input_reference_path} \
       --output_path ${output_path} \
       --ref_output_path ${output_reference_path} \
       --start_date ${start_date} \
       --final_date ${final_date} \
       --stype ${cycle_type} \

   echo "GIOPS_VP_dia_general_plot_v3.py finished"
 
   echo "Running GIOPS_VP_dia_general_plot_ens.py"
   python python/GIOPS_VP_dia_general_plot_ens.py  \
       --suite ${suite} \
       --ref_suite ${reference_suite} \
       --path ${input_path}  \
       --replace ${replace} \
       --ref_path ${input_reference_path} \
       --output_path ${output_path} \
       --ref_output_path ${output_reference_path} \
       --start_date ${start_date} \
       --final_date ${final_date} \
       --stype ${cycle_type} \
       --ensemble ${ensemble[*]}

   echo "GIOPS_VP_dia_general_plot_ens.py finished"

fi

if [ "${run_DS_ola}" = "T" ]; then
   echo "Running GIOPS_ola_plot_DS.py for ${suite}"
   python python/GIOPS_ola_plot_DS.py  \
       --suite ${suit0} \
       --input_dir ${input_path} \
       --output_dir ${output_path}/ola_diag \
       --start_date ${start_date} \
       --final_date ${final_date} \
       --stype ${cycle_type}

   echo "GIOPS_ola_plot_DS.py for ${suite} finished."

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
fi

if [ "${run_DS_ola_ref}" = "T" ]; then
   echo "Running GIOPS_ola_plot_DS.py for ${reference_suite}"
   python python/GIOPS_ola_plot_DS.py  \
       --suite ${reference_suite} \
       --input_dir ${input_reference_path}  \
       --output_dir ${output_reference_path}/ola_diag \
       --start_date ${start_date} \
       --final_date ${final_date} \
       --stype ${cycle_type}

   echo "GIOPS_ola_plot_DS.py for ${reference_suite} finished."
fi

if [ "${run_IS_ola}" = "T" ]; then
   echo "Running GIOPS_ola_plot_IS.py for ${suite}"
   python python/GIOPS_ola_plot_IS.py  \
       --suite ${suit0} \
       --input_dir ${input_path} \
       --output_dir ${output_path}/ola_diag \
       --start_date ${start_date} \
       --final_date ${final_date} \
       --stype ${cycle_type}

   echo "GIOPS_ola_plot_IS.py for ${suite} finished."
fi

if [ "${run_IS_ola_ref}" = "T" ]; then
   echo "Running GIOPS_ola_plot_IS.py for ${reference_suite}"
   python python/GIOPS_ola_plot_IS.py  \
       --suite ${reference_suite} \
       --input_dir ${input_reference_path}  \
       --output_dir ${output_reference_path}/ola_diag \
       --start_date ${start_date} \
       --final_date ${final_date} \
       --stype ${cycle_type}

   echo "GIOPS_ola_plot_IS.py for ${reference_suite} finished."
fi

if [ "${run_VP_ola}" = "T" ]; then
   echo "Running GIOPS_ola_plot_VP.py for ${suite}"
   python python/GIOPS_ola_plot_VP.py  \
       --suite ${suit0} \
       --input_dir ${input_path} \
       --output_dir ${output_path}/ola_diag \
       --start_date ${start_date} \
       --final_date ${final_date} \
       --stype ${cycle_type}

   echo "GIOPS_ola_plot_VP.py for ${suite} finished."
fi


if [ "${run_VP_ola_ref}" = "T" ]; then
   echo "Running GIOPS_ola_plot_VP.py for ${reference_suite}"
   python python/GIOPS_ola_plot_VP.py  \
       --suite ${reference_suite} \
       --input_dir ${input_reference_path}  \
       --output_dir ${output_reference_path}/ola_diag \
       --start_date ${start_date} \
       --final_date ${final_date} \
       --stype ${cycle_type}

   echo "GIOPS_ola_plot_VP.py for ${reference_suite} finished."
fi 


