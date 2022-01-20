#!/bin/bash
#ord_soumet /fs/homeu1/eccc/mrd/ords/rpnenv/dpe000/EnGIOPS/jobscripts_drew/produce_difference_plots.sh -cpus 1 -mpi -cm 8000M -t 3600 -shell=/bin/bash
#bash /fs/homeu1/eccc/mrd/ords/rpnenv/dpe000/EnGIOPS/jobscripts_drew/produce_difference_plots.sh

TDIR=/fs/homeu1/eccc/mrd/ords/rpnenv/dpe000/EnGIOPS
EXPT=STOP
NXPT=10

#for EN in STOP1 STOP2 STOP3 STOP4 STOP5 STOP6 STOP7 STOP8 STOP9 STOP10 STOP11 STOP12 STOP13 STOP14 STOP15 STOP16 STOP17 STOP18 STOP19 STOP20 STOQA0 STOQA1 STOQA1 STOQA2 STOQA3 STOQA4 STOQA5 STOQA6 STOQA7 STOQA8 STOQA9 STOQA10 STOQA11 STO00 STO10 STO20 STOR0 STOR1; do
#for EN in STOQA1 STOQA1 STOQA2 STOQA3 STOQA4 STOQA5 STOQA6 ; do
#for EN in STOQA10 STO00 STO10 STO20 STOR1; do
for EN in STOQA3 STOQA4 STOQA5 STOQA6 STOQA7 STOQA8 STOQA9 STOQA10 STOQA11 STOQA12 STOQA13 STOQA14; do
    EXPT=${EN:0:4}
    NXPT=${EN:4}
    COMMENT=None
   ln_sppt_traldf       = .true.   !!! Switch for lateral diffusion
   ln_sppt_traqsr       = .true.   !!! Switch for solar radiation
   ln_sppt_traatf       = .true.   !!! Switch for Asselin time-filter
   ln_sppt_dynldf       = .true.   !!! Switch for lateral diffusion
    case ${EN} in
      STOP7) COMMENT="STOP.1: ln\_sppt\_dynldf = true, Switch for lateral diffusion" ;;
      STOP8) COMMENT="STOP.8: ln\_sppt_traldf = true,Switch for lateral diffusion" ;;
      STOP9) COMMENT="STOP.9: ln\_sppt_trazdf = true, Switch for vertical diffusion" ;;
      STOP10) COMMENT="STOP.10: ln\_sppt\_trazdfp = true, Switch for pure vertical diffusion" ;;
      STOP11) COMMENT="STOP.11: ln\_sppt\_traevd = true, Switch for enhanced vertical diffusion" ;;
      STOP12) COMMENT="STOP.12: ln\_sppt\_trabbc = true, Switch for bottom boundary condition" ;;
      STOP13) COMMENT="STOP.13: ln\_sppt\_trabbl = true, Switch for bottom boundary layer" ;;
      STOP14) COMMENT="STOP.14: ln\_sppt\_tranpc = true, Switch for non-penetrative convection" ;;
      STOP15) COMMENT="STOP.15: ln\_sppt\_tradmp = true, Switch for tracer damping" ;;
      STOP16) COMMENT="STOP.16: ln\_sppt\_traqsr = true, Switch for solar radiation" ;;
      STOP17) COMMENT="STOP.17: ln\_sppt\_transr = true, Switch for non-solar radiation / freshwater flux" ;;
      STOP18) COMMENT="STOP.18: ln\_sppt\_traatf = true, Switch for Asselin time-filter" ;;
      STOP19) COMMENT="STOP.19: ln\_sppt\_dynzad = true, Switch for vertical diffusion" ;;
      STOP20) COMMENT="STOP.20: ln\_sppt\_trald, ln\_sppt\_dynldf, ln\_sppt\_traqsr, ln\_sppt\_traatf, Likely Combination" ;;
      STOP21) COMMENT="STOP.21: ln\_sppt\_traxad, ln\_sppt\_trayad" ;;
      STOP22) COMMENT="STOP.22: ln\_sppt\_trazad" ;;
      STOP23) COMMENT="STOP.23: ln\_sppt\_trasad (NULL)" ;; 
      STOP26) COMMENT="STOP.26: ln\_sppt\_dynkeg" ;;
      STOP27) COMMENT="STOP.27: ln\_sppt\_dynrvo" ;;
      STOP29) COMMENT="STOP.29: ln\_sppt\_dynbfr" ;;
      STOP30) COMMENT="STOP.30: ln\_sppt\_dynatf" ;;
      STOPAA) COMMENT="STOP.AA: FINAL CONFIGURATION ln_sppt_traldfln_sppt_traqsrln_sppt_traatfln_sppt_dynldf" ;;
      STOQA0) COMMENT="STOQ.A0: ALL SPP" ;;
      STOQA1) COMMENT="STOQ.A1: nn\_spp\_avt = 2, Vertical mixing of tracers (TKE or GLS only)" ;;
      STOQA2) COMMENT="STOQ.A2: nn\_spp\_avm = 2, Vertical mixing of momentum (TKE or GLS only)" ;;
      STOQA3) COMMENT="STOQ.A3: nn\_spp\_ahtu = 2, for laplacian/iso operator" ;;
      STOQA4) COMMENT="STOQ.A4: nn\_spp\_ahtv = 2, for laplacian/iso operator" ;;
      STOQA5) COMMENT="STOQ.A5: nn\_spp\_ahtw = 2, for iso operator" ;;
      STOQA6) COMMENT="STOQ.A6: nn\_spp\_ahtt = 2, for bilaplacian operator" ;;
      STOQA7) COMMENT="STOQ.A7: All nn\_spp\_aht\[uvwt\]" ;;
      STOQA8) COMMENT="nn\_spp\_arnf = 2, Enhanced mixing at river mouths";;
      STOQA9) COMMENT="nn\_spp\_aevd = 2, Enhanced vertical diffusion" ;;
      STOQA10) COMMENT="nn\_spp\_tkelc = 2, TKE : Langmuir cell coefficient" ;;
      STOQA11) COMMENT="nn\_spp\_tkeds = 2, TKE : Kolmogoroff dissipation coeff." ;;
      STOQA12) COMMENT="nn\_spp\_tkefr = 2, TKE : Fraction of srf TKE below ML" ;;
      STOQA13) COMMENT="ALL TKE terms" ;;
      STOQA14) COMMENT="nn_spp_ahubbl = 2" ;;
      STOQA15) COMMENT="nn_spp_ahvbbl = 2" ;;
      STOQA16) COMMENT="nn_spp_ah\[uv\]bbl = 2" ;;
      STOR0) COMMENT="Null Experiment" ;;
      STOR1) COMMENT="ln\_skeb=true" ;;
      STO00) COMMENT="Ensemble \#0" ;;
      STO10) COMMENT="Ensemble \#1" ;;
      STO20) COMMENT="Ensemble \#2" ;;
      STO0A) COMMENT="Final Ensemble \#0" ;;
      STO1A) COMMENT="Final Ensemble \#1" ;;
      STO2A) COMMENT="Final Ensemble \#2" ;;
      STO3A) COMMENT="Final Ensemble \#3" ;;
      STO4A) COMMENT="Final Ensemble \#4" ;;
      TTO1A) COMMENT="Total Ensemble \#1" ;;
      TTO2A) COMMENT="Total Ensemble \#2" ;;
      TTO3A) COMMENT="Total Ensemble \#3" ;;
      TTO4A) COMMENT="Total Ensemble \#4" ;;
    *) COMMENT=None ;;
    esac
    echo $EN $EXPT $NXPT ${COMMENT}
    
