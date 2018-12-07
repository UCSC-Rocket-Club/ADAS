import datetime

def datalog(s, timestamp=None, f_path="datalog.csv") :
    # Saves a string and timestamp (type string) to a CSV (f_path) in following format:
    # string, timestamp
    # If no timestamp, it'll create a timestamp in Y-M-D H:M:S.microsecond
    # TODO: Parse IMU data (data looks smth like accel[0, 1, 2] gyro [0, 1, 2])
    with open(f_path, "a") as f:
        if not timestamp:
            now = datetime.datetime.now()
            timestamp = now.strftime('%Y-%m-%d %H:%M:%S.%f')
        f.write("{},{}\n".format(timestamp, s))
