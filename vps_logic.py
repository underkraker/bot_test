import subprocess, psutil

def listar_usuarios_ssh():
    # Solo lista usuarios reales creados en el sistema
    cmd = "awk -F: '$3 >= 1000 && $1 != \"nobody\" {print $1}' /etc/passwd"
    return subprocess.check_output(cmd, shell=True).decode().split()

def obtener_puertos():
    # Extrae solo los números de puerto para limpieza
    cmd = "netstat -tunlp | grep LISTEN | awk '{print $4}' | grep -oP '(?<=:)\\d+$' | sort -nu | xargs | sed 's/ /, /g'"
    p = subprocess.check_output(cmd, shell=True).decode().strip()
    return p if p else "22, 80, 443"

def obtener_info_vps():
    # Rapidez optimizada sin intervalos [cite: 2026-01-10]
    return {
        "cpu": f"{psutil.cpu_percent(interval=None)}%", 
        "ram": f"{psutil.virtual_memory().percent}%",
        "uptime": subprocess.check_output("uptime -p", shell=True).decode().strip()
    }

def obtener_ip():
    try: return subprocess.check_output("curl -s https://api.ipify.org", shell=True).decode().strip()
    except: return "127.0.0.1"
