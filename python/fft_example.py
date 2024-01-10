import numpy as np
import scipy.stats
import scipy.signal
import matplotlib.pyplot as plt

import sys
sys.path.insert(0, '/home/dpe000/GEOPS/python')
import shapiro

A = np.random.randn(1442, 1021)
B, W = shapiro.shapiro2D(A, npass=100)

N=100
X=721; Y = 510
sub_A = A[X-50:X+50, Y-50:Y+50]
sub_B = B[X-50:X+50, Y-50:Y+50]
sub_C = sub_B - np.mean(sub_B)
sub_D = sub_A - np.mean(sub_A)

FFT2A = np.fft.fft2(sub_A)
PSD2A = np.abs(FFT2A*np.conj(FFT2A))

FFT2 = np.fft.fft2(sub_C)
PSD2 = np.abs(FFT2*np.conj(FFT2))

nx, ny = sub_A.shape

FDTX = np.zeros((nx,ny)).astype(complex)
FDTY = np.zeros((nx,ny)).astype(complex)
PDDX = np.zeros((nx,ny))
PDDY = np.zeros((nx,ny))

FFTX = np.zeros((nx,ny)).astype(complex)
FFTY = np.zeros((nx,ny)).astype(complex)
PSDX = np.zeros((nx,ny))
PSDY = np.zeros((nx,ny))

for iy in range(ny):
    fft=np.fft.fft(sub_A[:, iy])
    psd=np.abs(fft*np.conj(fft))
    FDTX[:, iy] = fft
    PDDX[:, iy] = psd
    fft=np.fft.fft(sub_C[:, iy])
    psd=np.abs(fft*np.conj(fft))
    FFTX[:, iy] = fft
    PSDX[:, iy] = psd
    
    
for ix in range(nx):
    fft=np.fft.fft(sub_A[ix,:])
    psd=np.abs(fft*np.conj(fft))
    FDTY[ix, :] = fft
    PDDY[ix, :] = psd
    fft=np.fft.fft(sub_C[ix,:])
    psd=np.abs(fft*np.conj(fft))
    FFTY[ix, :] = fft
    PSDY[ix, :] = psd
    
PSEX = np.mean(PDDX, axis=1)
PSEY = np.mean(PDDY, axis=0)
PSRX = PSEX[:51]
PSRX[1:50] = (PSEX[-1:50:-1]+PSEX[1:50])/2
PSRY=PSEY[:51]
PSRY[1:50] = (PSEY[-1:50:-1]+PSEY[1:50])/2

#FFAX = np.mean(FFTX, axis=1)
#FFAY = np.mean(FFTY, axis=0)
#PSBX = np.abs(FFAX*np.conj(FFAX))
#PSBY = np.abs(FFAY*np.conj(FFAY))
#PSQX = PSBX[:51] 
#PSQX[1:50] = (PSBX[-1:50:-1]+PSBX[1:50])/2
#PSQY=PSBY[:51]
#PSQY[1:50] = (PSBY[-1:50:-1]+PSBY[1:50])/2

PSAX = np.mean(PSDX, axis=1)
PSAY = np.mean(PSDY, axis=0)
PSPX=PSAX[:51]
PSPX[1:50] = (PSAX[-1:50:-1]+PSAX[1:50])/2
PSPY=PSAY[:51]
PSPY[1:50] = (PSAY[-1:50:-1]+PSAY[1:50])/2

kw, psd_v = scipy.signal.welch(sub_C, 1, axis=0, window='hann')
kw, psd_u = scipy.signal.welch(sub_C, 1, axis=1, window='hann')
psa_v = np.mean(psd_v, axis=1)  # actually x
psa_u = np.mean(psd_u, axis=0)  # actually y

ka, pad_v = scipy.signal.welch(sub_A, 1, axis=0, window='hann')
ka, pad_u = scipy.signal.welch(sub_A, 1, axis=1, window='hann')
pad_v = np.mean(pad_v, axis=1)  # actually x
pad_u = np.mean(pad_u, axis=0)  # actually y

dx=1
K1D = np.fft.fftfreq(N, dx)
K2D = np.meshgrid(K1D, K1D)
K1P = np.abs(K1D[:51])

knorm = np.sqrt(K2D[0]**2 +K2D[1]**2)
isort= np.argsort(knorm.flatten())
knorp=knorm.flatten()[isort]
PSDP=PSD2.flatten()[isort]

kbins = np.arange(0.5, N/2., 1.)/(dx*N/np.sqrt(2))
kvals = 0.5 * (kbins[1:] + kbins[:-1])

