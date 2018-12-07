from numpy import *
from matplotlib.pyplot import *
from scipy.interpolate import interp1d, interp2d
from time import time
import numpy as np

'''
Need to:
 - write in deployment algorithm (use Eddie's code)
 - read data from pipe
 - write (what) data where ?
 - simulate to predict a after launch and Fd of rocket at MECO

'''


# note: t_arb(itrary) needs to be near t_apogee for retraction ensurance
class Times :
    def __init__ (self, t_burn, t_start, t_res, t_deploy, t_end) :
        self.burn = t_burn;     # motor burn time
        self.start = t_burn + t_start  # time to start deployment
        self.end = t_end        # time to end activity after apogee for insurance
        self.step = t_res       # time step
        self.deploy = t_deploy  # time from 0 to 100% deployment 
        self.launch = 0.0       # stays at 0
        self.launch_date = 0.0  # will be actual time() of launch to use as reference 
        self.MECO = t_arb       # time after launch of MECO 
        self.apogee = t_arb     # time after launch of apogee
        self.arr = np.arange(self.launch, self.end, self.step)  # array of all time steps


# popen C program
Cprogram = subprocess.Popen(['./a.out'],stdout=subprocess.PIPE, stdin=subprocess.PIPE)     


# define constants
g = 9.81            # [m/s^2]
time_res = 1. / 25  # 25 Hz
burn_time = 4.2     # [s] (approximately)
t_start = 

# initialize drag force function and rocket and flight objects
t_end = 90      # max time that rocket should be in air32
t = Times(burn_time, t_start, time_res, t_end)   # CAREFUL, don't use t elsewhere



def deployment (ti, i):

    if ti <= t.start :
        deployment = 0
    elif Apogee == False:   # modify gaussian business?
        deployment = 0      # insert some deployment procedure here
    else :
        deployment = 0

    data.deployment[i] = deployment
    return drag

# Waiting on launch pad, measuring acc to detect launch
a = 10
a_thresh = 9
while True :
    # read accelerometer data and update
    

    if a >= a_thresh :
        t.launch_date = time()
        break



# define buffers for determining launch, MECO, and apogee
buffer_acc = .2     
buffer_vel = .1

# False until detected or timed
MECO = False
Apogee = False

for i in range (1, len(t.arr)) :

    ti = t.arr[i]
    # get data through pipe 
    

    # detect MECO as point when a is only gravity and drag or as the burn time
    # thinking: acceleration should range from a_thresh -> g
    if not MECO :
        if (data.a[i] <= - (g + buffer_acc) or t.arr[i] > t.burn) :
            t_MECO = t.arr[i]
            MECO = True     # Boolean for MECO detected 
            continue

    # detect apogee with velocity (when negative) CHANGE (use pressure instead?)
    if (not Apogee) and MECO :
        if (data.v[i-1] < buffer_vel or t.arr[i] > t.end) :
            t.apogee = t.arr[i]
            Apogee = True   # Boolean for Apogee detected
            continue   # set to continue for actual to record data during descent


exit()