import time, os, datetime, sys, ctypes, psutil
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpi4py import MPI
from mpl_toolkits.mplot3d import axes3d
from mpl_toolkits.axes_grid1 import make_axes_locatable
from scipy.constants import c, mu_0, epsilon_0
import numpy as np
import cupy as cp
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import source, space, plotfield, structure, rft

#------------------------------------------------------------------#
#----------------------- Paramter settings ------------------------#
#------------------------------------------------------------------#
savedir = '/home/ldg/2nd_paper/SHPF.cupy.diel.CPML.MPI/'

nm = 1e-9
um = 1e-6

Lx, Ly, Lz = 128*10*um, 128*10*um, 128*10*um
Nx, Ny, Nz = 128, 128, 128
dx, dy, dz = Lx/Nx, Ly/Ny, Lz/Nz

courant = 1./4
dt = courant * min(dx,dy,dz) / c
Tstep = 2000

wvc = 300*um
interval = 2
spread   = 0.3
pick_pos = 1000
plot_per = 30

wvlens = np.arange(200, 600, interval) * um
freqs = c / wvlens
np.save("../graph/freqs", freqs)

#------------------------------------------------------------------#
#-------------------------- Call objects --------------------------#
#------------------------------------------------------------------#

FDTDspace = space.Basic3D((Nx,Ny,Nz), (dx,dy,dz), dt, Tstep, np.complex64, np.complex64, method='FDTD', engine='cupy')
PSTDspace = space.Basic3D((Nx,Ny,Nz), (dx,dy,dz), dt, Tstep, np.complex64, np.complex64, method='PSTD', engine='cupy')
Diffspace = space.Empty3D((Nx,Ny,Nz), (dx,dy,dz), dt, Tstep, np.complex64, np.complex64)

FDTDspace.malloc()
PSTDspace.malloc()

# Put structures
#Box1_srt = (round(222*um/dx), round( 0*um/dy), round(  0*um/dz))
#Box1_end = (round(272*um/dx), round(96*um/dy), round( 96*um/dz))
#Box = structure.Box(FDTDspace, Box1_srt, Box1_end, 4., 1.)

# Set PML and PBC
FDTDspace.set_PML({'x':'+-','y':'','z':''}, 10)
PSTDspace.set_PML({'x':'+-','y':'','z':''}, 10)

# Save eps, mu and PML data.
#FDTDspace.save_PML_parameters('./')
#FDTDspace.save_eps_mu(savedir)

# Set the type of input source.
smoothing = source.Smoothing(dt, 1000)
#Src = source.Gaussian(dt, wvc, spread, pick_pos, np.float64)
#Src.plot_pulse(Tstep, freqs, savedir)
Src = source.Harmonic(dt)
wvlen = 300*um
Src.set_wvlen(wvlen)

# Set source position.
#src_xpos = int(Nx/2)
src_xpos = 50
src_ypos = 50

# Momentum of the source.
# mmt for plane wave normal to x axis
# phi is the angle between k0 vector and xz-plane.
# theta is the angle between k0cos(phi) and x-axis.
k0 = 2*np.pi / wvlen
phi, theta = 0*np.pi/180, -30*np.pi/180
#phi, theta = 0, 0
kx = k0 * np.cos(phi) * np.cos(theta)
ky = k0 * np.sin(phi)
kz = k0 * np.cos(phi) * np.sin(theta)

# mmt for plane wave normal to y axis
# phi is the angle between k0 vector and xy-plane.
# theta is the angle between k0cos(phi) and y-axis.
#k0 = 2*np.pi / wvlen
#phi, theta = 20*np.pi/180, 0*np.pi/180
#kx = k0 * np.cos(phi)* np.sin(theta)
#ky = k0 * np.cos(phi)* np.cos(theta)
#kz = k0 * np.sin(phi)

# mmt for plane wave normal to z axis
# phi is the angle between k0 vector and yz-plane.
# theta is the angle between k0cos(phi) and y-axis.
#k0 = 2*np.pi / wvlen
#phi, theta = 0*np.pi/180, 30*np.pi/180
#kx = k0 * np.sin(phi)
#ky = k0 * np.cos(phi)* np.sin(theta)
#kz = k0 * np.cos(phi)* np.cos(theta)

#mmt = (0, 0, 0)
mmt = (kx, ky, kz)
#mmt = (0, ky, 0)
#mmt = (0, 0, kz)

region = {'x':False, 'y':False, 'z':True}
FDTDspace.apply_BPBC(region, BBC=True, PBC=False)
PSTDspace.apply_BPBC(region, BBC=True, PBC=False)

# plain wave normal to x.
FDTDspace.set_src((src_xpos, 0, 0), (src_xpos+1, Ny, Nz), mmt) # Plane wave for Ey, x-direction.
PSTDspace.set_src((src_xpos, 0, 0), (src_xpos+1, Ny, Nz), mmt) # Plane wave for Ey, x-direction.

