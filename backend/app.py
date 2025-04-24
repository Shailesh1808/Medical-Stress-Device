from flask import Flask
from models import db
from routes.auth import auth

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'super-secret-key'  # 🔒 Replace with env var in production
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:password@localhost/stress_monitoring'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Register routes
app.register_blueprint(auth)

@app.route('/')
def index():
    return 'App running!'

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Creates tables if not already present
    app.run(debug=True)
