import time
import subprocess
import os
import sys
import signal

ON_POSIX = 'posix' in sys.builtin_module_names

DATA = subprocess.Popen(['./sensors'],
                        stdout=subprocess.PIPE,
                        stdin=subprocess.PIPE,
                        bufsize=1,
                        close_fds=ON_POSIX,
                        preexec_fn=os.setsid)

passes = 0

while passes < 40:
    data = DATA.stdout.readline().strip()
    print(data)
    passes += 1

os.killpg(os.getpgid(DATA.pid), signal.SIGINT)  # Send the signal to all the process groups

