
# Code that obtains and logs data and communicates deployment percentages for flight
# To be implemented on March 16 by UCSC Rocket Team 2019

import time
import datetime
import serial
from Deployment import StepDeployment
from gyroscope import IMU
from MS5611 import MS5611


class Data_Log :
    def __init__ (self, fname, header='') :
        self.fname = fname
        self.file = open(fname, "a")
        self.file.write("{}\n".format(header))

    # Saves a string and timestamp (type string) to a CSV (f_path) in following format:
    # string, timestamp
    def log (self, data) :
        now = datetime.datetime.now()
        timestamp = now.strftime('%Y-%m-%d %H:%M:%S.%f')
        self.file.write("{},{}\n".format(timestamp, data))

    def close (self):
        self.file.close()


# returns deployment % (=0 unless between MECO and apogee events)
def deployment () :

    if not MECO :
        deployment = 0              # no deployment before MECO
    elif not Apogee :
        deployment = 0   
    else :
        deployment = 0              # no deployment after apogee

    return deployment




# define constants 
HZ = 40             # [s^-1] frequency of updates
dt = 1. / HZ        # [s] expecting motor to operate at 25 Hz
t_burn = 2.49       # [s] expected time for MECO
t_start = 1.        # [s] when to start deployment after MECO
t_apogee = 17.74    # [s] expected time to reach apogee (actually 11.9 for J420)
t_end = 20          # [s] max time that rocket should be in air


# define near-zero buffers for detection of launch, MECO, and apogee
buffer_acc = .2     # [m/s^2] approx acc due to drag at MECO instance 
g_thresh = 2        # [Gs] threshhold to detect launch (expect max of 10)
mile = 1609.34      # [m] 1 mile


# Booleans for detection of MECO and Apogee
MECO = False
Apogee = False


# create opjects for logging data, arg is log filename
sensors = Data_Log('/home/pi/sensors.csv', 'Acc, Gyr, Alt')
events = Data_Log('/home/pi/events.csv')
depFile = Data_Log('/home/pi/deployment.csv')

sensors.log('wtf ADAS why')



# Setting up IMU
imu = IMU()
index_vert_acc = 1      # index of vertical acceleration, read in [Gs]

# Setting up Altimeter
alt = MS5611(i2c=0x77)



# want to store (some) data before launch is detected
launch_data = []    # holds pre-launch data
num_data_pts = 20   # ~t(g_thresh)*HZ points to catch data pre-launch detection


speaker = serial.Serial('/dev/ttyS0', 115200)

# print("testing out speaker")
# time.sleep(1)
# speaker.write("9".encode())
# time.sleep(1)

# print("speaker should speak")


# speaker.write()


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
    alt.read()
    z = alt.getAltitude()


    # store and overwrite num_data_pts of data
    launch_data.append([acc, gyr, z])
    if len(launch_data) > num_data_pts :
        launch_data.pop(0)

    # check threshhold against vertical acceleration data
    if acc[index_vert_acc] >= g_thresh :
        events.log('\n-----LAUNCH-----\n')      # log launch event
        sensors.log('\n-----LAUNCH-----\n')     # log launch event
        depFile.log('\n-----LAUNCH-----\n')     # log launch event
        print("launch!!!")
        speaker.write("l".encode())
        break

t_launch = time.time()

# store the data at launch (the most recent)
for i in range(num_data_pts):
    sensors.log(launch_data[i])

# speaker.write()


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

    # use altimeter data to detect apogee
    alt.read()
    z = alt.getAltitude()
    # sensors.log("Altitude:" + str(z))
    
    # write sensor data to file
    sensors.log([acc, gyr, z])

    
    # detect MECO as point when a is only gravity and drag or as the expected burn time
    if not MECO :
        if (acc[index_vert_acc]+1) <= -buffer_acc or t_flight >= t_burn :
            events.log("\n-----MECO-----\n")
            sensors.log("\n-----MECO-----\n")
            depFile.log("\n-----MECO-----\n")
            print "MECO!"
            speaker.write("m".encode())
             
            MECO = True  

            # speaker.write() 
            continue




    # detect APOGEE with altitude or precalculated time
    if MECO and not Apogee :
        if z >= mile or t_flight >= t_apogee :
            events.log("\n-----APOGEE-----\n")
            sensors.log("\n-----APOGEE-----\n")
            depFile.log("\n-----APOGEE-----\n")
            print "APOGEE!"
            speaker.write("a".encode())

            Apogee = True 

            # speaker.write()
            continue    # continue to record data during descent


time.sleep(5)


# closing all the files
# sensors.close()
events.close()

speaker.write("d".encode())

# speaker.write()

speaker.close()

exit(0)
