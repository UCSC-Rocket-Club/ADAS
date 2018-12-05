from numpy import *
from matplotlib.pyplot import *
from scipy.interpolate import interp1d, interp2d
# import Get_Drag_Function as GDF
# for testing
from scipy.integrate import quad
from time import time
import numpy as np


class Rocket :
    def __init__ (self, thrust_profile, rocket_mass, motor_mass, propellant_mass, burn_time, max_deploy, t_start, t_deploy, t_res) :
        self.rocket_time, self.thrust_curve = np.loadtxt(thrust_profile, skiprows=1, unpack=True)
        self.thrust_function = interp1d(self.rocket_time, self.thrust_curve)
        self.wet_mass = motor_mass + rocket_mass + propellant_mass  #kg
        self.dry_mass = motor_mass + rocket_mass #kg
        self.propellant_mass = propellant_mass
        self.max_deploy = max_deploy

# note: t_arb needs to be near t_apogee for retraction ensurance
class Times :
    def __init__ (self, t_burn, t_start, t_res, t_deploy, t_arb) :
        self.burn = t_burn;
        self.start = t_burn + t_start  # start of deployment after 
        self.end = t_arb        # end activity after takeoff for insurance
        self.step = t_res
        self.deploy = t_deploy
        self.launch = 0.0
        self.launch_date = 0.0  # actual time() of launch to use as reference 
        self.MECO = t_arb
        self.apogee = t_arb
        self.arr = np.arange(self.launch, self.end, self.step)

# holds N-dim arrays of data initialized to None with ICs
class Data :
    def __init__ (self, N) :
        self.h = [None] * N      # height
        self.h[0] = 0.0
        self.v = [None] * N      # velocity
        self.v[0] = 0.0
        self.a = [None] * N      # acceleration
        self.a[0] = 0.0
        self.j = [None] * N      # jerk
        self.j[0] = 0.0
        self.m = [None] * N      # mass
        self.drag = [None] * N   # ?
        self.deployment = [None] * N # ?