# plain wave normal to y.
#FDTDspace.set_src((1, src_ypos, 0), (Nx, src_ypos+1, Nz-0), mmt) # Plane wave for Ez, y-direction.

# plain wave normal to z.
#FDTDspace.set_src((0, 0, 40), (Nx, Ny, 41), mmt) # Plane wave for Ez, y-direction.

# Line source along y axis.
#FDTDspace.set_src((src_xpos, 0, FDTDspace.Nzc), (src_xpos+1, FDTDspace.Ny, FDTDspace.Nzc+1))

# Line source along z axis.
#FDTDspace.set_src((src_xpos, FDTDspace.Nyc, 0), (src_xpos+1, FDTDspace.Nyc+1, FDTDspace.Nz))

# Set Poynting vector calculator.
leftx, rightx = int(Nx/4), int(Nx*3/4)
lefty, righty = int(Ny/4), int(Ny*3/4)
leftz, rightz = int(Nz/4), int(Nz*3/4)

#Sx_R_getter = rft.Sx("SF_R", "./graph/Sx", FDTDspace, (rightx, lefty, leftz), (rightx+1, righty, rightz), freqs, 'cupy')

# Set plotfield options
FDTDgraphtool = plotfield.Graphtool(FDTDspace, 'FDTD', savedir)
PSTDgraphtool = plotfield.Graphtool(PSTDspace, 'PSTD', savedir)
Diffgraphtool = plotfield.Graphtool(Diffspace, 'Diff', savedir)

# Save what time the simulation begins.
start_time = datetime.datetime.now()

# time loop begins
for tstep in range(FDTDspace.tsteps+1):

    # At the start point
    if tstep == 0:
        FDTDspace.MPIcomm.Barrier()
        if FDTDspace.MPIrank == 0:
            print("Total time step: %d" %(FDTDspace.tsteps))
            print(("Size of a total field array : %05.2f Mbytes" %(FDTDspace.TOTAL_NUM_GRID_SIZE)))
            print("Simulation start: {}".format(datetime.datetime.now()))
        
    #pulse = Src.pulse_re(tstep, pick_pos)
    pulse = Src.signal(tstep) * smoothing.apply(tstep)
    #pulse = Src.signal(tstep)

    #FDTDspace.put_src('Ex', pulse, 'soft')
    FDTDspace.put_src('Ey', pulse, 'soft')
    PSTDspace.put_src('Ey', pulse, 'soft')
    #FDTDspace.put_src('Ez', pulse, 'soft')

    FDTDspace.updateH(tstep)
    PSTDspace.updateH(tstep)

    FDTDspace.updateE(tstep)
    PSTDspace.updateE(tstep)

    Diffspace.get_SF(PSTDspace, FDTDspace)

    #Sx_R_calculator.do_RFT(tstep)

    # Plot the field profile
    if tstep % plot_per == 0:

        #Ex = graphtool.gather('Ex')
        #graphtool.plot2D3D(Ex, tstep, xidx=FDTDspace.Nxc, colordeep=3., stride=2, zlim=3.)

        Ey = Diffgraphtool.gather('Ey')
        Diffgraphtool.plot2D3D(Ey, tstep, yidx=FDTDspace.Nyc, colordeep=2., stride=2, zlim=2.)
        Ey = FDTDgraphtool.gather('Ey')
        FDTDgraphtool.plot2D3D(Ey, tstep, yidx=FDTDspace.Nyc, colordeep=2., stride=2, zlim=2.)
        Ey = PSTDgraphtool.gather('Ey')
        PSTDgraphtool.plot2D3D(Ey, tstep, yidx=FDTDspace.Nyc, colordeep=2., stride=2, zlim=2.)
        #graphtool.plot2D3D(Ey, tstep, zidx=FDTDspace.Nzc, colordeep=3., stride=2, zlim=3.)
        
        #Ez = graphtool.gather('Ez')
        #graphtool.plot2D3D(Ez, tstep, xidx=FDTDspace.Nxc, colordeep=3., stride=2, zlim=3.)
        #graphtool.plot2D3D(Ez, tstep, zidx=FDTDspace.Nzc, colordeep=3., stride=2, zlim=3.)

        if FDTDspace.MPIrank == 0:

            interval_time = datetime.datetime.now()
            print(("time: %s, step: %05d, %5.2f%%" %(interval_time-start_time, tstep, 100.*tstep/FDTDspace.tsteps)))

#Sx_R_calculator.get_Sx()

if FDTDspace.MPIrank == 0:

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
                .format(FDTDspace.MPIsize, FDTDspace.Nx, FDTDspace.Ny, FDTDspace.Nz,\
                    FDTDspace.dx, FDTDspace.dy, FDTDspace.dz, FDTDspace.tsteps, cal_time, me_vmsmem_GB, me_rssmem_GB))
    f.close()
    
    print("Simulation finished: {}".format(datetime.datetime.now()))
