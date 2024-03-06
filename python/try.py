import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as tk

def inverse(x):
    """Vectorized 1/x, treating x==0 manually"""
    x = np.array(x, float)
    near_zero = np.isclose(x, 0)
    x[near_zero] = np.inf
    x[~near_zero] = 1 / x[~near_zero]
    return x


def forlog(x):
    y = np.log10(inverse(x))
    return y
    

def baclog(x):
    y = inverse(10**x)
    return y
    
def adjust_axis(taxe):
    #taxe.set_xscale('function', functions=(forlog, baclog))
    taxe.xaxis.set_major_formatter(tk.NullFormatter())
    taxe.xaxis.set_minor_formatter(tk.NullFormatter())
    taxe.set_xlim([1.0e-3, 1.0])
    taxe.set_ylim([0, 3])
    taxe.set_xticks([])
    taxe.set_xticks([], minor=True)
    taxe.set_xticks(np.flip(inverse([10**(1.0*ii) for ii in range(0,4)])))
    taxe.set_xticks(np.flip(inverse(np.concatenate([np.arange(2,10)*10**(1*ii) for ii in range(0,3)]))), minor=True)
    Xxticks = taxe.get_xticks()
    Mxticks = taxe.get_xticks(minor=True)
    print(Xxticks)
    OldXlabels = taxe.get_xticklabels()
    NewXxticks = inverse(Xxticks)
    NewXlabels = [ str(int(round(xtick))) for xtick in NewXxticks]
    print(OldXlabels, NewXlabels)
    print('old labels', taxe.get_xticklabels())
    taxe.set_xticklabels(NewXlabels)
    print('new labels', taxe.get_xticklabels())
    taxe.set_xlabel('Wavelength')
    return taxe

    
x = np.arange(1,301) / 100
y = 10**(-1.0*x)

fig,axe = plt.subplots()

axe.semilogx(y, x)

naxe=adjust_axis(axe)
print(axe.get_xticklabels())
print(axe.get_xticks())
print(axe.get_xticks(minor=True))

print(axe)
print(naxe)
print(axe == naxe)
fig.savefig('try.png')
plt.close(fig)

