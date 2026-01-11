import subprocess, psutil

def obtener_info_vps():
    return {
        "cpu": f"{psutil.cpu_percent()}%",
        "ram": f"{psutil.virtual_memory().percent}%",
        "uptime": subprocess.check_output("uptime -p", shell=True).decode().strip()
    }

def obtener_ip():
    try: return subprocess.check_output("curl -s https://api.ipify.org", shell=True).decode().strip()
    except: return "127.0.0.1"

def obtener_puertos():
    try: 
        # Comando corregido para filtrar solo los números de puertos externos activos
        cmd = "netstat -tunlp | grep LISTEN | awk '{print $4}' | awk -F: '{print $NF}' | sort -nu | grep -v '^$' | xargs | sed 's/ /, /g'"
        return subprocess.check_output(cmd, shell=True).decode().strip()
    except: 
        return "22, 80, 443"
        
