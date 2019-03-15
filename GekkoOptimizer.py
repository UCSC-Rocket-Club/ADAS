import numpy as np
from gekko import GEKKO
from scipy.interpolate import interp1d, interp2d
import matplotlib.pyplot as plt

# Currently simulating for subscale, starting at MECO


# # Interpolates drag coefficients as fxn of rocket velocity [m/s] and ADAS deployment percentage
# # return F_D(v,%)
# def Get_Drag_Function () :

#     # Drag coefficient data from flow simulations with states P = 98000 [Pa], T = 283 [K], density = rho = 1.15 [kg/m^2]
#     # NOTE: data excludes that for 10 degrees
#     sim_drag_coeffs = [       # DUNCAN ROCKS   :D
#     [0, 0.4897130673,    0.4605084415,    0.4566277895,    0.457260162,     0.4577140061,    0.4570957994,    0.4566626055,    0.5642732454,    0.4545761375,    0.5717283138],
#     [0, 0.5697580479,    0.4602782598,    0.456513712,     0.4567162609,    0.4569759963,    0.456424171,     0.455415689,     0.5583588651,    0.5620175824,    0.5649677736],
#     [0, 0.5668725374,    0.4682819154,    0.4469762488,    0.4645024797,    0.4644837072,    0.4639810209,    0.4625354359,    0.556496065,     0.559965656,     0.562991906],
#     [0, 0.5638586086,    0.4830633638,    0.4804639344,    0.481315034,     0.4815977549,    0.4822440287,    0.4804765347,    0.5557061413,    0.5589313185,    0.5619646087],
#     [0, 0.5641773622,    0.4839314615,    0.4825487796,    0.4821114534,    0.4831116457,    0.4827254992,    0.4811014429,    0.5541560884,    0.5575369803,    0.5604568335],
#     [0, 0.5690075644,    0.4846769576,    0.4816589436,    0.4822390455,    0.4827377599,    0.4830244712,    0.4806339902,    0.5587568886,    0.5619985844,    0.5647384353],
#     [0, 0.5702164927,    0.4923129991,    0.4892673582,    0.4893980557,    0.4892061981,    0.4885889214,    0.4869239868,    0.5621926732,    0.5655911728,    0.5683652118],
#     [0, 0.57425205,      0.5092990664,    0.5063569557,    0.5065504403,    0.5063751519,    0.5060755784,    0.5064538141,    0.5662279936,    0.5694119308,    0.5721914277],
#     [0, 0.5792708916,    0.5054756846,    0.50307373,      0.5033542067,    0.5032704218,    0.5022323,       0.5047265086,    0.5713875199,    0.5744315084,    0.5768540181],
#     [0, 0.5788864078,    0.5192401696,    0.5165947143,    0.5170544599,    0.5171723766,    0.5165778943,    0.5151439218,    0.5719901683,    0.5750984082,    0.5780046877]] 
#     sim_drag_coeffs = np.array(sim_drag_coeffs, dtype='float64')

#     sim_velocities = np.array([0, 20, 40,  60,  80,  100, 120, 140, 160, 180, 200])  # [m/s] simulation velocities
#     # ADAS_deploy_array = array([0, 14.4, 21.6, 28.8, 36, 43.2, 50.4, 57.6, 64.8, 72])     # degrees of deployment for sim data
#     sim_deploy_percents = np.delete(np.linspace(0, 1, 11), 1)       # simlation deployment percentages
    

#     # Cross-sectional area [m^2] of subscale with fin deployment corresponding to angles in ADAS_deploy_array 
#     sim_deploy_areas = [0.007127518874, 0.007256550874, 0.007411389274, 0.007566227674, 0.007695259674, 0.007811388474, 0.007914614074, 0.008017839674, 0.008095258874, 0.008185581274]
#     # Convert areas from subscale to full scale (only thing that should change in this calc)
#     # sim_deploy_areas = [x * (5.5**2)/(3.15**2) for x in sim_deploy_areas]    # convert to full scale

#     # Drag force = .5 * rho * A * v^2 * cd [N = kg*m/s^2]
#     rho = 1.15	
#     drag_force = 0.5 * rho * np.transpose( np.transpose(sim_drag_coeffs * sim_velocities**2) * sim_deploy_areas )

#     print(type(sim_drag_coeffs[0][0]))
#     return interp2d(sim_velocities, sim_deploy_percents, drag_force, kind='cubic')



# sim_drag_coeffs = [       # DUNCAN ROCKS   :D
# [0, 0.4897130673,    0.4605084415,    0.4566277895,    0.457260162,     0.4577140061,    0.4570957994,    0.4566626055,    0.5642732454,    0.4545761375,    0.5717283138],
# [0, 0.5697580479,    0.4602782598,    0.456513712,     0.4567162609,    0.4569759963,    0.456424171,     0.455415689,     0.5583588651,    0.5620175824,    0.5649677736],
# [0, 0.5668725374,    0.4682819154,    0.4469762488,    0.4645024797,    0.4644837072,    0.4639810209,    0.4625354359,    0.556496065,     0.559965656,     0.562991906],
# [0, 0.5638586086,    0.4830633638,    0.4804639344,    0.481315034,     0.4815977549,    0.4822440287,    0.4804765347,    0.5557061413,    0.5589313185,    0.5619646087],
# [0, 0.5641773622,    0.4839314615,    0.4825487796,    0.4821114534,    0.4831116457,    0.4827254992,    0.4811014429,    0.5541560884,    0.5575369803,    0.5604568335],
# [0, 0.5690075644,    0.4846769576,    0.4816589436,    0.4822390455,    0.4827377599,    0.4830244712,    0.4806339902,    0.5587568886,    0.5619985844,    0.5647384353],
# [0, 0.5702164927,    0.4923129991,    0.4892673582,    0.4893980557,    0.4892061981,    0.4885889214,    0.4869239868,    0.5621926732,    0.5655911728,    0.5683652118],
# [0, 0.57425205,      0.5092990664,    0.5063569557,    0.5065504403,    0.5063751519,    0.5060755784,    0.5064538141,    0.5662279936,    0.5694119308,    0.5721914277],
# [0, 0.5792708916,    0.5054756846,    0.50307373,      0.5033542067,    0.5032704218,    0.5022323,       0.5047265086,    0.5713875199,    0.5744315084,    0.5768540181],
# [0, 0.5788864078,    0.5192401696,    0.5165947143,    0.5170544599,    0.5171723766,    0.5165778943,    0.5151439218,    0.5719901683,    0.5750984082,    0.5780046877]] 
# sim_drag_coeffs = np.array(sim_drag_coeffs, dtype='float64')

