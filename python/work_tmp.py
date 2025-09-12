>>> VP
<xarray.Dataset>
Dimensions:            (datanumber: 30649, vert: 4, levels: 50)
Dimensions without coordinates: datanumber, vert, levels
Data variables: (12/17)
    H_ij               (datanumber, vert) int32 ...
    H_wgt              (datanumber, vert) float64 ...
    latitude           (datanumber) float64 ...
    longitude          (datanumber) float64 ...
    time               (datanumber) float64 ...
    eqv_temperature    (datanumber, levels) float64 ...
    ...                 ...
    estat_temperature  (datanumber, levels) float64 ...
    estat_salinity     (datanumber, levels) float64 ...
    mis_temperature    (datanumber, levels) float64 ...
    mis_salinity       (datanumber, levels) float64 ...
    dep_temperature    (datanumber, levels) float32 ...
    dep_salinity       (datanumber, levels) float32 ...
>>> len(VP.latitude)
30649
>>> len(VP.coords)
0
>>> VP.coords
Coordinates:
    *empty*
>>> VP.coordinates
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/fs/ssm/eccc/cmd/cmds/env/python/py39_2022.05.24_rhel-8-icelake-64/lib/python3.9/site-packages/xarray/core/common.py", line 239, in __getattr__
    raise AttributeError(
AttributeError: 'Dataset' object has no attribute 'coordinates'
>>> VP.dimensions
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/fs/ssm/eccc/cmd/cmds/env/python/py39_2022.05.24_rhel-8-icelake-64/lib/python3.9/site-packages/xarray/core/common.py", line 239, in __getattr__
    raise AttributeError(
AttributeError: 'Dataset' object has no attribute 'dimensions'
>>> VP.dimensions()
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/fs/ssm/eccc/cmd/cmds/env/python/py39_2022.05.24_rhel-8-icelake-64/lib/python3.9/site-packages/xarray/core/common.py", line 239, in __getattr__
    raise AttributeError(
AttributeError: 'Dataset' object has no attribute 'dimensions'
>>> VP
<xarray.Dataset>
Dimensions:            (datanumber: 30649, vert: 4, levels: 50)
Dimensions without coordinates: datanumber, vert, levels
Data variables: (12/17)
    H_ij               (datanumber, vert) int32 ...
    H_wgt              (datanumber, vert) float64 ...
    latitude           (datanumber) float64 ...
    longitude          (datanumber) float64 ...
    time               (datanumber) float64 ...
    eqv_temperature    (datanumber, levels) float64 ...
    ...                 ...
    estat_temperature  (datanumber, levels) float64 ...
    estat_salinity     (datanumber, levels) float64 ...
    mis_temperature    (datanumber, levels) float64 ...
    mis_salinity       (datanumber, levels) float64 ...
    dep_temperature    (datanumber, levels) float32 ...
    dep_salinity       (datanumber, levels) float32 ...
>>> VP.dims()
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: 'Frozen' object is not callable
>>> VP.dims
Frozen({'datanumber': 30649, 'vert': 4, 'levels': 50})
>>> import glob
>>> file
'/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/noobs_noUSArgo_obsUS/SAM2/20200108/DIAG/trial/20200108000_QCOLA_VP_BEST.nc'
>>> glob.glob('/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/noobs_noUSArgo_obsUS/SAM2/2020????/DIAG/trial/2020????000_QCOLA_VP_BEST.nc')
['/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/noobs_noUSArgo_obsUS/SAM2/20200311/DIAG/trial/20200311000_QCOLA_VP_BEST.nc', '/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/noobs_noUSArgo_obsUS/SAM2/20200108/DIAG/trial/20200108000_QCOLA_VP_BEST.nc', '/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/noobs_noUSArgo_obsUS/SAM2/20201104/DIAG/trial/20201104000_QCOLA_VP_BEST.nc', '/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/noobs_noUSArgo_obsUS/SAM2/20200408/DIAG/trial/20200408000_QCOLA_VP_BEST.nc', '/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/noobs_noUSArgo_obsUS/SAM2/20200610/DIAG/trial/20200610000_QCOLA_VP_BEST.nc', '/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/noobs_noUSArgo_obsUS/SAM2/20200212/DIAG/trial/20200212000_QCOLA_VP_BEST.nc', '/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/noobs_noUSArgo_obsUS/SAM2/20200401/DIAG/trial/20200401000_QCOLA_VP_BEST.nc', '/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/noobs_noUSArgo_obsUS/SAM2/20200701/DIAG/trial/20200701000_QCOLA_VP_BEST.nc', '/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/noobs_noUSArgo_obsUS/SAM2/20201125/DIAG/trial/20201125000_QCOLA_VP_BEST.nc', '/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/noobs_noUSArgo_obsUS/SAM2/20200429/DIAG/trial/20200429000_QCOLA_VP_BEST.nc', '/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/noobs_noUSArgo_obsUS/SAM2/20200729/DIAG/trial/20200729000_QCOLA_VP_BEST.nc', '/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/noobs_noUSArgo_obsUS/SAM2/20201216/DIAG/trial/20201216000_QCOLA_VP_BEST.nc', '/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/noobs_noUSArgo_obsUS/SAM2/20200325/DIAG/trial/20200325000_QCOLA_VP_BEST.nc', '/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/noobs_noUSArgo_obsUS/SAM2/20201007/DIAG/trial/20201007000_QCOLA_VP_BEST.nc', '/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/noobs_noUSArgo_obsUS/SAM2/20200722/DIAG/trial/20200722000_QCOLA_VP_BEST.nc', '/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/noobs_noUSArgo_obsUS/SAM2/20200930/DIAG/trial/20200930000_QCOLA_VP_BEST.nc', '/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/noobs_noUSArgo_obsUS/SAM2/20200819/DIAG/trial/20200819000_QCOLA_VP_BEST.nc', '/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/noobs_noUSArgo_obsUS/SAM2/20200115/DIAG/trial/20200115000_QCOLA_VP_BEST.nc', '/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/noobs_noUSArgo_obsUS/SAM2/20201111/DIAG/trial/20201111000_QCOLA_VP_BEST.nc', '/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/noobs_noUSArgo_obsUS/SAM2/20200415/DIAG/trial/20200415000_QCOLA_VP_BEST.nc', '/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/noobs_noUSArgo_obsUS/SAM2/20200506/DIAG/trial/20200506000_QCOLA_VP_BEST.nc', '/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/noobs_noUSArgo_obsUS/SAM2/20200909/DIAG/trial/20200909000_QCOLA_VP_BEST.nc', '/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/noobs_noUSArgo_obsUS/SAM2/20200805/DIAG/trial/20200805000_QCOLA_VP_BEST.nc', '/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/noobs_noUSArgo_obsUS/SAM2/20200101/DIAG/trial/20200101000_QCOLA_VP_BEST.nc', '/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/noobs_noUSArgo_obsUS/SAM2/20201223/DIAG/trial/20201223000_QCOLA_VP_BEST.nc', '/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/noobs_noUSArgo_obsUS/SAM2/20200527/DIAG/trial/20200527000_QCOLA_VP_BEST.nc', '/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/noobs_noUSArgo_obsUS/SAM2/20200129/DIAG/trial/20200129000_QCOLA_VP_BEST.nc', '/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/noobs_noUSArgo_obsUS/SAM2/20201014/DIAG/trial/20201014000_QCOLA_VP_BEST.nc', '/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/noobs_noUSArgo_obsUS/SAM2/20200826/DIAG/trial/20200826000_QCOLA_VP_BEST.nc', '/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/noobs_noUSArgo_obsUS/SAM2/20200122/DIAG/trial/20200122000_QCOLA_VP_BEST.nc', '/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/noobs_noUSArgo_obsUS/SAM2/20200422/DIAG/trial/20200422000_QCOLA_VP_BEST.nc', '/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/noobs_noUSArgo_obsUS/SAM2/20200617/DIAG/trial/20200617000_QCOLA_VP_BEST.nc', '/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/noobs_noUSArgo_obsUS/SAM2/20200219/DIAG/trial/20200219000_QCOLA_VP_BEST.nc', '/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/noobs_noUSArgo_obsUS/SAM2/20200513/DIAG/trial/20200513000_QCOLA_VP_BEST.nc', '/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/noobs_noUSArgo_obsUS/SAM2/20200708/DIAG/trial/20200708000_QCOLA_VP_BEST.nc', '/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/noobs_noUSArgo_obsUS/SAM2/20200916/DIAG/trial/20200916000_QCOLA_VP_BEST.nc', '/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/noobs_noUSArgo_obsUS/SAM2/20200304/DIAG/trial/20200304000_QCOLA_VP_BEST.nc', '/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/noobs_noUSArgo_obsUS/SAM2/20200812/DIAG/trial/20200812000_QCOLA_VP_BEST.nc', '/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/noobs_noUSArgo_obsUS/SAM2/20201028/DIAG/trial/20201028000_QCOLA_VP_BEST.nc', '/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/noobs_noUSArgo_obsUS/SAM2/20201230/DIAG/trial/20201230000_QCOLA_VP_BEST.nc', '/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/noobs_noUSArgo_obsUS/SAM2/20200603/DIAG/trial/20200603000_QCOLA_VP_BEST.nc', '/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/noobs_noUSArgo_obsUS/SAM2/20200205/DIAG/trial/20200205000_QCOLA_VP_BEST.nc', '/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/noobs_noUSArgo_obsUS/SAM2/20201021/DIAG/trial/20201021000_QCOLA_VP_BEST.nc', '/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/noobs_noUSArgo_obsUS/SAM2/20200902/DIAG/trial/20200902000_QCOLA_VP_BEST.nc', '/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/noobs_noUSArgo_obsUS/SAM2/20201118/DIAG/trial/20201118000_QCOLA_VP_BEST.nc', '/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/noobs_noUSArgo_obsUS/SAM2/20200624/DIAG/trial/20200624000_QCOLA_VP_BEST.nc', '/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/noobs_noUSArgo_obsUS/SAM2/20200226/DIAG/trial/20200226000_QCOLA_VP_BEST.nc', '/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/noobs_noUSArgo_obsUS/SAM2/20201209/DIAG/trial/20201209000_QCOLA_VP_BEST.nc', '/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/noobs_noUSArgo_obsUS/SAM2/20200318/DIAG/trial/20200318000_QCOLA_VP_BEST.nc', '/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/noobs_noUSArgo_obsUS/SAM2/20200520/DIAG/trial/20200520000_QCOLA_VP_BEST.nc', '/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/noobs_noUSArgo_obsUS/SAM2/20200715/DIAG/trial/20200715000_QCOLA_VP_BEST.nc', '/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/noobs_noUSArgo_obsUS/SAM2/20200923/DIAG/trial/20200923000_QCOLA_VP_BEST.nc', '/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/noobs_noUSArgo_obsUS/SAM2/20201202/DIAG/trial/20201202000_QCOLA_VP_BEST.nc']
>>> files=glob.glob('/fs/site5/eccc/mrd/rpnenv/dpe000/maestro_archives/noobs_noUSArgo_obsUS/SAM2/2020????/DIAG/trial/2020????000_QCOLA_VP_BEST.nc')
>>> VP = xr.open_mfdataset(file, group='VP/VP_GEN_INSITU_REALTIME')
>>> VP = xr.open_mfdataset(files, group='VP/VP_GEN_INSITU_REALTIME')
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/fs/ssm/eccc/cmd/cmds/env/python/py39_2022.05.24_rhel-8-icelake-64/lib/python3.9/site-packages/xarray/backends/api.py", line 936, in open_mfdataset
    combined = combine_by_coords(
  File "/fs/ssm/eccc/cmd/cmds/env/python/py39_2022.05.24_rhel-8-icelake-64/lib/python3.9/site-packages/xarray/core/combine.py", line 975, in combine_by_coords
    concatenated = _combine_single_variable_hypercube(
  File "/fs/ssm/eccc/cmd/cmds/env/python/py39_2022.05.24_rhel-8-icelake-64/lib/python3.9/site-packages/xarray/core/combine.py", line 626, in _combine_single_variable_hypercube
    combined_ids, concat_dims = _infer_concat_order_from_coords(list(datasets))
  File "/fs/ssm/eccc/cmd/cmds/env/python/py39_2022.05.24_rhel-8-icelake-64/lib/python3.9/site-packages/xarray/core/combine.py", line 144, in _infer_concat_order_from_coords
    raise ValueError(
ValueError: Could not find any dimension coordinates to use to order the datasets for concatenation
>>> VP = xr.open_mfdataset(files, group='VP/VP_GEN_INSITU_REALTIME', concat_dims='datanumber')
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/fs/ssm/eccc/cmd/cmds/env/python/py39_2022.05.24_rhel-8-icelake-64/lib/python3.9/site-packages/xarray/backends/api.py", line 908, in open_mfdataset
    datasets = [open_(p, **open_kwargs) for p in paths]
  File "/fs/ssm/eccc/cmd/cmds/env/python/py39_2022.05.24_rhel-8-icelake-64/lib/python3.9/site-packages/xarray/backends/api.py", line 908, in <listcomp>
    datasets = [open_(p, **open_kwargs) for p in paths]
  File "/fs/ssm/eccc/cmd/cmds/env/python/py39_2022.05.24_rhel-8-icelake-64/lib/python3.9/site-packages/xarray/backends/api.py", line 495, in open_dataset
    backend_ds = backend.open_dataset(
TypeError: open_dataset() got an unexpected keyword argument 'concat_dims'
>>> VP = xr.open_mfdataset(files, group='VP/VP_GEN_INSITU_REALTIME', concat_dim='datanumber')
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/fs/ssm/eccc/cmd/cmds/env/python/py39_2022.05.24_rhel-8-icelake-64/lib/python3.9/site-packages/xarray/backends/api.py", line 888, in open_mfdataset
    raise ValueError(
ValueError: When combine='by_coords', passing a value for `concat_dim` has no effect. To manually combine along a specific dimension you should instead specify combine='nested' along with a value for `concat_dim`.
>>> VP = xr.open_mfdataset(files, group='VP/VP_GEN_INSITU_REALTIME', combine='nested', concat_dim='datanumber')
>>> VP.dim
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/fs/ssm/eccc/cmd/cmds/env/python/py39_2022.05.24_rhel-8-icelake-64/lib/python3.9/site-packages/xarray/core/common.py", line 239, in __getattr__
    raise AttributeError(
AttributeError: 'Dataset' object has no attribute 'dim'
>>> VP.dims
Frozen({'datanumber': 1606282, 'vert': 4, 'levels': 50})
>>> VP.dims['datanumber']
1606282
>>> VP.longitude.min
<bound method ImplementsArrayReduce._reduce_method.<locals>.wrapped_func of <xarray.DataArray 'longitude' (datanumber: 1606282)>
dask.array<concatenate, shape=(1606282,), dtype=float64, chunksize=(32752,), chunktype=numpy.ndarray>
Dimensions without coordinates: datanumber>
>>> VP.longitude.min.compute()
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
AttributeError: 'function' object has no attribute 'compute'
>>> VP.longitude.min
<bound method ImplementsArrayReduce._reduce_method.<locals>.wrapped_func of <xarray.DataArray 'longitude' (datanumber: 1606282)>
dask.array<concatenate, shape=(1606282,), dtype=float64, chunksize=(32752,), chunktype=numpy.ndarray>
Dimensions without coordinates: datanumber>
>>> VP.longitude.min.value
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
AttributeError: 'function' object has no attribute 'value'
>>> print(VP.longitude.min)
<bound method ImplementsArrayReduce._reduce_method.<locals>.wrapped_func of <xarray.DataArray 'longitude' (datanumber: 1606282)>
dask.array<concatenate, shape=(1606282,), dtype=float64, chunksize=(32752,), chunktype=numpy.ndarray>
Dimensions without coordinates: datanumber>
>>> print(VP['longitude'].min)
<bound method ImplementsArrayReduce._reduce_method.<locals>.wrapped_func of <xarray.DataArray 'longitude' (datanumber: 1606282)>
dask.array<concatenate, shape=(1606282,), dtype=float64, chunksize=(32752,), chunktype=numpy.ndarray>
Dimensions without coordinates: datanumber>
>>> print(VP['longitude'].values.min)
<built-in method min of numpy.ndarray object at 0x155014caf390>
>>> print(VP['longitude'].values.min())
-179.99960327148438
>>> print(VP['longitude'].min())
<xarray.DataArray 'longitude' ()>
dask.array<_nanmin_skip-aggregate, shape=(), dtype=float64, chunksize=(), chunktype=numpy.ndarray>
>>> print(VP['longitude'].min().compute())
<xarray.DataArray 'longitude' ()>
array(-179.99960327)
>>> print(VP['longitude'].max().compute())
<xarray.DataArray 'longitude' ()>
array(179.99960327)
>>> import sys
>>> sys.path.insert(0, '/home/dpe000/EnGIOPS/python')
>>> import inside_polygon
>>> points_are_inside = inside_polygon.test_inside_xyarray(polygon, VP.longitude, df_EaVP.latitude)[0]
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
NameError: name 'polygon' is not defined
>>> import read_DF_VP
>>> REGIONS=read_DF_VP.PAREAS
>>> REGIONS
{'NINO34': [[-170, -5], [-120, -5], [-120, 5], [-170, 5], [-170, -5]], 'NINO12': [[-90, -10], [-80, -10], [-80, 0], [-90, 0], [-90, -10]], 'SPacGyre': [[-179, -45], [-90, -45], [-90, -20], [-179, -20], [-179, -45]], 'CalCurnt': [[-125, 20], [-100, 20], [-100, 40], [-125, 40], [-125, 20]], 'Tropics': [[-180, -20], [180, -20], [180, 20], [-180, 20], [-180, -20]], 'NordAtl': [[-90, 30], [15, 30], [15, 65], [-90, 65], [-90, 30]], 'Pirata': [[-40, -2.5], [-30, -2.5], [-30, 2.5], [-40, 2.5], [-40, -2.5]], 'GlfSt1': [[-70, 36], [-62, 36], [-62, 40], [-70, 40], [-70, 36]], 'GlfSt2': [[-62, 38], [-45, 38], [-45, 42], [-62, 42], [-62, 38]], 'NFIS': [[-48, 45], [-37, 45], [-37, 55], [-48, 55], [-48, 45]], 'NPacGyre': [[130.0, 20.0], [160.0, 45.0], [240.0, 45.0], [240.0, 20.0], [130.0, 20.0]], 'ISBsn': [[-35.0, 55.0], [-25.0, 62.0], [-10.0, 62.0], [-10.0, 55], [-35.0, 55.0]], 'ACC': [[-180, -90], [180, -90], [180, -45], [-180, -45], [-180, -90]], 'North60': [[-180, 60], [180, 60], [180, 90], [-180, 90], [-180, 60]]}
>>> points_are_inside = inside_polygon.test_inside_xyarray(REGIONS['NINO34'], VP.longitude, VP.latitude)[0]
^CTraceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/home/dpe000/EnGIOPS/python/inside_polygon.py", line 38, in test_inside_xyarray
    Spoint = geometry.Point(point[0], point[1])
  File "/fs/ssm/eccc/cmd/cmds/env/python/py39_2022.05.24_rhel-8-icelake-64/lib/python3.9/site-packages/shapely/geometry/point.py", line 57, in __init__
    geom, n = geos_point_from_py(tuple(args))
  File "/fs/ssm/eccc/cmd/cmds/env/python/py39_2022.05.24_rhel-8-icelake-64/lib/python3.9/site-packages/shapely/geometry/point.py", line 263, in geos_point_from_py
    dy = c_double(coords[1])
  File "/fs/ssm/eccc/cmd/cmds/env/python/py39_2022.05.24_rhel-8-icelake-64/lib/python3.9/site-packages/xarray/core/common.py", line 134, in __float__
    return float(self.values)
  File "/fs/ssm/eccc/cmd/cmds/env/python/py39_2022.05.24_rhel-8-icelake-64/lib/python3.9/site-packages/xarray/core/dataarray.py", line 642, in values
    return self.variable.values
  File "/fs/ssm/eccc/cmd/cmds/env/python/py39_2022.05.24_rhel-8-icelake-64/lib/python3.9/site-packages/xarray/core/variable.py", line 512, in values
    return _as_array_or_item(self._data)
  File "/fs/ssm/eccc/cmd/cmds/env/python/py39_2022.05.24_rhel-8-icelake-64/lib/python3.9/site-packages/xarray/core/variable.py", line 252, in _as_array_or_item
    data = np.asarray(data)
  File "/fs/ssm/eccc/cmd/cmds/env/python/py39_2022.05.24_rhel-8-icelake-64/lib/python3.9/site-packages/dask/array/core.py", line 1625, in __array__
    x = self.compute()
  File "/fs/ssm/eccc/cmd/cmds/env/python/py39_2022.05.24_rhel-8-icelake-64/lib/python3.9/site-packages/dask/base.py", line 288, in compute
    (result,) = compute(self, traverse=False, **kwargs)
  File "/fs/ssm/eccc/cmd/cmds/env/python/py39_2022.05.24_rhel-8-icelake-64/lib/python3.9/site-packages/dask/base.py", line 565, in compute
    dsk = collections_to_dsk(collections, optimize_graph, **kwargs)
  File "/fs/ssm/eccc/cmd/cmds/env/python/py39_2022.05.24_rhel-8-icelake-64/lib/python3.9/site-packages/dask/base.py", line 340, in collections_to_dsk
    dsk = opt(dsk, keys, **kwargs)
  File "/fs/ssm/eccc/cmd/cmds/env/python/py39_2022.05.24_rhel-8-icelake-64/lib/python3.9/site-packages/dask/array/optimization.py", line 45, in optimize
    dsk = optimize_blockwise(dsk, keys=keys)
  File "/fs/ssm/eccc/cmd/cmds/env/python/py39_2022.05.24_rhel-8-icelake-64/lib/python3.9/site-packages/dask/blockwise.py", line 1212, in optimize_blockwise
    out = _optimize_blockwise(graph, keys=keys)
  File "/fs/ssm/eccc/cmd/cmds/env/python/py39_2022.05.24_rhel-8-icelake-64/lib/python3.9/site-packages/dask/blockwise.py", line 1222, in _optimize_blockwise
    dependents = reverse_dict(full_graph.dependencies)
  File "/fs/ssm/eccc/cmd/cmds/env/python/py39_2022.05.24_rhel-8-icelake-64/lib/python3.9/site-packages/dask/core.py", line 312, in reverse_dict
    for k, vals in d.items():
KeyboardInterrupt
>>> points_are_inside = inside_polygon.test_inside_xyarray(REGIONS['NINO34'], VP.longitude.values.compute(), VP.latitude.values.compute())[0]
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
AttributeError: 'numpy.ndarray' object has no attribute 'compute'
>>> points_are_inside = inside_polygon.test_inside_xyarray(REGIONS['NINO34'], VP.longitude.values, VP.latitude.values)[0]
>>> VP
<xarray.Dataset>
Dimensions:            (datanumber: 1606282, vert: 4, levels: 50)
Dimensions without coordinates: datanumber, vert, levels
Data variables: (12/17)
    H_ij               (datanumber, vert) int32 dask.array<chunksize=(32721, 4), meta=np.ndarray>
    H_wgt              (datanumber, vert) float64 dask.array<chunksize=(32721, 4), meta=np.ndarray>
    latitude           (datanumber) float64 dask.array<chunksize=(32721,), meta=np.ndarray>
    longitude          (datanumber) float64 dask.array<chunksize=(32721,), meta=np.ndarray>
    time               (datanumber) float64 dask.array<chunksize=(32721,), meta=np.ndarray>
    eqv_temperature    (datanumber, levels) float64 dask.array<chunksize=(32721, 50), meta=np.ndarray>
    ...                 ...
    estat_temperature  (datanumber, levels) float64 dask.array<chunksize=(32721, 50), meta=np.ndarray>
    estat_salinity     (datanumber, levels) float64 dask.array<chunksize=(32721, 50), meta=np.ndarray>
    mis_temperature    (datanumber, levels) float64 dask.array<chunksize=(32721, 50), meta=np.ndarray>
    mis_salinity       (datanumber, levels) float64 dask.array<chunksize=(32721, 50), meta=np.ndarray>
    dep_temperature    (datanumber, levels) float32 dask.array<chunksize=(32721, 50), meta=np.ndarray>
    dep_salinity       (datanumber, levels) float32 dask.array<chunksize=(32721, 50), meta=np.ndarray>
>>> mVP = np.mean(VP['mis_temperature'])
>>> mVP = np.mean(VP['mis_temperature'][points_are_inside])
>>> mvP
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
NameError: name 'mvP' is not defined
>>> mVP = np.mean(VP['mis_temperature'])
>>> mVPr = np.mean(VP['mis_temperature'][points_are_inside])
>>> mVP
<xarray.DataArray 'mis_temperature' ()>
dask.array<mean_agg-aggregate, shape=(), dtype=float64, chunksize=(), chunktype=numpy.ndarray>
>>> mVP.compute()
<xarray.DataArray 'mis_temperature' ()>
array(0.02833239)
>>> mVPr.compute()
<xarray.DataArray 'mis_temperature' ()>
array(-0.0432506)
>>> mVPr = np.mean(VP['mis_temperature'][points_are_inside], axis='datanumber')
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "<__array_function__ internals>", line 5, in mean
  File "/fs/ssm/eccc/cmd/cmds/env/python/py39_2022.05.24_rhel-8-icelake-64/lib/python3.9/site-packages/numpy/core/fromnumeric.py", line 3438, in mean
    return mean(axis=axis, dtype=dtype, out=out, **kwargs)
  File "/fs/ssm/eccc/cmd/cmds/env/python/py39_2022.05.24_rhel-8-icelake-64/lib/python3.9/site-packages/xarray/core/common.py", line 58, in wrapped_func
    return self.reduce(func, dim, axis, skipna=skipna, **kwargs)
  File "/fs/ssm/eccc/cmd/cmds/env/python/py39_2022.05.24_rhel-8-icelake-64/lib/python3.9/site-packages/xarray/core/dataarray.py", line 2696, in reduce
    var = self.variable.reduce(func, dim, axis, keep_attrs, keepdims, **kwargs)
  File "/fs/ssm/eccc/cmd/cmds/env/python/py39_2022.05.24_rhel-8-icelake-64/lib/python3.9/site-packages/xarray/core/variable.py", line 1804, in reduce
    data = func(self.data, axis=axis, **kwargs)
  File "/fs/ssm/eccc/cmd/cmds/env/python/py39_2022.05.24_rhel-8-icelake-64/lib/python3.9/site-packages/xarray/core/duck_array_ops.py", line 557, in mean
    return _mean(array, axis=axis, skipna=skipna, **kwargs)
  File "/fs/ssm/eccc/cmd/cmds/env/python/py39_2022.05.24_rhel-8-icelake-64/lib/python3.9/site-packages/xarray/core/duck_array_ops.py", line 335, in f
    return func(values, axis=axis, **kwargs)
  File "/fs/ssm/eccc/cmd/cmds/env/python/py39_2022.05.24_rhel-8-icelake-64/lib/python3.9/site-packages/xarray/core/nanops.py", line 139, in nanmean
    return dask_array.nanmean(a, axis=axis, dtype=dtype)
  File "/fs/ssm/eccc/cmd/cmds/env/python/py39_2022.05.24_rhel-8-icelake-64/lib/python3.9/site-packages/dask/array/reductions.py", line 690, in nanmean
    return reduction(
  File "/fs/ssm/eccc/cmd/cmds/env/python/py39_2022.05.24_rhel-8-icelake-64/lib/python3.9/site-packages/dask/array/reductions.py", line 144, in reduction
    axis = validate_axis(axis, x.ndim)
  File "/fs/ssm/eccc/cmd/cmds/env/python/py39_2022.05.24_rhel-8-icelake-64/lib/python3.9/site-packages/dask/array/utils.py", line 455, in validate_axis
    raise TypeError("Axis value must be an integer, got %s" % axis)
TypeError: Axis value must be an integer, got datanumber
>>> mVPr = np.mean(VP['mis_temperature'][points_are_inside], axis=0)
>>> mVPr = VP['mis_temperature'][points_are_inside].mean(axis='datanumber')
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/fs/ssm/eccc/cmd/cmds/env/python/py39_2022.05.24_rhel-8-icelake-64/lib/python3.9/site-packages/xarray/core/common.py", line 58, in wrapped_func
    return self.reduce(func, dim, axis, skipna=skipna, **kwargs)
  File "/fs/ssm/eccc/cmd/cmds/env/python/py39_2022.05.24_rhel-8-icelake-64/lib/python3.9/site-packages/xarray/core/dataarray.py", line 2696, in reduce
    var = self.variable.reduce(func, dim, axis, keep_attrs, keepdims, **kwargs)
  File "/fs/ssm/eccc/cmd/cmds/env/python/py39_2022.05.24_rhel-8-icelake-64/lib/python3.9/site-packages/xarray/core/variable.py", line 1804, in reduce
    data = func(self.data, axis=axis, **kwargs)
  File "/fs/ssm/eccc/cmd/cmds/env/python/py39_2022.05.24_rhel-8-icelake-64/lib/python3.9/site-packages/xarray/core/duck_array_ops.py", line 557, in mean
    return _mean(array, axis=axis, skipna=skipna, **kwargs)
  File "/fs/ssm/eccc/cmd/cmds/env/python/py39_2022.05.24_rhel-8-icelake-64/lib/python3.9/site-packages/xarray/core/duck_array_ops.py", line 335, in f
    return func(values, axis=axis, **kwargs)
  File "/fs/ssm/eccc/cmd/cmds/env/python/py39_2022.05.24_rhel-8-icelake-64/lib/python3.9/site-packages/xarray/core/nanops.py", line 139, in nanmean
    return dask_array.nanmean(a, axis=axis, dtype=dtype)
  File "/fs/ssm/eccc/cmd/cmds/env/python/py39_2022.05.24_rhel-8-icelake-64/lib/python3.9/site-packages/dask/array/reductions.py", line 690, in nanmean
    return reduction(
  File "/fs/ssm/eccc/cmd/cmds/env/python/py39_2022.05.24_rhel-8-icelake-64/lib/python3.9/site-packages/dask/array/reductions.py", line 144, in reduction
    axis = validate_axis(axis, x.ndim)
  File "/fs/ssm/eccc/cmd/cmds/env/python/py39_2022.05.24_rhel-8-icelake-64/lib/python3.9/site-packages/dask/array/utils.py", line 455, in validate_axis
    raise TypeError("Axis value must be an integer, got %s" % axis)
TypeError: Axis value must be an integer, got datanumber
>>> mVPr = VP['mis_temperature'][points_are_inside].mean(axis=0)
>>> VP.dims
Frozen({'datanumber': 1606282, 'vert': 4, 'levels': 50})
>>> VP.mis_temperature.dims
('datanumber', 'levels')
>>> mVPr.shape
(50,)
>>> depths=VP.depths
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/fs/ssm/eccc/cmd/cmds/env/python/py39_2022.05.24_rhel-8-icelake-64/lib/python3.9/site-packages/xarray/core/common.py", line 239, in __getattr__
    raise AttributeError(
AttributeError: 'Dataset' object has no attribute 'depths'
>>> VP
<xarray.Dataset>
Dimensions:            (datanumber: 1606282, vert: 4, levels: 50)
Dimensions without coordinates: datanumber, vert, levels
Data variables: (12/17)
    H_ij               (datanumber, vert) int32 dask.array<chunksize=(32721, 4), meta=np.ndarray>
    H_wgt              (datanumber, vert) float64 dask.array<chunksize=(32721, 4), meta=np.ndarray>
    latitude           (datanumber) float64 dask.array<chunksize=(32721,), meta=np.ndarray>
    longitude          (datanumber) float64 dask.array<chunksize=(32721,), meta=np.ndarray>
    time               (datanumber) float64 dask.array<chunksize=(32721,), meta=np.ndarray>
    eqv_temperature    (datanumber, levels) float64 dask.array<chunksize=(32721, 50), meta=np.ndarray>
    ...                 ...
    estat_temperature  (datanumber, levels) float64 dask.array<chunksize=(32721, 50), meta=np.ndarray>
    estat_salinity     (datanumber, levels) float64 dask.array<chunksize=(32721, 50), meta=np.ndarray>
    mis_temperature    (datanumber, levels) float64 dask.array<chunksize=(32721, 50), meta=np.ndarray>
    mis_salinity       (datanumber, levels) float64 dask.array<chunksize=(32721, 50), meta=np.ndarray>
    dep_temperature    (datanumber, levels) float32 dask.array<chunksize=(32721, 50), meta=np.ndarray>
    dep_salinity       (datanumber, levels) float32 dask.array<chunksize=(32721, 50), meta=np.ndarray>
>>> VP.keys()
KeysView(<xarray.Dataset>
Dimensions:            (datanumber: 1606282, vert: 4, levels: 50)
Dimensions without coordinates: datanumber, vert, levels
Data variables: (12/17)
    H_ij               (datanumber, vert) int32 dask.array<chunksize=(32721, 4), meta=np.ndarray>
    H_wgt              (datanumber, vert) float64 dask.array<chunksize=(32721, 4), meta=np.ndarray>
    latitude           (datanumber) float64 dask.array<chunksize=(32721,), meta=np.ndarray>
    longitude          (datanumber) float64 dask.array<chunksize=(32721,), meta=np.ndarray>
    time               (datanumber) float64 dask.array<chunksize=(32721,), meta=np.ndarray>
    eqv_temperature    (datanumber, levels) float64 dask.array<chunksize=(32721, 50), meta=np.ndarray>
    ...                 ...
    estat_temperature  (datanumber, levels) float64 dask.array<chunksize=(32721, 50), meta=np.ndarray>
    estat_salinity     (datanumber, levels) float64 dask.array<chunksize=(32721, 50), meta=np.ndarray>
    mis_temperature    (datanumber, levels) float64 dask.array<chunksize=(32721, 50), meta=np.ndarray>
    mis_salinity       (datanumber, levels) float64 dask.array<chunksize=(32721, 50), meta=np.ndarray>
    dep_temperature    (datanumber, levels) float32 dask.array<chunksize=(32721, 50), meta=np.ndarray>
    dep_salinity       (datanumber, levels) float32 dask.array<chunksize=(32721, 50), meta=np.ndarray>)
>>> depths=VP.levels
>>> lepths
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
NameError: name 'lepths' is not defined
>>> depths
<xarray.DataArray 'levels' (levels: 50)>
array([ 0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15, 16, 17,
       18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35,
       36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49])
Dimensions without coordinates: levels
>>> depths=VP.dep_temperature
>>> depths
<xarray.DataArray 'dep_temperature' (datanumber: 1606282, levels: 50)>
dask.array<concatenate, shape=(1606282, 50), dtype=float32, chunksize=(32752, 50), chunktype=numpy.ndarray>
Dimensions without coordinates: datanumber, levels
>>> depths=VP.dep_temperature.mean(axis=0),compute()
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
NameError: name 'compute' is not defined
>>> depths=VP.dep_temperature.mean(axis=0).compute()
>>> depths
<xarray.DataArray 'dep_temperature' (levels: 50)>
array([4.9412400e-01, 1.5416682e+00, 2.6458526e+00, 3.8201811e+00,
       5.0781269e+00, 6.4387345e+00, 7.9261332e+00, 9.5737915e+00,
       1.1406102e+01, 1.3468600e+01, 1.5812092e+01, 1.8498608e+01,
       2.1601217e+01, 2.5207602e+01, 2.9438631e+01, 3.4435974e+01,
       4.0361607e+01, 4.7374958e+01, 5.5752396e+01, 6.5782440e+01,
       7.7855522e+01, 9.2321632e+01, 1.0974606e+02, 1.3069650e+02,
       1.5583017e+02, 1.8613937e+02, 2.2249771e+02, 2.6600647e+02,
       3.1808157e+02, 3.8008664e+02, 4.5399521e+02, 5.4102515e+02,
       6.4379504e+02, 7.6341974e+02, 9.0212286e+02, 1.0621392e+03,
       1.2454178e+03, 1.4520714e+03, 1.6840626e+03, 1.9411359e+03,
       2.2247490e+03, 2.5332024e+03, 2.8647356e+03, 3.2214124e+03,
       3.5979990e+03, 3.9920344e+03, 4.4062100e+03, 4.8323657e+03,
       5.2746401e+03, 5.7279980e+03], dtype=float32)
Dimensions without coordinates: levels
>>> import matplotlib.pyplot as plt
>>> plt.plot(mVPr, -1*depths)
[<matplotlib.lines.Line2D object at 0x154f2d1fbb50>]
>>> plt.show()
>>> plt.savefig('P.png')
>>> mVPs = np.sqrt(np.square(VP['mis_temperature'][points_are_inside]).mean(axis=0))
>>> plt.close()
>>> plt.plot(mVPr, -1*depths)
[<matplotlib.lines.Line2D object at 0x154f2cf73460>]
>>> plt.plot(mVPs, -1*depths, style='--')
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/fs/ssm/eccc/cmd/cmds/env/python/py39_2022.05.24_rhel-8-icelake-64/lib/python3.9/site-packages/matplotlib/pyplot.py", line 2769, in plot
    return gca().plot(
  File "/fs/ssm/eccc/cmd/cmds/env/python/py39_2022.05.24_rhel-8-icelake-64/lib/python3.9/site-packages/matplotlib/axes/_axes.py", line 1632, in plot
    lines = [*self._get_lines(*args, data=data, **kwargs)]
  File "/fs/ssm/eccc/cmd/cmds/env/python/py39_2022.05.24_rhel-8-icelake-64/lib/python3.9/site-packages/matplotlib/axes/_base.py", line 312, in __call__
    yield from self._plot_args(this, kwargs)
  File "/fs/ssm/eccc/cmd/cmds/env/python/py39_2022.05.24_rhel-8-icelake-64/lib/python3.9/site-packages/matplotlib/axes/_base.py", line 538, in _plot_args
    return [l[0] for l in result]
  File "/fs/ssm/eccc/cmd/cmds/env/python/py39_2022.05.24_rhel-8-icelake-64/lib/python3.9/site-packages/matplotlib/axes/_base.py", line 538, in <listcomp>
    return [l[0] for l in result]
  File "/fs/ssm/eccc/cmd/cmds/env/python/py39_2022.05.24_rhel-8-icelake-64/lib/python3.9/site-packages/matplotlib/axes/_base.py", line 531, in <genexpr>
    result = (make_artist(x[:, j % ncx], y[:, j % ncy], kw,
  File "/fs/ssm/eccc/cmd/cmds/env/python/py39_2022.05.24_rhel-8-icelake-64/lib/python3.9/site-packages/matplotlib/axes/_base.py", line 351, in _makeline
    seg = mlines.Line2D(x, y, **kw)
  File "/fs/ssm/eccc/cmd/cmds/env/python/py39_2022.05.24_rhel-8-icelake-64/lib/python3.9/site-packages/matplotlib/lines.py", line 393, in __init__
    self.update(kwargs)
  File "/fs/ssm/eccc/cmd/cmds/env/python/py39_2022.05.24_rhel-8-icelake-64/lib/python3.9/site-packages/matplotlib/artist.py", line 1064, in update
    raise AttributeError(f"{type(self).__name__!r} object "
AttributeError: 'Line2D' object has no property 'style'
>>> plt.plot(mVPs, -1*depths, linesty='--')
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/fs/ssm/eccc/cmd/cmds/env/python/py39_2022.05.24_rhel-8-icelake-64/lib/python3.9/site-packages/matplotlib/pyplot.py", line 2769, in plot
    return gca().plot(
  File "/fs/ssm/eccc/cmd/cmds/env/python/py39_2022.05.24_rhel-8-icelake-64/lib/python3.9/site-packages/matplotlib/axes/_axes.py", line 1632, in plot
    lines = [*self._get_lines(*args, data=data, **kwargs)]
  File "/fs/ssm/eccc/cmd/cmds/env/python/py39_2022.05.24_rhel-8-icelake-64/lib/python3.9/site-packages/matplotlib/axes/_base.py", line 312, in __call__
    yield from self._plot_args(this, kwargs)
  File "/fs/ssm/eccc/cmd/cmds/env/python/py39_2022.05.24_rhel-8-icelake-64/lib/python3.9/site-packages/matplotlib/axes/_base.py", line 538, in _plot_args
    return [l[0] for l in result]
  File "/fs/ssm/eccc/cmd/cmds/env/python/py39_2022.05.24_rhel-8-icelake-64/lib/python3.9/site-packages/matplotlib/axes/_base.py", line 538, in <listcomp>
    return [l[0] for l in result]
  File "/fs/ssm/eccc/cmd/cmds/env/python/py39_2022.05.24_rhel-8-icelake-64/lib/python3.9/site-packages/matplotlib/axes/_base.py", line 531, in <genexpr>
    result = (make_artist(x[:, j % ncx], y[:, j % ncy], kw,
  File "/fs/ssm/eccc/cmd/cmds/env/python/py39_2022.05.24_rhel-8-icelake-64/lib/python3.9/site-packages/matplotlib/axes/_base.py", line 351, in _makeline
    seg = mlines.Line2D(x, y, **kw)
  File "/fs/ssm/eccc/cmd/cmds/env/python/py39_2022.05.24_rhel-8-icelake-64/lib/python3.9/site-packages/matplotlib/lines.py", line 393, in __init__
    self.update(kwargs)
  File "/fs/ssm/eccc/cmd/cmds/env/python/py39_2022.05.24_rhel-8-icelake-64/lib/python3.9/site-packages/matplotlib/artist.py", line 1064, in update
    raise AttributeError(f"{type(self).__name__!r} object "
AttributeError: 'Line2D' object has no property 'linesty'
>>> 
>>> plt.plot(mVPs, -1*depths, linestyle='--')
[<matplotlib.lines.Line2D object at 0x154f2d0913d0>]
>>> plt.savefig('P.png')
>>> REGIONS['NINO34']
[[-170, -5], [-120, -5], [-120, 5], [-170, 5], [-170, -5]]
>>> PAREAS
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
NameError: name 'PAREAS' is not defined
>>> REGIONS
{'NINO34': [[-170, -5], [-120, -5], [-120, 5], [-170, 5], [-170, -5]], 'NINO12': [[-90, -10], [-80, -10], [-80, 0], [-90, 0], [-90, -10]], 'SPacGyre': [[-179, -45], [-90, -45], [-90, -20], [-179, -20], [-179, -45]], 'CalCurnt': [[-125, 20], [-100, 20], [-100, 40], [-125, 40], [-125, 20]], 'Tropics': [[-180, -20], [180, -20], [180, 20], [-180, 20], [-180, -20]], 'NordAtl': [[-90, 30], [15, 30], [15, 65], [-90, 65], [-90, 30]], 'Pirata': [[-40, -2.5], [-30, -2.5], [-30, 2.5], [-40, 2.5], [-40, -2.5]], 'GlfSt1': [[-70, 36], [-62, 36], [-62, 40], [-70, 40], [-70, 36]], 'GlfSt2': [[-62, 38], [-45, 38], [-45, 42], [-62, 42], [-62, 38]], 'NFIS': [[-48, 45], [-37, 45], [-37, 55], [-48, 55], [-48, 45]], 'NPacGyre': [[130.0, 20.0], [160.0, 45.0], [240.0, 45.0], [240.0, 20.0], [130.0, 20.0]], 'ISBsn': [[-35.0, 55.0], [-25.0, 62.0], [-10.0, 62.0], [-10.0, 55], [-35.0, 55.0]], 'ACC': [[-180, -90], [180, -90], [180, -45], [-180, -45], [-180, -90]], 'North60': [[-180, 60], [180, 60], [180, 90], [-180, 90], [-180, 60]]}
>>> REGIONS['Pacific']
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
KeyError: 'Pacific'
>>> REGIONS.keys()
dict_keys(['NINO34', 'NINO12', 'SPacGyre', 'CalCurnt', 'Tropics', 'NordAtl', 'Pirata', 'GlfSt1', 'GlfSt2', 'NFIS', 'NPacGyre', 'ISBsn', 'ACC', 'North60'])
>>> REGIONS['NPacGyre']
[[130.0, 20.0], [160.0, 45.0], [240.0, 45.0], [240.0, 20.0], [130.0, 20.0]]
>>> NWPac=[[130.0, 20.0], [160.0, 45.0], [240.0, 45.0], [240.0, 20.0], [130.0, 20.0]]
>>> REGIONS['NINO34']
[[-170, -5], [-120, -5], [-120, 5], [-170, 5], [-170, -5]]
>>> NWPac=[[-180.0, 45.0], [-120.0, 45.0], [-120.0, 65.0], [-180, 65.0], [-180, 45.0]]
>>> REGIONS['NINO34]
  File "<stdin>", line 1
    REGIONS['NINO34]
                    ^
SyntaxError: EOL while scanning string literal
>>> REGIONS['NINO34']
[[-170, -5], [-120, -5], [-120, 5], [-170, 5], [-170, -5]]
>>> 
