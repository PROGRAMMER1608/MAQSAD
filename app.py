from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'your_password'
app.config['MYSQL_DB'] = 'result_management'

mysql = MySQL(app)

# Route: Home
@app.route('/')
def home():
    return render_template('index.html')

# Route: Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()

        if user and check_password_hash(user[2], password):
            session['user'] = username
            flash('Login successful', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

# Route: Dashboard
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:  # Check if user is logged in
        return redirect(url_for('login'))  # Redirect to login page if not logged in
    return render_template('dashboard.html')  # Render the dashboard template

# Route: Logout
@app.route('/logout')
def logout():
    session.pop('user', None)  # Remove the user from the session
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))  # Redirect to the login page



# Route: Add Student
@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        roll = request.form['roll']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO students (name, roll) VALUES (%s, %s)", (name, roll))
        mysql.connection.commit()
        cur.close()

        flash('Student added successfully', 'success')
        return redirect(url_for('add_student'))

    return render_template('add_student.html')

# Route: Add Marks
@app.route('/add_marks', methods=['GET', 'POST'])
def add_marks():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        roll = request.form['roll']
        subject = request.form['subject']
        marks = request.form['marks']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO marks (roll, subject, marks) VALUES (%s, %s, %s)", (roll, subject, marks))
        mysql.connection.commit()
        cur.close()

        flash('Marks added successfully', 'success')
        return redirect(url_for('add_marks'))

    return render_template('add_marks.html')
    

# Route: View Students
@app.route('/view_students')
def view_students():
    if 'user' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM students")
    students = cur.fetchall()
    cur.close()
    return render_template('view_students.html', students=students)

# Route: View Marks
@app.route('/view_marks')
def view_marks():
    if 'user' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM marks")
    marks = cur.fetchall()
    cur.close()
    return render_template('view_marks.html', marks=marks)

# Default Admin User
admin_created = False

@app.before_request
def create_admin():
    global admin_created
    if not admin_created:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", ('admin',))
        admin = cur.fetchone()
        if not admin:
            hashed_password = generate_password_hash('password')
            cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", ('admin', hashed_password))
            mysql.connection.commit()
        cur.close()
        admin_created = True


if __name__ == '__main__':
    app.run(debug=True)

