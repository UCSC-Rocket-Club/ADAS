from numpy import *
from time import time
import subprocess

'''
Need to:
 - write in deployment algorithm (use Eddie's code)
 - read data from pipe
 - write (what) data where ?
 - simulate to predict a after launch and Fd of rocket at MECO
'''


class Times :
    def __init__ (self, t_burn, t_start, t_res, t_deploy, t_end) :
        self.burn = t_burn;     # motor burn time
        self.start = t_burn + t_start  # time to start deployment
        self.end = t_end        # time to end activity after apogee for insurance
        self.step = t_res       # time step
        self.deploy = t_deploy  # time from 0 to 100% deployment 
        self.launch = 0.0       # stays at 0
        self.launch_date = 0.0  # will be actual time() of launch to use as reference 
        self.MECO = t_end       # time after launch of MECO 
        self.apogee = t_end     # time after launch of apogee
        self.arr = np.arange(self.launch, self.end, self.step)  # array of all time steps


Cprogram = subprocess.Popen(['./a.out'],stdout=subprocess.PIPE, stdin=subprocess.PIPE)     
Cprogram1 = subprocess.Popen(['./b.out'], stdout=subprocess.PIPE, stdin=subprocess.PIPE)     

# currently for J825
# define constants
g = 9.81            # [m/s^2]
time_res = 1. / 25  # 25 Hz
burn_time = 1.2     # [s] (approximately)
t_start = 1         # [s]
# approx apogee at 14.4s    => 13s of adjustments
t_end = 90      # max time that rocket should be in air


t = Times(burn_time, t_start, time_res, t_end)   # CAREFUL, don't use t elsewhere



def deployment (i):

    if ti <= t.start :
        deployment = 0
    elif Apogee == False:   # modify gaussian business?
        deployment = depl_arr[i]      # insert some deployment procedure here
    else :
        deployment = 0

    return deployment

# Waiting on launch pad, measuring acc to detect launch
a_thresh = 10   # [g]s a_thresh = 180 m/s^2
while True :
    # save and overwrite .1s worth of data
    data = Cprogram.stdout.readline().strip()
    acc_data = split(", ")

    if a/g >= a_thresh :
        t.launch_date = time()
        break



# define buffers for determining launch, MECO, and apogee
buffer_acc = .2     
buffer_vel = .1

# Booleans for detection of MECO and Apogee
MECO = False
Apogee = False

for i in range(1, len(t.arr)) :

    ti = t.arr[i]

    # get data through pipe 
    
    data = Cprogram.stdout.readline().strip()
    datalog()
    
    # write deployment to another C code

    # detect MECO as point when a is only gravity and drag or as the burn time
    if not MECO :
        if (data.a[i] <= - (g + buffer_acc) or t.arr[i] > t.burn) :
            t_MECO = t.arr[i]
            MECO = True     
            continue

    # detect apogee with velocity (when negative) CHANGE (use pressure instead?)
    if (not Apogee) and MECO :
        if (data.v[i] < buffer_vel or t.arr[i] > t.end) :
            t.apogee = t.arr[i]
            Apogee = True 
            # set rest of deployments to 0
            continue   # set to continue for actual to record data during descent

# write launch time, MECO time, Apogee time
exit(0)