# sim_velocities = np.array([0, 20, 40,  60,  80,  100, 120, 140, 160, 180, 200])  # [m/s] simulation velocities
# # ADAS_deploy_array = array([0, 14.4, 21.6, 28.8, 36, 43.2, 50.4, 57.6, 64.8, 72])     # degrees of deployment for sim data
# sim_deploy_percents = np.delete(np.linspace(0, 1, 11), 1)       # simlation deployment percentages


# # Cross-sectional area [m^2] of subscale with fin deployment corresponding to angles in ADAS_deploy_array 
# sim_deploy_areas = [0.007127518874, 0.007256550874, 0.007411389274, 0.007566227674, 0.007695259674, 0.007811388474, 0.007914614074, 0.008017839674, 0.008095258874, 0.008185581274]
# # Convert areas from subscale to full scale (only thing that should change in this calc)
# # sim_deploy_areas = [x * 5.5/3.15 for x in sim_deploy_areas]    # convert to full scale

# # Drag force = .5 * rho * A * v^2 * cd [N = kg*m/s^2]
# rho = 1.15	
# drag_force = 0.5 * rho * np.transpose( np.transpose(sim_drag_coeffs * sim_velocities**2) * sim_deploy_areas )

# # print(type(sim_drag_coeffs[0][0]))
# drag_function = interp2d(sim_velocities, sim_deploy_percents, drag_force, kind='cubic')


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
gk = GEKKO()

# t=1.6 is MECO, not factored in anywhere
# initialize normalized time
nt = 601 								# ~25(Hz) * tf
gk.time = np.linspace(0, 1, nt) 		# normalize time

#define parameter
maxalt = gk.Param(value=6000) 			# max possible height
maxspeed = gk.Param(value=343) 			# max possible speed
maxdep = gk.Param(value=0.9) 			# max possible deployment
m = gk.Param(value=8.85)				# weight in kg after MECO
g = gk.Param(value=9.8)					# Earth's gravity in Troposphere
mile = gk.Param(value=1609.34)			# 1 mile in meters
x_MECO = gk.Param(value=100)			# altitude at MECO
v_MECO = gk.Param(value=107)			# velocity at MECO
Fd_MECO = gk.Param(value=5)				# drag force at MECO

#initialize variables
x = gk.SV(lb=0, ub=maxalt, value=x_MECO)			# height [m]
v = gk.SV(lb=0, ub=maxspeed, value=v_MECO)		# velocity [m/s]
Fd = gk.Var(value=Fd_MECO)						# drag force [kg*m/s^2]

u = gk.CV(lb=0, ub=maxdep, value=0)  	# control = deployment [%] (could be MV)
u.STATUS = 1							# needs to be calculated

# optimize final time
p = np.zeros(nt) 						
p[-1] = 1.0								# final time = 1
final = gk.Param(value=p)
tf = gk.FV(value=1.0,lb=0.1,ub=100.0)
tf.STATUS = 1
	
I = gk.Var(lb=0, value=0)				# integral to be minimized



# Physics
gk.Equation( Fd == p00 + p10*u + p01*v + p20*u**2 + p11*u*v + p02*v**2 + p30*u**3 + p21*u**2*v + p12*u*v**2 + p03*v**3 )
                    # + p31*u**3*v + p22*u**2*v**2 + p13*u*v**3 + p04*v**4 + p32*u**3*v**2 + p23*u**2*v**3 + p14*u*v**4 + p05*v**5 )
gk.Equation( x.dt() == tf * v )
gk.Equation( v.dt() == tf * (- Fd / m - g) )
# minimizing integral of squared deployment
gk.Equation( I.dt() == tf * u ** 2 )
# m.Equation( Fd == thrust_function(v,u) )
# m.Equation( rho == rho * e)

# apogee conditions
gk.Equation( x*final <= tf * x_MECO )	
gk.Equation( v*final <= tf * v_MECO )

#Objective
gk.Obj(I)		# want to minimize integral over possible deployments
gk.Obj(tf)		# minimize time to apogee - actually not needed

print('\n pre-solve \n')

#Set global options
gk.options.IMODE = 6 # dynamic optimization with control
gk.MAX_ITER = 10000
#Solve simulation
gk.solve(disp=True)
# m.solve(remote=False) # windows only perhaps




#Results
print('')
print('Results')
print('tf is %f' % tf.value[0])
# print('tf is %f' % tf)
print('deployment is %f', u)


tm = np.linspace(1.6, tf.value[0], nt) 	# 1.6 is t_MECO


plt.figure(1)
plt.title('Altitude')
plt.xlabel('time')
plt.plot(tm, x.value, 'k-')
plt.plot(tm, v.value, 'b-')


plt.figure(2)
plt.title('Deployment')
plt.plot(tm, u.value, 'k-')








