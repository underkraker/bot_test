import subprocess, psutil

def listar_usuarios_ssh():
    try:
        # Extrae usuarios creados por el bot (con ID >= 1000)
        cmd = "awk -F: '$3 >= 1000 && $1 != \"nobody\" {print $1}' /etc/passwd"
        return subprocess.check_output(cmd, shell=True).decode().split()
    except: return []

def obtener_puertos():
    try:
        # Solo números para evitar el error de la imagen
        cmd = "netstat -tunlp | grep LISTEN | awk '{print $4}' | grep -oP '(?<=:)\\d+$' | sort -nu | xargs | sed 's/ /, /g'"
        p = subprocess.check_output(cmd, shell=True).decode().strip()
        return p if p else "22, 80, 443"
    except: return "22, 80, 443"

def obtener_info_vps():
    return {"cpu": f"{psutil.cpu_percent(interval=None)}%", "ram": f"{psutil.virtual_memory().percent}%", "uptime": subprocess.check_output("uptime -p", shell=True).decode().strip()}

def obtener_ip():
    try: return subprocess.check_output("curl -s https://api.ipify.org", shell=True).decode().strip()
    except: return "127.0.0.1"
