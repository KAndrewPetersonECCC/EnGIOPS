import os

import find_hall
import get_archive

hall=find_hall.find_hall()
site=find_hall.get_site()
main_host=find_hall.get_main_host()
datadir='/fs/'+site+'/eccc/mrd/rpnenv/dpe000/'
tmpdir=datadir+'tmpdir/'

nens = 21

d_geps='/fs/'+site+'/eccc/prod/ops/suites/geps/'
d_geps_20220621='/fs/'+site+'/eccc/prod/ops/suites/geps_20220621/'
d_geps_ANYTHING='/fs/'+site+'/eccc/prod/ops/suites/geps_ANYTHING/'

def find_geps_fcst_file(date, leadhrs, ie, sys='OP', src='ocn', execute=False, only_this_ens=False):
    if ( src == 'ocn' ):  
       file_fcst=find_geps_ocn_fcst(date, leadhrs, ie, sys=sys, execute=execute, only_this_ens=only_this_ens)
    else:
       asrc = src
       if ( src == 'atm' ): asrc='hyb'
       file_fcst=find_geps_atm_fcst(date,leadhrs, ie, sys=sys, execute=execute, only_this_ens=only_this_ens, src=asrc)
    return file_fcst

def find_geps_ocn_fcst(date, leadhrs, ie, sys='OP', execute=False, only_this_ens=False):

    file_fcst='Null'

    this_date_str = date.strftime('%Y%m%d%H')
    this_hour_str = date.strftime('%H')
    if ( (this_hour_str != '00' ) and ( this_hour_str != '12' ) ):
        print('HOUR must be 00Z or 12Z')
        return file_fcst
        
    lead_hour_str = str(leadhrs).zfill(3)
    ens_str = str(ie)
    en3_str = str(ie).zfill(3)
    weekday = date.weekday()

    tmp_fcst = tmpdir+sys+'/O/'
    
    if ( sys == 'OP' ):
      d_geps_sys = d_geps
      branch = 'operation.ensemble.prog.ens.glboce'
    if ( sys == 'PS' ): 
      d_geps_sys = d_geps_ANYTHING
      branch = 'parallel.ensemble.prog.ens.glboce'
   
    file_fcst=d_geps_sys+'/gridpt/prog/ens.glboce/'+this_date_str+'_'+lead_hour_str+'_'+en3_str
    if ( not os.path.isfile(file_fcst) ):
        file_fcst=tmp_fcst+branch+'/'+this_date_str+'_'+lead_hour_str+'_'+en3_str
        # WHEN OCN DATA ARCHIVED.  REORDER.
        if ( not os.path.isfile(file_fcst) ):
            if ( ( weekday == 3 ) or ( leadhrs < 385 ) ): # ONLY LONGER LEADS ON THURSDAY
                if ( ( ie == 0 ) and ( not only_this_ens ) ): # Now gets full ensemble if ens==0.
                    enslst = list(range(nens))
                    rc=get_archive.get_archive(tmp_fcst, branch=branch, date=date, fcst_hour=leadhrs, ensnum=enslst, execute=execute)
                else:
                    rc=get_archive.get_archive(tmp_fcst, branch=branch, date=date, fcst_hour=leadhrs, ensnum=ie, execute=execute)

    return file_fcst
            

def find_geps_atm_fcst(date, leadhrs, ie, sys='OP', execute=False, only_this_ens=False, src='hyb'):

    file_fcst='Null'
    
    this_date_str = date.strftime('%Y%m%d%H')
    this_hour_str = date.strftime('%H')
    if ( (this_hour_str != '00' ) and ( this_hour_str != '12' ) ):
        print('HOUR must be 00Z or 12Z')
        return file_fcst
        
    lead_hour_str = str(leadhrs).zfill(3)
    ens_str = str(ie)
    en3_str = str(ie).zfill(3)
    weekday = date.weekday()

    tmp_fcst = tmpdir+sys+'/A/'

    if ( sys == 'OP' ):
       d_geps_sys = d_geps
       branch = 'operation.ensemble.prog.ens.'+src
    if ( sys == 'PS' ): 
      d_geps_sys = d_geps_ANYTHING
      branch = 'parallel.ensemble.prog.ens.'+src
    if ( src == 'hyb' ): branch=branch+'.e1'
    file_fcst=d_geps_sys+'/gridpt/prog/ens.'+src+'/'+this_date_str+'_'+lead_hour_str+'_'+en3_str

    if ( not os.path.isfile(file_fcst) ):
        file_fcst=tmp_fcst+'/'+branch+'/'+this_date_str+'_'+lead_hour_str+'_'+en3_str
        # WHEN OCN DATA ARCHIVED.  REORDER.
        if ( not os.path.isfile(file_fcst) ):
            if ( ( weekday == 3 ) or ( leadhrs < 385 ) ): # ONLY LONGER LEADS ON THURSDAY
                if ( ie == 0 ): # Now gets full ensemble if ens==0.
                    enslst = list(range(nens))
                    rc=get_archive.get_archive(tmp_fcst, branch=branch, date=date, fcst_hour=leadhrs, ensnum=enslst, execute=execute)
                else:
                    rc=get_archive.get_archive(tmp_fcst, branch=branch, date=date, fcst_hour=leadhrs, ensnum=ie, execute=execute)

    return file_fcst
    
def geps_in_maestro(expt, date, lhr, ie, src='ocn', ddir=datadir+'/maestro'):
    date_str = date.strftime('%Y%m%d%H')
    lhr_str = str(lhr).zfill(3)
    ens_str = str(ie).zfill(3)
    basename=date_str+'_'+lhr_str+'_'+ens_str
    if ( src == 'ocn' ):  diradd='gridpt/prog/ens.glboce'
    file=ddir+'/'+expt+'/'+diradd+'/'+basename
    EXIST=os.path.isfile(file)
    return file, EXIST
    
    
