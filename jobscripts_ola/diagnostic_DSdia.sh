!/bin/bash
#ord_soumet /fs/homeu1/eccc/mrd/ords/rpnenv/dpe000/EnGIOPS/jobscripts/diagnostic_DSdia.sh -cpus 1 -mpi -cm 8000M -t 21600 -shell=/bin/bash

export MPLBACKEND=agg

# Define all scripts arguments
suite="GIOPS_PX"
suit0="GIOPS_P0"
reference_suite="GIOPS_GDPS"
input_path="/fs/site3/eccc/mrd/rpnenv/dpe000/maestro_archives/GIOPS_P0/SAM2"
replace="GIOPS_P"
input_reference_path="/home/kch001/data_hall3/maestro_archives/GX330_CONTROLE/SAM2"
output_path="/fs/site3/eccc/mrd/rpnenv/dpe000/SAM2_diags/GIOPS_P"

output_reference_path="/fs/site3/eccc/mrd/rpnenv/dpe000/SAM2_diags/GDPS"
start_date=20190320
final_date="20190424"
#final_date=20200401
#ensemble=(0 1 2 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20)
ensemble=(0 1 3 4 5 6)
cycle_type="W"

cd /fs/homeu1/eccc/mrd/ords/rpnenv/dpe000/EnGIOPS
source jobscripts/preconda.sh
source activate metpyy

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
