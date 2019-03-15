# Code that logs data and determines deployment percentages for subscale flight
# To be implemented on Dec. 8 by UCSC Rocket Team 2019

import time
import subprocess
import datetime
import os
import signal
from Deployment import StepDeployment

# Queue needed to read lines from encoder without holding up Py program
# https://stackoverflow.com/questions/375427/non-blocking-read-on-a-subprocess-pipe-in-python
# try/except not needed if Py version is known/set
import sys
try:
    from queue import Queue, Empty
except ImportError:
    from Queue import Queue, Empty  # python 2.x

ON_POSIX = 'posix' in sys.builtin_module_names

def enqueue_output(out, queue):
    for line in iter(out.readline, b''):
        queue.put(line)
    out.close()

def signal_handler(sig, frame):
    print("You exited the program!\n")
    os.killpg(os.getpgid(DATA.pid), signal.SIGINT) 
    os.killpg(os.getpgid(MOTOR.pid), signal.SIGINT) 
    sensors.close()
    events.close()
    encoder.close()
    exit(0)

# this will handle any Ctrl+C that is sent to the program
# so it correclty shutdowns the processes it opened
signal.signal(signal.SIGINT, signal_handler)

class Data_Log :
    def __init__ (self, fname) :
        self.fname = fname
        self.file = open(fname, "a")

    # Saves a string and timestamp (type string) to a CSV (f_path) in following format:
    # string, timestamp
    def log (self, data) :
        now = datetime.datetime.now()
        timestamp = now.strftime('%Y-%m-%d %H:%M:%S.%f')
        self.file.write("{},{}\n".format(timestamp, data))

    def close(self):
        self.file.close()


# give deployment % (=0 unless between MECO and apogee events)
def deployment () :

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
HZ = 25             # [1/s] frequency of updates
time_res = 1./25    # [s] expecting motor to operate at 25 Hz
t_burn = 1.54       # [s] expected time for MECO
# t_start = 1.      # [s] when to start deployment after MECO
t_apogee = 12.      # [s] expected time to reach apogee (actually 11.9 for J420)
t_end = 90          # [s] max time that rocket should be in air
t_arr = [] 



# populating array with time steps
for i in range(0, HZ*t_end) :
    t_arr.append(i * time_res)
t_arr.append(t_end)



# get deployment array from module
# constants for deployment calculation    
# min_depl = 0.10     # [%] minimum deployment
# max_depl = 0.80     # [%] maximum deployment
# steps_depl = 4      # num steps in stair function between min and max depl
depl_arr = StepDeployment((t_apogee-t_burn)/time_res) #, steps_depl, min_depl, max_depl)


# open pipes to C programs to read IMU data and communicate with the motor 
DATA = subprocess.Popen(['./IMU/sensors'],stdout=subprocess.PIPE, stdin=subprocess.PIPE, bufsize=1, close_fds=ON_POSIX)     
# MOTOR = subprocess.Popen(['./MotorDriver/motorDriver'], stdout=subprocess.PIPE, stdin=subprocess.PIPE, bufsize=1, close_fds=ON_POSIX)  
''' Note about close_fds from docs: 
 If close_fds is true, all file descriptors except 0, 1 and 2 will be closed before the child process is executed. 
 Unix only). Or, on Windows, if close_fds is true then no handles will be inherited by the child process. 
 Note that on Windows, you cannot set close_fds to true and also redirect the standard handles by setting stdin, stdout or stderr. '''
 # needed? needed on DATA pipe ??
# queue = Queue()
# thread = Thread(target=enqueue_output, args=(MOTOR.stdout, queue))
# thread.daemon = True # thread dies with the program
# thread.start()

# create opjects for logging data, arg is log filename
sensors = Data_Log('/home/debian/sensors.csv')
encoder = Data_Log('/home/debian/encoder.csv')
events = Data_Log('/home/debian/events.csv')


# Booleans for detection of MECO and Apogee
MECO = False
Apogee = False

# define near-zero buffers for detection of launch, MECO, and apogee
buffer_acc = .2     # [m/s^2] approx acc due to drag at MECO instance 
buffer_vel = .2     # [m/s] approx vel at MECO (How good is BB resolution??)
g_thresh = 1.5      # [gs] threshhold to detect launch (expect max of 10)

# want to store (some) data before launch is detected
launch_data = []    # holds pre-launch data
num_data_pts = 20   # arbitrary number of points to catch data pre-launch detection
                    # should be t(g_thresh) * HZ

time.sleep(5)       # It takes a while for the sensors to fire up.
                    
index_vert_vel = 1      # index 1 is the vertical velocity
index_vert_acc = 4      # index 4 is the kalman filtered Vertical Accelaration m/s^2
index_K_vert_acc = 7    # index 7 is the raw Z-axis acceleration in m/s^2

# Waiting on launch pad, measuring acceleration to detect launch with
while True :
    data = DATA.stdout.readline().strip()   # get sensor output data
    dat = data.split(",")  # get vertical acc data only for use
    if len(dat) < 10:      # go to next line if reading headers/text rather than data
        continue

    # store and overwrite num_data_pts of data
    launch_data.append(data)
    if len(launch_data) > num_data_pts :
        launch_data.pop(0)

    # check threshhold against both Kalman- and non-filtered vertical acceleration data
    if (float(dat[index_vert_acc]) >= g_thresh * g) or (float(dat[index_K_vert_acc]) >= g_thresh * g):
        events.log('Launch')     # log launch event
        # tell motor code to start!!
        break

# store the data at launch (the most recent )
for i in range(num_data_pts):
    sensors.log(launch_data[i])


sensors.log("\n----IN AIR-----\n")

start_air_time = time.time()

# in air, logging data throughout
for i in range(1, len(t_arr)+1) :
    # ti = t_arr[i]   # current time

    data = DATA.stdout.readline().strip() # get sensor data through pipe 
    dat = data.split(",")                 # parse data by commas
    sensors.log(data)                     # write sensor data to file
    
    # get vertical velocity and acceleration to check for events
    v = dat[index_vert_vel]     # [m/s]
    a = dat[index_vert_acc]     # [m/s^2]

    MOTOR.stdin.write(deployment())     # pipe deployment % to the motor code
    MOTOR.stdin.flush()
    
    # to avoid holdup - need to do for data reading ? 
    # https://stackoverflow.com/questions/375427/non-blocking-read-on-a-subprocess-pipe-in-python
    # read line without blocking
    try :  line = q.get_nowait() # or q.get(timeout=.1)
    except Empty :
        print('no output yet')  # do nothing
    else: # got line
        encoder.log(MOTOR.stdout.readline().strip()) # write encoding from the driver to file

    
    # detect MECO as point when a is only gravity and drag or as the burn time
    if not MECO :
        if (a <= - (g + buffer_acc) or (time.time() - start_air_time > t_burn)):
            events.log('MECO ')     # log MECO event
            sensors.log("\n----MECO-----\n")
            MECO = True   
            continue


    # detect apogee with velocity (when negative) CHANGE (use pressure instead?)
    if (not Apogee) and MECO :
        if (v < buffer_vel or (time.time() - start_air_time) > t_apogee):
            events.log('Apogee ')     # log apogee event
            sensors.log("\n----APOGEE-----\n")
            Apogee = True 
            continue    # continue to record data during descent



# send kill signal to exit c program cleanly
os.killpg(os.getpgid(DATA.pid), signal.SIGINT) 
os.killpg(os.getpgid(MOTOR.pid), signal.SIGINT) 

# closing all the files
sensors.close()
events.close()
encoder.close()

exit(0)
