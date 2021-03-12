#!/usr/bin/env python
import os, sys
import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
from scipy.constants import c
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import analyzer as az

um = 1e-6
nm = 1e-9

Lx, Ly, Lz = 574/256*nm, 574*nm, 574*nm
Nx, Ny, Nz = 1, 256, 256
dx, dy, dz = Lx/Nx, Ly/Ny, Lz/Nz 

courant = 1./4
dt = courant * min(dx,dy,dz) /c

Q = 30
E = 1e-4
nf = 100
fmin = -5e14 
fmax = +5e14

loaddir = '/home/ldg/2nd_paper/SHPF.cupy.diel.CPML.MPI/graph/{}/' .format(sys.argv[1])
savedir = loaddir

names = ['fap1', 'fap2', 'fap3', 'fap4', 'fap5']
#names = ['fap1', 'fap2', 'fap3', 'fap4']
#names = ['fap1']

xlim = [-1,1]
ylim = [0,1]

where = 'Ez'
test = az.CsvCreator(loaddir, names, dt, Ly, where)
test.get_fft_plot_csv(2, 'TM', where, xlim, ylim, [])
test.get_pharminv_csv('Ez', 'fap1', 200001, dt, fmin, fmax, nf)
#test.get_pharminv_csv('Hx', 'fap1', 200001, dt, fmin, fmax, nf)
#test.get_pharminv_csv('Hy', 'fap1', 200001, dt, fmin, fmax, nf)
