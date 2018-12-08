# Code that logs data and determines deployment percentages for subscale flight
# To be implemented on Dec. 8 by UCSC Rocket Team 2019

from numpy import *
from time import time
import subprocess
from Deployment import Deployment
from datalog import datalog

'''
Need to:
 - read data from pipe
 - write (what) data where ?
 - simulate to predict a after launch and Fd of rocket at MECO
'''


class Data_Log :
    def __init__ (self, fname) :
        self.fname = fname

    def log(self, data) :
        with open(self.fname, "a") as f:
            now = datetime.datetime.now()
            timestamp = now.strftime('%Y-%m-%d %H:%M:%S.%f')
            f.write("{},{}\n".format(timestamp, data))


# give deployment % (=0 unless between MECO and apogee events)
def deployment (ti):

    if ti <= t_start :
        deployment = 0              # no deployment before MECO
    elif Apogee == False:   
        deployment = depl_arr[1]    # grab next deployment percentage
        depl_arr.pop(0)             # remove used deployment value
    else :
        deployment = 0              # no deployment after apogee

    return deployment




# define constants (currently using J420 motor)

g = 9.81            # [m/s^2]gravitational constant 
time_res = 1. / 25  # [s] expecting motor to operate at 25 Hz
t_burn = 1.54       # [s] expected time for MECO
t_start = 1.        # [s] when to start deployment after MECO
t_apogee = 12.      # [s] expected time to reach apogee (actually 11.9 for J420)
t_end = 90.         # [s] max time that rocket should be in air
t_arr = np.arange(self.launch, self.end, self.step)  # array of all time steps
 
# constants for deployment calculation    
min_depl = 0.10     # [%] minimum deployment
max_depl = 0.80     # [%] maximum deployment
steps_depl = 4      # num steps in stair function between min and max depl



# open pipes to C programs to read IMU data and communicate with the motor 
DATA = subprocess.Popen(['./a.out'],stdout=subprocess.PIPE, stdin=subprocess.PIPE)     
MOTOR = subprocess.Popen(['./b.out'], stdout=subprocess.PIPE, stdin=subprocess.PIPE)     

# get deployment array from module
depl_arr = Deployment((t_ap-t_burn)/time_res, steps_depl, min_depl, max_depl) 

# create opjects for logging data
sensors = Data_Log('sensors.csv')
encoder = Data_Log('encoder.csv')
events = Data_Log('events.csv')



# Booleans for detection of MECO and Apogee
MECO = False
Apogee = False

# define near-zero buffers for detection of launch, MECO, and apogee
buffer_acc = .2     # approx acc due to drag at MECO instance 
buffer_vel = .1     # approx vel at MECO !! (How good is BB resolution?)
a_thresh = 8        # [gs] threshhold to detect launch (expect max of 10)

# want to store (some) data before launch is detected
launch_data = []    # holds pre-launch data
num_data_pts = 20   # arbitrary number of points to catch data pre-launch detection


# Waiting on launch pad, measuring acc to detect launch
while True :
    data = DATA.stdout.readline().strip()
    a = split(", ")  # get vertical acc data only for use

    # store and overwrite num_data_pts of data
    launch_data.append(data)
    if len(launch_data) > num_data_pts :
        launch_data.pop(0)

    if (a/g) >= a_thresh :
        events.log('Launch ')
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
    v = 
    a = 

    MOTOR.stdin.write(deployment(ti))     # pipe deployment % to the motor code
    encoder.log(MOTOR.stdout.readline().strip()) # write encoding to file

    

    # detect MECO as point when a is only gravity and drag or as the burn time
    if not MECO :
        if (a <= - (g + buffer_acc) or t_arr[i] > t_burn) :
            events.log('MECO ')
            MECO = True     
            continue


    # detect apogee with velocity (when negative) CHANGE (use pressure instead?)
    if (not Apogee) and MECO :
        if (v < buffer_vel or t_arr[i] > t_apogee) :
            events.log('Apogee ')
            Apogee = True 
            continue   # set to continue for actual to record data during descent


exit(0)