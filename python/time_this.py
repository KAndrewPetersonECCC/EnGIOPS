import time
date=datetime.datetime(2021,6,2)
ens=list(range(21)); deterministic=False; ddir=read_DF_IS.get_mdir(5); mp_read=True; SAT='ALL'               
expt='GIOPS_T'
df_EnSSH = read_DF_IS.read_ensemble_SSH(expt, date, ddir=ddir, ens=ens, mp_read=mp_read, SAT=SAT)


time0=time.time(); df_EaSSH = read_DF_IS.ensemble_average_SSH(df_EnSSH, count=nens); print('MEAN TIME', time.time() - time0)
time0=time.time(); df_EaSSH = read_DF_IS.add_squared_error(df_EaSSH); print('SQRERR TIME', time.time() - time0)
time0=time.time(); df_EaSSH = read_DF_IS.add_crps_SSH(df_EaSSH, df_EnSSH); print('CRPS TIME', time.time() - time0)
time0=time.time(); df_EaSSH = read_DF_IS.add_rank_SSH(df_EaSSH, df_EnSSH, nens=nens); print('RANK TIME', time.time() - time0)
time0=time.time(); gl_df = read_DF_IS.summed_field(df_EaSSH); print('GLOBAL TIME', time.time() - time0)
time0=time.time(); hist_df = read_DF_IS.sum_rank(df_EaSSH, nens=nens); print('SUM RANK TIME', time.time() - time0)
time0=time.time(); rgs_df = read_DF_IS.calc_region_errors(df_EaSSH); print('REGION TIME', time.time() - time0)
time0=time.time(); bin_df = read_DF_IS.sum_ongrid(df_EaSSH); print('GRID TIME', time.time() - time0)
time0=time.time(); pdf_df = read_DF_IS.calc_pdf(df_EnSSH[['misfit']]) ; print('PDF TIME', time.time() - time0) 
time0=time.time(); pd2_df = read_DF_IS.calc_2dpdf(df_EaSSH, var_err='misfit', var_spr='ensvar') ; print('HEAT TIME', time.time() - time0)


df_column=df_EnSSH[['misfit']]
Nbins = 100
brange_err = [-5,5]
brange_spr = [0, 5]  
brange = [-5,5]
bin_key='misfit'
