from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'  # Change this to a random secret key

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

# User Model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    role = db.Column(db.String(50))  # 'admin', 'teacher', or 'student'

# Database creation and admin user creation
@app.before_first_request
def create_admin_user():
    with app.app_context():  # Ensure we are in the app context
        db.create_all()  # Create the database tables
        if User.query.filter_by(username='admin').first() is None:
            admin_user = User(
                name='Admin',
                username='admin',
                password=generate_password_hash('adminpassword'),  # Use a secure password here
                role='admin'
            )
            db.session.add(admin_user)
            db.session.commit()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Home page
@app.route('/')
def home():
    return render_template('login.html')

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

# Dashboard
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

# Add Student
@app.route('/add_student', methods=['GET', 'POST'])
@login_required
def add_student():
    if current_user.role != 'admin':
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        new_student = User(name=name, username=username, password=password, role='student')
        db.session.add(new_student)
        db.session.commit()
        return redirect(url_for('manage_students'))
    return render_template('add_student.html')

# Manage Students
@app.route('/manage_students', methods=['GET', 'POST'])
@login_required
def manage_students():
    if current_user.role != 'admin':
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        student_id = request.form['student_id']
        student = User.query.get(student_id)
        if student:
            db.session.delete(student)
            db.session.commit()
        return redirect(url_for('manage_students'))

    students = User.query.filter_by(role='student').all()
    return render_template('manage_students.html', students=students)

# Add Teacher
@app.route('/add_teacher', methods=['GET', 'POST'])
@login_required
def add_teacher():
    if current_user.role != 'admin':
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        new_teacher = User(name=name, username=username, password=password, role='teacher')
        db.session.add(new_teacher)
        db.session.commit()
        return redirect(url_for('manage_teachers'))
    return render_template('add_teacher.html')

# Manage Teachers
@app.route('/manage_teachers', methods=['GET', 'POST'])
@login_required
def manage_teachers():
    if current_user.role != 'admin':
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        teacher_id = request.form['teacher_id']
        teacher = User.query.get(teacher_id)
        if teacher:
            db.session.delete(teacher)
            db.session.commit()
        return redirect(url_for('manage_teachers'))

    teachers = User.query.filter_by(role='teacher').all()
    return render_template('manage_teachers.html', teachers=teachers)

# Add Marks
@app.route('/add_marks', methods=['GET', 'POST'])
@login_required
def add_marks():
    if current_user.role != 'teacher':
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        student_id = request.form['student_id']
        subject = request.form['subject']
        marks = request.form['marks']
        # Logic to save marks associated with the student and subject
        flash('Marks added successfully!')
        return redirect(url_for('add_marks'))

    students = User.query.filter_by(role='student').all()
    return render_template('add_marks.html', students=students)

# View Marks
@app.route('/view_marks')
@login_required
def view_marks():
    # Logic to fetch and display marks for the logged-in student
    return render_template('view_marks.html')

# Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
