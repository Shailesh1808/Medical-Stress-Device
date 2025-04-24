from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# ========================
# User Table
# ========================
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'patient' or 'doctor'
    ssn = db.Column(db.Integer, unique=True)  # Social Security Number
    address = db.Column(db.String(200))



    # Common fields
    full_name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    contact_number = db.Column(db.String(20))

    # Patient-specific
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))

    # Doctor-specific
    specialty = db.Column(db.String(100))
    hospital = db.Column(db.String(100))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ========================
# Doctor-Patient Mapping Table
# ========================
class DoctorPatientMap(db.Model):
    __tablename__ = 'doctor_patient_map'

    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    doctor = db.relationship('User', foreign_keys=[doctor_id], backref='patients_mapped')
    patient = db.relationship('User', foreign_keys=[patient_id], backref='doctors_mapped')


# ========================
# Sensor Data Table
# ========================
class SensorData(db.Model):
    __tablename__ = 'sensor_data'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # ECG Metrics
    heart_rate = db.Column(db.Float)
    hrv = db.Column(db.Float)
    arrhythmia_flag = db.Column(db.Boolean)

    # GSR Metrics
    gsr_mean = db.Column(db.Float)
    gsr_peak_count = db.Column(db.Integer)
    gsr_trend = db.Column(db.Float)

    # Optional: LLM summary
    notes = db.Column(db.Text)

    user = db.relationship('User', backref=db.backref('sensor_data', lazy=True))
