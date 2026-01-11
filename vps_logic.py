import subprocess, psutil

def obtener_info_vps():
    return {
        "cpu": f"{psutil.cpu_percent(interval=None)}%", # Optimizado para rapidez [cite: 2026-01-10]
        "ram": f"{psutil.virtual_memory().percent}%",
        "uptime": subprocess.check_output("uptime -p", shell=True).decode().strip()
    }

def obtener_ip():
    try: return subprocess.check_output("curl -s https://api.ipify.org", shell=True).decode().strip()
    except: return "127.0.0.1"

def obtener_puertos():
    try: 
        # Filtro corregido para mostrar solo números de puertos reales
        cmd = "netstat -tunlp | grep LISTEN | awk '{print $4}' | grep -oP '(?<=:)\\d+$' | sort -nu | xargs | sed 's/ /, /g'"
        puertos = subprocess.check_output(cmd, shell=True).decode().strip()
        return puertos if puertos else "22, 80, 443"
    except: return "22, 80, 443"

def listar_usuarios_ssh():
    try:
        # Lista usuarios reales para la selección por botones [cite: 2026-01-10]
        cmd = "awk -F: '$3 >= 1000 && $1 != \"nobody\" {print $1}' /etc/passwd"
        usuarios = subprocess.check_output(cmd, shell=True).decode().split()
        return usuarios
    except: return []
