from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from flask import session
from flask import request, session, redirect, url_for, render_template, flash
from werkzeug.security import check_password_hash
from models import db, DoctorPatientMap, User



auth = Blueprint('auth', __name__)

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Common fields
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        contact_number = request.form.get('contact_number')

        # Hash the password

        # Role-specific fields
        age = gender = condition = specialty = hospital = None

        if role == 'patient':
            age = request.form.get('age')
            gender = request.form.get('gender')
            condition = request.form.get('condition')
        elif role == 'doctor':
            specialty = request.form.get('specialty')
            hospital = request.form.get('hospital')

        # Check if user already exists
        if User.query.filter_by(username=username).first():
            return "User already exists", 409

        # Create user
        user = User(
            username=username,
            password=password,
            role=role,
            full_name=full_name,
            email=email,
            contact_number=contact_number,
            age=age,
            gender=gender,
            condition=condition,
            specialty=specialty,
            hospital=hospital
        )

        db.session.add(user)
        db.session.commit()

        return redirect(url_for('auth.login'))

    return render_template('signup.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if not user:
            flash("Invalid credentials", "danger")
            return redirect(url_for('auth.login'))
        
        if user.password != password:
            flash("Invalid credentials", "danger")
            return redirect(url_for('auth.login'))

        # Store session
        session['user_id'] = user.id
        session['username'] = user.username
        session['role'] = user.role

        print("Logged in user:", session)

        # 🔁 Redirect based on role
        if user.role == 'admin':
            return redirect(url_for('auth.admin_assign'))
        elif user.role == 'patient':
            return redirect(url_for('auth.patient_dashboard'))
        elif user.role == 'doctor':
            return redirect(url_for('auth.doctor_dashboard'))

    return render_template('login.html')


@auth.route('/admin/assign', methods=['GET', 'POST'])
def admin_assign():
    if session['username'] != 'admin':
        return redirect(url_for('auth.login'))

    doctors = User.query.filter_by(role='doctor').all()
    patients = User.query.filter_by(role='patient').all()
    message = None

    if request.method == 'POST':
        doctor_id = request.form['doctor_id']
        patient_id = request.form['patient_id']

        # Prevent duplicate assignments
        existing = DoctorPatientMap.query.filter_by(doctor_id=doctor_id, patient_id=patient_id).first()
        if not existing:
            mapping = DoctorPatientMap(doctor_id=doctor_id, patient_id=patient_id)
            db.session.add(mapping)
            db.session.commit()
            message = "Patient successfully assigned to doctor."
        else:
            message = "This patient is already assigned to the doctor."

    return render_template("admin_assign.html", doctors=doctors, patients=patients, message=message)

@auth.route('/dashboard/patient')
def patient_dashboard():
    if 'user_id' not in session or session['role'] != 'patient':
        return redirect(url_for('auth.login'))
    return render_template('patient_dashboard.html', username=session['username'])

@auth.route('/dashboard/doctor')
def doctor_dashboard():
    if 'user_id' not in session or session['role'] != 'doctor':
        return redirect(url_for('auth.login'))
    return render_template('doctor_dashboard.html', username=session['username'])

@auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))