import subprocess
import time
from datalog import datalog

Cprogram = subprocess.Popen(['./a.out'],stdout=subprocess.PIPE, stdin=subprocess.PIPE)

while(1)
    input = input()
	Cprogram.stdin.write("input")
	Cprogram.stdin.flush()
	A = Cprogram.stdout.readline().strip()
	print(A)


	# datalog(A)
	time.sleep(1)

# print(A)
exit(0)
