import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.misc import derivative
from scipy.special import spherical_jn
from scipy.special import spherical_yn

fig = plt.figure(figsize=[4,4])

n = 1.0
xrad1 = 20.E-7; yrad1 = 20.E-7; zrad1 = 70.E-7
xrad2 = 20.E-7; yrad2 = 20.E-7; zrad2 = 50.E-7


# radii2 = 5E-7
gap = 10.E-7


######### SIMULATION #########
##############################
# shape_bothstring = str(int(radii1*10**7))+str('nm')+str(int(radii2*10**7))+str('nm_')+str(int(gap*10**7))+str('nm')
shape_onestring = str(int(xrad1*10**7))+str('_')+str(int(yrad1*10**7))+str('_')+str(int(zrad1*10**7))

# shape_twostring = str(int(radii2*10**7))+str('nmsph144')
shape_bothstring = str(int(xrad1*10**7))+str(int(yrad1*10**7))+str(int(zrad1*10**7)) + \
                  str('_')+str(int(xrad2*10**7))+str(int(yrad2*10**7))+str(int(zrad2*10**7)) +str('_')+str(int(gap*10**7))


# def plot_onespectra(src, shape, diel_data, n):
#     if shape == shape_onestring:
#         filename = str('simulated_spectra/single_ellipsoid/')+str('Spectrum_')+str(src)+str('_')+str(shape)+str('_')+str(diel_data)+str('_')+str(n)

#     if shape == shape_twostring:
#         filename = str('simulated_spectra/single_sphere/')+str('Spectrum_')+str(src)+str('_')+str(shape)+str('_')+str(diel_data)+str('_')+str(n)
#     data = np.loadtxt(filename,skiprows=1)
#     energy = data[:,0]
#     ext_cross = data[:,1]
#     abs_cross = data[:,2]
#     sca_cross = data[:,3]
#     plt.plot(energy, ext_cross, 'k',alpha=.5,label='bem ext')
#     plt.plot(energy, abs_cross, 'r',alpha=.5,label='bem abs')
#     plt.plot(energy, sca_cross, 'b',alpha=.5,label='bem sca')

def plot_twospectra(src, shape, diel_data, n):
    filename = str('simulated_spectra/two_ellipsoids/')+str('Spectrum_')+str(src)+str('_')+str(shape)+str('_')+str(diel_data)+str('_')+str(n)#+str('_y')
    data = np.loadtxt(filename,skiprows=1)
    energy = data[:,0]
    ext_cross = data[:,1]
    abs_cross = data[:,2]
    sca_cross = data[:,3]

    plt.plot(energy, ext_cross, 'k',alpha=.5,label='bem ext')
    plt.plot(energy, abs_cross, 'r',alpha=.5,label='bem abs')
    plt.plot(energy, sca_cross, 'b',alpha=.5,label='bem sca')

    # plt.plot(energy, ext_cross/max(ext_cross), label=str(shape)[:-3]+str('sim'))
    # plt.plot(energy, sca_cross/max(sca_cross), label=str(shape)[:-3]+str('sim'))

plot_twospectra(src='bemret', shape=shape_bothstring, diel_data='drude', n=str(n))

# plot_onespectra(src='bemret', shape=shape_onestring, diel_data='drude', n=str(n))
# plot_onespectra(src='bemret', shape=shape_twostring, diel_data='drude', n=str(n))

########################################################
# radii = radii1 # [cm]

eps_b = n**2
e = 4.80326E-10 # elementary charge, [statC, g^1/2 cm^3/2 s^-1]
c = 2.998E+10 # speed of light [cm/s]
hbar_eVs = 6.58212E-16 # Planck's constant [eV*s]
wp = 8.959/hbar_eVs # [1/s], bulk plasma frequency 

eps_inf = 9.695 # [unitless], static dielectric response of ionic background 
gamNR_qs = 0.073/hbar_eVs # [1/s]

N = 2 # number of particles
center_1 = np.array([ [0], [0], [-zrad1-gap/2] ])
center_2 = np.array([ [0], [0], [ zrad2+gap/2] ])
# center_2 = np.array([ [0], [ radii2+gap/2], [0] ])

centers = np.zeros((3*N, 1))
all_radii = np.zeros((3*N, 1))

centers[0:3,:] = center_1; centers[3:6,:] = center_2
# all_radii[0:3,:] = radii1; #all_radii[3:6,:] = radii2
all_radii[0,:] = xrad1; all_radii[1,:] = yrad1; all_radii[2,:] = zrad1;
all_radii[3,:] = xrad2; all_radii[4,:] = yrad2; all_radii[5,:] = zrad2;

def psi(rho):
    return rho*spherical_jn(1, rho)

def psi_prime(rho):
    return spherical_jn(1, rho) + rho*spherical_jn(1, rho, derivative=True)

def hankel(rho):
    return spherical_jn(1, rho) + 1j*spherical_yn(1, rho)

def hankel_prime(rho):
    return spherical_jn(1, rho, derivative=True) + 1j*spherical_yn(1, rho,derivative=True)