def num_solver(thrust_profile, rocket_mass, motor_mass, propellant_mass, time_res, temp, burn_time, max_deploy, t_start, t_deploy, plots, drag_f) :

    
    # define constants
    R = 8.31447         # Universal gas constant [J/mol*K]
    M = 0.0289644       # Molar mass of air [kg/mol]
    T = temp + 273.15   # temperature of the air at launch altitude in [K]
    g = 9.81            # [m/s^2]
    temps = [0., 20., 40., 60.]  # these could be highly variable given flight cond'ns
    densities = [1.293, 1.205, 1.127, 1.067]    # at what alititude ??
    dens_temp_fxn = interp1d(temps, densities, kind = 'quadratic')  # gives density(temp)
    rho = dens_temp_fxn(temp)        # [kg/m^3]


    # initialize drag force function and rocket and flight objects
    drag_function = Get_Drag_Function()
    Aeoline = Rocket(thrust_profile, rocket_mass, motor_mass, propellant_mass, burn_time,  max_deploy, t_start, t_deploy, time_res)
    t_arb = 20      # an arbitrary number around t.apogee for initial high vals and end of ADAS function
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

    def air_drag (hi, vi, th): # th is the angle of deployment
        return drag_function(vi, th) * air_pressure(hi, rho) / 1.225    # CHECK THIS
    
    # this needs testing and revamping
    gauss_steepness= 0.00005  #this measures the proportion that the gaussian starts off, so the bigger it is the bigger the jump but the faster ADAS deploys
    sigma_squared = ((-1)*(t_deploy)**2)/(2*log(gauss_steepness))
    def drag_curve (hi, vi, ti, i):
        
        if ti <= t.start :
            deployment = 0
        else:   # modify gaussian business?
            if t.start < ti < (t.deploy + t.start) :
                deployment = (max_deploy)*e**(-1*(ti-t.deploy-t.start)**2/(2*sigma_squared))
            else:
                deployment = max_deploy
        drag = air_drag(hi, vi, deployment)
        
        data.drag[i] = drag
        data.deployment[i] = deployment
        return drag
        
    # account for gyroscope data ??
    def height_step (hi, vi):
        return  hi + vi * t.step 
    
    def velocity_step (vi, ai):
        return vi + ai * t.step
    
    def acc_step (hi, vi, mi, ti, i):   # CHECK THIS
        return -g - drag_f * drag_curve(hi, vi, ti, i)/mi + Aeoline.thrust_function(ti)/mi
    
    # why is this needed and what is the if for?
    def jerk_step (ai, aii):
        if i > 1:
            jerk = (ai - aii) / t.step
        else:
            jerk = 0
        return jerk
    
    def mass_step (mi, ti): 
        return mi + mass_flow_rate(ti)
    
    def air_pressure (hi, pi):   # pressure not 3.14
        return pi * e ** (-1 * (g * M * hi) / (R * T))

    #arrays to push results to 
    drag_curve_arr = [0]
    ADAS_deployment_arr = [0]
    

    ################################################################
    ########################## Simulation ##########################
    ################################################################

    

    # need code for sitting on the pad waiting to detect launch
    # Waiting on launch pad
    # while True :
    #     if a >= a_thresh :
    #         t.launch_date = time()
    #         break

    # define buffers for determining launch, MECO, and apogee
    buffer_acc = .1      # ??? are these reasonable, are they needed
    buffer_vel = .1


    # Ascent
    i = 1
    while (t.arr[i] < t.burn) : 
    
        ti = t.arr[i]
        data.h[i] = height_step(data.h[i-1], data.v[i-1])
        data.v[i] = velocity_step(data.v[i-1], data.a[i-1])
        data.a[i] = acc_step(data.h[i-1], data.v[i-1], data.m[i-1], t.arr[i-1], i)
        data.j[i] = jerk_step(data.a[i], data.a[i-1])
        data.m[i] = mass_step(data.m[i-1], ti)
    
        # detect MECO
        # thinking: once this loop is entered acceleration should range from a_thresh -> g
        # if (ai <= (-g + buffer_acc)) :
        #     t_MECO = time_arr[i]
        #     break
    
        i += 1

    c = i - 1       # index of MECO
    if (t.MECO == t_arb) :  # if MECO was not detected in the loop
        t.MECO = t.arr[i-1]
    
    print('coasting: ' + str(t.MECO))

    # Coasting
    while (t.arr[i] < t.end) : 
    
        ti = t.arr[i]
        data.h[i] = height_step(data.h[i-1], data.v[i-1])
        data.v[i] = velocity_step(data.v[i-1], data.a[i-1])
        data.a[i] = acc_step(data.h[i-1], data.v[i-1], data.m[i-1], t.arr[i-1], i)
        data.j[i] = jerk_step(data.a[i], data.a[i-1])
        data.m[i] = mass_step(data.m[i-1], ti)
    
        # detect apogee with velocity (when negative) CHANGE
        if (data.v[i-1] < buffer_vel) :
            t.apogee = t.arr[i]
            break

        i += 1

    if (t.apogee == t_arb) :    # if apogee was not detected in the loop
        t.apogee = t.arr[i-1]
    print('apogee: ' + str(t.apogee))
    # write alg to close fins

    # Descent

    d = i - 1 # index of apogee
    #  while (h_arr[i]>0):
   

    t_arr = linspace(0,t.step*(len(data.h)+1),len(data.h))  #check

    if plots :
    
        figure(figsize=(10, 15))
        subplot(3,1,1)
        plot(t_arr[0:-1], data.drag[0:-1], '--', color = 'tomato', label = 'Trajectory')
        grid()
        xlim(0, t.arr[-1]+0.1)
        xlabel('Time [sec]')
        ylabel('Drag [N]')
   
        figure(figsize=(10, 15))
        subplot(3,1,1)
        plot(t_arr,array(data.h), '--', color = 'black', label = 'Trajectory')
        grid()
        title('Trajectory')
        xlabel('Time [s]')
        ylabel('Height [m]')

        plot(t_arr[c],data.h[c], 'o', color = 'black', label = 'Main Engine Cutoff')
        print 'MECO at', round(t_arr[c], 2), 'sec, at' , round(data.h[c], 2), 'm'

        plot(t_arr[d],data.h[d], 'o', color = 'tomato', label = 'Apogee')
        print 'Apogee at', round(t_arr[d], 2), 'sec, at' , round(data.h[d], 2), 'm'
        legend(loc = 'best')
        xlim(0, t.arr[-1]+0.1)
        ylim(-10, max(array(data.h))+50)

        subplot(3,1,2)
        plot(t_arr, array(data.v), '--', color = 'black', label = 'Velocity')
        grid()
        title('Velocity')
        xlabel('Time [s]')
        ylabel('Velocity [m/s]')

        #plot(t_arr[c],v_arr[c], 'o', color = 'black', label = 'Main Engine Cutoff')
        print 'MECO at', round(data.v[c], 2), 'm/s'

        plot(t_arr[d], data.v[d], 'o', color = 'tomato', label = 'Apogee')
        xlim(0, t.arr[-1]+0.1)
        ylim(min(data.v[0:i-1])-5, data.v[c] + 40)
        legend(loc = 'best')
        
        
        
        subplot(3,1,3)
        plot(t_arr[0:-1], data.a[0:-1], '-', color = 'black', label = 'Acceleration')
        #plot(t_arr[c], accel_array[c], 'o', color = 'black', label = 'Main Engine Cutoff')
        #plot(t_arr[d], accel_array[d], 'o', color = 'tomato', label = 'Apogee')
        xlabel('Time [s]')
        ylabel('Acceleration [m/sec^2]')
        title('Acceleration')
        grid()
        legend(loc = 'best')
        xlim(0, t.arr[-1]+0.1)
        
        figure(figsize=(10, 15))
        subplot(3,1,1)
        plot(t_arr[0:-1], data.deployment[0:-1], '-', color = 'black', label = 'ADAS Deployment')
        xlabel('Time [s]')
        ylabel('ADAS Dployment [deg]')
        title('ADAS Deployment')
        grid()
        legend(loc = 'best')
        ylim(0, max(data.deployment)+10)
        xlim(0, t.arr[-1]+0.1)

    return
    # return t_arr, v_arr, a_arr, j_arr, h_arr, m_arr, ADAS_deployment_arr, round(h_arr[-1], 2), round(v_arr[c], 2)



