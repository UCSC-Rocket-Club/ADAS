import subprocess
import time
from datalog import datalog

Cprogram = subprocess.Popen(['./a.out'],stdout=subprocess.PIPE, stdin=subprocess.PIPE)     

for i in range(0,20) :
	Cprogram.stdin.write("feed me\n")
	Cprogram.stdin.flush()


	A = Cprogram.stdout.readline().strip()
	print(A)

	
	# datalog(A)
	time.sleep(1)

# print(A)
exit(0)