# Code that logs data and determines deployment percentages for subscale flight
# To be implemented on Dec. 8 by UCSC Rocket Team 2019

import subprocess
import datetime 
import os
import signal


class Data_Log :
    def __init__ (self, fname) :
        self.fname = fname

    def log(self, data) :
        with open(self.fname, "a") as f:
            now = datetime.datetime.now()
            timestamp = now.strftime('%Y-%m-%d %H:%M:%S.%f')
            f.write("{},{}\n".format(timestamp, data))


depl_arr = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,\
            0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,\
            0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,\
            0.333333333333,0.333333333333,0.333333333333,\
            0.333333333333,0.333333333333,0.333333333333,\
            0.333333333333,0.333333333333,0.333333333333,\
            0.333333333333,0.333333333333,0.333333333333,\
            0.333333333333,0.333333333333,0.333333333333,\
            0.333333333333,0.333333333333,0.333333333333,\
            0.333333333333,0.333333333333,0.333333333333,\
            0.333333333333,0.333333333333,0.333333333333,\
            0.333333333333,0.333333333333,0.333333333333,\
            0.333333333333,0.333333333333,0.333333333333,\
            0.333333333333,0.333333333333,0.566666666667,\
            0.566666666667,0.566666666667,0.566666666667,\
            0.566666666667,0.566666666667,0.566666666667,\
            0.566666666667,0.566666666667,0.566666666667,\
            0.566666666667,0.566666666667,0.566666666667,\
            0.566666666667,0.566666666667,0.566666666667,\
            0.566666666667,0.566666666667,0.566666666667,\
            0.566666666667,0.566666666667,0.566666666667,\
            0.566666666667,0.566666666667,0.566666666667,\
            0.566666666667,0.566666666667,0.566666666667,\
            0.566666666667,0.566666666667,0.566666666667,\
            0.566666666667,0.8,0.8,0.8,0.8,0.8,0.8,0.8,\
            0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,\
            0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,\
            0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,\
            0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,\
            0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,\
            0.8,0.8,0.566666666667,0.566666666667,0.566666666667,\
            0.566666666667,0.566666666667,0.566666666667,\
            0.566666666667,0.566666666667,0.566666666667,\
            0.566666666667,0.566666666667,0.566666666667,\
            0.566666666667,0.566666666667,0.566666666667,\
            0.566666666667,0.566666666667,0.566666666667,\
            0.566666666667,0.566666666667,0.566666666667,\
            0.566666666667,0.566666666667,0.566666666667,\
            0.566666666667,0.566666666667,0.566666666667,\
            0.566666666667,0.566666666667,0.566666666667,\
            0.566666666667,0.566666666667,0.333333333333,\
            0.333333333333,0.333333333333,0.333333333333,\
            0.333333333333,0.333333333333,0.333333333333,\
            0.333333333333,0.333333333333,0.333333333333,\
            0.333333333333,0.333333333333,0.333333333333,\
            0.333333333333,0.333333333333,0.333333333333,\
            0.333333333333,0.333333333333,0.333333333333,\
            0.333333333333,0.333333333333,0.333333333333,\
            0.333333333333,0.333333333333,0.333333333333,\
            0.333333333333,0.333333333333,0.333333333333,\
            0.333333333333,0.333333333333,0.333333333333,\
            0.333333333333,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,\
            0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,\
            0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]

# give deployment % (=0 unless between MECO and apogee events)
def deployment (ti):

    if MECO == False :
        deployment = 0              # no deployment before MECO
    elif Apogee == False:   
        deployment = depl_arr[0]    # grab next deployment percentage
        depl_arr.pop(0)             # remove used deployment value
    else :
        deployment = 0              # no deployment after apogee

    return deployment




# define constants (currently using J420 motor)

g = 9.81            # [m/s^2]gravitational constant 
HZ = 25
time_res = 1./HZ    # [s] expecting motor to operate at 25 Hz
t_burn = 1.54       # [s] expected time for MECO
# t_start = 1.        # [s] when to start deployment after MECO
t_apogee = 12.      # [s] expected time to reach apogee (actually 11.9 for J420)
t_end = 90         # [s] max time that rocket should be in air
t_arr = range(0, t_end, int(round(t_end / step)))  # array of all time steps

t_arr = []
for i in range(t_end * HZ) :
	t_arr.append(i*time_res)

min_depl = 0.10     # [%] minimum deployment
max_depl = 0.80     # [%] maximum deployment
steps_depl = 4      # num steps in stair function between min and max depl



# open pipes to C programs to read IMU data and communicate with the motor 
DATA1 = subprocess.Popen(['./rc_altitude'],stdout=subprocess.PIPE, stdin=subprocess.PIPE)     
MOTOR = subprocess.Popen(['./MotorDriver/motorDriver'], stdout=subprocess.PIPE, stdin=subprocess.PIPE)     

# get deployment array from module
# depl_arr = Deployment((t_apogee-t_burn)/time_res, steps_depl, min_depl, max_depl) 

# create opjects for logging data
sensors = Data_Log('sensors.csv')
encoder = Data_Log('encoder.csv')
events = Data_Log('events.csv')


# Booleans for detection of MECO and Apogee
MECO = False
Apogee = False

# define near-zero buffers for detection of launch, MECO, and apogee
buffer_acc = .2     # [m/s^2] approx acc due to drag at MECO instance 
buffer_vel = .1     # [m/s] approx vel at MECO (How good is BB resolution??)
g_thresh = 5        # [gs] threshhold to detect launch (expect max of 10)

# want to store (some) data before launch is detected
num_data_pts = 40   # arbitrary number of points to catch data pre-launch detection
launch_data = [0] * num_data_pts    # holds pre-launch data
ay_index = 4


# Waiting on launch pad, measuring acc to detect launch
while True :
    data = DATA.stdout.readline().strip()
    dat = split(",")
    if (len(dat) < 10) :
	continue
    ay = dat[ay_index]     # get vertical acc data only for use
    ayy = dat[7]
    # store and overwrite num_data_pts of data
    launch_data.append(data)
    launch_data.pop(0)

    if ay >= g_thresh*g or ayy >= g_thresh*g :
        events.log('Launch ')     # log launch event
        break

# store the data at launch
for i in range(num_data_pts) :
    sensors.log(launch_data(i))


# in air, logging data throughout
for i in range(1, len(t_arr)) :
    
    ti = t_arr[i]   # current time

    
    data = DATA.stdout.readline().strip() # get sensor data through pipe 
    sensors.log(data)                     # write sensor data to file
    # get vertical v and a to check for events
    # v = 
    # a = 

    MOTOR.stdin.write(deployment(ti))     # pipe deployment % to the motor code
    MOTOR.stdin.flush()
    encoder.log(MOTOR.stdout.readline().strip()) # write encoding to file

    

    # detect MECO as point when a is only gravity and drag or as the burn time
    if not MECO :
        if (a <= - (g + buffer_acc) or t_arr[i] > t_burn) :
            events.log('MECO ')     # log MECO event
            MECO = True     
            continue


    # detect apogee with velocity (when negative) CHANGE (use pressure instead?)
    if (not Apogee) and MECO :
        if (v < buffer_vel or t_arr[i] > t_apogee) :
            events.log('Apogee ')     # log apogee event
            Apogee = True 
            continue   # set to continue for actual to record data during descent


os.killpg(os.getpgid(pro.pid), signal.SIGTERM) 

exit(0)
