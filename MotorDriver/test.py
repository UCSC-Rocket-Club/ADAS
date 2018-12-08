import subprocess
import time
import os

Cprogram = subprocess.Popen(['./motorDriver'],stdout=open('adae.txt','w'), stdin=subprocess.PIPE, preexec_fn=os.setsid)

while(1):
        inme = input("gimmie a position")
        Cprogram.stdin.write(str(inme))
	Cprogram.stdin.flush()
#	A = Cprogram.stdout.readline().strip()
#	print(A)


	# datalog(A)
	time.sleep(1)

# print(A)
os.killpg(os.getpgid(pro.pid), signal.SIGTERM)
exit(0)
