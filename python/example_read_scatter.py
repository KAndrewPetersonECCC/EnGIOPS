import sys
sys.path.insert(0, '/home/dpe000/EnGIOPS/python')
import numpy as np
import ola_functions
import cplot


# REPLACE ola_functions.test_file with any ola file

df_IS_AL, df_IS_C2, df_IS_J2, df_IS_J3, df_IS_J2N, df_IS_H2, df_IS_S3A, df_IS = ola_functions.SSH_dataframe(ola_functions.test_file)

lon = df_IS['Lon'].values
lat = df_IS['Lat'].values                                
misfit = df_IS['misfit'].values               

cplot.scatter(lon, lat, misfit, outfile='SSH_misfit.png', s=0.01, levels=np.arange(-0.5, 0.51, 0.05), cmap='seismic')

