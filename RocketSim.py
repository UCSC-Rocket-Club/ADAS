# this code uses physical dynamics to 1D Euler Integrate and generate rocket sim data
# note that descent with parachutes is not accounted for
# currently does not handle deployment =/= 0

from numpy import *
from matplotlib.pyplot import *
from scipy.interpolate import interp1d, interp2d
from time import time
import datetime
import os.path
from Deployment import StepDeployment, GaussianDeployment
import pandas



class Rocket :
    def __init__ (self, thrust_profile, rocket_mass, motor_mass, propellant_mass, burn_time) :
        self.rocket_time, self.thrust_curve = np.loadtxt(thrust_profile, skiprows=1, unpack=True)
        self.thrust_function = interp1d(self.rocket_time, self.thrust_curve)
        self.wet_mass = motor_mass + rocket_mass + propellant_mass  # all masses are in kg
        self.dry_mass = motor_mass + rocket_mass
        self.propellant_mass = propellant_mass

class Times :
    def __init__ (self, t_burn, t_start, t_apogee, t_step) :
        self.burn = t_burn;     # motor burn time
        self.start = t_start  # time to start deployment
        self.end = 90           # rocket can only be in air for 90s
        self.step = t_step      # time step
        self.launch = 0.0       # time of launch, stays at 0
        self.launch_date = 0.0  # will be actual time() of launch to use as reference
        self.MECO = t_burn      # assume burn time is accurate
        self.apogee = t_apogee  # time of apogee
        self.arr = np.arange(self.launch, self.end, self.step)  # array of all time steps


# Holds N-dim arrays of data initialized to None with ICs
class Data :
    def __init__ (self, N, fname) :

        if os.path.exists(fname) :
            open(fname, 'w')
            # add random number to front of filename to avoid mixing data
            # fname = str(np.random.randint(100)) + fname
            print('Logging data to ' + fname)
        self.fname = fname

        self.h = [0.0]          # [m] height
        self.v = [0.0]          # [m/s] velocity
        self.a = [0.0]          # [m/s2] acceleration
        self.m = [0.0]          # [kg] mass
        self.theta = [x * pi/2 for x in np.ones(N)] # [rad] initially set to no noise (exactly vertical)
        self.drag = [0.0]       # [N] drag force
        self.deployment = [0.0] # [%] ADAS deployment

    # Saves a string and timestamp (type string) to a CSV (fname) in following format: timestamp,string
    def log (self, data) :
        with open(self.fname, "a") as f:
            now = datetime.datetime.now()
            # timestamp = now.strftime('%Y-%m-%d %H:%M:%S.%f')
            # f.write("{},{}\n".format(timestamp, data))
            f.write("{}\n".format(data))



