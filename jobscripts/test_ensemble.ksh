#!/bin/ksh
#ord_soumet /fs/homeu1/eccc/mrd/ords/rpnenv/dpe000/EnGIOPS/jobscripts/diagnostics_ens.ksh -cpus 1 -mpi -cm 8000M -t 10800 -shell=/bin/bash

export MPLBACKEND=agg

# Define all scripts arguments
suite="GIOPS_GEPS"
reference_suite="GIOPS_GDPS"
input_path="/fs/site3/eccc/mrd/rpnenv/dpe000/maestro_archives/GIOPS_E0/SAM2"
replace="GIOPS_E"
input_reference_path="/home/kch001/data_hall3/maestro_archives/GX330_CONTROLE/SAM2"
output_path="/fs/site3/eccc/mrd/rpnenv/dpe000/SAM2_diags/GEPS"

output_reference_path="/fs/site3/eccc/mrd/rpnenv/dpe000/SAM2_diags/GDPS"
start_date=20190313
final_date=20190904
ensemble=(0 1 2 4 5)
cycle_type="W"

run_IS_DS_dia=T
run_VP_dia=T
run_DS_ola=T
run_DS_ola_ref=T
run_IS_ola=T
run_IS_ola_ref=T
run_VP_ola=T
run_VP_ola_ref=T

cd /fs/homeu1/eccc/mrd/ords/rpnenv/dpe000/EnGIOPS/python

if [ "${run_VP_dia}" = "T" ]; then
   echo "Running GIOPS_VP_dia_general_plot_ens.py"
   python GIOPS_VP_dia_general_plot_ens.py  \
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

   echo "GIOPS_VP_dia_general_plot_v3.py finished"
fi

