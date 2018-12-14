# simulation code from 17-18 rocket team

from numpy import *
from matplotlib.pyplot import *
from astropy.io import ascii
from scipy.interpolate import interp1d
from scipy.interpolate import interp2d

#style.use('classic')

def num_solver(thrust_profile, rocket_mass, motor_mass, propellant_mass, time_res, temp, burn_time, max_deploy, t_start, t_deploy, wind_speed, mixing_factor, plots):
    
    gauss_steepness= 0.005  #this measures the proportion that the gaussian starts off, so the bigger it is the bigger the jump but the faster ADAS deploys
    sigma_squared = ((-1)*(t_deploy)**2)/(2*log(gauss_steepness))
    t_start = t_start+burn_time
    ##t_deploy = t_deploy + burn_time - t_start
    
    
    #windspeed#
    wind_speed = wind_speed*0.51444444444444 #convert knots to m/s
    rail_length = 3.6 #launch rail length
    
    rocket_time = ascii.read(thrust_profile)['time']
    thrust_curve = ascii.read(thrust_profile)['thrust']

    thrust_function = interp1d(rocket_time, thrust_curve)

    drag_curve_arr = []
    ADAS_deployment_arr = []
    
    #constants
    g = 9.81 #m/s^2
    
    temps = [0., 20., 40., 60.]
    densities = [1.293, 1.205, 1.127, 1.067]
        
    temp_func = interp1d(temps, densities, kind = 'quadratic')
    rho = temp_func(temp) # kg/m^3
    
    #print "The air has density",rho

    #initial conditions
    h0 = 0. #m  (height)
    v0 = 0. #m/s (velocity)
    theta0 = 0 #rad

    #rocket characteristics

    Wet_mass = motor_mass + rocket_mass + propellant_mass  #kg
    Dry_mass = motor_mass + rocket_mass #kg
    
    
    # 1D trajectory plot via Forward Euler Integration

    time_step = time_res #sec
    
    
    
    #Get the mass flow rate from the thrust curve
    t_dummy = 0     #dummy time variable
    total_thrust = 0
    while t_dummy<burn_time+1:
        total_thrust = total_thrust+thrust_function(t_dummy)
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
    ADAS_deploy_array = [0, 4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 56, 72]
    
    
    
    drag_function = interp2d(ADAS_vel_array, ADAS_deploy_array, drag_array, kind='cubic')
    
    #print "Drag: ", drag_function(30, 7)
    
    
    def mass_flow_rate(t):
        if t<=burn_time:
            return thrust_function(t)*(Wet_mass-Dry_mass)/total_thrust
        else:
            return 0
        
    def air_drag(hi, vi, f): #f is the angle
        return drag_function(vi, f) * air_pressure(hi, rho)/1.225   # density of air = 1.225
    
    def drag_curve(hi, vi, t): ################New year new me (function)
        if t<=t_start:
            deployment = 0
        else:
            if t_start<t<t_deploy+t_start:
                deployment = (max_deploy)*e**(-1*(t-t_deploy-t_start)**2/(2*sigma_squared))
            else:
                deployment = max_deploy
        drag = air_drag(hi, vi, deployment)
        drag_curve_arr.append(drag)
        ADAS_deployment_arr.append(deployment)
        return drag
        
    def height_step(hi, vi, theta):
       # print (1-cos(theta))*vi * time_step
        return  hi + vi * time_step * cos(theta) 
    
    def velocity_step(hi, vi, mi, ti, theta):
        if vi != 0:
            sign = vi/abs(vi)
        else:
            sign = 1
        return vi +(-g*cos(theta) - sign * drag_curve(hi, vi, ti)/mi + thrust_function(ti)/mi)*time_step
    
    def mass_step(mi, t): 
        return mi + (-mass_flow_rate(t))
    
    def air_pressure(h, p_i):
        R=8.31447       #Universal gas constant
        M=0.0289644     #Molar mass of air kg/mol
        T=temp+273.15   #temperature of the air at launch altitude in Kelvin
        return p_i*e**(-1*(g*M*h)/(R*T))
    
    def angle_calculate(angle, velocity, height, time):
        #if height<=rail_length:
        if time < burn_time:
            return 0
        else:
            new_angle = arctan((wind_speed + (velocity * sin(angle))) / (cos(angle) * velocity))
            k = mixing_factor #mixing factor of the old angle and new angle
            return (1-k) * angle + k * new_angle

    #arrays to push results to

    h_arr = [h0]
    v_arr = [v0]
    a_arr = [0]
    m_arr = [Wet_mass]
    time_array = [0]
    theta_arr = [theta0]

    #calculation
    i = 0
    
    
    #ascent
   
    while (time_array[i]<burn_time): 
    
        ti = (time_step)*(i)
        time_array.append(ti)
    
        hi = height_step(h_arr[i], v_arr[i], theta_arr[i])
        h_arr.append(hi)
    
        vi = velocity_step(h_arr[i], v_arr[i], m_arr[i], time_array[i], theta_arr[i])
        v_arr.append(vi)
    
        mi = mass_step(m_arr[i], ti)
        m_arr.append(mi)
        
        theta_i = angle_calculate(theta_arr[i], v_arr[i], h_arr[i], time_array[i])
        theta_arr.append(theta_i)
    
        i = i+1
    
    # coast
    c = i #mark transition to coast

    while (v_arr[i] > 0 and theta_arr[i] < pi/2 - 0.05): 
    
        ti = (time_step)*(i)
        time_array.append(ti)
    
        hi = height_step(h_arr[i], v_arr[i], theta_arr[i])
        h_arr.append(hi)
    
        vi = velocity_step(h_arr[i], v_arr[i], m_arr[i], time_array[i], theta_arr[i])
        v_arr.append(vi)
    
        mi = Dry_mass
        m_arr.append(mi)
        
        theta_i = angle_calculate(theta_arr[i], v_arr[i], h_arr[i], time_array[i])
        theta_arr.append(theta_i)
        
        i = i+1
       
    #descent

    d = i #mark transition to descent
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

    if plots:
        
        #############a function that differentiates the data##############3
        
        def derive_accel(t, V):
            accel_array = zeros(len(V)-1)
            for i in range(0, len(accel_array)):
                accel_array[i] = (V[i+1] - V[i])/(t[i+1]-t[i])
            return accel_array
    
        figure(figsize=(10, 15))
        subplot(3,1,1)
        plot(t_arr[0:-1], drag_curve_arr, '--', color = 'tomato', label = 'Trajectory')
        grid()
        xlim(0, time_array[-1]+0.1)
        xlabel('Time [sec]')
        ylabel('Drag [N]')
   
        figure(figsize=(10, 15))
        subplot(3,1,1)
        plot(t_arr,array(h_arr), '--', color = 'black', label = 'Trajectory')
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
        plot(t_arr, array(v_arr), '--', color = 'black', label = 'Velocity')
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
        accel_array = derive_accel(t_arr, array(v_arr))
        plot(t_arr[0:-1], accel_array, '-', color = 'black', label = 'Acceleration')
        #plot(t_arr[c], accel_array[c], 'o', color = 'black', label = 'Main Engine Cutoff')
        #plot(t_arr[d], accel_array[d], 'o', color = 'tomato', label = 'Apogee')
        xlabel('Time [s]')
        ylabel('Acceleration [m/sec^2]')
        title('Acceleration')
        grid()
        legend(loc = 'best')
        xlim(0, time_array[-1]+0.1)
        
        figure(figsize=(10, 15))
        subplot(3,1,1)
        plot(t_arr[0:-2], ADAS_deployment_arr[0:-1], '-', color = 'black', label = 'ADAS Deployment')
        xlabel('Time [s]')
        ylabel('ADAS Dployment[deg]')
        title('ADAS Deployment')
        grid()
        legend(loc = 'best')
        xlim(0, time_array[-1]+0.1)
        
        figure(figsize=(10, 15))
        subplot(3,1,1)
        plot(t_arr[0:-1], theta_arr[0:-1], '-', color = 'black', label = 'Angle')
        xlabel('Time [s]')
        ylabel('Angle [rad]')
        title('Trajectory Angle')
        grid()
        legend(loc = 'best')
        xlim(0, time_array[-1]+0.1)
    
    return t_arr, v_arr, accel_array, h_arr, m_arr, ADAS_deployment_arr, round(h_arr[-1], 2), round(v_arr[c], 2)
