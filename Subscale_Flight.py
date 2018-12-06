from numpy import *
from matplotlib.pyplot import *
from scipy.interpolate import interp1d, interp2d
from time import time
import numpy as np

'''
Need to:
 - add gyro data (finish for simulating purposes)
 - write in deployment algorithm (use Eddie's code)
 - read data from pipe
 - write (what) data where ?
 - how to call python with args
 - check temp density function
 - simulate to predict a after launch and Fd of rocket at MECO

'''

class Rocket :
    def __init__ (self, thrust_profile, rocket_mass, motor_mass, propellant_mass, burn_time, max_deploy) :
        self.rocket_time, self.thrust_curve = np.loadtxt(thrust_profile, skiprows=1, unpack=True)
        self.thrust_function = interp1d(self.rocket_time, self.thrust_curve)
        self.wet_mass = motor_mass + rocket_mass + propellant_mass  # masses are in kg
        self.dry_mass = motor_mass + rocket_mass 
        self.propellant_mass = propellant_mass  
        self.max_deploy = max_deploy    # % of maximum deployment

# note: t_arb(itrary) needs to be near t_apogee for retraction ensurance
class Times :
    def __init__ (self, t_burn, t_start, t_res, t_deploy, t_arb) :
        self.burn = t_burn;     # motor burn time
        self.start = t_burn + t_start  # time to start deployment
        self.end = t_arb        # time to end activity after apogee for insurance
        self.step = t_res       # time step
        self.deploy = t_deploy  # time from 0 to 100% deployment 
        self.launch = 0.0       # stays at 0
        self.launch_date = 0.0  # will be actual time() of launch to use as reference 
        self.MECO = t_arb       # time after launch of MECO 
        self.apogee = t_arb     # time after launch of apogee
        self.arr = np.arange(self.launch, self.end, self.step)  # array of all time steps


# holds N-dim arrays of data initialized to None with ICs
class Data :
    def __init__ (self, N) :
        self.h = [None] * N      # height
        self.h[0] = 0.0
        self.v = [None] * N      # velocity
        self.v[0] = 0.0
        self.a = [None] * N      # acceleration
        self.a[0] = 0.0
        self.m = [None] * N      # mass
        self.drag = [None] * N   # 
        self.deployment = [None] * N # ?



