import numpy as np
from gekko import GEKKO
from scipy.interpolate import interp1d, interp2d
import matplotlib.pyplot as plt
import pandas


# apm_get(server,app,'infeasibilities.txt')

# Currently simulating for subscale, starting at MECO

# # Fifth order coefficients
# p00 =     0.06663  
# p10 =      0.4139  
# p01 =     -0.1585  
# p20 =      0.1342  
# p11 =    -0.09726  
# p02 =     0.01327  
# p30 =     -0.1382  
# p21 =     -0.0269  
# p12 =    0.003564  
# p03 =  -0.0001886  
# p31 =     0.02039  
# p22 =    0.001382  
# p13 =  -2.698e-05  
# p04 =   1.314e-06  
# p32 =  -0.0009374  
# p23 =    1.72e-06  
# p14 =   5.505e-08  
# p05 =  -2.903e-09 

# Linear model Poly35:
#      f(x,y) = p00 + p10*u + p01*v + p20*u^2 + p11*u*v + p02*v^2 + p30*u^3 + p21*u^2*v 
#                     + p12*u*v^2 + p03*v^3 + p31*u^3*v + p22*u^2*v^2 + p13*u*v^3 
#                     + p04*v^4 + p32*u^3*v^2 + p23*u^2*v^3 + p14*u*v^4 +
#                      p05*v^5

# Third order coefficients       
p00 =      0.9656
p10 =      -4.797
p01 =    -0.02562
p20 =       14.19
p11 =     0.01236
p02 =    0.002656
p30 =      -11.22
p21 =     0.06384
p12 =   0.0003626
p03 =   7.823e-06











# # Initialize thrust and mass functions
# rocket_time, thrust_curve = np.loadtxt('./ThrustData/J420_thrust.txt', skiprows=0, unpack=True)
# thrust_function = interp1d(rocket_time, thrust_curve)
# def mass_flow_rate (ti):
#     if ti <= t.burn:
#         return -Aeoline.thrust_function(ti) * Aeoline.propellant_mass / total_impulse
#     else:
#         return 0

# initialize coefficient of drag function and rocket and flight objects
# drag_function = Get_Drag_Function()






# --------------------------------------
# ------------ OPTIMIZER ---------------
# --------------------------------------


#Initialize Model
gk = GEKKO()	# normalize time

# define parameters
maxalt = gk.Param(value=1828.8)			# max possible height [m]
maxspeed = gk.Param(value=343) 			# max possible speed [m/s]
maxdep = gk.Param(value=0.9) 			# max possible deployment [%]

m = gk.Param(value=5.02217472)			# weight in kg after MECO [kg]
g = gk.Param(value=9.8)					# Earth's gravity in Troposphere [m/s^2]
apogee = gk.Param(value=540)			# target apogee [m]


# IC and t0 of simulations are OR-provided data for MECO

# initialize normalized time
ts = 1.58		# time of MECO, time for start of simulation
nt = 70
gk.time = np.linspace(0, 1, nt) 	

# initialize parameters
x_MECO = gk.Param(value=100)			# altitude at MECO [m]
v_MECO = gk.Param(value=105)			# velocity at MECO [m/s]
Fd_MECO = gk.Param(value=22)			# drag force at MECO [N]
										# acceleration at MECO = -15 m/s^2

# initialize variables
x = gk.SV(lb=0, ub=maxalt, value=x_MECO)		# height [m]
v = gk.SV(lb=0, ub=maxspeed, value=v_MECO)		# velocity [m/s]
Fd = gk.Var(lb=0, ub=200, value=Fd_MECO)		# drag force (>=0) [kg*m/s^2]

u = gk.CV(lb=0.2, ub=maxdep, value=0.3)  # control = deployment [%] (could be MV)
u.STATUS = 1							# needs to be calculated


# optimizing final time
p = np.zeros(nt) 						
p[-1] = 1.0								# final time = 1
final = gk.Param(value=p)

tf = gk.MV(value=9.0,lb=5,ub=25.0)
tf.STATUS = 1
	
# I = gk.Var(lb=0, value=0)				# integral to be minimized



# Physics
gk.Equation( Fd == p00 + p10*u + p01*v + p20*u**2 + p11*u*v + p02*v**2 ) 
# + p31*u**3*v + p22*u**2*v**2 + p13*u*v**3 + p04*v**4 + p32*u**3*v**2 + p23*u**2*v**3 + p14*u*v**4 + p05*v**5 )

gk.Equation( x.dt() == tf * v )
gk.Equation( v.dt() == tf * (- Fd/m - g) )
gk.Equation( v*final == 0 )

# minimizing integral of squared deployment
# gk.Equation( I.dt() == tf * u ** 2 )

# m.Equation( rho == rho * e)





#Objective
# scaling = gk.Param(value=100)
gk.Obj( (abs(x-apogee)*final) )



# want to minimize integral over possible deployments
# I*final * scaling + 


#Set global options
gk.options.IMODE = 6 		# dynamic optimization with control
gk.options.MAX_ITER = 3000	# default is 100
gk.options.MAX_MEMORY = 4	# default is 4 (OOM value)

#Solve simulation
gk.solve(disp=False)			# default is solving remotely




#Results
print('')
print('Apogee is {0}m at {1}s'.format(max(x.value), tf.value[0]))



tm = np.linspace(ts, tf.value[0], nt)
xdat = np.asarray(x.value)
vdat = np.asarray(v.value)
udat = np.asarray(u.value)
tdat = np.asarray(tm)

# Save data to csv
fname = './OptControl/Opt.csv'
df = pandas.DataFrame({"pos" : xdat, "vel" : vdat, "dep" : udat, "time" : tdat})
df.to_csv(fname, index=False)
print('Wrote to data to ' + fname)







