
# Code that obtains and logs data and communicates deployment percentages for flight
# To be implemented on March 16 by UCSC Rocket Team 2019

import time
import datetime
import serial
from Deployment import StepDeployment
from gyroscope import IMU
from MS5611 import MS5611


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


# returns deployment % (=0 unless between MECO and apogee events)
def deployment () :

    if not MECO :
        deployment = 0              # no deployment before MECO
    elif not Apogee :   
        deployment = depl_arr[0]    # grab next deployment percentage
        depl_arr.pop(0)             # remove used deployment value
    else :
        deployment = 0              # no deployment after apogee

    return deployment




# define constants 
HZ = 25             # [s^-1] frequency of updates
dt = 1. / HZ        # [s] expecting motor to operate at 25 Hz
t_burn = 2.49       # [s] expected time for MECO
t_start = 1.        # [s] when to start deployment after MECO
t_apogee = 17.74    # [s] expected time to reach apogee (actually 11.9 for J420)
t_end = 90          # [s] max time that rocket should be in air


# define near-zero buffers for detection of launch, MECO, and apogee
buffer_acc = .2     # [m/s^2] approx acc due to drag at MECO instance 
g_thresh = 2      # [Gs] threshhold to detect launch (expect max of 10)
mile = 1609.34      # [m] 1 mile


# Booleans for detection of MECO and Apogee
MECO = False
Apogee = False

# get deployment array from module
# constants for deployment calculation    
# min_depl = 0.10     # [%] minimum deployment
# max_depl = 0.80     # [%] maximum deployment
# steps_depl = 4      # num steps in stair function between min and max depl
depl_arr = StepDeployment((t_apogee-t_burn)/dt) #, steps_depl, min_depl, max_depl)
depl_arr = [int(((float(i)/max(depl_arr)) * 9)) for i in depl_arr]
print(depl_arr)


# create opjects for logging data, arg is log filename
sensors = Data_Log('/home/pi/sensors.csv')
events = Data_Log('/home/pi/events.csv')
depFile = Data_Log('/home/pi/deployment.csv')

depFile.log('----------- Deployment Array is -------------')
depFile.log(depl_arr)

# Setting up IMU
imu = IMU()
index_vert_acc = 1      # index of vertical acceleration, read in [Gs]

# Setting up Altimeter
alt = MS5611(i2c=0x77)

# Open serial communication with motor driver
motor = serial.Serial('/dev/ttyS0', 115200)


# want to store (some) data before launch is detected
launch_data = []    # holds pre-launch data
num_data_pts = 20   # ~t(g_thresh)*HZ points to catch data pre-launch detection

# test
time.sleep(1)
motor.write("9\n".encode())
time.sleep(1)
motor.write("0\n".encode())

# Waiting on launch pad measure acceleration to detect launch with
while True :

    # only read every dt seconds
    try :
        time.sleep(dt - (time.time()-t_read))   # 0.005s error
    except :
        pass

    t_read = time.time()

    # read data from IMU
    acc = imu.get_accel_data()
    gyr = imu.get_gyro_data()


    # store and overwrite num_data_pts of data
    launch_data.append([acc, gyr])
    if len(launch_data) > num_data_pts :
        launch_data.pop(0)

    # check threshhold against vertical acceleration data
    if acc[index_vert_acc] >= g_thresh :
        events.log('\n-----LAUNCH-----\n')     # log launch event
        print("launch!!!")
        depFile.log('--------fucking lunch---------')
        break

t_launch = time.time()

# store the data at launch (the most recent)
for i in range(num_data_pts):
    sensors.log(launch_data[i])


sensors.log("\n-----IN AIR-----\n")

# in air, logging data throughout
for i in range(0, t_end*HZ) :

    # only read every dt seconds
    try :
        time.sleep(dt - (time.time()-t_read))
    except :
        pass 
    t_curr = time.time()
    t_flight = t_curr - t_launch


    # get acceleration and gyroscope data
    acc = imu.get_accel_data()
    gyr = imu.get_gyro_data()
    
    # write sensor data to file
    sensors.log([acc, gyr])

    # write deployment to motor
    message = str(int(deployment()))
    print message
    depFile.log(message)
    motor.write(message.encode())
    
    # 'string' +'\n' .encode()
    
    # detect MECO as point when a is only gravity and drag or as the expected burn time
    if not MECO :
        if (acc[index_vert_acc]+1) <= -buffer_acc or t_flight >= t_burn :
            events.log("\n-----MECO-----\n")
            sensors.log("\n-----MECO-----\n")
            depFile.log("\n-----MECO-----\n")
            print "MECO!"
             
            MECO= True   
            continue


    # use altimeter data to detect apogee
    alt.read()
    z = alt.getAltitude()
    sensors.log("Altitude:" + str(z))

    # detect APOGEE with altitude or precalculated time
    if MECO and not Apogee :
        if z >= mile or t_flight >= t_apogee :
            events.log("\n-----APOGEE-----\n")
            sensors.log("\n-----APOGEE-----\n")
            depFile.log("\n-----APOGEE-----\n")
            print "APOGEE!"

            print("the deployment array fuckin is: ")
            print(depl_arr)
            depFile.log("\n ---------DEPLOYMENT FUCKIN ARRAY IS: -----------\n")
            depFile.log(depl_arr)
            Apogee = True 
            continue    # continue to record data during descent


time.sleep(5)
print("the deployment array fuckin is: ")
print(depl_arr)

# close serial communication with moto driver
motor.close()

# closing all the files
sensors.close()
events.close()

exit(0)
