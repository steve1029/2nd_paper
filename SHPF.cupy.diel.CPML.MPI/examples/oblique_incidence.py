#!/usr/bin/env python
import os, time, datetime, sys, psutil
import matplotlib
matplotlib.use('Agg')
import numpy as np
from mpi4py import MPI
import matplotlib.pyplot as plt
from scipy.constants import c
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import source, space, plotfield, structure, collector

#------------------------------------------------------------------#
#--------------------- Space object settings ----------------------#
#------------------------------------------------------------------#

savedir = '/home/ldg/2nd_paper/SHPF.cupy.diel.CPML.MPI/'

nm = 1e-9
um = 1e-6

Nx, Ny, Nz = 128, 128, 128
dx, dy, dz = 10*um, 10*um, 10*um
Lx, Ly, Lz = Nx*dx, Ny*dy, Nz*dz

courant = 1./4
dt = courant * min(dx,dy,dz) / c
Tsteps = int(sys.argv[1])

TF = space.Basic3D((Nx, Ny, Nz), (dx, dy, dz), dt, Tsteps, np.complex64, np.complex64, method='SHPF', engine='cupy')

TF.malloc()

########## Set PML and PBC
TF.set_PML({'x':'','y':'','z':'+-'}, 10)

region = {'x':True, 'y':True, 'z':False}
TF.apply_BPBC(region, BBC=True, PBC=False)

########## Save PML data.
#TF.save_pml_parameters('./')

#------------------------------------------------------------------#
#--------------------- Source object settings ---------------------#
#------------------------------------------------------------------#

########## Gaussian source
#wvc = 300*um
#interval = 2
#spread   = 0.3
#pick_pos = 2000
#wvlens = np.arange(200,600, interval)*um
#freqs = c / wvlens
#np.save("../graph/freqs", freqs)

#src = source.Gaussian(dt, wvc, spread, pick_pos, dtype=np.float32)
#src.plot_pulse(Tsteps, freqs, savedir)
#wvlen = 300*um

########## Sine source
#smth = source.Smoothing(dt, 1000)
#src = source.Sine(dt, np.float64)
#wvlen = 300*um
#freqs = c / wvlen
#src.set_wvlen(wvlen)

########## Harmonic source
smth = source.Smoothing(dt, 2000)
src = source.Harmonic(dt)
wvlen = 320*um
freqs = c / wvlen
src.set_wvlen(wvlen)

########## Delta source
#src = source.Delta(1000)
#wvlen = 300*um

########## Momentum of the source.
# mmt for plane wave normal to x axis
# phi is the angle between k0 vector and xz-plane.
# theta is the angle between k0cos(phi) and x-axis.
#k0 = 2*np.pi / wvlen
#phi, theta = 0*np.pi/180, 30*np.pi/180
#phi, theta = 0, 0
#kx = k0 * np.cos(phi) * np.cos(theta)
#ky = k0 * np.sin(phi)
#kz = k0 * np.cos(phi) * np.sin(theta)

# mmt for plane wave normal to y axis
# phi is the angle between k0 vector and xy-plane.
# theta is the angle between k0cos(phi) and y-axis.
#k0 = 2*np.pi / wvlen
#phi, theta = 0*np.pi/180, 30*np.pi/180
#phi, theta = 0, 0
#kx = k0 * np.cos(phi) * np.sin(theta)
#ky = k0 * np.cos(phi) * np.cos(theta)
#kz = k0 * np.sin(phi)

# mmt for plane wave normal to z axis
# phi is the angle between k0 vector and yz-plane.
# theta is the angle between k0cos(phi) and z-axis.
k0 = 2*np.pi / wvlen
phi, theta = 60*np.pi/180, 0*np.pi/180
#phi, theta = 0, 0
kx = k0 * np.sin(phi)
ky = k0 * np.cos(phi) * np.sin(theta)
kz = k0 * np.cos(phi) * np.cos(theta)

mmt = (kx, ky, kz)

########## Plane wave normal to x-axis.
#setter = source.Setter(TF, (200*um, 0, 0), (210*um, Ly, Lz), mmt)

########## Plane wave normal to y-axis.
#setter = source.Setter(TF, (0, 400*um, 0), (Lx, 410*um, Lz), mmt)

########## Plane wave normal to z-axis.
setter = source.Setter(TF, (0, 0, 200*um), (Lx, Ly, 210*um), mmt)