def Get_Drag_Function () :

    # do these still apply to the Aeolis design ?
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


#################################################################################################################################################################################################################################################################################################################################################################################################################################
#################################################################################################################################################################################################################################################################################################################################################################################################################################
#################################################################################################################################################################################################################################################################################################################################################################################################################################





## Lia's note: untouched

def PID(thrust_profile, rocket_mass, motor_mass, propellant_mass, time_res, temp, burn_time, max_deploy, t_start, t_deploy, plots, drag_f, k_height, k_vel, k_acc, k_jerk, PID_scale, ADAS_max_speed, update_interval, acc_noise, vel_noise, h_noise):
    
    nom_t, nom_v, nom_a, nom_j, nom_h, nom_m, nom_ADAS, nom_apogee, nom_v_MECO = num_solver(thrust_profile, rocket_mass, motor_mass, propellant_mass, time_res, temp, burn_time, max_deploy, t_start, t_deploy, 0, drag_f)
    #calculate the nominal flight path
    
    
    
    rocket_time = ascii.read(thrust_profile)['time']
    thrust_curve = ascii.read(thrust_profile)['thrust']

    thrust_function = interp1d(rocket_time, thrust_curve)
    
    #constants
    g = 9.81 #m/s^2
    temps = [0., 20., 40., 60.]
    densities = [1.293, 1.205, 1.127, 1.067]
    dens_temp_fxn = interp1d(temps, densities, kind = 'quadratic')
    rho = dens_temp_fxn(temp) # kg/m^3

    #initial conditions
    h0 = 0. #m  (height)
    v0 = 0. #m/s (velocity)

    #rocket characteristics

    Wet_mass = motor_mass + rocket_mass + propellant_mass  #kg
    Dry_mass = motor_mass + rocket_mass #kg
    
    
    # 1D trajectory plot via Forward Euler Integration

    time_step = time_res #rename
    
    #Get the mass flow rate from the thrust curve
    t_dummy = 0     #dummy time variable
    total_impulse = 0
    while t_dummy<burn_time+1:
        total_impulse = total_impulse+thrust_function(t_dummy)
        t_dummy = t_dummy+time_step
        
        
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
    
    ADAS_vel_array = [0, 20, 40, 60, 80, 100, 120, 140, 160, 180, 200, 220, 240, 250]
    ADAS_deploy_array = [0, 5.5555, 11.1111, 16.6667, 22.2222, 27.7778, 33.3333, 38.8888, 44.4444, 50, 55.5555, 77.7778, 100]
    
    drag_function = interp2d(ADAS_vel_array, ADAS_deploy_array, drag_array, kind='cubic')
    
    signal_h_arr = []
    signal_v_arr = []
    signal_a_arr = []
    signal_j_arr = []
    
    max_index = len(nom_t)-1
    
    
    motor_commands_arr = [0] #stores the list of commands sent to the motor
    wanted_deployments = [0] #stores every calculation done by PID
    last_seized_index = [0]  #stores the index of where the data has already been drawn from from wanted_deployments
    
    def mass_flow_rate(t):
        if t<=burn_time:
            return thrust_function(t)*(Wet_mass-Dry_mass)/total_impulse
        else:
            return 0
        
    def air_drag(hi, vi, f): #f is the angle
        return drag_function(vi, f) * air_pressure(hi, rho)/1.225
    
    def update_PID(hi, vi, ai, ji, t):
        prev_deployment = ADAS_deployment_arr[-1]
        if t<=t_start:
            deployment = 0
        else:
            index = int(t/time_step)
            if index<max_index:
                signal_h = hi-nom_h[index]
                signal_v = vi-nom_v[index]
                signal_a = ai-nom_a[index]
                signal_j = (ji-nom_j[index])
            else:
                signal_h = 0
                signal_v = 0
                signal_a = 0
                signal_j = 0
            signal_h_arr.append(signal_h)
            signal_v_arr.append(signal_v)
            signal_a_arr.append(signal_a)
            signal_j_arr.append(signal_j)
            
            total_signal = (signal_h*k_height+signal_v*k_vel+signal_a*k_acc+signal_j*k_jerk)*PID_scale
            
            deployment = total_signal
        '''
        #check that it isn't trying to deploy too fast
        if abs(deployment-prev_deployment) > ADAS_max_speed*time_step:
            sign = abs(deployment-prev_deployment)/(deployment-prev_deployment)
            deployment = prev_deployment + sign*ADAS_max_speed*time_step
        '''
        #check that the signal isn't above 100 or below 0
        if deployment > 100:
            deployment = 100
        if deployment < 0:
            deployment = 0
            
        wanted_deployments.append(deployment)
        
    
    def move_ADAS(t):
        if t < burn_time:
            ADAS_deployment_arr.append(0)
            return
        if (t/time_step)%(update_interval/time_step) == 0:    #if it is time to update the motor configuration
            av_depl = average(wanted_deployments[last_seized_index[-1]:-1])
            last_seized_index.append(int(t/time_step))              #update for the next iteration
            motor_commands_arr.append(av_depl)
            
        specific_wanted_deployment = motor_commands_arr[-1]
            
        current_ADAS_config = ADAS_deployment_arr[-1]
        if specific_wanted_deployment == current_ADAS_config:
            ADAS_deployment_arr.append(current_ADAS_config)
            return
        
        sign = abs(specific_wanted_deployment-current_ADAS_config)/(specific_wanted_deployment-current_ADAS_config) #whether to deploy more or less
        new_deployment = current_ADAS_config + sign*ADAS_max_speed*time_step
        ADAS_deployment_arr.append(new_deployment)
    
    def drag_curve(hi, vi, t):
        drag = air_drag(hi, vi, ADAS_deployment_arr[-1])
        drag_curve_arr.append(drag)
        
        return drag
        
    def height_step(hi, vi):
        return  hi + vi * time_step 
    
    def velocity_step(vi, ai):
        return vi + ai*time_step
    
    def acc_step(hi, vi, mi, ti):
        return -g - drag_f * drag_curve(hi, vi, ti)/mi + thrust_function(ti)/mi
    
    def jerk_step(index):
        if index > 1:
            jerk = (a_arr[index]-a_arr[index-1])/time_step
        else:
            jerk = 0
        return jerk
    
    def mass_step(mi, t): 
        return mi + (-mass_flow_rate(t))
    
    def air_pressure(h, p_i):
        R=8.31447       #Universal gas constant
        M=0.0289644     #Molar mass of air kg/mol
        T=temp+273.15   #temperature of the air at launch altitude in Kelvin
        return p_i*e**(-1*(g*M*h)/(R*T))

    #arrays to push results to

    h_arr = [h0]
    v_arr = [v0]
    a_arr = [0]
    j_arr = [0]
    
    h_arr_noised = [h0]   
    v_arr_noised = [v0]   
    a_arr_noised = [0]    
    j_arr_noised = [0]
    
    m_arr = [Wet_mass]
    time_array = [0]
    drag_curve_arr = [0]
    ADAS_deployment_arr = [0]

    #calculation
    i = 1
    
    
    #ascent
   
    while (time_array[i-1] < burn_time): 
    
        ti = (time_step)*(i)
        time_array.append(ti)
    
        hi = height_step(h_arr[i-1], v_arr[i-1])
        h_arr.append(hi)
        h_arr_noised.append(hi + random.normal(0, h_noise))
    
        vi = velocity_step(v_arr[i-1], a_arr[i-1])
        v_arr.append(vi)
        v_arr_noised.append(vi + random.normal(0, vel_noise))
        
        ai = acc_step(h_arr[i-1], v_arr[i-1], m_arr[i-1], time_array[i-1])
        a_arr.append(ai)
        a_arr_noised.append(ai + random.normal(0, acc_noise))
        
        ji = jerk_step(i)
        j_arr.append(ji)
        j_arr_noised.append(ji)
    
        mi = mass_step(m_arr[i-1], ti)
        m_arr.append(mi)
        
        #update ADAS calculation
        #update_PID(h_arr[i-1], v_arr[i-1], a_arr[i-1], time_array[i-1])
        update_PID(h_arr_noised[i-1], v_arr_noised[i-1], a_arr_noised[i-1], j_arr_noised[i-1], time_array[i-1])
        #move motor
        move_ADAS(ti)
    
        i = i+1
    
    # coast
    c = i-1 #mark transition to coast

    while (v_arr[i-1]>0): 
    
        ti = (time_step)*(i)
        time_array.append(ti)
    
        hi = height_step(h_arr[i-1], v_arr[i-1])
        h_arr.append(hi)
        h_arr_noised.append(hi + random.normal(0, h_noise))
    
        vi = velocity_step(v_arr[i-1], a_arr[i-1])
        v_arr.append(vi)
        v_arr_noised.append(vi + random.normal(0, vel_noise))
        
        ai = acc_step(h_arr[i-1], v_arr[i-1], m_arr[i-1], time_array[i-1])
        a_arr.append(ai)
        a_arr_noised.append(ai + random.normal(0, acc_noise))
        
        ji = jerk_step(i)
        j_arr.append(ji)
        j_arr_noised.append(ji)
    
        mi = Dry_mass
        m_arr.append(mi)
        
        #update ADAS calculation
        #update_PID(h_arr[i-1], v_arr[i-1], a_arr[i-1], time_array[i-1])
        update_PID(h_arr_noised[i-1], v_arr_noised[i-1], a_arr_noised[i-1], j_arr_noised[i-1], time_array[i-1])
        #move motor
        move_ADAS(ti)
    
        i = i+1
       
    #descent

    d = i-1 #mark transition to descent
    """
    while (h_arr[i]>0):
    
        ti = (time_step)*(i)
        time_array.append(ti)
        
        hi = height_step(h_arr[i], v_arr[i])
        h_arr.append(hi)
    
        vi = velocity_step(h_arr[i], v_arr[i], m_arr[i], time_array[i])
        v_arr.append(vi)
    
        mi = Dry_mass
        m_arr.append(mi)
    
        i = i+1
    """
    t_arr = linspace(0,time_step*(len(h_arr)+1),len(h_arr))  #check

    
    def multiply_arr(arr, const):
        new_arr = []
        for i in range(0, len(arr)-1):
            new_arr.append(arr[i]*const)
        return new_arr
    
    
    
    if plots:
        '''
        figure(figsize=(10, 15))
        subplot(3,1,1)
        plot(t_arr[0:-1], drag_curve_arr, '--', color = 'tomato', label = 'Trajectory')
        grid()
        xlim(0, time_array[-1]+0.1)
        xlabel('Time [sec]')
        ylabel('Drag [N]')
        '''
        
        figure(figsize=(10, 15))
        subplot(3,1,1)
        plot(t_arr[0:-1], ADAS_deployment_arr[0:-1], '-', color = 'black', label = 'ADAS Deployment')
        plot(nom_t[0:-1], nom_ADAS[0:-1], '--', color = 'tomato', label = 'Nominal ADAS Deployment')
        xlabel('Time [s]')
        ylabel('ADAS Dployment[%]')
        title('ADAS Deployment')
        grid()
        legend(loc = 'best')
        xlim(0, time_array[-1]+0.1)
        
        figure(figsize=(10, 15))
        subplot(3,1,1)
        
        height_plot = multiply(signal_h_arr, k_height)
        vel_plot = multiply(signal_v_arr, k_vel)
        acc_plot = multiply(signal_a_arr, k_acc)
        jerk_plot = multiply(signal_j_arr, k_jerk)
        
        plot(t_arr[0:-3], height_plot[0:-1], '-', color = 'black', label = 'Altitude Signal')
        plot(t_arr[0:-3], vel_plot[0:-1], '-', color = 'tomato', label = 'Velocity Signal')
        plot(t_arr[0:-3], acc_plot[0:-1], '-', color = 'blue', label = 'Acceleration Signal')
        plot(t_arr[0:-3], jerk_plot[0:-1], '-', color = 'forestgreen', label = 'Jerk Signal')
        xlabel('Time [s]')
        ylabel('Signal')
        title('PID Signals')
        grid()
        legend(loc = 'best')
        xlim(0, time_array[-1]+0.1)
        
        figure(figsize=(10, 15))
        subplot(3,1,1)
        plot(t_arr,array(h_arr), '-', color = 'black', label = 'Trajectory')
        plot(t_arr,array(h_arr_noised), '-', color = 'black', label = 'Noised Trajectory')
        plot(nom_t,array(nom_h), '--', color = 'tomato', label = 'Nominal Trajectory')
        grid()
        title('Trajectory')
        xlabel('Time [s]')
        ylabel('Height [m]')

        plot(t_arr[c],h_arr[c], 'o', color = 'black', label = 'Main Engine Cutoff')
        print 'MECO at', round(t_arr[c], 2), 'sec, at' , round(h_arr[c], 2), 'm'

        plot(t_arr[d],h_arr[d], 'o', color = 'tomato', label = 'Apogee')
        print 'Apogee at', round(t_arr[d], 2), 'sec, at' , round(h_arr[d], 2), 'm'
        legend(loc = 'best')
        xlim(0, time_array[-1]+0.1)
        ylim(-10, max(array(h_arr))+50)

        subplot(3,1,2)
        plot(t_arr, array(v_arr), '-', color = 'black', label = 'Velocity')
        plot(t_arr, array(v_arr_noised), '-', color = 'blue', label = 'Noised Velocity')
        plot(nom_t, nom_v, '--', color = 'tomato', label = 'Nominal Velocity')
        grid()
        title('Velocity')
        xlabel('Time [s]')
        ylabel('Velocity [m/s]')

        #plot(t_arr[c],v_arr[c], 'o', color = 'black', label = 'Main Engine Cutoff')
        print 'MECO at', round(v_arr[c], 2), 'm/s'

        plot(t_arr[d], v_arr[d], 'o', color = 'tomato', label = 'Apogee')
        xlim(0, time_array[-1]+0.1)
        ylim(min(v_arr)-5, v_arr[c] + 40)
        legend(loc = 'best')
        
        subplot(3,1,3)
        plot(t_arr[0:-1], a_arr[0:-1], '-', color = 'black', label = 'Acceleration')
        plot(t_arr[0:-1], a_arr_noised[0:-1], '-', color = 'blue', label = 'Noised Acceleration')
        plot(nom_t, nom_a, '--', color = 'tomato', label = 'Nominal Acceleration')
        xlabel('Time [s]')
        ylabel('Acceleration [m/sec^2]')
        title('Acceleration')
        grid()
        legend(loc = 'best')
        xlim(0, time_array[-1]+0.1)
        
        figure(figsize=(10, 15))
        subplot(3,1,2)
        plot(t_arr[0:-1], j_arr[0:-1], '-', color = 'black', label = 'Jerk')
        #plot(t_arr[0:-1], a_arr_noised[0:-1], '-', color = 'blue', label = 'Noised Acceleration')
        plot(nom_t, nom_j, '--', color = 'tomato', label = 'Nominal Jerk')
        xlabel('Time [s]')
        ylabel('Jerk [m/sec^3]')
        title('Jerk')
        grid()
        legend(loc = 'best')
        xlim(0, time_array[-1]+0.1)
        ylim(-100,200)
        
    
    return t_arr, v_arr, a_arr, h_arr, m_arr, ADAS_deployment_arr, round(h_arr[-1], 2), round(v_arr[c], 2)