from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # patient or doctor

    # Common fields
    full_name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    contact_number = db.Column(db.String(20))

    # Patient-specific
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    condition = db.Column(db.String(100))

    # Doctor-specific
    specialty = db.Column(db.String(100))
    hospital = db.Column(db.String(100))

    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class DoctorPatientMap(db.Model):
    __tablename__ = 'doctor_patient_map'

    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    doctor = db.relationship('User', foreign_keys=[doctor_id], backref='assigned_patients')
    patient = db.relationship('User', foreign_keys=[patient_id], backref='assigned_doctors')