########## Line src along y-axis.
"""
setter1 = source.Setter(TF, (400*um, 0, 200*um), (410*um, Ly, 210*um), mmt)
setter2 = source.Setter(TF, (400*um, 0, 300*um), (410*um, Ly, 310*um), mmt)
setter3 = source.Setter(TF, (400*um, 0, 400*um), (410*um, Ly, 410*um), mmt)
setter4 = source.Setter(TF, (400*um, 0, 500*um), (410*um, Ly, 510*um), mmt)
setter5 = source.Setter(TF, (400*um, 0, 600*um), (410*um, Ly, 610*um), mmt)
setter6 = source.Setter(TF, (400*um, 0, 700*um), (410*um, Ly, 710*um), mmt)
setter7 = source.Setter(TF, (400*um, 0, 800*um), (410*um, Ly, 810*um), mmt)
setter8 = source.Setter(TF, (400*um, 0, 900*um), (410*um, Ly, 910*um), mmt)
"""

########## Line src along z-axis.
#TF.set_src_pos((xpos, ypos, 0), (xpos+1, ypos+1, Nz))

########## Point src at the center.
#setter = source.Setter(TF, (xpos, ypos, zpos), (xpos+dx, ypos+dy, zpos+dz), mmt)

#------------------------------------------------------------------#
#-------------------- Structure object settings -------------------#
#------------------------------------------------------------------#

########## Box
#srt = ( 800*um,    0*um,    0*um)
#end = (1000*um, 1280*um, 1280*um)
#box = structure.Box(TF, srt, end, 4., 1.)

########## Cylinder
radius = 50*um
height = (0*um, Ly)
center1 = ( 300*um, 640*um)
center2 = ( 500*um, 640*um)
center3 = ( 700*um, 640*um)
center4 = ( 900*um, 640*um)
center5 = (1100*um, 640*um)
#cylinder1 = structure.Cylinder(TF, 'y', radius, height, center1, 8.9, 1.)
#cylinder2 = structure.Cylinder(TF, 'y', radius, height, center2, 8.9, 1.)
#cylinder3 = structure.Cylinder(TF, 'y', radius, height, center3, 8.9, 1.)
#cylinder4 = structure.Cylinder(TF, 'y', radius, height, center4, 8.9, 1.)
#cylinder5 = structure.Cylinder(TF, 'y', radius, height, center5, 8.9, 1.)

########## Save eps, mu data.
#TF.save_eps_mu(savedir)

#------------------------------------------------------------------#
#-------------------- Collector object settings -------------------#
#------------------------------------------------------------------#

loc = (900*um, 640*um, 640*um)
#field_at_point = collector.FieldAtPoint("fap1", "../graph/fap", TF, loc, freqs, 'cupy')

#------------------------------------------------------------------#
#-------------------- Graphtool object settings -------------------#
#------------------------------------------------------------------#

# Set plotfield options
plot_per = 30
TFgraphtool = plotfield.Graphtool(TF, 'TF', savedir)

#------------------------------------------------------------------#
#------------------------ Time loop begins ------------------------#
#------------------------------------------------------------------#

# Save what time the simulation begins.
start_time = datetime.datetime.now()

