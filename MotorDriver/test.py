import subprocess
import time
import os

Cprogram = subprocess.Popen(['./motorDriver'],stdout=subprocess.PIPE, stdin=subprocess.PIPE, preexec_fn=os.setsid)

for i in range(0,50, 10):
    #inme = input("gimmie a position")
        print("i is currently " +str(i))
        Cprogram.stdin.write(str(i))
	Cprogram.stdin.flush()
#	A = Cprogram.stdout.readline().strip()
#	print(A)


	# datalog(A)
	time.sleep(1)

os.killpg(os.getpgid(Cprogram.pid), signal.SIGKILL)  # Send the signal to all the process groups
# print(A)