def xi(rho):
    return rho*hankel(rho)

def xi_prime(rho):
    return hankel(rho) + rho*hankel_prime(rho)

def mie_coefficents(w,radius):
    eps = eps_inf - wp**2/(w**2 + 1j*w*gamNR_qs)
    m = np.sqrt(eps)
    k = w/c
    x = k*radius
    numer_a = m*psi(m*x)*psi_prime(x) - psi(x)*psi_prime(m*x)
    denom_a = m*psi(m*x)*xi_prime(x) - xi(x)*psi_prime(m*x)
    numer_b = psi(m*x)*psi_prime(x) - m*psi(x)*psi_prime(m*x)
    denom_b = psi(m*x)*xi_prime(x) - m*xi(x)*psi_prime(m*x)
    a = numer_a/denom_a
    b = numer_b/denom_b
    return a, b

def alpha0(w,radius,kind): 
    ### assumes z axis is long axis, and y = x 
    k = w/c
    xrad = radius[0]; yrad = radius[1]; zrad = radius[2]
    if xrad == yrad and xrad == zrad and yrad == zrad:
        # it's a sphere
        xrad = radius
        a, b = mie_coefficents(w,radius)
        alpha = 3/(2.*k**3)*1j*(a)#+b) 
    else:
        ### spheroid 
        wp = 8.959/hbar_eVs # [1/s], bulk plasma frequency 
        eps_inf = 9.695 # [unitless], static dielectric response of ionic background 
        gamNR_qs = 0.073/hbar_eVs # [1/s]
        V = 4/3*np.pi*xrad*yrad*zrad
        eps = eps_inf - wp**2/(w**2 + 1j*w*gamNR_qs)
        # cs must equal long axis, a must equal short axis
        cs = zrad; a = yrad
        es = np.sqrt(1 - a**2/cs**2)

        Lz = (1-es**2)/es**2*(-1 + 1/(2*es)*np.log((1+es)/(1-es)))
        Dz = 3./4*((1+es**2)/(1-es**2)*Lz + 1) # [unitless]

        Ly = (1 - Lz )/2
        Dy = a/(2*cs)*(3/es*np.tanh(es)**(-1)-Dz) 

        if kind == 'prolate_alonglong':
            lE = zrad1
            L = Lz
            D = Dz

        if kind == 'prolate_alongshort':
            lE = yrad1
            L = Ly
            D = Dy

        alphaR = V/(4*np.pi)*(eps-1)/(1+L*(eps-1))
        alphaMW = alphaR / (1 - k**2/lE *D*alphaR - 1j*2*k**3/3*alphaR)
        alpha = alphaMW
    return alpha


def A_ij(dip_i, dip_j, k):
    ''' off diagonal block terms in A_tilde '''
    A_ij = np.zeros( (3, 3) ,dtype=complex) 
    r_ij = centers[3*dip_i:3*(dip_i+1),:] - centers[3*dip_j:3*(dip_j+1),:] # [cm], distance between ith and jth dipole 
    r = np.sqrt(r_ij[0]**2+r_ij[1]**2+r_ij[2]**2)
    rx = r_ij[0]; ry = r_ij[1]; rz = r_ij[2]

    A_ij[0,0] = np.exp(1j*k*r)/r**3*(k**2*(rx*rx-r**2) + (1-1j*k*r)/r**2*(-3*rx*rx+r**2))
    A_ij[0,1] = np.exp(1j*k*r)/r**3*(k**2*(rx*ry) + (1-1j*k*r)/r**2*(-3*rx*ry))
    A_ij[0,2] = np.exp(1j*k*r)/r**3*(k**2*(rx*rz) + (1-1j*k*r)/r**2*(-3*rx*rz))

    A_ij[1,0] = A_ij[0,1]
    A_ij[1,1] = np.exp(1j*k*r)/r**3*(k**2*(ry*ry-r**2) + (1-1j*k*r)/r**2*(-3*ry*ry+r**2))
    A_ij[1,2] = np.exp(1j*k*r)/r**3*(k**2*(ry*rz) + (1-1j*k*r)/r**2*(-3*ry*rz))

    A_ij[2,0] = A_ij[0,2]
    A_ij[2,1] = A_ij[1,2]
    A_ij[2,2] = np.exp(1j*k*r)/r**3*(k**2*(rz*rz-r**2) + (1-1j*k*r)/r**2*(-3*rz*rz+r**2))

    return A_ij


def A_ii(dip_i, dip_j, k):
    ''' on diagonal block terms in A_tilde '''
    w = k*c
    A_ii = np.zeros( (3, 3) ,dtype=complex) 

    A_ii[0,0] = alpha0(w=w, radius=all_radii[3*dip_i: 3*dip_i+3], kind='prolate_alongshort')**(-1)
    A_ii[1,1] = alpha0(w=w, radius=all_radii[3*dip_i: 3*dip_i+3],kind='prolate_alongshort')**(-1)
    A_ii[2,2] = alpha0(w=w, radius=all_radii[3*dip_i: 3*dip_i+3],kind='prolate_alonglong')**(-1)
    return A_ii