# time loop begins
for tstep in range(Tsteps):

    # At the start point
    if tstep == 0:
        TF.MPIcomm.Barrier()
        if TF.MPIrank == 0:
            print("Total time step: %d" %(TF.tsteps))
            print(("Size of a total field array : %05.2f Mbytes" %(TF.TOTAL_NUM_GRID_SIZE)))
            print("Simulation start: {}".format(datetime.datetime.now()))
        
    # pulse for gaussian wave
    #pulse_re = src.pulse_re(tstep)
    #pulse_re = src.apply(tstep)

    # pulse for sine or harmonic wave
    pulse_re = src.signal(tstep) * smth.apply(tstep)
    #pulse_re = src.signal(tstep)
    setter.put_src('Ey', pulse_re, 'soft')

    TF.updateH(tstep)
    TF.updateE(tstep)

    #field_at_point.get_field(tstep)

    # Plot the field profile
    if tstep % plot_per == 0:

        Ey = TFgraphtool.gather('Ey')
        #TFgraphtool.plot2D3D(Ex, tstep, yidx=TF.Nyc, colordeep=2., stride=1, zlim=2.)
        TFgraphtool.plot2D3D(Ey, tstep, yidx=TF.Nyc, colordeep=2., stride=2, zlim=2.)
        #TFgraphtool.plot2D3D(Ey, tstep, zidx=TF.Nzc, colordeep=2., stride=2, zlim=2.)
        #TFgraphtool.plot2D3D(Ez, tstep, xidx=TF.Nxc, colordeep=.1, stride=1, zlim=.1)
        #TFgraphtool.plot2D3D(Hx, tstep, xidx=TF.Nxc, colordeep=.1, stride=1, zlim=.1)
        #TFgraphtool.plot2D3D(Hy, tstep, xidx=TF.Nxc, colordeep=.1, stride=1, zlim=.1)
        #TFgraphtool.plot2D3D(Hz, tstep, xidx=TF.Nxc, colordeep=.1, stride=1, zlim=.1)

        #Ez = TFgraphtool.gather('Ez')
        #TFgraphtool.plot2D3D(Ex, tstep, yidx=TF.Nzc, colordeep=2., stride=1, zlim=2.)
        #TFgraphtool.plot2D3D(Ey, tstep, yidx=TF.Nyc, colordeep=1., stride=2, zlim=1.)
        #TFgraphtool.plot2D3D(Ez, tstep, zidx=TF.Nzc, colordeep=2., stride=1, zlim=2.)
        #TFgraphtool.plot2D3D(Hx, tstep, xidx=TF.Nxc, colordeep=.1, stride=1, zlim=.1)
        #TFgraphtool.plot2D3D(Hy, tstep, xidx=TF.Nxc, colordeep=.1, stride=1, zlim=.1)
        #TFgraphtool.plot2D3D(Hz, tstep, xidx=TF.Nxc, colordeep=.1, stride=1, zlim=.1)

        #Ey = IFgraphtool.gather('Ey')
        #IFgraphtool.plot2D3D(Ex, tstep, yidx=TF.Nyc, colordeep=2., stride=1, zlim=2.)
        #IFgraphtool.plot2D3D(Ey, tstep, yidx=IF.Nyc, colordeep=2., stride=1, zlim=2.)
        #IFgraphtool.plot2D3D(Ez, tstep, xidx=TF.Nxc, colordeep=.1, stride=1, zlim=.1)
        #IFgraphtool.plot2D3D(Hx, tstep, xidx=TF.Nxc, colordeep=.1, stride=1, zlim=.1)
        #IFgraphtool.plot2D3D(Hy, tstep, xidx=TF.Nxc, colordeep=.1, stride=1, zlim=.1)
        #IFgraphtool.plot2D3D(Hz, tstep, xidx=TF.Nxc, colordeep=.1, stride=1, zlim=.1)

        #Ey = SFgraphtool.gather('Ey')
        #SFgraphtool.plot2D3D(Ex, tstep, yidx=TF.Nyc, colordeep=2., stride=1, zlim=2.)
        #SFgraphtool.plot2D3D(Ey, tstep, yidx=SF.Nyc, colordeep=2., stride=1, zlim=2.)
        #SFgraphtool.plot2D3D(Ez, tstep, xidx=TF.Nxc, colordeep=.1, stride=1, zlim=.1)
        #SFgraphtool.plot2D3D(Hx, tstep, xidx=TF.Nxc, colordeep=.1, stride=1, zlim=.1)
        #SFgraphtool.plot2D3D(Hy, tstep, xidx=TF.Nxc, colordeep=.1, stride=1, zlim=.1)
        #SFgraphtool.plot2D3D(Hz, tstep, xidx=TF.Nxc, colordeep=.1, stride=1, zlim=.1)

        if TF.MPIrank == 0:

            interval_time = datetime.datetime.now()
            print(("time: %s, step: %05d, %5.2f%%" %(interval_time-start_time, tstep, 100.*tstep/TF.tsteps)))

#------------------------------------------------------------------#
#--------------------------- Data analysis ------------------------#
#------------------------------------------------------------------#

#field_at_point.get_spectrum()
#field_at_point.plot_spectrum()

#------------------------------------------------------------------#
#------------------- Record simulation history --------------------#
#------------------------------------------------------------------#

if TF.MPIrank == 0:

    # Simulation finished time
    finished_time = datetime.datetime.now()

    # Record simulation size and operation time
    if not os.path.exists("../record") : os.mkdir("../record")
    record_path = "../record/record_%s.txt" %(datetime.date.today())

    if not os.path.exists(record_path):
        f = open( record_path,'a')
        f.write("{:4}\t{:4}\t{:4}\t{:4}\t{:4}\t\t{:4}\t\t{:4}\t\t{:8}\t{:4}\t\t\t\t{:12}\t{:12}\n\n" \
            .format("Node","Nx","Ny","Nz","dx","dy","dz","tsteps","Time","VM/Node(GB)","RM/Node(GB)"))
        f.close()

    me = psutil.Process(os.getpid())
    me_rssmem_GB = float(me.memory_info().rss)/1024/1024/1024
    me_vmsmem_GB = float(me.memory_info().vms)/1024/1024/1024

    cal_time = finished_time - start_time
    f = open( record_path,'a')
    f.write("{:2d}\t\t{:04d}\t{:04d}\t{:04d}\t{:5.2e}\t{:5.2e}\t{:5.2e}\t{:06d}\t\t{}\t\t{:06.3f}\t\t\t{:06.3f}\n" \
                .format(TF.MPIsize, TF.Nx, TF.Ny, TF.Nz,\
                    TF.dx, TF.dy, TF.dz, TF.tsteps, cal_time, me_vmsmem_GB, me_rssmem_GB))
    f.close()
    
    print("Simulation finished: {}".format(datetime.datetime.now()))