Abins, _, _ = scipy.stats.binned_statistic(knorm.flatten(), PSD2.flatten(), statistic = "mean",bins = kbins)
print('Abins', Abins)
Bbins, _, _ = scipy.stats.binned_statistic(knorm.flatten(), PSD2A.flatten(), statistic = "mean",bins = kbins)
Xbins, _, _ = scipy.stats.binned_statistic(np.abs(K1D), PSAX, statistic = "mean",bins = kbins)
Ybins, _, _ = scipy.stats.binned_statistic(np.abs(K1D), PSAY, statistic = "mean",bins = kbins)

fig,axe = plt.subplots()
axe.loglog(kvals, Abins/N**2, color='k', label='2D FFT')
axe.loglog(K1P, PSPX/N, color='r', linestyle='--',label='FFT-X avg(psd)')
axe.loglog(K1P, PSPY/N, color='b', linestyle='--',label='FFT-Y avg(psd)')
axe.loglog(kw, psa_v, color='m', linestyle=':', label='Welch PSD X')
axe.loglog(kw, psa_u, color='c', linestyle=':', label='Welch PSD Y')
axe.legend()
axe.set_ylim([1e-10, 2])
axe.set_title("Plot with 2D FFT and Welch")
fig.savefig('PSDD_Hann/PSD_EG1.png')
plt.close()

fig,axe = plt.subplots()
axe.loglog(K1P, PSPX/N, color='r', label='FFT-X avg(psd)')
axe.loglog(K1P, PSPY/N, color='b', label='FFT-Y avg(psd)')
axe.loglog(kw, psa_v, color='m', linestyle='--', label='Welch PSD X')
axe.loglog(kw, psa_u, color='c', linestyle='--', label='Welch PSD Y')
axe.legend()
axe.set_ylim([1e-10, 2])
axe.set_title("Only 1D FFT vs Welch")
fig.suptitle("FFT Normalized by N")
fig.savefig('PSDD_Hann/PSD_EG3.png')
plt.close()

fig,axe = plt.subplots()
axe.loglog(kw, psa_v, color='r', linestyle='-', label='Shapiroed PSD X')
axe.loglog(kw, psa_u, color='b', linestyle='-', label='Shapiroed PSD Y')
axe.loglog(kw, pad_v, color='c', linestyle='--', label='Random PSD X')
axe.loglog(kw, pad_u, color='m', linestyle='--', label='Random PSD Y')
axe.legend()
axe.set_ylim([1e-10, 2])
axe.set_title("Only Welch")
fig.savefig('PSDD_Hann/PSD_EGW.png')
plt.close()

fig,axe = plt.subplots()
axe.loglog(K1P, PSPX/N, color='r', linestyle='-', label='Shapiroed FFT-X')
axe.loglog(K1P, PSPY/N, color='b', linestyle='-', label='Shaoiroed FFT-Y')
axe.loglog(K1P, PSRX/N, color='m', linestyle='--', label='Random FFT-X')
axe.loglog(K1P, PSRY/N, color='c', linestyle='--', label='Random FFT-Y')
axe.legend()
axe.set_ylim([1e-10, 2])
axe.set_title("Only FFT")
fig.savefig('PSDD_Hann/PSD_EGF.png')
plt.close()

fig,axe = plt.subplots()
axe.loglog(kvals, Abins/N**2, color='k', linestyle='-', label='Shapiroed 2D FFT')
axe.loglog(kvals, Bbins/N**2, color='g', linestyle='--', label='Random 2D FFT')
axe.legend()
axe.set_ylim([1e-10, 2])
axe.set_title("Only 2D-FFT")
fig.savefig('PSDD_Hann/PSD_EGD.png')
plt.close()

fig,axe = plt.subplots()
axe.semilogx(kvals, Abins/Bbins, color='k', linestyle='-', label='Ratio 2D FFT')
axe.semilogx(K1P, PSPX/PSRX, color='r', linestyle='-', label='Ratio FFT-X')
axe.semilogx(K1P, PSPY/PSRY, color='b', linestyle='-', label='Ratio FFT-Y')
axe.semilogx(K1P, psa_u/pad_u, color='m', linestyle='--', label='Ratio Welch-X')
axe.semilogx(K1P, psa_v/pad_v, color='c', linestyle='--', label='Ratio Welch-Y')
axe.legend()
axe.set_ylim([1e-10, 2])
axe.set_title("Ratios Shapiro/Random")
fig.savefig('PSDD_Hann/PSD_EGR.png')
plt.close()
