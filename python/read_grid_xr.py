import xarray as xr

DEF_MESH_MASK='/fs/site5/eccc/mrd/rpnenv/dpe000/NEMO_MESH_MASK/mesh_mask.nc'

def read_mesh_var(var, file=DEF_MESH_MASK):
    mesh=xr.open_dataset(file)
    if ( isinstance(var, type(None) ) ):
        return mesh
    else:
        return mesh[var]
        
