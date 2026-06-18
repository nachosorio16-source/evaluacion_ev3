import sqlite3
from werkzeug.security import generate_password_hash # type: ignore

# Conexión a la base de datos
conn = sqlite3.connect('database.db')
c = conn.cursor()

# Crear la tabla de usuarios
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL
)
''')

# Insertar usuarios de prueba usando un hash seguro (PBKDF2 por defecto en Werkzeug)
c.execute('''
INSERT INTO users (username, password, role) VALUES (?, ?, ?)
''', ('admin', generate_password_hash('password'), 'admin'))

c.execute('''
INSERT INTO users (username, password, role) VALUES (?, ?, ?)
''', ('user', generate_password_hash('password'), 'user'))

# Crear la tabla de tareas
c.execute('''
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    task TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id)
)
''')

conn.commit()
conn.close()
print("Base de datos estructurada y asegurada con éxito.")