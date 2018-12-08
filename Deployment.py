<<<<<<< HEAD
# Deployment.py
# gives a stair up/down function of deployment percentages
# n is the number of points and n_step is the number of steps in deployment %
# deployments are given as a percentage

import numpy as np
# import itertools as itertools

def Deployment (n=402, n_step=4, min_deploy = 0.10, max_deploy = 0.80)

	step_arr = np.linspace(min_deploy, max_deploy, num=n_step) # step up and down array
	                       
	a = []
	for i in step_arr :
	    a.append((np.ones(int(n/(2*n_step)))*i))
	a=np.array(a).flatten()
	full_arr=np.concatenate((a, a[::-1])) # combine prev. array with step down array

	# print(np.size(full_arr))

	# if oscillations are desired:

	# osc_arr=[] # oscillation array
	#for i, j in enumerate(itertools.cycle([max_deploy/2, max_deploy])): # oscillate between 40 and 80
	#    if i == int(n/3):  # loop n/3 times
	#        break
	#    osc_arr.append(j)  
	#osc_arr=np.array(osc_arr)

return a
=======
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

>>>>>>> 6b6d615cf04b5a367f6f5b7c7b2332bcdad1bed4
