from numpy import *
from matplotlib.pyplot import *
from astropy.io import ascii
from scipy.interpolate import interp1d
from scipy.interpolate import interp2d

ADAS_deployment_arr=[]

def Move_ADAS(t,max_deployment, t_MECO,t_appogy):
    
    global deployment
    
    if t<=t_MECO:
        #if engines are burning, deploy ADAS 0%
        deployment=0.0
        ADAS_deployment_arr.append(deployment)
        
    if t_MECO<t<=t_appogy:
        #if engines stop burning and the rocket hasn't hit appogy, deploy ADAS as follows
        
        t_ADAS=t_appogy-t_MECO #time between engine vut off and appogy
        t_step=t_ADAS/10.0 #divide time into 10 sections 
        
        if t_MECO<t<=t_step+t_MECO:
            #between MECO and 1 time step, deploy ADAS 10% (small jump test)
            deployment= max_deployment*.10
            ADAS_deployment_arr.append(deployment)
            
        if t_step+t_MECO<t<=t_step*2.0+t_MECO:
            #between 1 time step and 2 time steps, deploy ADAS 20% (small jump test)
            deployment= max_deployment*.20
            ADAS_deployment_arr.append(deployment)
            
        if t_step*2.0+t_MECO<t<=t_step*3.0+t_MECO:
            #between 2 time steps and 3 time steps, deploy ADAS 30% (small jump test)
            deployment= max_deployment*.30
            ADAS_deployment_arr.append(deployment)
            
        if t_step*3.0+t_MECO<t<=t_step*4.0+t_MECO:
            #between 3 time steps and 4 time steps, deploy ADAS 80% (big jump test)
            deployment= max_deployment*.80
            ADAS_deployment_arr.append(deployment)
            
        if t_step*4.0+t_MECO<t<=t_step*6.0+t_MECO:
            #between 4 time steps and 6 time steps, deploy ADAS 10% (big jump test and hold)
            deployment=max_deployment*.10
            ADAS_deployment_arr.append(deployment)
            
        if t_step*6.0+t_MECO<t<=t_appogy:
            #between 6 time steps and appogy, deploy ADAS in sawtooth motion 
            # with amplitude of .1% and period of .1 seconds (Fast, Quick movement test)
            deployment = max_deployment*(.2/pi)*arctan(1.0/tan(t*pi/.1)) + 60
            ADAS_deployment_arr.append(deployment)
            
    if t>t_appogy:
        #after appogy, retract fins 
        deployment = 0
        ADAS_deployment_arr.append(deployment)
            
    return 

        