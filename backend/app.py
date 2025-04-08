from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from models import db
from routes.auth import auth 

app = Flask(__name__)
app = Flask(__name__)


app.config['SECRET_KEY'] = 'super-secret-key'  # Change later

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:MDS@localhost/stress_monitoring'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'

db.init_app(app)
jwt = JWTManager(app)

# Registering your authentication blueprint
app.register_blueprint(auth)

@app.route('/')
def index():
    return 'App running!'

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
