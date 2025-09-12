import sys 
sys.path.insert(0, '/home/dpe000/GEOPS/python')       


import xarray as xr
import numpy as np
import fstd2nc

def read_file(file, var=None):
    sset=fstd2nc.Buffer(file, ignore_etiket=True, quiet=True)
    xset=sset.to_xarray()
    if ( isinstance(var, type(None)) ):
        return xset
    else:
        return xset[var]
    