# description of args :
# 'thrust_profile' is a text file describing the thrust curve (from the internet)
# 'rocket_mass' is mass with no motor, 'motor_mass' doesn't include 'propellant_mass'
# 'frequency' [HZ] is that of desired/expected updates to data
# 'burn_time' is motor's expected time to MECO, 't_start' is time after MECO to start deployment
# 't_apogee' is predicted apogee or a large enough number to capture data for flight until apogee+some
# 'plots' is a boolean for plotting data or not
def num_solver(thrust_profile, rocket_mass, motor_mass, propellant_mass, frequency, burn_time, t_apogee, t_start=0, t_deploy=1, max_deploy=0.8, plots=True, logfilename='data.csv') :


    # Define constants
    R = 8.31447         # [J/mol*K] Universal gas constant
    M = 0.0289644       # [kg/mol] Molar mass of air
    T = 288             # [K] Temperature of the air at launch altitude ?
    g = 9.81            # [m/s^2]
    P0 = 101325         # [Pa] Standard pressure at sea level
    L0 = 6.5            # [K/m] Standard temperature lapse rate

    # initialize rocket object
    Aeoline = Rocket(thrust_profile, rocket_mass, motor_mass, propellant_mass, burn_time)

    # initialize time object
    t_res = frequency ** (-1)
    t = Times(burn_time, t_start, t_apogee, t_res)   # CAREFUL, don't use t elsewhere

    # initialize data object
    data = Data(len(t.arr), logfilename)
    data.m[0] = Aeoline.wet_mass
    # data.theta = np.random.normal(pi/2, pi/1000, len(t.arr))     # theta = pi/2 with some noise (.18 deg)

    # initialize coefficient of drag function and rocket and flight objects
    drag_function = Get_Drag_Function()

    # initialize step deployment array
    # depl_arr = StepDeployment((t_apogee-burn_time)/t_res) #, steps_depl, min_depl, max_depl)
    # GD args : (t_deployment = 15, t_step = 1./25, t_start = 1, t_deploy = 1, max_deploy = 0.8, gauss_steepness = 0.005) :
    depl_arr = GaussianDeployment(t.apogee-t.burn, t.step, t.start, t_deploy, max_deploy)


    # Use Riemann sum to get the mass flow rate from the thrust curve
    N = 1000            # arbitrary 1000 time steps
    time_steps = linspace(0, burn_time, N)
    total_impulse = 0
    for ti in time_steps :
        total_impulse += Aeoline.thrust_function(ti) * burn_time / N
    print(' total impulse: ' + str(total_impulse))



    # The following fxns are for time ti, height hi, velocity vi, angle th, mass mi, pressure pi

    # Returns time function of motor's mass flow. returns [kg/s]
    def mass_flow_rate (ti):
        if ti <= t.burn:
            return -Aeoline.thrust_function(ti) * Aeoline.propellant_mass / total_impulse
        else:
            return 0

    # Pressure from barometric formula - not currently used
    def air_pressure (hi) :
        # return P0 * (T / (T + L0 * hi)) ** (g * M / R * L0)   # non-zero lapse rate
        return P0 * exp(-g * M * hi / (R * T))    # 0 lapse rate

    # Returns drag force and deployment percentage
    def drag_curve (vi, ti, i) :

        if ti <= t.start :
            deployment = 0
        elif (t.burn <= ti <= t.apogee) :
            deployment = depl_arr[0]      # deployment procedure
            depl_arr.pop(0)
            # deployment = 0.0
        else :
            deployment = 0

        data.deployment.append(deployment)
        drag = drag_function(vi, deployment)
        data.drag.append(drag)
        return drag

    def height_step (hi, vi) :
        return hi + vi * t.step

    def velocity_step (vi, ai) :
        return vi + ai * t.step

    # Generate a_y step
    thrust_curve = [0.0]
    df = pandas.read_csv('Fullscale_OR.csv')    # data frame
    ORTime = df['time'].astype(np.float).values.tolist()
    ORAcc = df['acceleration'].astype(np.float).values.tolist()
    OR_acc_function = interp1d(ORTime, ORAcc)
    def acc_step (vi, mi, ti, th, i) :
        if (ti < (t.MECO + t.start)) :
            return OR_acc_function(ti)          # use open rocket interpolated acceleration
        else :
            return -g - drag_curve(vi,ti,i) / mi
        # note to selves: log thrust and drag accelerations and compare plots with open rocket's
        # thrust_curve.append(Aeoline.thrust_function(ti))
        # return -g + (Aeoline.thrust_function(ti) - drag_curve(vi, ti, i)) * sin(th) / mi

    def mass_step (mi, ti) :
        return mi + mass_flow_rate(ti) * t.step




    ################################################################
    ########################## Simulation ##########################
    ################################################################

    # 1D trajectory plot via Forward Euler Integration
    data.log('time,altitude,velocity,acceleration,mass')

    for i in range (1, int(t.apogee / t.step)+10) :   # simulate until a bit (10) after apogee

        ti = t.arr[i]

        data.m.append(mass_step(data.m[i-1], ti))
        data.a.append(acc_step(data.v[i-1], data.m[i], ti, data.theta[i], i))
        data.v.append(velocity_step(data.v[i-1], data.a[i-1]))
        data.h.append(height_step(data.h[i-1], data.v[i-1]))

        if (abs(ti-t.burn-1) < t.step) :
            print('height and deployment at MECO')
            print(data.h[-1])
            print(data.v[-1])

    # Some python silliness (list->np array->flattened->list) to be able to cleanly write to the log file
    data.a = asarray(data.a).flatten().tolist()
    data.v = asarray(data.v).flatten().tolist()
    data.h = asarray(data.h).flatten().tolist()
    data.m = asarray(data.m).flatten().tolist()

    # Log data in following form: "datetime,simtime,height,velocity,acceleration"
    for i in range(0, len(data.a)) :
        data.log(str(t.arr[i]) + ',' + str(data.h[i]) + ',' + str(data.v[i]) + ',' + str(data.a[i]) + ',' + str(data.m[i]))

    h_apogee = max(data.h)
    print('Apogee at ' + str(h_apogee))


    # calculation of deducted points (ded)
    # 1% if 1<e<100ft, 1.5% if 101<e<250, 2.5% if 251<e<500, 3% if 501<e<1000, 4% if 1001<e<2000, fatal if e>2000
    h_error = h_apogee - 1609.34
    print('Apogee is ' + str(h_error) + 'm away from desired 1609.34m')
    h_error = abs(h_error)
    if h_error < 30.48 :        # < 100ft
        ded = h_error * .01
    elif h_error < 76.2 :       # < 250ft
        ded = h_error * .015
    elif h_error < 152.4 :      # < 500 ft
        ded = h_error * .025
    elif h_error < 304.8 :       # < 1000 ft
        ded = h_error * .03
    elif h_error < 609.6 :       # < 2000 ft
        ded = h_error * .04
    else :                      # > 2000 ft => disqualified
        ded = 100

    print ('Flight receives %.1f/100 points' % (100-ded))





    if plots :
        t_arr = t.arr[0:len(data.h)]
        c = int(t.burn * t.step)
        d = int(t.apogee * t.step)

        figure(figsize=(10, 15))
        subplot(3,1,1)
        plot(t_arr, data.drag, '--', color = 'tomato', label = 'Drag')
        plot(t_arr, thrust_curve, '.-', color = 'black', label = 'Thrust')
        grid()
        xlim(0, t_arr[-1]+0.1)
        legend(loc = 'best')
        xlabel('Time [sec]')
        ylabel('Forces [N]')

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
        xlim(0, t_arr[-1]+0.1)
        ylim(-10, max(array(data.v))+10)
        grid()
        title('Velocity')
        xlabel('Time [s]')
        ylabel('Velocity [m/s]')


        #plot(t.arr[c],v_arr[c], 'o', color = 'black', label = 'Main Engine Cutoff')
        # print 'MECO at', round(data.v[c], 2), 'm/s'

        # plot(t_arr[d], data.v[d], 'o', color = 'tomato', label = 'Apogee')
        # xlim(0, t_arr[-1]+0.1)
        # ylim(min(data.v[0:i-1])-5, data.v[c] + 40)
        # legend(loc = 'best')



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

        figure(figsize=(10, 15))
        subplot(3,1,1)
        plot(t_arr[0:-1], data.deployment[0:-1], '-', color = 'black', label = 'ADAS Deployment')
        xlabel('Time [s]')
        ylabel('ADAS Dployment [deg]')
        title('ADAS Deployment')
        grid()
        legend(loc = 'best')
        ylim(0, max(data.deployment))
        xlim(0, t.arr[-1]+0.1)

    return
    # return t_arr, v_arr, a_arr, j_arr, h_arr, m_arr, ADAS_deployment_arr, round(h_arr[-1], 2), round(v_arr[c], 2)


