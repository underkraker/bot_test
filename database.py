import sqlite3

def crear_tablas():
    conn = sqlite3.connect('usuarios.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS resellers (id INTEGER PRIMARY KEY, creditos INTEGER DEFAULT 0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios_ssh (usuario TEXT PRIMARY KEY, vencimiento TEXT, owner_id INTEGER)''')
    conn.commit()
    conn.close()

def agregar_o_recargar_reseller(user_id, creditos):
    conn = sqlite3.connect('usuarios.db')
    c = conn.cursor()
    c.execute("INSERT INTO resellers (id, creditos) VALUES (?, ?) ON CONFLICT(id) DO UPDATE SET creditos = creditos + excluded.creditos", (user_id, creditos))
    conn.commit()
    conn.close()

def obtener_resellers():
    conn = sqlite3.connect('usuarios.db')
    c = conn.cursor()
    c.execute("SELECT id, creditos FROM resellers")
    res = c.fetchall()
    conn.close()
    return res

crear_tablas()