def A_tilde(w):
    '''A_tilde = [3*N, 3*N]'''
    k = w/c
    A_tilde = np.zeros( (3*N, 3*N) ,dtype=complex) 
    for i in range(0 , N): 
        for j in range(0, N):
            if i == j:  
                A_tilde[3*i : 3*(i+1), 3*i : 3*(i+1)] = A_ii(dip_i=i, dip_j=i, k=k)
            if i != j:
                A_tilde[3*i : 3*(i+1), 3*j : 3*(j+1)] = A_ij(dip_i=i, dip_j=j, k=k)
    return A_tilde

# print(A_tilde(w=2.5/hbar_eVs))
# print(np.linalg.inv(A_tilde(w=2.5/hbar_eVs)))

def P_tilde(w):
    E0_tilde = np.zeros((3*N, 1))
    P_tilde = np.zeros((3*N, 1),dtype=complex)

    Ex = 0; Ey = 0; Ez = 1

    for i in range(0, N):
        E0_tilde[3*i,:] = Ex
        E0_tilde[3*i+1,:] = Ey
        E0_tilde[3*i+2,:] = Ez
    P_tilde = np.linalg.solve(A_tilde(w), E0_tilde)
    return P_tilde

def dda_abs_cross_mie_polariz(w):
    ''' Works for spheres up to 50 nm radii, and in the window < 3.0 eV '''
    k = w/c
    P = P_tilde(w=w)
    P1 = P[0:3,:]
    P2 = P[3:6,:]
    E1 = np.zeros((3, 1),dtype=complex); E2 = np.zeros((3, 1),dtype=complex)
    E1[0,0] = alpha0(w=w, radius=all_radii[0 : 3],kind='prolate_alongshort')**(-1)*P1[0,0]
    E1[1,0] = alpha0(w=w, radius=all_radii[0 : 3],kind='prolate_alongshort')**(-1)*P1[1,0]
    E1[2,0] = alpha0(w=w, radius=all_radii[0 : 3],kind='prolate_alonglong')**(-1)*P1[2,0]

    E2[0,0] = alpha0(w=w, radius=all_radii[3 : 6],kind='prolate_alongshort')**(-1)*P2[0,0]
    E2[1,0] = alpha0(w=w, radius=all_radii[3 : 6],kind='prolate_alongshort')**(-1)*P2[1,0]
    E2[2,0] = alpha0(w=w, radius=all_radii[3 : 6],kind='prolate_alonglong')**(-1)*P2[2,0]
    # E2 = alpha0(w=w, radius=all_radii[3,0])**(-1)*P2

    ext_cross_1 = 4*np.pi*k*np.imag( np.sum( P1*np.conj(E1)) ) *10**8
    sca_cross_1 = 4*np.pi*k*2/3*k**3*np.real( np.sum(P1*np.conj(P1)) ) *10**8  
    abs_cross_1 = ext_cross_1 - sca_cross_1

    ext_cross_2 = 4*np.pi*k*np.imag( np.sum( P2*np.conj(E2)) ) *10**8
    sca_cross_2 = 4*np.pi*k*2/3*k**3*np.real( np.sum(P2*np.conj(P2)) ) *10**8  
    abs_cross_2 = ext_cross_2 - sca_cross_2

    Cext = ext_cross_1+ext_cross_2
    Cabs = abs_cross_1+abs_cross_2
    Csca = sca_cross_1+sca_cross_2

    return Cext, Cabs, Csca
    # return abs_cross_1, abs_cross_2


w = np.arange(.5,3,.005)/hbar_eVs
dda_ext = np.zeros(len(w))
dda_abs = np.zeros(len(w))
dda_sca = np.zeros(len(w))

# abs1 = np.zeros(len(w))
# abs2 = np.zeros(len(w))


for i in range(0,len(w)):
    dda_ext[i], dda_abs[i], dda_sca[i] = dda_abs_cross_mie_polariz(w=w[i])
    # abs1[i], abs2[i] = dda_abs_cross_mie_polariz(w=w[i])

plt.plot(w*hbar_eVs, dda_ext,'k--',label='dda ext')
plt.plot(w*hbar_eVs, dda_abs,'r--',label='dda abs')
plt.plot(w*hbar_eVs, dda_sca,'b--',label='dda sca')

# plt.plot(w*hbar_eVs, abs1, label='dda abs')
# plt.plot(w*hbar_eVs, abs2, label='dda abs')
# plt.plot(w*hbar_eVs, abs1+abs2, 'k',label='dda abs')


plt.xlabel('Energy [eV]')
plt.ticklabel_format(axis="y", style="sci", scilimits=(0,0))
plt.ylabel('Abs. Cross-section [$\mu$m$^2$]')
# plt.xlim([2.4, 3])
plt.tight_layout()
plt.legend(frameon=False,loc='upper right')
plt.show()
