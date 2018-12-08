'''
Output: 

full_arr # the array defining deployment percentage
'''
import numpy as np

n = 248 # number of steps
n_step = 4 # number of steps up or down
min_deploy = .1 # percentage of miimum deployment
max_deploy = .80 # Percentage of max deployment

step_arr = np.linspace(min_deploy, max_deploy, num=n_step) # step up and down array
                       
a = []
for i in step_arr :
    a.append((np.ones(int(n/(2*n_step)))*i))
a=np.array(a).flatten()
full_arr=np.concatenate((a, a[::-1])) # combine prev. array with step down array