def num_solver(thrust_profile, rocket_mass, motor_mass, propellant_mass, time_res, temp, burn_time, max_deploy, t_start, t_deploy, plots, drag_f) :

    # popen C program
    theta = np.pi / 2   # hardcode rocket to fly straight for simulation
    
    # define constants
    R = 8.31447         # Universal gas constant [J/mol*K]
    M = 0.0289644       # Molar mass of air [kg/mol]
    T = 288             # temperature of the air at launch altitude in [K]    # we think this is standard temp not temp(launch h)
    g = 9.81            # [m/s^2]
    P0 = 101325         # [Pa] Standard pressure at sea level
    L0 = 6.5         # [K/m] Standard temperature lapse rate
    temps = [0., 20., 40., 60.]  # these could be highly variable given flight cond'ns
    densities = [1.293, 1.205, 1.127, 1.067]    # at what alititude ??
    dens_temp_fxn = interp1d(temps, densities, kind = 'quadratic')  # gives density(temp)
    rho = dens_temp_fxn(temp)        # [kg/m^3]


    # initialize drag force function and rocket and flight objects
    drag_function = Get_Drag_Function()
    Aeoline = Rocket(thrust_profile, rocket_mass, motor_mass, propellant_mass, burn_time,  max_deploy)
    t_arb = 20      # an arbitrary number around t.apogee for initial high vals and end of ADAS deployment
    t = Times(burn_time, t_start, time_res, t_deploy, t_arb)   # CAREFUL, don't use t elsewhere
    data = Data(len(t.arr))
    data.m[0] = Aeoline.wet_mass
   
    # 1D trajectory plot via Forward Euler Integration

    # Use Riemann sum to get the mass flow rate from the thrust curve 
    start = time()  # TEST
    total_impulse = 0
    N = 1000        # arbitrary 10000 time steps
    time_steps = np.linspace(0, burn_time, N)  # TEST


    for ti in time_steps :
        total_impulse += Aeoline.thrust_function(ti) * burn_time/N
    print(' total impulse: ' + str(total_impulse)) # TEST

    
        
    # for time ti, height hi, velocity vi, angle th, mass mi, pressure pi
    def mass_flow_rate (ti):
        if ti <= t.burn:
            return -Aeoline.thrust_function(ti) * Aeoline.propellant_mass / total_impulse
        else:
            return 0

    # pressure from barometric formula with non-zero lapse rate (L0)
    def air_pressure (hi):   # pressure not 3.14
        # return P0 * (T / (T + L0 * hi)) ** (g * M / R * L0)   # non-zero lapse rate
        return P0 * np.exp(-g * M * hi / (R * T))    # 0 lapse rate
    
    # Gives drag force and deployment percentage
    # this needs testing and revamping
    gauss_steepness= 0.0005  #this measures the proportion that the gaussian starts off, so the bigger it is the bigger the jump but the faster ADAS deploys
    sigma_squared = ((-1)*(t_deploy)**2) / (2*log(gauss_steepness))
    def drag_curve (vi, ti, i):

        if ti <= t.start :
            deployment = 0
        elif Apogee == False:   # modify gaussian business?
            deployment = 0      # insert some deployment procedure here
        else :
            deployment = 0

        drag = drag_function(vi, deployment)
        data.drag[i] = drag
        data.deployment[i] = deployment
        return drag
        
    # account for gyroscope data ??
    def height_step (hi, vi):
        return hi + vi * t.step 
    
    def velocity_step (vi, ai):
        return vi + ai * t.step
    
    # a_y. drag_f is a fudge factor = 1.19
    def acc_step (vi, mi, ti, theta, i):   # CHECK THIS
        return -g + (Aeoline.thrust_function(ti) - drag_f * drag_curve(vi, ti, i)) * sin(theta) / mi
    
    def mass_step (mi, ti): 
        return mi + mass_flow_rate(ti) * t.step
    

    ################################################################
    ########################## Simulation ##########################
    ################################################################


    # Waiting on launch pad, measuring acc to detect launch
    a = 10
    a_thresh = 9
    while True :
        # read accelerometer data and update
        

        if a >= a_thresh :
            t.launch_date = time()
            break



    # define buffers for determining launch, MECO, and apogee
    buffer_acc = .2      # ??? are these reasonable, are they needed?
    buffer_vel = .1

    # False until detected or timed
    MECO = False
    Apogee = False
    c = 0   # defining indices of coasting and apogee (descent) outside of loop
    d = 0

    for i in range (1, len(t.arr)) :
    
        ti = t.arr[i]
        data.a[i] = acc_step(data.v[i-1], data.m[i-1], t.arr[i-1], theta, i)
        data.v[i] = velocity_step(data.v[i-1], data.a[i])
        data.h[i] = height_step(data.h[i-1], data.v[i])
        data.m[i] = mass_step(data.m[i-1], ti)    

        print(data.h[i], data.v[i], data.a[i])   # TESTING
    
        # detect MECO as point when a is only gravity and drag or as the burn time
        # thinking: acceleration should range from a_thresh -> g
        if not MECO :
            if (data.a[i] <= - (g + buffer_acc) or t.arr[i] > t.burn) :
                print(data.a[i])
                print('---------------------------------------------')
                t_MECO = t.arr[i]
                MECO = True     # Boolean for MECO detected 
                c = i - 1       # index of MECO
                print('coasting: ' + str(t.MECO))
                continue
    
        if (not Apogee) and MECO :
            # detect apogee with velocity (when negative) CHANGE (use pressure instead?)
            if (data.v[i-1] < buffer_vel or t.arr[i] > t.end) :
                t.apogee = t.arr[i]
                Apogee = True   # Boolean for Apogee detected
                d = i - 1 # index of apogee
                print('---------------------------------------------')
                print('apogee: ' + str(t.apogee))
                break   # set to continue for actual to record data during descent


