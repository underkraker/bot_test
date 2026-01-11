import time, subprocess
while True:
    try:
        cmd = "cut -d: -f1,5 /etc/passwd | grep 'LIM'"
        users = subprocess.check_output(cmd, shell=True).decode().splitlines()
        for l in users:
            u, info = l.split(':')
            lim = int(info.split('LIM ')[1])
            con = int(subprocess.check_output(f"ps -u {u} | grep sshd | wc -l", shell=True).decode().strip())
            if con > lim: subprocess.run(f"sudo pkill -u {u} -n", shell=True)
    except: pass
    time.sleep(10)
