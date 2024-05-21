import scipy.stats as ss
        
import matplotlib.pyplot as plt
import matplotlib.colors as clr
import matplotlib.cm as cm

import numpy as np
import math
import copy

dmap = copy.copy(cm.gist_stern_r)


def init_bins(brange, Nbins):
    num_bins = np.arange(Nbins+1) / Nbins
    bin_edge = brange[0] + (brange[1]-brange[0]) * num_bins
    del_bins = bin_edge[1] - bin_edge[0]
    bin_mids = bin_edge - del_bins/2.0
    bins, bin_fdge, binn = ss.binned_statistic(bin_mids, np.zeros(len(bin_mids)), statistic='sum', bins=bin_edge)
    #print( 'EDGES', bin_edge, np.all( bin_edge == bin_fdge) )
    #print( binn)
    #print( 'BINS', np.all(binn == list(range(Nbins+1))) , ( np.sum(bins) == 0 ) ) 
    return bin_edge
    
def calc_bin_mid(bin_edge):
    bin_mid = 0.5 * ( bin_edge[:-1] + bin_edge[1:] )
    return bin_mid

def zero_bins(bin_edge):
    del_bins = bin_edge[1] - bin_edge[0]
    bin_mids = bin_edge - del_bins/2.0
    bins, bin_fdge, binn = ss.binned_statistic(bin_mids, np.zeros(len(bin_mids)), statistic='sum', bins=bin_edge)
    return bins
    
def zero_2Dbins(bin_edge1, bin_edge2):
    del_bins1 = bin_edge1[1] - bin_edge1[0]
    del_bins2 = bin_edge2[1] - bin_edge2[0]
    bin_mids1 = bin_edge1 - del_bins1/2.0
    bin_mids2 = bin_edge2 - del_bins2/2.0
    bin_mids = np.meshgrid(bin_mids1, bin_mids2)
    bins, __, __, __ = ss.binned_statistic_2d(bin_mids[0].flatten(), bin_mids[1].flatten(), np.zeros((bin_mids[0].shape)).flatten(), statistic='sum', bins=[bin_edge1, bin_edge2])
    print ( np.where(bins != 0) )
    return bins
    
def bin_values(X, bin_edge):
    XA = np.array(X)
    bins, bin_fdge, binn = ss.binned_statistic(XA, np.ones(XA.size), statistic='sum', bins=bin_edge)
    nadd = XA.size
    return bins, nadd   

def bin2D_values(X, Y,  bin_edge1, bin_edge2):
    XA = np.array(X)
    YA = np.array(Y)
    if ( XA.size != YA.size ):
       print("ERROR.  Not same size")
       return None
    bins, bin_fdge1, bin_fdge2, binn = ss.binned_statistic_2d(XA, YA, np.ones(XA.size), bins=[bin_edge1, bin_edge2], statistic='sum')
    nadd = XA.size
    return bins, nadd   

def norm_bins(bins, Nnorm):
   binn = np.array(bins) / Nnorm
   return binn

def plot_pdf(bin_edge, bins, title, pfile):
    bwidth=bin_edge[1]-bin_edge[0]
    fig, axe = plt.subplots()
    axe.bar(bin_edge[:-1], bins, width=bwidth, align='edge') 
    axe.set_title(title) 
    fig.savefig(pfile+'.png',bbox_inches='tight')
    fig.savefig(pfile+'.pdf',bbox_inches='tight')
    plt.close(fig)

def plot_2dpdf(bin_edge1, bin_edge2, bins, title, pfile, levels=np.arange(0,1.1,0.1), cmap=dmap, cbar=True, obar='horizontal'):
    bwidth1=bin_edge1[1]-bin_edge1[0]
    bwidth2=bin_edge2[1]-bin_edge2[0]
    bmiddle1=bin_edge1[:-1]+bwidth1
    bmiddle2=bin_edge2[:-1]+bwidth2
    fig, axe = plt.subplots()
    Ncolors = plt.get_cmap(cmap).N
    norm = clr.BoundaryNorm(levels, ncolors=Ncolors, clip=True)
    mesh = axe.pcolormesh(bmiddle1, bmiddle2, np.transpose(bins), norm=norm, cmap=cmap)
    if ( cbar ): 
        #print('cbar', cbar_fontsize)
        cbar_fig=fig.colorbar(mesh, orientation=obar)
        cbar_fig.ax.tick_params(labelsize=cbar_fontsize)
    fig.savefig(pfile+'.png',bbox_inches='tight')
    fig.savefig(pfile+'.pdf',bbox_inches='tight')
    plt.close(fig)

def test_pdf():
    N = 1000000
    s = np.random.normal(0.0, 1.0, N)
    
    bin_edge = init_bins([-2, 2], 100)
    bins, nadd = bin_values(s, bin_edge1)
    print('NORM', N, nadd)
    binn = norm_bins(bins, N)
    print(binn)
    print(bin_edge)
    
    ofile='test_pdf'
    title='PDF'
    plot_pdf(bin_edge, binn, title, ofile)
   
def test_2dpdf():
    N = 10000
    s = np.random.normal(0.0, 1.0, 2*N)
    t = np.absolute(np.random.normal(0.0, 1.0, N))
    X, Y = np.meshgrid(s, t)
    print(type(X), type(Y), type(s), type(t))
    
    bin_edge1 = init_bins([-5, 5], 200)
    bin_edge2 = init_bins([0, 5], 100)
    bins, nadd = bin2D_values(X.flatten(), Y.flatten(), bin_edge1, bin_edge2)
    print('NORM', N, nadd)
    binn = norm_bins(bins, nadd)
    print(binn.shape)
    print(np.max(binn), np.min(binn), np.mean(binn))
    
    ofile='test_2dpdf'
    title='PDF'
    plot_2dpdf(bin_edge1, bin_edge2, binn, title, ofile, levels=np.arange(0, 1.1e-3, 1e-4))
    return
    
    
    
