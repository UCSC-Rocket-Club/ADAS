# this code uses physical dynamics to 1D Euler Integrate and generate rocket sim data
# note that descent with parachutes is not accounted for
# currently does not handle deployment =/= 0

from numpy import *
from matplotlib.pyplot import *
from scipy.interpolate import interp1d, interp2d
from time import time
import datetime
import os.path




class Rocket :
    def __init__ (self, thrust_profile, rocket_mass, motor_mass, propellant_mass, burn_time) :
        self.rocket_time, self.thrust_curve = np.loadtxt(thrust_profile, skiprows=0, unpack=True)
        self.thrust_function = interp1d(self.rocket_time, self.thrust_curve)
        self.wet_mass = motor_mass + rocket_mass + propellant_mass  # masses are in kg
        self.dry_mass = motor_mass + rocket_mass 
        self.propellant_mass = propellant_mass  

class Times :
    def __init__ (self, t_burn, t_start, t_apogee, t_step) :
        self.burn = t_burn;     # motor burn time
        self.start = t_burn + t_start  # time to start deployment
        self.end = 90           # rocket can only be in air for 90s
        self.step = t_step      # time step
        self.launch = 0.0       # time of launch, stays at 0
        self.launch_date = 0.0  # will be actual time() of launch to use as reference 
        self.MECO = t_burn      # assume burn time is accurate
        self.apogee = t_apogee  # time of apogee
        self.arr = np.arange(self.launch, self.end, self.step)  # array of all time steps


# holds N-dim arrays of data initialized to None with ICs
class Data :
    def __init__ (self, N, fname) :

    	if os.path.exists(fname) :
            # add random number to front of filename to avoid mixing data
    		fname = str(np.random.randint(100)) + fname
    		print('Logging data to ' + fname)
    	self.fname = fname

        self.h = [0.0]          # height
        self.v = [0.0]          # velocity
        self.a = [0.0]          # acceleration
        self.m = [0.0]          # mass
        self.theta = [x * pi/2 for x in np.ones(N)] # set to no-noise, exactly vertical initially
        # self.drag = [None] * N   # 
        # self.deployment = [None] * N # ?

    # Saves a string and timestamp (type string) to a CSV (f_path) in following format:
    # string, timestamp
    def log (self, data) :
        with open(self.fname, "a") as f:
            now = datetime.datetime.now()
            timestamp = now.strftime('%Y-%m-%d %H:%M:%S.%f')
            f.write("{},{}\n".format(timestamp, data))