# Interpolates drag coefficients as fxn of rocket velocity [m/s] and ADAS deployment percentage
def Get_Drag_Function () :

    # Drag coefficient data from flow simulations with states P = 98000 [Pa], T = 283 [K], density = rho = 1.15 [kg/m^2]
    # NOTE: data excludes that for 10 degrees
    sim_drag_coeffs = [       # DUNCAN ROCKS (LOL JK)  :D
    [0, 0.4897130673,    0.4605084415,    0.4566277895,    0.457260162,     0.4577140061,    0.4570957994,    0.4566626055,    0.5642732454,    0.5680928992,    0.5717283138],
    [0, 0.5697580479,    0.4602782598,    0.456513712,     0.4567162609,    0.4569759963,    0.456424171,     0.455415689,     0.5583588651,    0.5620175824,    0.5649677736],
    [0, 0.5668725374,    0.4682819154,    0.4469762488,    0.4645024797,    0.4644837072,    0.4639810209,    0.4625354359,    0.556496065,     0.559965656,     0.562991906],
    [0, 0.5638586086,    0.4830633638,    0.4804639344,    0.481315034,     0.4815977549,    0.4822440287,    0.4804765347,    0.5557061413,    0.5589313185,    0.5619646087],
    [0, 0.5641773622,    0.4839314615,    0.4825487796,    0.4821114534,    0.4831116457,    0.4827254992,    0.4811014429,    0.5541560884,    0.5575369803,    0.5604568335],
    [0, 0.5690075644,    0.4846769576,    0.4816589436,    0.4822390455,    0.4827377599,    0.4830244712,    0.4806339902,    0.5587568886,    0.5619985844,    0.5647384353],
    [0, 0.5702164927,    0.4923129991,    0.4892673582,    0.4893980557,    0.4892061981,    0.4885889214,    0.4869239868,    0.5621926732,    0.5655911728,    0.5683652118],
    [0, 0.57425205,      0.5092990664,    0.5063569557,    0.5065504403,    0.5063751519,    0.5060755784,    0.5064538141,    0.5662279936,    0.5694119308,    0.5721914277],
    [0, 0.5792708916,    0.5054756846,    0.50307373,      0.5033542067,    0.5032704218,    0.5022323,       0.5047265086,    0.5713875199,    0.5744315084,    0.5768540181],
    [0, 0.5788864078,    0.5192401696,    0.5165947143,    0.5170544599,    0.5171723766,    0.5165778943,    0.5151439218,    0.5719901683,    0.5750984082,    0.5780046877]]
    sim_drag_coeffs = array(sim_drag_coeffs, dtype='float64')

    sim_velocities = array([0, 20, 40,  60,  80,  100, 120, 140, 160, 180, 200])  # [m/s] simulation velocities
    # ADAS_deploy_array = array([0, 14.4, 21.6, 28.8, 36, 43.2, 50.4, 57.6, 64.8, 72])     # degrees of deployment for sim data
    sim_deploy_percents = delete(linspace(0, 1, 11), 1)       # simlation deployment percentages


    # Cross-sectional area [m^2] of subscale with fin deployment corresponding to angles in ADAS_deploy_array
    sim_deploy_areas = [0.007127518874, 0.007256550874, 0.007411389274, 0.007566227674, 0.007695259674, 0.007811388474, 0.007914614074, 0.008017839674, 0.008095258874, 0.008185581274]
    # Convert areas from subscale to full scale (only thing that should change in this calc)
    sim_deploy_areas = [x * (5.5**2)/(3.15**2) for x in sim_deploy_areas]    # convert to full scale

    # Drag force = .5 * rho * A * v^2 * cd [N = kg*m/s^2]
    drag_force = 0.5 * 1.15 * transpose( transpose(sim_drag_coeffs * sim_velocities**2) * sim_deploy_areas )

    return interp2d(sim_velocities, sim_deploy_percents, drag_force, kind='cubic')
