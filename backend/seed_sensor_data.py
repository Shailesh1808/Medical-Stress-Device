import random
from datetime import datetime, timedelta
from models import db, SensorData
from app import app

def seed_random_sensor_data(user_id=4, num_entries=30):
    with app.app_context():
        now = datetime.utcnow()
        for i in range(num_entries):
            data = SensorData(
                user_id=user_id,
                timestamp=now - timedelta(minutes=i),
                heart_rate=random.uniform(60, 100),
                hrv=random.uniform(20, 70),
                arrhythmia_flag=random.choice([True, False]),
                gsr_mean=random.uniform(0.5, 1.2),
                gsr_peak_count=random.randint(0, 3),
                gsr_trend=random.uniform(-0.2, 0.2),
                notes=None
            )
            db.session.add(data)
        db.session.commit()
        print(f"✅ Inserted {num_entries} random rows for user_id={user_id}")

if __name__ == '__main__':
    seed_random_sensor_data()