# note for actual launch dynamics will change for the descent, want to still grab data




    if plots :
    
        figure(figsize=(10, 15))
        subplot(3,1,1)
        plot(t.arr[0:-1], data.drag[0:-1], '--', color = 'tomato', label = 'Trajectory')
        grid()
        xlim(0, t.arr[-1]+0.1)
        xlabel('Time [sec]')
        ylabel('Drag [N]')
   
        figure(figsize=(10, 15))
        subplot(3,1,1)
        plot(t.arr,array(data.h), '--', color = 'black', label = 'Trajectory')
        grid()
        title('Trajectory')
        xlabel('Time [s]')
        ylabel('Height [m]')

        plot(t.arr[c],data.h[c], 'o', color = 'black', label = 'Main Engine Cutoff')
        print 'MECO at', round(t.arr[c], 2), 'sec, at' , round(data.h[c], 2), 'm'

        plot(t.arr[d],data.h[d], 'o', color = 'tomato', label = 'Apogee')
        print 'Apogee at', round(t.arr[d], 2), 'sec, at' , round(data.h[d], 2), 'm'
        legend(loc = 'best')
        xlim(0, t.arr[-1]+0.1)
        ylim(-10, max(array(data.h))+50)

        subplot(3,1,2)
        plot(t.arr, array(data.v), '--', color = 'black', label = 'Velocity')
        grid()
        title('Velocity')
        xlabel('Time [s]')
        ylabel('Velocity [m/s]')

        #plot(t.arr[c],v_arr[c], 'o', color = 'black', label = 'Main Engine Cutoff')
        print 'MECO at', round(data.v[c], 2), 'm/s'

        plot(t.arr[d], data.v[d], 'o', color = 'tomato', label = 'Apogee')
        xlim(0, t.arr[-1]+0.1)
        ylim(min(data.v[0:i-1])-5, data.v[c] + 40)
        legend(loc = 'best')
        
        
        
        subplot(3,1,3)
        plot(t.arr[0:-1], data.a[0:-1], '-', color = 'black', label = 'Acceleration')
        #plot(t.arr[c], accel_array[c], 'o', color = 'black', label = 'Main Engine Cutoff')
        #plot(t.arr[d], accel_array[d], 'o', color = 'tomato', label = 'Apogee')
        xlabel('Time [s]')
        ylabel('Acceleration [m/sec^2]')
        title('Acceleration')
        grid()
        legend(loc = 'best')
        xlim(0, t.arr[-1]+0.1)
        
        figure(figsize=(10, 15))
        subplot(3,1,1)
        plot(t.arr[0:-1], data.deployment[0:-1], '-', color = 'black', label = 'ADAS Deployment')
        xlabel('Time [s]')
        ylabel('ADAS Dployment [deg]')
        title('ADAS Deployment')
        grid()
        legend(loc = 'best')
        ylim(0, max(data.deployment)+10)
        xlim(0, t.arr[-1]+0.1)

    return
    # return t_arr, v_arr, a_arr, j_arr, h_arr, m_arr, ADAS_deployment_arr, round(h_arr[-1], 2), round(v_arr[c], 2)


# interpolate drag force as fxns of rocket velocity and ADAS deployment
def Get_Drag_Function () :

    # do these still apply to the Aeolis design ?
    # simlation data:
    drag_array = [
    [0, 0.59182,2.2296,4.83375,8.55161,13.4116,20.0177,28.9221,38.1124,49.3355,62.0703,76.0614,92.0093,100.165],
    [0, 0.591264,2.2295,4.83807,8.55265,13.4071,20.0157,28.9142,38.2055,49.2593,62.0156,76.2053,92.08,100.07],
    [0, 0.592957,2.23896,4.85798,8.58222,13.4421,20.1047,28.965,38.327,49.34,62.133,76.276,92.111,100.161],
    [0, 0.6,2.268,4.925,8.696,13.609,20.378,29.306,38.839,49.893,62.725,77.065,92.937,101.081],
    [0, 0.611581,2.31152,5.02217,8.86343,13.8963,20.7639,29.8256,39.5542,50.7838,63.7972,78.3321,94.4829,102.622],
    [0, 0.624584,2.36323,5.14082,9.07321,14.2113,21.2211,30.4146,40.2816,51.7134,65.021,79.7737,96.0817,104.417],
    [0, 0.646593,2.45084,5.34285,9.43213,14.7778,22.0341,31.5141,41.7977,53.6209,67.1877,82.4599,99.4136,108.013],
    [0, 0.661885,2.51603,5.49391,9.7072,15.2164,22.668,32.3353,42.7805,54.8745,68.7875,84.2702,101.464,110.237],
    [0, 0.676409,2.57771,5.61966,9.95661,15.6125,23.1988,33.0944,43.7218,56.0576,70.2006,86.0549,103.6,112.28],
    [0, 0.686241,2.61922,5.74393,10.1423,15.8945,23.5704,33.5766,44.4382,56.8404,71.3742,87.3685,105.032,114.097],
    [0, 0.706858,2.7187,5.96159,10.5506,16.5219,24.4577,34.7788,46.0257,58.8808,73.8345,90.2789,108.543,117.836],
    [0, 0.755909,2.91253,6.39603,11.3087,17.7266,26.2551,37.2794,49.436,63.0928,78.9964,96.7176,116.246,126.51],
    [0, 0.796638,3.09445,6.83227,12.1446,19.0946,28.2083,39.7859,52.7009,67.1758,84.0781,102.727,123.357,134.042]]#DUNCAN GOT HIS SHIT TOGETHER :D
    
    # are these velocities sufficient ?
    ADAS_vel_array = [0, 20, 40, 60, 80, 100, 120, 140, 160, 180, 200, 220, 240, 250]
    ADAS_deploy_array = [0, 5.5555, 11.1111, 16.6667, 22.2222, 27.7778, 33.3333, 38.8888, 44.4444, 50, 55.5555, 77.7778, 100]

    # why cubic ?
    return interp2d(ADAS_vel_array, ADAS_deploy_array, drag_array, kind='cubic')
