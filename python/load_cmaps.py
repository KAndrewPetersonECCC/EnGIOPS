import matplotlib.cm as cm
import copy

def load1():
    cmap_full='gist_stern_r'
    cmap_anom='seismic'
    cmap_anom = copy.copy(cm.seismic)
    cmap_anom.set_bad('g', 1.0)
    cmap_full = copy.copy(cm.gist_stern_r)
    cmap_full.set_bad('g', 1.0)
    return cmap_anom, cmap_full

def load2():
    cmap_full='YlOrRd'
    cmap_anom='RdYlBu_r'
    cmap_anom = copy.copy(cm.RdYlBu_r)
    cmap_anom.set_bad('g', 1.0)
    cmap_full = copy.copy(cm.YlOrRd)
    cmap_full.set_bad('g', 1.0)
    return cmap_anom, cmap_full
