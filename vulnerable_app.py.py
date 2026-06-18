from flask import Flask, request, render_template_string, session, redirect, url_for, flash
from werkzeug.security import check_password_hash
from prometheus_flask_exporter import PrometheusMetrics # Para la integración con Grafana
import sqlite3
import os

app = Flask(__name__)
# La clave secreta debe venir de una variable de entorno en producción
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))

# Inicializar métricas para Monitorización
metrics = PrometheusMetrics(app)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return 'Welcome to the Secure Task Manager Application!'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        
        # MITIGACIÓN SQLi: Consulta parametrizada estricta
        query = "SELECT * FROM users WHERE username = ?"
        user = conn.execute(query, (username,)).fetchone()
        
        # MITIGACIÓN Criptografía: Verificación de hash seguro
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['role'] = user['role']
            return redirect(url_for('dashboard'))
        else:
            return 'Invalid credentials!'
            
    return '''
    <form method="post">
        Username: <input type="text" name="username"><br>
        Password: <input type="password" name="password"><br>
        <input type="submit" value="Login">
    </form>
    '''

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    user_id = session['user_id']
    conn = get_db_connection()
    tasks = conn.execute("SELECT * FROM tasks WHERE user_id = ?", (user_id,)).fetchall()
    conn.close()
    
    return render_template_string(''' 
    <h1>Welcome, user {{ user_id }}!</h1>
    <form action="/add_task" method="post">
        <input type="text" name="task" placeholder="New task" required><br>
        <input type="submit" value="Add Task">
    </form>
    <h2>Your Tasks</h2>
    <ul>
    {% for task in tasks %}
        <li>{{ task['task'] }} <a href="/delete_task/{{ task['id'] }}">Delete</a></li>
    {% endfor %}
    </ul>
    ''', user_id=user_id, tasks=tasks)

@app.route('/add_task', methods=['POST'])
def add_task():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    task = request.form['task']
    user_id = session['user_id']
    conn = get_db_connection()
    # Parametrización segura
    conn.execute("INSERT INTO tasks (user_id, task) VALUES (?,?)", (user_id, task))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/delete_task/<int:task_id>')
def delete_task(task_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    # Verificar que la tarea pertenece al usuario actual (Mitigación IDOR)
    user_id = session['user_id']
    conn = get_db_connection()
    conn.execute("DELETE FROM tasks WHERE id = ? AND user_id = ?", (task_id, user_id))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/admin')
def admin():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    return 'Welcome to the admin panel!!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)