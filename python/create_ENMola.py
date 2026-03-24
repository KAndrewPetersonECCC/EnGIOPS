import os
import sys
sys.path.insert(0, '/home/dpe000/EnGIOPS/python')
from importlib import reload

import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import time
import subprocess

import read_qcola
import create_dates
import check_date
import cross_monitor
#from cross_monitor import subset_to_reference_mp
#from cross_monitor import subset_to_reference

def calc_and_write_mean(date, expt, ddir=read_qcola.mdir, trial='trial', ensemble=list(range(1,21)), MP=True):
    if ( isinstance(date, list) ):
        for thedate in date:
           calc_and_write_mean(thedate, expt, ddir=ddir, trial=trial, ensemble=ensemble, MP=MP)
        return 
    if ( trial == 'both' ):
        for thistrial in ['trial', 'iau']:
            calc_and_write_mean(date, expt, ddir=ddir, trial=thistrial, ensemble=ensemble, MP=MP)
        return
    ddir=read_qcola.change_dir(ddir)
    is_trial = ( trial == 'trial' )
    for OLAA in ['VP', 'SST', 'SLA']:
        if ( OLAA == 'VP' ): OLA='VP'
        if ( OLAA == 'SLA' ): OLA='IS'
        if ( OLAA == 'SST' ): OLA='DS'
        groups = read_qcola.find_group_types(date, expt=expt, primary=OLAA, ddir=ddir, is_trial=is_trial, ens=ensemble[0])
        file=read_qcola.obtain_files([date], expt, OLA=OLA, trial=trial, ext='000', ddir=ddir, ens=ensemble[0])[0]  
        enss=str(ensemble[0]).zfill(3)
        emfile = file.replace('/'+enss+'/', '/ENM/')
        emdir = os.path.dirname(emfile)
        if ( not os.path.isdir(emdir) ): os.makedirs(emdir)
        if ( emfile == file ): emfile='NULL'  ## SAFETY.
        for group in groups:
            GROUP=OLAA+'/'+group
            qcola_ENS = read_qcola.read_OLA_ens([date], expt, ddir=ddir, trial=trial, ext='000', group=GROUP, ensemble=ensemble )
            nobs = np.min([qcola_mem.datanumber.size for qcola_mem in qcola_ENS])
            COMMON = [ ( qcola_mem.datanumber.size == nobs ) for qcola_mem in qcola_ENS ]
            num_iter = 0
            time0 = time.time()
            while ( not all(COMMON) ):
                qcola_ref = qcola_ENS[COMMON.index(True)]
                if ( MP ):
                    qcola_ENS = cross_monitor.subset_to_reference_list(qcola_ENS, qcola_ref)
                else:
                    qcola_ENS = cross_monitor.subset_to_reference_liss(qcola_ENS, qcola_ref)
                nobs = np.min([qcola_mem.datanumber.size for qcola_mem in qcola_ENS])
                COMMON = [ ( qcola_mem.datanumber.size == nobs ) for qcola_mem in qcola_ENS ]
                num_iter = num_iter+1
                print('NUM_ITER', num_iter, time.time() - time0)
            print('#obs : ', GROUP,[qcola_mem.datanumber.size for qcola_mem in qcola_ENS])
            qcola_exr = xr.concat(qcola_ENS, dim='edim')
            qcola_mne = qcola_exr.mean(dim='edim')
            if ( OLAA == 'VP'):
                qcola_mne['estat_temperature'] = qcola_exr['estat_temperature'].min(dim='edim')
                qcola_mne['estat_salinity'] = qcola_exr['estat_salinity'].min(dim='edim')
                print('ENSM', np.min(qcola_exr['estat_temperature']).compute())
                print('ENSM', np.min(qcola_mne['estat_temperature']).compute())
            else:
                qcola_mne['estat'] = qcola_exr['estat'].min(dim='edim')
                print('ENSM', np.min(qcola_exr['estat']).compute())
                print('MEAN', np.min(qcola_mne['estat']).compute())
            mode='a'
            if ( groups.index(group) == 0 ): mode='w'
            print('WRITING TO FILE ', emfile)
            print('group', group, 'MODE ', mode)
            qcola_mne.to_netcdf(emfile, group=GROUP, mode=mode)
    return

def create_submit_file(date, expt, ddir=read_qcola.mdir, trial='both', ensemble=list(range(1,21))):
    date_str = check_date.check_date(date)
    INPUT_FILE = f"JOBS/create_ENMola_{expt}_{date_str}.sh"
    direct=["-cpus", "80", "-cm", "180000M", "-t", "10800"]
    SUBMIT=["ord_soumet", f"/home/dpe000/EnGIOPS/{INPUT_FILE}"]+direct

    lines = []
    lines.append("#"+" ".join(SUBMIT)+"\n")
    lines.append(f"cd /home/dpe000/EnGIOPS\n")
    lines.append(f"source /home/dpe000/GEOPS/jobscripts/prepython.sh\n")
    lines.append(f"\n")
    lines.append(f"python << EOD\n")
    lines.append(f"import sys\n")
    lines.append(f"sys.path.insert(0, '/home/dpe000/EnGIOPS/python')\n")
    lines.append(f"\n")
    lines.append(f"import create_ENMola\n")
    lines.append(f"\n")
    lines.append(f"create_ENMola.calc_and_write_mean({date_str}, '{expt}', ddir='{ddir}', trial='{trial}', ensemble={str(ensemble)})\n")
    lines.append(f"EOD\n")

    with open(INPUT_FILE, 'w') as f:
        for line in lines:
            f.write(line)

    return SUBMIT, INPUT_FILE, lines

def submit_dates(dates, expt, ddir=read_qcola.mdir, trial='both', ensemble=list(range(1,21))):
    if ( len(dates) > 50 ):
        print(f"Number of dates {len(dates)} to large")
        print("Try again with smaller list")
        return
    for date in dates:
        submit, __, __ = create_submit_file(date, expt, ddir=ddir, trial=trial, ensemble=ensemble)
        print("#"+" ".join(submit)+"\n")
        subprocess.call(submit)
    return
