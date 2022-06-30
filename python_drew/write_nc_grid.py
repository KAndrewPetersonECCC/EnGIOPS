import numpy as np
import netCDF4

def write_nc_grid(fields, variables, file):
    rc = 0
    # open a new netCDF file for writing.
    ncfile = netCDF4.Dataset(file,'w') 
    ##NOTE:  FIELDS with be output in netcdf as (ny, nx)!!!
    (nx, ny) = fields[0].shape
    #print('nx, ny = ', nx, ny)
    ncfile.createDimension('x',nx)
    ncfile.createDimension('y',ny)
    # create the variable (4 byte integer in this case)
    # first argument is name of variable, second is datatype, third is
    # a tuple with the names of dimensions.

    nf=len(fields)    
    nv=len(variables)    
    # Error control on length of fields/variables.
    if ( nf != nv ):
       print('Error -- incompatible lengths', len(fields), len(variables))
       
    data=[]
    for ifield in range(nf):
        field = fields[ifield]
        variable=variables[ifield]
        data.append(ncfile.createVariable(variable,np.dtype('float').char,('y','x')))
        # write data to variable.
        ##NOTE:  FIELDS with be output in netcdf as (ny, nx)!!!
        data[ifield][:] = np.transpose(field)
    # close the file.
    ncfile.close()
    print('*** SUCCESS writing ncfile file '+file+'!')
    return rc

def write_nc_multi_grid(grids, fields, variables, file):
    rc = 0
    # open a new netCDF file for writing.
    ncfile = netCDF4.Dataset(file,'w') 
    ##NOTE:  FIELDS with be output in netcdf as (ny, nx)!!!
    ngrids=len(grids)
    nfieldg=len(fields)
    nvariag=len(variables)
    
    if ( ( nfieldg != ngrids ) or ( nvariag != ngrids ) ):  
        print('Unequal tuples', nfieldg, nfieldg, nvariag)
        ncfile.close()
        rc = 99
        return rc
        
    dimensions = []
    for igrid, grid in enumerate(grids):
        (nx, ny) = grid
        print('nx, ny = ', nx, ny)
        dimx = 'x'+str(igrid)
        dimy = 'y'+str(igrid)
        dimensions.append((dimx, dimy))
        ncfile.createDimension(dimx,nx)
        ncfile.createDimension(dimy,ny)

        # create the variable (4 byte integer in this case)
        # first argument is name of variable, second is datatype, third is
        # a tuple with the names of dimensions.

        nf=len(fields[igrid])    
        nv=len(variables[igrid])    
        # Error control on length of fields/variables.
        if ( nf != nv ):
            print('Error -- incompatible lengths', nf, nv)
            ncfile.close()
            rc=99
            return rc
       
    for igrid, grid in enumerate(grids):
        (nx, ny) = grid
        (dimx, dimy) = dimensions[igrid]
        nf=len(fields[igrid])    
        nv=len(variables[igrid])    

        data=[]
        for ifield in range(nf):
            field = fields[igrid][ifield]
            variable=variables[igrid][ifield]
            data.append(ncfile.createVariable(variable,np.dtype('float').char,(dimy,dimx)))
            # write data to variable.
            ##NOTE:  FIELDS with be output in netcdf as (ny, nx)!!!
            data[ifield][:] = np.transpose(field)

    # close the file.
    ncfile.close()
    print('*** SUCCESS writing ncfile file '+file+'!')
    return rc

def write_nc3d_grid(fields, variables, dims, file):
    rc = 0
    # open a new netCDF file for writing.
    ncfile = netCDF4.Dataset(file,'w') 
    ##NOTE:  FIELDS with be output in netcdf as (ny, nx)!!!
    nz=0 ; ny=0 ; nx=0
    nd2=0
    nd3=0

    try:
        nd3=dims.index(3)
        (nz, nx, ny) = fields[nd3].shape
    except:
        try:
            nd2=dims.index(2)
            (nx, ny) = fields[nd2].shape
        except:
            pass
       
       
    print('nx, ny, nz = ', nx, ny, nz)
    ncfile.createDimension('x',nx)
    ncfile.createDimension('y',ny)
    if ( nz > 0 ):
        ncfile.createDimension('z',nz)
    # create the variable (4 byte integer in this case)
    # first argument is name of variable, second is datatype, third is
    # a tuple with the names of dimensions.

    nf=len(fields)    
    nv=len(variables)    
    # Error control on length of fields/variables.
    if ( nf != nv ):
       print('Error -- incompatible lengths', len(fields), len(variables))
       
    data=[]
    for ifield in range(nf):
        field = fields[ifield]
        variable=variables[ifield]
        if ( dims[ifield] == 2 ):
            data.append(ncfile.createVariable(variable,np.dtype('float').char,('y','x')))
            # write data to variable.
            ##NOTE:  FIELDS with be output in netcdf as (ny, nx)!!!
            data[ifield][:] = np.transpose(field)
        elif ( dims[ifield] == 3 ):
            data.append(ncfile.createVariable(variable,np.dtype('float').char,('z','y','x')))
            # write data to variable.
            ##NOTE:  FIELDS with be output in netcdf as (nz, ny, nx)!!!
            data[ifield][:] = np.transpose(field, (0, 2, 1) )
    # close the file.
    ncfile.close()
    print('*** SUCCESS writing ncfile file '+file+'!')
    return rc

def read_nc(file, variables):
    dataset = netCDF4.Dataset(file)

    if ( isinstance(variables, str) ): variables=[variables]
    fld_tuple = []
    for var in variables:
        fld = dataset.variables[var][:]
        # NEED TO TRANSPOSE TO FIT Standard File Standard of (x,y)
        if ( fld.ndim == 2 ):
            fld_tuple.append(np.transpose(fld))
        elif ( fld.ndim == 3 ):
            fld_tuple.append(np.transpose(fld, (0, 2, 1)))
        else:
            fld_tuple.append(fld)
    dataset.close()
    return fld_tuple

