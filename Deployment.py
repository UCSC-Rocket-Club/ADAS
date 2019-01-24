# Deployment.py returns has modules that return deployment lists
# deployments are given as a percentage, can be changed with ConvertArray


import numpy as np

#### This matplotlib code can be commented out because will not be used during flight
# import matplotlib
# matplotlib.use('TkAgg') # Needed for running when python isn't installed as a framework
# import matplotlib.pyplot as plt

# import itertools as itertools

# gives a stair up/down function of deployment percentages between min_ and max_
# n is the number of points and n_step is the number of steps in deployment %
def StepDeployment (n = 402, n_step = 4, min_deploy = 0.10, max_deploy = 0.80) :

	step_arr = np.linspace(min_deploy, max_deploy, num = n_step) # step up and down array
	                       
	a = []
	step_size = int(n / n_step / 2)		# divide into 2: step up and step down
	for i in step_arr :
	    a.append(np.ones(step_size,) * i)
	a = np.array(a).flatten()
	full_arr = np.concatenate((a, a[::-1])) # combine prev. array with step down array

	# oscillations:

	# osc_arr=[] # oscillation array
	# for i, j in enumerate(itertools.cycle([max_deploy/2, max_deploy])): # oscillate between 40 and 80
	#    if i == int(n/3):  # loop n/3 times
	#        break
	#    osc_arr.append(j)  
	# osc_arr=np.array(osc_arr)

	return full_arr.tolist()


# guassian deployment curve. source: Nitay
# [0, t_deployment] is time interval for ADAS deployment 
# max_deploy is percentage of maximum deployment
# t_start is time to start 
# t_deploy is time for ADAS to deploy from 0 to max_deploy
# gauss_steepness measures the proportion that the gaussian starts off, bigger => faster deployment 
def GaussianDeployment (t_deployment = 15, t_step = 1./25, t_start = 1, t_deploy = 1, max_deploy = 0.8, gauss_steepness = 0.005) :

	sigma_squared = -t_deploy ** 2 / (2 * np.log(gauss_steepness))
	deployment = [0.0]
	for t in np.arange(0, t_deployment, t_step) : 
		if t < t_start :
			deployment.append(0.0)
		elif t_start <= t < (t_deploy + t_start) :
			deployment.append( max_deploy * np.e**(-.5 * (t-t_deploy-t_start)**2 / sigma_squared) )
		else :
			deployment.append(max_deploy)
	return deployment


# This method will not be used during flight, so it is commented out
# def PlotDeployment (array, t_end = None) :
# 	if t_end is None :
# 		plt.plot(array)
# 		plt.xlabel('deployment index')
# 	else :
# 		plt.plot(linspace(0, t_end, len(array)), array)
# 		plt.xlabel('time (s)')
# 	plt.ylabel('deployment')
# 	plt.title('Deployment Profile')
# 	plt.grid(True)
# 	plt.show()
# 	return


# converts array between formats
# if array is initially %'s, maximum should be 90 degrees or pi/4 radians
def ConvertArray (array, maximum) :
	return [x * maximum for x in array]
