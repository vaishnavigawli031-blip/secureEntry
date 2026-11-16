
import sqlite3
import os

from flask import Flask, render_template, request, redirect, url_for,session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')


# ---------------- DATABASE CREATION ----------------

def init_db():
    con = sqlite3.connect(DB_PATH)

    con.execute('''
        CREATE TABLE IF NOT EXISTS guards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            mobile TEXT NOT NULL,
            address TEXT NOT NULL,
            guard_id TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    con.commit()
    con.close()


# Create database table automatically
init_db()


# ---------------- HOME PAGE ----------------

@app.route('/')
def home():
    return render_template('home.html')


# ---------------- ADMIN PAGE ----------------

@app.route('/admin')
def admin():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    return render_template('admin.html')
@app.route('/admin_logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))


# ---------------- ADMIN LOGIN ----------------

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        if username == os.environ.get('ADMIN_USERNAME') and password == os.environ.get('ADMIN_PASSWORD'):
            session['admin_logged_in'] = True
            return redirect(url_for('admin'))

        else:
            return "Invalid username or password!"

    return render_template('admin_login.html')


# ---------------- GUARD LOGIN PAGE ----------------

@app.route('/guard_login')
def guard_login():
    return render_template('guard_login.html')


# ---------------- GUARD DASHBOARD ----------------

@app.route('/guard_dashboard')
def guard_dashboard():
    return render_template('guard_dashboard.html')


# ---------------- GUARD REGISTRATION PAGE ----------------

@app.route('/guard_acc')
def guard_acc():
    return render_template('guard_acc.html')


# ---------------- GUARD REGISTRATION ACTION ----------------

@app.route('/guard_register_action', methods=['POST'])
def guard_register_action():

    name = request.form['name']
    mobile = request.form['mobile']
    address = request.form['address']
    guard_id = request.form['guard_id']
    password = request.form['password']

    # Hash password
    hashed_password = generate_password_hash(password)

    con = sqlite3.connect(DB_PATH)

    try:

        con.execute('''
            INSERT INTO guards
            (name, mobile, address, guard_id, password)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, mobile, address, guard_id, hashed_password))

        con.commit()

        return redirect(url_for('admin'))

    except sqlite3.IntegrityError:

        return "This Guard ID already exists!"

    finally:
        con.close()


# ---------------- VISITOR PAGE ----------------

@app.route('/visitor')
def visitor():
    return render_template('visitor.html')


# ---------------- VIEW PAGE ----------------

@app.route('/view')
def view():
    return render_template('view.html')


# ---------------- CONFIRMATION PAGE ----------------

@app.route('/confirm')
def confirm():
    return render_template('confirm.html')


# ---------------- RUN APPLICATION ----------------

if __name__ == "__main__":
    app.run(debug=True)
