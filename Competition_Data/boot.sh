#!/bin/bash

LOGGING=/home/pi/PythonCodeLogFile
date >> $LOGGING
sudo -u pi python /home/pi/ADAS/Competition.py >> $LOGGING &&
sudo shutdown -H now