PJOB=${TDIR}/JOBS/produce_difference_plots.${EXPT}.${NXPT}.py
BJOB=${TDIR}/JOBS/produce_difference_plots.${EXPT}.${NXPT}.sh
SJOB="ord_soumet ${BJOB} -cpus 1 -mpi -cm 8000M -t 3600 -shell=/bin/bash"

cat > ${BJOB} << EOB
#!/bin/bash
#${SJOB}

cd ${TDIR}
export MPLBACKEND=agg
source /home/dpe000/GEOPS/jobscripts/preconda.sh
source activate metcarto
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

import stop_diff

stofile='/fs/site3/eccc/mrd/rpnenv/dpe000/maestro_archives/GIOPS_${EXPT}/SAM2/20190313.${NXPT}/DIA/ORCA025-CMC-ANAL_1d_grid_T_2019031300.nc'
reffile='/fs/site3/eccc/mrd/rpnenv/dpe000/maestro_archives/GIOPS_DNHA/SAM2/20190313/DIA/ORCA025-CMC-ANAL_1d_grid_T_2019031300.nc'
comment="${COMMENT}"
CLEV=np.arange(-0.9,1.1,0.2)
psuf='$EXPT.${NXPT}'
if ( psuf[0:4] == 'STOQ' ): CLEV=np.arange(-0.9,1.1,0.2)/10.0
if ( comment == 'None') : comment=None
stop_diff.plot_fld_diff(stofile, reffile=reffile,pdir='SDIF', psuf=psuf,comment=comment,CLEV=CLEV)

EOP

${SJOB}

done