# description of args :
# 'thrust_profile' is a text file describing the thrust curve (from the internet)
# 'rocket_mass' is mass with no motor, 'motor_mass' doesn't include 'propellant_mass'
# 'frequency' [HZ] is that of desired/expected updates to data
# 'burn_time' is motor's expected time to MECO, 't_start' is time after MECO to start deployment
# 't_apogee' is predicted apogee or a large enough number to capture data for flight until apogee+some
# 'plots' is a boolean for plotting data or not
def num_solver(thrust_profile, rocket_mass, motor_mass, propellant_mass, frequency, burn_time, t_apogee, t_start=0, plots=True, logfilename='data.csv') :

    
    # define constants
    R = 8.31447         # Universal gas constant [J/mol*K]
    M = 0.0289644       # Molar mass of air [kg/mol]
    T = 288             # temperature of the air at launch altitude in [K]    # we think this is standard temp not temp(launch h)
    g = 9.81            # [m/s^2]
    P0 = 101325         # [Pa] Standard pressure at sea level
    L0 = 6.5         # [K/m] Standard temperature lapse rate


    # initialize drag force function and rocket and flight objects
    drag_function = Get_Drag_Function()
    Aeoline = Rocket(thrust_profile, rocket_mass, motor_mass, propellant_mass, burn_time)
    t_res = 1. / frequency
    t = Times(burn_time, t_start, t_apogee, t_res)   # CAREFUL, don't use t elsewhere
    data = Data(len(t.arr), logfilename)
    data.m[0] = Aeoline.wet_mass
    data.theta = np.random.normal(pi/2, pi/1000, len(t.arr))     # theta = pi/2 with some noise

    # Use Riemann sum to get the mass flow rate from the thrust curve 
    N = 1000        # arbitrary 1000 time steps
    time_steps = linspace(0, burn_time, N)
    total_impulse = 0
    for ti in time_steps :
        total_impulse += Aeoline.thrust_function(ti) * burn_time / N
    print(' total impulse: ' + str(total_impulse))

    
        
    # for time ti, height hi, velocity vi, angle th, mass mi, pressure pi
    def mass_flow_rate (ti):
        if ti <= t.burn:
            return -Aeoline.thrust_function(ti) * Aeoline.propellant_mass / total_impulse
        else:
            return 0

    # pressure from barometric formula with non-zero lapse rate (L0)
    def air_pressure (hi):   # pressure not 3.14 [??]
        # return P0 * (T / (T + L0 * hi)) ** (g * M / R * L0)   # non-zero lapse rate
        return P0 * exp(-g * M * hi / (R * T))    # 0 lapse rate
    
    # Gives drag force and deployment percentage
    def drag_curve (vi, ti, i) :

        # if ti <= t.start :
        #     deployment = 0
        # elif Apogee == False:   # modify gaussian business?
        #     deployment = 0      # insert some deployment procedure here
        # else :
        deployment = 0

        drag = drag_function(vi, deployment)
        # data.drag[i] = drag
        # data.deployment[i] = deployment
        return drag
        
    # account for gyroscope data ??
    def height_step (hi, vi) :
        return hi + vi * t.step 
    
    def velocity_step (vi, ai) :
        return vi + ai * t.step
    
    # generate a_y step
    drag_f = 1.5       # arbitrary fudge factor
    def acc_step (vi, mi, ti, th, i) : 
        return -g + (Aeoline.thrust_function(ti) - drag_f * drag_curve(vi, ti, i)) * sin(th) / mi  
    
    def mass_step (mi, ti) : 
        return mi + mass_flow_rate(ti) * t.step
    

    ################################################################
    ########################## Simulation ##########################
    ################################################################

    # 1D trajectory plot via Forward Euler Integration
    data.log('time,altitude,velocity,acceleration')
    for i in range (1, int(t.apogee / t.step)+10) :   # simulate until a little after apogee
    
        ti = t.arr[i]
          
        data.m.append(mass_step(data.m[i-1], ti))
        data.a.append(acc_step(data.v[i-1], data.m[i], ti, data.theta[i], i))
        data.v.append(velocity_step(data.v[i-1], data.a[i-1]))
        data.h.append(height_step(data.h[i-1], data.v[i-1]))

    # some silliness to make the log clean
    data.a = np.asarray(data.a).flatten().tolist()
    data.v = np.asarray(data.v).flatten().tolist()
    data.h = np.asarray(data.h).flatten().tolist()
    data.m = np.asarray(data.m).flatten().tolist()

    for i in range(0, len(data.a)) :
        data.log(str(t.arr[i]) + ',' + str(data.h[i]) + ',' + str(data.v[i]) + ',' + str(data.a[i]))



    if plots :
    	t_arr = t.arr[0:len(data.h)]
        c = int(t.burn * t.step)
        d = int(t.apogee * t.step)
    
        # figure(figsize=(10, 15))
        # subplot(3,1,1)
        # plot(t.arr[0:-1], data.drag[0:-1], '--', color = 'tomato', label = 'Trajectory')
        # grid()
        # xlim(0, t.arr[-1]+0.1)
        # xlabel('Time [sec]')
        # ylabel('Drag [N]')
   
        figure(figsize=(10, 15))
        subplot(3,1,1)
        plot(t_arr,array(data.h), '--', color = 'black', label = 'Trajectory')
        grid()
        title('Trajectory')
        xlabel('Time [s]')
        ylabel('Height [m]')

        # plot(t.arr[c],data.h[c], 'o', color = 'black', label = 'Main Engine Cutoff')
        # print 'MECO at', round(t.arr[c], 2), 'sec, at' , round(data.h[c], 2), 'm'

        # plot(t.arr[d],data.h[d], 'o', color = 'tomato', label = 'Apogee')
        # print 'Apogee at', round(t.arr[d], 2), 'sec, at' , round(data.h[d], 2), 'm'
        legend(loc = 'best')
        xlim(0, t_arr[-1]+0.1)
        ylim(-10, max(array(data.h))+50)

        subplot(3,1,2)
        plot(t_arr, array(data.v), '--', color = 'black', label = 'Velocity')
        grid()
        title('Velocity')
        xlabel('Time [s]')
        ylabel('Velocity [m/s]')

        #plot(t.arr[c],v_arr[c], 'o', color = 'black', label = 'Main Engine Cutoff')
        # print 'MECO at', round(data.v[c], 2), 'm/s'

        plot(t_arr[d], data.v[d], 'o', color = 'tomato', label = 'Apogee')
        xlim(0, t_arr[-1]+0.1)
        ylim(min(data.v[0:i-1])-5, data.v[c] + 40)
        legend(loc = 'best')
        
        
        
        subplot(3,1,3)
        plot(t_arr[0:-1], data.a[0:-1], '-', color = 'black', label = 'Acceleration')
        #plot(t.arr[c], accel_array[c], 'o', color = 'black', label = 'Main Engine Cutoff')
        #plot(t.arr[d], accel_array[d], 'o', color = 'tomato', label = 'Apogee')
        xlabel('Time [s]')
        ylabel('Acceleration [m/sec^2]')
        title('Acceleration')
        grid()
        legend(loc = 'best')
        xlim(0, t_arr[-1]+0.1)
        
        # figure(figsize=(10, 15))
        # subplot(3,1,1)
        # plot(t.arr[0:-1], data.deployment[0:-1], '-', color = 'black', label = 'ADAS Deployment')
        # xlabel('Time [s]')
        # ylabel('ADAS Dployment [deg]')
        # title('ADAS Deployment')
        # grid()
        # legend(loc = 'best')
        # ylim(0, max(data.deployment)+10)
        # xlim(0, t.arr[-1]+0.1)

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
    
    pause(1)
    # are these velocities sufficient ?
    ADAS_vel_array = array([0, 20, 40, 60, 80, 100, 120, 140, 160, 180, 200, 220, 240, 250])
    ADAS_deploy_array = array([0, 5.5555, 11.1111, 16.6667, 22.2222, 27.7778, 33.3333, 38.8888, 44.4444, 50, 55.5555, 77.7778, 100])

    # why cubic ?
    return interp2d(ADAS_vel_array, ADAS_deploy_array, array(drag_array,dtype='float64'), kind='cubic')