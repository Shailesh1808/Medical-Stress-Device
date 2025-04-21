from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify, session, current_app
from werkzeug.security import check_password_hash  # You can switch to hashed passwords later
from models import db, DoctorPatientMap, User, SensorData
from sensor_interface import collect_sensor_data
from threading import Thread
from report_utils import generate_stress_report  # Optional, if used
from report_utils import generate_single_report  # Optional, if used


auth = Blueprint('auth', __name__)

# ------------------------
# User Signup
# ------------------------
@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')  # ⚠️ Replace with hash later
        role = request.form.get('role')
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        contact_number = request.form.get('contact_number')

        # Role-specific fields
        age = gender = condition = specialty = hospital = None
        if role == 'patient':
            age = request.form.get('age')
            ssn = request.form.get('ssn')
            gender = request.form.get('gender')
            address = request.form.get('address')
        elif role == 'doctor':
            specialty = request.form.get('specialty')
            hospital = request.form.get('hospital')

        if User.query.filter_by(username=username).first():
            return "User already exists", 409

        user = User(
            username=username,
            password=password,
            role=role,
            full_name=full_name,
            email=email,
            contact_number=contact_number,
            age=age,
            ssn=ssn,
            gender=gender,
            address=address,
            specialty=specialty,
            hospital=hospital
        )
        db.session.add(user)
        db.session.commit()

        return redirect(url_for('auth.login'))

    return render_template('signup.html')

# ------------------------
# User Login
# ------------------------
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if not user or user.password != password:  # ⚠️ Add hashing later
            flash("Invalid credentials", "danger")
            return redirect(url_for('auth.login'))

        # Set session
        session['user_id'] = user.id
        session['username'] = user.username
        session['role'] = user.role

        print("Logged in user:", session)

        # Role-based redirect
        if user.role == 'admin':
            return redirect(url_for('auth.admin_assign'))
        elif user.role == 'patient':
            return redirect(url_for('auth.patient_dashboard'))
        elif user.role == 'doctor':
            return redirect(url_for('auth.doctor_dashboard'))

    return render_template('login.html')

# ------------------------
# Admin: Assign Patients to Doctors
# ------------------------
@auth.route('/admin/assign', methods=['GET', 'POST'])
def admin_assign():
    if session.get('role') != 'admin':
        return redirect(url_for('auth.login'))

    doctors = User.query.filter_by(role='doctor').all()
    patients = User.query.filter_by(role='patient').all()
    message = None

    if request.method == 'POST':
        doctor_id = request.form['doctor_id']
        patient_id = request.form['patient_id']

        existing = DoctorPatientMap.query.filter_by(doctor_id=doctor_id, patient_id=patient_id).first()
        if not existing:
            mapping = DoctorPatientMap(doctor_id=doctor_id, patient_id=patient_id)
            db.session.add(mapping)
            db.session.commit()
            message = "Patient successfully assigned to doctor."
        else:
            message = "This patient is already assigned to the doctor."

    return render_template("admin_assign.html", doctors=doctors, patients=patients, message=message)

# ------------------------
# Patient Dashboard
# ------------------------

@auth.route('/dashboard/patient')
def patient_dashboard():
    if 'user_id' not in session or session['role'] != 'patient':
        return redirect(url_for('auth.login'))

    user_id = session['user_id']

    # Fetch 10 latest records
    reports = SensorData.query.filter_by(user_id=user_id).order_by(SensorData.timestamp.desc()).limit(10).all()

    # Generate GPT report if missing
    for record in reports:
        if record.notes is None:
            try:
                record.notes = generate_single_report(record)
                db.session.commit()
            except Exception as e:
                print(f"⚠️ GPT report failed for record {record.id}: {e}")
                record.notes = "Report not available."

    return render_template('patient_dashboard.html', reports=reports, username=session['username'])


# ------------------------
# Collect Sensor Data (30 sec)
# ------------------------
@auth.route('/collect', methods=['POST'])
def collect_data():
    if 'user_id' not in session:
        return jsonify({"message": "Unauthorized"}), 401

    user_id = session['user_id']
    Thread(target=collect_sensor_data, args=(user_id, 30, current_app._get_current_object())).start()
    return jsonify({"message": "Collecting 30 seconds of data..."})

# ------------------------
# Doctor Dashboard
# ------------------------
@auth.route('/dashboard/doctor')
def doctor_dashboard():
    if 'user_id' not in session or session['role'] != 'doctor':
        return redirect(url_for('auth.login'))
    return render_template('doctor_dashboard.html', username=session['username'])

# ------------------------
# Logout
# ------------------------
@auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
