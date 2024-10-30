from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User Model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # 'admin', 'teacher', 'student'

# Marks Model
class Marks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    marks = db.Column(db.Float, nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Login Failed. Check your username and password.')
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        return render_template('dashboard.html')
    return redirect(url_for('home'))

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
        flash('Student added successfully!')
        return redirect(url_for('dashboard'))
    
    return render_template('add_student.html')

@app.route('/manage_students', methods=['GET', 'POST'])
@login_required
def manage_students():
    if current_user.role != 'admin':
        return redirect(url_for('dashboard'))
    
    students = User.query.filter_by(role='student').all()
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        student = User.query.get(student_id)
        if student:
            db.session.delete(student)
            db.session.commit()
            flash('Student removed successfully!')
            return redirect(url_for('manage_students'))
    
    return render_template('manage_students.html', students=students)

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
        flash('Teacher added successfully!')
        return redirect(url_for('dashboard'))
    
    return render_template('add_teacher.html')

@app.route('/manage_teachers', methods=['GET', 'POST'])
@login_required
def manage_teachers():
    if current_user.role != 'admin':
        return redirect(url_for('dashboard'))
    
    teachers = User.query.filter_by(role='teacher').all()
    if request.method == 'POST':
        teacher_id = request.form.get('teacher_id')
        teacher = User.query.get(teacher_id)
        if teacher:
            db.session.delete(teacher)
            db.session.commit()
            flash('Teacher removed successfully!')
            return redirect(url_for('manage_teachers'))
    
    return render_template('manage_teachers.html', teachers=teachers)

@app.route('/add_marks', methods=['GET', 'POST'])
@login_required
def add_marks():
    if current_user.role != 'teacher':
        return redirect(url_for('dashboard'))
    
    students = User.query.filter_by(role='student').all()
    if request.method == 'POST':
        student_id = request.form['student_id']
        subject = request.form['subject']
        marks = request.form['marks']
        new_marks = Marks(student_id=student_id, subject=subject, marks=marks)
        db.session.add(new_marks)
        db.session.commit()
        flash('Marks added successfully!')
        return redirect(url_for('dashboard'))
    
    return render_template('add_marks.html', students=students)

@app.route('/view_marks', methods=['GET'])
@login_required
def view_marks():
    if current_user.role != 'student':
        return redirect(url_for('dashboard'))
    
    marks = Marks.query.filter_by(student_id=current_user.id).all()
    return render_template('view_marks.html', marks=marks)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == '__main__':
    db.create_all()  # Create the database tables
    app.run(debug=True)
