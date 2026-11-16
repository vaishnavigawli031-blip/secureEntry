
import sqlite3
import os

from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')


# ---------------- DATABASE CREATION ----------------

def init_db():

    con = sqlite3.connect(DB_PATH)

    # Create Guards table
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

    # Create Visitors table
    con.execute('''
        CREATE TABLE IF NOT EXISTS visitors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT,
            address TEXT NOT NULL,
            purpose TEXT NOT NULL,
            visit_date TEXT NOT NULL,
            visit_time TEXT NOT NULL,
            photo_data TEXT,
            status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Check existing visitors table columns
    columns = {
        row[1] for row in con.execute(
            "PRAGMA table_info(visitors)"
        ).fetchall()
    }

    # Add checkout_time if it does not exist
    if "checkout_time" not in columns:
        con.execute(
            "ALTER TABLE visitors ADD COLUMN checkout_time TEXT"
        )

    con.commit()
    con.close()


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

        if (
            username == os.environ.get('ADMIN_USERNAME')
            and password == os.environ.get('ADMIN_PASSWORD')
        ):

            session['admin_logged_in'] = True

            return redirect(url_for('admin'))

        else:
            return "Invalid username or password!"

    return render_template('admin_login.html')


# ---------------- GUARD LOGIN ----------------

@app.route('/guard_login', methods=['GET', 'POST'])
def guard_login():

    if request.method == 'POST':

        guard_id = request.form.get('guard_id', '').strip()
        password = request.form.get('password', '')

        con = sqlite3.connect(DB_PATH)

        try:

            guard = con.execute(
                'SELECT password FROM guards WHERE guard_id = ?',
                (guard_id,)
            ).fetchone()

        finally:
            con.close()

        if guard and check_password_hash(guard[0], password):

            session['guard_logged_in'] = True
            session['guard_id'] = guard_id

            return redirect(url_for('guard_dashboard'))

        return "Invalid Guard ID or password!"

    return render_template('guard_login.html')


# ---------------- GUARD DASHBOARD ----------------

@app.route('/guard_dashboard')
def guard_dashboard():

    if not session.get('guard_logged_in'):
        return redirect(url_for('guard_login'))

    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row

    try:

        guard = con.execute('''
            SELECT name, guard_id, mobile, address
            FROM guards
            WHERE guard_id = ?
        ''', (session.get('guard_id'),)).fetchone()

        if guard is None:

            session.pop('guard_logged_in', None)
            session.pop('guard_id', None)

            return redirect(url_for('guard_login'))

        visitors = con.execute('''
            SELECT id, name, phone, email, address,
                   purpose, visit_date, visit_time,
                   photo_data, status, created_at, checkout_time
            FROM visitors
            WHERE visit_date = date('now', 'localtime')
            ORDER BY id DESC
        ''').fetchall()

    finally:
        con.close()

    return render_template(
        'guard_dashboard.html',
        guard=guard,
        visitors=visitors
    )


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


# ---------------- CHECK IN ----------------

@app.route('/checkin/<int:visitor_id>')
def checkin(visitor_id):

    if not session.get('guard_logged_in'):
        return redirect(url_for('guard_login'))

    con = sqlite3.connect(DB_PATH)

    try:

        con.execute('''
            UPDATE visitors
            SET status = 'Checked In'
            WHERE id = ? AND status = 'Pending'
        ''', (visitor_id,))

        con.commit()

    finally:
        con.close()

    return redirect(url_for('guard_dashboard'))


# ---------------- CHECK OUT ----------------

@app.route('/checkout/<int:visitor_id>')
def checkout(visitor_id):

    if not session.get('guard_logged_in'):
        return redirect(url_for('guard_login'))

    con = sqlite3.connect(DB_PATH)

    try:

        con.execute('''
            UPDATE visitors
            SET status = 'Checked Out',
                checkout_time = datetime('now', 'localtime')
            WHERE id = ? AND status = 'Checked In'
        ''', (visitor_id,))

        con.commit()

    finally:
        con.close()

    return redirect(url_for('guard_dashboard'))


# ---------------- REJECT VISITOR ----------------

@app.route('/reject/<int:visitor_id>')
def reject(visitor_id):

    if not session.get('guard_logged_in'):
        return redirect(url_for('guard_login'))

    con = sqlite3.connect(DB_PATH)

    try:

        con.execute('''
            UPDATE visitors
            SET status = 'Rejected'
            WHERE id = ? AND status = 'Pending'
        ''', (visitor_id,))

        con.commit()

    finally:
        con.close()

    return redirect(url_for('guard_dashboard'))


# ---------------- VIEW PAGE ----------------

@app.route('/view')
def view():
    return render_template('view.html')


# ---------------- CONFIRMATION PAGE ----------------

@app.route('/confirm', methods=['GET', 'POST'])
def confirm():

    if request.method == 'POST':

        name = request.form.get('Name', '').strip()
        phone = request.form.get('Phone', '').strip()
        email = request.form.get('Email', '').strip()
        address = request.form.get('Address', '').strip()
        purpose = request.form.get('Purpose', '').strip()
        visit_date = request.form.get('Date', '')
        visit_time = request.form.get('Time', '')
        photo_data = request.form.get('photo_data', '')

        if not all([
            name, phone, address,
            purpose, visit_date, visit_time
        ]):

            return "Please fill in all required fields!"

        con = sqlite3.connect(DB_PATH)
        con.row_factory = sqlite3.Row

        try:

            # Save visitor registration time automatically
            cursor = con.execute('''
                INSERT INTO visitors
                (name, phone, email, address, purpose,
                 visit_date, visit_time, photo_data, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?,
                        datetime('now', 'localtime'))
            ''', (
                name,
                phone,
                email,
                address,
                purpose,
                visit_date,
                visit_time,
                photo_data
            ))

            visitor_id = cursor.lastrowid

            con.commit()

            visitor = con.execute(
                'SELECT * FROM visitors WHERE id = ?',
                (visitor_id,)
            ).fetchone()

        finally:
            con.close()

        return render_template(
            'confirm.html',
            visitor=visitor
        )

    return redirect(url_for('visitor'))


# ---------------- RUN APPLICATION ----------------

if __name__ == "__main__":
    app.run(debug=True)
