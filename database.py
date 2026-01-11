import sqlite3
DB_NAME = "chumo_bot.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME, timeout=10)
    conn.execute('PRAGMA journal_mode=WAL')
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS resellers (user_id INTEGER PRIMARY KEY, creditos INTEGER DEFAULT 0)')
    cursor.execute('CREATE TABLE IF NOT EXISTS usuarios_ssh (username TEXT PRIMARY KEY, password TEXT, expiracion DATE, reseller_id INTEGER, limite INTEGER)')
    conn.commit()
    conn.close()

def obtener_resellers():
    conn = get_connection(); cursor = conn.cursor()
    cursor.execute("SELECT user_id, creditos FROM resellers"); res = cursor.fetchall()
    conn.close(); return res if res else []

def agregar_o_recargar_reseller(u_id, creds):
    conn = get_connection(); cursor = conn.cursor()
    cursor.execute("INSERT INTO resellers (user_id, creditos) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET creditos = creditos + ?", (u_id, creds, creds))
    conn.commit(); conn.close()

def restar_credito(u_id):
    conn = get_connection(); cursor = conn.cursor()
    cursor.execute("UPDATE resellers SET creditos = creditos - 1 WHERE user_id = ? AND creditos > 0", (u_id,))
    ok = cursor.rowcount > 0; conn.commit(); conn.close(); return ok

def registrar_usuario_ssh(u, p, e, r_id, l):
    conn = get_connection(); cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO usuarios_ssh VALUES (?, ?, ?, ?, ?)", (u, p, e, r_id, l))
    conn.commit(); conn.close()
